"""Gateway adapter that composes browser management and ForexFactory scraping."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from forexcalendar_scraper.infrastructure.web.browser import BrowserSessionFactory
from forexcalendar_scraper.infrastructure.web.forexfactory_client import ForexFactoryClient
from forexcalendar_scraper.domain.entities import CalendarEvent, DetailBlock, HistoryNewsBundle, HistoryRecord, NewsItem


@dataclass(slots=True)
class ForexFactoryGateway:
    """Outbound adapter that shields application services from Playwright details."""

    browser_factory: BrowserSessionFactory
    client: ForexFactoryClient

    def scrape_calendar(self, date_param: str, logger: logging.Logger) -> list[CalendarEvent]:
        with self.browser_factory.open_page(logger, "calendar scraping") as page:
            return self.client.scrape_calendar(page, date_param, logger)

    def extract_detail_block(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> DetailBlock | None:
        if not event.detail_id:
            return None

        with self.browser_factory.open_page(logger, "detail extraction") as page:
            fields = self.client.extract_detail_specs(page, date_param, event.detail_id, logger)

        if not fields:
            return None

        return DetailBlock(
            detail_id=event.detail_id,
            event_date=event.date,
            event_time=event.time,
            event_currency=event.currency,
            event_name=event.name,
            fields=fields,
        )

    def extract_history_records(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> list[HistoryRecord] | None:
        if not event.detail_id:
            return None

        with self.browser_factory.open_page(logger, "history extraction") as page:
            records = self.client.extract_history(page, date_param, event.detail_id, logger)

        if not records:
            return None
        return [record.with_event_context(event) for record in records]

    def extract_news_items(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> list[NewsItem] | None:
        if not event.detail_id:
            return None

        with self.browser_factory.open_page(logger, "news extraction") as page:
            records = self.client.extract_news(page, date_param, event.detail_id, logger)

        if not records:
            return None
        return [record.with_event_context(event) for record in records]

    def extract_history_news_bundle(
        self,
        event: CalendarEvent,
        date_param: str,
        logger: logging.Logger,
    ) -> HistoryNewsBundle | None:
        if not event.detail_id:
            return None

        with self.browser_factory.open_page(logger, "history and news extraction") as page:
            if not self.client.open_event_overlay(page, date_param, event.detail_id, logger):
                return None

            history = [
                record.with_event_context(event)
                for record in self.client.extract_history_from_open_page(page, event.detail_id, logger)
            ]
            news = [
                item.with_event_context(event)
                for item in self.client.extract_news_from_open_page(page, event.detail_id, logger)
            ]

        bundle = HistoryNewsBundle(history=history, news=news)
        return bundle if bundle else None