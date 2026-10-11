"""Copy existing FXMind SQLite records to MongoDB without modifying SQLite."""

from __future__ import annotations

import asyncio
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymongo import UpdateOne

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402
from app.db.database import close_mongo_connection, connect_to_mongo  # noqa: E402

PROJECT_ROOT = BACKEND_DIR.parent
SQLITE_PATH = PROJECT_ROOT / "backend" / "data" / "fxmind.db"
BATCH_SIZE = 500
TABLE_COLLECTIONS = {
    "users": "users",
    "market_candles": "market_candles",
    "market_quotes": "market_quotes",
    "signals": "signals",
    "economic_events": "economic_events",
    "model_versions": "model_versions",
    "alerts": "alerts",
    "notifications": "notifications",
    "backtest_runs": "backtest_runs",
}
DATETIME_FIELDS = {
    "created_at",
    "updated_at",
    "timestamp",
    "training_start_date",
    "training_end_date",
    "validation_start_date",
    "validation_end_date",
    "test_start_date",
    "test_end_date",
    "outcome_timestamp",
    "start_date",
    "end_date",
}


def _convert_value(field: str, value: Any) -> Any:
    """Convert SQLite ISO datetime strings to BSON dates where applicable."""
    if value is None or field not in DATETIME_FIELDS or not isinstance(value, str):
        return value
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


async def migrate() -> None:
    settings = get_settings()
    if not settings.mongodb_uri or not settings.mongodb_uri.strip():
        raise RuntimeError("Set MONGODB_URI in backend/.env or the repository-root .env first.")
    if not SQLITE_PATH.is_file():
        raise FileNotFoundError(f"Existing SQLite database was not found: {SQLITE_PATH}")

    database = await connect_to_mongo()
    connection = sqlite3.connect(SQLITE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        existing_tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        migrated_counts: dict[str, int] = {}

        for table, collection_name in TABLE_COLLECTIONS.items():
            if table not in existing_tables:
                continue

            collection = database[collection_name]
            columns = [
                row["name"]
                for row in connection.execute(f'PRAGMA table_info("{table}")')
            ]
            if "id" not in columns:
                raise RuntimeError(f"Cannot safely migrate {table}: no id column exists.")

            has_reasons = table == "signals" and "signal_reasons" in existing_tables
            reasons_by_signal: dict[int, list[dict[str, Any]]] = {}
            if has_reasons:
                reason_columns = {
                    row["name"]
                    for row in connection.execute('PRAGMA table_info("signal_reasons")')
                }
                if {"signal_id", "category", "reason"}.issubset(reason_columns):
                    for reason in connection.execute(
                        'SELECT signal_id, category, reason, value, sentiment '
                        'FROM signal_reasons ORDER BY id'
                    ):
                        reasons_by_signal.setdefault(reason["signal_id"], []).append({
                            key: reason[key]
                            for key in ("category", "reason", "value", "sentiment")
                        })

            cursor = connection.execute(f'SELECT * FROM "{table}" ORDER BY id')
            migrated = 0
            while rows := cursor.fetchmany(BATCH_SIZE):
                operations = []
                max_id = 0
                for row in rows:
                    document = {
                        key: _convert_value(key, row[key])
                        for key in row.keys()
                        if key != "id"
                    }
                    document["_id"] = row["id"]
                    max_id = max(max_id, int(row["id"]))
                    if table == "signals":
                        document["reasons"] = reasons_by_signal.get(int(row["id"]), [])
                    operations.append(UpdateOne(
                        {"_id": document["_id"]},
                        {"$setOnInsert": document},
                        upsert=True,
                    ))

                if operations:
                    result = await collection.bulk_write(operations, ordered=False)
                    migrated += result.upserted_count
                    await database["counters"].update_one(
                        {"_id": collection_name},
                        {"$max": {"sequence": max_id}},
                        upsert=True,
                    )

            migrated_counts[collection_name] = migrated

        for name, count in migrated_counts.items():
            print(f"{name}: copied {count} new documents")
        print("Migration complete. Existing MongoDB documents were not overwritten.")
        print("The SQLite database was read-only and has not been changed or deleted.")
    finally:
        connection.close()
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(migrate())
