"""
FacebookScraperClient — synchronous wrapper around the Apify
``apivault_labs/facebook-profile-scraper`` actor (v2.x).

The actor handles all heavy work (Apify residential proxy, multi-strategy
fetch fallback, login-wall detection, tech stack detection, real-email
scraping, phone normalisation, page category, JSON-LD aggregate rating,
postal address, opening hours, activity scoring, outreach-pitch
generation) on Apify infrastructure. This client forwards inputs, polls
until the run finishes, then downloads the dataset and splits it into
per-profile records and the optional aggregate summary.

Pricing: $0.004 per profile ($4 / 1000). All enrichment included.
"""

from __future__ import annotations

import os
import time
from typing import Any, Iterable, Sequence

import requests

from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    FacebookScraperError,
)


ACTOR_ID = "apivault_labs~facebook-profile-scraper"
APIFY_API_BASE = "https://api.apify.com/v2"

TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}

PRICE_PER_PROFILE_USD = 0.004


class FacebookScraperClient:
    """Synchronous client for the Facebook Profile Scraper Apify actor.

    Parameters
    ----------
    api_token : str, optional
        Apify Personal API token. If omitted, falls back to the
        ``APIFY_API_TOKEN`` environment variable.
    timeout : int, optional
        Maximum seconds to wait for an actor run to finish. Default 900
        (15 min) — typical runs finish in 10-60 seconds, but residential
        proxy retries on rate-limited URLs can stretch the tail.
    poll_interval : float, optional
        Seconds between status polls. Default 3.
    base_url : str, optional
        Override the Apify API base URL (mostly for testing).
    """

    def __init__(
        self,
        api_token: str | None = None,
        timeout: int = 900,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "Apify API token is required. Pass api_token='apify_api_...' "
                "or set the APIFY_API_TOKEN environment variable. "
                "Get a token at https://console.apify.com/account/integrations"
            )
        self._token = token
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "facebook-profile-scraper-python/0.1.0",
        })

    # ------------------------------------------------------------------ public

    def scrape(
        self,
        profile_urls: Iterable[str],
        *,
        max_concurrency: int = 3,
        timeout_per_profile: int = 45,
        use_residential_proxy: bool = True,
        proxy_country: str = "US",
        actor_timeout_secs: int = 600,
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Scrape a batch of public Facebook profiles and pages.

        Parameters
        ----------
        profile_urls : iterable of str
            Public Facebook profile or page URLs (e.g.
            ``https://www.facebook.com/NASA``). Both ``/username/`` and
            ``/profile.php?id=...`` formats are accepted.
        max_concurrency : int, optional
            How many profiles to scrape in parallel (1-10). Default 3.
            Higher values are faster but more likely to trigger Facebook
            rate limits.
        timeout_per_profile : int, optional
            Seconds to wait per profile fetch (15-120). Default 45.
        use_residential_proxy : bool, optional
            Use Apify residential proxy. Strongly recommended — Facebook
            blocks most datacenter IPs.
        proxy_country : str, optional
            ISO 2-letter country code for residential proxy. Default "US".
        actor_timeout_secs : int, optional
            Maximum runtime hint passed to the actor.

        Returns
        -------
        tuple[list[dict], dict | None]
            ``(profiles, summary)``. ``summary`` contains aggregate stats
            (totalScraped, totalFailed, verifiedCount, withEmailCount,
            avgActivityScore, activityTierBreakdown) or ``None`` when zero
            profiles succeeded.
        """
        cleaned = [u.strip() for u in profile_urls if u and u.strip()]
        if not cleaned:
            raise ValueError("profile_urls must contain at least one non-empty URL")

        payload = {
            "profileUrls": cleaned,
            "maxConcurrency": max(1, min(10, int(max_concurrency))),
            "timeout": max(15, min(120, int(timeout_per_profile))),
            "useResidentialProxy": bool(use_residential_proxy),
            "proxyCountry": (proxy_country or "").strip().upper(),
        }

        run_id = self._start_run(payload, actor_timeout_secs=actor_timeout_secs)
        run = self._wait_for_run(run_id)
        records = self._fetch_dataset(run["defaultDatasetId"])
        return self._split_summary(records)

    def scrape_one(self, profile_url: str, **kwargs: Any) -> dict[str, Any]:
        """Convenience wrapper for a single Facebook URL.

        Returns the result record. Raises ``ActorRunError`` if the actor
        produced no records or only an error record.
        """
        results, _ = self.scrape([profile_url], **kwargs)
        if not results:
            raise ActorRunError(
                f"Actor returned no records for {profile_url!r} — Facebook may "
                "have blocked all fetch strategies. Try again later or use a "
                "different proxy country."
            )
        rec = results[0]
        if not rec.get("success", True):
            raise ActorRunError(
                f"Scrape failed for {profile_url!r}: {rec.get('error', '?')}"
            )
        return rec

    # ------------------------------------------------------------------ filters

    def filter_by_tier(
        self,
        profiles: Sequence[dict[str, Any]],
        *tiers: str,
    ) -> list[dict[str, Any]]:
        """Filter profiles by activity tier.

        Tiers: ``"major"`` (≥70), ``"established"`` (50-69),
        ``"growing"`` (30-49), ``"small"`` (<30). Pass one or more tiers
        — they are OR'd together.
        """
        if not tiers:
            tiers = ("major", "established")
        wanted = {t.lower() for t in tiers}
        return [r for r in profiles if (r.get("activityTier") or "").lower() in wanted]

    def filter_verified(
        self,
        profiles: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Filter to profiles with the verified blue badge."""
        return [r for r in profiles if r.get("verified")]

    def filter_with_email(
        self,
        profiles: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Filter to profiles where at least one public email was scraped
        from the page."""
        return [r for r in profiles if r.get("emails")]

    def filter_micro_influencers(
        self,
        profiles: Sequence[dict[str, Any]],
        min_followers: int = 10_000,
        max_followers: int = 100_000,
    ) -> list[dict[str, Any]]:
        """Filter to micro-influencer territory — usually the highest-ROI
        outreach segment for brand partnerships."""
        out: list[dict[str, Any]] = []
        for r in profiles:
            followers = r.get("followerCount") or 0
            if min_followers <= followers <= max_followers:
                out.append(r)
        return out

    def estimate_cost(self, profile_count: int) -> float:
        """Return the estimated USD cost for ``profile_count`` profiles.

        Pricing is $0.004 per profile ($4 / 1000). All enrichment is
        included in the per-profile price.
        """
        return round(profile_count * PRICE_PER_PROFILE_USD, 4)

    # ------------------------------------------------------------------ internal

    @staticmethod
    def _split_summary(
        records: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Separate the aggregate `_summary` record from per-profile records."""
        profiles: list[dict[str, Any]] = []
        summary: dict[str, Any] | None = None
        for rec in records:
            if isinstance(rec, dict) and rec.get("_summary"):
                summary = rec
            else:
                profiles.append(rec)
        return profiles, summary

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        params = {"timeout": int(actor_timeout_secs)}
        try:
            r = self._session.post(url, params=params, json=payload, timeout=30)
        except requests.RequestException as e:
            raise FacebookScraperError(f"Failed to start actor run: {e}") from e

        if r.status_code == 401:
            raise AuthenticationError(
                "Apify rejected the API token. Generate a new one at "
                "https://console.apify.com/account/integrations"
            )
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when starting run: {r.text[:300]}"
            )

        data = r.json().get("data") or {}
        run_id = data.get("id")
        if not run_id:
            raise ActorRunError(f"Apify response missing run id: {r.text[:300]}")
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=30)
            except requests.RequestException as e:
                raise FacebookScraperError(f"Failed to poll run status: {e}") from e

            if r.status_code >= 400:
                raise ActorRunError(
                    f"Apify returned HTTP {r.status_code} when polling run: {r.text[:300]}"
                )

            run = r.json().get("data") or {}
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(
                    f"Actor run {run_id} ended with status={status}: "
                    f"{run.get('statusMessage') or '(no message)'}"
                )

            if time.time() > deadline:
                raise ActorTimeoutError(
                    f"Actor run {run_id} did not finish within {self._timeout}s "
                    f"(last status={status}). The run may still be running on Apify; "
                    "increase `timeout=` or fetch the dataset manually."
                )

            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        try:
            r = self._session.get(url, params=params, timeout=120)
        except requests.RequestException as e:
            raise FacebookScraperError(f"Failed to download dataset: {e}") from e

        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when fetching dataset: "
                f"{r.text[:300]}"
            )

        try:
            data = r.json()
        except ValueError as e:
            raise ActorRunError(f"Apify dataset is not valid JSON: {e}") from e

        if not isinstance(data, list):
            raise ActorRunError(
                f"Unexpected dataset payload (not a list): {type(data).__name__}"
            )
        return data
