"""Market news REST endpoint."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.news_service import yahoo_news_service

router = APIRouter(prefix="/news", tags=["news"])


class NewsHeadline(BaseModel):
    id: str
    title: str
    publisher: str
    url: str
    published_at: datetime | None
    image_url: str | None
    related_tickers: list[str]


@router.get("", response_model=list[NewsHeadline])
async def get_market_news(
    limit: int = Query(default=10, ge=1, le=20),
) -> list[NewsHeadline]:
    try:
        return await yahoo_news_service.get_headlines(limit)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Yahoo Finance news is temporarily unavailable.",
        ) from exc