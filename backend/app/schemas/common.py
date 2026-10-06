"""
Common Pydantic schemas for FXMind API responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Overall system status")
    database: str = Field(..., description="Database connection status")
    market_data: str = Field(..., description="Market data availability")
    model: str = Field(..., description="ML model status")
    model_version: Optional[str] = Field(None, description="Current production model version")
    last_market_update: Optional[datetime] = Field(None, description="Last market data timestamp")
    last_prediction: Optional[datetime] = Field(None, description="Last prediction timestamp")
    demo_mode: bool = Field(False, description="Whether running in demo mode")
    timestamp: datetime = Field(..., description="Health check timestamp")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: dict[str, Any] = Field(default_factory=dict)


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
