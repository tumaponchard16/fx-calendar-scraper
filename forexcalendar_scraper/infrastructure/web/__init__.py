"""External integration adapters."""

from forexcalendar_scraper.infrastructure.web.browser import BrowserSession, BrowserSessionFactory
from forexcalendar_scraper.infrastructure.web.forexfactory_client import ForexFactoryClient
from forexcalendar_scraper.infrastructure.web.forexfactory_gateway import ForexFactoryGateway

__all__ = ["BrowserSession", "BrowserSessionFactory", "ForexFactoryClient", "ForexFactoryGateway"]
