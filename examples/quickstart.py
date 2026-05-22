"""
Quickstart: scrape 3 Facebook pages and print pitches.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from facebook_scraper import FacebookScraperClient


def main() -> None:
    client = FacebookScraperClient()  # picks up APIFY_API_TOKEN from env

    urls = [
        "https://www.facebook.com/NASA",
        "https://www.facebook.com/cocacola",
        "https://www.facebook.com/Microsoft",
    ]

    print(f"Scraping {len(urls)} pages "
          f"(estimated cost: ${client.estimate_cost(len(urls))})...\n")

    profiles, summary = client.scrape(urls)

    for p in profiles:
        if not p.get("success"):
            print(f"❌ {p.get('inputUrl')}: {p.get('error', '?')}")
            continue
        name = p.get("fullName") or p.get("username") or "?"
        followers = p.get("followerCount") or 0
        tier = p.get("activityTier") or "?"
        verified = "✓" if p.get("verified") else " "
        print(f"\n{verified} {name}")
        print(f"   Followers:  {followers:,}")
        print(f"   Category:   {p.get('category') or '—'}")
        print(f"   Tier:       {tier} ({p.get('activityScore')}/100)")

        bc = p.get("bestContact") or {}
        print(f"   Contact:    {bc.get('value', '—')}  ({bc.get('label', '')})")

        pitch = p.get("outreachPitch")
        if pitch:
            print(f"   💡 {pitch[:200]}")

        recs = p.get("recommendations") or []
        if recs:
            print("   Recommendations:")
            for r in recs[:3]:
                print(f"      {r}")

    if summary:
        print(f"\n=== Summary ===")
        print(f"  Scraped:        {summary['totalScraped']}/{summary['totalScraped'] + summary['totalFailed']}")
        print(f"  Verified:       {summary['verifiedCount']}")
        print(f"  With email:     {summary['withEmailCount']}")
        print(f"  With phone:     {summary['withPhoneCount']}")
        print(f"  With website:   {summary['withWebsiteCount']}")
        print(f"  Avg score:      {summary['avgActivityScore']}/100")
        print(f"  Tier breakdown: {summary['activityTierBreakdown']}")


if __name__ == "__main__":
    main()
