"""
Demo Market Data Provider.

Generates realistic synthetic market data for GBP/USD and context pairs
with proper statistical properties (session volatility, trending/ranging regimes,
realistic spreads and tick volumes).
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Sequence

import numpy as np

from ml.data.providers.base import Candle, MarketDataProvider, Quote

# Base prices for symbols
BASE_PRICES = {
    "GBPUSD": 1.3450,
    "EURUSD": 1.0850,
    "USDJPY": 154.50,
    "EURGBP": 0.8520,
    "DXY": 104.20,
}

# Standard spreads in pips/points
SPREAD_PIPS = {
    "GBPUSD": 0.00012,
    "EURUSD": 0.00010,
    "USDJPY": 0.012,
    "EURGBP": 0.00015,
    "DXY": 0.015,
}


class DemoDataProvider(MarketDataProvider):
    """
    Generates deterministic or stochastic synthetic candles with
    realistic financial properties.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self._rng = np.random.default_rng(seed)

    async def is_connected(self) -> bool:
        return True

    def _get_session_volatility_multiplier(self, dt: datetime) -> float:
        """London/NY overlap has higher vol; Asian has lower vol."""
        hour = dt.hour
        if 12 <= hour <= 16:  # London-NY Overlap
            return 1.6
        elif 7 <= hour < 12:  # London Session
            return 1.2
        elif 16 < hour <= 21:  # NY Session
            return 1.1
        else:  # Asian Session
            return 0.6

    async def fetch_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> Sequence[Candle]:
        base_price = BASE_PRICES.get(symbol, 1.2000)
        
        # Timeframe delta
        if timeframe == "M15":
            step = timedelta(minutes=15)
            base_vol = 0.0008
        elif timeframe == "H1":
            step = timedelta(hours=1)
            base_vol = 0.0016
        else:
            step = timedelta(minutes=15)
            base_vol = 0.0008

        # Create timestamps
        current = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)
        timestamps = []
        while current <= end_utc:
            # Skip weekends (Saturday=5, Sunday=6)
            if current.weekday() < 5:
                timestamps.append(current)
            current += step

        if not timestamps:
            return []

        # Generate realistic price path using geometric Brownian motion with regime regime switches
        n = len(timestamps)
        candles = []
        price = base_price

        # Micro-trend state
        trend_direction = 0.0
        trend_duration = 0

        for i, ts in enumerate(timestamps):
            vol_mult = self._get_session_volatility_multiplier(ts)
            dt_vol = base_vol * vol_mult

            # Trend switching
            if trend_duration <= 0:
                trend_direction = float(self._rng.choice([-1.0, 0.0, 1.0], p=[0.35, 0.3, 0.35]))
                trend_duration = int(self._rng.integers(8, 48))
            else:
                trend_duration -= 1

            drift = trend_direction * dt_vol * 0.2
            ret = self._rng.normal(drift, dt_vol)

            open_p = price
            close_p = price * math.exp(ret)

            # High and Low
            high_extra = abs(self._rng.normal(0, dt_vol * 0.5))
            low_extra = abs(self._rng.normal(0, dt_vol * 0.5))

            high_p = max(open_p, close_p) + high_extra
            low_p = min(open_p, close_p) - low_extra

            # Tick volume correlates with volatility and session
            tick_volume = int(self._rng.normal(1200 * vol_mult, 300))
            tick_volume = max(100, tick_volume)

            candle = Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=ts,
                open=round(open_p, 5),
                high=round(high_p, 5),
                low=round(low_p, 5),
                close=round(close_p, 5),
                tick_volume=tick_volume,
            )
            candles.append(candle)
            price = close_p

        return candles

    async def get_latest_quote(self, symbol: str) -> Quote:
        base_p = BASE_PRICES.get(symbol, 1.2000)
        spread = SPREAD_PIPS.get(symbol, 0.00012)
        now = datetime.now(timezone.utc)
        
        # Add minor random fluctuation
        fluctuation = float(self._rng.normal(0, 0.0002))
        mid = base_p + fluctuation
        bid = mid - spread / 2
        ask = mid + spread / 2

        return Quote(
            symbol=symbol,
            bid=round(bid, 5),
            ask=round(ask, 5),
            spread=round(spread, 5),
            timestamp=now,
        )
