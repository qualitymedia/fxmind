"""MongoDB documents for alerts, notifications, and backtest metadata."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Optional

from app.models.base import MongoDocument


class Alert(MongoDocument):
    """User-configured alert rule."""

    collection: ClassVar[str] = "alerts"
    user_id: int
    alert_type: str
    symbol: str = "GBPUSD"
    min_confidence: Optional[float] = None
    enabled: bool = True
    config_json: Optional[str] = None


class Notification(MongoDocument):
    """Alert notification sent to a user."""

    collection: ClassVar[str] = "notifications"
    user_id: int
    alert_id: Optional[int] = None
    title: str
    message: str
    notification_type: str
    is_read: bool = False
    data_json: Optional[str] = None


class BacktestRun(MongoDocument):
    """Backtest execution and results metadata."""

    collection: ClassVar[str] = "backtest_runs"
    model_version: str
    start_date: datetime
    end_date: datetime
    config_json: str
    total_trades: Optional[int] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    expectancy: Optional[float] = None
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    results_json: Optional[str] = None
    equity_curve_json: Optional[str] = None
