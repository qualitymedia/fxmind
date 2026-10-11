"""MongoDB persistence for generated signals and trade outcomes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.db.database import next_document_id
from app.models.base import from_mongo, to_mongo
from app.models.signal import Signal, SignalReason


async def save_signal_to_db(signal_dict: dict, db: AsyncDatabase) -> Signal:
    """Save a signal and its bounded evidence reasons in a single document."""
    trade = signal_dict.get("trade", {})
    model_probs = signal_dict.get("model", {})
    market = signal_dict.get("market", {})
    filters = signal_dict.get("filters", {})

    ts_raw = signal_dict.get("timestamp")
    if isinstance(ts_raw, str):
        try:
            timestamp = datetime.fromisoformat(ts_raw)
        except ValueError:
            timestamp = datetime.now(timezone.utc)
    elif isinstance(ts_raw, datetime):
        timestamp = ts_raw
    else:
        timestamp = datetime.now(timezone.utc)

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    reasons = [
        SignalReason(
            category=reason.get("category", "Analysis"),
            reason=reason.get("reason", ""),
            value=reason.get("value"),
            sentiment=reason.get("sentiment", "NEUTRAL"),
        )
        for reason in signal_dict.get("reasons", [])
    ]
    signal = Signal(
        id=await next_document_id(db, "signals"),
        symbol=signal_dict.get("symbol", "GBPUSD"),
        timeframe=signal_dict.get("timeframe", "M15"),
        timestamp=timestamp,
        bias=signal_dict.get("bias", "NEUTRAL"),
        confidence=float(signal_dict.get("confidence", 0.3333)),
        regime=signal_dict.get("regime", "RANGING"),
        bull_probability=float(model_probs.get("bull_probability", 0.3333)),
        bear_probability=float(model_probs.get("bear_probability", 0.3333)),
        neutral_probability=float(model_probs.get("neutral_probability", 0.3334)),
        status=trade.get("status", "NO_TRADE"),
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
        reasons=reasons,
    )
    await db[Signal.collection].insert_one(to_mongo(signal))
    return signal


async def update_signal_outcome(
    signal_id: int,
    outcome: str,
    pnl: float,
    db: AsyncDatabase,
) -> Optional[Signal]:
    """Update outcome and P&L for a resolved signal."""
    updates = {
        "outcome": outcome,
        "outcome_pnl": round(pnl, 2),
        "outcome_timestamp": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    if outcome in ("TARGET_HIT", "STOP_HIT", "EXPIRED", "INVALIDATED"):
        updates["status"] = outcome

    result = await db[Signal.collection].find_one_and_update(
        {"_id": signal_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    return from_mongo(Signal, result)


async def get_signals_from_db(
    db: AsyncDatabase,
    limit: int = 50,
    status: Optional[str] = None,
) -> list[Signal]:
    """Query recent signals and their embedded reasons."""
    query = {"status": status.upper()} if status else {}
    cursor = db[Signal.collection].find(query).sort("timestamp", -1).limit(limit)
    return [
        signal
        for document in await cursor.to_list(length=limit)
        if (signal := from_mongo(Signal, document)) is not None
    ]


async def get_signal_by_id(db: AsyncDatabase, signal_id: int) -> Optional[Signal]:
    """Query a single signal by its public numeric ID."""
    document = await db[Signal.collection].find_one({"_id": signal_id})
    return from_mongo(Signal, document)
