"""Seed small model metadata documents from bundled model artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from pymongo.asynchronous.database import AsyncDatabase

from app.db.database import next_document_id
from app.models.model_version import ModelVersion
from app.models.base import to_mongo
from ml.artifacts.saver import ModelArtifactSaver


async def seed_runtime_data(database: AsyncDatabase) -> None:
    """Seed model metadata only; large market history remains in Parquet files."""
    if await database[ModelVersion.collection].find_one(
        {"state": "PRODUCTION"}, projection={"_id": 1}
    ):
        return

    saver = ModelArtifactSaver()
    bundle = saver.load_bundle()
    version = bundle.get("version") or "gbpusd-ensemble-v2.0"
    version_dir = saver.get_version_dir(version)
    metrics: dict = {}
    metrics_file = version_dir / "metrics.json"
    if metrics_file.exists():
        with open(metrics_file, "r", encoding="utf-8") as handle:
            metrics = json.load(handle)

    model_version = ModelVersion(
        id=await next_document_id(database, ModelVersion.collection),
        version=version,
        model_type=(bundle.get("metadata") or {}).get("model_type", "ensemble"),
        state="PRODUCTION",
        feature_count=len(bundle["schema"].feature_names) if "schema" in bundle else 0,
        calibration_method="Isotonic Regression (Out-Of-Sample)",
        metrics_json=json.dumps(metrics),
        accuracy=metrics.get("accuracy"),
        profit_factor=metrics.get("profit_factor"),
        sharpe_ratio=metrics.get("sharpe_ratio"),
        max_drawdown=metrics.get("max_drawdown"),
        win_rate=metrics.get("win_rate"),
        artifacts_path=str(version_dir),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    await database[ModelVersion.collection].update_one(
        {"version": version},
        {"$setOnInsert": to_mongo(model_version)},
        upsert=True,
    )
