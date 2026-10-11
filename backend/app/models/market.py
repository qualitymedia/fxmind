"""MongoDB documents for market data."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from app.models.base import MongoDocument


class MarketCandle(MongoDocument):
    """OHLCV candle stored separately to keep the time series unbounded."""

    collection: ClassVar[str] = "market_candles"
    id: int
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    tick_volume: int = 0


class MarketQuote(MongoDocument):
    """Market quote snapshot."""

    collection: ClassVar[str] = "market_quotes"
    symbol: str
    bid: float
    ask: float
    spread: float
    timestamp: datetime
