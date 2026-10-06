from __future__ import annotations

import math
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.signal import Signal
from ml.artifacts.saver import ModelArtifactSaver

router = APIRouter(prefix="/performance", tags=["performance"])
saver = ModelArtifactSaver()

INITIAL_CAPITAL = 100.0  # Paper trading account size in USD


@router.get("")
async def get_performance_summary(db: AsyncSession = Depends(get_db)):
    """
    Get performance metrics.
    Priority:
    1. Real DB-recorded trade outcomes (from paper trading / live signals).
    2. Walk-forward out-of-sample evaluation metrics from the trained model bundle.
    """
    # 1. Check for real closed trades in SQLite DB
    stmt = (
        select(Signal)
        .where(Signal.outcome.isnot(None))
        .where(Signal.outcome_pnl.isnot(None))
        .order_by(Signal.timestamp.asc())
    )
    result = await db.execute(stmt)
    closed_signals = list(result.scalars().all())

    if len(closed_signals) >= 3:
        pnls = [s.outcome_pnl for s in closed_signals]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]

        trade_count = len(pnls)
        win_rate = len(wins) / trade_count if trade_count > 0 else 0.0
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = abs(sum(losses)) if losses else 1e-6
        profit_factor = round(gross_profit / gross_loss, 2)
        avg_win = round(sum(wins) / len(wins), 2) if wins else 0.0
        avg_loss = round(abs(sum(losses)) / len(losses), 2) if losses else 0.0
        expectancy = round((win_rate * avg_win) - ((1.0 - win_rate) * avg_loss), 2)

        # Real cumulative equity curve starting at $100
        equity_curve = [{"index": 0, "equity": INITIAL_CAPITAL}]
        running_equity = INITIAL_CAPITAL
        for i, pnl in enumerate(pnls, 1):
            running_equity += pnl
            equity_curve.append({"index": i, "equity": round(running_equity, 2)})

        # Max drawdown from real equity curve
        equities = [pt["equity"] for pt in equity_curve]
        max_dd = 0.0
        peak = equities[0]
        for eq in equities:
            if eq > peak:
                peak = eq
            dd = peak - eq
            if dd > max_dd:
                max_dd = dd

        # Real Sharpe & Sortino from actual pnl series
        import numpy as np
        pnl_arr = np.array(pnls, dtype=float)
        pnl_mean = float(np.mean(pnl_arr))
        pnl_std = float(np.std(pnl_arr)) if len(pnl_arr) > 1 else 1.0
        ann_factor = math.sqrt(max(1.0, trade_count))
        sharpe = round((pnl_mean / (pnl_std + 1e-8)) * ann_factor, 2)

        downside = pnl_arr[pnl_arr < 0]
        downside_std = float(np.std(downside)) if len(downside) > 1 else 1.0
        sortino = round((pnl_mean / (downside_std + 1e-8)) * ann_factor, 2)

        return {
            "accuracy": round(win_rate, 3),
            "profit_factor": profit_factor,
            "expectancy": expectancy,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown": round(max_dd, 2),
            "win_rate": round(win_rate, 3),
            "trade_count": trade_count,
            "average_win": avg_win,
            "average_loss": avg_loss,
            "equity_curve": equity_curve,
            "initial_capital": INITIAL_CAPITAL,
            "source": "REAL_DB_OUTCOMES",
        }

    # 2. Fallback to Walk-Forward Model Bundle Metrics
    metrics: dict = {}
    try:
        bundle = saver.load_bundle()
        version = bundle.get("version") or bundle.get("metadata", {}).get("version", "gbpusd-ensemble-v1.0")
        v_dir = saver.get_version_dir(version)
        metrics_file = v_dir / "metrics.json"
        if metrics_file.exists():
            import json
            with open(metrics_file, "r", encoding="utf-8") as f:
                metrics = json.load(f)
    except Exception as exc:
        print(f"[Performance API] Could not load metrics from bundle: {exc}")

    trade_count = metrics.get("total_trades", metrics.get("trade_count", 0))
    win_rate = metrics.get("win_rate", 0.0)
    avg_win = metrics.get("avg_win_pips", 0.0)
    avg_loss = metrics.get("avg_loss_pips", 0.0)

    # Build equity curve from model metrics if available, else flat line
    equity_curve = _build_equity_curve_from_metrics(
        trade_count, win_rate, avg_win, avg_loss, INITIAL_CAPITAL
    )

    return {
        "accuracy": round(metrics.get("accuracy", 0.0), 3),
        "profit_factor": round(metrics.get("profit_factor", 0.0), 2),
        "expectancy": round(metrics.get("expectancy_pips", 0.0), 2),
        "sharpe_ratio": round(metrics.get("sharpe_ratio", 0.0), 2),
        "sortino_ratio": round(metrics.get("sortino_ratio", 0.0), 2),
        "max_drawdown": round(metrics.get("max_drawdown_pips", 0.0), 1),
        "win_rate": round(win_rate, 3),
        "trade_count": trade_count,
        "average_win": round(avg_win, 2),
        "average_loss": round(avg_loss, 2),
        "equity_curve": equity_curve,
        "initial_capital": INITIAL_CAPITAL,
        "source": "WALK_FORWARD_VALIDATION" if metrics else "NO_DATA",
    }


def _build_equity_curve_from_metrics(
    trade_count: int,
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    start_equity: float,
) -> list[dict]:
    """
    Build a smooth cumulative equity curve from aggregated metrics.
    Uses expected value per trade — no fake randomness or sine modulation.
    """
    if trade_count <= 0:
        return [{"index": 0, "equity": start_equity}]

    expected_gain_per_trade = (win_rate * avg_win) - ((1.0 - win_rate) * avg_loss)
    n_points = min(10, trade_count)
    step = trade_count / n_points

    curve = [{"index": 0, "equity": start_equity}]
    for i in range(1, n_points + 1):
        trades_done = int(i * step)
        equity = start_equity + (trades_done * expected_gain_per_trade)
        curve.append({"index": trades_done, "equity": round(equity, 2)})

    return curve


@router.get("/by-regime")
async def get_performance_by_regime(db: AsyncSession = Depends(get_db)):
    """Get real performance breakdown by market regime from DB outcomes."""
    stmt = (
        select(Signal)
        .where(Signal.outcome.isnot(None))
        .where(Signal.outcome_pnl.isnot(None))
        .where(Signal.regime.isnot(None))
    )
    result = await db.execute(stmt)
    closed_signals = list(result.scalars().all())

    # Group by regime
    regime_groups: dict[str, list[float]] = {}
    for s in closed_signals:
        regime = s.regime or "UNKNOWN"
        if regime not in regime_groups:
            regime_groups[regime] = []
        regime_groups[regime].append(s.outcome_pnl)

    breakdown = []
    for regime, pnls in regime_groups.items():
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        w = len(wins) / len(pnls) if pnls else 0.0
        gp = sum(wins) if wins else 0.0
        gl = abs(sum(losses)) if losses else 1e-6
        breakdown.append({
            "regime": regime,
            "win_rate": round(w, 3),
            "profit_factor": round(gp / gl, 2),
            "trades": len(pnls),
            "total_pnl_pips": round(sum(pnls), 1),
        })

    # If no real data yet, return empty structure — not fake numbers
    if not breakdown:
        return []

    return sorted(breakdown, key=lambda x: x["trades"], reverse=True)
