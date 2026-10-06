"""
Price features engineering (~15 features).

Calculates returns across 1, 2, 3, 4, 8, 12, 16, 24, 32 bars,
high-low range, body size, upper/lower wicks, body-to-range ratio, and close location.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute price-based features from OHLC DataFrame."""
    res = pd.DataFrame(index=df.index)

    close = df["close"]
    high = df["high"]
    low = df["low"]
    open_p = df["open"]

    # Log returns over multiple lookback horizons
    for k in [1, 2, 3, 4, 8, 12, 16, 24, 32]:
        res[f"return_{k}b"] = np.log(close / close.shift(k))

    # Range and Candle geometry
    hl_range = high - low
    body = (close - open_p).abs()
    
    # Avoid zero division
    safe_hl = np.where(hl_range == 0, 1e-6, hl_range)

    res["hl_range_pips"] = hl_range * 10000.0
    res["body_pips"] = body * 10000.0
    res["body_to_range"] = body / safe_hl

    upper_wick = high - np.maximum(open_p, close)
    lower_wick = np.minimum(open_p, close) - low

    res["upper_wick_ratio"] = upper_wick / safe_hl
    res["lower_wick_ratio"] = lower_wick / safe_hl

    # Close location within the bar (0.0 = low, 1.0 = high)
    res["close_location"] = (close - low) / safe_hl

    return res
