"""
Generic MongoDB repository for FXMind documents.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, Optional, Type, TypeVar

from pymongo.asynchronous.database import AsyncDatabase

from app.models.base import MongoDocument, from_mongo, to_mongo

ModelType = TypeVar("ModelType", bound=MongoDocument)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations."""

    def __init__(self, model: Type[ModelType], database: AsyncDatabase):
        self.model = model
        self.collection = database[model.collection]

    async def get_by_id(self, id: int | str) -> Optional[ModelType]:
        """Get a single record by ID."""
        return from_mongo(self.model, await self.collection.find_one({"_id": id}))

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
    ) -> list[ModelType]:
        """Get multiple records with pagination."""
        if order_by is not None:
            cursor = self.collection.find().sort(order_by)
        else:
            cursor = self.collection.find()
        documents = await cursor.skip(skip).limit(limit).to_list(length=limit)
        return [
            model
            for document in documents
            if (model := from_mongo(self.model, document)) is not None
        ]

    async def count(self) -> int:
        """Count total records."""
        return await self.collection.count_documents({})

    async def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        await self.collection.insert_one(to_mongo(obj))
        return obj

    async def create_many(self, objects: list[ModelType]) -> list[ModelType]:
        """Create multiple records."""
        if objects:
            await self.collection.insert_many([to_mongo(obj) for obj in objects])
        return objects

    async def update(self, obj: ModelType, **kwargs: Any) -> ModelType:
        """Update a record with the given keyword arguments."""
        valid_fields = self.model.model_fields
        updates = {
            key: value
            for key, value in kwargs.items()
            if key in valid_fields and key not in {"id", "created_at"}
        }
        updates["updated_at"] = datetime.now(timezone.utc)
        updated = obj.model_copy(update=updates)
        await self.collection.replace_one({"_id": obj.id}, to_mongo(updated))
        return updated

    async def delete(self, obj: ModelType) -> None:
        """Delete a record."""
        await self.collection.delete_one({"_id": obj.id})

    async def delete_by_id(self, id: int | str) -> bool:
        """Delete a record by ID. Returns True if deleted."""
        obj = await self.get_by_id(id)
        if obj:
            await self.delete(obj)
            return True
        return False
