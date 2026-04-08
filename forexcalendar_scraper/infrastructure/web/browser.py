"""Playwright browser session management."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import logging
from typing import Iterator

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from forexcalendar_scraper.core.config import Settings, get_settings
from forexcalendar_scraper.core.constants import BROWSER_ARGS, VIEWPORT_HEIGHT, VIEWPORT_WIDTH
from forexcalendar_scraper.core.exceptions import BrowserInitializationError


@dataclass(slots=True)
class BrowserSession:
    """A single Playwright browser session."""

    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page

    def close(self) -> None:
        """Close all Playwright resources in a safe order."""

        try:
            self.context.close()
        finally:
            try:
                self.browser.close()
            finally:
                self.playwright.stop()


@dataclass(slots=True)
class BrowserSessionFactory:
    """Create browser sessions with shared configuration."""

    settings: Settings

    def create_session(self, logger: logging.Logger, purpose: str) -> BrowserSession:
        logger.info("Initializing Playwright browser for %s", purpose)

        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(
                headless=self.settings.browser_headless,
                args=list(BROWSER_ARGS),
            )
            context = browser.new_context(
                viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
                user_agent=self.settings.user_agent,
            )
            page = context.new_page()
            logger.info("Playwright browser initialized successfully")
            return BrowserSession(
                playwright=playwright,
                browser=browser,
                context=context,
                page=page,
            )
        except Exception as error:
            logger.error("Failed to initialize Playwright browser: %s", error)
            logger.error(
                "Make sure Playwright Chromium is installed: python3 -m playwright install chromium"
            )
            raise BrowserInitializationError(str(error)) from error

    @contextmanager
    def open_page(self, logger: logging.Logger, purpose: str) -> Iterator[Page]:
        """Yield a Playwright page and always release the browser session."""

        session = self.create_session(logger, purpose)
        try:
            yield session.page
        finally:
            session.close()


def create_default_browser_session_factory() -> BrowserSessionFactory:
    """Create the default browser session factory."""

    return BrowserSessionFactory(get_settings())
