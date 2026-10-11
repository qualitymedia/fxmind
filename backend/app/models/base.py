"""Pydantic document models and MongoDB document conversion helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, ClassVar, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DocumentType = TypeVar("DocumentType", bound="MongoDocument")


class MongoDocument(BaseModel):
    """Base document with API-compatible IDs and UTC audit timestamps."""

    model_config = ConfigDict(populate_by_name=True)

    collection: ClassVar[str]
    id: int | str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def from_mongo(model: type[DocumentType], document: dict[str, Any] | None) -> DocumentType | None:
    """Validate a MongoDB document as its API-facing Pydantic model."""
    if document is None:
        return None
    data = dict(document)
    data["id"] = data.pop("_id")
    return model.model_validate(data)


def to_mongo(document: MongoDocument) -> dict[str, Any]:
    """Serialize a document while mapping its public id to MongoDB's _id."""
    data = document.model_dump()
    data["_id"] = data.pop("id")
    return data
