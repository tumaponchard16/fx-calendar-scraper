"""Pydantic models for the FastAPI application."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from forexcalendar_scraper.domain.entities import (
    CommandResult,
    DetailBlock,
    HistoryRecord,
    NewsItem,
    StoredCalendarEvent,
    StoredEventAggregate,
)


class HealthResponseModel(BaseModel):
    status: str = "ok"
    postgres_enabled: bool
    postgres_configured: bool


class CommandResultModel(BaseModel):
    processed_events: int
    failed_events: int
    skipped_events: int
    written_counts: dict[str, int]
    output_files: dict[str, str]


class EventSummaryModel(BaseModel):
    id: int
    source_event_key: str
    date_param: str
    date: str = ""
    time: str = ""
    currency: str = ""
    impact: str = ""
    name: str = ""
    actual: str = ""
    forecast: str = ""
    previous: str = ""
    detail_id: str = ""
    output_file: str = ""
    created_at: str = ""
    updated_at: str = ""


class DetailModel(BaseModel):
    detail_id: str
    event_date: str = ""
    event_time: str = ""
    event_currency: str = ""
    event_name: str = ""
    fields: dict[str, str] = Field(default_factory=dict)


class HistoryRecordModel(BaseModel):
    detail_id: str
    date: str
    date_url: str = ""
    actual: str = ""
    forecast: str = ""
    previous: str = ""
    event_name: str = ""
    event_date: str = ""
    event_currency: str = ""


class NewsItemModel(BaseModel):
    detail_id: str
    title: str
    url: str
    snippet: str = ""
    link_type: str = "related"
    event_name: str = ""
    event_date: str = ""
    event_currency: str = ""


class EventAggregateModel(BaseModel):
    event: EventSummaryModel
    details: DetailModel | None = None
    history: list[HistoryRecordModel] = Field(default_factory=list)
    news: list[NewsItemModel] = Field(default_factory=list)


class ScrapeWorkflowRequestModel(BaseModel):
    date_param: str = "day=today"


class ExtractWorkflowRequestModel(BaseModel):
    date_param: str = "day=today"
    csv_file: str | None = None


def build_health_response_model(
    postgres_enabled: bool,
    postgres_configured: bool,
) -> HealthResponseModel:
    return HealthResponseModel(
        postgres_enabled=postgres_enabled,
        postgres_configured=postgres_configured,
    )


def build_command_result_model(result: CommandResult) -> CommandResultModel:
    return CommandResultModel(
        processed_events=result.processed_events,
        failed_events=result.failed_events,
        skipped_events=result.skipped_events,
        written_counts=dict(result.written_counts),
        output_files={key: _stringify_path(path) for key, path in result.output_files.items()},
    )


def build_event_summary_model(event: StoredCalendarEvent) -> EventSummaryModel:
    return EventSummaryModel(
        id=event.id,
        source_event_key=event.source_event_key,
        date_param=event.date_param,
        date=event.date,
        time=event.time,
        currency=event.currency,
        impact=event.impact,
        name=event.name,
        actual=event.actual,
        forecast=event.forecast,
        previous=event.previous,
        detail_id=event.detail_id,
        output_file=event.output_file,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


def build_detail_model(detail: DetailBlock) -> DetailModel:
    return DetailModel(
        detail_id=detail.detail_id,
        event_date=detail.event_date,
        event_time=detail.event_time,
        event_currency=detail.event_currency,
        event_name=detail.event_name,
        fields=dict(detail.fields),
    )


def build_history_record_model(record: HistoryRecord) -> HistoryRecordModel:
    return HistoryRecordModel(
        detail_id=record.detail_id,
        date=record.date,
        date_url=record.date_url,
        actual=record.actual,
        forecast=record.forecast,
        previous=record.previous,
        event_name=record.event_name,
        event_date=record.event_date,
        event_currency=record.event_currency,
    )


def build_news_item_model(item: NewsItem) -> NewsItemModel:
    return NewsItemModel(
        detail_id=item.detail_id,
        title=item.title,
        url=item.url,
        snippet=item.snippet,
        link_type=item.link_type,
        event_name=item.event_name,
        event_date=item.event_date,
        event_currency=item.event_currency,
    )


def build_event_aggregate_model(aggregate: StoredEventAggregate) -> EventAggregateModel:
    return EventAggregateModel(
        event=build_event_summary_model(aggregate.event),
        details=build_detail_model(aggregate.details) if aggregate.details else None,
        history=[build_history_record_model(record) for record in aggregate.history],
        news=[build_news_item_model(item) for item in aggregate.news],
    )


def _stringify_path(path: Path) -> str:
    return str(path)