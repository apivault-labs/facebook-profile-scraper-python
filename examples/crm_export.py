"""
Export Facebook page data as a flat CSV ready for HubSpot, Pipedrive,
Salesforce or Close.

Maps the actor's nested JSON structure to flat columns with CRM-friendly
names (Company, Website, Industry, Lead Score, etc.).

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/crm_export.py > leads.csv
"""

import csv
import sys

from facebook_scraper import FacebookScraperClient


PROFILES = [
    "https://www.facebook.com/NASA",
    "https://www.facebook.com/cocacola",
    "https://www.facebook.com/Microsoft",
    "https://www.facebook.com/Tesla",
]


COLUMNS = [
    "Company",
    "Industry",
    "Website",
    "Email",
    "Phone",
    "Best Contact",
    "Best Contact Channel",
    "Verified",
    "Followers",
    "Likes",
    "Activity Score",
    "Activity Tier",
    "Bio",
    "Locale",
    "Profile URL",
    "Profile Type",
    "Avatar URL",
    "Outreach Pitch",
    "Recommendations",
]


def to_row(p: dict) -> dict:
    if not p.get("success"):
        return {}
    bc = p.get("bestContact") or {}
    return {
        "Company":              p.get("fullName"),
        "Industry":             p.get("category") or "",
        "Website":              p.get("primaryWebsite") or "",
        "Email":                p.get("primaryEmail") or "",
        "Phone":                p.get("primaryPhone") or "",
        "Best Contact":         bc.get("value", ""),
        "Best Contact Channel": bc.get("channel", ""),
        "Verified":             "Yes" if p.get("verified") else "No",
        "Followers":            p.get("followerCount") or "",
        "Likes":                p.get("likeCount") or "",
        "Activity Score":       p.get("activityScore") or "",
        "Activity Tier":        p.get("activityTier") or "",
        "Bio":                  (p.get("bio") or "").replace("\n", " ")[:500],
        "Locale":               p.get("locale") or "",
        "Profile URL":          p.get("profileUrl") or "",
        "Profile Type":         p.get("profileType") or "",
        "Avatar URL":           p.get("avatarUrl") or "",
        "Outreach Pitch":       (p.get("outreachPitch") or "").replace("\n", " "),
        "Recommendations":      "; ".join(p.get("recommendations") or []),
    }


def main() -> None:
    client = FacebookScraperClient()
    profiles, _ = client.scrape(PROFILES)

    writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    writer.writeheader()
    for p in profiles:
        row = to_row(p)
        if row:
            writer.writerow(row)


if __name__ == "__main__":
    main()
