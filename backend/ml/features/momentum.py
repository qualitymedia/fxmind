"""
Momentum features (~12 features).

RSI: 7, 14, 28
ROC: 4, 8, 16
MACD (12, 26, 9): MACD line, Signal line, Histogram
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _calculate_rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / np.where(loss == 0, 1e-6, loss)
    return 100 - (100 / (1 + rs))


def compute_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute RSI, ROC, and MACD momentum indicators."""
    res = pd.DataFrame(index=df.index)
    close = df["close"]

    # RSI
    for p in [7, 14, 28]:
        res[f"rsi_{p}"] = _calculate_rsi(close, p) / 100.0  # Normalized 0..1

    # ROC (Rate of Change)
    for p in [4, 8, 16]:
        res[f"roc_{p}"] = (close - close.shift(p)) / close.shift(p)

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal

    res["macd_line"] = macd / close
    res["macd_signal"] = signal / close
    res["macd_hist"] = hist / close

    return res
