"""FastAPI driver adapter for the project."""

from __future__ import annotations

from forexcalendar_scraper.api.app import app, create_app
from forexcalendar_scraper.core.config import Settings, get_settings
from forexcalendar_scraper.core.exceptions import OptionalDependencyError


def run_api_server(
    host: str | None = None,
    port: int | None = None,
    reload: bool | None = None,
    settings: Settings | None = None,
) -> int:
    resolved_settings = settings or get_settings()
    bind_host = host or resolved_settings.api_host
    bind_port = port if port is not None else resolved_settings.api_port
    use_reload = resolved_settings.api_reload if reload is None else reload

    try:
        import uvicorn
    except ModuleNotFoundError as error:
        raise OptionalDependencyError(
            "FastAPI server dependencies are not installed. "
            "Install with `pip install -e '.[server]'`."
        ) from error

    uvicorn.run(
        "forexcalendar_scraper.api.app:app",
        host=bind_host,
        port=bind_port,
        reload=use_reload,
    )
    return 0


__all__ = ["app", "create_app", "run_api_server"]