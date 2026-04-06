import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import query_details


class QueryDetailsTests(unittest.TestCase):
    def test_load_details_parses_vertical_block_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            details_file = Path(temp_dir) / "details.csv"
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

            events = query_details.load_details(details_file)

        self.assertEqual(events["1"]["detail_id"], "148482")
        self.assertEqual(events["1"]["description"], "Moderated discussion")
        self.assertEqual(events["2"]["event_name"], "MPC Member Breeden Speaks")

    def test_load_details_exits_when_file_is_missing(self):
        stdout_buffer = io.StringIO()

        with self.assertRaises(SystemExit) as raised_error:
            with redirect_stdout(stdout_buffer):
                query_details.load_details("missing-details.csv")

        self.assertEqual(raised_error.exception.code, 1)
        self.assertIn("missing-details.csv", stdout_buffer.getvalue())

    def test_list_all_events_sorts_event_ids_numerically(self):
        events = {
            "10": {"event_name": "Tenth", "event_date": "Wed Oct 22", "event_time": "1:00pm"},
            "2": {"event_name": "Second", "event_date": "Tue Oct 21", "event_time": "9:00am"},
        }
        stdout_buffer = io.StringIO()

        with redirect_stdout(stdout_buffer):
            query_details.list_all_events(events)

        output = stdout_buffer.getvalue()
        self.assertLess(output.index("Event 2"), output.index("Event 10"))

    def test_show_specific_field_prints_requested_value(self):
        events = {
            "2": {
                "event_name": "MPC Member Breeden Speaks",
                "speaker": "Sarah Breeden",
            }
        }
        stdout_buffer = io.StringIO()

        with redirect_stdout(stdout_buffer):
            query_details.show_specific_field(events, "2", "speaker")

        output = stdout_buffer.getvalue()
        self.assertIn("MPC Member Breeden Speaks", output)
        self.assertIn("Sarah Breeden", output)