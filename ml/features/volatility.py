"""
Volatility features (~15 features). Vectorized for ultra-fast calculation.

ATR: 7, 14, 28
Rolling std: 8, 16, 32
Bollinger Band width (20, 2)
Range/ATR ratios
ATR and Realized Volatility percentiles (over 500-bar rolling window)
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _calculate_atr(df: pd.DataFrame, period: int) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return tr.rolling(window=period).mean()


def compute_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute ATR, rolling std, Bollinger width, and fast vectorized volatility percentiles."""
    res = pd.DataFrame(index=df.index)
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # ATR
    atrs = {}
    for p in [7, 14, 28]:
        atr = _calculate_atr(df, p)
        atrs[p] = atr
        res[f"atr_{p}"] = atr / close  # Normalized by close

    # Rolling std of returns
    log_ret = np.log(close / close.shift(1))
    for p in [8, 16, 32]:
        res[f"vol_std_{p}"] = log_ret.rolling(window=p).std()

    # Bollinger Band Width
    ma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = ma20 + 2 * std20
    lower = ma20 - 2 * std20
    res["bollinger_width"] = (upper - lower) / ma20

    # Range / ATR14 ratio
    safe_atr14 = np.where(atrs[14] == 0, 1e-6, atrs[14])
    res["range_to_atr14"] = (high - low) / safe_atr14

    # Vectorized fast percentile calculation using rolling min/max
    atr14_min = atrs[14].rolling(500, min_periods=50).min()
    atr14_max = atrs[14].rolling(500, min_periods=50).max()
    span_atr = np.where((atr14_max - atr14_min) == 0, 1e-6, atr14_max - atr14_min)
    res["atr14_percentile"] = (atrs[14] - atr14_min) / span_atr

    realized_vol = log_ret.rolling(20).std()
    rvol_min = realized_vol.rolling(500, min_periods=50).min()
    rvol_max = realized_vol.rolling(500, min_periods=50).max()
    span_rvol = np.where((rvol_max - rvol_min) == 0, 1e-6, rvol_max - rvol_min)
    res["volatility_percentile"] = (realized_vol - rvol_min) / span_rvol

    return res
