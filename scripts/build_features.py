"""
CLI to build feature matrix from stored parquet candles.
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.data.storage import ParquetStorage
from ml.features.pipeline import FeaturePipeline


def main():
    parser = argparse.ArgumentParser(description="Build feature matrix")
    parser.add_argument("--symbol", type=str, default="GBPUSD")
    args = parser.parse_args()

    storage = ParquetStorage(base_dir=project_root / "data" / "parquet")
    m15_df = storage.load_candles_df(args.symbol, "M15")
    if m15_df.empty:
        print(f"❌ No M15 data found for {args.symbol}. Start the API server to fetch live data first.")
        return

    h1_df = storage.load_candles_df(args.symbol, "H1")
    context_dfs = {s: storage.load_candles_df(s, "M15") for s in ["EURUSD", "USDJPY", "EURGBP", "DXY"]}

    pipeline = FeaturePipeline()
    features = pipeline.compute_features(m15_df, context_dfs, h1_df)

    print(f"✅ Generated feature matrix with shape {features.shape} ({features.shape[1]} features)")


if __name__ == "__main__":
    main()
