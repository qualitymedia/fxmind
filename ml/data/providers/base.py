"""
Market Data Provider Abstraction.

Allows providers (Demo, CSV, OANDA, Yahoo, MT4/MT5) to be swapped
without rewriting the ML pipeline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence


@dataclass(frozen=True)
class Candle:
    """
    Normalized Candle object.
    
    Standard format across all data providers:
    Candle(symbol, timeframe, timestamp, open, high, low, close, tick_volume)
    """
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    tick_volume: int

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "tick_volume": self.tick_volume,
        }


@dataclass(frozen=True)
class Quote:
    """Normalized real-time quote object."""
    symbol: str
    bid: float
    ask: float
    spread: float
    timestamp: datetime


class MarketDataProvider(ABC):
    """Abstract base class for all market data providers."""

    @abstractmethod
    async def fetch_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> Sequence[Candle]:
        """Fetch historical candles for a symbol and timeframe."""
        pass

    @abstractmethod
    async def get_latest_quote(self, symbol: str) -> Quote:
        """Get the latest real-time quote."""
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check provider connectivity."""
        pass
