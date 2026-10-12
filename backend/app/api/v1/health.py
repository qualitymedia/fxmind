"""Health endpoint for FXMind."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, Depends
from pymongo.errors import PyMongoError
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.database import get_db
from app.models.signal import Signal
from app.schemas.common import HealthResponse
from ml.artifacts.saver import ModelArtifactSaver

router = APIRouter(tags=["health"])
logger = get_logger("fxmind.health")


@router.get("/health", response_model=HealthResponse)
async def health_check(database: AsyncDatabase = Depends(get_db)) -> HealthResponse:
    """Report database connectivity, available market data, and model status."""
    settings = get_settings()
    db_status = "healthy"
    market_status = "healthy"
    model_status = "healthy"
    model_version = None
    last_market_update = None
    last_prediction = None

    try:
        await database.command("ping")
        candle = await database["market_candles"].find_one(
            {"symbol": "GBPUSD"},
            projection={"timestamp": 1},
            sort=[("timestamp", -1)],
        )
        if candle:
            last_market_update = candle.get("timestamp")
        else:
            market_file = settings.project_root / "data" / "parquet" / "GBPUSD_M15.parquet"
            if market_file.exists():
                df = pd.read_parquet(market_file)
                if not df.empty:
                    last_market_update = pd.to_datetime(df["timestamp"]).max().to_pydatetime()
                else:
                    market_status = "no_data"
            else:
                market_status = "no_data"

        try:
            bundle = ModelArtifactSaver().load_bundle()
            model_version = bundle.get("version")
            if model_version is None:
                model_status = "unavailable"
        except Exception:
            logger.exception("model_artifact_load_failed")
            model_status = "unavailable"

        signal = await database[Signal.collection].find_one(
            {"symbol": "GBPUSD"},
            projection={"timestamp": 1},
            sort=[("timestamp", -1)],
        )
        last_prediction = signal.get("timestamp") if signal else None
    except PyMongoError:
        db_status = "unhealthy"
        market_status = "unknown"
        model_status = "unknown"

    overall = "healthy"
    if db_status != "healthy" or market_status != "healthy" or model_status != "healthy":
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
