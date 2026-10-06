"""
Paper Trading REST Endpoints:
GET /api/v1/paper-trading/positions — open paper positions (live, in-memory)
GET /api/v1/paper-trading/history   — closed trade history (DB-backed, survives restarts)
GET /api/v1/paper-trading/summary   — live equity, win rate, total PnL
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.paper_trading import paper_trading_engine

router = APIRouter(prefix="/paper-trading", tags=["paper-trading"])


@router.get("/positions")
async def get_open_positions():
    """Get active, unclosed paper positions (in-memory, live)."""
    return paper_trading_engine.get_open_positions()


@router.get("/history")
async def get_trade_history(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Get history of completed paper trades from the database.
    DB-backed — survives server restarts.
    Only returns signals that had an actual active trade (with entry prices).
    """
    return await paper_trading_engine.get_history_from_db(db, limit=limit)


@router.get("/summary")
async def get_trading_summary():
    """Get aggregate paper trading performance summary."""
    return paper_trading_engine.get_closed_summary()
