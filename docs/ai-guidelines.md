# AI Guidelines

Use these rules when generating or editing code for this repository so changes stay consistent with the current architecture.

## Coding Conventions

- Follow PEP 8 and prefer explicit, readable names.
- Add type hints to public functions, service methods, and data models.
- Prefer dataclasses for domain payloads unless a stronger validation need emerges.
- Use the standard logging module instead of `print` inside application code.
- Keep comments rare and focused on non-obvious behavior.

## Folder Responsibilities

- `forexcalendar_scraper/cli/`: argument parsing and command orchestration only
- `forexcalendar_scraper/bootstrap.py`: composition root for wiring concrete adapters
- `forexcalendar_scraper/core/`: configuration, constants, logging, paths, exceptions
- `forexcalendar_scraper/domain/`: shared dataclasses and result objects
- `forexcalendar_scraper/ports/`: application-facing contracts for adapters
- `forexcalendar_scraper/application/`: application use cases and coordination logic
- `forexcalendar_scraper/infrastructure/web/`: browser control, selectors, and external web adapters
- `forexcalendar_scraper/infrastructure/persistence/`: file or storage access only
- `forexcalendar_scraper/utils/`: isolated pure helpers
- Repository root: package metadata, docs, tests, samples, and generated artifacts only

## Patterns To Follow

- Use constructor injection for repositories, clients, and factories in services.
- Make services depend on ports, not concrete adapters.
- Keep CLI logic in `forexcalendar_scraper/cli/` and delegate all real work to services.
- Prefer `python -m forexcalendar_scraper` and the console scripts in `pyproject.toml` over adding new root entrypoint files.
- Wire concrete implementations in `forexcalendar_scraper/bootstrap.py`.
- Raise specific exceptions from `forexcalendar_scraper/core/exceptions.py` for expected failure modes.
- Resolve output and input paths through `PathService` instead of manual string building.
- Reuse `CsvRepository`, `ForexFactoryGateway`, and `ForexFactoryClient` before adding new file or scraping helpers.

## Anti-Patterns To Avoid

- Do not add new runnable wrappers or browser automation at the repository root.
- Do not import Playwright page types or browser factories into `forexcalendar_scraper/application/`.
- Do not mix CSV reading or writing into service formatting helpers.
- Do not hardcode output paths outside `forexcalendar_scraper/core/paths.py`.
- Do not catch broad exceptions and silently continue without logging context.
- Do not add unrelated refactors in the same change when a targeted update is sufficient.

## Example Templates

### Service Class

```python
from dataclasses import dataclass

from forexcalendar_scraper.core.config import Settings
from forexcalendar_scraper.ports import LoggerFactory, PathServicePort


@dataclass(slots=True)
class ExampleService:
    settings: Settings
    path_service: PathServicePort
    logger_factory: LoggerFactory

    def run(self, date_param: str) -> None:
        output_file = self.path_service.build_output_file_path(date_param, "_example")
        _ = output_file
```

### Repository Class

```python
from pathlib import Path


class ExampleRepository:
    def save(self, output_file: Path, rows: list[dict[str, str]]) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        # write rows here
```

### API Handler

```python
import argparse

from forexcalendar_scraper.bootstrap import build_example_service


def run_example_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date-param", required=True)
    args = parser.parse_args(argv)

    build_example_service().run(args.date_param)
    return 0
```

### Data Model

```python
from dataclasses import dataclass


@dataclass(slots=True)
class ExampleRecord:
    identifier: str
    name: str
    value: str = ""
```

## Decision Rule For New Code

If a change needs scraping logic, file storage, and CLI wiring, implement it in this order:

1. Add or update the datamodel in `forexcalendar_scraper/domain/`.
2. Define or update the required contract in `forexcalendar_scraper/ports/`.
3. Add the scraping or integration adapter in `forexcalendar_scraper/infrastructure/web/`.
4. Add the persistence behavior in `forexcalendar_scraper/infrastructure/persistence/` if needed.
5. Orchestrate it in a service under `forexcalendar_scraper/application/`.
6. Wire the implementation in `forexcalendar_scraper/bootstrap.py`.
7. Expose it through `forexcalendar_scraper/cli/` and `pyproject.toml` console scripts instead of adding a new root wrapper.