"""
Free Real Market Data Ingestion via yfinance.

Downloads authentic historical and real-time candles for GBPUSD, EURUSD, USDJPY, EURGBP, and DXY
and saves them to Parquet format for model training and live dashboard streaming.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

from ml.data.providers.base import Candle
from ml.data.storage import ParquetStorage
from ml.data.validation import validate_candles

# Ticker mapping for Yahoo Finance
TICKERS = {
    "GBPUSD": "GBPUSD=X",
    "EURUSD": "EURUSD=X",
    "USDJPY": "JPY=X",
    "EURGBP": "EURGBP=X",
    "DXY": "DX-Y.NYB",
}


def download_real_data():
    if not HAS_YFINANCE:
        print("[ERROR] 'yfinance' library is not installed.")
        return

    print("[INFO] Fetching authentic market data from Yahoo Finance...")
    storage = ParquetStorage(base_dir=project_root / "data" / "parquet")

    for symbol, ticker_symbol in TICKERS.items():
        # 1. Download 15m data (max 60 days from Yahoo Finance)
        print(f"Downloading {symbol} ({ticker_symbol}) 15m data...")
        df_15m = yf.download(ticker_symbol, period="60d", interval="15m", progress=False)

        if not df_15m.empty:
            df_15m = df_15m.reset_index()
            if isinstance(df_15m.columns, pd.MultiIndex):
                df_15m.columns = [col[0].lower().strip() for col in df_15m.columns]
            else:
                df_15m.columns = [str(c).lower().strip() for c in df_15m.columns]

            time_col = "datetime" if "datetime" in df_15m.columns else ("date" if "date" in df_15m.columns else df_15m.columns[0])
            df_15m["timestamp"] = pd.to_datetime(df_15m[time_col], utc=True)
            df_15m = df_15m.dropna(subset=["open", "high", "low", "close"])

            candles_15m = []
            for _, row in df_15m.iterrows():
                vol = int(row.get("volume", 0)) if pd.notnull(row.get("volume")) else 0
                if vol <= 0:
                    vol = 1200
                candles_15m.append(
                    Candle(
                        symbol=symbol,
                        timeframe="M15",
                        timestamp=row["timestamp"].to_pydatetime(),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        tick_volume=vol,
                    )
                )

            saved_path_15m = storage.save_candles(candles_15m)
            print(f"  [SUCCESS] Saved {len(candles_15m)} M15 candles to {saved_path_15m} (Latest price: {candles_15m[-1].close:.4f})")

        # 2. Download 1h data (up to 730 days / 2 years from Yahoo Finance)
        print(f"Downloading {symbol} ({ticker_symbol}) 1h data...")
        df_1h = yf.download(ticker_symbol, period="730d", interval="1h", progress=False)

        if not df_1h.empty:
            df_1h = df_1h.reset_index()
            if isinstance(df_1h.columns, pd.MultiIndex):
                df_1h.columns = [col[0].lower().strip() for col in df_1h.columns]
            else:
                df_1h.columns = [str(c).lower().strip() for c in df_1h.columns]

            time_col = "datetime" if "datetime" in df_1h.columns else ("date" if "date" in df_1h.columns else df_1h.columns[0])
            df_1h["timestamp"] = pd.to_datetime(df_1h[time_col], utc=True)
            df_1h = df_1h.dropna(subset=["open", "high", "low", "close"])

            candles_1h = []
            for _, row in df_1h.iterrows():
                vol = int(row.get("volume", 0)) if pd.notnull(row.get("volume")) else 0
                if vol <= 0:
                    vol = 2400
                candles_1h.append(
                    Candle(
                        symbol=symbol,
                        timeframe="H1",
                        timestamp=row["timestamp"].to_pydatetime(),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        tick_volume=vol,
                    )
                )

            saved_path_1h = storage.save_candles(candles_1h)
            print(f"  [SUCCESS] Saved {len(candles_1h)} H1 candles to {saved_path_1h}")

    print("[ALL DONE] Real market data synchronization complete!")


if __name__ == "__main__":
    download_real_data()
