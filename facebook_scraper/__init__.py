"""
Facebook Profile Scraper — Python SDK

Official Python client for the apivault_labs/facebook-profile-scraper
Apify actor (v2.x). Direct Facebook scraping for public profiles and pages
with no login required.

Returns 30+ enrichment fields per profile:
- name, bio, follower count, like count, page category, locale
- verification badge (blue tick) detection
- public emails, phones, websites scraped from page HTML
- aggregate rating, postal address, opening hours
- activity score (0-100) + tier (small/growing/established/major)
- best-contact-channel recommendation
- cross-platform social search URLs (IG, LinkedIn, TikTok, Twitter, YouTube)
- auto-generated outreach pitch
- actionable recommendations

Quick start:

    from facebook_scraper import FacebookScraperClient

    client = FacebookScraperClient(api_token="apify_api_xxxxxx")

    profiles, summary = client.scrape([
        "https://www.facebook.com/NASA",
        "https://www.facebook.com/cocacola",
    ])
    for p in profiles:
        print(f"{p['fullName']}  {p['followerCount']:,}  {p['activityTier']}")
        print(f"  pitch: {p['outreachPitch']}")

See https://github.com/apivault-labs/facebook-profile-scraper-python for full docs.
"""

from .client import FacebookScraperClient
from .exceptions import (
    FacebookScraperError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    "FacebookScraperClient",
    "FacebookScraperError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
