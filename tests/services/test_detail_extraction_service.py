from __future__ import annotations

import logging

from forexcalendar_scraper.application.detail_extraction_service import DetailExtractionService
from forexcalendar_scraper.core.config import Settings
from forexcalendar_scraper.core.paths import PathService
from forexcalendar_scraper.domain.entities import CalendarEvent, DetailBlock
from forexcalendar_scraper.infrastructure.persistence.csv_repository import CsvRepository


class StubDetailGateway:
    def extract_detail_block(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> DetailBlock | None:
        if event.detail_id != "12345":
            return None
        return DetailBlock(
            detail_id=event.detail_id,
            event_date=event.date,
            event_time=event.time,
            event_currency=event.currency,
            event_name=event.name,
            fields={
                "description": "Moderated discussion",
                "speaker": "Alberto Musalem",
            },
        )


class StubEventStore:
    def __init__(self) -> None:
        self.detail_results: list[tuple[CalendarEvent, DetailBlock]] = []

    def is_enabled(self) -> bool:
        return True

    def upsert_detail_blocks(
        self,
        date_param: str,
        detail_results: list[tuple[CalendarEvent, DetailBlock]],
    ) -> None:
        self.detail_results = list(detail_results)


def _build_test_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    logger.propagate = False
    return logger


def test_detail_extraction_service_writes_vertical_blocks(tmp_path):
    path_service = PathService.from_root(tmp_path)
    repository = CsvRepository()
    logger = _build_test_logger("test.detail_extractor")
    event_store = StubEventStore()

    input_file = path_service.build_output_file_path("day=oct6.2025")
    repository.save_events(
        input_file,
        [
            CalendarEvent(
                date="Mon Oct 6",
                time="8:30am",
                currency="USD",
                name="CPI m/m",
                detail_id="12345",
            )
        ],
    )

    service = DetailExtractionService(
        settings=Settings(request_delay_seconds=0.0, batch_delay_seconds=0.0),
        path_service=path_service,
        csv_repository=repository,
        calendar_gateway=StubDetailGateway(),
        logger_factory=lambda *args, **kwargs: logger,
        event_store=event_store,
    )

    result = service.run(date_param="day=oct6.2025")

    output_file = path_service.build_output_file_path("day=oct6.2025", "_details", create_dir=False)
    detail_blocks = repository.load_detail_blocks(output_file)

    assert result.processed_events == 1
    assert result.written_counts == {"details": 1}
    assert detail_blocks["1"]["detail_id"] == "12345"
    assert detail_blocks["1"]["description"] == "Moderated discussion"
    assert detail_blocks["1"]["speaker"] == "Alberto Musalem"
    assert event_store.detail_results[0][0].detail_id == "12345"
    assert event_store.detail_results[0][1].fields["speaker"] == "Alberto Musalem"