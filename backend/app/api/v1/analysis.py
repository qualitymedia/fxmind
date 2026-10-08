"""
Analysis REST Endpoints:
GET /api/v1/analysis/GBPUSD
GET /api/v1/analysis/GBPUSD/history
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter

from ml.data.storage import ParquetStorage
from ml.inference.service import InferenceService
from app.schemas.signal import AnalysisResponse, SignalResponse
from app.services.market_service import MarketService

router = APIRouter(prefix="/analysis", tags=["analysis"])

inference_service = InferenceService()
market_service = MarketService()
storage = ParquetStorage()


@router.get("/{symbol}", response_model=AnalysisResponse)
async def get_current_analysis(symbol: str = "GBPUSD") -> AnalysisResponse:
    """Get real-time AI analysis & trade setup for symbol."""
    symbol = symbol.upper()

    # Run all blocking parquet loads + inference in thread pool to avoid blocking the event loop
    loop = asyncio.get_running_loop()

    def _run_inference():
        m15_df = storage.load_candles_df(symbol, "M15")
        h1_df = storage.load_candles_df(symbol, "H1")
        context_dfs = {s: storage.load_candles_df(s, "M15") for s in ["EURUSD", "USDJPY", "EURGBP", "DXY"]}
        sig = inference_service.analyze(m15_df, context_dfs, h1_df)
        return m15_df, h1_df, sig

    m15_df, h1_df, signal_dict = await loop.run_in_executor(None, _run_inference)

    if not signal_dict.get("id"):
        signal_dict["id"] = 1

    market_overview, cross_market = await asyncio.gather(
        market_service.get_overview(symbol),
        market_service.get_cross_market_context(),
    )

    # Calculate real H1 context metrics from H1 dataframe
    if not h1_df.empty and len(h1_df) >= 50:
        c_h1 = h1_df["close"]
        ema20 = c_h1.ewm(span=20).mean().iloc[-1]
        ema50 = c_h1.ewm(span=50).mean().iloc[-1]
        last_h1_close = float(c_h1.iloc[-1])
        h1_high_24 = float(h1_df.tail(24)["high"].max())

        # Dynamic RSI 14 on H1
        delta = c_h1.diff()
        gain = delta.clip(lower=0).rolling(14).mean().iloc[-1]
        loss = (-delta.clip(upper=0)).rolling(14).mean().iloc[-1]
        rs = gain / (loss + 1e-8)
        rsi_h1_val = round(float(100 - (100 / (1 + rs))), 1)

        # Dynamic ATR 14 on H1
        tr = (h1_df["high"] - h1_df["low"]).rolling(14).mean().iloc[-1]
        atr_h1_val = round(float(tr), 5)

        is_bullish = ema20 > ema50
        trend_str = "Uptrend" if is_bullish else "Downtrend"
        ema_str = "Bullish" if is_bullish else "Bearish"
        h1_bias = "BULLISH" if is_bullish else "BEARISH"
        dist_pct = round(((last_h1_close - h1_high_24) / h1_high_24) * 100.0, 2)
        dist_str = f"{dist_pct}%"
    else:
        trend_str = "Neutral"
        rsi_h1_val = 50.0
        ema_str = "Neutral"
        atr_h1_val = 0.0025
        dist_str = "0.0%"
        h1_bias = "NEUTRAL"

    h1_context = {
        "trend": trend_str,
        "rsi_h1": rsi_h1_val,
        "ema_structure": ema_str,
        "atr_h1": atr_h1_val,
        "dist_from_high": dist_str,
        "bias": h1_bias,
    }

    upcoming_events = []

    return AnalysisResponse(
        signal=SignalResponse(**signal_dict),
        market=market_overview,
        cross_market=cross_market,
        h1_context=h1_context,
        upcoming_events=upcoming_events,
        data_freshness="LIVE" if market_overview["is_live"] else "STALE",
        last_updated=datetime.now(timezone.utc),
    )
