"""
Cross-Market features (~12 features).

DXY, EURUSD, USDJPY, EURGBP returns & volatility.
Relative strength features where statistically justified.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_cross_market_features(
    main_df: pd.DataFrame,
    context_dfs: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Compute cross-market context features.
    
    context_dfs: dict mapping symbol -> DataFrame with 'timestamp' and 'close'
    """
    res = pd.DataFrame(index=main_df.index)

    main_ts = pd.to_datetime(main_df["timestamp"], utc=True)
    main_close = main_df["close"]

    for symbol in ["DXY", "EURUSD", "USDJPY", "EURGBP"]:
        if symbol not in context_dfs or context_dfs[symbol].empty:
            # Fill default zeroes if symbol data missing
            res[f"cross_{symbol}_return_1b"] = 0.0
            res[f"cross_{symbol}_return_4b"] = 0.0
            res[f"cross_{symbol}_vol_16b"] = 0.0
            continue

        c_df = context_dfs[symbol].copy()
        c_df["timestamp"] = pd.to_datetime(c_df["timestamp"], utc=True)

        # Merge on timestamp using forward fill
        merged = pd.merge_asof(
            pd.DataFrame({"timestamp": main_ts}),
            c_df[["timestamp", "close"]].sort_values("timestamp"),
            on="timestamp",
            direction="backward",
        )
        c_close = merged["close"].ffill().bfill()

        res[f"cross_{symbol}_return_1b"] = np.log(c_close / c_close.shift(1)).fillna(0.0)
        res[f"cross_{symbol}_return_4b"] = np.log(c_close / c_close.shift(4)).fillna(0.0)
        
        c_ret = np.log(c_close / c_close.shift(1))
        res[f"cross_{symbol}_vol_16b"] = c_ret.rolling(16).std().fillna(0.0)

    # Relative strength: GBPUSD return - EURUSD return
    if "cross_EURUSD_return_4b" in res.columns:
        gbp_ret4 = np.log(main_close / main_close.shift(4)).fillna(0.0)
        res["relative_strength_gbp_eur"] = gbp_ret4 - res["cross_EURUSD_return_4b"]

    return res
