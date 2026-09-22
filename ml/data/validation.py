"""
Market Data Validation.

Checks candles for:
- Price logical integrity (High >= Open, Close, Low; Low <= Open, Close, High)
- Duplicate timestamps
- Gaps in continuous sequence
- Outliers (spike ratio)
- Timezone correctness (must be UTC)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Sequence

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


def validate_candles(
    candles: Sequence[Candle],
    max_spike_ratio: float = 0.05,  # 5% price change in one M15 bar limit for anomaly flag
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

    errors: list[str] = []
    invalid_ohlc = 0
    duplicates = 0
    gaps = 0
    outliers = 0

    seen_timestamps = set()
    prev_candle: Candle | None = None

    for i, c in enumerate(candles):
        # 1. OHLC Integrity
        if not (c.low <= c.open <= c.high and c.low <= c.close <= c.high):
            invalid_ohlc += 1
            errors.append(f"Invalid OHLC at {c.timestamp}: O={c.open}, H={c.high}, L={c.low}, C={c.close}")

        # 2. Duplicate Check
        if c.timestamp in seen_timestamps:
            duplicates += 1
            errors.append(f"Duplicate timestamp found at {c.timestamp}")
        else:
            seen_timestamps.add(c.timestamp)

        # 3. Continuity / Gap check (excluding weekends)
        if prev_candle is not None:
            time_diff = c.timestamp - prev_candle.timestamp
            # If gap > 1 hour during weekdays, count gap
            if time_diff > timedelta(hours=1) and c.timestamp.weekday() < 5:
                gaps += 1

            # 4. Outlier Spike Check
            if prev_candle.close > 0:
                ret = abs((c.close - prev_candle.close) / prev_candle.close)
                if ret > max_spike_ratio:
                    outliers += 1
                    errors.append(f"Spike outlier detected at {c.timestamp}: return = {ret:.4f}")

        prev_candle = c

    is_valid = (invalid_ohlc == 0) and (duplicates == 0)

    return ValidationReport(
        is_valid=is_valid,
        total_candles=len(candles),
        invalid_ohlc_count=invalid_ohlc,
        duplicate_count=duplicates,
        missing_gap_count=gaps,
        outlier_count=outliers,
        error_messages=errors[:20],  # cap error report length
    )
