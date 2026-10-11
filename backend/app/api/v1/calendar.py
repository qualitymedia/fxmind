"""
Economic Calendar REST Endpoints:
GET /api/v1/calendar
GET /api/v1/calendar/upcoming
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.finance_calendar_service import finance_calendar_service

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("")
async def get_economic_calendar(
    days: int = Query(default=14, ge=1, le=90),
) -> list[dict[str, object]]:
    """Return upcoming GBP/USD events from FinanceCalendar.com."""
    try:
        return await finance_calendar_service.get_events(days)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Economic calendar feed is temporarily unavailable.") from exc


@router.get("/upcoming")
async def get_upcoming_high_impact(
    days: int = Query(default=7, ge=1, le=90),
) -> list[dict[str, object]]:
    """Return upcoming high-impact GBP/USD events from FinanceCalendar.com."""
    try:
        return await finance_calendar_service.get_events(days, high_impact_only=True)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Economic calendar feed is temporarily unavailable.") from exc
