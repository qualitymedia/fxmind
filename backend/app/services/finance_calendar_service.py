"""FinanceCalendar.com event feed adapter for GBP/USD insights."""

from __future__ import annotations

import hashlib
import re
import time
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx


BASE_URL = "https://www.financecalendar.com/wp-json/fc/v1"
_GBP_TERMS = re.compile(r"\b(uk|britain|british|england|boe|bank of england|mpc)\b", re.IGNORECASE)
_USD_TERMS = re.compile(r"\b(us|u\.s\.|united states|fed|fomc|federal reserve)\b", re.IGNORECASE)


def _currency_for_event(event: dict[str, Any]) -> str | None:
    text = f"{event.get('name', '')} {event.get('title', '')}"
    if _GBP_TERMS.search(text):
        return "GBP"
    if _USD_TERMS.search(text):
        return "USD"
    return None


def _normalize_event(event: dict[str, Any]) -> dict[str, Any] | None:
    currency = _currency_for_event(event)
    event_date = event.get("date")
    title = event.get("name") or event.get("title")
    source_url = event.get("url")
    if not currency or not event_date or not title or not source_url:
        return None

    all_day = bool(event.get("all_day"))
    event_time = event.get("time_utc")
    if event_time:
        timestamp = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        timestamp = timestamp.astimezone(timezone.utc)
    else:
        timestamp = datetime.combine(date.fromisoformat(event_date), datetime.min.time(), timezone.utc)

    key = f"{event_date}:{title}:{source_url}".encode("utf-8")
    event_id = int.from_bytes(hashlib.sha256(key).digest()[:7], "big")
    return {
        "id": event_id,
        "timestamp": timestamp.isoformat(),
        "currency": currency,
        "event": title,
        "importance": str(event.get("impact") or "low").upper(),
        "actual": event.get("actual"),
        "forecast": event.get("consensus"),
        "previous": event.get("prior"),
        "event_code": event.get("category"),
        "all_day": all_day,
        "url": source_url,
    }


class FinanceCalendarService:
    def __init__(self, cache_seconds: int = 300) -> None:
        self.cache_seconds = cache_seconds
        self._cached_at = 0.0
        self._cached_from: date | None = None
        self._cached_to: date | None = None
        self._cached_events: list[dict[str, Any]] = []

    async def get_events(self, days: int = 14, high_impact_only: bool = False) -> list[dict[str, Any]]:
        today = datetime.now(timezone.utc).date()
        end_date = today + timedelta(days=days)
        cache_valid = (
            self._cached_from == today
            and self._cached_to == end_date
            and time.monotonic() - self._cached_at < self.cache_seconds
        )
        if not cache_valid:
            params = {"from": today.isoformat(), "to": end_date.isoformat(), "limit": 500}
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{BASE_URL}/calendar", params=params)
                response.raise_for_status()
                payload = response.json()

            events = [_normalize_event(event) for event in payload.get("events", [])]
            self._cached_events = [event for event in events if event is not None]
            self._cached_from = today
            self._cached_to = end_date
            self._cached_at = time.monotonic()

        events = self._cached_events
        if high_impact_only:
            events = [event for event in events if event["importance"] == "HIGH"]
        return events[:500]


finance_calendar_service = FinanceCalendarService()