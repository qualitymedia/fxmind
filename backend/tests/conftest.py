"""
Pytest configuration and fixtures.
"""

import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.database import get_db
from app.main import app


class _FakeCollection:
    def __init__(self, document: dict | None = None):
        self.document = document

    async def find_one(self, *_args, **_kwargs):
        return self.document


class _FakeMongoDatabase:
    def __init__(self):
        now = datetime.now(timezone.utc)
        self.collections = {
            "market_candles": _FakeCollection({"timestamp": now}),
            "model_versions": _FakeCollection({"version": "test-model"}),
            "signals": _FakeCollection({"timestamp": now}),
        }

    def __getitem__(self, name: str) -> _FakeCollection:
        return self.collections[name]

    async def command(self, _command: str):
        return {"ok": 1}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client."""
    async def override_get_db():
        yield _FakeMongoDatabase()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        try:
            yield client
        finally:
            app.dependency_overrides.pop(get_db, None)
