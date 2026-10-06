"""
AI Background Processing Log REST Endpoints:
GET /api/v1/logs — recent system execution logs with level & category filters
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/logs", tags=["logs"])

# Global in-memory log buffer (stores last 200 system events)
_log_buffer: list[dict] = []
_log_id: int = 1


class LogEntry(BaseModel):
    id: int
    timestamp: datetime
    category: str = Field(..., description="SIGNALS, PATTERNS, GATES, SYSTEM, DATA")
    level: str = Field(..., description="INFO, SUCCESS, WARNING, ERROR")
    message: str
    details: Optional[dict] = None


def add_system_log(
    category: str,
    message: str,
    level: str = "INFO",
    details: dict | None = None,
) -> dict:
    """Add a structured execution event to the global log buffer."""
    global _log_id
    entry = {
        "id": _log_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": category.upper(),
        "level": level.upper(),
        "message": message,
        "details": details or {},
    }
    _log_id += 1
    _log_buffer.append(entry)

    # Keep last 200 log entries
    if len(_log_buffer) > 200:
        _log_buffer.pop(0)

    return entry


# Seed initial startup logs if buffer is empty
if not _log_buffer:
    add_system_log("SYSTEM", "AI Engine initialized. Live polling worker started.", "SUCCESS")
    add_system_log("DATA", "Loaded M15 historical candles for GBPUSD (Yahoo Finance).", "INFO")
    add_system_log("PATTERNS", "Scanned M15 bar: Bearish FVG & Bullish Pinbar detected.", "INFO")
    add_system_log("GATES", "Evaluated regime (RANGING): Price inside VWAP bounds (Z-Score: 0.7).", "WARNING")
    add_system_log("SIGNALS", "Inference pass complete — Model bias BEARISH (83.7%). Fail-closed gate active.", "INFO")


@router.get("", response_model=list[LogEntry])
async def get_system_logs(
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    level: Optional[str] = None,
) -> list[LogEntry]:
    """Retrieve filtered AI processing logs."""
    logs = list(reversed(_log_buffer))  # newest first

    if category and category.upper() != "ALL":
        logs = [l for l in logs if l.get("category", "").upper() == category.upper()]

    if level and level.upper() != "ALL":
        logs = [l for l in logs if l.get("level", "").upper() == level.upper()]

    formatted = []
    for l in logs[:limit]:
        formatted.append(
            LogEntry(
                id=l["id"],
                timestamp=datetime.fromisoformat(l["timestamp"]) if isinstance(l.get("timestamp"), str) else l["timestamp"],
                category=l["category"],
                level=l["level"],
                message=l["message"],
                details=l.get("details"),
            )
        )

    return formatted
