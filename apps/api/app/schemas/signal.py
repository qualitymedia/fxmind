"""
Signal Pydantic schemas for FXMind.

Matches the signal contract specification exactly.
Numbers in the contract are examples only — never hard-coded.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TradeSetup(BaseModel):
    """Trade setup geometry — deterministic from ATR, not from ML."""
    status: str = Field(..., description="ACTIVE or NO_TRADE")
    direction: Optional[str] = Field(None, description="LONG or SHORT")
    strategy_type: Optional[str] = Field(None, description="TREND_FOLLOWING or MEAN_REVERSION")
    entry_low: Optional[float] = None
    entry_high: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward: Optional[float] = None


class ModelProbabilities(BaseModel):
    """Calibrated class probabilities from XGBoost."""
    bull_probability: float
    bear_probability: float
    neutral_probability: float


class MarketContext(BaseModel):
    """Market context at signal time."""
    atr14: Optional[float] = None
    spread: Optional[float] = None
    session: Optional[str] = None


class SignalFilters(BaseModel):
    """Signal filter gate results."""
    news_clear: bool = True
    liquidity_ok: bool = True
    spread_ok: bool = True
    h1_confluence_ok: bool = True


class SignalReasonResponse(BaseModel):
    """Individual evidence reason."""
    category: str
    reason: str
    value: Optional[str] = None
    sentiment: Optional[str] = None

    model_config = {"from_attributes": True}


class SignalResponse(BaseModel):
    """
    Complete signal response matching the signal contract.
    
    This is the primary output of the AI analysis pipeline.
    Uses probabilistic language — never claims certainty.
    """
    id: int
    symbol: str = "GBPUSD"
    timestamp: datetime
    timeframe: str = "M15"
    bias: str = Field(..., description="BULLISH, BEARISH, or NEUTRAL")
    confidence: float = Field(..., ge=0, le=1, description="Calibrated probability")
    regime: str = Field(..., description="TRENDING, RANGING, HIGH_VOLATILITY, or ILLIQUID")
    trade: TradeSetup
    model: ModelProbabilities
    market: MarketContext
    filters: SignalFilters
    reasons: list[SignalReasonResponse] = Field(default_factory=list)
    patterns: list[dict] = Field(default_factory=list, description="Active SMC and Price Action patterns")
    model_version: str
    explanation: Optional[dict] = None
    outcome: Optional[str] = None
    outcome_pnl: Optional[float] = None

    model_config = {"from_attributes": True}


class SignalListItem(BaseModel):
    """Condensed signal for list views."""
    id: int
    timestamp: datetime
    bias: str
    regime: str
    confidence: float
    direction: Optional[str] = None
    strategy_type: Optional[str] = None
    entry_low: Optional[float] = None
    entry_high: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: str
    patterns: list[dict] = Field(default_factory=list)
    outcome: Optional[str] = None

    model_config = {"from_attributes": True}


class AnalysisResponse(BaseModel):
    """
    Complete analysis response for the dashboard.
    
    Combines signal, market overview, cross-market context,
    and upcoming events into a single response.
    """
    signal: SignalResponse
    market: dict = Field(default_factory=dict)
    cross_market: list[dict] = Field(default_factory=list)
    h1_context: Optional[dict] = None
    upcoming_events: list[dict] = Field(default_factory=list)
    data_freshness: str = "LIVE"
    last_updated: datetime
