"""
Model version tracking for FXMind.

Implements a state machine for model lifecycle:
TRAINING → CANDIDATE → VALIDATED → PRODUCTION → RETIRED
                                                → FAILED
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.base import TimestampMixin


class ModelVersion(Base, TimestampMixin):
    """
    ML model version with full metadata and lifecycle state.
    
    States:
    - TRAINING: Model is being trained
    - CANDIDATE: Training complete, pending validation
    - VALIDATED: Passed out-of-sample validation
    - PRODUCTION: Active production model
    - RETIRED: Previously production, now replaced
    - FAILED: Failed validation or runtime errors
    
    Only VALIDATED models can become PRODUCTION.
    Never overwrite model versions.
    """

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)  # xgboost, logistic, etc.
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="TRAINING")

    # Training metadata
    training_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    training_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validation_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validation_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    test_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    test_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Model details
    feature_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feature_names_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    hyperparameters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    label_config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    calibration_method: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Metrics
    metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    balanced_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    brier_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    log_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    profit_factor: Mapped[float | None] = mapped_column(Float, nullable=True)
    sharpe_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[float | None] = mapped_column(Float, nullable=True)
    win_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Artifacts
    artifacts_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    git_commit: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Feature importance
    feature_importance_json: Mapped[str | None] = mapped_column(Text, nullable=True)
