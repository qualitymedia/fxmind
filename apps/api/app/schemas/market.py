"""
Market data Pydantic schemas for FXMind.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CandleResponse(BaseModel):
    """Normalized candle data response."""
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    tick_volume: int

    model_config = {"from_attributes": True}


class QuoteResponse(BaseModel):
    """Market quote response."""
    symbol: str
    bid: float
    ask: float
    spread: float
    timestamp: datetime

    model_config = {"from_attributes": True}


class MarketOverview(BaseModel):
    """Market overview for a symbol."""
    symbol: str
    current_price: float
    bid: float
    ask: float
    spread: float
    change: float = Field(..., description="Price change from previous close")
    change_percent: float = Field(..., description="Percentage change")
    high_24h: float
    low_24h: float
    session: str = Field(..., description="Current trading session")
    is_live: bool = Field(..., description="Whether data is live or stale")
    last_updated: datetime
    timeframe: str = "M15"


class CandlesQuery(BaseModel):
    """Query parameters for candle data."""
    timeframe: str = "M15"
    limit: int = Field(100, ge=1, le=1000)
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class CrossMarketContext(BaseModel):
    """Cross-market correlation context."""
    symbol: str
    current_value: float
    change_percent: float
    bias: Optional[str] = None  # BULLISH, BEARISH, NEUTRAL
    correlation_note: Optional[str] = None
