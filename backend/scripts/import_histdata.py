"""
HistData.com CSV Importer & Resampler.

Imports historical M1 or M15 CSV data downloaded from HistData.com
(e.g., DAT_ASCII_GBPUSD_M1_2023.csv or DAT_MT_GBPUSD_M1_2023.csv),
parses timestamps, normalizes OHLCV, resamples to M15/H1 if needed,
and updates the Parquet dataset.

Supports 5 to 10+ years of historical data.
"""

import argparse
import glob
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.data.providers.base import Candle
from ml.data.storage import ParquetStorage
from ml.data.validation import validate_candles


def parse_histdata_csv(file_path: Path, symbol: str) -> pd.DataFrame:
    """
    Parse HistData.com CSV format.
    HistData comes in a few variants:
    1. Generic ASCII: YYYYMMDD HHMMSS;open;high;low;close;vol (semicolon or comma separated)
    2. MetaTrader format: YYYY.MM.DD,HH:MM,open,high,low,close,vol
    """
    print(f"Reading {file_path.name}...")
    
    # Peek header / line sample
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        first_line = f.readline().strip()

    sep = ";" if ";" in first_line else ","

    df = pd.read_csv(file_path, sep=sep, header=None)

    # Detect format based on column count and date strings
    if len(df.columns) >= 6:
        # Standard HistData ASCII: Col 0 = Date string, Col 1 = Time string (or combined)
        c0 = str(df.iloc[0, 0])
        c1 = str(df.iloc[0, 1])

        if len(c0) == 8 and c0.isdigit():
            # YYYYMMDD and HHMMSS in separate cols
            df["datetime_str"] = df[0].astype(str) + " " + df[1].astype(str)
            df["timestamp"] = pd.to_datetime(df["datetime_str"], format="%Y%m%d %H%M%S", utc=True)
            df["open"] = df[2].astype(float)
            df["high"] = df[3].astype(float)
            df["low"] = df[4].astype(float)
            df["close"] = df[5].astype(float)
            df["tick_volume"] = df[6].astype(int) if len(df.columns) > 6 else 1000
        elif "." in c0 and ":" in c1:
            # YYYY.MM.DD HH:MM
            df["datetime_str"] = df[0].astype(str) + " " + df[1].astype(str)
            df["timestamp"] = pd.to_datetime(df["datetime_str"], format="%Y.%m.%d %H:%M", utc=True)
            df["open"] = df[2].astype(float)
            df["high"] = df[3].astype(float)
            df["low"] = df[4].astype(float)
            df["close"] = df[5].astype(float)
            df["tick_volume"] = df[6].astype(int) if len(df.columns) > 6 else 1000
        else:
            # Combined datetime string in Col 0
            df["timestamp"] = pd.to_datetime(df[0], utc=True)
            df["open"] = df[1].astype(float)
            df["high"] = df[2].astype(float)
            df["low"] = df[3].astype(float)
            df["close"] = df[4].astype(float)
            df["tick_volume"] = df[5].astype(int) if len(df.columns) > 5 else 1000
    else:
        raise ValueError(f"Unrecognized HistData format in {file_path}")

    return df[["timestamp", "open", "high", "low", "close", "tick_volume"]]


def main():
    parser = argparse.ArgumentParser(description="Import HistData.com CSV files")
    parser.add_argument("--symbol", type=str, default="GBPUSD", help="Symbol (e.g. GBPUSD)")
    parser.add_argument("--dir", type=str, default="data/raw", help="Directory containing HistData CSVs")
    args = parser.parse_args()

    raw_dir = project_root / args.dir
    csv_files = sorted(glob.glob(str(raw_dir / f"*{args.symbol}*.csv")))

    if not csv_files:
        print(f"[ERROR] No CSV files matching '*{args.symbol}*.csv' found in {raw_dir}")
        print("Please place your downloaded HistData CSV files into data/raw/ and try again.")
        return

    print(f"[INFO] Found {len(csv_files)} HistData CSV files for {args.symbol}")

    all_dfs = []
    for f in csv_files:
        try:
            parsed = parse_histdata_csv(Path(f), args.symbol)
            all_dfs.append(parsed)
        except Exception as e:
            print(f"  [WARN] Failed to parse {f}: {e}")

    if not all_dfs:
        print("[ERROR] No files successfully parsed.")
        return

    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df.drop_duplicates(subset=["timestamp"], inplace=True)
    combined_df.sort_values("timestamp", inplace=True)

    print(f"[INFO] Total raw candles parsed: {len(combined_df)}")

    # Set timestamp index for resampling
    combined_df.set_index("timestamp", inplace=True)

    # 1. Resample to M15
    print("[INFO] Resampling to M15 timeframe...")
    m15_resampled = combined_df.resample("15min").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "tick_volume": "sum",
        }
    ).dropna()

    m15_resampled.reset_index(inplace=True)

    # 2. Resample to H1
    print("[INFO] Resampling to H1 timeframe...")
    h1_resampled = combined_df.resample("1H").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "tick_volume": "sum",
        }
    ).dropna()

    h1_resampled.reset_index(inplace=True)

    # Convert to Candle objects and save to Parquet
    storage = ParquetStorage(base_dir=project_root / "data" / "parquet")

    # M15
    m15_candles = [
        Candle(
            symbol=args.symbol,
            timeframe="M15",
            timestamp=row["timestamp"].to_pydatetime(),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            tick_volume=int(row["tick_volume"]),
        )
        for _, row in m15_resampled.iterrows()
    ]
    report_m15 = validate_candles(m15_candles)
    print(f"  M15 Valid: {report_m15.is_valid} | Candles: {report_m15.total_candles}")
    p15 = storage.save_candles(m15_candles)
    print(f"  [SAVED] M15 dataset saved to {p15}")

    # H1
    h1_candles = [
        Candle(
            symbol=args.symbol,
            timeframe="H1",
            timestamp=row["timestamp"].to_pydatetime(),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            tick_volume=int(row["tick_volume"]),
        )
        for _, row in h1_resampled.iterrows()
    ]
    p_h1 = storage.save_candles(h1_candles)
    print(f"  [SAVED] H1 dataset saved to {p_h1}")

    print(f"[SUCCESS] Successfully imported {len(m15_candles)} M15 bars ({m15_candles[0].timestamp.strftime('%Y-%m-%d')} to {m15_candles[-1].timestamp.strftime('%Y-%m-%d')})!")


if __name__ == "__main__":
    main()
