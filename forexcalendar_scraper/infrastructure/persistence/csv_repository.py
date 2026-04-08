"""CSV-backed repository layer."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from forexcalendar_scraper.domain.entities import CalendarEvent, DetailBlock, HistoryRecord, NewsItem


class CsvRepository:
    """Read and write CSV files used by the project."""

    def load_event_rows(self, csv_file: str | Path) -> list[dict[str, str]]:
        events: list[dict[str, str]] = []
        with Path(csv_file).open("r", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            if reader.fieldnames:
                reader.fieldnames = [field.strip() if field else field for field in reader.fieldnames]

            for row in reader:
                cleaned_row: dict[str, str] = {}
                for key, value in row.items():
                    cleaned_key = key.strip() if key else ""
                    cleaned_value = value.strip() if isinstance(value, str) else ""
                    cleaned_row[cleaned_key] = cleaned_value
                events.append(cleaned_row)
        return events

    def load_events(self, csv_file: str | Path) -> list[CalendarEvent]:
        return [CalendarEvent.from_mapping(row) for row in self.load_event_rows(csv_file)]

    def save_events(self, output_file: Path, events: Iterable[CalendarEvent]) -> None:
        event_rows = [event.to_csv_row() for event in events]
        if not event_rows:
            return

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", newline="", encoding="utf-8") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=list(event_rows[0].keys()))
            writer.writeheader()
            writer.writerows(event_rows)

    def save_detail_blocks(self, output_file: Path, detail_blocks: Iterable[DetailBlock]) -> None:
        blocks = list(detail_blocks)
        if not blocks:
            return

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", newline="", encoding="utf-8") as file_handle:
            writer = csv.writer(file_handle)
            for event_id, block in enumerate(blocks, start=1):
                writer.writerows(block.to_block_rows(event_id))
                if event_id < len(blocks):
                    writer.writerow(["---", "---"])

    def load_detail_blocks(self, csv_file: str | Path) -> dict[str, dict[str, str]]:
        events: dict[str, dict[str, str]] = {}
        current_event_id: str | None = None

        with Path(csv_file).open("r", encoding="utf-8") as file_handle:
            reader = csv.reader(file_handle)
            for row in reader:
                if len(row) < 2:
                    continue

                field_name = row[0].strip()
                field_value = row[1].strip()

                if field_name == "---":
                    continue
                if field_name == "event_id":
                    current_event_id = field_value
                    events[current_event_id] = {}
                    continue
                if current_event_id is not None:
                    events[current_event_id][field_name] = field_value

        return events

    def save_history_records(self, output_file: Path, history_records: Iterable[HistoryRecord]) -> None:
        records = [record.to_csv_row() for record in history_records]
        if not records:
            return

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", newline="", encoding="utf-8") as file_handle:
            fieldnames = [
                "detail_id",
                "event_name",
                "event_date",
                "event_currency",
                "date",
                "date_url",
                "actual",
                "forecast",
                "previous",
            ]
            writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    def save_news_items(self, output_file: Path, news_items: Iterable[NewsItem]) -> None:
        records = [record.to_csv_row() for record in news_items]
        if not records:
            return

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", newline="", encoding="utf-8") as file_handle:
            fieldnames = [
                "detail_id",
                "event_name",
                "event_date",
                "event_currency",
                "title",
                "url",
                "snippet",
                "link_type",
            ]
            writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
