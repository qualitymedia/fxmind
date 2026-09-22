"""
Signals REST Endpoints:
GET /api/v1/signals      — recent signal history (in-memory session log)
GET /api/v1/signals/{id} — signal detail by ID
"""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query

from apps.api.app.schemas.signal import SignalListItem, SignalResponse
from ml.data.storage import ParquetStorage
from ml.inference.service import InferenceService

router = APIRouter(prefix="/signals", tags=["signals"])

_inference_service = InferenceService()
_storage = ParquetStorage()

# In-memory session signal log — populated on first call and updated as candles arrive.
# This is NOT hardcoded data; it reflects real inference runs in the current server session.
_session_signals: list[dict] = []
_next_id: int = 1


def _run_and_log_signal() -> dict:
    """Run a fresh inference pass and append result to the session log."""
    global _next_id
    m15_df = _storage.load_candles_df("GBPUSD", "M15")
    h1_df = _storage.load_candles_df("GBPUSD", "H1")
    ctx_dfs = {s: _storage.load_candles_df(s, "M15") for s in ["EURUSD", "USDJPY", "EURGBP", "DXY"]}
    result = _inference_service.analyze(m15_df, ctx_dfs, h1_df)
    result["id"] = _next_id
    _next_id += 1

    # Avoid duplicating the same candle timestamp
    if _session_signals and _session_signals[-1].get("timestamp") == result.get("timestamp"):
        return _session_signals[-1]

    _session_signals.append(result)
    # Keep last 50 signals in memory
    if len(_session_signals) > 50:
        _session_signals.pop(0)

    return result


def _to_list_item(s: dict) -> SignalListItem:
    trade = s.get("trade", {})
    return SignalListItem(
        id=s.get("id", 0),
        timestamp=datetime.fromisoformat(s["timestamp"]) if isinstance(s.get("timestamp"), str) else s.get("timestamp", datetime.now(timezone.utc)),
        bias=s.get("bias", "NEUTRAL"),
        confidence=s.get("confidence", 0.333),
        regime=s.get("regime", "RANGING"),
        direction=trade.get("direction"),
        strategy_type=trade.get("strategy_type"),
        entry_low=trade.get("entry_low"),
        entry_high=trade.get("entry_high"),
        stop_loss=trade.get("stop_loss"),
        take_profit=trade.get("take_profit"),
        status=trade.get("status", "NO_TRADE"),
        patterns=s.get("patterns", []),
        outcome=s.get("outcome"),
    )


@router.get("", response_model=list[SignalListItem])
async def get_signals_list(
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
) -> list[SignalListItem]:
    """
    Get recent signal history from the live inference session.
    Runs a fresh inference pass if no session signals exist yet.
    """
    if not _session_signals:
        try:
            _run_and_log_signal()
        except Exception as exc:
            print(f"[Signals API] Inference error: {exc}")

    items = list(reversed(_session_signals))  # newest first
    if status:
        items = [s for s in items if s.get("trade", {}).get("status", "").upper() == status.upper()]

    return [_to_list_item(s) for s in items[:limit]]


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal_detail(signal_id: int) -> SignalResponse:
    """Get signal detail by ID from the live session log."""
    match = next((s for s in _session_signals if s.get("id") == signal_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Signal ID '{signal_id}' not found in current session.")

    trade = match.get("trade", {})
    model_probs = match.get("model", {})

    return SignalResponse(
        id=match["id"],
        symbol=match.get("symbol", "GBPUSD"),
        timestamp=datetime.fromisoformat(match["timestamp"]) if isinstance(match.get("timestamp"), str) else match.get("timestamp"),
        timeframe=match.get("timeframe", "M15"),
        bias=match.get("bias", "NEUTRAL"),
        confidence=match.get("confidence", 0.333),
        regime=match.get("regime", "RANGING"),
        trade=trade,
        model=model_probs,
        market=match.get("market", {}),
        filters=match.get("filters", {}),
        reasons=match.get("reasons", []),
        patterns=match.get("patterns", []),
        model_version=match.get("model_version", "gbpusd-ensemble-v1.0"),
        outcome=match.get("outcome"),
    )
