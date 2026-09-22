"""
Notifications REST Endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["notifications"])

_NOTIFICATIONS = [
    {
        "id": 1,
        "title": "New Bullish Setup Detected",
        "message": "GBP/USD M15 Bullish Bias with 68% calibrated confidence",
        "notification_type": "NEW_BULLISH_SETUP",
        "is_read": False,
        "created_at": "2026-09-08T17:40:00Z",
    },
    {
        "id": 2,
        "title": "High Impact Event Approaching",
        "message": "USD CPI in 12 minutes. AI Signal Paused.",
        "notification_type": "HIGH_IMPACT_EVENT",
        "is_read": True,
        "created_at": "2026-09-08T17:18:00Z",
    },
]


@router.get("")
async def list_notifications():
    return _NOTIFICATIONS


@router.patch("/{id}/read")
async def mark_read(id: int):
    for n in _NOTIFICATIONS:
        if n["id"] == id:
            n["is_read"] = True
            return n
    return {"message": "Notification updated"}
