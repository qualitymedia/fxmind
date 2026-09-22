"""
CLI to download/fetch historical market data using configured provider.
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.data.providers.demo import DemoDataProvider
from ml.data.providers.csv import CSVDataProvider
from ml.data.storage import ParquetStorage


async def main():
    parser = argparse.ArgumentParser(description="Download/ingest market data")
    parser.add_argument("--provider", type=str, default="demo", choices=["demo", "csv"])
    parser.add_argument("--symbol", type=str, default="GBPUSD")
    parser.add_argument("--timeframe", type=str, default="M15")
    parser.add_argument("--days", type=int, default=365)
    args = parser.parse_args()

    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=args.days)

    if args.provider == "demo":
        provider = DemoDataProvider()
    else:
        provider = CSVDataProvider(data_dir=project_root / "data" / "raw")

    print(f"Fetching {args.symbol} {args.timeframe} via {args.provider}...")
    candles = await provider.fetch_candles(args.symbol, args.timeframe, start_dt, end_dt)
    
    if not candles:
        print("❌ No candles fetched.")
        return

    storage = ParquetStorage(base_dir=project_root / "data" / "parquet")
    saved_path = storage.save_candles(list(candles))
    print(f"✅ Downloaded and saved {len(candles)} candles to {saved_path}")


if __name__ == "__main__":
    asyncio.run(main())
