"""Service for extracting event history."""

from __future__ import annotations

from dataclasses import dataclass

from forexcalendar_scraper.core.config import Settings
from forexcalendar_scraper.core.constants import DEFAULT_EXTRACTOR_DATE_PARAM
from forexcalendar_scraper.domain.entities import CommandResult, HistoryRecord
from forexcalendar_scraper.ports import CalendarGatewayPort, EventRepositoryPort, LoggerFactory, PathServicePort
from forexcalendar_scraper.application.event_processing import EventBatchProcessor
from forexcalendar_scraper.application.runtime import resolve_required_input_csv


@dataclass(slots=True)
class HistoryExtractionService:
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
            "history_extractor",
            self.path_service.build_log_file_path("history_extractor"),
            self.settings.log_level,
        )
        resolved_csv_file = resolve_required_input_csv(self.path_service, csv_file, date_param)
        logger.info(
            "Starting history extraction from %s",
            self.path_service.display_path(resolved_csv_file),
        )
        events = self.csv_repository.load_events(resolved_csv_file)
        logger.info("Found %s events to process", len(events))

        processor = EventBatchProcessor[list[HistoryRecord]](self.settings, logger)
        results, summary = processor.process(
            events,
            lambda event: self.calendar_gateway.extract_history_records(event, date_param, logger),
            "Processed %s history events so far",
        )

        history_records = [
            history_record
            for _, records in results
            for history_record in records
        ]
        result = CommandResult(
            processed_events=summary.processed_events,
            failed_events=summary.failed_events,
            skipped_events=summary.skipped_events,
        )
        if history_records:
            output_file = self.path_service.build_output_file_path(date_param, "_history")
            self.csv_repository.save_history_records(output_file, history_records)
            result.output_files["history"] = output_file
            result.written_counts["history"] = len(history_records)
            logger.info(
                "Saved %s history records to %s",
                len(history_records),
                self.path_service.display_path(output_file),
            )
        else:
            logger.warning("No history data found to save")

        return result
