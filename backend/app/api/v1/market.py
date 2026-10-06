"""
Market REST Endpoints:
GET /api/v1/market/GBPUSD
GET /api/v1/market/GBPUSD/candles
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.market import CandleResponse, MarketOverview
from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["market"])
market_service = MarketService()


@router.get("/{symbol}", response_model=MarketOverview)
async def get_market_overview(symbol: str = "GBPUSD") -> MarketOverview:
    """Get current market overview for symbol."""
    data = await market_service.get_overview(symbol.upper())
    return MarketOverview(**data)


@router.get("/{symbol}/candles", response_model=list[CandleResponse])
async def get_market_candles(
    symbol: str = "GBPUSD",
    timeframe: str = Query("M15", regex="^(M15|30m|H1)$"),
    limit: int = Query(100, ge=1, le=1000),
) -> list[CandleResponse]:
    """Get historical candles for chart rendering."""
    data = await market_service.get_candles(symbol.upper(), timeframe, limit)
    return [CandleResponse(**c) for c in data]


@router.get("/{symbol}/volume-profile")
async def get_volume_profile(symbol: str = "GBPUSD") -> dict:
    """Get rolling 24h Volume Profile, Point of Control (POC), and Value Area (VAH/VAL)."""
    return await market_service.get_volume_profile(symbol.upper())

