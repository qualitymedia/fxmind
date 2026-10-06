"""
Master Model Training Orchestrator.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import numpy as np
import pandas as pd

from ml.artifacts.saver import ModelArtifactSaver
from ml.backtest.engine import EventDrivenBacktester
from ml.calibration.calibrator import ProbabilityCalibrator
from ml.data.storage import ParquetStorage
from ml.features.pipeline import FeaturePipeline
from ml.features.schema import FeatureSchema
from ml.labels.triple_barrier import compute_triple_barrier_labels
from ml.models.direction import LABEL_MAP
from ml.models.ensemble import VotingEnsembleDirectionModel
from ml.training.optimizer import OptunaOptimizer
from ml.validation.metrics import compute_classification_metrics
from ml.validation.purge import purge_and_embargo_splits


class ModelTrainer:
    """Orchestrates end-to-end model training."""

    def __init__(self, artifacts_dir: str | Path = "./ml/artifacts"):
        self.saver = ModelArtifactSaver(base_dir=artifacts_dir)

    def train(
        self,
        symbol: str = "GBPUSD",
        timeframe: str = "M15",
        version_name: str | None = None,
        run_optuna: bool = False,
    ) -> str:
        if version_name is None:
            version_name = f"gbpusd-ensemble-v2.0"


        print(f"[INFO] Starting model training pipeline for {version_name}...")

        # 1. Load Data
        storage = ParquetStorage()
        m15_df = storage.load_candles_df(symbol, timeframe)
        if m15_df.empty:
            raise ValueError(f"No parquet data found for {symbol} {timeframe}.")

        h1_df = storage.load_candles_df(symbol, "H1")
        context_dfs = {
            s: storage.load_candles_df(s, "M15")
            for s in ["EURUSD", "USDJPY", "EURGBP", "DXY"]
        }

        # 2. Features
        pipeline = FeaturePipeline()
        X_df = pipeline.compute_features(m15_df, context_dfs, h1_df)

        # 3. Labels
        label_df = compute_triple_barrier_labels(m15_df, upper_atr_mult=1.5, lower_atr_mult=1.0, horizon_bars=4)

        # Align X and y
        valid_mask = ~X_df.isna().any(axis=1)
        X_df = X_df[valid_mask]
        label_df = label_df[valid_mask]
        m15_df = m15_df[valid_mask]

        X_vals = X_df.values
        y_vals = label_df["label"].values
        y_int = np.array([LABEL_MAP[val] for val in y_vals])
        label_ends = label_df["label_end_index"].values

        n = len(X_df)
        train_end = int(n * 0.70)
        val_end = int(n * 0.85)

        train_idx = list(range(0, train_end))
        val_idx = list(range(train_end, val_end))
        test_idx = list(range(val_end, n))

        # 4. Purge & Embargo
        purged_train_idx, val_idx = purge_and_embargo_splits(train_idx, val_idx, label_ends, embargo_bars=4)
        purged_val_idx, test_idx = purge_and_embargo_splits(val_idx, test_idx, label_ends, embargo_bars=4)

        X_train, y_train = X_vals[purged_train_idx], y_int[purged_train_idx]
        X_val, y_val = X_vals[purged_val_idx], y_int[purged_val_idx]
        X_test, y_test = X_vals[test_idx], y_int[test_idx]

        # 5. Hyperparameter search with Optuna
        if run_optuna:
            print("  Running Bayesian optimization via Optuna over max_depth, colsample_bytree, learning_rate, reg_alpha...")
            optimizer = OptunaOptimizer(n_trials=15)
            best_params = optimizer.optimize(X_train, y_train, label_ends[purged_train_idx])
            print(f"  Best parameters found: max_depth={best_params.get('max_depth')}, lr={best_params.get('learning_rate'):.4f}, colsample={best_params.get('colsample_bytree'):.3f}")
        else:
            best_params = {
                "objective": "multi:softprob",
                "num_class": 3,
                "max_depth": 4,
                "learning_rate": 0.025,
                "n_estimators": 350,
                "subsample": 0.8,
                "colsample_bytree": 0.75,
                "min_child_weight": 20,
                "reg_alpha": 0.15,
                "reg_lambda": 1.2,
                "gamma": 0.05,
                "random_state": 42,
                "n_jobs": -1,
            }

        # 6. Fit Multi-Model Voting Ensemble (XGBoost + LightGBM + CatBoost)
        print("  Training Multi-Model Voting Ensemble (XGBoost + LightGBM + CatBoost)...")
        model = VotingEnsembleDirectionModel(xgb_params=best_params)
        model.fit(X_train, y_train, X_val, y_val)

        # 7. Fit Calibrator
        print("  Fitting probability calibrator on validation set...")
        val_raw_probs = model.predict_proba(X_val)
        calibrator = ProbabilityCalibrator(method="isotonic")
        calibrator.fit(val_raw_probs, y_val)

        # 8. Evaluate on untouched Test Set
        print("  Evaluating performance on untouched test set...")
        test_raw_probs = model.predict_proba(X_test)
        test_cal_probs = calibrator.calibrate(test_raw_probs)
        test_preds = np.argmax(test_cal_probs, axis=1)

        metrics = compute_classification_metrics(y_test, test_preds, test_cal_probs)

        # 9. Run Backtest
        backtester = EventDrivenBacktester()
        test_m15 = m15_df.iloc[test_idx].reset_index(drop=True)
        test_X_df = X_df.iloc[test_idx].reset_index(drop=True)
        bt_results = backtester.run(test_m15, test_X_df, model, calibrator)

        metrics.update(bt_results["metrics"])
        print(f"  Test Accuracy: {metrics['accuracy']} | Sharpe: {metrics.get('sharpe_ratio', 0.0)} | Win Rate: {metrics.get('win_rate', 0.0)}")

        # 10. Save Artifact Bundle
        schema = FeatureSchema(feature_names=list(X_df.columns), feature_count=len(X_df.columns))
        metadata = {
            "version": version_name,
            "model_type": "Multi-Model Ensemble (XGBoost + LightGBM + CatBoost)",
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "test_samples": len(X_test),
            "features_engineered": len(X_df.columns),
            "has_vwap": True,
            "has_candlestick_patterns": True,
            "has_volume_profile": True,
            "has_vp_poc_strategy": True,
            "has_smc_sweep": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        saved_path = self.saver.save_bundle(
            version=version_name,
            model=model,
            calibrator=calibrator,
            schema=schema,
            metrics=metrics,
            config=best_params,
            metadata=metadata,
        )

        print(f"[SUCCESS] Training complete! Saved versioned model bundle to {saved_path}")
        return version_name
