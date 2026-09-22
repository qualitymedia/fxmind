"""
Models package — exports all SQLAlchemy models.

Import all models here so Alembic autogenerate can discover them.
"""

from apps.api.app.models.user import User
from apps.api.app.models.market import MarketCandle, MarketQuote
from apps.api.app.models.signal import Signal, SignalReason
from apps.api.app.models.economic import EconomicEvent
from apps.api.app.models.model_version import ModelVersion
from apps.api.app.models.alert import Alert, Notification, BacktestRun

__all__ = [
    "User",
    "MarketCandle",
    "MarketQuote",
    "Signal",
    "SignalReason",
    "EconomicEvent",
    "ModelVersion",
    "Alert",
    "Notification",
    "BacktestRun",
]
