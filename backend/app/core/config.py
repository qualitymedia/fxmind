"""
FXMind Core Configuration.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[2] / ".env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────
    app_name: str = "FXMind"
    app_env: AppEnv = AppEnv.DEVELOPMENT
    debug: bool = False
    demo_mode: bool = True
    broker_features_enabled: bool = False
    log_level: str = "INFO"

    # ── Database ─────────────────────────────────
    mongodb_uri: Optional[str] = None
    mongodb_database: str = "fxmind"

    # ── API Server ───────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    cors_origin_regex: Optional[str] = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.app_env is AppEnv.PRODUCTION:
            if self.debug:
                raise ValueError("DEBUG must be false in production.")
            if self.broker_features_enabled:
                raise ValueError(
                    "BROKER_FEATURES_ENABLED must be false in production until broker actions are secured."
                )
            if not self.mongodb_uri or not self.mongodb_uri.strip():
                raise ValueError("MONGODB_URI must be set in production.")
            if len(self.jwt_secret_key) < 32 or self.jwt_secret_key.startswith("replace-with-"):
                raise ValueError(
                    "Set JWT_SECRET_KEY to a unique random value of at least 32 characters."
                )
            if not self.cors_origin_list or any(
                not origin.startswith("https://") for origin in self.cors_origin_list
            ):
                raise ValueError(
                    "Set CORS_ORIGINS to the HTTPS origin of the deployed frontend."
                )
        return self

    # ── JWT Authentication ───────────────────────
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Market Data ──────────────────────────────
    market_data_provider: str = "demo"
    csv_data_dir: str = "./data/raw"

    # ── ML Configuration ─────────────────────────
    model_artifacts_dir: str = "./ml/artifacts"
    training_config: str = "./configs/training.yaml"

    # ── Rate Limiting ────────────────────────────
    rate_limit_per_minute: int = 60

    # ── Derived Paths ────────────────────────────
    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @property
    def artifacts_path(self) -> Path:
        path = Path(self.model_artifacts_dir)
        if not path.is_absolute():
            path = self.project_root / path
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def data_path(self) -> Path:
        path = self.project_root / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
