#!/usr/bin/env python3
"""Decide whether the contribution heatmap needs a refresh: true when the
user's latest push (to any repo) is newer than the last commit that touched
contrib-heatmap.svg. No state file -- git history is the marker.

Pushes older than RETRY_WINDOW are ignored, so a push that never changes the
graph (e.g. to a feature branch) stops being retried instead of looping.

Writes `changed=true|false` to $GITHUB_OUTPUT when run in Actions.

Usage:
    python scripts/check_new_push.py [username]
"""
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import requests

USERNAME = "rcjasub"
HEATMAP = "contrib-heatmap.svg"
RETRY_WINDOW = timedelta(hours=3)


def latest_push(username: str) -> datetime | None:
    headers = {"User-Agent": "profile-readme-bot", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_TOKEN")
    if token:
        # a token belonging to the user also returns their private-repo events
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(
        f"https://api.github.com/users/{username}/events",
        headers=headers,
        params={"per_page": 100},
        timeout=30,
    )
    resp.raise_for_status()
    pushes = [e["created_at"] for e in resp.json() if e["type"] == "PushEvent"]
    if not pushes:
        return None
    return datetime.fromisoformat(max(pushes).replace("Z", "+00:00"))


def last_heatmap_commit() -> datetime | None:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", HEATMAP],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return datetime.fromisoformat(out) if out else None


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    pushed = latest_push(username)
    rendered = last_heatmap_commit()
    now = datetime.now(timezone.utc)

    changed = (
        pushed is not None
        and (rendered is None or pushed > rendered)
        and now - pushed <= RETRY_WINDOW
    )
    print(f"latest push: {pushed}  last heatmap commit: {rendered}  -> changed={changed}")

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")


if __name__ == "__main__":
    main()
