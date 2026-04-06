import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import extractor_common


class ExtractorCommonTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = Path(self.temp_dir.name)
        self.output_root = self.root_dir / "outputs"
        self.log_root = self.output_root / "logs"

        self.patches = [
            patch.object(extractor_common, "ROOT_DIR", self.root_dir),
            patch.object(extractor_common, "OUTPUT_ROOT", self.output_root),
            patch.object(extractor_common, "LOG_ROOT", self.log_root),
        ]

        for active_patch in self.patches:
            active_patch.start()

        self.addCleanup(self._cleanup_patches)
        self.addCleanup(self.temp_dir.cleanup)

    def _cleanup_patches(self):
        for active_patch in reversed(self.patches):
            active_patch.stop()

    def test_build_date_folder_name_supports_day_and_week(self):
        self.assertEqual(extractor_common.build_date_folder_name("day=oct6.2025"), "oct-06-2025")
        self.assertEqual(extractor_common.build_date_folder_name("week=oct21.2025"), "oct-21-2025")

    def test_build_date_folder_name_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            extractor_common.build_date_folder_name("oct6.2025")

    def test_build_output_file_path_creates_date_directory(self):
        output_file = extractor_common.build_output_file_path("day=oct6.2025", "_details")

        self.assertEqual(
            output_file,
            self.output_root / "oct-06-2025" / "day=oct6.2025_details.csv",
        )
        self.assertTrue(output_file.parent.exists())

    def test_build_log_file_path_creates_logs_directory(self):
        log_file = extractor_common.build_log_file_path("scraper")

        self.assertEqual(log_file, self.log_root / "scraper.log")
        self.assertTrue(self.log_root.exists())

    def test_display_path_returns_repo_relative_path_when_possible(self):
        docs_file = self.root_dir / "docs" / "guide.md"
        docs_file.parent.mkdir(parents=True)
        docs_file.write_text("guide", encoding="utf-8")

        self.assertEqual(extractor_common.display_path(docs_file), "docs/guide.md")

    def test_resolve_input_file_finds_repo_relative_file(self):
        csv_file = self.root_dir / "custom.csv"
        csv_file.write_text("header\nvalue\n", encoding="utf-8")

        resolved_file = extractor_common.resolve_input_file("custom.csv")

        self.assertEqual(resolved_file, csv_file.resolve())

    def test_resolve_input_file_finds_dated_output_file(self):
        output_file = extractor_common.build_output_file_path("day=oct6.2025")
        output_file.write_text("header\nvalue\n", encoding="utf-8")

        resolved_file = extractor_common.resolve_input_file(
            "day=oct6.2025.csv",
            preferred_date_param="day=oct6.2025",
        )

        self.assertEqual(resolved_file, output_file.resolve())

    def test_resolve_primary_csv_path_prefers_dated_output(self):
        dated_output = extractor_common.build_output_file_path("day=oct6.2025")
        dated_output.write_text("from-output", encoding="utf-8")

        legacy_root_file = self.root_dir / "day=oct6.2025.csv"
        legacy_root_file.write_text("from-root", encoding="utf-8")

        resolved_file = extractor_common.resolve_primary_csv_path(None, "day=oct6.2025")

        self.assertEqual(resolved_file, dated_output.resolve())

    def test_resolve_primary_csv_path_falls_back_to_legacy_root_file(self):
        legacy_root_file = self.root_dir / "day=oct6.2025.csv"
        legacy_root_file.write_text("from-root", encoding="utf-8")

        resolved_file = extractor_common.resolve_primary_csv_path(None, "day=oct6.2025")

        self.assertEqual(resolved_file, legacy_root_file.resolve())

    def test_find_matching_files_returns_root_and_output_matches(self):
        output_match = extractor_common.build_output_file_path("day=oct6.2025", "_details")
        output_match.write_text("output", encoding="utf-8")

        root_match = self.root_dir / "legacy_details.csv"
        root_match.write_text("root", encoding="utf-8")

        matches = extractor_common.find_matching_files("*_details.csv")

        self.assertEqual(set(matches), {output_match.resolve(), root_match.resolve()})

    def test_load_events_strips_header_and_value_whitespace(self):
        csv_file = self.root_dir / "events.csv"
        csv_file.write_text(
            " date , event , detail \n Mon Oct 6 , CPI , 12345 \n",
            encoding="utf-8",
        )

        events = extractor_common.load_events(csv_file)

        self.assertEqual(
            events,
            [{"date": "Mon Oct 6", "event": "CPI", "detail": "12345"}],
        )