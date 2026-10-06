"""
H1 Contextual features (~10 features).

H1 EMA structure, RSI, ATR, return, volatility, trend state, distance from highs/lows.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_h1_context_features(
    main_m15_df: pd.DataFrame,
    h1_df: pd.DataFrame | None,
) -> pd.DataFrame:
    """Compute H1-derived higher timeframe context features merged into M15 bars."""
    res = pd.DataFrame(index=main_m15_df.index)

    if h1_df is None or h1_df.empty:
        # Default zeros if H1 data not supplied
        for col in [
            "h1_return_1b", "h1_rsi_14", "h1_atr_14",
            "h1_dist_ema_21", "h1_dist_ema_50", "h1_ema_trend_state",
            "h1_dist_high_24b", "h1_dist_low_24b"
        ]:
            res[col] = 0.0
        return res

    h1 = h1_df.copy()
    h1["timestamp"] = pd.to_datetime(h1["timestamp"], utc=True)
    h1.sort_values("timestamp", inplace=True)

    # Compute H1 indicators
    close = h1["close"]
    high = h1["high"]
    low = h1["low"]

    h1["h1_return_1b"] = np.log(close / close.shift(1))

    # H1 RSI 14
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / np.where(loss == 0, 1e-6, loss)
    h1["h1_rsi_14"] = (100 - (100 / (1 + rs))) / 100.0

    # H1 ATR 14
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    h1["h1_atr_14"] = (tr.rolling(14).mean() / close)

    # H1 EMAs
    ema21 = close.ewm(span=21, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()

    h1["h1_dist_ema_21"] = (close - ema21) / close
    h1["h1_dist_ema_50"] = (close - ema50) / close
    h1["h1_ema_trend_state"] = np.where(ema21 > ema50, 1.0, -1.0)

    # Dist from H1 24-bar high/low (approx 1 day)
    h1["h1_dist_high_24b"] = (high.rolling(24).max() - close) / close
    h1["h1_dist_low_24b"] = (close - low.rolling(24).min()) / close

    # Merge into M15 bars using backward merge_asof (prevents lookahead bias)
    m15_ts = pd.to_datetime(main_m15_df["timestamp"], utc=True)

    cols_to_merge = [
        "timestamp", "h1_return_1b", "h1_rsi_14", "h1_atr_14",
        "h1_dist_ema_21", "h1_dist_ema_50", "h1_ema_trend_state",
        "h1_dist_high_24b", "h1_dist_low_24b"
    ]

    merged = pd.merge_asof(
        pd.DataFrame({"timestamp": m15_ts}),
        h1[cols_to_merge],
        on="timestamp",
        direction="backward",
    )

    for col in cols_to_merge[1:]:
        res[col] = merged[col].fillna(0.0).values

    return res
