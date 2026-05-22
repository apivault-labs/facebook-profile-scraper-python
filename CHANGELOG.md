# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] — 2026-05-22

### Added
- Initial release of the Python SDK for `apivault_labs/facebook-profile-scraper` (actor v2.x)
- `FacebookScraperClient` with primary methods:
  - `scrape(profile_urls, **kwargs)` — main entry point
  - `scrape_one(profile_url, **kwargs)` — convenience wrapper
  - `filter_by_tier(profiles, *tiers)` — client-side tier filter (`major`, `established`, `growing`, `small`)
  - `filter_verified(profiles)` — keep only blue-badge pages
  - `filter_with_email(profiles)` — keep only pages with public email
  - `filter_micro_influencers(profiles, ...)` — 10K-100K follower segment
  - `estimate_cost(profile_count)` — pricing helper
- All 5 actor input parameters forwarded:
  `profileUrls`, `maxConcurrency`, `timeout`, `useResidentialProxy`, `proxyCountry`
- Automatic split of dataset into per-profile records and the aggregate `_summary` record
- 7 example scripts covering common workflows
- MIT license
