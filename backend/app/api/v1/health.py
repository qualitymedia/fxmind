"""
Health endpoint for FXMind.

Returns comprehensive system status including database,
market data, and model availability.
"""

from __future__ import annotations

import asyncio
import sqlite3
from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthResponse
from ml.artifacts.saver import ModelArtifactSaver

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Lightweight system health check — does NOT use the async session pool
    so it always responds even when the live worker holds the write lock.
    """
    settings = get_settings()

    def _check_db():
        """Run direct sqlite3 checks in a thread (bypasses async pool contention)."""
        db_status = "healthy"
        market_status = "healthy"
        model_status = "healthy"
        model_version = None
        last_market_update = None
        last_prediction = None

        try:
            db_path = (settings.project_root / "data" / "fxmind.db").resolve()
            if not db_path.exists():
                return "no_db", "no_data", "no_model", None, None, None

            conn = sqlite3.connect(str(db_path), timeout=5)
            conn.row_factory = sqlite3.Row
            try:
                # Test DB connectivity
                conn.execute("SELECT 1").fetchone()

                # Check market data
                row = conn.execute(
                    "SELECT MAX(timestamp) FROM market_candles WHERE symbol = 'GBPUSD'"
                ).fetchone()
                last_market_update = row[0] if row else None
                if last_market_update is None:
                    market_file = settings.project_root / "data" / "parquet" / "GBPUSD_M15.parquet"
                    if market_file.exists():
                        try:
                            df = pd.read_parquet(market_file)
                            if not df.empty:
                                last_market_update = pd.to_datetime(df["timestamp"]).max().to_pydatetime()
                                market_status = "healthy"
                            else:
                                market_status = "no_data"
                        except Exception:
                            market_status = "no_data"
                    else:
                        market_status = "no_data"
                else:
                    market_status = "healthy"

                # Check model
                row = conn.execute(
                    "SELECT version FROM model_versions WHERE state = 'PRODUCTION' ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
                model_version = row[0] if row else None
                if model_version is None:
                    try:
                        bundle = ModelArtifactSaver().load_bundle()
                        candidate = bundle.get("version") if isinstance(bundle, dict) else None
                    except Exception:
                        candidate = None
                    if candidate:
                        model_version = candidate
                        model_status = "healthy"
                    else:
                        model_status = "no_model"
                else:
                    model_status = "healthy"

                # Last prediction
                row = conn.execute(
                    "SELECT MAX(timestamp) FROM signals WHERE symbol = 'GBPUSD'"
                ).fetchone()
                last_prediction = row[0] if row else None

            finally:
                conn.close()

        except Exception as e:
            db_status = "unhealthy"

        return db_status, market_status, model_status, model_version, last_market_update, last_prediction

    loop = asyncio.get_running_loop()
    db_status, market_status, model_status, model_version, last_market_update, last_prediction = \
        await loop.run_in_executor(None, _check_db)

    # Overall status
    overall = "healthy"
    if db_status != "healthy":
        overall = "degraded"
    elif market_status not in ("healthy",):
        overall = "degraded"
    elif model_status not in ("healthy", "no_model"):
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
