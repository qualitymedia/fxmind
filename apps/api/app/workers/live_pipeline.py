"""
Live Continuous Inference Pipeline & Real-Time Broadcast Worker.

Runs in the background at every completed M15 candle:
1. Ingests latest closed M15 candle from live provider
2. Validates & appends candle to storage
3. Re-computes full ~112 feature matrix at t0
4. Predicts market regime & calibrated direction probabilities
5. Applies news-risk filters & candidate gates
6. Saves signal to database
7. Broadcasts live updates via WebSockets (/ws/market and /ws/signals)
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

from ml.data.providers.yfinance_provider import YFinanceLiveProvider
from ml.data.providers.base import Candle
from ml.data.storage import ParquetStorage
from ml.inference.service import InferenceService
from apps.api.app.websocket.manager import ws_manager


class LivePipelineWorker:
    """Background worker executing real-time M15 market analysis."""

    def __init__(self, poll_interval_seconds: int = 15):
        self.poll_interval = poll_interval_seconds
        self.provider = YFinanceLiveProvider()
        self.storage = ParquetStorage()
        self.inference_service = InferenceService()
        self.is_running = False
        self.last_processed_timestamp: Optional[datetime] = None

    async def start(self) -> None:
        """Start the background live analysis loop."""
        self.is_running = True
        print("[LIVE WORKER] Live Market Analysis Worker started.")

        while self.is_running:
            try:
                await self._process_tick()
            except Exception as e:
                print(f"[LIVE WORKER ERROR] {e}")

            await asyncio.sleep(self.poll_interval)

    def stop(self) -> None:
        """Stop the background worker."""
        self.is_running = False
        print("[LIVE WORKER] Live Market Analysis Worker stopped.")

    async def _process_tick(self) -> None:
        """Execute single tick check."""
        now = datetime.now(timezone.utc)

        # 1. Fetch latest live quote
        quote = await self.provider.get_latest_quote("GBPUSD")
        
        # Broadcast real-time quote over WebSocket
        await ws_manager.broadcast(
            "market",
            {
                "type": "QUOTE_UPDATE",
                "symbol": "GBPUSD",
                "bid": quote.bid,
                "ask": quote.ask,
                "spread": quote.spread,
                "timestamp": quote.timestamp.isoformat(),
            },
        )

        # Periodically refresh M15 candles if needed
        m15_df = self.storage.load_candles_df("GBPUSD", "M15")
        if not m15_df.empty:
            latest_ts = m15_df.iloc[-1]["timestamp"].to_pydatetime()
            # If latest stored candle is older than 20 minutes and market is open, sync recent candles
            if (now - latest_ts).total_seconds() > 20 * 60:
                try:
                    recent_candles = await self.provider.fetch_candles("GBPUSD", "M15", latest_ts, now)
                    if recent_candles:
                        self.storage.save_candles(list(recent_candles))
                        m15_df = self.storage.load_candles_df("GBPUSD", "M15")
                        latest_ts = m15_df.iloc[-1]["timestamp"].to_pydatetime()
                except Exception as e:
                    print(f"[LIVE WORKER] Candle sync warning: {e}")
        else:
            return

        if self.last_processed_timestamp is not None and latest_ts <= self.last_processed_timestamp:
            return  # No new candle closed yet

        self.last_processed_timestamp = latest_ts
        print(f"[LIVE WORKER] New M15 candle closed at {latest_ts}. Running AI pipeline...")

        # 3. Run full Inference Pipeline
        h1_df = self.storage.load_candles_df("GBPUSD", "H1")
        context_dfs = {s: self.storage.load_candles_df(s, "M15") for s in ["EURUSD", "USDJPY", "EURGBP", "DXY"]}

        analysis_result = self.inference_service.analyze(
            m15_df=m15_df,
            context_dfs=context_dfs,
            h1_df=h1_df,
            spread_pips=quote.spread,
        )

        # 4. Broadcast live signal over WebSocket
        await ws_manager.broadcast(
            "signals",
            {
                "type": "SIGNAL_UPDATE",
                "signal": analysis_result,
            },
        )
        print(f"[LIVE WORKER] Broadcasted signal: {analysis_result['bias']} ({analysis_result['confidence']:.1%}) Regime: {analysis_result['regime']}")


# Worker instance
live_worker = LivePipelineWorker()
