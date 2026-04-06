# Project Guidelines

## Architecture

- Keep the repository root focused on runnable scripts and core project files. Place supporting documentation under `docs/`.
- `scraper.py` produces the base calendar CSV. `detail_extractor.py`, `history_extractor.py`, `news_extractor.py`, and `history_news_extractor.py` build on that output.
- Reuse `extractor_common.py` for shared browser setup, logger configuration, output-path logic, and CSV resolution instead of duplicating helper code in each script.

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

- Install dependencies with `pip install -r requirements.txt` and install Playwright Chromium with `python3 -m playwright install chromium` when needed.
- Run the standard unit test suite with `python3 -m unittest discover -s tests`.
- Scraper behavior should still be validated by running the affected script for a concrete date param and checking the generated files under `outputs/`.
- When changing details querying or output resolution, also verify `python3 query_details.py --list-fields` still works.

## Documentation

- Keep `README.md` as the main entry point for setup and usage.
- Put deeper workflow or extractor-specific guides under `docs/` and link to them from the README instead of expanding the root with extra markdown files.
