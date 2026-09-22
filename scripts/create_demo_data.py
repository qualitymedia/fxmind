"""
Script to generate demo data for 2+ years of historical M15/H1 candles
for GBPUSD, EURUSD, USDJPY, EURGBP, and DXY.
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.data.providers.demo import DemoDataProvider
from ml.data.storage import ParquetStorage
from ml.data.validation import validate_candles


async def main():
    print("[INFO] Generating 2 years of demo market data...")

    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=730)  # 2 years

    symbols = ["GBPUSD", "EURUSD", "USDJPY", "EURGBP", "DXY"]
    provider = DemoDataProvider(seed=42)
    storage = ParquetStorage(base_dir=project_root / "data" / "parquet")

    for symbol in symbols:
        print(f"Generating M15 data for {symbol}...")
        m15_candles = await provider.fetch_candles(symbol, "M15", start_dt, end_dt)
        val_report = validate_candles(m15_candles)
        print(f"  Valid: {val_report.is_valid} | Candles: {val_report.total_candles}")

        p15 = storage.save_candles(list(m15_candles))
        print(f"  Saved to {p15}")

        # H1 data for GBPUSD context
        if symbol == "GBPUSD":
            print(f"Generating H1 data for {symbol}...")
            h1_candles = await provider.fetch_candles(symbol, "H1", start_dt, end_dt)
            p_h1 = storage.save_candles(list(h1_candles))
            print(f"  Saved H1 to {p_h1}")

    print("[SUCCESS] Demo data generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
