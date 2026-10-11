"""MongoDB document for economic calendar events."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Optional

from app.models.base import MongoDocument


class EconomicEvent(MongoDocument):
    """Economic calendar event with market-impact context."""

    collection: ClassVar[str] = "economic_events"
    timestamp: datetime
    currency: str
    event: str
    importance: str
    actual: Optional[float] = None
    forecast: Optional[float] = None
    previous: Optional[float] = None
    event_code: Optional[str] = None
