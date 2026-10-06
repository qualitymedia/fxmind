"""
Notifications & Telegram Alerts REST Endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.telegram_service import telegram_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


class TelegramConfigRequest(BaseModel):
    bot_token: str
    chat_id: str


@router.get("/telegram/status")
async def get_telegram_status():
    """Return whether Telegram integration is active."""
    return {
        "is_configured": telegram_service.is_configured(),
        "chat_id": telegram_service.chat_id if telegram_service.chat_id else None,
    }


@router.post("/telegram/config")
async def save_telegram_config(config: TelegramConfigRequest):
    """Save Telegram bot token and chat ID."""
    telegram_service.save_config(config.bot_token, config.chat_id)
    test_result = await telegram_service.test_connection()
    return {
        "success": test_result.get("success", False),
        "bot_username": test_result.get("bot_username"),
        "error": test_result.get("error"),
    }


@router.post("/telegram/test")
async def send_telegram_test():
    """Send an immediate test alert to the configured Telegram channel/chat."""
    if not telegram_service.is_configured():
        return {
            "success": False,
            "error": "Telegram Bot Token and Chat ID must be configured in Settings first.",
        }

    test_signal = {
        "symbol": "GBPUSD",
        "bias": "BULLISH",
        "confidence": 0.684,
        "regime": "TRENDING",
        "trade": {
            "direction": "LONG",
            "entry_low": 1.32450,
            "entry_high": 1.32480,
            "stop_loss": 1.32150,
            "take_profit": 1.33080,
            "risk_reward": 2.10,
        },
    }

    result = await telegram_service.send_signal_alert(test_signal)
    return {
        "success": result,
        "message": "Test alert dispatched to Telegram!" if result else "Failed to dispatch test alert.",
    }
