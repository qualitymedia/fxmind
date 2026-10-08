"""
Database engine and session management for FXMind.

Uses SQLAlchemy async engine with asyncpg for PostgreSQL.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


# Engine and session factory — initialized lazily
_engine = None
_session_factory = None


async def _configure_sqlite(conn, _):
    """Enable WAL journal mode and busy timeout on every new SQLite connection."""
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA busy_timeout=30000")  # 30s wait before SQLITE_BUSY error
    await conn.execute("PRAGMA synchronous=NORMAL")


def get_engine():
    """Get or create the async engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        if "sqlite" in settings.db_url:
            from sqlalchemy import event
            _engine = create_async_engine(
                settings.db_url,
                echo=settings.debug and settings.app_env.value == "development",
                connect_args={"timeout": 30},
            )
            # Apply WAL + busy timeout on every new connection
            event.listen(_engine.sync_engine, "connect", lambda c, _: (
                c.execute("PRAGMA journal_mode=WAL"),
                c.execute("PRAGMA busy_timeout=30000"),
                c.execute("PRAGMA synchronous=NORMAL"),
            ))
        else:
            _engine = create_async_engine(
                settings.db_url,
                echo=settings.debug and settings.app_env.value == "development",
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
            )
    return _engine


async def init_db() -> None:
    """Initialize database tables."""
    # Import all models to ensure metadata registration
    import app.models  # noqa: F401
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_session_factory():
    """Get or create the async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    """Dispose the engine on shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
