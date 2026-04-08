"""Environment-backed application configuration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from os import environ
from pathlib import Path

from forexcalendar_scraper.core.constants import DEFAULT_USER_AGENT


def _read_bool(source: Mapping[str, str], name: str, default: bool) -> bool:
    raw_value = source.get(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _read_int(source: Mapping[str, str], name: str, default: int) -> int:
    raw_value = source.get(name)
    if raw_value is None:
        return default
    return int(raw_value.strip())


def _read_float(source: Mapping[str, str], name: str, default: float) -> float:
    raw_value = source.get(name)
    if raw_value is None:
        return default
    return float(raw_value.strip())


def _load_dotenv_values(dotenv_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not dotenv_path.exists():
        return values

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        name, raw_value = line.split("=", 1)
        key = name.strip()
        value = raw_value.strip()
        if not key:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

        values[key] = value

    return values


@dataclass(frozen=True, slots=True)
class Settings:
    """Configuration values used by services and integrations."""

    forex_factory_base_url: str = "https://www.forexfactory.com/calendar"
    browser_headless: bool = True
    user_agent: str = DEFAULT_USER_AGENT
    log_level: str = "INFO"
    calendar_timeout_ms: int = 15_000
    overlay_timeout_ms: int = 5_000
    detail_render_wait_seconds: float = 2.0
    request_delay_seconds: float = 3.0
    batch_delay_seconds: float = 5.0
    batch_size: int = 5
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = False
    postgres_enabled: bool = False
    postgres_dsn: str = ""

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        if env is None:
            dotenv_path = Path(__file__).resolve().parents[2] / ".env"
            source = _load_dotenv_values(dotenv_path)
            source.update(environ)
        else:
            source = dict(env)

        postgres_dsn = source.get("FOREXFACTORY_POSTGRES_DSN", "").strip()

        return cls(
            forex_factory_base_url=source.get(
                "FOREXFACTORY_BASE_URL",
                "https://www.forexfactory.com/calendar",
            ).strip(),
            browser_headless=_read_bool(source, "FOREXFACTORY_HEADLESS", True),
            user_agent=source.get("FOREXFACTORY_USER_AGENT", DEFAULT_USER_AGENT).strip(),
            log_level=source.get("FOREXFACTORY_LOG_LEVEL", "INFO").strip().upper(),
            calendar_timeout_ms=_read_int(source, "FOREXFACTORY_CALENDAR_TIMEOUT_MS", 15_000),
            overlay_timeout_ms=_read_int(source, "FOREXFACTORY_OVERLAY_TIMEOUT_MS", 5_000),
            detail_render_wait_seconds=_read_float(
                source,
                "FOREXFACTORY_RENDER_WAIT_SECONDS",
                2.0,
            ),
            request_delay_seconds=_read_float(
                source,
                "FOREXFACTORY_REQUEST_DELAY_SECONDS",
                3.0,
            ),
            batch_delay_seconds=_read_float(
                source,
                "FOREXFACTORY_BATCH_DELAY_SECONDS",
                5.0,
            ),
            batch_size=_read_int(source, "FOREXFACTORY_BATCH_SIZE", 5),
            api_host=source.get("FOREXFACTORY_API_HOST", "127.0.0.1").strip(),
            api_port=_read_int(source, "FOREXFACTORY_API_PORT", 8000),
            api_reload=_read_bool(source, "FOREXFACTORY_API_RELOAD", False),
            postgres_enabled=_read_bool(
                source,
                "FOREXFACTORY_POSTGRES_ENABLED",
                bool(postgres_dsn),
            ),
            postgres_dsn=postgres_dsn,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings.from_env()
