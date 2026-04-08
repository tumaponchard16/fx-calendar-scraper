"""Database-backed event query service for API consumers."""

from __future__ import annotations

from dataclasses import dataclass

from forexcalendar_scraper.core.exceptions import EventNotFoundError, StorageUnavailableError
from forexcalendar_scraper.domain.entities import DetailBlock, HistoryRecord, NewsItem, StoredCalendarEvent, StoredEventAggregate
from forexcalendar_scraper.ports import EventStorePort


@dataclass(slots=True)
class EventCatalogService:
    event_store: EventStorePort

    def list_events(
        self,
        date_param: str | None = None,
        currency: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredCalendarEvent]:
        self._ensure_store_available()
        return self.event_store.list_events(
            date_param=date_param,
            currency=currency,
            limit=limit,
            offset=offset,
        )

    def get_event(self, event_id: int) -> StoredEventAggregate:
        self._ensure_store_available()
        event = self.event_store.get_event(event_id)
        if event is None:
            raise EventNotFoundError(f"Stored event {event_id} was not found.")
        return event

    def get_event_details(self, event_id: int) -> DetailBlock | None:
        return self.get_event(event_id).details

    def list_event_history(self, event_id: int) -> list[HistoryRecord]:
        return self.get_event(event_id).history

    def list_event_news(self, event_id: int) -> list[NewsItem]:
        return self.get_event(event_id).news

    def _ensure_store_available(self) -> None:
        if self.event_store.is_enabled():
            return
        raise StorageUnavailableError(
            "PostgreSQL storage is not configured. Set FOREXFACTORY_POSTGRES_DSN and enable FOREXFACTORY_POSTGRES_ENABLED to use database-backed endpoints."
        )