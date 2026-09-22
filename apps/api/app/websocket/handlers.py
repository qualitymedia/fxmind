"""
WebSocket route handlers for real-time market updates, signals, and notifications.
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from apps.api.app.websocket.manager import ws_manager

ws_router = APIRouter(tags=["websockets"])


@ws_router.websocket("/ws/market/{symbol}")
async def websocket_market(websocket: WebSocket, symbol: str):
    """Real-time market price and candle updates."""
    await ws_manager.connect(websocket, "market")
    try:
        while True:
            # Keepalive receiver loop
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "market")


@ws_router.websocket("/ws/signals")
async def websocket_signals(websocket: WebSocket):
    """Real-time AI signal updates."""
    await ws_manager.connect(websocket, "signals")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "signals")


@ws_router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """Real-time user notification alerts."""
    await ws_manager.connect(websocket, "notifications")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "notifications")
