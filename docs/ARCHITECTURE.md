# Architecture

## Overview

The project now uses a pragmatic clean and hexagonal architecture. The application layer owns use-case orchestration, the ports define what it needs from the outside world, and the adapters implement those ports.

```text
driver adapters         application                 outbound adapters

console scripts     ->  forexcalendar_scraper/cli        ->  forexcalendar_scraper/bootstrap.py
python -m forexcalendar_scraper  forexcalendar_scraper/application  wires implementations

                                                                     |
                                                                     v
                                                           forexcalendar_scraper/ports
                                                                     |
                                       +-----------------------------+-----------------------------+
                                       |                                                           |
                                       v                                                           v
                 forexcalendar_scraper/infrastructure/web      forexcalendar_scraper/infrastructure/persistence
                 ForexFactory gateway + web adapters           CSV repository
```

Dependency direction points inward. The use cases in `forexcalendar_scraper/application/` depend on contracts from `forexcalendar_scraper/ports/`, not on Playwright, concrete CSV classes, or CLI code.

The public command surface is package-first: `python -m forexcalendar_scraper` and the console scripts declared in `pyproject.toml`.

## Layer Responsibilities

### `forexcalendar_scraper/application/` as the application layer

- Owns use-case orchestration for scrape, detail extraction, history extraction, news extraction, and detail querying
- Contains business workflow rules such as batching, output decisions, and result aggregation
- Depends only on domain models, configuration values, and ports

### `forexcalendar_scraper/ports/` as the boundary contracts

- Defines the contracts for path resolution, persistence, logging, and ForexFactory scraping behavior
- Allows tests to inject simple stubs without importing browser or filesystem details
- Keeps the application layer independent from infrastructure choices

### `forexcalendar_scraper/infrastructure/web/` as outbound web adapters

- `browser.py`: Playwright browser lifecycle
- `forexfactory_client.py`: low-level page parsing and selectors
- `forexfactory_gateway.py`: higher-level adapter that hides Playwright from the application layer and satisfies the scraping port

### `forexcalendar_scraper/infrastructure/persistence/` as outbound persistence adapters

- `csv_repository.py`: CSV-backed persistence implementation for events, details, history, and news
- No CLI logic or web scraping logic belongs here

### `forexcalendar_scraper/cli/` as driver adapters

- CLI parsing and user-facing command output
- Converts command-line input into use-case invocations
- Handles exit codes and error display

### `forexcalendar_scraper/core/` as supporting infrastructure

- Environment-backed settings and static constants
- Path calculation and log configuration
- Shared exception types

### `forexcalendar_scraper/bootstrap.py` as the composition root

- Wires concrete adapters to application use cases
- Centralizes service construction
- Keeps infrastructure assembly out of the application layer itself

## Data Flow

### Base Scrape

1. A driver adapter such as `python -m forexcalendar_scraper scrape` or `forexcalendar-scrape` enters `forexcalendar_scraper/cli/main.py`.
2. `forexcalendar_scraper/bootstrap.py` builds the `CalendarScraperService` with a path service, CSV repository, logger factory, and ForexFactory gateway.
3. The use case calls the scraping port.
4. `ForexFactoryGateway` opens a Playwright session and delegates page parsing to `ForexFactoryClient`.
5. The repository adapter writes the dated CSV output.

### Detail, History, And News Extraction

1. The driver adapter resolves CLI inputs.
2. The use case loads base events through the repository port.
3. `EventBatchProcessor` iterates through events and invokes the scraping gateway port.
4. The gateway adapter performs browser work and returns domain data objects.
5. The use case decides which output files to write and saves them through the repository port.

### Detail Querying

1. CLI resolves a details CSV path.
2. `DetailQueryService` uses the path and repository ports to load the vertical block data.
3. The same use case formats the requested projection for CLI display.

## Key Design Decisions

### Explicit Ports

The main architectural change is `forexcalendar_scraper/ports/`. Services no longer import concrete browser or repository implementations directly.

### Gateway Adapter For Scraping

The `ForexFactoryGateway` combines browser lifecycle and page parsing into a single outbound adapter so the application layer no longer deals with Playwright pages.

### Composition Root

`forexcalendar_scraper/bootstrap.py` is responsible for assembling the application with concrete adapters. That keeps object graph construction out of use-case classes and improves testability.

### Package-First Entry Points

The command surface is exposed through `forexcalendar_scraper/cli/`, `python -m forexcalendar_scraper`, and the console scripts in `pyproject.toml`. This keeps the repository root focused on metadata and documentation rather than wrapper files.

### Vertical Detail Storage

Event detail fields vary significantly across ForexFactory events. The vertical block CSV format avoids sparse, unstable wide schemas while keeping each event's field set intact.

## Testing Strategy

- `tests/core/` covers foundational path behavior
- `tests/services/` injects stub ports into use cases
- `tests/integration/` exercises real adapters with temporary files
- Existing `unittest` tests still validate path, query, and formatting behavior

## Extension Guidelines

- Add or update a port before binding a new infrastructure dependency into a use case.
- Implement new external dependencies in `forexcalendar_scraper/infrastructure/web/` or `forexcalendar_scraper/infrastructure/persistence/`.
- Wire new adapters in `forexcalendar_scraper/bootstrap.py`.
- Keep CLI handlers thin and keep the repository root free of ad-hoc wrappers.
- Do not reintroduce Playwright page handling into `forexcalendar_scraper/application/`.