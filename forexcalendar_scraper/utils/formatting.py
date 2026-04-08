"""Formatting helpers for labels and CLI output."""

from __future__ import annotations

import re


NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9_]+")


def sanitize_field_name(label: str) -> str:
    """Convert a scraped label into a stable field name."""

    normalized = label.strip().lower()
    normalized = normalized.replace("/", "_")
    normalized = normalized.replace(" ", "_")
    normalized = normalized.replace(":", "")
    normalized = normalized.replace("(", "")
    normalized = normalized.replace(")", "")
    normalized = NON_ALNUM_PATTERN.sub("_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_")


def truncate_text(value: str, limit: int) -> str:
    """Truncate a string without exceeding the requested display width."""

    if len(value) <= limit:
        return value
    return f"{value[: limit - 3]}..."


def numeric_sort_key(raw_value: str) -> tuple[int, int | str]:
    """Sort numeric strings numerically and fall back to lexical ordering."""

    if raw_value.isdigit():
        return (0, int(raw_value))
    return (1, raw_value)