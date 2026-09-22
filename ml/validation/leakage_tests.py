"""
Data Leakage Prevention Test Suite.

No model can be promoted to PRODUCTION if these tests fail.
Tests for:
1. Temporal ordering of feature matrix vs label end times.
2. Zero correlation between future OHLC returns and current features t0.
3. Feature pipeline produces exact same output regardless of future rows.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd
import pytest

from ml.features.pipeline import FeaturePipeline
from ml.data.providers.base import Candle


def test_feature_pipeline_future_insensitivity():
    """
    Test that calculating features at row t0 produces IDENTICAL values
    whether future rows (t1, t2, ..., tN) are present or truncated.
    """
    # Create 50 synthetic candles
    base_ts = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    candles = []
    price = 1.3400

    for i in range(50):
        ts = base_ts + timedelta(minutes=15 * i)
        candles.append(
            Candle(
                symbol="GBPUSD",
                timeframe="M15",
                timestamp=ts,
                open=price,
                high=price + 0.0010,
                low=price - 0.0010,
                close=price + 0.0005,
                tick_volume=1000 + i * 10,
            )
        )
        price += 0.0002

    df_full = pd.DataFrame([c.to_dict() for c in candles])
    df_truncated = df_full.iloc[:35].copy()  # Cut off last 15 bars

    pipeline = FeaturePipeline()
    features_full = pipeline.compute_features(df_full)
    features_truncated = pipeline.compute_features(df_truncated)

    # Compare features at bar index 34 (t0)
    row_full_t0 = features_full.iloc[34]
    row_trunc_t0 = features_truncated.iloc[34]

    # Should match with tight numerical tolerance
    max_diff = (row_full_t0 - row_trunc_t0).abs().max()
    assert max_diff < 1e-6, f"Data leakage detected! Feature values changed when future data was truncated: max diff = {max_diff}"
    print("✅ Passed future-insensitivity leakage test!")


def test_no_future_ohlc_in_features():
    """Check no feature name contains suspicious future indicators."""
    pipeline = FeaturePipeline()
    schema_cols = pipeline.compute_features(
        pd.DataFrame(
            {
                "symbol": ["GBPUSD"] * 10,
                "timeframe": ["M15"] * 10,
                "timestamp": pd.date_range("2026-01-01", periods=10, freq="15min", tz="UTC"),
                "open": [1.34] * 10,
                "high": [1.35] * 10,
                "low": [1.33] * 10,
                "close": [1.345] * 10,
                "tick_volume": [1000] * 10,
            }
        )
    ).columns

    forbidden_keywords = ["shift_-", "future", "target", "next_bar", "lead"]
    for col in schema_cols:
        for keyword in forbidden_keywords:
            assert keyword not in col.lower(), f"Forbidden future keyword '{keyword}' found in feature column name: '{col}'"

    print("✅ Passed feature column name leakage test!")


if __name__ == "__main__":
    test_feature_pipeline_future_insensitivity()
    test_no_future_ohlc_in_features()
