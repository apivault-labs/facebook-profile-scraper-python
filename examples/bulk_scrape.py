"""
Scrape many Facebook pages in one batch.

The actor runs them in parallel on Apify infrastructure (configurable via
``max_concurrency``), so a single ``scrape`` call with many URLs is faster
and cheaper than calling the SDK once per URL.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/bulk_scrape.py
"""

from facebook_scraper import FacebookScraperClient


PROFILES = [
    "https://www.facebook.com/NASA",
    "https://www.facebook.com/cocacola",
    "https://www.facebook.com/Microsoft",
    "https://www.facebook.com/Apple",
    "https://www.facebook.com/Google",
    "https://www.facebook.com/Tesla",
    "https://www.facebook.com/SpaceX",
    "https://www.facebook.com/redbull",
]


def main() -> None:
    client = FacebookScraperClient(timeout=1800)
    print(f"Scraping {len(PROFILES)} profiles "
          f"(estimated cost: ${client.estimate_cost(len(PROFILES))})...\n")

    profiles, summary = client.scrape(PROFILES, max_concurrency=4)

    print(f"{'Verified':<9} {'Page':<28} {'Tier':<13} {'Followers':>13} {'Score':>6}")
    print("-" * 72)
    for p in sorted(profiles, key=lambda x: -(x.get("followerCount") or 0)):
        if not p.get("success"):
            continue
        verified = "✓" if p.get("verified") else " "
        name = (p.get("fullName") or "?")[:28]
        tier = (p.get("activityTier") or "?")[:13]
        followers = p.get("followerCount") or 0
        score = p.get("activityScore") or 0
        print(f"{verified:<9} {name:<28} {tier:<13} {followers:>13,} {score:>6}")

    if summary:
        print(f"\nVerified:       {summary['verifiedCount']}/{summary['totalScraped']}")
        print(f"With email:     {summary['withEmailCount']}")
        print(f"Avg score:      {summary['avgActivityScore']}/100")
        print(f"Tier breakdown: {summary['activityTierBreakdown']}")


if __name__ == "__main__":
    main()
