"""
Keep only verified (blue-badge) Facebook pages.

Use case: brand-safety vetting before a partnership, or building an
"established brands" outreach list. Verified pages are slightly more likely
to have a public PR/business email.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/verified_only.py
"""

from facebook_scraper import FacebookScraperClient


CANDIDATES = [
    "https://www.facebook.com/NASA",
    "https://www.facebook.com/cocacola",
    "https://www.facebook.com/Microsoft",
    "https://www.facebook.com/zuck",
    "https://www.facebook.com/Apple",
]


def main() -> None:
    client = FacebookScraperClient()
    profiles, summary = client.scrape(CANDIDATES)

    verified = client.filter_verified(profiles)
    unverified = [p for p in profiles if p.get("success") and not p.get("verified")]
    failed = [p for p in profiles if not p.get("success")]

    print(f"\n✓  Verified ({len(verified)}):")
    for p in sorted(verified, key=lambda x: -(x.get("followerCount") or 0)):
        followers = p.get("followerCount") or 0
        print(f"   {p.get('fullName'):<40} {followers:>14,} followers")

    print(f"\n·  Unverified ({len(unverified)}):")
    for p in unverified:
        followers = p.get("followerCount") or 0
        print(f"   {p.get('fullName'):<40} {followers:>14,} followers")

    if failed:
        print(f"\n✗  Failed ({len(failed)}):")
        for p in failed:
            print(f"   {p.get('inputUrl'):<40} {p.get('error', '?')[:60]}")

    if summary:
        print(f"\nVerification rate: {summary['verifiedCount']}/{summary['totalScraped']}")


if __name__ == "__main__":
    main()
