"""
FXMind Core Configuration.
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────
    app_name: str = "FXMind"
    app_env: AppEnv = AppEnv.DEVELOPMENT
    debug: bool = True
    demo_mode: bool = True
    broker_features_enabled: bool = False
    log_level: str = "INFO"
    secret_key: str = "change-me-to-a-random-string-in-production"

    # ── Database ─────────────────────────────────
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "fxmind"
    postgres_user: str = "fxmind"
    postgres_password: str = "fxmind_dev_password"
    database_url: Optional[str] = None

    @property
    def db_url(self) -> str:
        if self.database_url:
            return self.database_url
        # Fallback to local SQLite file for zero-setup dev execution if postgres not supplied
        db_path = (self.project_root / "data" / "fxmind.db").resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite+aiosqlite:///{db_path.as_posix()}"

    @property
    def db_url_sync(self) -> str:
        """Synchronous DB URL for Alembic migrations."""
        return self.db_url.replace("+aiosqlite", "")

    # ── API Server ───────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,"
        "http://172.20.10.4:3000,http://172.20.10.4:3001,http://0.0.0.0:3000,http://0.0.0.0:3001"
    )
    cors_origin_regex: str = r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|172\.\d+\.\d+\.\d+|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)(:\d+)?"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # ── JWT Authentication ───────────────────────
    jwt_secret_key: str = "change-me-to-a-different-random-string"
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
