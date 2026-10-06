"""
Event-Driven Backtest Engine.

Replays historical candles, calls inference and signal logic at every t0,
simulates executions with transaction costs, and tracks performance.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ml.backtest.execution import Position, calculate_execution_price
from ml.backtest.metrics import compute_trading_metrics
from ml.models.direction import XGBDirectionModel
from ml.calibration.calibrator import ProbabilityCalibrator


class EventDrivenBacktester:
    """Event-Driven Backtest Simulator."""

    def __init__(
        self,
        min_confidence: float = 0.58,
        min_margin: float = 0.15,
        sl_atr_mult: float = 1.0,
        tp_atr_mult: float = 1.8,
        spread_pips: float = 0.00012,
        slippage_pips: float = 0.00002,
    ):
        self.min_confidence = min_confidence
        self.min_margin = min_margin
        self.sl_atr_mult = sl_atr_mult
        self.tp_atr_mult = tp_atr_mult
        self.spread_pips = spread_pips
        self.slippage_pips = slippage_pips

    def run(
        self,
        m15_df: pd.DataFrame,
        feature_matrix: pd.DataFrame,
        model: XGBDirectionModel,
        calibrator: ProbabilityCalibrator,
    ) -> dict:
        """Run backtest loop on historical feature matrix."""
        if feature_matrix.empty:
            return {"metrics": compute_trading_metrics([])}

        raw_probs = model.predict_proba(feature_matrix.values)
        calibrated_probs = calibrator.calibrate(raw_probs)

        positions: list[Position] = []
        active_position: Position | None = None

        close = m15_df["close"].values
        high = m15_df["high"].values
        low = m15_df["low"].values
        ts = pd.to_datetime(m15_df["timestamp"]).values

        # ATR for risk calculation
        tr = np.maximum(high - low, np.maximum(np.abs(high - np.roll(close, 1)), np.abs(low - np.roll(close, 1))))
        atr14 = pd.Series(tr).rolling(14, min_periods=1).mean().values

        pos_id = 1
        n = len(m15_df)

        for i in range(50, n):
            c_time = pd.Timestamp(ts[i]).to_pydatetime()
            c_close = close[i]
            c_high = high[i]
            c_low = low[i]
            c_atr = atr14[i]

            # 1. Update active position (check SL/TP)
            if active_position is not None:
                if active_position.direction == "LONG":
                    # Check SL
                    if c_low <= active_position.stop_loss:
                        exit_price = calculate_execution_price("LONG", "EXIT", active_position.stop_loss, self.spread_pips, self.slippage_pips)
                        active_position.status = "CLOSED_SL"
                        active_position.exit_time = c_time
                        active_position.exit_price = exit_price
                        active_position.pnl_pips = (exit_price - active_position.entry_price) * 10000.0
                        positions.append(active_position)
                        active_position = None
                    # Check TP
                    elif c_high >= active_position.take_profit:
                        exit_price = calculate_execution_price("LONG", "EXIT", active_position.take_profit, self.spread_pips, self.slippage_pips)
                        active_position.status = "CLOSED_TP"
                        active_position.exit_time = c_time
                        active_position.exit_price = exit_price
                        active_position.pnl_pips = (exit_price - active_position.entry_price) * 10000.0
                        positions.append(active_position)
                        active_position = None

                elif active_position.direction == "SHORT":
                    # Check SL
                    if c_high >= active_position.stop_loss:
                        exit_price = calculate_execution_price("SHORT", "EXIT", active_position.stop_loss, self.spread_pips, self.slippage_pips)
                        active_position.status = "CLOSED_SL"
                        active_position.exit_time = c_time
                        active_position.exit_price = exit_price
                        active_position.pnl_pips = (active_position.entry_price - exit_price) * 10000.0
                        positions.append(active_position)
                        active_position = None
                    # Check TP
                    elif c_low <= active_position.take_profit:
                        exit_price = calculate_execution_price("SHORT", "EXIT", active_position.take_profit, self.spread_pips, self.slippage_pips)
                        active_position.status = "CLOSED_TP"
                        active_position.exit_time = c_time
                        active_position.exit_price = exit_price
                        active_position.pnl_pips = (active_position.entry_price - exit_price) * 10000.0
                        positions.append(active_position)
                        active_position = None

            # 2. Check signal at t0 if no position active
            if active_position is None:
                probs = calibrated_probs[i]
                p_bear, p_neutral, p_bull = probs[0], probs[1], probs[2]

                max_prob = max(p_bull, p_bear)
                direction = "LONG" if p_bull > p_bear else "SHORT"
                opposite_prob = p_bear if direction == "LONG" else p_bull
                margin = max_prob - opposite_prob

                # Gates
                if max_prob >= self.min_confidence and margin >= self.min_margin:
                    entry_price = calculate_execution_price(direction, "ENTRY", c_close, self.spread_pips, self.slippage_pips)

                    if direction == "LONG":
                        sl = entry_price - (self.sl_atr_mult * c_atr)
                        tp = entry_price + (self.tp_atr_mult * c_atr)
                    else:
                        sl = entry_price + (self.sl_atr_mult * c_atr)
                        tp = entry_price - (self.tp_atr_mult * c_atr)

                    active_position = Position(
                        id=pos_id,
                        symbol="GBPUSD",
                        direction=direction,
                        entry_time=c_time,
                        entry_price=entry_price,
                        stop_loss=sl,
                        take_profit=tp,
                        status="OPEN",
                    )
                    pos_id += 1

        metrics = compute_trading_metrics(positions)
        return {
            "metrics": metrics,
            "positions_count": len(positions),
        }
