"""Application ports used by the clean and hexagonal architecture boundaries."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Iterable, Protocol

from forexcalendar_scraper.domain.entities import CalendarEvent, DetailBlock, HistoryNewsBundle, HistoryRecord, NewsItem


LoggerFactory = Callable[[str, Path, str | int | None], logging.Logger]


class PathServicePort(Protocol):
    """Port for resolving input and output paths."""

    def build_output_file_path(
        self,
        date_param: str,
        suffix: str = "",
        create_dir: bool = True,
    ) -> Path: ...

    def build_log_file_path(self, script_name: str) -> Path: ...

    def display_path(self, path: Path) -> str: ...

    def resolve_input_file(
        self,
        file_name: str | Path | None,
        preferred_date_param: str | None = None,
    ) -> Path | None: ...

    def resolve_primary_csv_path(self, csv_file: str | Path | None, date_param: str) -> Path | None: ...

    def find_matching_files(self, pattern: str) -> list[Path]: ...


class EventRepositoryPort(Protocol):
    """Port for reading and writing calendar data."""

    def load_event_rows(self, csv_file: str | Path) -> list[dict[str, str]]: ...

    def load_events(self, csv_file: str | Path) -> list[CalendarEvent]: ...

    def save_events(self, output_file: Path, events: Iterable[CalendarEvent]) -> None: ...

    def save_detail_blocks(self, output_file: Path, detail_blocks: Iterable[DetailBlock]) -> None: ...

    def load_detail_blocks(self, csv_file: str | Path) -> dict[str, dict[str, str]]: ...

    def save_history_records(self, output_file: Path, history_records: Iterable[HistoryRecord]) -> None: ...

    def save_news_items(self, output_file: Path, news_items: Iterable[NewsItem]) -> None: ...


class CalendarGatewayPort(Protocol):
    """Port for scraping and extracting ForexFactory data without exposing browser details."""

    def scrape_calendar(self, date_param: str, logger: logging.Logger) -> list[CalendarEvent]: ...

    def extract_detail_block(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> DetailBlock | None: ...

    def extract_history_records(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> list[HistoryRecord] | None: ...

    def extract_news_items(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> list[NewsItem] | None: ...

    def extract_history_news_bundle(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> HistoryNewsBundle | None: ...