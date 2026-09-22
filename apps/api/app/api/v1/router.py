"""
V1 API Router for FXMind.
Aggregates all REST endpoints and WebSockets.
"""

from fastapi import APIRouter

from apps.api.app.api.v1 import (
    alerts,
    analysis,
    calendar,
    health,
    logs,
    market,
    models,
    notifications,
    performance,
    signals,
)
from apps.api.app.websocket.handlers import ws_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health.router)
api_v1_router.include_router(market.router)
api_v1_router.include_router(analysis.router)
api_v1_router.include_router(signals.router)
api_v1_router.include_router(calendar.router)
api_v1_router.include_router(performance.router)
api_v1_router.include_router(models.router)
api_v1_router.include_router(alerts.router)
api_v1_router.include_router(notifications.router)
api_v1_router.include_router(logs.router)
api_v1_router.include_router(ws_router)
