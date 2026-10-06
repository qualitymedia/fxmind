"""
Execution simulation with transaction costs.

Models bid/ask spread, slippage, and execution delay.
LONG: entry uses ask, exit uses bid
SHORT: entry uses bid, exit uses ask
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Position:
    """Active or closed trade position."""
    id: int
    symbol: str
    direction: str  # LONG or SHORT
    entry_time: datetime
    entry_price: float
    stop_loss: float
    take_profit: float
    size: float = 1.0
    status: str = "OPEN"  # OPEN, CLOSED_TP, CLOSED_SL, CLOSED_EXPIRED
    exit_time: datetime | None = None
    exit_price: float | None = None
    pnl_pips: float = 0.0
    pnl_amount: float = 0.0


def calculate_execution_price(
    direction: str,
    action: str,  # ENTRY or EXIT
    mid_price: float,
    spread_pips: float = 0.00012,
    slippage_pips: float = 0.00002,
) -> float:
    """
    Calculate realistic execution price including spread and slippage.
    """
    half_spread = spread_pips / 2.0

    if direction == "LONG":
        if action == "ENTRY":
            # Buy at Ask + slippage
            return mid_price + half_spread + slippage_pips
        else:
            # Sell at Bid - slippage
            return mid_price - half_spread - slippage_pips
    else:  # SHORT
        if action == "ENTRY":
            # Sell at Bid - slippage
            return mid_price - half_spread - slippage_pips
        else:
            # Buy at Ask + slippage
            return mid_price + half_spread + slippage_pips
