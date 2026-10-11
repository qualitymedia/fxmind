"""
Alerts REST Endpoints (CRUD).
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.api.deps import require_authenticated_user_features
from app.db.database import get_db, next_document_id
from app.models.alert import Alert
from app.models.base import from_mongo, to_mongo

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    dependencies=[Depends(require_authenticated_user_features)],
)


def _alert_response(alert: Alert) -> dict:
    """Keep the public alert response compact and API-compatible."""
    return {
        "id": alert.id,
        "symbol": alert.symbol,
        "alert_type": alert.alert_type,
        "min_confidence": alert.min_confidence,
        "enabled": alert.enabled,
    }


@router.get("")
async def list_alerts(database: AsyncDatabase = Depends(get_db)):
    cursor = database[Alert.collection].find().sort("_id", 1)
    documents = await cursor.to_list(length=500)
    alerts = [
        alert
        for document in documents
        if (alert := from_mongo(Alert, document)) is not None
    ]
    return [_alert_response(alert) for alert in alerts]


@router.post("")
async def create_alert(alert: dict, database: AsyncDatabase = Depends(get_db)):
    if not alert.get("alert_type"):
        raise HTTPException(status_code=422, detail="alert_type is required")
    document = Alert(
        id=await next_document_id(database, Alert.collection),
        user_id=int(alert.get("user_id", 0)),
        alert_type=alert["alert_type"],
        symbol=alert.get("symbol", "GBPUSD"),
        min_confidence=alert.get("min_confidence"),
        enabled=alert.get("enabled", True),
        config_json=alert.get("config_json"),
    )
    await database[Alert.collection].insert_one(to_mongo(document))
    return _alert_response(document)


@router.patch("/{id}")
async def update_alert(
    id: int,
    update_data: dict,
    database: AsyncDatabase = Depends(get_db),
):
    updates = {
        key: value
        for key, value in update_data.items()
        if key in {"alert_type", "symbol", "min_confidence", "enabled", "config_json"}
    }
    updates["updated_at"] = datetime.now(timezone.utc)
    updated = await database[Alert.collection].find_one_and_update(
        {"_id": id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    alert = from_mongo(Alert, updated)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _alert_response(alert)


@router.delete("/{id}")
async def delete_alert(id: int, database: AsyncDatabase = Depends(get_db)):
    await database[Alert.collection].delete_one({"_id": id})
    return {"message": f"Alert {id} deleted"}
