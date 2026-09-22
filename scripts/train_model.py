"""
CLI to train the model.
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.training.trainer import ModelTrainer


def main():
    parser = argparse.ArgumentParser(description="Train XGBoost direction model")
    parser.add_argument("--version", type=str, default="gbpusd-m15-v1.0")
    parser.add_argument("--optuna", action="store_true", help="Run Optuna search")
    args = parser.parse_args()

    trainer = ModelTrainer(artifacts_dir=project_root / "ml" / "artifacts")
    trainer.train(version_name=args.version, run_optuna=args.optuna)


if __name__ == "__main__":
    main()
