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
async def test_open_paper_position_is_restored_from_signal_after_restart():
    from app.services.paper_trading import PaperTradingEngine

    now = datetime.now(timezone.utc)
    signal = Signal(
        id=42,
        symbol="GBPUSD",
        timeframe="M15",
        timestamp=now,
        paper_opened_at=now,
        bias="BULLISH",
        confidence=0.62,
        regime="TRENDING",
        bull_probability=0.62,
        bear_probability=0.2,
        neutral_probability=0.18,
        status="ACTIVE",
        direction="LONG",
        entry_low=1.2700,
        entry_high=1.2710,
        stop_loss=1.2680,
        take_profit=1.2750,
        strategy_type="TREND_FOLLOWING",
        model_version="test",
    )
    database = _FakeSignalsDatabase([to_mongo(signal)])
    engine = PaperTradingEngine()

    restored_count = await engine.restore_open_positions(database)

    assert restored_count == 1
    assert engine.open_positions[0]["signal_id"] == 42
    assert engine.open_positions[0]["direction"] == "LONG"
    assert engine.open_positions[0]["entry_price"] == 1.2705
    assert engine.open_positions[0]["strategy_type"] == "TREND_FOLLOWING"
    assert engine.open_positions[0]["opened_at"] == now.isoformat()
    assert (await engine.get_open_positions_from_db(database))[0]["signal_id"] == 42


@pytest.mark.asyncio
async def test_paper_position_remains_tracked_if_outcome_cannot_be_persisted(monkeypatch):
    from app.services import paper_trading as paper_trading_module
    from app.services.paper_trading import PaperTradingEngine

    async def fail_to_persist_outcome(**_kwargs):
        return None

    monkeypatch.setattr(
        paper_trading_module,
        "update_signal_outcome",
        fail_to_persist_outcome,
    )
    engine = PaperTradingEngine()
    position = engine.open_trade(
        {
            "symbol": "GBPUSD",
            "confidence": 0.7,
            "trade": {
                "status": "ACTIVE",
                "direction": "LONG",
                "entry_low": 1.2700,
                "entry_high": 1.2710,
                "stop_loss": 1.2680,
                "take_profit": 1.2750,
            },
        },
        db_signal_id=42,
    )
    assert position is not None

    closed = await engine.check_and_close_positions(
        current_price=1.2750,
        high=1.2750,
        low=1.2740,
        db=object(),
    )

    assert closed == []
    assert len(engine.open_positions) == 1
    assert engine.open_positions[0]["signal_id"] == 42
    assert engine.open_positions[0]["status"] == "OPEN"


class _FakeCursor:
    def __init__(self, documents):
        self.documents = documents

    def sort(self, *_args):
        return self

    async def to_list(self, length=None):
        return self.documents if length is None else self.documents[:length]


class _FakeSignalsCollection:
    def __init__(self, documents):
        self.documents = documents

    def find(self, _query):
        return _FakeCursor(self.documents)


class _FakeSignalsDatabase:
    def __init__(self, documents):
        self.collection = _FakeSignalsCollection(documents)

    def __getitem__(self, _name):
        return self.collection


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
