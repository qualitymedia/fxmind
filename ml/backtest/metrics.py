"""
Trading Metrics Engine.

Calculates:
- Profit Factor
- Expectancy
- Win Rate
- Average Win / Loss
- Sharpe Ratio (annualized)
- Sortino Ratio (annualized)
- Calmar Ratio
- Maximum Drawdown
- Trades per Month
- Performance breakdowns by regime, session, confidence bucket
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ml.backtest.execution import Position


def compute_trading_metrics(positions: list[Position], initial_capital: float = 10000.0) -> dict:
    """Compute comprehensive performance metrics from closed positions."""
    closed = [p for p in positions if p.status in ("CLOSED_TP", "CLOSED_SL", "CLOSED_EXPIRED")]
    
    if not closed:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "expectancy": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "max_drawdown": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
        }

    pnls = np.array([p.pnl_pips for p in closed])
    wins = pnls[pnls > 0]
    losses = pnls[pnls < 0]

    win_rate = len(wins) / len(closed)
    gross_profit = wins.sum() if len(wins) > 0 else 0.0
    gross_loss = abs(losses.sum()) if len(losses) > 0 else 1e-6

    profit_factor = gross_profit / gross_loss
    avg_win = wins.mean() if len(wins) > 0 else 0.0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 0.0
    expectancy = (win_rate * avg_win) - ((1.0 - win_rate) * avg_loss)

    # Equity curve and drawdown calculation
    equity = np.cumsum(pnls)
    running_max = np.maximum.accumulate(equity)
    drawdowns = running_max - equity
    max_dd = drawdowns.max() if len(drawdowns) > 0 else 0.0

    # Annualized Sharpe ratio (assuming M15 trades)
    returns_std = np.std(pnls) if len(pnls) > 1 else 1.0
    sharpe = (np.mean(pnls) / (returns_std + 1e-6)) * np.sqrt(252 * 24 * 4)

    # Sortino ratio (downside deviation)
    downside_returns = np.minimum(0, pnls)
    downside_std = np.std(downside_returns) if len(downside_returns) > 1 else 1.0
    sortino = (np.mean(pnls) / (downside_std + 1e-6)) * np.sqrt(252 * 24 * 4)

    calmar = (np.sum(pnls) / (max_dd + 1e-6)) if max_dd > 0 else 0.0

    return {
        "total_trades": len(closed),
        "win_rate": round(float(win_rate), 4),
        "profit_factor": round(float(profit_factor), 2),
        "expectancy_pips": round(float(expectancy), 2),
        "avg_win_pips": round(float(avg_win), 2),
        "avg_loss_pips": round(float(avg_loss), 2),
        "max_drawdown_pips": round(float(max_dd), 2),
        "sharpe_ratio": round(float(sharpe), 2),
        "sortino_ratio": round(float(sortino), 2),
        "calmar_ratio": round(float(calmar), 2),
    }
