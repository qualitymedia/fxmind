"""
Signal Persistence Service.

Handles database transactions for saving ML inference signals and
updating trade outcomes (TARGET_HIT, STOP_HIT, EXPIRED).
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.signal import Signal, SignalReason


async def save_signal_to_db(signal_dict: dict, db: AsyncSession) -> Signal:
    """Save an AI analysis signal and its reasons to the database."""
    trade = signal_dict.get("trade", {})
    model_probs = signal_dict.get("model", {})
    market = signal_dict.get("market", {})
    filters = signal_dict.get("filters", {})

    ts_raw = signal_dict.get("timestamp")
    if isinstance(ts_raw, str):
        try:
            timestamp = datetime.fromisoformat(ts_raw)
        except Exception:
            timestamp = datetime.now(timezone.utc)
    elif isinstance(ts_raw, datetime):
        timestamp = ts_raw
    else:
        timestamp = datetime.now(timezone.utc)

    # Ensure timezone awareness
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    # Status handling
    trade_status = trade.get("status", "NO_TRADE")

    signal = Signal(
        symbol=signal_dict.get("symbol", "GBPUSD"),
        timeframe=signal_dict.get("timeframe", "M15"),
        timestamp=timestamp,
        bias=signal_dict.get("bias", "NEUTRAL"),
        confidence=float(signal_dict.get("confidence", 0.3333)),
        regime=signal_dict.get("regime", "RANGING"),
        bull_probability=float(model_probs.get("bull_probability", 0.3333)),
        bear_probability=float(model_probs.get("bear_probability", 0.3333)),
        neutral_probability=float(model_probs.get("neutral_probability", 0.3334)),
        status=trade_status,
        direction=trade.get("direction"),
        entry_low=trade.get("entry_low"),
        entry_high=trade.get("entry_high"),
        stop_loss=trade.get("stop_loss"),
        take_profit=trade.get("take_profit"),
        risk_reward=trade.get("risk_reward"),
        atr14=market.get("atr14"),
        spread=market.get("spread"),
        session_name=market.get("session"),
        news_clear=filters.get("news_clear", True),
        liquidity_ok=filters.get("liquidity_ok", True),
        spread_ok=filters.get("spread_ok", True),
        model_version=signal_dict.get("model_version", "gbpusd-ensemble-v1.0"),
        outcome=signal_dict.get("outcome"),
        outcome_pnl=signal_dict.get("outcome_pnl"),
    )

    db.add(signal)
    await db.flush()  # Populates signal.id

    # Add reasons
    reasons_data = signal_dict.get("reasons", [])
    for r in reasons_data:
        reason_obj = SignalReason(
            signal_id=signal.id,
            category=r.get("category", "Analysis"),
            reason=r.get("reason", ""),
            value=r.get("value"),
            sentiment=r.get("sentiment", "NEUTRAL"),
        )
        db.add(reason_obj)

    await db.commit()
    await db.refresh(signal)
    return signal


async def update_signal_outcome(
    signal_id: int,
    outcome: str,
    pnl: float,
    db: AsyncSession,
) -> Optional[Signal]:
    """Update outcome and P&L for a resolved signal."""
    result = await db.execute(select(Signal).where(Signal.id == signal_id))
    signal = result.scalar_one_or_none()
    if not signal:
        return None

    signal.outcome = outcome
    signal.outcome_pnl = round(pnl, 2)
    signal.outcome_timestamp = datetime.now(timezone.utc)
    if outcome in ("TARGET_HIT", "STOP_HIT", "EXPIRED", "INVALIDATED"):
        signal.status = outcome

    await db.commit()
    await db.refresh(signal)
    return signal


async def get_signals_from_db(
    db: AsyncSession,
    limit: int = 50,
    status: Optional[str] = None,
) -> list[Signal]:
    """Query recent signals with reasons preloaded."""
    from sqlalchemy.orm import selectinload
    stmt = (
        select(Signal)
        .options(selectinload(Signal.reasons))
        .order_by(Signal.timestamp.desc())
        .limit(limit)
    )
    if status:
        stmt = stmt.where(Signal.status == status.upper())

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_signal_by_id(db: AsyncSession, signal_id: int) -> Optional[Signal]:
    """Query a single signal by ID."""
    from sqlalchemy.orm import selectinload
    stmt = select(Signal).options(selectinload(Signal.reasons)).where(Signal.id == signal_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
