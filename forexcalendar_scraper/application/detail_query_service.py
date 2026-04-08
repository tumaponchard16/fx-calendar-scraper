"""Service for querying detail CSV blocks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from forexcalendar_scraper.core.constants import DETAILS_FILE_GLOB
from forexcalendar_scraper.core.exceptions import InputFileResolutionError
from forexcalendar_scraper.ports import EventRepositoryPort, PathServicePort
from forexcalendar_scraper.utils.formatting import numeric_sort_key, truncate_text


@dataclass(slots=True)
class DetailQueryService:
    path_service: PathServicePort
    csv_repository: EventRepositoryPort

    def resolve_details_file(self, file_name: str | None) -> tuple[Path, bool]:
        if file_name:
            resolved_file = self.path_service.resolve_input_file(file_name)
            if resolved_file is None:
                raise InputFileResolutionError(f"File '{file_name}' not found.")
            return resolved_file, False

        details_files = self.path_service.find_matching_files(DETAILS_FILE_GLOB)
        if not details_files:
            raise InputFileResolutionError(
                "No details CSV files found. Specify one with --file or run the detail extraction workflow first."
            )
        latest_file = max(details_files, key=lambda path: path.stat().st_mtime)
        return latest_file, True

    def load_details(self, filename: str | Path) -> dict[str, dict[str, str]]:
        return self.csv_repository.load_detail_blocks(filename)

    def show_event(self, events: Mapping[str, Mapping[str, str]], event_id: str) -> str:
        if event_id not in events:
            return f"Event ID {event_id} not found.\n"

        event = events[event_id]
        event_name = event.get("event_name", "Unknown Event")
        lines = [f"Event {event_id}: {event_name}", "=" * 80]

        for field_name in ["event_date", "event_time", "event_currency", "detail_id"]:
            if field_name in event:
                lines.append(f"{field_name:20s}: {event[field_name]}")

        lines.append("")
        lines.append("Specifications:")
        lines.append("-" * 80)
        for field_name, field_value in sorted(event.items()):
            if field_name in {"event_date", "event_time", "event_currency", "detail_id", "event_name"}:
                continue
            lines.append(f"{field_name:20s}: {truncate_text(field_value, 60)}")

        lines.append("=" * 80)
        return "\n".join(lines) + "\n"

    def show_field_across_events(
        self,
        events: Mapping[str, Mapping[str, str]],
        field_name: str,
    ) -> str:
        lines = [f"Field '{field_name}' across all events:", "=" * 80]
        found_any = False
        for event_id in sorted(events.keys(), key=numeric_sort_key):
            event = events[event_id]
            if field_name not in event:
                continue
            found_any = True
            event_name = event.get("event_name", "Unknown")
            lines.append(
                f"Event {event_id}: {event_name[:30]:30s} | {truncate_text(event[field_name], 50)}"
            )

        if not found_any:
            lines.append(f"Field '{field_name}' not found in any event.")

        lines.append("=" * 80)
        return "\n".join(lines) + "\n"

    def show_specific_field(
        self,
        events: Mapping[str, Mapping[str, str]],
        event_id: str,
        field_name: str,
    ) -> str:
        if event_id not in events:
            return f"Event ID {event_id} not found.\n"

        event = events[event_id]
        if field_name not in event:
            available_fields = ", ".join(sorted(event.keys()))
            return (
                f"Field '{field_name}' not found in event {event_id}.\n"
                f"Available fields: {available_fields}\n"
            )

        event_name = event.get("event_name", "Unknown")
        lines = [f"Event {event_id}: {event_name}", f"Field: {field_name}", "=" * 80, event[field_name], "=" * 80]
        return "\n".join(lines) + "\n"

    def list_all_events(self, events: Mapping[str, Mapping[str, str]]) -> str:
        lines = [f"All Events ({len(events)} total):", "=" * 80]
        for event_id in sorted(events.keys(), key=numeric_sort_key):
            event = events[event_id]
            event_name = event.get("event_name", "Unknown")
            event_date = event.get("event_date", "N/A")
            event_time = event.get("event_time", "N/A")
            field_count = len(event)
            lines.append(
                f"Event {event_id}: {event_name[:40]:40s} | {event_date:12s} {event_time:10s} | {field_count} fields"
            )
        lines.append("=" * 80)
        return "\n".join(lines) + "\n"

    def list_all_fields(self, events: Mapping[str, Mapping[str, str]]) -> str:
        all_fields: set[str] = set()
        for event in events.values():
            all_fields.update(event.keys())

        lines = [f"All Unique Fields ({len(all_fields)} total):", "=" * 80]
        for field_name in sorted(all_fields):
            count = sum(1 for event in events.values() if field_name in event)
            lines.append(f"{field_name:25s} (present in {count}/{len(events)} events)")
        lines.append("=" * 80)
        return "\n".join(lines) + "\n"