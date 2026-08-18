#!/usr/bin/env python3
"""Fetch public GitHub profile stats (join year, public repo count, top
language) via the public REST API -- no token needed. Writes
data/github_stats.json.

Usage:
    python scripts/fetch_github_stats.py [username]
"""
import json
import sys
from collections import Counter
from pathlib import Path

import requests

USERNAME = "rcjasub"
OUT_PATH = Path("data/github_stats.json")
HEADERS = {"User-Agent": "profile-readme-bot", "Accept": "application/vnd.github+json"}


def fetch_user(username: str) -> dict:
    resp = requests.get(f"https://api.github.com/users/{username}", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_top_language(username: str) -> str | None:
    languages: Counter = Counter()
    page = 1
    while True:
        resp = requests.get(
            f"https://api.github.com/users/{username}/repos",
            params={"per_page": 100, "page": page, "type": "owner"},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        repos = resp.json()
        if not repos:
            break
        for repo in repos:
            if repo.get("language") and not repo.get("fork"):
                languages[repo["language"]] += 1
        if len(repos) < 100:
            break
        page += 1
    if not languages:
        return None
    return languages.most_common(1)[0][0]


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    user = fetch_user(username)
    top_language = fetch_top_language(username)

    payload = {
        "username": username,
        "joined_year": user["created_at"][:4],
        "public_repos": user["public_repos"],
        "top_language": top_language,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"wrote {OUT_PATH}: {payload}")


if __name__ == "__main__":
    main()
