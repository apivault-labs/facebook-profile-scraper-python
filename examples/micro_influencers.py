"""
Filter Facebook pages to micro-influencer territory (10K-100K followers).

This segment is the highest-ROI for brand partnerships — proven engagement
at affordable rates, often more responsive to direct outreach than mega-
brands behind PR/agency gatekeepers.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/micro_influencers.py
"""

from facebook_scraper import FacebookScraperClient


# Replace with actual creator URLs you're researching
CANDIDATE_URLS = [
    "https://www.facebook.com/NASA",            # too big — will filter out
    "https://www.facebook.com/cocacola",        # too big — will filter out
    "https://www.facebook.com/Microsoft",       # too big — will filter out
    # Add micro-influencer URLs here:
    # "https://www.facebook.com/some-small-page",
]


def main() -> None:
    client = FacebookScraperClient()
    profiles, _ = client.scrape(CANDIDATE_URLS)

    # 10K-100K = micro-influencer
    micros = client.filter_micro_influencers(profiles, 10_000, 100_000)
    # Mid-tier creators (100K-1M)
    mids = client.filter_micro_influencers(profiles, 100_000, 1_000_000)

    print(f"Scraped:               {len(profiles)}")
    print(f"Micro-influencers:     {len(micros)}  (10K-100K followers)")
    print(f"Mid-tier creators:     {len(mids)}    (100K-1M followers)")

    if micros:
        print(f"\n=== Micro-influencer candidates ===")
        for p in sorted(micros, key=lambda x: -(x.get("activityScore") or 0)):
            verified = "✓" if p.get("verified") else " "
            name = p.get("fullName") or "?"
            followers = p.get("followerCount") or 0
            score = p.get("activityScore")
            bc = p.get("bestContact") or {}
            print(f"  {verified} {name:<35} {followers:>10,}  score={score}  → {bc.get('value', '?')}")
            pitch = (p.get("outreachPitch") or "")[:180]
            if pitch:
                print(f"     💡 {pitch}")


if __name__ == "__main__":
    main()
