"""
Market Data Validation.

Checks candles for:
- Price logical integrity (High >= Open, Close, Low; Low <= Open, Close, High)
- Duplicate timestamps
- Gaps in continuous sequence
- Outliers (spike ratio)
- Timezone correctness (must be UTC)
- Nulls, stale data, and impossible feature inputs
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Sequence

import pandas as pd

from ml.data.providers.base import Candle


@dataclass
class ValidationReport:
    """Summary of data validation results."""
    is_valid: bool
    total_candles: int
    invalid_ohlc_count: int
    duplicate_count: int
    missing_gap_count: int
    outlier_count: int
    error_messages: list[str]


def _as_utc_timestamp(value: Any) -> datetime:
    ts = pd.to_datetime(value, utc=True)
    if pd.isna(ts):
        raise ValueError("Timestamp cannot be null")
    return ts.to_pydatetime()


def validate_market_dataframe(
    df: pd.DataFrame,
    symbol: str = "GBPUSD",
    timeframe: str = "M15",
    max_gap_hours: int = 24,
    max_spike_ratio: float = 0.05,
    max_staleness_minutes: int = 90,
) -> ValidationReport:
    """Validate a market dataframe before training or inference."""
    if df is None or df.empty:
        return ValidationReport(
            is_valid=False,
            total_candles=0,
            invalid_ohlc_count=0,
            duplicate_count=0,
            missing_gap_count=0,
            outlier_count=0,
            error_messages=[f"No market data found for {symbol} {timeframe}"],
        )

    errors: list[str] = []
    warnings: list[str] = []
    required_cols = {"timestamp", "open", "high", "low", "close", "tick_volume"}
    missing = sorted(required_cols - set(df.columns))
    if missing:
        return ValidationReport(
            is_valid=False,
            total_candles=len(df),
            invalid_ohlc_count=0,
            duplicate_count=0,
            missing_gap_count=0,
            outlier_count=0,
            error_messages=[f"Missing required columns for {symbol} {timeframe}: {', '.join(missing)}"],
        )

    working = df.copy()
    working["timestamp"] = pd.to_datetime(working["timestamp"], utc=True, errors="coerce")
    working = working.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    if working.empty:
        return ValidationReport(
            is_valid=False,
            total_candles=0,
            invalid_ohlc_count=0,
            duplicate_count=0,
            missing_gap_count=0,
            outlier_count=0,
            error_messages=[f"Market data timestamps are invalid for {symbol} {timeframe}"],
        )

    for col in ["open", "high", "low", "close", "tick_volume"]:
        if working[col].isna().any():
            bad_rows = int(working[col].isna().sum())
            errors.append(f"Null values found in {col} ({bad_rows} rows)")

    invalid_ohlc = 0
    duplicates = 0
    gaps = 0
    outliers = 0
    seen_timestamps = set()
    prev_row: pd.Series | None = None

    for _, row in working.iterrows():
        try:
            ts = row["timestamp"]
            o = float(row["open"])
            h = float(row["high"])
            l = float(row["low"])
            c = float(row["close"])
            vol = float(row["tick_volume"])
        except (TypeError, ValueError):
            invalid_ohlc += 1
            errors.append(f"Invalid numeric OHLC or volume at timestamp {row.get('timestamp')}")
            continue

        if not (l <= o <= h and l <= c <= h):
            invalid_ohlc += 1
            errors.append(f"Invalid OHLC at {ts}: O={o}, H={h}, L={l}, C={c}")

        if pd.isna(ts) or ts in seen_timestamps:
            duplicates += 1
            errors.append(f"Duplicate or invalid timestamp found at {ts}")
        else:
            seen_timestamps.add(ts)

        if prev_row is not None:
            prev_ts = prev_row["timestamp"]
            if pd.notna(prev_ts) and pd.notna(ts):
                diff = ts - prev_ts
                if diff > pd.Timedelta(hours=max_gap_hours) and ts.weekday() < 5:
                    gaps += 1
                    warnings.append(f"Large time gap detected between {prev_ts} and {ts}")

                prev_close = float(prev_row["close"])
                if prev_close > 0:
                    ret = abs((c - prev_close) / prev_close)
                    if ret > max_spike_ratio:
                        outliers += 1
                        errors.append(f"Price spike detected at {ts}: return = {ret:.4f}")

        prev_row = row

    latest_ts = working["timestamp"].max()
    now_utc = datetime.now(timezone.utc)
    if latest_ts.tzinfo is None:
        latest_ts = latest_ts.replace(tzinfo=timezone.utc)
    if (now_utc - latest_ts).total_seconds() > max_staleness_minutes * 60:
        errors.append(
            f"Market data is stale: latest candle is {latest_ts.isoformat()} while now is {now_utc.isoformat()}"
        )

    is_valid = (invalid_ohlc == 0) and (duplicates == 0) and (not errors)
    merged_errors = errors[:20]
    if warnings:
        merged_errors.extend(warnings[:5])

    return ValidationReport(
        is_valid=is_valid,
        total_candles=len(working),
        invalid_ohlc_count=invalid_ohlc,
        duplicate_count=duplicates,
        missing_gap_count=gaps,
        outlier_count=outliers,
        error_messages=merged_errors,
    )


def validate_candles(
    candles: Sequence[Candle],
    max_spike_ratio: float = 0.05,
    max_staleness_minutes: int = 90,
) -> ValidationReport:
    """
    Validate sequence of candles for logical integrity and continuity.
    """
    if not candles:
        return ValidationReport(
            is_valid=False,
            total_candles=0,
            invalid_ohlc_count=0,
            duplicate_count=0,
            missing_gap_count=0,
            outlier_count=0,
            error_messages=["No candles provided"],
        )

    rows = []
    for c in candles:
        rows.append({
            "symbol": getattr(c, "symbol", "GBPUSD"),
            "timeframe": getattr(c, "timeframe", "M15"),
            "timestamp": _as_utc_timestamp(c.timestamp),
            "open": float(c.open),
            "high": float(c.high),
            "low": float(c.low),
            "close": float(c.close),
            "tick_volume": int(getattr(c, "tick_volume", 0) or 0),
        })

    return validate_market_dataframe(
        pd.DataFrame(rows),
        symbol=rows[0]["symbol"],
        timeframe=rows[0]["timeframe"],
        max_spike_ratio=max_spike_ratio,
        max_staleness_minutes=max_staleness_minutes,
    )
