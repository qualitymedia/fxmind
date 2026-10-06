"""
Economic Calendar REST Endpoints:
GET /api/v1/calendar
GET /api/v1/calendar/upcoming
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("")
async def get_economic_calendar():
    """Get full economic calendar events."""
    return [
        {"id": 1, "time": "12:30 UTC", "currency": "USD", "event": "CPI (MoM)", "importance": "HIGH", "actual": None, "forecast": "0.3%", "previous": "0.2%"},
        {"id": 2, "time": "14:00 UTC", "currency": "USD", "event": "FOMC Member Speech", "importance": "MEDIUM", "actual": None, "forecast": None, "previous": None},
        {"id": 3, "time": "15:30 UTC", "currency": "GBP", "event": "BoE Governor Speech", "importance": "MEDIUM", "actual": None, "forecast": None, "previous": None},
        {"id": 4, "time": "16:00 UTC", "currency": "USD", "event": "Consumer Confidence", "importance": "LOW", "actual": None, "forecast": "101.2", "previous": "100.4"},
    ]


@router.get("/upcoming")
async def get_upcoming_high_impact():
    """Get upcoming high-impact risk events."""
    return [
        {"id": 1, "time": "12:30 UTC", "currency": "USD", "event": "CPI (MoM)", "importance": "HIGH", "minutes_away": 12},
    ]
