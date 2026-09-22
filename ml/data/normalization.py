"""
Market Data Normalization.

Converts arbitrary raw dictionaries or DataFrames into standard Candle objects.
Ensures provider-specific formats NEVER reach feature engineering.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from ml.data.providers.base import Candle


def normalize_to_candle(
    symbol: str,
    timeframe: str,
    timestamp: datetime | str | pd.Timestamp,
    open_p: float,
    high_p: float,
    low_p: float,
    close_p: float,
    tick_volume: int = 0,
) -> Candle:
    """Normalize candle inputs to immutable Candle dataclass in UTC."""
    if isinstance(timestamp, str):
        ts = pd.to_datetime(timestamp, utc=True).to_pydatetime()
    elif isinstance(timestamp, pd.Timestamp):
        ts = timestamp.tz_convert("UTC").to_pydatetime() if timestamp.tz is not None else timestamp.tz_localize("UTC").to_pydatetime()
    elif isinstance(timestamp, datetime):
        ts = timestamp.astimezone(timezone.utc) if timestamp.tzinfo is not None else timestamp.replace(tzinfo=timezone.utc)
    else:
        raise ValueError(f"Unsupported timestamp format: {type(timestamp)}")

    return Candle(
        symbol=symbol.upper().strip(),
        timeframe=timeframe.upper().strip(),
        timestamp=ts,
        open=float(open_p),
        high=float(high_p),
        low=float(low_p),
        close=float(close_p),
        tick_volume=int(tick_volume),
    )


def candles_to_dataframe(candles: list[Candle]) -> pd.DataFrame:
    """Convert a list of Candle objects into a pandas DataFrame."""
    if not candles:
        return pd.DataFrame(columns=["symbol", "timeframe", "timestamp", "open", "high", "low", "close", "tick_volume"])

    records = [c.to_dict() for c in candles]
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
