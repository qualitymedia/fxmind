"""
WebSocket Connection Manager.

Manages active connections across channels:
- market:GBPUSD
- signals
- notifications
"""

from __future__ import annotations

import json
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket clients and broadcasts channel updates."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {
            "market": [],
            "signals": [],
            "notifications": [],
        }

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections and websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)

    async def broadcast(self, channel: str, message: dict[str, Any]):
        """Broadcast JSON message to all connected clients on channel."""
        if channel not in self.active_connections:
            return

        dead_sockets = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_sockets.append(connection)

        # Cleanup dead sockets
        for dead in dead_sockets:
            self.disconnect(dead, channel)


ws_manager = ConnectionManager()
