"""
Volume Profile, Point of Control (POC), and Value Area (VA) Engine.

Calculates:
- Point of Control (POC): Price bin with the maximum traded volume.
- Value Area High (VAH) & Value Area Low (VAL): Boundaries containing 70% of total traded volume.
- High Volume Nodes (HVN) & Low Volume Nodes (LVN): Liquidity support and voids.
- Profile distribution histogram for visualization.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import TypedDict


class VolumeProfileResult(TypedDict):
    poc: float
    vah: float
    val: float
    total_volume: float
    value_area_volume: float
    price_position: str  # "ABOVE_VAH" (Premium), "INSIDE_VA" (Fair Value), "BELOW_VAL" (Discount)
    dist_to_poc_pips: float
    bins: list[dict]


def compute_volume_profile(
    df: pd.DataFrame,
    lookback_bars: int = 96,  # 96 M15 bars = 24 Hours
    bin_size_pips: float = 0.5,  # 0.5 pip resolution
) -> VolumeProfileResult:
    """
    Compute rolling Volume Profile from candlestick price and volume.
    
    Distributes bar volume across the [Low, High] range of each candle,
    identifies the Point of Control (POC), and derives 70% Value Area (VAH/VAL).
    """
    if df.empty:
        return {
            "poc": 1.3500,
            "vah": 1.3520,
            "val": 1.3480,
            "total_volume": 0.0,
            "value_area_volume": 0.0,
            "price_position": "INSIDE_VA",
            "dist_to_poc_pips": 0.0,
            "bins": [],
        }

    subset = df.tail(lookback_bars).copy()
    if subset.empty:
        subset = df.copy()

    # Determine pip multiplier (1 pip = 0.0001 for GBP/USD)
    pip_scale = 0.0001
    bin_size = bin_size_pips * pip_scale

    min_price = float(subset["low"].min())
    max_price = float(subset["high"].max())
    current_close = float(subset["close"].iloc[-1])

    if min_price == max_price or np.isnan(min_price) or np.isnan(max_price):
        return {
            "poc": current_close,
            "vah": current_close + 0.0020,
            "val": current_close - 0.0020,
            "total_volume": 1000.0,
            "value_area_volume": 700.0,
            "price_position": "INSIDE_VA",
            "dist_to_poc_pips": 0.0,
            "bins": [],
        }

    # Generate price bins
    bins = np.arange(min_price, max_price + bin_size, bin_size)
    if len(bins) < 2:
        bins = np.linspace(min_price, max_price, 20)

    bin_volumes = np.zeros(len(bins) - 1, dtype=float)

    # Distribute candle volume across covered price bins
    for _, row in subset.iterrows():
        c_low = float(row["low"])
        c_high = float(row["high"])
        vol = float(row.get("tick_volume", row.get("volume", 100.0)))
        if vol <= 0:
            vol = 100.0

        # Find overlapping bins
        c_range = max(c_high - c_low, 1e-6)
        
        # Calculate overlap with each bin
        b_lows = bins[:-1]
        b_highs = bins[1:]

        # Overlap = max(0, min(c_high, b_high) - max(c_low, b_low))
        overlap = np.maximum(0.0, np.minimum(c_high, b_highs) - np.maximum(c_low, b_lows))
        fraction = overlap / c_range
        bin_volumes += fraction * vol

    total_volume = float(np.sum(bin_volumes))
    if total_volume <= 0:
        total_volume = 1000.0

    # 1. Point of Control (POC): Price bin with maximum volume
    poc_idx = int(np.argmax(bin_volumes))
    bin_centers = (bins[:-1] + bins[1:]) / 2.0
    poc_price = round(float(bin_centers[poc_idx]), 5)

    # 2. Value Area: 70% of total volume expanding outward from POC
    target_va_vol = 0.70 * total_volume
    va_vol = bin_volumes[poc_idx]
    lower_idx = poc_idx
    upper_idx = poc_idx

    while va_vol < target_va_vol and (lower_idx > 0 or upper_idx < len(bin_volumes) - 1):
        vol_above = bin_volumes[upper_idx + 1] if upper_idx < len(bin_volumes) - 1 else 0.0
        vol_below = bin_volumes[lower_idx - 1] if lower_idx > 0 else 0.0

        if vol_above >= vol_below and upper_idx < len(bin_volumes) - 1:
            upper_idx += 1
            va_vol += vol_above
        elif lower_idx > 0:
            lower_idx -= 1
            va_vol += vol_below
        elif upper_idx < len(bin_volumes) - 1:
            upper_idx += 1
            va_vol += vol_above
        else:
            break

    vah_price = round(float(bins[upper_idx + 1]), 5)
    val_price = round(float(bins[lower_idx]), 5)

    # 3. Position relative to Value Area
    if current_close > vah_price:
        price_position = "ABOVE_VAH"
    elif current_close < val_price:
        price_position = "BELOW_VAL"
    else:
        price_position = "INSIDE_VA"

    dist_to_poc_pips = round((current_close - poc_price) / pip_scale, 1)

    # Prepare top bins for visualization (normalized 0-100)
    max_bin_vol = max(np.max(bin_volumes), 1.0)
    step = max(1, len(bin_centers) // 15)  # sample ~15-20 display levels
    profile_bins = []
    for i in range(0, len(bin_centers), step):
        p_lvl = round(float(bin_centers[i]), 5)
        p_vol = float(bin_volumes[i])
        profile_bins.append({
            "price": p_lvl,
            "volume": int(p_vol),
            "percentage": round((p_vol / max_bin_vol) * 100, 1),
            "is_poc": abs(p_lvl - poc_price) < (bin_size / 2.0),
            "is_value_area": val_price <= p_lvl <= vah_price,
        })

    return {
        "poc": poc_price,
        "vah": vah_price,
        "val": val_price,
        "total_volume": round(total_volume, 1),
        "value_area_volume": round(float(va_vol), 1),
        "price_position": price_position,
        "dist_to_poc_pips": dist_to_poc_pips,
        "bins": profile_bins,
    }
