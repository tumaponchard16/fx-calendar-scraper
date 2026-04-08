"""Shared runtime helpers for service construction."""

from __future__ import annotations

from pathlib import Path

from forexcalendar_scraper.core.exceptions import InputFileResolutionError
from forexcalendar_scraper.ports import PathServicePort


def resolve_required_input_csv(
    path_service: PathServicePort,
    csv_file: str | None,
    date_param: str,
) -> Path:
    resolved_csv = path_service.resolve_primary_csv_path(csv_file, date_param)
    if resolved_csv is None:
        missing_file = csv_file or f"{date_param}.csv"
        raise InputFileResolutionError(
            f"CSV file '{missing_file}' not found. Run the base scraper first."
        )
    return resolved_csv
