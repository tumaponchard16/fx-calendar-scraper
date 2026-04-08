"""Path resolution and output layout helpers."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re

from forexcalendar_scraper.core.constants import DATE_PARAM_PATTERN_TEXT


DATE_PARAM_PATTERN = re.compile(DATE_PARAM_PATTERN_TEXT, re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class PathService:
    """Resolve project-relative paths and generated output locations."""

    root_dir: Path
    output_root: Path
    log_root: Path

    @classmethod
    def from_root(cls, root_dir: Path) -> "PathService":
        output_root = root_dir / "outputs"
        return cls(root_dir=root_dir, output_root=output_root, log_root=output_root / "logs")

    def build_date_folder_name(self, date_param: str) -> str:
        match = DATE_PARAM_PATTERN.fullmatch(date_param.strip())
        if not match:
            raise ValueError(
                "Unsupported date parameter format. Use values like 'day=oct18.2025' or 'week=oct21.2025'."
            )

        _, month, day, year = match.groups()
        return f"{month.lower()}-{int(day):02d}-{year}"

    def get_output_directory(self, date_param: str, create: bool = True) -> Path:
        output_directory = self.output_root / self.build_date_folder_name(date_param)
        if create:
            output_directory.mkdir(parents=True, exist_ok=True)
        return output_directory

    def build_output_file_path(
        self,
        date_param: str,
        suffix: str = "",
        create_dir: bool = True,
    ) -> Path:
        return self.get_output_directory(date_param, create=create_dir) / f"{date_param}{suffix}.csv"

    def build_log_file_path(self, script_name: str) -> Path:
        self.log_root.mkdir(parents=True, exist_ok=True)
        return self.log_root / f"{script_name}.log"

    def display_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root_dir))
        except ValueError:
            return str(path)

    def resolve_input_file(
        self,
        file_name: str | Path | None,
        preferred_date_param: str | None = None,
    ) -> Path | None:
        if not file_name:
            return None

        raw_path = Path(file_name)
        candidates: list[Path] = []

        if raw_path.is_absolute():
            candidates.append(raw_path)
        else:
            candidates.append(self.root_dir / raw_path)
            if preferred_date_param:
                candidates.append(
                    self.get_output_directory(preferred_date_param, create=False) / raw_path.name
                )
            if self.output_root.exists():
                candidates.extend(self.output_root.rglob(raw_path.name))

        seen: set[str] = set()
        for candidate in candidates:
            candidate_key = str(candidate)
            if candidate_key in seen:
                continue
            seen.add(candidate_key)
            if candidate.exists():
                return candidate.resolve()

        return None

    def resolve_primary_csv_path(self, csv_file: str | Path | None, date_param: str) -> Path | None:
        if csv_file:
            resolved_path = self.resolve_input_file(csv_file, preferred_date_param=date_param)
            if resolved_path:
                return resolved_path

        default_candidates = [
            self.build_output_file_path(date_param, create_dir=False),
            self.root_dir / f"{date_param}.csv",
            self.root_dir / "forexfactory_calendar.csv",
        ]

        for candidate in default_candidates:
            if candidate.exists():
                return candidate.resolve()

        return None

    def find_matching_files(self, pattern: str) -> list[Path]:
        matches: list[Path] = []
        if self.output_root.exists():
            matches.extend(sorted(self.output_root.rglob(pattern)))

        matches.extend(sorted(self.root_dir.glob(pattern)))

        unique_matches: list[Path] = []
        seen: set[str] = set()
        for match in matches:
            resolved_match = match.resolve()
            match_key = str(resolved_match)
            if match_key in seen:
                continue
            seen.add(match_key)
            unique_matches.append(resolved_match)

        return unique_matches


@lru_cache(maxsize=1)
def get_default_path_service() -> PathService:
    """Return the default path service rooted at the repository."""

    return PathService.from_root(Path(__file__).resolve().parents[2])
