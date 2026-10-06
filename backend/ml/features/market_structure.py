"""
Market Structure features (~12 features).

Rolling high/low distances: 16, 32, 64 bars.
Breakout indicators: 8, 16, 32 bars.
Higher-high / Lower-low counts over 16 bars.
Higher-close / Lower-close counts over 16 bars.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_market_structure_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute market structure, breakout, and trend persistence features."""
    res = pd.DataFrame(index=df.index)
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # Distance to rolling high/low
    for p in [16, 32, 64]:
        r_high = high.rolling(p).max()
        r_low = low.rolling(p).min()
        r_span = np.where((r_high - r_low) == 0, 1e-6, r_high - r_low)

        res[f"dist_high_{p}b"] = (r_high - close) / close
        res[f"dist_low_{p}b"] = (close - r_low) / close
        res[f"price_position_{p}b"] = (close - r_low) / r_span

    # Breakouts (close > max high of previous N bars, or close < min low)
    for p in [8, 16, 32]:
        prev_high = high.shift(1).rolling(p).max()
        prev_low = low.shift(1).rolling(p).min()
        res[f"breakout_high_{p}b"] = (close > prev_high).astype(float)
        res[f"breakout_low_{p}b"] = (close < prev_low).astype(float)

    # HH / LL counts over 16 bars
    hh = (high > high.shift(1)).astype(float)
    ll = (low < low.shift(1)).astype(float)
    res["hh_count_16b"] = hh.rolling(16).sum() / 16.0
    res["ll_count_16b"] = ll.rolling(16).sum() / 16.0

    # Higher close / Lower close counts
    hc = (close > close.shift(1)).astype(float)
    lc = (close < close.shift(1)).astype(float)
    res["hc_count_16b"] = hc.rolling(16).sum() / 16.0
    res["lc_count_16b"] = lc.rolling(16).sum() / 16.0

    return res
