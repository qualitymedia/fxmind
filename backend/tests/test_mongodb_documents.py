"""Unit tests for MongoDB document serialization without an Atlas connection."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from app.models.base import from_mongo, to_mongo
from app.models.signal import Signal, SignalReason


def test_signal_reasons_are_embedded_and_id_round_trips():
    now = datetime.now(timezone.utc)
    signal = Signal(
        id=17,
        symbol="GBPUSD",
        timeframe="M15",
        timestamp=now,
        bias="BULLISH",
        confidence=0.7,
        regime="TRENDING",
        bull_probability=0.7,
        bear_probability=0.2,
        neutral_probability=0.1,
        status="ACTIVE",
        model_version="test",
        reasons=[SignalReason(category="Momentum", reason="Positive momentum")],
    )

    stored = to_mongo(signal)
    restored = from_mongo(Signal, stored)

    assert restored is not None
    assert stored["_id"] == 17
    assert "id" not in stored
    assert restored.id == signal.id
    assert restored.timestamp == now
    assert restored.reasons[0].category == "Momentum"


@pytest.mark.asyncio
async def test_mongodb_uri_is_required_without_sqlite_fallback(monkeypatch):
    from app.db import database as database_module

    monkeypatch.setattr(
        database_module,
        "get_settings",
        lambda: SimpleNamespace(mongodb_uri=None),
    )

    with pytest.raises(RuntimeError, match="MONGODB_URI is required"):
        await database_module.connect_to_mongo()


def test_production_settings_require_secure_deployment_values():
    from app.core.config import Settings

    settings = Settings(
        _env_file=None,
        app_env="production",
        debug=False,
        mongodb_uri="mongodb://localhost:27017",
        jwt_secret_key="a" * 32,
        cors_origins="https://fxmind.vercel.app",
    )

    assert settings.app_env.value == "production"
    assert settings.debug is False


def test_production_settings_reject_default_jwt_secret():
    from app.core.config import Settings

    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        Settings(
            _env_file=None,
            app_env="production",
            debug=False,
            mongodb_uri="mongodb://localhost:27017",
            cors_origins="https://fxmind.vercel.app",
        )


def test_production_settings_disable_broker_execution():
    from app.core.config import Settings

    with pytest.raises(ValueError, match="BROKER_FEATURES_ENABLED"):
        Settings(
            _env_file=None,
            app_env="production",
            debug=False,
            broker_features_enabled=True,
            mongodb_uri="mongodb://localhost:27017",
            jwt_secret_key="a" * 32,
            cors_origins="https://fxmind.vercel.app",
        )


def test_user_settings_features_are_disabled_in_production(monkeypatch):
    from fastapi import HTTPException

    from app.api.deps import require_authenticated_user_features
    from app.core.config import AppEnv

    monkeypatch.setattr(
        "app.api.deps.get_settings",
        lambda: SimpleNamespace(app_env=AppEnv.PRODUCTION),
    )

    with pytest.raises(HTTPException) as exc_info:
        require_authenticated_user_features()

    assert exc_info.value.status_code == 503


def test_user_settings_features_remain_available_outside_production(monkeypatch):
    from app.api.deps import require_authenticated_user_features
    from app.core.config import AppEnv

    monkeypatch.setattr(
        "app.api.deps.get_settings",
        lambda: SimpleNamespace(app_env=AppEnv.DEVELOPMENT),
    )

    require_authenticated_user_features()
