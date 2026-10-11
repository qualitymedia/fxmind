"""MongoDB document for user accounts."""

from __future__ import annotations

from typing import ClassVar, Optional

from app.models.base import MongoDocument


class User(MongoDocument):
    """User account."""

    collection: ClassVar[str] = "users"
    email: str
    hashed_password: str
    display_name: Optional[str] = None
    timezone: str = "UTC"
    is_active: bool = True
    settings_json: Optional[str] = None
