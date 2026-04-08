from forexcalendar_scraper.core.paths import PathService


def test_resolve_primary_csv_path_prefers_dated_output(tmp_path):
    path_service = PathService.from_root(tmp_path)
    output_file = path_service.build_output_file_path("day=oct6.2025")
    output_file.write_text("from-output", encoding="utf-8")

    legacy_file = tmp_path / "day=oct6.2025.csv"
    legacy_file.write_text("from-root", encoding="utf-8")

    assert path_service.resolve_primary_csv_path(None, "day=oct6.2025") == output_file.resolve()


def test_resolve_input_file_finds_matching_output_file(tmp_path):
    path_service = PathService.from_root(tmp_path)
    output_file = path_service.build_output_file_path("day=oct6.2025", "_details")
    output_file.write_text("details", encoding="utf-8")

    resolved = path_service.resolve_input_file(
        "day=oct6.2025_details.csv",
        preferred_date_param="day=oct6.2025",
    )

    assert resolved == output_file.resolve()