"""Shared constants used across the application."""

from typing import Final


DEFAULT_SCRAPER_DATE_PARAM: Final[str] = "day=oct2.2025"
DEFAULT_EXTRACTOR_DATE_PARAM: Final[str] = "day=oct6.2025"
DETAILS_FILE_GLOB: Final[str] = "*_details.csv"
DATE_PARAM_PATTERN_TEXT: Final[str] = r"^(day|week)=([a-z]{3})(\d{1,2})\.(\d{4})$"

DEFAULT_USER_AGENT: Final[str] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
BROWSER_ARGS: Final[tuple[str, ...]] = (
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage",
)
VIEWPORT_WIDTH: Final[int] = 1920
VIEWPORT_HEIGHT: Final[int] = 1080

CALENDAR_TABLE_SELECTOR: Final[str] = "table.calendar__table tbody"
CALENDAR_ROW_SELECTOR: Final[str] = "table.calendar__table tbody tr"

DETAIL_OVERLAY_SELECTORS: Final[tuple[str, ...]] = (
    ".overlay__content",
    ".calendar__detail",
)
DETAIL_CONTAINER_SELECTORS: Final[tuple[str, ...]] = (
    "[data-event-id='{detail_id}']",
    ".calendar__detail",
    ".calendar-detail",
    "#detail",
    "[id*='detail']",
)
DETAIL_SPECS_TABLE_SELECTORS: Final[tuple[str, ...]] = (
    "table.calendarspecs",
    ".calendarspecs",
    "table.calendar-specs",
    ".calendar-specs",
    "[class*='specs']",
    ".calendar__detail table",
    ".calendar-detail table",
)
DETAIL_HISTORY_TABLE_SELECTORS: Final[tuple[str, ...]] = (
    ".half.last.details table",
    ".overlay__content .half.last table",
    "[class*='history'] table",
    ".calendar__history table",
)
DETAIL_NEWS_CONTAINER_SELECTORS: Final[tuple[str, ...]] = (
    ".half.last.details .ff_taglist",
    ".overlay__content .half.last .ff_taglist",
    "[class*='news']",
    ".calendar__news",
)
