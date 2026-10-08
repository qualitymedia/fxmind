"""Helpers that repopulate runtime tables from the checked-in parquet and artifact data."""

from __future__ import annotations

import json
from datetime import timezone

import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.database import Base
from app.models.market import MarketCandle
from app.models.model_version import ModelVersion
from ml.artifacts.saver import ModelArtifactSaver


async def seed_runtime_data(session: AsyncSession) -> None:
    """Backfill the SQLite tables used by the dashboard if the restructure left them empty."""
    settings = get_settings()
    parquet_dir = settings.project_root / "data" / "parquet"

    # Repair legacy market_candles schema left behind by the repo reorg so new rows
    # can be inserted with SQLite auto-generated primary keys again.
    schema = await session.execute(text("PRAGMA table_info(market_candles)"))
    columns = schema.fetchall()
    if columns and (columns[0][2].upper() != "INTEGER" or columns[0][5] != 1):
        await session.execute(text("DROP TABLE IF EXISTS market_candles"))
        Base.metadata.create_all(bind=session.bind.sync_engine)

    # Seed candle data from parquet when the database was created without the historical data.
    has_candle_rows = await session.execute(select(MarketCandle.id).limit(1))
    if has_candle_rows.scalar_one_or_none() is None and parquet_dir.exists():
        for parquet_file in sorted(parquet_dir.glob("*.parquet")):
            try:
                df = pd.read_parquet(parquet_file)
            except Exception:
                continue

            if df.empty:
                continue

            stem = parquet_file.stem
            symbol, timeframe = stem.rsplit("_", 1)
            candle_rows = []
            for _, row in df.iterrows():
                ts = row.get("timestamp")
                if pd.isna(ts):
                    continue
                candle_rows.append(
                    MarketCandle(
                        symbol=str(symbol).upper(),
                        timeframe=str(timeframe).upper(),
                        timestamp=pd.Timestamp(ts).to_pydatetime().astimezone(timezone.utc),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        tick_volume=int(row.get("tick_volume", 0) or 0),
                    )
                )

            if candle_rows:
                last_id = await session.scalar(select(MarketCandle.id).order_by(MarketCandle.id.desc()).limit(1))
                next_id = (last_id or 0) + 1
                for candle in candle_rows:
                    candle.id = next_id
                    next_id += 1
                session.add_all(candle_rows)

    # Seed the active model record from the artifact bundle when the DB was left empty.
    has_model_rows = await session.execute(select(ModelVersion.id).limit(1))
    if has_model_rows.scalar_one_or_none() is None:
        saver = ModelArtifactSaver()
        try:
            bundle = saver.load_bundle()
        except Exception:
            return

        version = bundle.get("version") or "gbpusd-ensemble-v2.0"
        version_dir = saver.get_version_dir(version)
        metrics: dict = {}
        metrics_file = version_dir / "metrics.json"
        if metrics_file.exists():
            with open(metrics_file, "r", encoding="utf-8") as handle:
                metrics = json.load(handle)

        session.add(
            ModelVersion(
                id=1,
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
            )
        )

    await session.commit()
