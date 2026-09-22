"""
FastAPI application entry point for FXMind API.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.api.v1.router import api_v1_router
from apps.api.app.core.config import get_settings
from apps.api.app.core.exceptions import register_exception_handlers
from apps.api.app.core.logging import get_logger, setup_logging
from apps.api.app.db.database import dispose_engine, init_db
from apps.api.app.workers.live_pipeline import live_worker

setup_logging()
logger = get_logger("fxmind.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    logger.info(
        f"app_startup app_name={settings.app_name} env={settings.app_env.value} demo_mode={settings.demo_mode}"
    )

    # Initialize DB tables
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"init_db warning: {e}")

    # Start live continuous inference worker task
    worker_task = asyncio.create_task(live_worker.start())

    yield

    logger.info("app_shutdown")
    live_worker.stop()
    worker_task.cancel()
    await dispose_engine()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="GBP/USD AI Market Analysis Assistant API",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    register_exception_handlers(app)

    # Mount API routers
    app.include_router(api_v1_router)

    return app


app = create_app()
