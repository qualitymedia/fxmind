"""MongoDB document for model lifecycle and evaluation metadata."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Optional

from app.models.base import MongoDocument


class ModelVersion(MongoDocument):
    """Versioned ML model metadata; model binaries remain in artifact storage."""

    collection: ClassVar[str] = "model_versions"
    version: str
    model_type: str
    state: str = "TRAINING"
    training_start_date: Optional[datetime] = None
    training_end_date: Optional[datetime] = None
    validation_start_date: Optional[datetime] = None
    validation_end_date: Optional[datetime] = None
    test_start_date: Optional[datetime] = None
    test_end_date: Optional[datetime] = None
    feature_count: Optional[int] = None
    feature_names_json: Optional[str] = None
    hyperparameters_json: Optional[str] = None
    label_config_json: Optional[str] = None
    calibration_method: Optional[str] = None
    metrics_json: Optional[str] = None
    accuracy: Optional[float] = None
    balanced_accuracy: Optional[float] = None
    brier_score: Optional[float] = None
    log_loss: Optional[float] = None
    profit_factor: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    artifacts_path: Optional[str] = None
    git_commit: Optional[str] = None
    feature_importance_json: Optional[str] = None
