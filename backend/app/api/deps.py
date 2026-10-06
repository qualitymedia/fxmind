"""
API dependencies for FastAPI routes.
"""

from __future__ import annotations

from typing import AsyncGenerator, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.database import get_db


async def get_optional_user(
    user_id: Optional[int] = Depends(get_current_user_id),
) -> Optional[int]:
    """Return optional user ID if authenticated."""
    return user_id
