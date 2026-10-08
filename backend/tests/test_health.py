"""
Tests for health endpoint and market validation.
"""

import pandas as pd
import pytest
from httpx import AsyncClient

from ml.data.validation import validate_market_dataframe


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test health check returns HTTP 200 with expected structure."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "market_data" in data
    assert "model" in data
    assert "timestamp" in data

    # Regression: the restructure should not leave the database empty when the parquet
    # files and model bundle are still present in the project.
    assert data["market_data"] == "healthy"
    assert data["model"] == "healthy"


def test_market_dataframe_rejects_invalid_price_data():
    """Invalid OHLC should be rejected before trading or training begins."""
    bad_df = pd.DataFrame([
        {
            "timestamp": "2026-10-01T00:00:00Z",
            "open": 1.0,
            "high": 1.2,
            "low": 1.3,
            "close": 1.1,
            "tick_volume": 200,
        },
    ])

    report = validate_market_dataframe(bad_df, symbol="GBPUSD", timeframe="M15")
    assert report.is_valid is False
    assert report.invalid_ohlc_count >= 1
    assert "Invalid OHLC" in report.error_messages[0]
