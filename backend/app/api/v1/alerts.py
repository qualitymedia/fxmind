"""
Alerts REST Endpoints (CRUD).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/alerts", tags=["alerts"])

# In-memory store for demo
_ALERTS = [
    {
        "id": 1,
        "symbol": "GBPUSD",
        "alert_type": "NEW_BULLISH_SETUP",
        "min_confidence": 0.65,
        "enabled": True,
    },
    {
        "id": 2,
        "symbol": "GBPUSD",
        "alert_type": "HIGH_IMPACT_EVENT",
        "min_confidence": None,
        "enabled": True,
    },
]


@router.get("")
async def list_alerts():
    return _ALERTS


@router.post("")
async def create_alert(alert: dict):
    new_id = max([a["id"] for a in _ALERTS], default=0) + 1
    alert["id"] = new_id
    _ALERTS.append(alert)
    return alert


@router.patch("/{id}")
async def update_alert(id: int, update_data: dict):
    match = next((a for a in _ALERTS if a["id"] == id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Alert not found")
    match.update(update_data)
    return match


@router.delete("/{id}")
async def delete_alert(id: int):
    global _ALERTS
    _ALERTS = [a for a in _ALERTS if a["id"] != id]
    return {"message": f"Alert {id} deleted"}
