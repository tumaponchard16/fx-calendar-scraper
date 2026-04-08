from __future__ import annotations

import logging

from forexcalendar_scraper.application.calendar_scraper_service import CalendarScraperService
from forexcalendar_scraper.core.config import Settings
from forexcalendar_scraper.core.paths import PathService
from forexcalendar_scraper.domain.entities import CalendarEvent
from forexcalendar_scraper.infrastructure.persistence.csv_repository import CsvRepository


class StubCalendarGateway:
    def scrape_calendar(self, date_param: str, logger: logging.Logger) -> list[CalendarEvent]:
        return [
            CalendarEvent(
                date="Mon Oct 6",
                time="8:30am",
                currency="USD",
                impact="High",
                name="CPI m/m",
                actual="0.3%",
                forecast="0.2%",
                previous="0.2%",
                detail_id="12345",
            )
        ]


class StubEventStore:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, list[CalendarEvent], str | None]] = []

    def is_enabled(self) -> bool:
        return True

    def upsert_events(
        self,
        date_param: str,
        events: list[CalendarEvent],
        output_file: str | None = None,
    ) -> None:
        self.calls.append(("events", date_param, list(events), output_file))


def _build_test_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    logger.propagate = False
    return logger


def test_calendar_scraper_service_writes_events(tmp_path):
    path_service = PathService.from_root(tmp_path)
    repository = CsvRepository()
    logger = _build_test_logger("test.calendar_scraper")
    event_store = StubEventStore()

    service = CalendarScraperService(
        settings=Settings(),
        path_service=path_service,
        csv_repository=repository,
        calendar_gateway=StubCalendarGateway(),
        logger_factory=lambda *args, **kwargs: logger,
        event_store=event_store,
    )

    result = service.run("day=oct6.2025")

    output_file = path_service.build_output_file_path("day=oct6.2025", create_dir=False)
    rows = repository.load_event_rows(output_file)

    assert result.processed_events == 1
    assert result.written_counts == {"events": 1}
    assert rows[0]["event"] == "CPI m/m"
    assert rows[0]["detail"] == "12345"
    assert event_store.calls[0][0] == "events"
    assert event_store.calls[0][1] == "day=oct6.2025"
    assert event_store.calls[0][2][0].name == "CPI m/m"