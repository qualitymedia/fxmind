"""MongoDB client lifecycle and collection indexes."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Optional

from pymongo import ASCENDING, DESCENDING, ReturnDocument, AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings

_client: Optional[AsyncMongoClient] = None
_database: Optional[AsyncDatabase] = None


async def connect_to_mongo() -> AsyncDatabase:
    """Connect to MongoDB and ensure indexes exist before serving requests."""
    global _client, _database
    settings = get_settings()
    if not settings.mongodb_uri or not settings.mongodb_uri.strip():
        raise RuntimeError(
            "MONGODB_URI is required. Add your MongoDB Atlas connection string "
            "to backend/.env before starting FXMind."
        )

    if _client is None:
        _client = AsyncMongoClient(settings.mongodb_uri, tz_aware=True)
        _database = _client[settings.mongodb_database]

    try:
        await _client.admin.command("ping")
    except Exception:
        await close_mongo_connection()
        raise
    assert _database is not None

    await _database["signals"].create_index(
        [("symbol", ASCENDING), ("timestamp", DESCENDING)]
    )
    await _database["signals"].create_index(
        [("status", ASCENDING), ("timestamp", DESCENDING)]
    )
    await _database["signals"].create_index(
        [("outcome", ASCENDING), ("outcome_timestamp", DESCENDING)]
    )
    await _database["market_candles"].create_index(
        [("symbol", ASCENDING), ("timeframe", ASCENDING), ("timestamp", ASCENDING)],
        unique=True,
    )
    await _database["market_quotes"].create_index(
        [("symbol", ASCENDING), ("timestamp", DESCENDING)]
    )
    await _database["economic_events"].create_index(
        [("timestamp", ASCENDING), ("currency", ASCENDING), ("importance", ASCENDING)]
    )
    await _database["model_versions"].create_index("version", unique=True)
    await _database["model_versions"].create_index(
        [("state", ASCENDING), ("created_at", DESCENDING)]
    )
    await _database["users"].create_index("email", unique=True)
    await _database["alerts"].create_index("user_id")
    await _database["notifications"].create_index(
        [("user_id", ASCENDING), ("is_read", ASCENDING)]
    )
    await _database["backtest_runs"].create_index(
        [("model_version", ASCENDING), ("start_date", DESCENDING)]
    )
    return _database


def get_database() -> AsyncDatabase:
    """Return the connected database or fail clearly when startup was skipped."""
    if _database is None:
        raise RuntimeError("MongoDB is not connected; application startup did not complete.")
    return _database


async def get_db() -> AsyncGenerator[AsyncDatabase, None]:
    """FastAPI dependency yielding the shared MongoDB database."""
    yield get_database()


async def next_document_id(database: AsyncDatabase, collection: str) -> int:
    """Allocate a process-safe integer ID for endpoints that expose numeric IDs."""
    counter = await database["counters"].find_one_and_update(
        {"_id": collection},
        {"$inc": {"sequence": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(counter["sequence"])


async def close_mongo_connection() -> None:
    """Close the shared MongoDB client during application shutdown."""
    global _client, _database
    if _client is not None:
        await _client.close()
    _client = None
    _database = None
