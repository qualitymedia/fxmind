"""
Tests for health endpoint and market validation.
"""

import pandas as pd
import pytest
from httpx import AsyncClient

from ml.data.validation import validate_market_dataframe
from ml.artifacts.saver import ModelArtifactSaver
from ml.inference.service import InferenceService


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test health check returns HTTP 200 with expected structure."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "market_data" in data
    assert "model" in data
    assert "timestamp" in data

    # Regression: the restructure should not leave the database empty when the parquet
    # files and model bundle are still present in the project.
    assert data["market_data"] == "healthy"
    assert data["model"] == "healthy"


def test_market_dataframe_rejects_invalid_price_data():
    """Invalid OHLC should be rejected before trading or training begins."""
    bad_df = pd.DataFrame([
        {
            "timestamp": "2026-10-01T00:00:00Z",
            "open": 1.0,
            "high": 1.2,
            "low": 1.3,
            "close": 1.1,
            "tick_volume": 200,
        },
    ])

    report = validate_market_dataframe(bad_df, symbol="GBPUSD", timeframe="M15")
    assert report.is_valid is False
    assert report.invalid_ohlc_count >= 1
    assert "Invalid OHLC" in report.error_messages[0]


def test_model_bundle_loads_outside_backend_working_directory(monkeypatch, tmp_path):
    """Model loading should not depend on Render's configured working directory."""
    monkeypatch.chdir(tmp_path)

    bundle = ModelArtifactSaver().load_bundle()

    assert bundle["version"] == "gbpusd-ensemble-v2.0"
    assert len(bundle["schema"].feature_names) == 130


def test_inference_service_has_regime_aware_ai_logic():
    """The runtime should adapt ensemble weighting by regime and report AI drift safely."""
    service = InferenceService()

    trend_weights = service._regime_aware_weights("TRENDING")
    range_weights = service._regime_aware_weights("RANGING")

    assert len(trend_weights) == 3
    assert trend_weights[0] > trend_weights[1]
    assert range_weights[1] > range_weights[0]

    sample_features = pd.DataFrame([
        {"feature_a": 1.0, "feature_b": 2.0, "feature_c": 3.0},
        {"feature_a": 1.2, "feature_b": 1.9, "feature_c": 2.8},
        {"feature_a": 1.1, "feature_b": 2.1, "feature_c": 2.7},
    ])

    drift = service._compute_ai_drift_score(sample_features)
    assert 0.0 <= drift <= 1.0


def test_valid_range_scalp_gate_only_triggers_in_real_ranges():
    """Only allow scalp entries when the market is truly oscillating inside a valid range."""
    service = InferenceService()

    valid_long = service._is_valid_range_scalp(
        regime="RANGING",
        direction="LONG",
        confidence=0.68,
        price_pos="INSIDE_VA",
        c_close=1.2720,
        val=1.2680,
        vah=1.2760,
        vwap_zscore=0.25,
        is_news_clear=True,
        spread_pips=0.00012,
    )
    noisy_short = service._is_valid_range_scalp(
        regime="RANGING",
        direction="SHORT",
        confidence=0.51,
        price_pos="ABOVE_VAH",
        c_close=1.2810,
        val=1.2680,
        vah=1.2760,
        vwap_zscore=1.4,
        is_news_clear=True,
        spread_pips=0.00012,
    )

    assert valid_long is True
    assert noisy_short is False


def test_paper_trading_allows_multiple_valid_positions():
    """Multiple valid active trades should be allowed when each setup passes the profit gate."""
    from app.services.paper_trading import PaperTradingEngine

    engine = PaperTradingEngine(initial_capital=100.0)

    first = {
        "symbol": "GBPUSD",
        "confidence": 0.72,
        "trade": {
            "status": "ACTIVE",
            "direction": "LONG",
            "strategy_type": "RANGE_SCALP",
            "entry_low": 1.2700,
            "entry_high": 1.2710,
            "stop_loss": 1.2685,
            "take_profit": 1.2735,
            "risk_reward": 2.1,
        },
        "id": 101,
    }

    second = {
        "symbol": "GBPUSD",
        "confidence": 0.74,
        "trade": {
            "status": "ACTIVE",
            "direction": "SHORT",
            "strategy_type": "RANGE_SCALP",
            "entry_low": 1.2760,
            "entry_high": 1.2770,
            "stop_loss": 1.2790,
            "take_profit": 1.2745,
            "risk_reward": 2.1,
        },
        "id": 102,
    }

    pos1 = engine.open_trade(first, db_signal_id=101)
    pos2 = engine.open_trade(second, db_signal_id=102)

    assert pos1 is not None
    assert pos2 is not None
    assert len(engine.open_positions) == 2


def test_scrap_trade_profit_stays_small_and_is_marked():
    """Paper / scrap trades should be intentionally tiny and clearly labeled as simulation-only."""
    from app.services.paper_trading import PaperTradingEngine

    engine = PaperTradingEngine(initial_capital=100.0)

    signal = {
        "symbol": "GBPUSD",
        "confidence": 0.82,
        "trade": {
            "status": "ACTIVE",
            "direction": "LONG",
            "strategy_type": "SCRAP_TRADE",
            "entry_low": 1.2700,
            "entry_high": 1.2710,
            "stop_loss": 1.2685,
            "take_profit": 1.2735,
            "risk_reward": 2.1,
        },
        "id": 999,
    }

    pos = engine.open_trade(signal, db_signal_id=999)
    assert pos is not None
    assert pos["trade_mode"] == "SCRAP"
    assert pos["is_scrap_trade"] is True

    engine.open_positions = []
    pos["status"] = "TARGET_HIT"
    pos["pnl_pips"] = 6.4
    pos["realized_pnl"] = 1.55
    pos["trade_mode"] = "SCRAP"
    pos["is_scrap_trade"] = True
    engine.closed_positions.append(pos)

    summary = engine.get_closed_summary()
    assert summary["total_trades"] == 1
    assert abs(summary["total_pnl_pips"]) <= 1.5
    assert abs(pos["realized_pnl"]) <= 1.5


def test_broker_scrap_signal_uses_smaller_lot_size():
    """A scrap trade should get a notably smaller MT5 lot size than a normal active strategy."""
    from app.services.broker_service import BrokerExecutionService

    service = BrokerExecutionService()
    service.account_info = {"equity": 3000.0}

    normal = service.calculate_dynamic_lot_size(
        stop_loss=1.2685,
        entry_price=1.2710,
        risk_pct=0.01,
        trade_type="TREND_FOLLOWING",
    )
    scrap = service.calculate_dynamic_lot_size(
        stop_loss=1.2685,
        entry_price=1.2710,
        risk_pct=0.01,
        trade_type="SCRAP_TRADE",
    )

    assert normal > scrap
    assert scrap <= 0.25


def test_broker_close_monitor_closes_positions_on_tp_or_sl(monkeypatch):
    """Open broker positions should be closed automatically when they hit TP or SL."""
    from app.services.broker_service import BrokerExecutionService

    class FakePosition:
        def __init__(self, ticket, symbol, type_, volume, price_current, sl, tp):
            self.ticket = ticket
            self.symbol = symbol
            self.type = type_
            self.volume = volume
            self.price_current = price_current
            self.sl = sl
            self.tp = tp
            self.profit = 0.0

    class FakeMT5:
        TRADE_ACTION_DEAL = 1
        ORDER_TYPE_BUY = 0
        ORDER_TYPE_SELL = 1
        ORDER_FILLING_FOK = 0
        ORDER_FILLING_IOC = 1
        ORDER_FILLING_RETURN = 2
        ORDER_TIME_GTC = 0

        @staticmethod
        def initialize():
            return True

        @staticmethod
        def positions_get():
            return [
                FakePosition(101, "GBPUSD", FakeMT5.ORDER_TYPE_BUY, 0.10, 1.2740, 1.2685, 1.2765),
            ]

        @staticmethod
        def order_send(request):
            return type("R", (), {"retcode": 10009, "order": request.get("position_ticket", 101)})()

        @staticmethod
        def symbol_info_tick(symbol):
            return type("Tick", (), {"bid": 1.2740, "ask": 1.2742})()

    monkeypatch.setitem(__import__("sys").modules, "MetaTrader5", FakeMT5)

    service = BrokerExecutionService()
    result = service.check_and_close_open_positions(current_price=1.2740, high=1.2742, low=1.2738)

    assert result["closed"] >= 1
    assert result["positions_checked"] >= 1
