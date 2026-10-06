"""
Economic event model for FXMind.

Tracks economic calendar events with timestamps, currencies,
importance levels, and actual/forecast/previous values.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.base import TimestampMixin


class EconomicEvent(Base, TimestampMixin):
    """
    Economic calendar event.
    
    Recognized high-impact events: CPI, NFP, FOMC, BoE, GDP,
    Retail Sales, PMI, Employment, Rate Decisions.
    """

    __tablename__ = "economic_events"
    __table_args__ = (
        Index("ix_econ_event_ts", "timestamp"),
        Index("ix_econ_event_currency", "currency"),
        Index("ix_econ_event_importance", "importance"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    event: Mapped[str] = mapped_column(String(255), nullable=False)
    importance: Mapped[str] = mapped_column(String(20), nullable=False)  # HIGH, MEDIUM, LOW
    actual: Mapped[float | None] = mapped_column(Float, nullable=True)
    forecast: Mapped[float | None] = mapped_column(Float, nullable=True)
    previous: Mapped[float | None] = mapped_column(Float, nullable=True)
    event_code: Mapped[str | None] = mapped_column(String(50), nullable=True)  # CPI, NFP, etc.
