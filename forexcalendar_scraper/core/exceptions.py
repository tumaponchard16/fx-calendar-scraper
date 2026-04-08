"""Application-specific exception types."""


class ForexCalendarError(Exception):
    """Base exception for the application."""


class BrowserInitializationError(ForexCalendarError):
    """Raised when Playwright cannot create a browser session."""


class InputFileResolutionError(ForexCalendarError):
    """Raised when an expected input file cannot be resolved."""
