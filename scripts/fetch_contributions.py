#!/usr/bin/env python3
"""Scrape the public (no-token) contribution calendar HTML fragment GitHub
serves at /users/<username>/contributions and write data/contributions.json
with raw days plus derived stats.

Usage:
    python scripts/fetch_contributions.py [username]
"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "rcjasub"
URL_TMPL = "https://github.com/users/{username}/contributions"
OUT_PATH = Path("data/contributions.json")

COUNT_RE = re.compile(r"([\d,]+)\s+contributions?")


def fetch_html(username: str) -> str:
    resp = requests.get(
        URL_TMPL.format(username=username),
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day")

    tooltips = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        if target:
            tooltips[target] = tip.get_text(strip=True)

    days = []
    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = int(cell.get("data-level", 0))

        tooltip_text = tooltips.get(cell.get("id"), "") or cell.get("aria-label", "") or ""
        match = COUNT_RE.search(tooltip_text)
        count = int(match.group(1).replace(",", "")) if match else 0

        days.append({"date": d, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    if not days:
        return {}

    total = sum(d["count"] for d in days)

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"])

    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": dict(sorted(monthly.items())),
    }


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    html = fetch_html(username)
    days = parse_days(html)
    if not days:
        sys.exit("no contribution cells found -- GitHub markup may have changed")

    stats = compute_stats(days)
    payload = {
        "username": username,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"wrote {OUT_PATH} ({len(days)} days, {stats['total']} total contributions)")


if __name__ == "__main__":
    main()
