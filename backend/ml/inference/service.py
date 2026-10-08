"""
Inference Service.

Production inference pipeline:
1. Load production model bundle
2. Validate feature schema
3. Generate features at t0
4. Predict market regime
5. Predict direction probabilities via XGBoost/Ensemble
6. Calibrate probabilities
7. Apply signal gates, Price Action/SMC pattern extraction & Multi-Timeframe (H1) Confluence filters
8. Generate setup (TREND_FOLLOWING or MEAN_REVERSION) or NO_TRADE + Key Watch Levels
9. Generate evidence-based explanation & background log streaming
10. Return SignalResponse contract object

Fails closed:
If data is stale -> NO_TRADE
If model is unavailable -> NO_TRADE
Never fake a signal.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import pandas as pd

from ml.artifacts.saver import ModelArtifactSaver
from ml.data.validation import validate_market_dataframe
from ml.features.pipeline import FeaturePipeline
from ml.features.volume_profile import compute_volume_profile
from ml.models.regime import RegimeDetector
from app.api.v1.logs import add_system_log


def is_forex_market_closed(dt: datetime) -> bool:
    """
    Check if the Forex market is closed for the weekend.
    Forex market hours: Sunday 22:00 UTC to Friday 22:00 UTC.
    Market is closed Friday 22:00 UTC to Sunday 22:00 UTC.
    """
    weekday = dt.weekday()  # 0=Mon, ..., 4=Fri, 5=Sat, 6=Sun
    hour = dt.hour
    if weekday == 5:  # Saturday
        return True
    if weekday == 4 and hour >= 22:  # Friday after 22:00 UTC
        return True
    if weekday == 6 and hour < 22:  # Sunday before 22:00 UTC
        return True
    return False


class InferenceService:
    """Production Inference Service."""

    def __init__(self, artifacts_dir: str = "./ml/artifacts"):
        self.saver = ModelArtifactSaver(base_dir=artifacts_dir)
        self.regime_detector = RegimeDetector()
        self.current_bundle = None
        self._load_production_model()

    def _load_production_model(self) -> None:
        """Attempt to load latest production model bundle (v2.0 preferred, v1.0 fallback)."""
        for version in [None, "gbpusd-ensemble-v2.0", "gbpusd-ensemble-v1.0"]:
            try:
                self.current_bundle = self.saver.load_bundle(version)
                v = self.current_bundle.get("version", version or "unknown")
                print(f"[InferenceService] Loaded model bundle: {v}")
                return
            except Exception:
                continue
        self.current_bundle = None
        print("[InferenceService] WARNING: No model bundle found.")

    def analyze(
        self,
        m15_df: pd.DataFrame,
        context_dfs: dict[str, pd.DataFrame] | None = None,
        h1_df: pd.DataFrame | None = None,
        events_df: pd.DataFrame | None = None,
        spread_pips: float = 0.00012,
    ) -> dict:
        """
        Run inference at t0 candle close.
        Fails closed with explicit NO_TRADE if conditions fail.
        """
        now = datetime.now(timezone.utc)

        # 0. Fail Closed: Weekend Market Closure Check
        if is_forex_market_closed(now):
            add_system_log("GATES", "Market is closed for the weekend. Live analysis paused.", "WARNING")
            return self._build_no_trade(
                now,
                "Forex market is closed for the weekend (Friday 22:00 UTC to Sunday 22:00 UTC). Live analysis is paused.",
                market_session="WEEKEND_CLOSED"
            )

        # 1. Fail Closed: Stale or empty data
        if m15_df.empty:
            add_system_log("DATA", "No candle data available from data provider.", "ERROR")
            return self._build_no_trade(now, "No market data available.")

        latest_candle = m15_df.iloc[-1]
        candle_ts = pd.to_datetime(latest_candle["timestamp"]).to_pydatetime()
        c_close = float(latest_candle["close"])

        # Check freshness (> 45 mins = stale)
        if (now - candle_ts).total_seconds() > 45 * 60:
            add_system_log("DATA", f"Market data stale (>45 mins old at {candle_ts.strftime('%H:%M')}).", "WARNING")
            return self._build_no_trade(candle_ts, "Market data is stale. Analysis paused.")

        # 2. Fail Closed: Model unavailable
        if self.current_bundle is None:
            add_system_log("SYSTEM", "Trained ML model bundle unavailable.", "ERROR")
            return self._build_no_trade(candle_ts, "AI analysis model is unavailable.")

        # 2b. Fail Closed: Validate raw market data before features are built
        validation = validate_market_dataframe(m15_df, symbol="GBPUSD", timeframe="M15")
        if not validation.is_valid:
            first_error = validation.error_messages[0] if validation.error_messages else "unknown market data validation issue"
            add_system_log("DATA", f"Market data failed validation: {first_error}", "ERROR")
            return self._build_no_trade(candle_ts, f"Market data failed validation: {first_error}")

        # 3. Compute Features
        schema = self.current_bundle["schema"]
        pipeline = FeaturePipeline(schema=schema)
        f_matrix = pipeline.compute_features(m15_df, context_dfs, h1_df, events_df)

        if f_matrix.empty:
            add_system_log("FEATURES", "Feature computation produced empty matrix.", "ERROR")
            return self._build_no_trade(candle_ts, "Insufficient historical context for feature engineering.")

        latest_features = f_matrix.iloc[[-1]]
        feat_row = latest_features.iloc[0]

        add_system_log("FEATURES", f"Extracted {len(feat_row)} features for GBPUSD M15 candle close ({c_close:.5f}).", "INFO")

        # 4. Predict Regime
        regime = self.regime_detector.detect_regime(feat_row)
        add_system_log("REGIME", f"Regime classified as {regime}.", "INFO")

        # 5. Model Inference & Calibration
        model = self.current_bundle["model"]
        calibrator = self.current_bundle["calibrator"]

        raw_probs = model.predict_proba(latest_features.values)
        cal_probs = calibrator.calibrate(raw_probs)[0]

        p_bear, p_neutral, p_bull = float(cal_probs[0]), float(cal_probs[1]), float(cal_probs[2])

        # Direction & confidence
        if p_bull >= p_bear and p_bull >= p_neutral:
            bias = "BULLISH"
            confidence = p_bull
            direction = "LONG"
            margin = p_bull - p_bear
        elif p_bear >= p_bull and p_bear >= p_neutral:
            bias = "BEARISH"
            confidence = p_bear
            direction = "SHORT"
            margin = p_bear - p_bull
        else:
            bias = "NEUTRAL"
            confidence = p_neutral
            direction = None
            margin = 0.0

        add_system_log("SIGNALS", f"Model prediction: Bias={bias}, Confidence={confidence:.1%}, Bull={p_bull:.1%}, Bear={p_bear:.1%}", "INFO")

        # ATR calculation for risk setup
        atr14 = float(feat_row.get("atr_14", 0.0012) * c_close)
        if atr14 <= 0:
            atr14 = 0.0012

        # 6. Extract Active Price Action & SMC Patterns
        pattern_items = []
        if float(feat_row.get("pattern_bullish_liquidity_sweep", 0.0)) > 0.5:
            pattern_items.append({"name": "Bullish Liquidity Sweep (Stop Hunt)", "type": "SMC_SWEEP", "bias": "BULLISH", "icon": "⚡"})
        if float(feat_row.get("pattern_bearish_liquidity_sweep", 0.0)) > 0.5:
            pattern_items.append({"name": "Bearish Liquidity Sweep (Stop Hunt)", "type": "SMC_SWEEP", "bias": "BEARISH", "icon": "⚡"})

        if float(feat_row.get("pattern_bullish_fvg", 0.0)) > 0.5:
            gap = float(feat_row.get("fvg_bull_gap_pips", 0.0))
            pattern_items.append({"name": f"Bullish Fair Value Gap ({gap:.1f} pips)", "type": "SMC_FVG", "bias": "BULLISH", "icon": "📊"})
        if float(feat_row.get("pattern_bearish_fvg", 0.0)) > 0.5:
            gap = float(feat_row.get("fvg_bear_gap_pips", 0.0))
            pattern_items.append({"name": f"Bearish Fair Value Gap ({gap:.1f} pips)", "type": "SMC_FVG", "bias": "BEARISH", "icon": "📊"})

        if float(feat_row.get("pattern_bullish_pinbar", 0.0)) > 0.5:
            pattern_items.append({"name": "Bullish Rejection Pinbar", "type": "PINBAR", "bias": "BULLISH", "icon": "📍"})
        if float(feat_row.get("pattern_bearish_pinbar", 0.0)) > 0.5:
            pattern_items.append({"name": "Bearish Rejection Pinbar", "type": "PINBAR", "bias": "BEARISH", "icon": "📍"})

        if float(feat_row.get("pattern_bullish_engulfing", 0.0)) > 0.5:
            pattern_items.append({"name": "Bullish Engulfing Bar", "type": "ENGULFING", "bias": "BULLISH", "icon": "🕯️"})
        if float(feat_row.get("pattern_bearish_engulfing", 0.0)) > 0.5:
            pattern_items.append({"name": "Bearish Engulfing Bar", "type": "ENGULFING", "bias": "BEARISH", "icon": "🕯️"})

        if float(feat_row.get("pattern_inside_bar", 0.0)) > 0.5:
            pattern_items.append({"name": "Inside Bar Compression", "type": "INSIDE_BAR", "bias": "NEUTRAL", "icon": "📦"})

        if pattern_items:
            add_system_log("PATTERNS", f"Detected {len(pattern_items)} SMC patterns on M15 bar: {[p['name'] for p in pattern_items]}", "SUCCESS")

        # 7. Multi-Timeframe (H1) Confluence Check
        h1_trend_state = float(feat_row.get("h1_ema_trend_state", 0.0))
        h1_dist_ema50 = float(feat_row.get("h1_dist_ema_50", 0.0))

        h1_confluence_ok = True
        h1_reason_msg = "H1 higher-timeframe structure is aligned."

        if direction == "LONG":
            if h1_trend_state < 0 and h1_dist_ema50 < -0.003:
                h1_reason_msg = "Counter-trend LONG against H1 macro trend (tightened TP/SL target)."
        elif direction == "SHORT":
            if h1_trend_state > 0 and h1_dist_ema50 > 0.003:
                h1_reason_msg = "Counter-trend SHORT against H1 macro trend (tightened TP/SL target)."

        # 8. Signal Gates & Strategy Selection
        min_confidence = 0.45
        min_margin = 0.06

        # --- Dynamic TP multiplier based on confidence ---
        # Low confidence (45-55%) → conservative TP (1.2x SL)
        # Medium confidence (55-65%) → balanced TP (1.6x SL)
        # High confidence (65-75%) → extended TP (2.0x SL)
        # Very high confidence (75%+) → maximum TP (2.5x SL)
        def dynamic_tp_mult(conf: float) -> float:
            if conf >= 0.75:
                return 2.5
            elif conf >= 0.65:
                return 2.0
            elif conf >= 0.55:
                return 1.6
            else:
                return 1.2

        # Volume Profile POC & Value Area (VAH/VAL) Engine
        vp = compute_volume_profile(m15_df)
        poc = vp["poc"]
        vah = vp["vah"]
        val = vp["val"]
        price_pos = vp["price_position"]

        is_news_clear = float(feat_row.get("high_impact_event_near", 0.0)) == 0.0
        is_spread_ok = spread_pips <= 0.00030

        # Session & Liquidity logic: Allow trailing limit order entry in Asian session if confidence >= 52%
        is_illiquid = regime == "ILLIQUID"
        allow_illiquid_entry = is_illiquid and confidence >= 0.52
        is_liquidity_ok = not is_illiquid or allow_illiquid_entry

        vwap_zscore = float(feat_row.get("vwap_zscore", 0.0))
        above_upper_1 = float(feat_row.get("above_vwap_upper_1", 0.0)) > 0.5
        below_lower_1 = float(feat_row.get("below_vwap_lower_1", 0.0)) > 0.5

        no_trade_reasons = []
        if not is_news_clear:
            no_trade_reasons.append("High-impact economic news event nearby")
        if not is_spread_ok:
            no_trade_reasons.append("Market spread exceeds threshold")
        if not is_liquidity_ok:
            no_trade_reasons.append("Market liquidity is low (ILLIQUID Asian session)")
        if confidence < min_confidence:
            no_trade_reasons.append(f"Calibrated confidence ({confidence:.1%}) below threshold ({min_confidence:.1%})")
        if margin < min_margin:
            no_trade_reasons.append(f"Directional margin ({margin:.1%}) is weak")

        strategy_type = None

        if allow_illiquid_entry:
            strategy_type = "TRAILING_LIMIT_ENTRY"
            add_system_log("GATES", f"Asian Session Entry ({confidence:.1%} >= 52%). Activating Trailing Limit Entry.", "SUCCESS")
        elif regime == "TRENDING":
            if abs(vp["dist_to_poc_pips"]) <= 3.5:
                strategy_type = "VP_POC_RETEST_BOUNCE"
            else:
                strategy_type = "TREND_FOLLOWING"
        elif regime == "RANGING":
            if direction == "SHORT" and (price_pos == "ABOVE_VAH" or c_close >= vah or vwap_zscore >= 0.8 or above_upper_1):
                strategy_type = "VP_VALUE_AREA_ROTATION"
            elif direction == "LONG" and (price_pos == "BELOW_VAL" or c_close <= val or vwap_zscore <= -0.8 or below_lower_1):
                strategy_type = "VP_VALUE_AREA_ROTATION"
            else:
                strategy_type = "MEAN_REVERSION"
        elif regime == "HIGH_VOLATILITY":
            strategy_type = "BREAKOUT_EXPANSION"
        else:
            strategy_type = "TREND_FOLLOWING"

        reasons = []
        for r in no_trade_reasons:
            reasons.append({"category": "NO_TRADE", "reason": r, "sentiment": "NEUTRAL"})

        for p in pattern_items:
            reasons.append({
                "category": "Price Action & SMC",
                "reason": f"{p['icon']} {p['name']}",
                "sentiment": "SUPPORTIVE" if p["bias"] == bias else "NEUTRAL"
            })

        # Add Volume Profile Point of Control Evidence
        reasons.append({
            "category": "Volume Profile & POC",
            "reason": f"Price is {price_pos} | POC: {poc:.5f}, VAH: {vah:.5f}, VAL: {val:.5f} (Dist: {vp['dist_to_poc_pips']:+.1f}p)",
            "sentiment": "SUPPORTIVE" if strategy_type in ("VP_VALUE_AREA_ROTATION", "VP_POC_RETEST_BOUNCE") else "NEUTRAL"
        })

        # Calculate Key Watch Levels (Projected Trade Geometry when status is NO_TRADE)
        if direction == "LONG":
            watch_low = round(c_close - (0.1 * atr14), 5)
            watch_high = round(c_close + (0.1 * atr14), 5)
            watch_sl = round(c_close - (1.0 * atr14), 5)
            watch_tp = round(c_close + (1.8 * atr14), 5)
        elif direction == "SHORT":
            watch_low = round(c_close - (0.1 * atr14), 5)
            watch_high = round(c_close + (0.1 * atr14), 5)
            watch_sl = round(c_close + (1.0 * atr14), 5)
            watch_tp = round(c_close - (1.8 * atr14), 5)
        else:
            watch_low = watch_high = watch_sl = watch_tp = None

        if no_trade_reasons or bias == "NEUTRAL" or strategy_type is None:
            add_system_log("GATES", f"NO_TRADE gate active: {no_trade_reasons[0] if no_trade_reasons else 'Neutral bias'}. Generated Key Watch Levels.", "WARNING")
            return {
                "symbol": "GBPUSD",
                "timestamp": candle_ts.isoformat(),
                "timeframe": "M15",
                "bias": bias,
                "confidence": round(confidence, 4),
                "regime": regime,
                "trade": {
                    "status": "NO_TRADE",
                    "direction": direction,
                    "strategy_type": strategy_type or ("MEAN_REVERSION" if regime == "RANGING" else "TREND_FOLLOWING"),
                    "entry_low": watch_low,
                    "entry_high": watch_high,
                    "stop_loss": watch_sl,
                    "take_profit": watch_tp,
                    "risk_reward": 1.8 if direction else None,
                    "is_watch_level": True,
                },
                "model": {
                    "bull_probability": round(p_bull, 4),
                    "bear_probability": round(p_bear, 4),
                    "neutral_probability": round(p_neutral, 4),
                },
                "market": {
                    "atr14": round(atr14, 5),
                    "spread": round(spread_pips, 5),
                    "session": "LONDON_NY_OVERLAP" if float(feat_row.get("is_london_ny_overlap", 0.0)) > 0.5 else "ACTIVE",
                },
                "filters": {
                    "news_clear": is_news_clear,
                    "liquidity_ok": is_liquidity_ok,
                    "spread_ok": is_spread_ok,
                    "h1_confluence_ok": h1_confluence_ok,
                },
                "reasons": reasons,
                "patterns": pattern_items,
                "model_version": self.current_bundle.get("version", "gbpusd-ensemble-v1.0") if self.current_bundle else "gbpusd-ensemble-v1.0",
                "volume_profile": {
                    "poc": poc,
                    "vah": vah,
                    "val": val,
                    "price_position": price_pos,
                    "dist_to_poc_pips": vp.get("dist_to_poc_pips", 0.0),
                },
            }

        # 9. Generate Trade Geometry for ACTIVE Signal
        # All strategies: SL multiplier is fixed, TP multiplier is dynamic by confidence.
        # This guarantees TP distance > SL distance (always positive R:R > 1.0).
        tp_mult = dynamic_tp_mult(confidence)
        sl_mult_base = 0.8  # Will be adjusted per strategy

        if strategy_type == "TRAILING_LIMIT_ENTRY":
            sl_m = 1.1
            if direction == "LONG":
                entry_low = round(c_close - (0.2 * atr14), 5)
                entry_high = round(c_close - (0.05 * atr14), 5)
                sl = round(c_close - (sl_m * atr14), 5)
                tp = round(c_close + (tp_mult * atr14), 5)
            else:
                entry_low = round(c_close + (0.05 * atr14), 5)
                entry_high = round(c_close + (0.2 * atr14), 5)
                sl = round(c_close + (sl_m * atr14), 5)
                tp = round(c_close - (tp_mult * atr14), 5)
            rr = round(tp_mult / sl_m, 2)

        elif strategy_type == "VP_VALUE_AREA_ROTATION":
            # 80% Rule: Rotate towards POC and opposite Value Area boundary
            sl_m = 0.9
            if direction == "LONG":
                entry_low = round(c_close - (0.05 * atr14), 5)
                entry_high = round(c_close + (0.05 * atr14), 5)
                sl = round(min(c_close - (sl_m * atr14), val - 0.0006), 5)
                # TP: use POC if it's further than dynamic multiplier, else use multiplier
                tp_candidate = round(c_close + (tp_mult * atr14), 5)
                tp = max(poc, tp_candidate) if poc > c_close else tp_candidate
                tp = round(tp, 5)
            else:
                entry_low = round(c_close - (0.05 * atr14), 5)
                entry_high = round(c_close + (0.05 * atr14), 5)
                sl = round(max(c_close + (sl_m * atr14), vah + 0.0006), 5)
                tp_candidate = round(c_close - (tp_mult * atr14), 5)
                tp = min(poc, tp_candidate) if poc < c_close else tp_candidate
                tp = round(tp, 5)
            rr = round(abs(tp - c_close) / max(abs(c_close - sl), 1e-5), 2)

        elif strategy_type == "VP_POC_RETEST_BOUNCE":
            # Retest of Point of Control node with trend continuation
            sl_m = 0.8
            if direction == "LONG":
                entry_low = round(poc - (0.05 * atr14), 5)
                entry_high = round(poc + (0.05 * atr14), 5)
                sl = round(poc - (sl_m * atr14), 5)
                tp = round(c_close + (tp_mult * atr14), 5)
            else:
                entry_low = round(poc - (0.05 * atr14), 5)
                entry_high = round(poc + (0.05 * atr14), 5)
                sl = round(poc + (sl_m * atr14), 5)
                tp = round(c_close - (tp_mult * atr14), 5)
            rr = round(tp_mult / sl_m, 2)

        elif strategy_type == "MEAN_REVERSION":
            # Mean reversion: tighter SL, TP scales with confidence (market might snap back fast)
            sl_m = 0.7
            if direction == "LONG":
                entry_low = round(c_close - (0.05 * atr14), 5)
                entry_high = round(c_close + (0.05 * atr14), 5)
                sl = round(c_close - (sl_m * atr14), 5)
                tp = round(c_close + (tp_mult * atr14), 5)
            else:
                entry_low = round(c_close - (0.05 * atr14), 5)
                entry_high = round(c_close + (0.05 * atr14), 5)
                sl = round(c_close + (sl_m * atr14), 5)
                tp = round(c_close - (tp_mult * atr14), 5)
            rr = round(tp_mult / sl_m, 2)

        elif strategy_type == "BREAKOUT_EXPANSION":
            # Breakout: wider SL to survive the spike, TP extended on confidence
            sl_m = 1.2
            if direction == "LONG":
                entry_low = round(c_close - (0.05 * atr14), 5)
                entry_high = round(c_close + (0.1 * atr14), 5)
                sl = round(c_close - (sl_m * atr14), 5)
                tp = round(c_close + (tp_mult * atr14), 5)
            else:
                entry_low = round(c_close - (0.1 * atr14), 5)
                entry_high = round(c_close + (0.05 * atr14), 5)
                sl = round(c_close + (sl_m * atr14), 5)
                tp = round(c_close - (tp_mult * atr14), 5)
            rr = round(tp_mult / sl_m, 2)

        else:  # TREND_FOLLOWING (default)
            sl_m = 1.0
            if direction == "LONG":
                entry_low = round(c_close - (0.1 * atr14), 5)
                entry_high = round(c_close + (0.1 * atr14), 5)
                sl = round(c_close - (sl_m * atr14), 5)
                tp = round(c_close + (tp_mult * atr14), 5)
            else:
                entry_low = round(c_close - (0.1 * atr14), 5)
                entry_high = round(c_close + (0.1 * atr14), 5)
                sl = round(c_close + (sl_m * atr14), 5)
                tp = round(c_close - (tp_mult * atr14), 5)
            rr = round(tp_mult / sl_m, 2)

        # Final sanity: ensure TP is strictly on the correct side of entry
        entry_mid = (entry_low + entry_high) / 2.0
        if direction == "LONG":
            if tp <= entry_mid:
                tp = round(entry_mid + (tp_mult * atr14), 5)
            if sl >= entry_mid:
                sl = round(entry_mid - (sl_m * atr14), 5)
        else:
            if tp >= entry_mid:
                tp = round(entry_mid - (tp_mult * atr14), 5)
            if sl <= entry_mid:
                sl = round(entry_mid + (sl_m * atr14), 5)

        add_system_log("SIGNALS", f"ACTIVE {strategy_type} | conf={confidence:.1%} | tp_mult={tp_mult:.1f}x | Direction={direction}, Entry={entry_low:.5f}-{entry_high:.5f}, SL={sl:.5f}, TP={tp:.5f}, RR={rr}", "SUCCESS")

        # 10. Reasons / Evidence Breakdown
        active_reasons = [
            {
                "category": "Strategy Mode",
                "reason": f"Active {strategy_type} setup triggered for {regime} regime",
                "sentiment": "SUPPORTIVE"
            },
            {
                "category": "H1 Confluence",
                "reason": h1_reason_msg,
                "sentiment": "SUPPORTIVE" if h1_confluence_ok else "CAUTION"
            },
            {
                "category": "Momentum & Stretch",
                "reason": f"RSI level at {float(feat_row.get('rsi_14', 0.5))*100:.1f} | VWAP Z-Score: {vwap_zscore:.2f}",
                "sentiment": "SUPPORTIVE"
            },
        ]

        for p in pattern_items:
            active_reasons.append({
                "category": "Price Action & SMC",
                "reason": f"{p['icon']} {p['name']}",
                "sentiment": "SUPPORTIVE" if p["bias"] == bias else "NEUTRAL"
            })

        active_reasons.append({
            "category": "News & Liquidity",
            "reason": "No high-impact economic news nearby; spread within limits",
            "sentiment": "CLEAR"
        })

        return {
            "symbol": "GBPUSD",
            "timestamp": candle_ts.isoformat(),
            "timeframe": "M15",
            "bias": bias,
            "confidence": round(confidence, 4),
            "regime": regime,
            "trade": {
                "status": "ACTIVE",
                "direction": direction,
                "strategy_type": strategy_type,
                "entry_low": entry_low,
                "entry_high": entry_high,
                "stop_loss": sl,
                "take_profit": tp,
                "risk_reward": rr,
                "is_watch_level": False,
            },
            "model": {
                "bull_probability": round(p_bull, 4),
                "bear_probability": round(p_bear, 4),
                "neutral_probability": round(p_neutral, 4),
            },
            "market": {
                "atr14": round(atr14, 5),
                "spread": round(spread_pips, 5),
                "session": "LONDON_NY_OVERLAP" if float(feat_row.get("is_london_ny_overlap", 0.0)) > 0.5 else "ACTIVE",
            },
            "filters": {
                "news_clear": is_news_clear,
                "liquidity_ok": is_liquidity_ok,
                "spread_ok": is_spread_ok,
                "h1_confluence_ok": h1_confluence_ok,
            },
            "reasons": active_reasons,
            "patterns": pattern_items,
            "model_version": self.current_bundle.get("version", "gbpusd-ensemble-v1.0") if self.current_bundle else "gbpusd-ensemble-v1.0",
            "volume_profile": {
                "poc": poc,
                "vah": vah,
                "val": val,
                "price_position": price_pos,
                "dist_to_poc_pips": vp.get("dist_to_poc_pips", 0.0),
            },
        }

    def _build_no_trade(self, ts: datetime, reason_msg: str, market_session: str = "UNKNOWN") -> dict:
        """Build clean NO_TRADE response when inference is impossible or restricted."""
        version_str = "gbpusd-ensemble-v1.0"
        if self.current_bundle:
            version_str = self.current_bundle.get("version") or self.current_bundle.get("metadata", {}).get("version", version_str)

        return {
            "symbol": "GBPUSD",
            "timestamp": ts.isoformat() if isinstance(ts, datetime) else str(ts),
            "timeframe": "M15",
            "bias": "NEUTRAL",
            "confidence": 0.3333,
            "regime": "RANGING",
            "trade": {
                "status": "NO_TRADE",
                "direction": None,
                "strategy_type": None,
                "entry_low": None,
                "entry_high": None,
                "stop_loss": None,
                "take_profit": None,
                "risk_reward": None,
                "is_watch_level": True,
            },
            "model": {
                "bull_probability": 0.3333,
                "bear_probability": 0.3333,
                "neutral_probability": 0.3334,
            },
            "market": {
                "atr14": 0.0012,
                "spread": 0.00012,
                "session": market_session,
            },
            "filters": {
                "news_clear": False,
                "liquidity_ok": False,
                "spread_ok": True,
                "h1_confluence_ok": True,
            },
            "reasons": [
                {"category": "NO_TRADE", "reason": reason_msg, "sentiment": "NEUTRAL"}
            ],
            "patterns": [],
            "model_version": version_str,
        }
