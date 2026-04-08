from __future__ import annotations

import logging

from forexcalendar_scraper.core.config import Settings
from forexcalendar_scraper.core.paths import PathService
from forexcalendar_scraper.domain.entities import CalendarEvent, HistoryNewsBundle, HistoryRecord, NewsItem
from forexcalendar_scraper.infrastructure.persistence.csv_repository import CsvRepository
from forexcalendar_scraper.application.history_news_extraction_service import HistoryNewsExtractionService


class StubHistoryNewsGateway:
    def extract_history_news_bundle(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> HistoryNewsBundle | None:
        if event.detail_id != "12345":
            return None

        history = [
            HistoryRecord(
                detail_id=event.detail_id,
                date="Sep 6",
                actual="0.2%",
                forecast="0.1%",
                previous="0.1%",
                event_name=event.name,
                event_date=event.date,
                event_currency=event.currency,
            )
        ]
        news = [
            NewsItem(
                detail_id=event.detail_id,
                title="Inflation update",
                url="https://example.com/news/inflation-update",
                snippet="Coverage of the inflation release.",
                link_type="news",
                event_name=event.name,
                event_date=event.date,
                event_currency=event.currency,
            )
        ]
        return HistoryNewsBundle(history=history, news=news)


def _build_test_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    logger.propagate = False
    return logger


def test_history_news_extraction_service_writes_both_outputs(tmp_path):
    path_service = PathService.from_root(tmp_path)
    repository = CsvRepository()
    logger = _build_test_logger("test.history_news_extractor")

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

    service = HistoryNewsExtractionService(
        settings=Settings(request_delay_seconds=0.0, batch_delay_seconds=0.0),
        path_service=path_service,
        csv_repository=repository,
        calendar_gateway=StubHistoryNewsGateway(),
        logger_factory=lambda *args, **kwargs: logger,
    )

    result = service.run(date_param="day=oct6.2025")

    history_file = path_service.build_output_file_path("day=oct6.2025", "_history", create_dir=False)
    news_file = path_service.build_output_file_path("day=oct6.2025", "_news", create_dir=False)
    history_rows = repository.load_event_rows(history_file)
    news_rows = repository.load_event_rows(news_file)

    assert result.processed_events == 1
    assert result.written_counts == {"history": 1, "news": 1}
    assert history_rows[0]["event_name"] == "CPI m/m"
    assert history_rows[0]["actual"] == "0.2%"
    assert news_rows[0]["title"] == "Inflation update"
    assert news_rows[0]["event_currency"] == "USD"