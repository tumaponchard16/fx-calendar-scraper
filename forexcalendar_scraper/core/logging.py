"""Logging helpers."""

from __future__ import annotations

import logging
from pathlib import Path

from forexcalendar_scraper.core.config import get_settings


def _resolve_log_level(level: str | int | None) -> int:
    if isinstance(level, int):
        return level
    if isinstance(level, str) and level:
        return getattr(logging, level.upper(), logging.INFO)
    return getattr(logging, get_settings().log_level.upper(), logging.INFO)


def configure_logger(logger_name: str, log_file: Path, level: str | int | None = None) -> logging.Logger:
    """Create a logger with matching console and file handlers."""

    logger = logging.getLogger(logger_name)
    logger.setLevel(_resolve_log_level(level))
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger
