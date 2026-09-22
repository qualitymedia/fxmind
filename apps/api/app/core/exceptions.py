"""
Custom exceptions and FastAPI exception handlers for FXMind.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from apps.api.app.core.logging import get_logger

logger = get_logger(__name__)


# ── Custom Exception Classes ────────────────────


class FXMindError(Exception):
    """Base exception for all FXMind errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


class NotFoundError(FXMindError):
    """Resource not found."""

    def __init__(self, resource: str, identifier: Any = None):
        msg = f"{resource} not found"
        if identifier:
            msg = f"{resource} with id '{identifier}' not found"
        super().__init__(msg, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(FXMindError):
    """Data validation failed."""

    def __init__(self, message: str, errors: Optional[list[dict]] = None):
        super().__init__(
            message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors or []},
        )


class MarketDataError(FXMindError):
    """Market data is unavailable or stale."""

    def __init__(self, message: str = "Market data unavailable"):
        super().__init__(message, status_code=status.HTTP_530_SERVICE_UNAVAILABLE if hasattr(status, 'HTTP_530_SERVICE_UNAVAILABLE') else status.HTTP_503_SERVICE_UNAVAILABLE)


class ModelError(FXMindError):
    """ML model is unavailable or failed."""

    def __init__(self, message: str = "AI model unavailable"):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class AuthenticationError(FXMindError):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class RateLimitError(FXMindError):
    """Rate limit exceeded."""

    def __init__(self):
        super().__init__(
            "Rate limit exceeded. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# ── Exception Handlers ─────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""

    @app.exception_handler(FXMindError)
    async def fxmind_error_handler(request: Request, exc: FXMindError) -> JSONResponse:
        logger.error(
            f"application_error error={exc.message} status_code={exc.status_code} path={request.url}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            f"unhandled_error error={exc} path={request.url}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "An internal error occurred. Please try again later.",
                "detail": {},
            },
        )
