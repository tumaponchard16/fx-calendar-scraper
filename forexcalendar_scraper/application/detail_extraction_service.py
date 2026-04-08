"""Service for extracting detail blocks for events."""

from __future__ import annotations

from dataclasses import dataclass

from forexcalendar_scraper.core.config import Settings
from forexcalendar_scraper.core.constants import DEFAULT_EXTRACTOR_DATE_PARAM
from forexcalendar_scraper.domain.entities import CommandResult, DetailBlock
from forexcalendar_scraper.ports import CalendarGatewayPort, EventRepositoryPort, LoggerFactory, PathServicePort
from forexcalendar_scraper.application.event_processing import EventBatchProcessor
from forexcalendar_scraper.application.runtime import resolve_required_input_csv


@dataclass(slots=True)
class DetailExtractionService:
    settings: Settings
    path_service: PathServicePort
    csv_repository: EventRepositoryPort
    calendar_gateway: CalendarGatewayPort
    logger_factory: LoggerFactory

    def run(
        self,
        csv_file: str | None = None,
        date_param: str = DEFAULT_EXTRACTOR_DATE_PARAM,
    ) -> CommandResult:
        logger = self.logger_factory(
            "detail_extractor",
            self.path_service.build_log_file_path("detail_extractor"),
            self.settings.log_level,
        )
        resolved_csv_file = resolve_required_input_csv(self.path_service, csv_file, date_param)
        logger.info(
            "Starting detail extraction from %s",
            self.path_service.display_path(resolved_csv_file),
        )
        events = self.csv_repository.load_events(resolved_csv_file)
        logger.info("Found %s events to process", len(events))

        processor = EventBatchProcessor[DetailBlock](self.settings, logger)
        results, summary = processor.process(
            events,
            lambda event: self.calendar_gateway.extract_detail_block(event, date_param, logger),
            "Processed %s event details so far",
        )

        detail_blocks = [block for _, block in results]
        result = CommandResult(
            processed_events=summary.processed_events,
            failed_events=summary.failed_events,
            skipped_events=summary.skipped_events,
        )
        if detail_blocks:
            output_file = self.path_service.build_output_file_path(date_param, "_details")
            self.csv_repository.save_detail_blocks(output_file, detail_blocks)
            result.output_files["details"] = output_file
            result.written_counts["details"] = len(detail_blocks)
            logger.info(
                "Saved %s detail blocks to %s",
                len(detail_blocks),
                self.path_service.display_path(output_file),
            )
        else:
            logger.warning("No event details found to save")

        return result
