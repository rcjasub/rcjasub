#!/usr/bin/env python3
"""Render data/contributions.json as a 53-week x 7-day calendar of rounded
boxes, revealed once with a diagonal slide-down (CSS keyframes, no loop).

Usage:
    python scripts/render_heatmap_svg.py [output.svg]
"""
import json
import sys
from datetime import datetime
from pathlib import Path

DATA_PATH = Path("data/contributions.json")
DEFAULT_OUT = "contrib-heatmap.svg"

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]  # none -> brightest (level 5 is a neon top end)

BOX = 11
GAP = 3
CELL = BOX + GAP
PAD_LEFT = 30
PAD_TOP = 20
PAD_BOTTOM = 34
FONT = "ui-monospace, SFMono-Regular, Consolas, monospace"


def load_data() -> tuple[list[dict], dict]:
    payload = json.loads(DATA_PATH.read_text())
    return payload["days"], payload["stats"]


def to_weeks(days: list[dict]) -> list[list[dict | None]]:
    weeks: list[list[dict | None]] = []
    current_week: list[dict | None] = []
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        dow = (dt.weekday() + 1) % 7  # Sun=0 .. Sat=6

        if dow == 0 and current_week:
            weeks.append(current_week)
            current_week = []
        elif not current_week and dow != 0:
            current_week = [None] * dow

        current_week.append(d)

    if current_week:
        weeks.append(current_week)
    return weeks


def build_svg(weeks: list[list[dict | None]], stats: dict) -> str:
    cols = len(weeks)
    grid_width = cols * CELL
    legend_x = PAD_LEFT + grid_width + 20
    width = legend_x + 30 + len(PALETTE) * (BOX + 3) + 40
    height = PAD_TOP + 7 * CELL + PAD_BOTTOM

    boxes = []
    for w, week in enumerate(weeks):
        for r in range(7):
            day = week[r] if r < len(week) else None
            if day is None:
                continue
            color = PALETTE[min(day["level"], len(PALETTE) - 1)]
            x = PAD_LEFT + w * CELL
            y = PAD_TOP + r * CELL
            delay = (w + r) * 0.012
            boxes.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" '
                f'fill="{color}" class="cell" style="animation-delay:{delay:.3f}s">'
                f'<title>{day["count"]} contributions on {day["date"]}</title>'
                f'</rect>'
            )

    legend_y = PAD_TOP + (7 * CELL) / 2 - BOX / 2
    legend_boxes = [
        f'<rect x="{legend_x + 32 + i * (BOX + 3)}" y="{legend_y}" '
        f'width="{BOX}" height="{BOX}" rx="2" fill="{color}" />'
        for i, color in enumerate(PALETTE)
    ]
    more_x = legend_x + 32 + len(PALETTE) * (BOX + 3) + 6

    total = stats.get("total", 0)
    footer = f"{total:,} contributions in the last year"

    style = """
<style>
  .cell { opacity: 0; transform: translate(-6px, -6px); animation: reveal 0.35s ease-out forwards; }
  @keyframes reveal { to { opacity: 1; transform: translate(0, 0); } }
</style>"""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{style}
{"".join(boxes)}
<text x="{legend_x}" y="{legend_y + BOX}" font-family="{FONT}" font-size="10" fill="#8b949e">Less</text>
{"".join(legend_boxes)}
<text x="{more_x}" y="{legend_y + BOX}" font-family="{FONT}" font-size="10" fill="#8b949e">More</text>
<text x="{PAD_LEFT}" y="{height - 12}" font-family="{FONT}" font-size="11" fill="#c9d1d9">{footer}</text>
</svg>'''


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    days, stats = load_data()
    weeks = to_weeks(days)
    svg = build_svg(weeks, stats)
    Path(out).write_text(svg)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
