"""
Health endpoint for FXMind.

Returns comprehensive system status including database,
market data, and model availability.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.config import get_settings
from apps.api.app.db.database import get_db
from apps.api.app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    System health check.
    
    Returns the status of all critical subsystems:
    - database: PostgreSQL connection
    - market_data: Data availability and freshness
    - model: ML model availability
    """
    settings = get_settings()

    # Check database
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # Check market data availability
    market_status = "healthy"
    last_market_update = None
    try:
        result = await db.execute(
            text(
                "SELECT MAX(timestamp) FROM market_candles "
                "WHERE symbol = 'GBPUSD'"
            )
        )
        last_market_update = result.scalar_one_or_none()
        if last_market_update is None:
            market_status = "no_data"
    except Exception:
        market_status = "unavailable"

    # Check model availability
    model_status = "healthy"
    model_version = None
    last_prediction = None
    try:
        result = await db.execute(
            text(
                "SELECT version FROM model_versions "
                "WHERE state = 'PRODUCTION' "
                "ORDER BY created_at DESC LIMIT 1"
            )
        )
        model_version = result.scalar_one_or_none()
        if model_version is None:
            model_status = "no_model"

        result = await db.execute(
            text(
                "SELECT MAX(timestamp) FROM signals "
                "WHERE symbol = 'GBPUSD'"
            )
        )
        last_prediction = result.scalar_one_or_none()
    except Exception:
        model_status = "unavailable"

    # Overall status
    overall = "healthy"
    if db_status != "healthy":
        overall = "degraded"
    elif market_status not in ("healthy",):
        overall = "degraded"
    elif model_status not in ("healthy",):
        overall = "degraded"

    return HealthResponse(
        status=overall,
        database=db_status,
        market_data=market_status,
        model=model_status,
        model_version=model_version,
        last_market_update=last_market_update,
        last_prediction=last_prediction,
        demo_mode=settings.demo_mode,
        timestamp=datetime.now(timezone.utc),
    )
