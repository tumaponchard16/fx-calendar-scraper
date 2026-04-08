import tempfile
import unittest
from pathlib import Path

from forexcalendar_scraper.application.detail_query_service import DetailQueryService
from forexcalendar_scraper.core.exceptions import InputFileResolutionError
from forexcalendar_scraper.core.paths import PathService
from forexcalendar_scraper.infrastructure.persistence.csv_repository import CsvRepository


class DetailQueryServiceTests(unittest.TestCase):
    @staticmethod
    def _build_service(root_dir: Path) -> DetailQueryService:
        return DetailQueryService(
            path_service=PathService.from_root(root_dir),
            csv_repository=CsvRepository(),
        )

    def test_load_details_parses_vertical_block_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir)
            details_file = root_dir / "details.csv"
            details_file.write_text(
                "event_id,1\n"
                "detail_id,148482\n"
                "event_name,FOMC Member Musalem Speaks\n"
                "description,Moderated discussion\n"
                "---,---\n"
                "event_id,2\n"
                "detail_id,148483\n"
                "event_name,MPC Member Breeden Speaks\n",
                encoding="utf-8",
            )

            events = self._build_service(root_dir).load_details(details_file)

        self.assertEqual(events["1"]["detail_id"], "148482")
        self.assertEqual(events["1"]["description"], "Moderated discussion")
        self.assertEqual(events["2"]["event_name"], "MPC Member Breeden Speaks")

    def test_resolve_details_file_raises_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = self._build_service(Path(temp_dir))

            with self.assertRaises(InputFileResolutionError) as raised_error:
                service.resolve_details_file("missing-details.csv")

        self.assertIn("missing-details.csv", str(raised_error.exception))

    def test_list_all_events_sorts_event_ids_numerically(self):
        events = {
            "10": {"event_name": "Tenth", "event_date": "Wed Oct 22", "event_time": "1:00pm"},
            "2": {"event_name": "Second", "event_date": "Tue Oct 21", "event_time": "9:00am"},
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            output = self._build_service(Path(temp_dir)).list_all_events(events)

        self.assertLess(output.index("Event 2"), output.index("Event 10"))

    def test_show_specific_field_returns_requested_value(self):
        events = {
            "2": {
                "event_name": "MPC Member Breeden Speaks",
                "speaker": "Sarah Breeden",
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            output = self._build_service(Path(temp_dir)).show_specific_field(events, "2", "speaker")

        self.assertIn("MPC Member Breeden Speaks", output)
        self.assertIn("Sarah Breeden", output)