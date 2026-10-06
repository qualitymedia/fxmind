"""
Session & Time features (~12 features).

Hour sin/cos, minute sin/cos, day of week.
Asian, London, New York session flags, London-NY overlap flag.
Minutes to/since London open (07:00 UTC) and New York open (12:00 UTC).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_session_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute time-of-day cyclicals, trading sessions, and minutes to/since opens."""
    res = pd.DataFrame(index=df.index)
    
    # Ensure timestamp is datetime
    ts = pd.to_datetime(df["timestamp"], utc=True)
    
    hours = ts.dt.hour + ts.dt.minute / 60.0
    day_of_week = ts.dt.dayofweek

    # Cyclical sin/cos encodings for time of day
    res["hour_sin"] = np.sin(2 * np.pi * hours / 24.0)
    res["hour_cos"] = np.cos(2 * np.pi * hours / 24.0)
    res["day_of_week"] = day_of_week / 4.0  # Normalized 0..1 (Mon=0, Fri=1)

    # Session flags (UTC hours)
    # Asian: 00:00 - 07:00 UTC
    # London: 07:00 - 16:00 UTC
    # New York: 12:00 - 21:00 UTC
    # Overlap: 12:00 - 16:00 UTC
    h_int = ts.dt.hour
    res["is_asian_session"] = ((h_int >= 0) & (h_int < 7)).astype(float)
    res["is_london_session"] = ((h_int >= 7) & (h_int < 16)).astype(float)
    res["is_ny_session"] = ((h_int >= 12) & (h_int < 21)).astype(float)
    res["is_london_ny_overlap"] = ((h_int >= 12) & (h_int < 16)).astype(float)

    # Minutes since midnight
    mins_day = ts.dt.hour * 60 + ts.dt.minute

    # London open: 07:00 UTC = 420 mins
    mins_from_london = mins_day - 420
    res["mins_to_london_open"] = np.maximum(0, -mins_from_london) / 420.0
    res["mins_since_london_open"] = np.maximum(0, mins_from_london) / 540.0

    # NY open: 12:00 UTC = 720 mins
    mins_from_ny = mins_day - 720
    res["mins_to_ny_open"] = np.maximum(0, -mins_from_ny) / 720.0
    res["mins_since_ny_open"] = np.maximum(0, mins_from_ny) / 540.0

    return res
