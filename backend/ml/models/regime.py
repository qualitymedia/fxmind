"""
Market Regime Detection Engine.

States:
- TRENDING: Strong directional movement (ADX > 25, EMA21/EMA50 separation)
- RANGING: Low ADX, price oscillating inside channels
- HIGH_VOLATILITY: Volatility percentile > 90
- ILLIQUID: Low tick volume percentile < 10 outside major sessions
"""

from __future__ import annotations

import pandas as pd


class RegimeDetector:
    """Deterministic market regime classification based on domain rules."""

    def __init__(
        self,
        high_vol_percentile: float = 0.90,
        illiquid_volume_percentile: float = 0.10,
        trending_adx_threshold: float = 25.0,
    ):
        self.high_vol_percentile = high_vol_percentile
        self.illiquid_volume_percentile = illiquid_volume_percentile
        self.trending_adx_threshold = trending_adx_threshold

    def detect_regime(self, row: pd.Series | dict) -> str:
        """Classify single bar regime."""
        # 1. High Volatility Check
        atr_pct = float(row.get("atr14_percentile", 0.5))
        vol_pct = float(row.get("volatility_percentile", 0.5))

        if atr_pct >= self.high_vol_percentile or vol_pct >= self.high_vol_percentile:
            return "HIGH_VOLATILITY"

        # 2. Illiquid Check
        tick_pct = float(row.get("tick_activity_percentile", 0.5))
        is_asian = float(row.get("is_asian_session", 0.0)) > 0.5

        if tick_pct <= self.illiquid_volume_percentile and is_asian:
            return "ILLIQUID"

        # 3. Trending Check
        dist_ema21_50 = abs(float(row.get("dist_ema_21_50", 0.0)))
        rsi = float(row.get("rsi_14", 0.5)) * 100.0 if float(row.get("rsi_14", 0.5)) <= 1.0 else float(row.get("rsi_14", 50.0))

        # ADX surrogate: strong RSI deviation from 50 and wide EMA separation
        is_trending_momentum = (rsi > 60.0 or rsi < 40.0) and dist_ema21_50 > 0.0008

        if is_trending_momentum:
            return "TRENDING"

        # 4. Ranging (Default)
        return "RANGING"
