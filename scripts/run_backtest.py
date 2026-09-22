"""
CLI to run event-driven backtest.
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.artifacts.saver import ModelArtifactSaver
from ml.backtest.engine import EventDrivenBacktester
from ml.data.storage import ParquetStorage
from ml.features.pipeline import FeaturePipeline


def main():
    parser = argparse.ArgumentParser(description="Run backtest")
    parser.add_argument("--version", type=str, default="gbpusd-m15-v1.0")
    args = parser.parse_args()

    saver = ModelArtifactSaver(base_dir=project_root / "ml" / "artifacts")
    try:
        bundle = saver.load_bundle(args.version)
    except Exception as e:
        print(f"[ERROR] Model version '{args.version}' not found: {e}")
        return

    storage = ParquetStorage(base_dir=project_root / "data" / "parquet")
    m15_df = storage.load_candles_df("GBPUSD", "M15")

    if m15_df.empty:
        print("[ERROR] No market data found.")
        return

    h1_df = storage.load_candles_df("GBPUSD", "H1")
    context_dfs = {s: storage.load_candles_df(s, "M15") for s in ["EURUSD", "USDJPY", "EURGBP", "DXY"]}

    pipeline = FeaturePipeline(schema=bundle["schema"])
    X_df = pipeline.compute_features(m15_df, context_dfs, h1_df)

    backtester = EventDrivenBacktester()
    results = backtester.run(m15_df, X_df, bundle["model"], bundle["calibrator"])
    metrics = results["metrics"]

    print("===============================================")
    print(f" Backtest Performance Summary ({args.version})")
    print("===============================================")
    print(f" Total Trades:    {metrics['total_trades']}")
    print(f" Win Rate:        {metrics['win_rate'] * 100:.1f}%")
    print(f" Profit Factor:   {metrics['profit_factor']}")
    print(f" Expectancy:      {metrics['expectancy_pips']} pips")
    print(f" Sharpe Ratio:    {metrics['sharpe_ratio']}")
    print(f" Sortino Ratio:   {metrics['sortino_ratio']}")
    print(f" Max Drawdown:    {metrics['max_drawdown_pips']} pips")
    print("===============================================")


if __name__ == "__main__":
    main()
