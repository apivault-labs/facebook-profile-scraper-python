"""
Filter Facebook pages to those with a public email.

These are your highest-converting cold-outreach targets — direct email
beats DMs every time.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/with_email_only.py
"""

from facebook_scraper import FacebookScraperClient


PROFILES = [
    "https://www.facebook.com/NASA",
    "https://www.facebook.com/cocacola",
    "https://www.facebook.com/Microsoft",
    "https://www.facebook.com/Tesla",
    "https://www.facebook.com/SpaceX",
]


def main() -> None:
    client = FacebookScraperClient()
    profiles, _ = client.scrape(PROFILES)

    with_email = client.filter_with_email(profiles)

    print(f"\n📧 {len(with_email)} of {len(profiles)} pages have a public email\n")

    for p in with_email:
        name = p.get("fullName") or "?"
        emails = p.get("emails") or []
        score = p.get("activityScore")
        tier = p.get("activityTier")
        print(f"  {name:<40}")
        for e in emails[:3]:
            print(f"      📧 {e}")
        print(f"      score={score} tier={tier}")
        pitch = (p.get("outreachPitch") or "")[:160]
        if pitch:
            print(f"      💡 {pitch}")
        print()


if __name__ == "__main__":
    main()
