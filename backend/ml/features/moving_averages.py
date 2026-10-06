"""
Moving Average features (~15 features).

EMAs: 8, 21, 50, 100, 200.
Normalized distances between price and EMAs, and between EMA pairs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_ma_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute EMA and distance features."""
    res = pd.DataFrame(index=df.index)
    close = df["close"]

    emas = {}
    periods = [8, 21, 50, 100, 200]
    for p in periods:
        ema = close.ewm(span=p, adjust=False).mean()
        emas[p] = ema
        # Distance from price to EMA (normalized by close price)
        res[f"dist_ema_{p}"] = (close - ema) / close

    # Normalized distances between key EMA pairs
    pairs = [(8, 21), (21, 50), (50, 200), (8, 50), (21, 200)]
    for p1, p2 in pairs:
        res[f"dist_ema_{p1}_{p2}"] = (emas[p1] - emas[p2]) / close

    # EMA slope/momentum (4-bar change in EMA)
    for p in [8, 21, 50]:
        res[f"ema_{p}_slope_4b"] = (emas[p] - emas[p].shift(4)) / close

    return res
