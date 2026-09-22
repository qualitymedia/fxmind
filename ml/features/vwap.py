"""
Session VWAP (Volume-Weighted Average Price) & Standard Deviation Bands.

Computes institutional intraday reference levels:
- Daily Session VWAP
- +/- 1 Standard Deviation Band (Value Area bounds)
- +/- 2 Standard Deviation Band (Extreme exhaustion / mean-reversion bounds)
- Price distance and Z-score relative to VWAP
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_session_vwap_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute session-anchored VWAP and standard deviation bands."""
    res = pd.DataFrame(index=df.index)

    if df.empty:
        return res

    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)
    
    # Tick volume fallback
    if "tick_volume" in df.columns:
        vol = df["tick_volume"].astype(float)
    else:
        vol = pd.Series(1000.0, index=df.index)
    vol = pd.Series(np.where(vol <= 0, 100.0, vol), index=df.index)

    # Typical price
    typical_price = (high + low + close) / 3.0

    # Group by UTC date for intraday session reset
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"])
    else:
        ts = pd.to_datetime(df.index)

    date_group = ts.dt.date

    vp = pd.Series(typical_price * vol, index=df.index)

    # Cumulative sums within each trading day
    cum_vol = vol.groupby(date_group).cumsum()
    cum_vp = vp.groupby(date_group).cumsum()

    # Avoid zero division
    cum_vol = np.where(cum_vol == 0, 1e-6, cum_vol)
    vwap = pd.Series(cum_vp / cum_vol, index=df.index)

    # Intraday variance & standard deviation
    vp2 = pd.Series(vol * ((typical_price - vwap) ** 2), index=df.index)
    cum_vp2 = vp2.groupby(date_group).cumsum()
    vwap_std = pd.Series(np.sqrt(cum_vp2 / cum_vol), index=df.index)
    safe_std = np.where(vwap_std == 0, 1e-5, vwap_std)

    # 1. Normalized distance from VWAP
    res["vwap_dist_pips"] = (close - vwap) * 10000.0
    res["vwap_dist_pct"] = (close - vwap) / vwap

    # 2. VWAP Z-Score (institutional stretch measurement)
    res["vwap_zscore"] = (close - vwap) / safe_std

    # 3. Position relative to +/- 1 SD and +/- 2 SD bands
    vwap_upper_1 = vwap + 1.0 * vwap_std
    vwap_lower_1 = vwap - 1.0 * vwap_std
    vwap_upper_2 = vwap + 2.0 * vwap_std
    vwap_lower_2 = vwap - 2.0 * vwap_std

    res["above_vwap"] = (close > vwap).astype(float)
    res["above_vwap_upper_1"] = (close > vwap_upper_1).astype(float)
    res["below_vwap_lower_1"] = (close < vwap_lower_1).astype(float)
    res["above_vwap_upper_2"] = (close > vwap_upper_2).astype(float)
    res["below_vwap_lower_2"] = (close < vwap_lower_2).astype(float)

    # VWAP slope (3-bar momentum of VWAP itself)
    res["vwap_slope_3b"] = (vwap - vwap.shift(3)) * 10000.0

    return res.ffill().fillna(0.0)
