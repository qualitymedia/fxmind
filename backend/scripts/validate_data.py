"""
CLI script to validate stored Parquet candles for logical integrity.
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.data.storage import ParquetStorage
from ml.data.validation import validate_candles
from ml.data.providers.base import Candle


def main():
    parser = argparse.ArgumentParser(description="Validate candle data integrity")
    parser.add_argument("--symbol", type=str, default="GBPUSD")
    parser.add_argument("--timeframe", type=str, default="M15")
    args = parser.parse_args()

    storage = ParquetStorage(base_dir=project_root / "data" / "parquet")
    df = storage.load_candles_df(args.symbol, args.timeframe)

    if df.empty:
        print(f"❌ No parquet data found for {args.symbol} {args.timeframe}")
        return

    candles = [
        Candle(
            symbol=row["symbol"],
            timeframe=row["timeframe"],
            timestamp=row["timestamp"].to_pydatetime(),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            tick_volume=int(row["tick_volume"]),
        )
        for _, row in df.iterrows()
    ]

    report = validate_candles(candles)

    print("═══════════════════════════════════════════════")
    print(f" Data Validation Report: {args.symbol} {args.timeframe}")
    print("═══════════════════════════════════════════════")
    print(f" Status:            {'✅ PASS' if report.is_valid else '❌ FAIL'}")
    print(f" Total Candles:     {report.total_candles}")
    print(f" Invalid OHLC:      {report.invalid_ohlc_count}")
    print(f" Duplicate TS:      {report.duplicate_count}")
    print(f" Gap Count:         {report.missing_gap_count}")
    print(f" Outlier Count:     {report.outlier_count}")
    if report.error_messages:
        print("\nErrors (first 5):")
        for err in report.error_messages[:5]:
            print(f" - {err}")
    print("═══════════════════════════════════════════════")


if __name__ == "__main__":
    main()
