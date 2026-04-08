import os
import time

from forexcalendar_scraper.core.paths import PathService
from forexcalendar_scraper.domain.entities import DetailBlock
from forexcalendar_scraper.infrastructure.persistence.csv_repository import CsvRepository
from forexcalendar_scraper.application.detail_query_service import DetailQueryService


def test_detail_query_service_uses_latest_details_file_and_formats_output(tmp_path):
    path_service = PathService.from_root(tmp_path)
    repository = CsvRepository()

    older_file = path_service.build_output_file_path("day=oct6.2025", "_details")
    repository.save_detail_blocks(
        older_file,
        [DetailBlock(detail_id="111", event_name="Older Event", fields={"description": "Older details"})],
    )

    newer_file = path_service.build_output_file_path("day=oct7.2025", "_details")
    repository.save_detail_blocks(
        newer_file,
        [
            DetailBlock(
                detail_id="222",
                event_name="Newer Event",
                fields={"description": "Latest details"},
            )
        ],
    )

    now = time.time()
    os.utime(older_file, (now - 60, now - 60))
    os.utime(newer_file, (now, now))

    service = DetailQueryService(path_service=path_service, csv_repository=repository)

    resolved_file, auto_discovered = service.resolve_details_file(None)
    events = service.load_details(resolved_file)
    output = service.show_specific_field(events, "1", "description")

    assert auto_discovered is True
    assert resolved_file == newer_file.resolve()
    assert "Newer Event" in output
    assert "Latest details" in output