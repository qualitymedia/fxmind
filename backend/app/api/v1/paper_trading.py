"""
Paper Trading REST Endpoints:
GET /api/v1/paper-trading/positions — open paper positions (MongoDB-backed)
GET /api/v1/paper-trading/history   — closed trade history (DB-backed, survives restarts)
GET /api/v1/paper-trading/summary   — live equity, win rate, total PnL
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pymongo.asynchronous.database import AsyncDatabase

from app.db.database import get_db
from app.services.paper_trading import paper_trading_engine

router = APIRouter(prefix="/paper-trading", tags=["paper-trading"])


@router.get("/positions")
async def get_open_positions(db: AsyncDatabase = Depends(get_db)):
    """Get active paper positions from MongoDB, including after worker restarts."""
    return await paper_trading_engine.get_open_positions_from_db(db)


@router.get("/history")
async def get_trade_history(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncDatabase = Depends(get_db),
):
    """
    Get history of completed paper trades from MongoDB.
    DB-backed — survives server restarts.
    Only returns signals that had an actual active trade (with entry prices).
    """
    return await paper_trading_engine.get_history_from_db(db, limit=limit)


@router.get("/summary")
async def get_trading_summary(db: AsyncDatabase = Depends(get_db)):
    """Get aggregate paper trading performance from persistent MongoDB records."""
    return await paper_trading_engine.get_summary_from_db(db)
