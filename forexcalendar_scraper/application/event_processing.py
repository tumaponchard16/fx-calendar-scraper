"""Shared processing workflow for detail-based extractors."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import time
from typing import Callable, Generic, Sequence, TypeVar

from forexcalendar_scraper.core.config import Settings
from forexcalendar_scraper.domain.entities import CalendarEvent


PayloadT = TypeVar("PayloadT")


@dataclass(slots=True)
class BatchProcessingSummary:
    processed_events: int = 0
    failed_events: int = 0
    skipped_events: int = 0


class EventBatchProcessor(Generic[PayloadT]):
    """Run per-event extraction with consistent delays and browser lifecycle."""

    def __init__(
        self,
        settings: Settings,
        logger: logging.Logger,
    ) -> None:
        self.settings = settings
        self.logger = logger

    def process(
        self,
        events: Sequence[CalendarEvent],
        extractor: Callable[[CalendarEvent], PayloadT | None],
        progress_message: str,
    ) -> tuple[list[tuple[CalendarEvent, PayloadT]], BatchProcessingSummary]:
        results: list[tuple[CalendarEvent, PayloadT]] = []
        summary = BatchProcessingSummary()

        for index, event in enumerate(events, start=1):
            if not event.detail_id:
                summary.skipped_events += 1
                self.logger.debug("Skipping event %s because it has no detail ID", index)
                self._apply_delay(index, len(events))
                continue

            payload = extractor(event)

            if payload:
                results.append((event, payload))
                summary.processed_events += 1
                if summary.processed_events % self.settings.batch_size == 0:
                    self.logger.info(progress_message, summary.processed_events)
            else:
                summary.failed_events += 1

            self._apply_delay(index, len(events))

        return results, summary

    def _apply_delay(self, index: int, total_events: int) -> None:
        if index >= total_events:
            return

        if index % self.settings.batch_size == 0:
            delay = self.settings.batch_delay_seconds
            self.logger.info("Waiting %.1f seconds (batch delay)", delay)
        else:
            delay = self.settings.request_delay_seconds
            self.logger.debug("Waiting %.1f seconds", delay)

        if delay > 0:
            time.sleep(delay)
