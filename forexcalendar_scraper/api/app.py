"""FastAPI application exposing scrape workflows and stored event data."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query, status

from forexcalendar_scraper.api.models import (
    CommandResultModel,
    DetailModel,
    EventAggregateModel,
    EventSummaryModel,
    ExtractWorkflowRequestModel,
    HealthResponseModel,
    HistoryRecordModel,
    NewsItemModel,
    ScrapeWorkflowRequestModel,
    build_command_result_model,
    build_detail_model,
    build_event_aggregate_model,
    build_event_summary_model,
    build_health_response_model,
    build_history_record_model,
    build_news_item_model,
)
from forexcalendar_scraper.application import (
    CalendarScraperService,
    DetailExtractionService,
    EventCatalogService,
    HistoryExtractionService,
    HistoryNewsExtractionService,
    NewsExtractionService,
)
from forexcalendar_scraper.bootstrap import (
    build_calendar_scraper_service,
    build_detail_extraction_service,
    build_event_catalog_service,
    build_history_extraction_service,
    build_history_news_extraction_service,
    build_news_extraction_service,
)
from forexcalendar_scraper.core.config import Settings, get_settings
from forexcalendar_scraper.core.exceptions import (
    EventNotFoundError,
    ForexCalendarError,
    StorageUnavailableError,
)


def create_app(
    settings: Settings | None = None,
    event_catalog_service: EventCatalogService | None = None,
    scraper_service: CalendarScraperService | None = None,
    detail_extraction_service: DetailExtractionService | None = None,
    history_extraction_service: HistoryExtractionService | None = None,
    news_extraction_service: NewsExtractionService | None = None,
    history_news_extraction_service: HistoryNewsExtractionService | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    catalog_service = event_catalog_service or build_event_catalog_service(resolved_settings)
    scrape_service = scraper_service or build_calendar_scraper_service(resolved_settings)
    details_service = detail_extraction_service or build_detail_extraction_service(
        resolved_settings
    )
    history_service = history_extraction_service or build_history_extraction_service(
        resolved_settings
    )
    news_service = news_extraction_service or build_news_extraction_service(resolved_settings)
    history_news_service = history_news_extraction_service or build_history_news_extraction_service(
        resolved_settings
    )

    app = FastAPI(
        title="ForexCalendar Scraper API",
        description=(
            "FastAPI surface for scraping ForexFactory calendar data and "
            "reading the PostgreSQL-backed event store."
        ),
        version="0.1.0",
    )

    @app.get("/health", response_model=HealthResponseModel)
    def health() -> HealthResponseModel:
        return build_health_response_model(
            postgres_enabled=(
                resolved_settings.postgres_enabled
                and bool(resolved_settings.postgres_dsn)
            ),
            postgres_configured=bool(resolved_settings.postgres_dsn),
        )

    @app.get("/events", response_model=list[EventSummaryModel])
    def list_events(
        date_param: str | None = None,
        currency: str | None = None,
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[EventSummaryModel]:
        try:
            events = catalog_service.list_events(
                date_param=date_param,
                currency=currency,
                limit=limit,
                offset=offset,
            )
        except ForexCalendarError as error:
            raise _to_http_exception(error) from error
        return [build_event_summary_model(event) for event in events]

    @app.get("/events/{event_id}", response_model=EventAggregateModel)
    def get_event(event_id: int) -> EventAggregateModel:
        try:
            aggregate = catalog_service.get_event(event_id)
        except ForexCalendarError as error:
            raise _to_http_exception(error) from error
        return build_event_aggregate_model(aggregate)

    @app.get("/events/{event_id}/details", response_model=DetailModel)
    def get_event_details(event_id: int) -> DetailModel:
        try:
            detail = catalog_service.get_event_details(event_id)
        except ForexCalendarError as error:
            raise _to_http_exception(error) from error
        if detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stored event {event_id} does not have details.",
            )
        return build_detail_model(detail)

    @app.get("/events/{event_id}/history", response_model=list[HistoryRecordModel])
    def get_event_history(event_id: int) -> list[HistoryRecordModel]:
        try:
            history = catalog_service.list_event_history(event_id)
        except ForexCalendarError as error:
            raise _to_http_exception(error) from error
        return [build_history_record_model(record) for record in history]

    @app.get("/events/{event_id}/news", response_model=list[NewsItemModel])
    def get_event_news(event_id: int) -> list[NewsItemModel]:
        try:
            news = catalog_service.list_event_news(event_id)
        except ForexCalendarError as error:
            raise _to_http_exception(error) from error
        return [build_news_item_model(item) for item in news]

    @app.post("/workflows/scrape", response_model=CommandResultModel)
    def run_scrape_workflow(request: ScrapeWorkflowRequestModel) -> CommandResultModel:
        return _run_workflow(lambda: scrape_service.run(date_param=request.date_param))

    @app.post("/workflows/details", response_model=CommandResultModel)
    def run_details_workflow(request: ExtractWorkflowRequestModel) -> CommandResultModel:
        return _run_workflow(
            lambda: details_service.run(
                csv_file=request.csv_file,
                date_param=request.date_param,
            )
        )

    @app.post("/workflows/history", response_model=CommandResultModel)
    def run_history_workflow(request: ExtractWorkflowRequestModel) -> CommandResultModel:
        return _run_workflow(
            lambda: history_service.run(
                csv_file=request.csv_file,
                date_param=request.date_param,
            )
        )

    @app.post("/workflows/news", response_model=CommandResultModel)
    def run_news_workflow(request: ExtractWorkflowRequestModel) -> CommandResultModel:
        return _run_workflow(
            lambda: news_service.run(
                csv_file=request.csv_file,
                date_param=request.date_param,
            )
        )

    @app.post("/workflows/history-news", response_model=CommandResultModel)
    def run_history_news_workflow(request: ExtractWorkflowRequestModel) -> CommandResultModel:
        return _run_workflow(
            lambda: history_news_service.run(
                csv_file=request.csv_file,
                date_param=request.date_param,
            )
        )

    def _run_workflow(executor: Any) -> CommandResultModel:
        try:
            result = executor()
        except ForexCalendarError as error:
            raise _to_http_exception(error) from error
        return build_command_result_model(result)

    return app


def _to_http_exception(error: ForexCalendarError) -> HTTPException:
    if isinstance(error, EventNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, StorageUnavailableError):
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


app = create_app()