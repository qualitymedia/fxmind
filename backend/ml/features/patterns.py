"""
Explicit Candlestick & Price Action Pattern Recognition Engine.

Detects institutional chart and candlestick patterns:
- Bullish / Bearish Pinbar (Rejection wicks)
- Bullish / Bearish Engulfing
- Inside Bar (Compression / Coiling)
- Fair Value Gaps (FVG / Imbalances)
- Liquidity Sweep / False Breakout (Stop hunt)
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_pattern_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute explicit candlestick and price action pattern flags."""
    res = pd.DataFrame(index=df.index)

    if df.empty or len(df) < 5:
        return res

    open_p = df["open"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)

    candle_range = high - low
    safe_range = np.where(candle_range == 0, 1e-6, candle_range)
    body = (close - open_p).abs()
    upper_wick = high - np.maximum(open_p, close)
    lower_wick = np.minimum(open_p, close) - low
    close_loc = (close - low) / safe_range

    # 1. Pinbar / Wick Rejection Patterns
    # Bullish pinbar: Lower wick >= 60% of range, close in upper 35% of candle
    res["pattern_bullish_pinbar"] = (
        (lower_wick / safe_range >= 0.60) & (close_loc >= 0.65)
    ).astype(float)

    # Bearish pinbar: Upper wick >= 60% of range, close in lower 35% of candle
    res["pattern_bearish_pinbar"] = (
        (upper_wick / safe_range >= 0.60) & (close_loc <= 0.35)
    ).astype(float)

    # 2. Engulfing Patterns
    prev_open = open_p.shift(1)
    prev_close = close.shift(1)
    prev_body = (prev_close - prev_open).abs()

    # Bullish Engulfing: previous bar was red, current bar is green and its body > prev body & covers it
    res["pattern_bullish_engulfing"] = (
        (prev_close < prev_open)
        & (close > open_p)
        & (close >= prev_open)
        & (open_p <= prev_close)
        & (body > prev_body)
    ).astype(float)

    # Bearish Engulfing: previous bar was green, current bar is red and its body covers prev body
    res["pattern_bearish_engulfing"] = (
        (prev_close > prev_open)
        & (close < open_p)
        & (close <= prev_open)
        & (open_p >= prev_close)
        & (body > prev_body)
    ).astype(float)

    # 3. Inside Bar (Volatility contraction / consolidation)
    res["pattern_inside_bar"] = (
        (high < high.shift(1)) & (low > low.shift(1))
    ).astype(float)

    # 4. Fair Value Gap (FVG / 3-bar Imbalance)
    # Bullish FVG: current low > high of 2 bars ago (clean buying imbalance)
    fvg_bull_gap = low - high.shift(2)
    res["pattern_bullish_fvg"] = (fvg_bull_gap > 0).astype(float)
    res["fvg_bull_gap_pips"] = np.maximum(0.0, fvg_bull_gap) * 10000.0

    # Bearish FVG: current high < low of 2 bars ago (clean selling imbalance)
    fvg_bear_gap = low.shift(2) - high
    res["pattern_bearish_fvg"] = (fvg_bear_gap > 0).astype(float)
    res["fvg_bear_gap_pips"] = np.maximum(0.0, fvg_bear_gap) * 10000.0

    # 5. Liquidity Sweep (Took out 12-bar high/low but closed back inside)
    rolling_high_12 = high.shift(1).rolling(12).max()
    rolling_low_12 = low.shift(1).rolling(12).min()

    # Bullish sweep (swept low, trapped sellers, closed back above)
    res["pattern_bullish_liquidity_sweep"] = (
        (low < rolling_low_12) & (close > rolling_low_12)
    ).astype(float)

    # Bearish sweep (swept high, trapped buyers, closed back below)
    res["pattern_bearish_liquidity_sweep"] = (
        (high > rolling_high_12) & (close < rolling_high_12)
    ).astype(float)

    return res.ffill().fillna(0.0)
