"""
FastAPI application entry point for FXMind API.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.db.database import close_mongo_connection, connect_to_mongo
from app.services.data_bootstrap import seed_runtime_data
from app.workers.live_pipeline import live_worker

setup_logging()
logger = get_logger("fxmind.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    logger.info(
        f"app_startup app_name={settings.app_name} env={settings.app_env.value} demo_mode={settings.demo_mode}"
    )

    try:
        database = await connect_to_mongo()
        await seed_runtime_data(database)
    except Exception:
        await close_mongo_connection()
        raise

    # Start live continuous inference worker task
    worker_task = asyncio.create_task(live_worker.start())

    yield

    logger.info("app_shutdown")
    live_worker.stop()
    worker_task.cancel()
    await close_mongo_connection()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="GBP/USD market analysis API",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Exception Handlers
    register_exception_handlers(app)

    # Mount API routers
    app.include_router(api_v1_router)

    return app


app = create_app()
