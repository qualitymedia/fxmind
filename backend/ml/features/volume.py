"""
Tick Activity & Volume features (~8 features). Vectorized for ultra-fast calculation.

Note: In FX, volume is tick volume (number of price updates),
NOT centralized exchange volume. We never label it as centralized FX volume.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute tick volume moving averages, ratios, z-scores, and return x volume."""
    res = pd.DataFrame(index=df.index)
    
    if "tick_volume" not in df.columns:
        df["tick_volume"] = 1000

    vol = df["tick_volume"].astype(float)
    close = df["close"]
    log_ret = np.log(close / close.shift(1))

    # Log tick volume
    res["log_tick_volume"] = np.log1p(vol)

    # Volume moving averages (16, 64 bars)
    vma16 = vol.rolling(16).mean()
    vma64 = vol.rolling(64).mean()
    safe_vma64 = np.where(vma64 == 0, 1e-6, vma64)

    res["vol_ma_ratio_16_64"] = vma16 / safe_vma64

    # Volume Z-score (over 64 bars)
    v_std = vol.rolling(64).std()
    safe_vstd = np.where(v_std == 0, 1e-6, v_std)
    res["vol_zscore_64"] = (vol - vma64) / safe_vstd

    # Volume 1-bar percentage change
    res["vol_change_1b"] = (vol - vol.shift(1)) / np.where(vol.shift(1) == 0, 1e-6, vol.shift(1))

    # Return x volume (Price-volume momentum)
    res["return_x_volume"] = log_ret * np.log1p(vol)

    # Vectorized fast volume percentile calculation using rolling min/max
    vol_min = vol.rolling(500, min_periods=50).min()
    vol_max = vol.rolling(500, min_periods=50).max()
    span_vol = np.where((vol_max - vol_min) == 0, 1e-6, vol_max - vol_min)
    res["tick_activity_percentile"] = (vol - vol_min) / span_vol

    return res
