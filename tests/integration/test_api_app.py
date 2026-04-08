from __future__ import annotations

from fastapi.testclient import TestClient
from forexcalendar_scraper.api.app import create_app
from forexcalendar_scraper.core.config import Settings
from forexcalendar_scraper.domain.entities import (
    CommandResult,
    DetailBlock,
    HistoryRecord,
    NewsItem,
    StoredCalendarEvent,
    StoredEventAggregate,
)


class StubEventCatalogService:
    def __init__(self) -> None:
        self.aggregate = StoredEventAggregate(
            event=StoredCalendarEvent(
                id=1,
                source_event_key="day=oct6.2025|mon oct 6|8:30am|usd|cpi m/m|12345",
                date_param="day=oct6.2025",
                date="Mon Oct 6",
                time="8:30am",
                currency="USD",
                impact="High",
                name="CPI m/m",
                actual="0.3%",
                forecast="0.2%",
                previous="0.2%",
                detail_id="12345",
                output_file="outputs/oct-06-2025/day=oct6.2025.csv",
            ),
            details=DetailBlock(
                detail_id="12345",
                event_date="Mon Oct 6",
                event_time="8:30am",
                event_currency="USD",
                event_name="CPI m/m",
                fields={"description": "Inflation release"},
            ),
            history=[
                HistoryRecord(
                    detail_id="12345",
                    date="Sep 6",
                    actual="0.2%",
                    forecast="0.1%",
                    previous="0.1%",
                    event_name="CPI m/m",
                    event_date="Mon Oct 6",
                    event_currency="USD",
                )
            ],
            news=[
                NewsItem(
                    detail_id="12345",
                    title="Inflation update",
                    url="https://example.com/news/inflation-update",
                    snippet="Coverage of the inflation release.",
                    link_type="news",
                    event_name="CPI m/m",
                    event_date="Mon Oct 6",
                    event_currency="USD",
                )
            ],
        )

    def list_events(
        self,
        date_param: str | None = None,
        currency: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredCalendarEvent]:
        return [self.aggregate.event]

    def get_event(self, event_id: int) -> StoredEventAggregate:
        return self.aggregate

    def get_event_details(self, event_id: int) -> DetailBlock | None:
        return self.aggregate.details

    def list_event_history(self, event_id: int) -> list[HistoryRecord]:
        return self.aggregate.history

    def list_event_news(self, event_id: int) -> list[NewsItem]:
        return self.aggregate.news


class StubWorkflowService:
    def __init__(self, written_counts: dict[str, int]) -> None:
        self.written_counts = written_counts
        self.calls: list[dict[str, str | None]] = []

    def run(self, date_param: str, csv_file: str | None = None) -> CommandResult:
        self.calls.append({"date_param": date_param, "csv_file": csv_file})
        return CommandResult(processed_events=1, written_counts=dict(self.written_counts))


def test_api_app_serves_docs_and_event_resources():
    app = create_app(
        settings=Settings(postgres_enabled=True, postgres_dsn="postgresql://example/test"),
        event_catalog_service=StubEventCatalogService(),
        scraper_service=StubWorkflowService({"events": 1}),
        detail_extraction_service=StubWorkflowService({"details": 1}),
        history_extraction_service=StubWorkflowService({"history": 1}),
        news_extraction_service=StubWorkflowService({"news": 1}),
        history_news_extraction_service=StubWorkflowService({"history": 1, "news": 1}),
    )
    client = TestClient(app)

    docs_response = client.get("/docs")
    events_response = client.get("/events")
    event_response = client.get("/events/1")
    detail_response = client.get("/events/1/details")
    history_response = client.get("/events/1/history")
    news_response = client.get("/events/1/news")

    assert docs_response.status_code == 200
    assert events_response.status_code == 200
    assert event_response.status_code == 200
    assert detail_response.status_code == 200
    assert history_response.status_code == 200
    assert news_response.status_code == 200
    assert events_response.json()[0]["name"] == "CPI m/m"
    assert event_response.json()["details"]["fields"]["description"] == "Inflation release"
    assert history_response.json()[0]["actual"] == "0.2%"
    assert news_response.json()[0]["title"] == "Inflation update"


def test_api_app_runs_workflows_from_http_requests():
    scrape_service = StubWorkflowService({"events": 1})
    details_service = StubWorkflowService({"details": 1})
    history_service = StubWorkflowService({"history": 1})
    news_service = StubWorkflowService({"news": 1})
    history_news_service = StubWorkflowService({"history": 1, "news": 1})
    app = create_app(
        settings=Settings(postgres_enabled=True, postgres_dsn="postgresql://example/test"),
        event_catalog_service=StubEventCatalogService(),
        scraper_service=scrape_service,
        detail_extraction_service=details_service,
        history_extraction_service=history_service,
        news_extraction_service=news_service,
        history_news_extraction_service=history_news_service,
    )
    client = TestClient(app)

    health_response = client.get("/health")
    scrape_response = client.post("/workflows/scrape", json={"date_param": "day=oct6.2025"})
    details_response = client.post(
        "/workflows/details",
        json={"date_param": "day=oct6.2025", "csv_file": "outputs/oct-06-2025/day=oct6.2025.csv"},
    )
    history_response = client.post("/workflows/history", json={"date_param": "day=oct6.2025"})
    news_response = client.post("/workflows/news", json={"date_param": "day=oct6.2025"})
    history_news_response = client.post(
        "/workflows/history-news",
        json={"date_param": "day=oct6.2025"},
    )

    assert health_response.status_code == 200
    assert health_response.json()["postgres_enabled"] is True
    assert scrape_response.json()["written_counts"] == {"events": 1}
    assert details_response.json()["written_counts"] == {"details": 1}
    assert history_response.json()["written_counts"] == {"history": 1}
    assert news_response.json()["written_counts"] == {"news": 1}
    assert history_news_response.json()["written_counts"] == {"history": 1, "news": 1}
    assert scrape_service.calls[0]["date_param"] == "day=oct6.2025"
    assert details_service.calls[0]["csv_file"] == "outputs/oct-06-2025/day=oct6.2025.csv"