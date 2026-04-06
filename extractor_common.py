#!/usr/bin/env python3
"""
Shared helpers for ForexFactory extractor scripts.
"""

from pathlib import Path
import csv
import logging
import re

from playwright.sync_api import sync_playwright


ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT_DIR / "outputs"
LOG_ROOT = OUTPUT_ROOT / "logs"
DATE_PARAM_PATTERN = re.compile(r"^(day|week)=([a-z]{3})(\d{1,2})\.(\d{4})$", re.IGNORECASE)
BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
VIEWPORT = {"width": 1920, "height": 1080}


def build_date_folder_name(date_param):
    """Convert a ForexFactory date param into a stable folder name."""
    match = DATE_PARAM_PATTERN.fullmatch(date_param.strip())
    if not match:
        raise ValueError(
            "Unsupported date parameter format. Use values like 'day=oct18.2025' or 'week=oct21.2025'."
        )

    _, month, day, year = match.groups()
    return f"{month.lower()}-{int(day):02d}-{year}"


def get_output_directory(date_param, create=True):
    """Return the dated output directory for a given ForexFactory date param."""
    output_directory = OUTPUT_ROOT / build_date_folder_name(date_param)
    if create:
        output_directory.mkdir(parents=True, exist_ok=True)
    return output_directory


def build_output_file_path(date_param, suffix="", create_dir=True):
    """Build the full output path for a generated CSV file."""
    return get_output_directory(date_param, create=create_dir) / f"{date_param}{suffix}.csv"


def build_log_file_path(script_name):
    """Build the shared log path for a script."""
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    return LOG_ROOT / f"{script_name}.log"


def display_path(path):
    """Render a path relative to the repository when possible."""
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def resolve_input_file(file_name, preferred_date_param=None):
    """Resolve a user-provided file path from the repo root or the outputs folder."""
    if not file_name:
        return None

    raw_path = Path(file_name)
    candidates = []

    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.append(ROOT_DIR / raw_path)
        if preferred_date_param:
            candidates.append(get_output_directory(preferred_date_param, create=False) / raw_path.name)
        if OUTPUT_ROOT.exists():
            candidates.extend(OUTPUT_ROOT.rglob(raw_path.name))

    seen = set()
    for candidate in candidates:
        candidate_key = str(candidate)
        if candidate_key in seen:
            continue
        seen.add(candidate_key)
        if candidate.exists():
            return candidate.resolve()

    return None


def resolve_primary_csv_path(csv_file, date_param):
    """Resolve the main event CSV for a given date parameter."""
    if csv_file:
        resolved_path = resolve_input_file(csv_file, preferred_date_param=date_param)
        if resolved_path:
            return resolved_path

    default_candidates = [
        build_output_file_path(date_param, create_dir=False),
        ROOT_DIR / f"{date_param}.csv",
        ROOT_DIR / "forexfactory_calendar.csv",
    ]

    for candidate in default_candidates:
        if candidate.exists():
            return candidate.resolve()

    return None


def find_matching_files(pattern):
    """Find generated files in the outputs folder, with repo-root fallback for legacy files."""
    matches = []

    if OUTPUT_ROOT.exists():
        matches.extend(sorted(OUTPUT_ROOT.rglob(pattern)))

    matches.extend(sorted(ROOT_DIR.glob(pattern)))

    unique_matches = []
    seen = set()
    for match in matches:
        resolved_match = match.resolve()
        if str(resolved_match) in seen:
            continue
        seen.add(str(resolved_match))
        unique_matches.append(resolved_match)

    return unique_matches


def load_events(csv_file):
    """Load event rows from a CSV file with whitespace cleanup."""
    events = []

    with open(csv_file, "r", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        if reader.fieldnames:
            reader.fieldnames = [field.strip() if field else field for field in reader.fieldnames]

        for row in reader:
            cleaned_row = {}
            for key, value in row.items():
                cleaned_key = key.strip() if key else key
                cleaned_value = value.strip() if isinstance(value, str) else value
                cleaned_row[cleaned_key] = cleaned_value
            events.append(cleaned_row)

    return events


def configure_logger(logger_name, log_file, level=logging.DEBUG):
    """Create a logger with both file and console handlers."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger


def setup_browser(logger, purpose):
    """Setup Playwright browser with shared options."""
    logger.info(f"Initializing Playwright browser for {purpose}...")

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = browser.new_context(viewport=VIEWPORT, user_agent=USER_AGENT)
        page = context.new_page()

        logger.info("✅ Playwright browser initialized successfully")
        return playwright, browser, context, page

    except Exception as error:
        logger.error(f"❌ Failed to initialize Playwright browser: {error}")
        logger.error("Make sure you have installed the browser with: python3 -m playwright install chromium")
        raise Exception(f"Failed to initialize Playwright browser: {error}")
