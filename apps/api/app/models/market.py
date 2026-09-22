"""
Market data models for FXMind.

Normalized candle format: Candle(symbol, timeframe, timestamp, open, high, low, close, tick_volume)
All timestamps in UTC. Tick volume is NOT centralized FX volume.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.app.db.database import Base
from apps.api.app.models.base import TimestampMixin


class MarketCandle(Base, TimestampMixin):
    """
    OHLCV candle data in normalized format.
    
    All providers are normalized to this format before storage.
    Provider-specific formats must not leak into feature engineering.
    """

    __tablename__ = "market_candles"
    __table_args__ = (
        UniqueConstraint("symbol", "timeframe", "timestamp", name="uq_candle"),
        Index("ix_candle_symbol_tf_ts", "symbol", "timeframe", "timestamp"),
        Index("ix_candle_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    tick_volume: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class MarketQuote(Base, TimestampMixin):
    """
    Latest market quote (bid/ask/spread).
    
    Updated in real-time for spread monitoring and freshness tracking.
    """

    __tablename__ = "market_quotes"
    __table_args__ = (
        Index("ix_quote_symbol", "symbol"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    bid: Mapped[float] = mapped_column(Float, nullable=False)
    ask: Mapped[float] = mapped_column(Float, nullable=False)
    spread: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
