# 📘 Facebook Profile Scraper — Python SDK

> **Direct Facebook scraping for public profiles and pages — no login, no cookies, no browser. Returns 30+ enrichment fields per profile: name, bio, followers, verification badge, public emails + phones, websites, page category, aggregate rating, postal address, opening hours, activity score, best-contact-channel recommendation, and an auto-generated outreach pitch.**

Python client for the [Facebook Profile Scraper Apify Actor](https://apify.com/apivault_labs/facebook-profile-scraper) — multi-strategy fallback (mobile, desktop, embed iframe) survives Facebook's 2026 anti-bot updates with residential proxy rotation.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue?logo=apify)](https://apify.com/apivault_labs/facebook-profile-scraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Pricing](https://img.shields.io/badge/pricing-$4%20per%201,000-orange)](https://apify.com/apivault_labs/facebook-profile-scraper)

---

## What it does

Scrape any public Facebook profile or page and get a sales-ready record back. Skips the broken third-party scrapers — fetches directly through Facebook's mobile, desktop, and embed iframe endpoints with multi-strategy merge so missing fields on one endpoint are filled in from another.

A direct, pay-per-use alternative to:
- Manual Facebook scraping (Graph API requires app review + login)
- Facebook Graph API (rate-limited, requires Page admin access)
- Generic social-data APIs ($99-$499/mo)
- Browser automation (10× slower, 10× more expensive per profile)

**Pricing:** $4 per 1,000 profiles ($0.004 each). All 30+ enrichment fields included in the per-profile price.

---

## Quick start

```python
from facebook_scraper import FacebookScraperClient

client = FacebookScraperClient(api_token="apify_api_xxxxxx")

profiles, summary = client.scrape([
    "https://www.facebook.com/NASA",
    "https://www.facebook.com/cocacola",
    "https://www.facebook.com/Microsoft",
])

for p in profiles:
    name = p.get("fullName")
    followers = p.get("followerCount") or 0
    tier = p.get("activityTier")
    contact = (p.get("bestContact") or {}).get("value")
    print(f"{name:<40} {followers:>12,}  [{tier}]  {contact}")
    print(f"  💡 {p.get('outreachPitch', '')[:150]}")
```

Output:
```
NASA - National Aeronautics and Space ...      28,639,533  [established]  https://www.facebook.com/NASA
  💡 Hi NASA - National Aeronautics and Space Administration (Government organization) — huge fan of...
Coca-Cola                                      107,494,695  [established]  https://www.facebook.com/Coca-Cola/
  💡 Hi Coca-Cola — huge fan of what you're doing for 107,494,695 followers...
Microsoft                                       13,344,221  [established]  https://www.facebook.com/Microsoft/
  💡 Hi Microsoft — huge fan of what you're doing for 13,344,221 followers...
```

---

## Installation

```bash
pip install git+https://github.com/apivault-labs/facebook-profile-scraper-python.git
```

Or clone and use directly:

```bash
git clone https://github.com/apivault-labs/facebook-profile-scraper-python.git
cd facebook-profile-scraper-python
pip install -r requirements.txt
```

Requires Python 3.9+ and the [`requests`](https://pypi.org/project/requests/) library.

---

## Get your API token (free)

1. Sign up at [apify.com](https://apify.com) — free tier includes $5 monthly credits, no card required
2. Go to [Account → Integrations](https://console.apify.com/account/integrations)
3. Copy your Personal API token

```bash
export APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
```

Or pass it explicitly:

```python
client = FacebookScraperClient(api_token="apify_api_xxxxxx")
```

---

## What you get for $0.004 per profile

### Core fields (always returned when scrape succeeds)
- `username`, `fullName`, `bio`, `category`, `locale`
- `profileUrl`, `avatarUrl`
- `profileType` — `page` / `profile` / `group` / `unknown`
- `verified` — boolean for blue badge

### Counts
- `followerCount` — primary follower number
- `likeCount` — page likes (different from followers)

### Contact data
- `emails[]`, `primaryEmail` — public emails scraped from page (mailto, plain-text, CloudFlare-decoded, obfuscated)
- `phones[]`, `primaryPhone` — public phones with regex normalisation
- `websites[]`, `primaryWebsite` — external sites, unwrapped from `l.facebook.com/l.php?u=…`
- `bestContact: {channel, value, label}` — single highest-confidence outreach path

### LocalBusiness fields (when available)
- `aggregateRating: {ratingValue, ratingCount, reviewCount, bestRating}` — Facebook reviews aggregate
- `address: {street, city, region, postcode, country}` — postal address from JSON-LD
- `openingHours[]` — `["Mo-Fr 09:00-18:00", "Sa 10:00-14:00"]`

### Lead intelligence
- `activityScore` (0-100) — composite of followers + verification + has-contact + has-bio
- `activityScoreReasons[]` — every contributing signal in plain English
- `activityTier` — `small` / `growing` / `established` / `major`
- `recommendations[]` — actionable plain-English advice
- `outreachPitch` — auto-written cold opener tailored to the page

### Cross-platform helpers
- `socialSearchUrls{}` — 1-click search links for Instagram, LinkedIn, TikTok, Twitter/X, YouTube, Google

### Diagnostics
- `fetchStrategy` — which endpoints succeeded (`mobile`, `desktop`, `embed`)
- `fetchStatus` — HTTP status of the successful fetch

---

## Examples

See the [`examples/`](examples) folder for full code:

| File | What it does |
|---|---|
| [`quickstart.py`](examples/quickstart.py) | Scrape 3 well-known pages, print pitches |
| [`bulk_scrape.py`](examples/bulk_scrape.py) | Batch scrape with summary stats |
| [`micro_influencers.py`](examples/micro_influencers.py) | Filter to 10K-100K follower territory |
| [`verified_only.py`](examples/verified_only.py) | Keep only verified pages |
| [`with_email_only.py`](examples/with_email_only.py) | Keep only pages with public email |
| [`crm_export.py`](examples/crm_export.py) | Export flat CSV for HubSpot/Pipedrive |
| [`competitor_watch.py`](examples/competitor_watch.py) | Daily snapshot of competitor pages |

---

## API reference

### `FacebookScraperClient(api_token=None, timeout=900)`

| Param | Type | Description |
|---|---|---|
| `api_token` | `str` | Apify API token. Falls back to `APIFY_API_TOKEN` env var. |
| `timeout` | `int` | Max seconds to wait for the actor run. Default 900 (15 min). |
| `poll_interval` | `float` | Seconds between status polls. Default 3. |

### `client.scrape(profile_urls, **kwargs)`

Scrape a batch of profiles synchronously.

| Param | Type | Default | Description |
|---|---|---|---|
| `profile_urls` | `list[str]` | required | Public Facebook profile or page URLs |
| `max_concurrency` | `int` | 3 | Parallel scrapes (1-10) |
| `timeout_per_profile` | `int` | 45 | Seconds to wait per profile |
| `use_residential_proxy` | `bool` | `True` | Use Apify residential proxy (recommended) |
| `proxy_country` | `str` | `"US"` | ISO 2-letter country code |

Returns: `tuple[list[dict], dict | None]` — `(profiles, summary)`.

### `client.scrape_one(profile_url, **kwargs)`

Convenience wrapper for a single URL. Returns one `dict` or raises `ActorRunError`.

### Filter helpers (client-side, no extra Apify calls)

```python
client.filter_by_tier(profiles, "major", "established")  # tier filter
client.filter_verified(profiles)                          # blue badge only
client.filter_with_email(profiles)                        # pages with public email
client.filter_micro_influencers(profiles, min_followers=10_000, max_followers=100_000)
```

### `client.estimate_cost(profile_count)`

Returns the estimated USD cost (`profile_count × $0.004`).

---

## Sample output

```json
{
  "success": true,
  "inputUrl": "https://www.facebook.com/NASA",
  "profileType": "page",
  "fetchStrategy": "mobile,embed,desktop",
  "fetchStatus": 200,

  "username": "NASA",
  "fullName": "NASA - National Aeronautics and Space Administration",
  "bio": "Explore the universe and discover our home planet.",
  "category": "Government organization",
  "locale": "en_us",
  "verified": true,

  "profileUrl": "https://www.facebook.com/NASA",
  "avatarUrl": "https://scontent.fbcdn.net/...",

  "followerCount": 28639533,
  "likeCount": 25800000,

  "websites": ["https://www.nasa.gov/"],
  "primaryWebsite": "https://www.nasa.gov/",
  "emails": ["public-inquiries@hq.nasa.gov"],
  "primaryEmail": "public-inquiries@hq.nasa.gov",
  "phones": [],
  "primaryPhone": null,

  "aggregateRating": null,
  "address": null,
  "openingHours": null,

  "bestContact": {
    "channel": "email",
    "value": "public-inquiries@hq.nasa.gov",
    "label": "public email from page"
  },

  "socialSearchUrls": {
    "instagram": "https://www.google.com/search?q=...+site%3Ainstagram.com",
    "linkedin":  "https://www.google.com/search?q=...+site%3Alinkedin.com",
    "tiktok":    "https://www.google.com/search?q=...+site%3Atiktok.com",
    "twitter":   "https://www.google.com/search?q=...+site%3Ax.com",
    "youtube":   "https://www.google.com/search?q=...+site%3Ayoutube.com",
    "googleSearch": "https://www.google.com/search?q=..."
  },

  "activityScore": 73,
  "activityTier": "major",
  "activityScoreReasons": [
    "verified page (blue badge)",
    "business page (extracts more data)",
    "28,639,533 followers — major brand",
    "has external website",
    "has public email"
  ],
  "recommendations": [
    "⭐ Major brand — high outreach effort justified, expect long sales cycle and gatekeepers.",
    "🛡️ Verified mega-brand — go through their PR/agency contact, not direct DM.",
    "📧 Public email available — your highest-converting channel for cold outreach."
  ],
  "outreachPitch": "Hi NASA - National Aeronautics and Space Administration (Government organization) — huge fan of what you're doing for 28,639,533 followers. We work with verified brands like yours to expand cross-platform presence (Instagram, TikTok, LinkedIn). Worth a 15-min intro call?"
}
```

---

## Use cases

### 🏢 B2B Lead Generation
Pull a list of competitor pages, filter to those with `primaryEmail` populated, sort by `activityScore`. Hand to your SDR team.

```python
profiles, _ = client.scrape(competitor_urls)
hot_leads = client.filter_with_email(client.filter_by_tier(profiles, "established", "major"))
```

### 🎯 Micro-Influencer Discovery
Filter to 10K-100K follower territory — proven engagement at affordable rates.

```python
profiles, _ = client.scrape(creator_urls)
micros = client.filter_micro_influencers(profiles)
verified_micros = client.filter_verified(micros)
```

### 🔗 CRM Enrichment
Already have FB URLs in HubSpot/Pipedrive? Run the actor and merge `bestContact`, `primaryEmail`, `verified`, `category`, `activityTier` back into your records.

### 📊 Brand Monitoring
Daily snapshot of follower counts, verification status, and category for a watchlist of brands. Diff against yesterday to catch verification changes or follower spikes.

### 🌍 International Expansion Research
Use `locale` to find pages in target markets. Cross-reference `socialSearchUrls` to find their other-platform presence.

### 📰 Media Watchlist
Scrape news outlets, government pages, NGOs periodically. Track follower growth and any verification changes.

### 🏪 Local Business Audit
Pages with `address` + `openingHours` + `aggregateRating` are LocalBusiness entities — combine with email scraping for local SEO outreach.

---

## How activity score works

| Signal | Points |
|---|---|
| Verified blue badge | +25 |
| Is business page | +5 |
| Followers ≥ 50M | +35 |
| Followers 5M-50M | +30 |
| Followers 1M-5M | +25 |
| Followers 100K-1M | +18 |
| Followers 10K-100K | +12 |
| Followers 1K-10K | +6 |
| Has external website | +10 |
| Has public email | +10 |
| Has public phone | +5 |
| Has bio | +5 |
| Has avatar | +3 |

Score is clamped 0-100. Tiers:
- `small` (<30)
- `growing` (30-49)
- `established` (50-69)
- `major` (70+)

---

## How fetch fallback works

Each profile cycles through Facebook endpoints until one returns parseable HTML:

1. **`m.facebook.com/{username}`** — modern mobile site, lightest payload, gives og:title + bio reliably
2. **`www.facebook.com/{username}`** — desktop, has full JSON-LD with category and rating
3. **`/plugins/page.php?href=...`** — embed iframe, public-by-design, exposes follower count even when other endpoints hide it for logged-out users

The actor runs all three concurrently through Apify residential proxy, then **merges the responses** by picking the most populated record as a skeleton and filling missing fields from the others.

Login walls are detected and discarded explicitly so we never return "Log in to Facebook" as a fake success.

---

## Pricing

Pay only for successful scrapes:

| Volume | Cost |
|---|---|
| 100 profiles | $0.40 |
| 1,000 profiles | $4.00 |
| 10,000 profiles | $40.00 |

Free Apify tier (~$5/month credit) covers ~1,250 profiles per month.

You only pay for **successful** scrapes. If Facebook blocks all fetch strategies for a URL, that record is marked `success: false` and you're not charged for it.

---

## FAQ

**Q: Why doesn't this require a Facebook login or API key?**
A: It uses the same public HTML endpoints Facebook serves to logged-out browsers. No Facebook accounts, no app review, no Graph API tokens.

**Q: How accurate is verification detection?**
A: When `verified: true`, the blue badge has been confirmed via either JSON-LD `identifier` or `verification_badge` HTML token. False negatives possible (some old pages don't expose the badge in HTML even when verified on-site).

**Q: Will it scrape personal profiles?**
A: Yes — public personal profiles return name, bio, avatar, and (sometimes) follower count. They don't have category, page email, or aggregate rating.

**Q: What about private profiles?**
A: Returns `success: false` — only data Facebook serves to logged-out users is accessible.

**Q: Why is `emails: []` for some big brands?**
A: Many brands hide emails behind contact forms or login prompts. The actor can't see those. When `emails` is empty but `websites` is populated, try the website's contact form.

**Q: How does the SDK handle Facebook's frequent layout changes?**
A: The underlying actor merges results from multiple Facebook endpoints — when one breaks, the others still work. The actor team patches breakages within 24-48 hours of detection.

**Q: Can I use my own proxy?**
A: Currently the actor uses Apify residential proxy. Custom-proxy support is on the roadmap.

**Q: Is there an async / concurrent client?**
A: The actor itself runs requests concurrently on Apify (configurable via `max_concurrency`). The Python client is sync because Apify run polling is inherently sequential — wrap `scrape()` in `asyncio.to_thread()` if you need it inside an asyncio app.

---

## Related Apify actors

- [TikTok Profile Scraper](https://apify.com/apivault_labs/tiktok-profile-scraper) — same intelligence pattern for TikTok
- [TikTok Shadow Ban Checker](https://apify.com/apivault_labs/tiktok-shadow-ban-checker) — detect FYP suppression
- [Instagram Profile Scraper](https://apify.com/apivault_labs/instagram-profile-scraper) — Instagram pages and accounts
- [Local Lead Finder](https://apify.com/apivault_labs/local-business-lead-finder) — YellowPages business discovery

See [all actors by apivault_labs](https://apify.com/apivault_labs).

---

## License

MIT — see [LICENSE](LICENSE).

This client is open source. The underlying Apify actor is a paid service ($0.004/profile).

---

## Disclaimer

This scraper extracts only publicly accessible data Facebook serves to logged-out users. Use responsibly and respect Facebook's Terms of Service for your jurisdiction. Do not use scraped data for spam, harassment, or any unlawful purpose.

---

## Keywords

`facebook-scraper` `facebook-api` `facebook-profile-scraper` `facebook-page-scraper` `facebook-no-login` `facebook-no-api-key` `facebook-public-data` `facebook-graph-alternative` `facebook-followers-api` `facebook-verification-api` `facebook-page-info` `facebook-emails` `facebook-page-emails` `facebook-business-pages` `facebook-page-category` `facebook-aggregate-rating` `facebook-localbusiness` `social-media-scraper` `social-media-intelligence` `lead-generation` `b2b-lead-gen` `crm-enrichment` `influencer-discovery` `micro-influencers` `verified-pages` `brand-monitoring` `competitor-research` `web-scraping` `apify` `apify-actor` `python-sdk` `hunter-alternative` `apollo-alternative`
