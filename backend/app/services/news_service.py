"""Yahoo Finance headline retrieval for GBP/USD."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any

import yfinance as yf


class YahooNewsService:
    def __init__(self, cache_seconds: int = 300) -> None:
        self.cache_seconds = cache_seconds
        self._cached_at = 0.0
        self._cached_headlines: list[dict[str, Any]] = []

    async def get_headlines(self, limit: int = 10) -> list[dict[str, Any]]:
        if time.monotonic() - self._cached_at < self.cache_seconds:
            return self._cached_headlines[:limit]

        headlines = await asyncio.to_thread(self._search, limit)
        self._cached_headlines = headlines
        self._cached_at = time.monotonic()
        return headlines

    @staticmethod
    def _search(limit: int) -> list[dict[str, Any]]:
        results = yf.Search("GBPUSD", news_count=limit).news
        headlines = []
        for item in results:
            title = item.get("title")
            url = item.get("link")
            if not title or not url:
                continue

            published_at = item.get("providerPublishTime")
            if isinstance(published_at, (int, float)):
                published_at = datetime.fromtimestamp(published_at, timezone.utc)
            else:
                published_at = None

            headlines.append(
                {
                    "id": item.get("uuid") or url,
                    "title": title,
                    "publisher": item.get("publisher") or "Unknown publisher",
                    "url": url,
                    "published_at": published_at,
                    "image_url": next(
                        (
                            image.get("url")
                            for image in (item.get("thumbnail") or {}).get("resolutions", [])
                            if image.get("url")
                        ),
                        None,
                    ),
                    "related_tickers": item.get("relatedTickers") or [],
                }
            )
        return headlines


yahoo_news_service = YahooNewsService()