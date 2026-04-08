"""No-op database store used when PostgreSQL is disabled."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from forexcalendar_scraper.domain.entities import (
    CalendarEvent,
    DetailBlock,
    HistoryRecord,
    NewsItem,
    StoredCalendarEvent,
    StoredEventAggregate,
)


class NullEventStore:
    """No-op implementation of the database store contract."""

    def is_enabled(self) -> bool:
        return False

    def upsert_events(
        self,
        date_param: str,
        events: Iterable[CalendarEvent],
        output_file: str | None = None,
    ) -> None:
        return None

    def upsert_detail_blocks(
        self,
        date_param: str,
        detail_results: Iterable[tuple[CalendarEvent, DetailBlock]],
    ) -> None:
        return None

    def replace_history_records(
        self,
        date_param: str,
        history_results: Iterable[tuple[CalendarEvent, Sequence[HistoryRecord]]],
    ) -> None:
        return None

    def replace_news_items(
        self,
        date_param: str,
        news_results: Iterable[tuple[CalendarEvent, Sequence[NewsItem]]],
    ) -> None:
        return None

    def list_events(
        self,
        date_param: str | None = None,
        currency: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredCalendarEvent]:
        return []

    def get_event(self, event_id: int) -> StoredEventAggregate | None:
        return None