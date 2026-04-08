"""CLI controllers for the project entrypoints."""

from forexcalendar_scraper.cli.main import (
    main,
    run_api_cli,
    run_detail_extractor_cli,
    run_history_extractor_cli,
    run_history_news_extractor_cli,
    run_news_extractor_cli,
    run_query_details_cli,
    run_scraper_cli,
)

__all__ = [
    "main",
    "run_api_cli",
    "run_detail_extractor_cli",
    "run_history_extractor_cli",
    "run_history_news_extractor_cli",
    "run_news_extractor_cli",
    "run_query_details_cli",
    "run_scraper_cli",
]