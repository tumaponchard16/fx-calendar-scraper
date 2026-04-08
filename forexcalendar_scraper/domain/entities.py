"""Data models exchanged across repositories, services, and integrations."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Mapping


def _read_mapping_value(row: Mapping[str, object], key: str) -> str:
    value = row.get(key, "")
    return str(value).strip() if value is not None else ""


@dataclass(slots=True)
class CalendarEvent:
    date: str = ""
    time: str = ""
    currency: str = ""
    impact: str = ""
    name: str = ""
    actual: str = ""
    forecast: str = ""
    previous: str = ""
    detail_id: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> "CalendarEvent":
        return cls(
            date=_read_mapping_value(row, "date"),
            time=_read_mapping_value(row, "time"),
            currency=_read_mapping_value(row, "currency"),
            impact=_read_mapping_value(row, "impact"),
            name=_read_mapping_value(row, "event"),
            actual=_read_mapping_value(row, "actual"),
            forecast=_read_mapping_value(row, "forecast"),
            previous=_read_mapping_value(row, "previous"),
            detail_id=_read_mapping_value(row, "detail"),
        )

    def to_csv_row(self) -> dict[str, str]:
        return {
            "date": self.date,
            "time": self.time,
            "currency": self.currency,
            "impact": self.impact,
            "event": self.name,
            "actual": self.actual,
            "forecast": self.forecast,
            "previous": self.previous,
            "detail": self.detail_id,
        }


@dataclass(slots=True)
class DetailBlock:
    detail_id: str
    event_date: str = ""
    event_time: str = ""
    event_currency: str = ""
    event_name: str = ""
    fields: dict[str, str] = field(default_factory=dict)

    def to_flat_mapping(self) -> dict[str, str]:
        mapping = {
            "detail_id": self.detail_id,
            "event_date": self.event_date,
            "event_time": self.event_time,
            "event_currency": self.event_currency,
            "event_name": self.event_name,
        }
        mapping.update(self.fields)
        return {key: value for key, value in mapping.items() if value != ""}

    def to_block_rows(self, event_id: int) -> list[list[str]]:
        rows = [["event_id", str(event_id)]]
        for field_name, field_value in self.to_flat_mapping().items():
            rows.append([field_name, field_value])
        return rows


@dataclass(slots=True)
class HistoryRecord:
    detail_id: str
    date: str
    date_url: str = ""
    actual: str = ""
    forecast: str = ""
    previous: str = ""
    event_name: str = ""
    event_date: str = ""
    event_currency: str = ""

    def with_event_context(self, event: CalendarEvent) -> "HistoryRecord":
        return replace(
            self,
            event_name=event.name,
            event_date=event.date,
            event_currency=event.currency,
        )

    def to_csv_row(self) -> dict[str, str]:
        return {
            "detail_id": self.detail_id,
            "event_name": self.event_name,
            "event_date": self.event_date,
            "event_currency": self.event_currency,
            "date": self.date,
            "date_url": self.date_url,
            "actual": self.actual,
            "forecast": self.forecast,
            "previous": self.previous,
        }


@dataclass(slots=True)
class NewsItem:
    detail_id: str
    title: str
    url: str
    snippet: str = ""
    link_type: str = "related"
    event_name: str = ""
    event_date: str = ""
    event_currency: str = ""

    def with_event_context(self, event: CalendarEvent) -> "NewsItem":
        return replace(
            self,
            event_name=event.name,
            event_date=event.date,
            event_currency=event.currency,
        )

    def to_csv_row(self) -> dict[str, str]:
        return {
            "detail_id": self.detail_id,
            "event_name": self.event_name,
            "event_date": self.event_date,
            "event_currency": self.event_currency,
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "link_type": self.link_type,
        }


@dataclass(slots=True)
class HistoryNewsBundle:
    history: list[HistoryRecord] = field(default_factory=list)
    news: list[NewsItem] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.history or self.news)


@dataclass(slots=True)
class CommandResult:
    processed_events: int = 0
    failed_events: int = 0
    skipped_events: int = 0
    written_counts: dict[str, int] = field(default_factory=dict)
    output_files: dict[str, Path] = field(default_factory=dict)
