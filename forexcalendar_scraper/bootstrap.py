"""Composition root for wiring concrete adapters to application services."""

from __future__ import annotations

from forexcalendar_scraper.application import (
    CalendarScraperService,
    DetailExtractionService,
    DetailQueryService,
    EventCatalogService,
    HistoryExtractionService,
    HistoryNewsExtractionService,
    NewsExtractionService,
)
from forexcalendar_scraper.core.config import Settings, get_settings
from forexcalendar_scraper.core.exceptions import OptionalDependencyError
from forexcalendar_scraper.core.logging import configure_logger
from forexcalendar_scraper.core.paths import get_default_path_service
from forexcalendar_scraper.infrastructure.persistence.csv_repository import CsvRepository
from forexcalendar_scraper.infrastructure.persistence.null_event_store import NullEventStore
from forexcalendar_scraper.infrastructure.web.browser import BrowserSessionFactory
from forexcalendar_scraper.infrastructure.web.forexfactory_client import ForexFactoryClient
from forexcalendar_scraper.infrastructure.web.forexfactory_gateway import ForexFactoryGateway
from forexcalendar_scraper.ports import (
    CalendarGatewayPort,
    EventRepositoryPort,
    EventStorePort,
    LoggerFactory,
    PathServicePort,
)


def _resolve_settings(settings: Settings | None) -> Settings:
    return settings or get_settings()


def build_calendar_gateway(
    settings: Settings | None = None,
    calendar_gateway: CalendarGatewayPort | None = None,
) -> CalendarGatewayPort:
    if calendar_gateway is not None:
        return calendar_gateway

    resolved_settings = _resolve_settings(settings)
    return ForexFactoryGateway(
        browser_factory=BrowserSessionFactory(resolved_settings),
        client=ForexFactoryClient(resolved_settings),
    )


def build_csv_repository(repository: EventRepositoryPort | None = None) -> EventRepositoryPort:
    return repository or CsvRepository()


def build_path_service(path_service: PathServicePort | None = None) -> PathServicePort:
    return path_service or get_default_path_service()


def build_event_store(
    settings: Settings | None = None,
    event_store: EventStorePort | None = None,
) -> EventStorePort:
    if event_store is not None:
        return event_store

    resolved_settings = _resolve_settings(settings)
    if not resolved_settings.postgres_enabled or not resolved_settings.postgres_dsn:
        return NullEventStore()

    try:
        from forexcalendar_scraper.infrastructure.persistence.postgres_event_store import (
            PostgresEventStore,
        )
    except ModuleNotFoundError as error:
        raise OptionalDependencyError(
            "PostgreSQL support requires optional server dependencies. "
            "Install with `pip install -e '.[server]'`."
        ) from error

    return PostgresEventStore(resolved_settings.postgres_dsn)


def build_logger_factory(logger_factory: LoggerFactory | None = None) -> LoggerFactory:
    return logger_factory or configure_logger


def build_calendar_scraper_service(
    settings: Settings | None = None,
    path_service: PathServicePort | None = None,
    repository: EventRepositoryPort | None = None,
    calendar_gateway: CalendarGatewayPort | None = None,
    logger_factory: LoggerFactory | None = None,
    event_store: EventStorePort | None = None,
) -> CalendarScraperService:
    resolved_settings = _resolve_settings(settings)
    return CalendarScraperService(
        settings=resolved_settings,
        path_service=build_path_service(path_service),
        csv_repository=build_csv_repository(repository),
        calendar_gateway=build_calendar_gateway(resolved_settings, calendar_gateway),
        logger_factory=build_logger_factory(logger_factory),
        event_store=build_event_store(resolved_settings, event_store),
    )


def build_detail_extraction_service(
    settings: Settings | None = None,
    path_service: PathServicePort | None = None,
    repository: EventRepositoryPort | None = None,
    calendar_gateway: CalendarGatewayPort | None = None,
    logger_factory: LoggerFactory | None = None,
    event_store: EventStorePort | None = None,
) -> DetailExtractionService:
    resolved_settings = _resolve_settings(settings)
    return DetailExtractionService(
        settings=resolved_settings,
        path_service=build_path_service(path_service),
        csv_repository=build_csv_repository(repository),
        calendar_gateway=build_calendar_gateway(resolved_settings, calendar_gateway),
        logger_factory=build_logger_factory(logger_factory),
        event_store=build_event_store(resolved_settings, event_store),
    )


def build_history_extraction_service(
    settings: Settings | None = None,
    path_service: PathServicePort | None = None,
    repository: EventRepositoryPort | None = None,
    calendar_gateway: CalendarGatewayPort | None = None,
    logger_factory: LoggerFactory | None = None,
    event_store: EventStorePort | None = None,
) -> HistoryExtractionService:
    resolved_settings = _resolve_settings(settings)
    return HistoryExtractionService(
        settings=resolved_settings,
        path_service=build_path_service(path_service),
        csv_repository=build_csv_repository(repository),
        calendar_gateway=build_calendar_gateway(resolved_settings, calendar_gateway),
        logger_factory=build_logger_factory(logger_factory),
        event_store=build_event_store(resolved_settings, event_store),
    )


def build_news_extraction_service(
    settings: Settings | None = None,
    path_service: PathServicePort | None = None,
    repository: EventRepositoryPort | None = None,
    calendar_gateway: CalendarGatewayPort | None = None,
    logger_factory: LoggerFactory | None = None,
    event_store: EventStorePort | None = None,
) -> NewsExtractionService:
    resolved_settings = _resolve_settings(settings)
    return NewsExtractionService(
        settings=resolved_settings,
        path_service=build_path_service(path_service),
        csv_repository=build_csv_repository(repository),
        calendar_gateway=build_calendar_gateway(resolved_settings, calendar_gateway),
        logger_factory=build_logger_factory(logger_factory),
        event_store=build_event_store(resolved_settings, event_store),
    )


def build_history_news_extraction_service(
    settings: Settings | None = None,
    path_service: PathServicePort | None = None,
    repository: EventRepositoryPort | None = None,
    calendar_gateway: CalendarGatewayPort | None = None,
    logger_factory: LoggerFactory | None = None,
    event_store: EventStorePort | None = None,
) -> HistoryNewsExtractionService:
    resolved_settings = _resolve_settings(settings)
    return HistoryNewsExtractionService(
        settings=resolved_settings,
        path_service=build_path_service(path_service),
        csv_repository=build_csv_repository(repository),
        calendar_gateway=build_calendar_gateway(resolved_settings, calendar_gateway),
        logger_factory=build_logger_factory(logger_factory),
        event_store=build_event_store(resolved_settings, event_store),
    )


def build_detail_query_service(
    path_service: PathServicePort | None = None,
    repository: EventRepositoryPort | None = None,
) -> DetailQueryService:
    return DetailQueryService(
        path_service=build_path_service(path_service),
        csv_repository=build_csv_repository(repository),
    )


def build_event_catalog_service(
    settings: Settings | None = None,
    event_store: EventStorePort | None = None,
) -> EventCatalogService:
    resolved_settings = _resolve_settings(settings)
    return EventCatalogService(event_store=build_event_store(resolved_settings, event_store))