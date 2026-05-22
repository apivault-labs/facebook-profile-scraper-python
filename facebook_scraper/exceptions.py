"""Exception classes for the Facebook Profile Scraper SDK."""


class FacebookScraperError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(FacebookScraperError):
    """Raised when the Apify API token is missing or invalid."""


class ActorRunError(FacebookScraperError):
    """Raised when the actor run fails on Apify infrastructure."""


class ActorTimeoutError(FacebookScraperError):
    """Raised when the actor run does not finish within the allowed timeout."""
