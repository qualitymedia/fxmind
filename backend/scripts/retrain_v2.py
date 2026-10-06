"""
FXMind Model Retrain + Data Refresh Script (v2.0)

1. Fetches the latest GBPUSD + context pair data via YFinance
2. Saves to Parquet
3. Retrains the Multi-Model Ensemble with full updated dataset
4. Saves as gbpusd-ensemble-v2.0
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath("."))

from datetime import datetime, timezone, timedelta
import pandas as pd
from ml.data.storage import ParquetStorage
from ml.data.providers.yfinance_provider import YFinanceLiveProvider


async def refresh_data():
    """Fetch and persist latest market data for all required symbols."""
    storage = ParquetStorage()
    provider = YFinanceLiveProvider()

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=180)  # 6 months of history

    symbols_timeframes = [
        ("GBPUSD", "M15"),
        ("GBPUSD", "H1"),
        ("EURUSD", "M15"),
        ("USDJPY", "M15"),
        ("EURGBP", "M15"),
        ("DXY", "M15"),
    ]

    for symbol, tf in symbols_timeframes:
        print(f"  Fetching {symbol} {tf}...", end="", flush=True)
        try:
            candles = await provider.fetch_candles(symbol, tf, start, end)
            if candles:
                storage.save_candles(list(candles))
                df = storage.load_candles_df(symbol, tf)
                print(f" OK — {len(df)} bars ({str(df.iloc[-1]['timestamp'])[:16]})")
            else:
                print(f" WARNING: No candles returned")
        except Exception as e:
            print(f" ERROR: {e}")


def run_training():
    """Run the full model training pipeline."""
    from ml.training.trainer import ModelTrainer

    trainer = ModelTrainer()
    version = trainer.train(
        symbol="GBPUSD",
        timeframe="M15",
        version_name="gbpusd-ensemble-v2.0",
        run_optuna=False,  # Fast retrain with current good params
    )
    return version


if __name__ == "__main__":
    print("=" * 60)
    print("FXMind Model Retrain Pipeline — v2.0")
    print("=" * 60)

    print("\n[STEP 1] Refreshing market data...")
    asyncio.run(refresh_data())

    print("\n[STEP 2] Training model on updated dataset...")
    try:
        version = run_training()
        print(f"\n[DONE] Model saved as: {version}")
        print("Restart the API server to load the new model.")
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
