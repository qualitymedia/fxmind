"""
Signal and signal reason models for FXMind.

Signals represent ML-generated analysis outputs.
NO_TRADE is a first-class signal status, not an error.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.app.db.database import Base
from apps.api.app.models.base import TimestampMixin


class Signal(Base, TimestampMixin):
    """
    AI-generated market analysis signal.
    
    Each signal captures the complete analysis state at the time of
    an M15 candle close, including probabilities, regime, setup, and reasons.
    """

    __tablename__ = "signals"
    __table_args__ = (
        Index("ix_signal_symbol_ts", "symbol", "timestamp"),
        Index("ix_signal_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False, default="M15")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # AI Analysis
    bias: Mapped[str] = mapped_column(
        SAEnum("BULLISH", "BEARISH", "NEUTRAL", name="bias_enum", create_constraint=False),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    regime: Mapped[str] = mapped_column(
        SAEnum("TRENDING", "RANGING", "HIGH_VOLATILITY", "ILLIQUID", name="regime_enum", create_constraint=False),
        nullable=False,
    )

    # Calibrated Probabilities
    bull_probability: Mapped[float] = mapped_column(Float, nullable=False)
    bear_probability: Mapped[float] = mapped_column(Float, nullable=False)
    neutral_probability: Mapped[float] = mapped_column(Float, nullable=False)

    # Trade Setup (null if NO_TRADE)
    status: Mapped[str] = mapped_column(
        SAEnum(
            "ACTIVE", "TARGET_HIT", "STOP_HIT", "EXPIRED",
            "INVALIDATED", "NO_TRADE",
            name="signal_status_enum", create_constraint=False,
        ),
        nullable=False,
    )
    direction: Mapped[str | None] = mapped_column(String(10), nullable=True)
    entry_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    entry_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    stop_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    take_profit: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_reward: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Market Context
    atr14: Mapped[float | None] = mapped_column(Float, nullable=True)
    spread: Mapped[float | None] = mapped_column(Float, nullable=True)
    session_name: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Filters
    news_clear: Mapped[bool | None] = mapped_column(nullable=True)
    liquidity_ok: Mapped[bool | None] = mapped_column(nullable=True)
    spread_ok: Mapped[bool | None] = mapped_column(nullable=True)

    # Model
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)

    # Explanation (JSON string of SHAP evidence categories)
    explanation_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Outcome tracking
    outcome: Mapped[str | None] = mapped_column(String(20), nullable=True)
    outcome_pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    outcome_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    reasons: Mapped[list["SignalReason"]] = relationship(
        "SignalReason", back_populates="signal", cascade="all, delete-orphan"
    )


class SignalReason(Base):
    """
    Individual reason for a signal decision.
    
    Captures why a signal was generated or why NO_TRADE was decided.
    Uses actual feature/model evidence, never fabricated explanations.
    """

    __tablename__ = "signal_reasons"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    signal_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sentiment: Mapped[str | None] = mapped_column(
        SAEnum("SUPPORTIVE", "NEUTRAL", "OPPOSING", "CLEAR", name="sentiment_enum", create_constraint=False),
        nullable=True,
    )

    # Relationships
    signal: Mapped["Signal"] = relationship("Signal", back_populates="reasons")
