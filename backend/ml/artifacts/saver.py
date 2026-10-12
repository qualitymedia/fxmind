"""
Model Artifact Saver and Loader.

Manages saving and loading of model files into versioned folders.
Supports overwriting existing versions during retraining or saving new versions.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import joblib

from ml.features.schema import FeatureSchema
from ml.models.direction import XGBDirectionModel
from ml.calibration.calibrator import ProbabilityCalibrator


class ModelArtifactSaver:
    """Saves and loads all model bundle artifacts."""

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = (
            Path(base_dir)
            if base_dir is not None
            else Path(__file__).resolve().parents[2] / "ml" / "artifacts"
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_version_dir(self, version: str) -> Path:
        return self.base_dir / version

    def get_latest_version_dir(self) -> Path | None:
        """Find the newest version directory in artifacts."""
        version_dirs = [
            d for d in self.base_dir.iterdir() 
            if d.is_dir() and ((d / "direction_model.json").exists() or (d / "model.pkl").exists())
        ]
        if not version_dirs:
            return None
        # Sort by creation / modification time
        version_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
        return version_dirs[0]

    def save_bundle(
        self,
        version: str,
        model: XGBDirectionModel,
        calibrator: ProbabilityCalibrator,
        schema: FeatureSchema,
        metrics: dict[str, Any],
        config: dict[str, Any],
        metadata: dict[str, Any],
        overwrite: bool = True,
    ) -> Path:
        """Save complete versioned model artifact bundle."""
        v_dir = self.get_version_dir(version)
        if v_dir.exists():
            if overwrite:
                shutil.rmtree(v_dir)
            else:
                raise FileExistsError(f"Model version '{version}' already exists.")

        v_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save Model (supports VotingEnsembleDirectionModel and XGBDirectionModel)
        if hasattr(model, "xgb_model"):
            joblib.dump(model, v_dir / "model.pkl")
        elif hasattr(model, "model") and model.model is not None:
            model.model.save_model(v_dir / "direction_model.json")
        else:
            joblib.dump(model, v_dir / "model.pkl")

        # 2. Calibrator
        joblib.dump(calibrator, v_dir / "calibrator.pkl")

        # 3. Feature schema
        schema.save(v_dir / "feature_schema.json")

        # 4. Metrics
        with open(v_dir / "metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        # 5. Config
        with open(v_dir / "config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # 6. Feature Importance
        fi = model.get_feature_importance(schema.feature_names)
        with open(v_dir / "feature_importance.json", "w", encoding="utf-8") as f:
            json.dump(fi, f, indent=2)

        # 7. Training Metadata
        with open(v_dir / "training_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return v_dir

    def load_bundle(self, version: str | None = None) -> dict[str, Any]:
        """
        Load model artifact bundle.
        If version is None, automatically loads the latest version available.
        """
        if version is None:
            v_dir = self.get_latest_version_dir()
            if v_dir is None:
                raise FileNotFoundError("No model bundles found in artifacts directory.")
            version = v_dir.name
        else:
            v_dir = self.get_version_dir(version)

        if not v_dir.exists():
            # Fallback to latest
            v_dir_latest = self.get_latest_version_dir()
            if v_dir_latest is not None:
                v_dir = v_dir_latest
                version = v_dir.name
            else:
                raise FileNotFoundError(f"Model version '{version}' not found at {v_dir}")

        # Load Model
        if (v_dir / "model.pkl").exists():
            trained_model = joblib.load(v_dir / "model.pkl")
        elif (v_dir / "direction_model.json").exists():
            xgb_model = XGBDirectionModel()
            import xgboost as xgb
            clf = xgb.XGBClassifier()
            clf.load_model(v_dir / "direction_model.json")
            xgb_model.model = clf
            trained_model = xgb_model
        else:
            raise FileNotFoundError("No valid model file found in bundle")

        # Load Calibrator
        calibrator = joblib.load(v_dir / "calibrator.pkl")

        # Load Feature Schema
        schema = FeatureSchema.load(v_dir / "feature_schema.json")

        # Load Metadata
        with open(v_dir / "training_metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        return {
            "version": version,
            "model": trained_model,
            "calibrator": calibrator,
            "schema": schema,
            "metadata": metadata,
        }
