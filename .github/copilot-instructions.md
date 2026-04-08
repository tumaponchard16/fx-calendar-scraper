# Project Guidelines

## Architecture

- Keep the repository root focused on project metadata, high-signal docs, tests, and generated artifacts. Place runtime code under `forexcalendar_scraper/` and supporting documentation under `docs/`.
- Use `python3 -m forexcalendar_scraper` or the console scripts in `pyproject.toml` for scrape, extract, and query workflows.
- Reuse `forexcalendar_scraper/core/paths.py`, `forexcalendar_scraper/core/logging.py`, `forexcalendar_scraper/infrastructure/persistence/csv_repository.py`, and `forexcalendar_scraper/infrastructure/web/browser.py` instead of introducing new root-level helper modules.

## Output And File Conventions

- Generated CSV files belong under `outputs/<mon-dd-yyyy>/`, derived from ForexFactory date params such as `day=oct18.2025` or `week=oct21.2025`.
- Logs belong under `outputs/logs/`.
- Sample CSVs used for manual verification belong under `samples/`.
- If output names, directory layout, or CLI examples change, update the relevant docs in `README.md` and `docs/extractors/` in the same change.

## Code Style

- Keep the codebase script-friendly and stdlib-first. Add dependencies only when they clearly simplify scraping or reliability.
- Preserve the existing `argparse`-based CLIs unless a task explicitly requires interface changes.
- Prefer small helper functions and targeted changes over large rewrites.

## Validation

- Install the project with `pip install -e .` for runtime usage and `pip install -e ".[dev]"` for development workflows. Install Playwright Chromium with `python3 -m playwright install chromium` when needed.
- Run the standard unit test suite with `python3 -m unittest discover -s tests`.
- Scraper behavior should still be validated by running the affected command for a concrete date param and checking the generated files under `outputs/`.
- When changing details querying or output resolution, also verify `python3 -m forexcalendar_scraper query-details --list-fields` still works.

## Documentation

- Keep `README.md` as the main entry point for setup and usage.
- Put deeper workflow or extractor-specific guides under `docs/` and link to them from the README instead of expanding the root with extra markdown files.
