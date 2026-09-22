"""
Triple-Barrier Label Engine.

Generates multiclass labels (BULL / BEAR / NEUTRAL) for M15 candles.
At t0:
- ATR14 = current ATR
- upper barrier = entry + 1.5 * ATR14
- lower barrier = entry - 1.0 * ATR14
- time barrier = horizon_bars (default 4 M15 bars = 60 mins)

BULL: Upper barrier hit first
BEAR: Lower barrier hit first
NEUTRAL: Neither barrier hit before time barrier
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import numpy as np
import pandas as pd


@dataclass
class LabelResult:
    """Label metadata for a single bar."""
    timestamp: datetime
    label: str  # BULL, BEAR, NEUTRAL
    label_start: datetime
    label_end: datetime
    touch_price: float
    barrier_type: str  # UPPER, LOWER, TIME


def compute_triple_barrier_labels(
    df: pd.DataFrame,
    upper_atr_mult: float = 1.5,
    lower_atr_mult: float = 1.0,
    horizon_bars: int = 4,
) -> pd.DataFrame:
    """
    Compute triple barrier labels for each candle in df.
    Returns DataFrame with columns: ['label', 'label_end_index', 'barrier_type'].
    """
    df = df.copy()
    close = df["close"].values
    high = df["high"].values
    low = df["low"].values
    ts = pd.to_datetime(df["timestamp"]).values

    # Calculate ATR14
    tr1 = high - low
    tr2 = np.abs(high - np.roll(close, 1))
    tr3 = np.abs(low - np.roll(close, 1))
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    atr14 = pd.Series(tr).rolling(14, min_periods=1).mean().values

    n = len(df)
    labels = ["NEUTRAL"] * n
    label_ends = [0] * n
    barrier_types = ["TIME"] * n

    for i in range(n - horizon_bars):
        entry_price = close[i]
        curr_atr = atr14[i]
        if curr_atr <= 0:
            continue

        upper_barrier = entry_price + (upper_atr_mult * curr_atr)
        lower_barrier = entry_price - (lower_atr_mult * curr_atr)

        # Look forward up to horizon_bars
        hit_upper = False
        hit_lower = False
        hit_index = i + horizon_bars

        for j in range(1, horizon_bars + 1):
            future_idx = i + j
            if future_idx >= n:
                break

            f_high = high[future_idx]
            f_low = low[future_idx]

            # Check if barriers touched in this bar
            is_upper = f_high >= upper_barrier
            is_lower = f_low <= lower_barrier

            if is_upper and is_lower:
                # Both touched in same bar: decide by which close was closer or touch open
                # Conservative approach: count as NEUTRAL or assign based on bar direction
                hit_upper = True
                hit_index = future_idx
                break
            elif is_upper:
                hit_upper = True
                hit_index = future_idx
                break
            elif is_lower:
                hit_lower = True
                hit_index = future_idx
                break

        if hit_upper:
            labels[i] = "BULL"
            barrier_types[i] = "UPPER"
            label_ends[i] = hit_index
        elif hit_lower:
            labels[i] = "BEAR"
            barrier_types[i] = "LOWER"
            label_ends[i] = hit_index
        else:
            labels[i] = "NEUTRAL"
            barrier_types[i] = "TIME"
            label_ends[i] = min(i + horizon_bars, n - 1)

    result_df = pd.DataFrame(
        {
            "label": labels,
            "label_end_index": label_ends,
            "barrier_type": barrier_types,
        },
        index=df.index,
    )
    return result_df
