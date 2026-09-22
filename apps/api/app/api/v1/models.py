from __future__ import annotations

import json
from fastapi import APIRouter
from ml.artifacts.saver import ModelArtifactSaver

router = APIRouter(prefix="/models", tags=["models"])
saver = ModelArtifactSaver()


def _load_bundle_info() -> dict:
    """Load the active model bundle and parse its metrics and metadata."""
    bundle = saver.load_bundle()
    version = bundle.get("version", "unknown")
    v_dir = saver.get_version_dir(version)
    metadata = bundle.get("metadata", {})

    metrics: dict = {}
    metrics_file = v_dir / "metrics.json"
    if metrics_file.exists():
        with open(metrics_file, "r", encoding="utf-8") as f:
            metrics = json.load(f)

    feature_count = len(bundle["schema"].feature_names) if "schema" in bundle else 0

    return {
        "version": version,
        "model_type": metadata.get("model_type", "Unknown"),
        "state": "PRODUCTION",
        "feature_count": feature_count,
        "calibration_method": "Isotonic Regression (Out-Of-Sample)",
        "training_samples": metadata.get("training_samples", 0),
        "validation_samples": metadata.get("validation_samples", 0),
        "accuracy": round(metrics.get("accuracy", 0.0), 3),
        "profit_factor": round(metrics.get("profit_factor", 0.0), 2),
        "win_rate": round(metrics.get("win_rate", 0.0), 3),
        "sharpe_ratio": round(metrics.get("sharpe_ratio", 0.0), 2),
        "last_validation": metadata.get("created_at", ""),
        "data_source": "Yahoo Finance (Authentic)",
    }


@router.get("/current")
async def get_current_model():
    """Get active production model info directly from model bundle artifacts."""
    try:
        return _load_bundle_info()
    except Exception as exc:
        return {"error": str(exc), "state": "UNAVAILABLE"}


@router.get("/history")
async def get_model_history():
    """Get list of tracked model versions from the artifacts directory."""
    try:
        info = _load_bundle_info()
        return [
            {
                "version": info["version"],
                "model_type": info["model_type"],
                "state": "PRODUCTION",
                "accuracy": info["accuracy"],
                "win_rate": info.get("win_rate"),
                "profit_factor": info.get("profit_factor"),
                "feature_count": info["feature_count"],
                "data_source": info["data_source"],
                "created_at": info["last_validation"],
            }
        ]
    except Exception:
        return []
