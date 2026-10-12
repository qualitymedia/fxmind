"""MongoDB documents for generated signals and their bounded reason lists."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Optional

from pydantic import BaseModel, Field

from app.models.base import MongoDocument


class SignalReason(BaseModel):
    """Evidence explaining one signal decision, embedded in its signal."""

    category: str
    reason: str
    value: Optional[str] = None
    sentiment: Optional[str] = None


class Signal(MongoDocument):
    """AI-generated analysis; its small reason list is embedded in the document."""

    collection: ClassVar[str] = "signals"
    id: int
    symbol: str
    timeframe: str = "M15"
    timestamp: datetime
    bias: str
    confidence: float
    regime: str
    bull_probability: float
    bear_probability: float
    neutral_probability: float
    status: str
    direction: Optional[str] = None
    entry_low: Optional[float] = None
    entry_high: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy_type: Optional[str] = None
    risk_reward: Optional[float] = None
    atr14: Optional[float] = None
    spread: Optional[float] = None
    session_name: Optional[str] = None
    news_clear: Optional[bool] = None
    liquidity_ok: Optional[bool] = None
    spread_ok: Optional[bool] = None
    model_version: str
    explanation_json: Optional[str] = None
    outcome: Optional[str] = None
    outcome_pnl: Optional[float] = None
    outcome_timestamp: Optional[datetime] = None
    paper_opened_at: Optional[datetime] = None
    reasons: list[SignalReason] = Field(default_factory=list)
