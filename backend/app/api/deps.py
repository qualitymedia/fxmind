"""
API dependencies for FastAPI routes.
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status

from app.core.config import AppEnv, get_settings
from app.core.security import get_current_user_id


async def get_optional_user(
    user_id: Optional[int] = Depends(get_current_user_id),
) -> Optional[int]:
    """Return optional user ID if authenticated."""
    return user_id


def require_authenticated_user_features() -> None:
    """Disable user-specific routes until authentication and ownership checks exist."""
    if get_settings().app_env is AppEnv.PRODUCTION:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="This feature is unavailable until account authentication is enabled.",
        )
