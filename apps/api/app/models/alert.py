"""
Alert and notification models for FXMind.

Supports: new bullish/bearish setup, entry zone reached,
regime change, high-impact event approaching, setup invalidated.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.app.db.database import Base
from apps.api.app.models.base import TimestampMixin


class Alert(Base, TimestampMixin):
    """
    User-configured alert rule.
    
    Alert types:
    - NEW_BULLISH_SETUP
    - NEW_BEARISH_SETUP
    - ENTRY_ZONE_REACHED
    - REGIME_CHANGE
    - HIGH_IMPACT_EVENT
    - SETUP_INVALIDATED
    """

    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alert_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), default="GBPUSD", nullable=False)
    min_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class Notification(Base, TimestampMixin):
    """
    Notification sent to a user when an alert fires.
    """

    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notification_user", "user_id"),
        Index("ix_notification_read", "is_read"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    alert_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("alerts.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class BacktestRun(Base, TimestampMixin):
    """
    Backtest execution record.
    
    Tracks configuration, date ranges, and performance metrics
    for each backtest run.
    """

    __tablename__ = "backtest_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    config_json: Mapped[str] = mapped_column(Text, nullable=False)

    # Results
    total_trades: Mapped[int | None] = mapped_column(Integer, nullable=True)
    win_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    profit_factor: Mapped[float | None] = mapped_column(Float, nullable=True)
    sharpe_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    sortino_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    calmar_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[float | None] = mapped_column(Float, nullable=True)
    expectancy: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_win: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    results_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    equity_curve_json: Mapped[str | None] = mapped_column(Text, nullable=True)
