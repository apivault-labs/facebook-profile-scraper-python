"""
Daily snapshot of competitor Facebook pages.

Run this once per day from cron / GitHub Actions / Make and append each
snapshot to a JSONL file. Diff against yesterday to catch follower spikes,
verification changes, or category updates.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/competitor_watch.py
"""

import json
import time
from pathlib import Path

from facebook_scraper import FacebookScraperClient


COMPETITORS = [
    "https://www.facebook.com/NASA",
    "https://www.facebook.com/cocacola",
    "https://www.facebook.com/Microsoft",
]
LOG_FILE = Path("competitor_snapshots.jsonl")


def main() -> None:
    client = FacebookScraperClient()
    profiles, summary = client.scrape(COMPETITORS)

    snapshot = {
        "ts": int(time.time()),
        "scraped": [
            {
                "url": p.get("inputUrl"),
                "name": p.get("fullName"),
                "verified": p.get("verified"),
                "followers": p.get("followerCount"),
                "likes": p.get("likeCount"),
                "category": p.get("category"),
                "tier": p.get("activityTier"),
                "score": p.get("activityScore"),
                "primaryEmail": p.get("primaryEmail"),
                "primaryWebsite": p.get("primaryWebsite"),
            }
            for p in profiles
            if p.get("success")
        ],
        "summary": summary,
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")

    print(f"Logged snapshot of {len(snapshot['scraped'])} pages")
    for s in snapshot["scraped"]:
        v = "✓" if s["verified"] else " "
        followers = s["followers"] or 0
        print(f"  {v} {s['name']:<40} {followers:>14,} followers  [{s['tier']}]")

    print(f"\nAppended to {LOG_FILE.resolve()}")


if __name__ == "__main__":
    main()
