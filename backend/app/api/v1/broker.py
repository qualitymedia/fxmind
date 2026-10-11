"""
Broker Auto-Execution API Endpoints.

Allows users to connect their MetaTrader 5 broker account with 1 click
and execute live/demo trades directly via REST API.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.config import get_settings
from app.services.broker_service import broker_service



def require_broker_features() -> None:
    if not get_settings().broker_features_enabled:
        raise HTTPException(status_code=503, detail="Broker integration is coming soon.")


router = APIRouter(
    prefix="/broker",
    tags=["broker"],
    dependencies=[Depends(require_broker_features)],
)


class BrokerConnectRequest(BaseModel):
    login: int
    password: str
    server: str


class BrokerTestTradeRequest(BaseModel):
    symbol: str = "GBPUSD"
    direction: str = "LONG"
    lot_size: float = 0.01
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@router.get("/status")
async def get_broker_status():
    """Return live broker connection status, balance, equity, and leverage."""
    return broker_service.get_status()


@router.post("/connect")
async def connect_broker(req: BrokerConnectRequest):
    """Authenticate and connect directly to user's MetaTrader broker account."""
    return broker_service.connect(
        login=req.login,
        password=req.password,
        server=req.server
    )


@router.post("/test-trade")
async def place_test_trade(req: BrokerTestTradeRequest):
    """
    Execute a micro-lot trade (0.01 lot default) directly on the connected broker.
    Used for instant live verification.
    """
    return broker_service.execute_order(
        symbol=req.symbol,
        direction=req.direction,
        lot_size=req.lot_size,
        stop_loss=req.stop_loss,
        take_profit=req.take_profit,
    )


@router.post("/disconnect")
async def disconnect_broker():
    """Disconnect active broker session."""
    return broker_service.disconnect()


@router.get("/auto-trading")
async def get_auto_trading_status():
    """Return current auto-trading state."""
    return broker_service.get_auto_trading_status()


@router.post("/auto-trading/enable")
async def enable_auto_trading():
    """Enable AI auto-execution on ACTIVE signals (default ON)."""
    return broker_service.enable_auto_trading()


@router.post("/auto-trading/disable")
async def disable_auto_trading():
    """Disable AI auto-execution — manual trading only."""
    return broker_service.disable_auto_trading()


@router.get("/positions")
async def get_open_positions():
    """Return all currently open positions on the connected broker account."""
    return broker_service.get_open_positions()


@router.get("/history")
async def get_trade_history(limit: int = 50):
    """Return recent closed trade history from the connected broker account."""
    return broker_service.get_trade_history(limit=limit)
