"""ForexFactory scraping integration."""

from __future__ import annotations

import logging
import re
import time

from playwright.sync_api import Locator, Page

from forexcalendar_scraper.core.config import Settings, get_settings
from forexcalendar_scraper.core.constants import (
    CALENDAR_ROW_SELECTOR,
    CALENDAR_TABLE_SELECTOR,
    DETAIL_CONTAINER_SELECTORS,
    DETAIL_HISTORY_TABLE_SELECTORS,
    DETAIL_NEWS_CONTAINER_SELECTORS,
    DETAIL_OVERLAY_SELECTORS,
    DETAIL_SPECS_TABLE_SELECTORS,
)
from forexcalendar_scraper.domain.entities import CalendarEvent, HistoryRecord, NewsItem
from forexcalendar_scraper.utils.formatting import sanitize_field_name


DAY_BREAKER_PATTERN = re.compile(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\w+\s+\d+)")


class ForexFactoryClient:
    """Playwright-based scraper for ForexFactory calendar pages."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def build_calendar_url(self, date_param: str) -> str:
        return f"{self.settings.forex_factory_base_url}?{date_param}"

    def scrape_calendar(
        self,
        page: Page,
        date_param: str,
        logger: logging.Logger,
    ) -> list[CalendarEvent]:
        url = self.build_calendar_url(date_param)
        logger.info("Navigating to ForexFactory calendar page: %s", url)
        page.goto(url)
        page.wait_for_selector(CALENDAR_TABLE_SELECTOR, timeout=self.settings.calendar_timeout_ms)

        rows = page.locator(CALENDAR_ROW_SELECTOR).all()
        logger.info("Found %s rows in the calendar table", len(rows))

        events: list[CalendarEvent] = []
        current_date = ""
        skipped_rows = 0

        for index, row in enumerate(rows):
            try:
                row_classes = row.get_attribute("class") or ""
                if "day-breaker" in row_classes:
                    extracted_date = self._extract_date_from_row(row, logger, index)
                    if extracted_date:
                        current_date = extracted_date
                    continue

                event = self._extract_event_from_row(row, current_date, logger, index)
                if event is None:
                    skipped_rows += 1
                    continue

                events.append(event)
                if len(events) % 10 == 0:
                    logger.info("Processed %s calendar events so far", len(events))
            except Exception as error:
                skipped_rows += 1
                logger.debug("Skipped row %s: %s", index + 1, error)

        logger.info("Calendar scraping finished. Processed=%s Skipped=%s", len(events), skipped_rows)
        return events

    def open_event_overlay(
        self,
        page: Page,
        date_param: str,
        detail_id: str,
        logger: logging.Logger,
    ) -> bool:
        if not detail_id:
            logger.debug("No detail ID provided; skipping overlay navigation")
            return False

        detail_url = f"{self.build_calendar_url(date_param)}#detail={detail_id}"
        logger.debug("Opening detail overlay for detail_id=%s", detail_id)
        page.goto(detail_url, wait_until="domcontentloaded")
        time.sleep(self.settings.detail_render_wait_seconds)

        detail_selectors = [selector.format(detail_id=detail_id) for selector in DETAIL_OVERLAY_SELECTORS]
        detail_selectors.extend(
            selector.format(detail_id=detail_id) for selector in DETAIL_CONTAINER_SELECTORS
        )
        selector = self._wait_for_any_selector(page, detail_selectors)
        if selector is None:
            logger.debug("Could not find detail overlay for detail_id=%s", detail_id)
            return False

        logger.debug("Found detail overlay for detail_id=%s with selector=%s", detail_id, selector)
        time.sleep(self.settings.detail_render_wait_seconds)
        return True

    def extract_detail_specs(
        self,
        page: Page,
        date_param: str,
        detail_id: str,
        logger: logging.Logger,
    ) -> dict[str, str] | None:
        if not self.open_event_overlay(page, date_param, detail_id, logger):
            return None
        return self.extract_detail_specs_from_open_page(page, detail_id, logger)

    def extract_detail_specs_from_open_page(
        self,
        page: Page,
        detail_id: str,
        logger: logging.Logger,
    ) -> dict[str, str] | None:
        specs_table = self._find_specs_table(page)
        if specs_table is None:
            logger.debug("No specs table found for detail_id=%s", detail_id)
            return None

        specs_data: dict[str, str] = {}
        for row in specs_table.locator("tr").all():
            cells = row.locator("td").all()
            if len(cells) < 2:
                continue

            label = (cells[0].text_content() or "").strip()
            value = (cells[1].text_content() or "").strip()
            if not label or not value:
                continue

            specs_data[sanitize_field_name(label)] = value

        self._attach_full_details_link(page, specs_data)
        if not specs_data:
            return None

        logger.debug(
            "Extracted %s detail fields for detail_id=%s",
            len(specs_data),
            detail_id,
        )
        return specs_data

    def extract_history(
        self,
        page: Page,
        date_param: str,
        detail_id: str,
        logger: logging.Logger,
    ) -> list[HistoryRecord]:
        if not self.open_event_overlay(page, date_param, detail_id, logger):
            return []
        return self.extract_history_from_open_page(page, detail_id, logger)

    def extract_history_from_open_page(
        self,
        page: Page,
        detail_id: str,
        logger: logging.Logger,
    ) -> list[HistoryRecord]:
        history_table = self._find_first_locator(page, DETAIL_HISTORY_TABLE_SELECTORS)
        if history_table is None:
            logger.debug("No history table found for detail_id=%s", detail_id)
            return []

        history_records: list[HistoryRecord] = []
        header_row = history_table.locator("thead tr, tr:first-child").first
        if header_row.count() > 0:
            headers = [
                (cell.text_content() or "").strip().lower()
                for cell in header_row.locator("th, td").all()
            ]
            if headers:
                logger.debug("History table headers for detail_id=%s: %s", detail_id, headers)

        for row in history_table.locator("tbody tr, tr").all():
            cells = row.locator("td").all()
            if len(cells) < 2:
                continue

            record = HistoryRecord(detail_id=detail_id, date="")
            for index, cell in enumerate(cells):
                cell_text = (cell.text_content() or "").strip()
                if index == 0:
                    record.date = cell_text
                    link = cell.locator("a").first
                    if link.count() > 0:
                        href = link.get_attribute("href")
                        if href:
                            record.date_url = self._normalize_url(href)
                elif index == 1:
                    record.actual = cell_text
                elif index == 2:
                    record.forecast = cell_text
                elif index == 3:
                    record.previous = cell_text

            if record.date:
                history_records.append(record)

        logger.debug(
            "Extracted %s history records for detail_id=%s",
            len(history_records),
            detail_id,
        )
        return history_records

    def extract_news(
        self,
        page: Page,
        date_param: str,
        detail_id: str,
        logger: logging.Logger,
    ) -> list[NewsItem]:
        if not self.open_event_overlay(page, date_param, detail_id, logger):
            return []
        return self.extract_news_from_open_page(page, detail_id, logger)

    def extract_news_from_open_page(
        self,
        page: Page,
        detail_id: str,
        logger: logging.Logger,
    ) -> list[NewsItem]:
        news_container = self._find_first_locator(page, DETAIL_NEWS_CONTAINER_SELECTORS)
        if news_container is not None:
            news_items = self._extract_news_links(news_container.locator("a").all(), detail_id)
            logger.debug("Extracted %s structured news items for detail_id=%s", len(news_items), detail_id)
            return news_items

        right_panel = page.locator(".half.last.details").first
        if right_panel.count() == 0:
            logger.debug("No news container found for detail_id=%s", detail_id)
            return []

        news_items = self._extract_news_links(right_panel.locator("a").all(), detail_id, include_parent=True)
        logger.debug("Extracted %s fallback news items for detail_id=%s", len(news_items), detail_id)
        return news_items

    def _extract_date_from_row(
        self,
        row: Locator,
        logger: logging.Logger,
        row_index: int,
    ) -> str:
        date_cell = row.locator("td").first
        date_text = (date_cell.text_content() or "").strip()
        if not date_text:
            cell_html = date_cell.inner_html()
            date_match = DAY_BREAKER_PATTERN.search(cell_html)
            if date_match:
                date_text = date_match.group(0)

        cleaned_date = " ".join(date_text.split())
        if cleaned_date:
            logger.info("Detected date section on row %s: %s", row_index + 1, cleaned_date)
        return cleaned_date

    def _extract_event_from_row(
        self,
        row: Locator,
        current_date: str,
        logger: logging.Logger,
        row_index: int,
    ) -> CalendarEvent | None:
        event = CalendarEvent(
            date=current_date or "Unknown",
            time=self._get_locator_text(row, ".calendar__time"),
            currency=self._get_locator_text(row, ".calendar__currency"),
            impact=self._get_locator_attribute_or_text(row, ".calendar__impact span", "title"),
            name=self._get_locator_text(row, ".calendar__event"),
            actual=self._get_locator_text(row, ".calendar__actual"),
            forecast=self._get_locator_text(row, ".calendar__forecast"),
            previous=self._get_locator_text(row, ".calendar__previous"),
            detail_id=(row.get_attribute("data-event-id") or "").strip(),
        )
        if event.name or event.currency:
            return event

        all_cells = row.locator("td").all()
        if len(all_cells) < 7:
            logger.debug("Skipped row %s due to insufficient columns", row_index + 1)
            return None

        fallback_event = CalendarEvent(
            date=current_date or "Unknown",
            time=self._get_locator_text(row, ".calendar__time"),
            currency=self._get_locator_text(row, ".calendar__currency"),
            impact=self._get_locator_attribute_or_text(row, ".calendar__impact span", "title"),
            name=self._get_locator_text(row, ".calendar__event"),
            actual=self._get_locator_text(row, ".calendar__actual"),
            forecast=self._get_locator_text(row, ".calendar__forecast"),
            previous=self._get_locator_text(row, ".calendar__previous"),
            detail_id=(row.get_attribute("data-event-id") or "").strip(),
        )
        if fallback_event.name or fallback_event.currency:
            logger.debug("Recovered event from row %s", row_index + 1)
            return fallback_event
        return None

    def _get_locator_text(self, row: Locator, selector: str) -> str:
        locator = row.locator(selector)
        if locator.count() == 0:
            return ""
        return (locator.first.text_content() or "").strip()

    def _get_locator_attribute_or_text(self, row: Locator, selector: str, attribute: str) -> str:
        locator = row.locator(selector)
        if locator.count() == 0:
            return ""
        value = locator.first.get_attribute(attribute)
        if value:
            return value.strip()
        return (locator.first.text_content() or "").strip()

    def _wait_for_any_selector(self, page: Page, selectors: list[str]) -> str | None:
        for selector in selectors:
            try:
                page.wait_for_selector(selector, timeout=self.settings.overlay_timeout_ms)
                return selector
            except Exception:
                continue
        return None

    def _find_first_locator(self, page: Page, selectors: tuple[str, ...]) -> Locator | None:
        for selector in selectors:
            try:
                page.wait_for_selector(selector, timeout=self.settings.overlay_timeout_ms)
                locator = page.locator(selector).first
                if locator.count() > 0:
                    return locator
            except Exception:
                continue
        return None

    def _find_specs_table(self, page: Page) -> Locator | None:
        specs_table = self._find_first_locator(page, DETAIL_SPECS_TABLE_SELECTORS)
        if specs_table is not None:
            return specs_table

        try:
            page.wait_for_selector("table", timeout=self.settings.overlay_timeout_ms)
        except Exception:
            return None

        for table in page.locator("table").all():
            if len(table.locator("tr").all()) > 1:
                return table
        return None

    def _attach_full_details_link(self, page: Page, specs_data: dict[str, str]) -> None:
        solo_div = page.locator(".calendardetails__solo").first
        if solo_div.count() == 0:
            return

        link = solo_div.locator("a").first
        if link.count() == 0:
            return

        href = link.get_attribute("href")
        if href:
            specs_data["full_details_url"] = self._normalize_url(href)

        link_text = (link.text_content() or "").strip()
        if link_text:
            specs_data["full_details_link_text"] = link_text

    def _extract_news_links(
        self,
        links: list[Locator],
        detail_id: str,
        include_parent: bool = False,
    ) -> list[NewsItem]:
        news_items: list[NewsItem] = []
        for link in links:
            title = (link.text_content() or "").strip()
            href = link.get_attribute("href")
            if not title or not href or len(title) <= 5:
                continue
            if len(title) < 15 and any(character.isdigit() for character in title):
                continue

            snippet = ""
            if include_parent:
                parent = link.locator("xpath=..").first
                if parent.count() > 0:
                    parent_text = (parent.text_content() or "").strip()
                    if len(parent_text) > len(title):
                        snippet = parent_text[:200]

            news_items.append(
                NewsItem(
                    detail_id=detail_id,
                    title=title,
                    url=self._normalize_url(href),
                    snippet=snippet,
                    link_type=self._infer_link_type(href),
                )
            )
        return news_items

    def _normalize_url(self, href: str) -> str:
        if href.startswith("/"):
            return f"https://www.forexfactory.com{href}"
        return href

    def _infer_link_type(self, href: str) -> str:
        lowered = href.lower()
        if "news" in lowered or "article" in lowered:
            return "news"
        return "related"
