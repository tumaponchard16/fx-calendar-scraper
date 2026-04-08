"""Service for scraping the main calendar event list."""

from __future__ import annotations

from dataclasses import dataclass

from forexcalendar_scraper.core.config import Settings
from forexcalendar_scraper.core.constants import DEFAULT_SCRAPER_DATE_PARAM
from forexcalendar_scraper.domain.entities import CommandResult
from forexcalendar_scraper.ports import CalendarGatewayPort, EventRepositoryPort, EventStorePort, LoggerFactory, PathServicePort


@dataclass(slots=True)
class CalendarScraperService:
    settings: Settings
    path_service: PathServicePort
    csv_repository: EventRepositoryPort
    calendar_gateway: CalendarGatewayPort
    logger_factory: LoggerFactory
    event_store: EventStorePort | None = None

    def run(self, date_param: str | None = None) -> CommandResult:
        effective_date_param = date_param or DEFAULT_SCRAPER_DATE_PARAM
        logger = self.logger_factory(
            "scraper",
            self.path_service.build_log_file_path("scraper"),
            self.settings.log_level,
        )
        output_file = self.path_service.build_output_file_path(effective_date_param)
        logger.info("Starting calendar scrape for %s", effective_date_param)
        logger.info("Output file: %s", self.path_service.display_path(output_file))

        events = self.calendar_gateway.scrape_calendar(effective_date_param, logger)

        result = CommandResult(processed_events=len(events))
        if events:
            self.csv_repository.save_events(output_file, events)
            if self.event_store is not None and self.event_store.is_enabled():
                self.event_store.upsert_events(
                    effective_date_param,
                    events,
                    output_file=self.path_service.display_path(output_file),
                )
            result.output_files["events"] = output_file
            result.written_counts["events"] = len(events)
            logger.info(
                "Saved %s events to %s",
                len(events),
                self.path_service.display_path(output_file),
            )
        else:
            logger.warning("No events found to save")

        return result
