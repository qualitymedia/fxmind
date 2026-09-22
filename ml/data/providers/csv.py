"""
CSV Market Data Provider.

Imports historical candle data from CSV files (e.g., exported from MT4, MT5, TradingView).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import pandas as pd

from ml.data.providers.base import Candle, MarketDataProvider, Quote


class CSVDataProvider(MarketDataProvider):
    """
    Imports candles from CSV files.
    
    Expected CSV columns: timestamp/date, open, high, low, close, volume/tick_volume
    """

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)

    async def is_connected(self) -> bool:
        return self.data_dir.exists()

    async def fetch_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> Sequence[Candle]:
        file_name = f"{symbol}_{timeframe}.csv"
        file_path = self.data_dir / file_name

        if not file_path.exists():
            return []

        df = pd.read_csv(file_path)
        
        # Standardize column names
        df.columns = [c.lower().strip() for c in df.columns]

        # Datetime column identification
        time_col = None
        for col in ["timestamp", "date", "datetime", "time"]:
            if col in df.columns:
                time_col = col
                break

        if not time_col:
            raise ValueError(f"No timestamp column found in {file_path}")

        df["timestamp"] = pd.to_datetime(df[time_col], utc=True)
        
        # Volume column
        vol_col = "tick_volume" if "tick_volume" in df.columns else ("volume" if "volume" in df.columns else None)
        if not vol_col:
            df["tick_volume"] = 0
        else:
            df["tick_volume"] = df[vol_col].fillna(0).astype(int)

        # Filter by start/end
        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)

        mask = (df["timestamp"] >= start_utc) & (df["timestamp"] <= end_utc)
        df_filtered = df.loc[mask].sort_values("timestamp")

        candles = []
        for _, row in df_filtered.iterrows():
            candle = Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=row["timestamp"].to_pydatetime(),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                tick_volume=int(row["tick_volume"]),
            )
            candles.append(candle)

        return candles

    async def get_latest_quote(self, symbol: str) -> Quote:
        file_name = f"{symbol}_M15.csv"
        file_path = self.data_dir / file_name
        if file_path.exists():
            df = pd.read_csv(file_path)
            last_close = float(df.iloc[-1]["close"])
        else:
            last_close = 1.3450

        spread = 0.00012
        now = datetime.now(timezone.utc)
        return Quote(
            symbol=symbol,
            bid=last_close - spread / 2,
            ask=last_close + spread / 2,
            spread=spread,
            timestamp=now,
        )
