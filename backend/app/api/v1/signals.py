"""
Signals REST Endpoints:
GET /api/v1/signals      — recent signal history from database
GET /api/v1/signals/{id} — signal detail by ID from database
"""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.signal import Signal
from app.schemas.signal import SignalListItem, SignalResponse
from app.services.signal_service import (
    get_signals_from_db,
    get_signal_by_id,
    save_signal_to_db,
)
from ml.data.storage import ParquetStorage
from ml.inference.service import InferenceService

router = APIRouter(prefix="/signals", tags=["signals"])

_inference_service = InferenceService()
_storage = ParquetStorage()


def _model_to_list_item(s: Signal) -> SignalListItem:
    return SignalListItem(
        id=s.id,
        timestamp=s.timestamp,
        bias=s.bias,
        confidence=s.confidence,
        regime=s.regime,
        direction=s.direction,
        strategy_type=None,
        entry_low=s.entry_low,
        entry_high=s.entry_high,
        stop_loss=s.stop_loss,
        take_profit=s.take_profit,
        status=s.status,
        patterns=[],
        outcome=s.outcome,
    )


def _model_to_response(s: Signal) -> SignalResponse:
    return SignalResponse(
        id=s.id,
        symbol=s.symbol,
        timestamp=s.timestamp,
        timeframe=s.timeframe,
        bias=s.bias,
        confidence=s.confidence,
        regime=s.regime,
        trade={
            "status": s.status,
            "direction": s.direction,
            "entry_low": s.entry_low,
            "entry_high": s.entry_high,
            "stop_loss": s.stop_loss,
            "take_profit": s.take_profit,
            "risk_reward": s.risk_reward,
        },
        model={
            "bull_probability": s.bull_probability,
            "bear_probability": s.bear_probability,
            "neutral_probability": s.neutral_probability,
        },
        market={
            "atr14": s.atr14,
            "spread": s.spread,
            "session": s.session_name,
        },
        filters={
            "news_clear": s.news_clear,
            "liquidity_ok": s.liquidity_ok,
            "spread_ok": s.spread_ok,
        },
        reasons=[
            {
                "category": r.category,
                "reason": r.reason,
                "value": r.value,
                "sentiment": r.sentiment,
            }
            for r in s.reasons
        ],
        patterns=[],
        model_version=s.model_version,
        outcome=s.outcome,
    )


@router.get("", response_model=list[SignalListItem])
async def get_signals_list(
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[SignalListItem]:
    """
    Get recent signal history from the SQLite database.
    If database has no signals yet, runs an inference pass and persists it.
    """
    db_signals = await get_signals_from_db(db, limit=limit, status=status)

    if not db_signals and not status:
        # Run cold-start inference and save to DB
        try:
            m15_df = _storage.load_candles_df("GBPUSD", "M15")
            h1_df = _storage.load_candles_df("GBPUSD", "H1")
            ctx_dfs = {s: _storage.load_candles_df(s, "M15") for s in ["EURUSD", "USDJPY", "EURGBP", "DXY"]}
            result = _inference_service.analyze(m15_df, ctx_dfs, h1_df)
            saved = await save_signal_to_db(result, db)
            db_signals = [saved]
        except Exception as exc:
            print(f"[Signals API] Cold-start inference error: {exc}")

    return [_model_to_list_item(s) for s in db_signals]


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal_detail(
    signal_id: int,
    db: AsyncSession = Depends(get_db),
) -> SignalResponse:
    """Get signal detail by ID directly from the database."""
    signal = await get_signal_by_id(db, signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal ID '{signal_id}' not found in database.")

    return _model_to_response(signal)
