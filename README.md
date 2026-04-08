# ForexFactory Calendar Scraper

Playwright-based workflows for scraping ForexFactory calendar events and generating dated CSV outputs for event details, history, and related news.

## Legal And Usage Notice

This repository is not affiliated with, endorsed by, or sponsored by Forex Factory or Fair Economy, Inc.

Before using this project, review Forex Factory's current notices and terms:

- Terms and notices: https://www.forexfactory.com/notices#tos
- Privacy policy and notices: https://www.forexfactory.com/notices

Forex Factory states that copying, republication, or redistribution of FEED calendar content may be restricted. You are responsible for reviewing the current terms, obtaining permission where needed, and ensuring your usage complies with applicable law and website restrictions.

## Architecture Snapshot

The codebase follows a pragmatic clean and hexagonal architecture under `forexcalendar_scraper/`. The repository root is intentionally kept small and now focuses on project metadata, docs, tests, samples, and generated outputs.

```text
forexcalendar_scraper/
├── api/                        FastAPI driver adapter and response models
├── cli/                        Driver adapters and unified CLI entrypoints
├── application/                Application use cases
├── domain/                     Domain dataclasses
├── infrastructure/
│   ├── persistence/            Outbound persistence adapters
│   └── web/                    Outbound web adapters and gateway implementations
├── core/                       Settings, constants, logging, paths, exceptions
├── ports/                      Application-facing contracts for adapters
├── utils/                      Shared formatting helpers
├── bootstrap.py                Composition root for wiring adapters to use cases
├── __main__.py                 `python -m forexcalendar_scraper` entrypoint
└── main.py                     Unified entrypoint module
```

The supported entrypoints are the package module and the console scripts defined in [pyproject.toml](pyproject.toml).

## Setup

### Runtime Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python3 -m playwright install chromium
```

### Development Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python3 -m playwright install chromium
```

### API And PostgreSQL Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[server,dev]"
python3 -m playwright install chromium
```

Dependencies are declared in `pyproject.toml`, and the project intentionally uses that file as the single packaging source of truth.

### Environment Configuration

Optional runtime settings live in [forexcalendar_scraper/core/config.py](forexcalendar_scraper/core/config.py). Start from `.env.example`:

```bash
cp .env.example .env
```

The application will read `.env` automatically if it exists.

To enable the API-backed database store, set `FOREXFACTORY_POSTGRES_ENABLED=true` and provide `FOREXFACTORY_POSTGRES_DSN`.

## Common Workflows

### Base Calendar Scrape

```bash
python3 -m forexcalendar_scraper scrape --date-param day=oct22.2025
forexcalendar-scrape --date-param day=oct22.2025
```

### Detail Extraction

```bash
python3 -m forexcalendar_scraper details --date-param day=oct22.2025
forexcalendar-detail-extract --date-param day=oct22.2025
```

### History And News Extraction

```bash
python3 -m forexcalendar_scraper history --date-param day=oct22.2025
python3 -m forexcalendar_scraper news --date-param day=oct22.2025
python3 -m forexcalendar_scraper history-news --date-param day=oct22.2025
```

Console script equivalents:

```bash
forexcalendar-history-extract --date-param day=oct22.2025
forexcalendar-news-extract --date-param day=oct22.2025
forexcalendar-history-news-extract --date-param day=oct22.2025
```

### Query Details

```bash
python3 -m forexcalendar_scraper query-details --list-fields
python3 -m forexcalendar_scraper query-details --event 1
forexcalendar-query-details --event 1 --field description
```

### FastAPI Server

```bash
forexcalendar-api
forexcalendar-api --host 0.0.0.0 --port 8080
python3 -m forexcalendar_scraper serve-api --reload
```

The FastAPI app exposes OpenAPI at `/openapi.json`, Swagger UI at `/docs`, and Redoc at `/redoc`.

## Output Layout

Generated CSV files are grouped by date parameter under `outputs/<mon-dd-yyyy>/`.

```text
outputs/
├── oct-22-2025/
│   ├── day=oct22.2025.csv
│   ├── day=oct22.2025_details.csv
│   ├── day=oct22.2025_history.csv
│   └── day=oct22.2025_news.csv
└── logs/
    ├── scraper.log
    ├── detail_extractor.log
    ├── history_extractor.log
    ├── history_news_extractor.log
    └── news_extractor.log
```

The base `day=...csv` file must exist before detail, history, or news extraction can run.

When PostgreSQL is enabled, the same workflows continue writing CSV outputs and also upsert related data into `calendar_events`, `event_details`, `event_history_records`, and `event_news_items`.

## Testing And Quality

Preferred test command:

```bash
python3 -m pytest
```

Legacy unittest suite is still supported:

```bash
python3 -m unittest discover -s tests
```

Quality checks:

```bash
ruff check .
black --check .
isort --check-only .
```

## Documentation

- [docs/README.md](docs/README.md) for the documentation index
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for folder responsibilities and data flow
- [docs/ai-guidelines.md](docs/ai-guidelines.md) for AI-assisted coding conventions
- [docs/extractors/history-news-quick-start.md](docs/extractors/history-news-quick-start.md) for extractor quick start guides

## Current Design Decisions

- `forexcalendar_scraper/application/` is the application layer and depends on ports instead of concrete Playwright or CSV implementations.
- `forexcalendar_scraper/ports/` defines the inbound expectations that outbound adapters must satisfy.
- `forexcalendar_scraper/bootstrap.py` is the composition root that wires concrete adapters into use cases.
- `forexcalendar_scraper/infrastructure/web/forexfactory_gateway.py` hides browser lifecycle and Playwright details behind a single gateway port.
- `forexcalendar_scraper/api/` adds a FastAPI driver adapter for Swagger/OpenAPI access to workflows and stored events.
- `forexcalendar_scraper/infrastructure/persistence/postgres_event_store.py` provides optional PostgreSQL persistence in parallel with CSV outputs.
- CLI entrypoints live in `forexcalendar_scraper/cli/` and `pyproject.toml`, not as root wrapper scripts.
- Details are stored in a vertical block CSV format to support variable field sets per event.
- Configuration is centralized in `forexcalendar_scraper/core/config.py` and can be overridden with environment variables.