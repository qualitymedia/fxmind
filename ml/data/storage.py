"""
Parquet Data Storage & Freshness Management.

Efficient columnar storage for historical market candles and feature matrices.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ml.data.normalization import candles_to_dataframe
from ml.data.providers.base import Candle


class ParquetStorage:
    """Manages Parquet files for raw/processed market data."""

    def __init__(self, base_dir: str | Path = "./data/parquet"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, symbol: str, timeframe: str) -> Path:
        return self.base_dir / f"{symbol}_{timeframe}.parquet"

    def save_candles(self, candles: list[Candle]) -> Path:
        """Save candle list to Parquet file."""
        if not candles:
            raise ValueError("Cannot save empty candle list")

        symbol = candles[0].symbol
        timeframe = candles[0].timeframe
        file_path = self._get_path(symbol, timeframe)

        df = candles_to_dataframe(candles)

        table = pa.Table.from_pandas(df)
        pq.write_table(table, file_path, compression="snappy")
        return file_path

    def load_candles_df(
        self,
        symbol: str,
        timeframe: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """Load candles DataFrame from Parquet file."""
        file_path = self._get_path(symbol, timeframe)
        if not file_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(file_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        if start is not None:
            start_utc = start.astimezone(timezone.utc)
            df = df[df["timestamp"] >= start_utc]
        if end is not None:
            end_utc = end.astimezone(timezone.utc)
            df = df[df["timestamp"] <= end_utc]

        return df.sort_values("timestamp").reset_index(drop=True)

    def get_freshness(self, symbol: str, timeframe: str) -> tuple[datetime | None, str]:
        """
        Check data freshness.
        Returns (last_timestamp, freshness_status)
        where status is LIVE, STALE, or NO_DATA.
        """
        df = self.load_candles_df(symbol, timeframe)
        if df.empty:
            return None, "NO_DATA"

        last_ts = df["timestamp"].max().to_pydatetime()
        now = datetime.now(timezone.utc)
        diff_minutes = (now - last_ts).total_seconds() / 60.0

        # M15 candle stale threshold: > 45 mins
        if diff_minutes <= 45:
            status = "LIVE"
        else:
            status = "STALE"

        return last_ts, status
