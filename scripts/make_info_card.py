#!/usr/bin/env python3
"""Hand-author a neofetch-style info card SVG.

Lines fade and slide in on a short stagger so the card looks like it's
printing next to the portrait. Set STATIC=1 to emit a frozen frame
(all lines already visible) for local Quick Look previews.

Usage:
    python scripts/make_info_card.py [output.svg]
"""
import os
import sys

# Edit these to taste -- placeholders for now.
TITLE = "rcjasub@github"
FIELDS = [
    ("Now", "Software Engineer"),
    ("Prev", "Add your previous role here"),
    ("Stack", "Add your stack here"),
    ("Highlights", "Add a highlight here"),
    ("Highlights", "Add another highlight here"),
]

WIDTH = 490
ROW_H = 30
PAD_X = 22
TITLE_H = 40
FONT = "ui-monospace, SFMono-Regular, Consolas, monospace"

BG = "#0d1117"
BORDER = "#30363d"
TITLE_BG = "#161b22"
LABEL_COLOR = "#58a6ff"
VALUE_COLOR = "#c9d1d9"
DIM_COLOR = "#8b949e"

ROW_STAGGER = 0.12
FADE_DURATION = 0.4

DEFAULT_OUT = "info-card.svg"


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(static: bool) -> str:
    height = TITLE_H + len(FIELDS) * ROW_H + 20

    rows = []
    for i, (label, value) in enumerate(FIELDS):
        y = TITLE_H + i * ROW_H + ROW_H * 0.65
        begin = round(i * ROW_STAGGER, 3)

        if static:
            opacity_attr = ""
            transform = ""
        else:
            opacity_attr = "0"
            transform = f' transform="translate(-12 0)"'

        anim = ""
        if not static:
            anim = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin}s" dur="{FADE_DURATION}s" fill="freeze" />'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-12 0" to="0 0" begin="{begin}s" dur="{FADE_DURATION}s" '
                f'fill="freeze" />'
            )

        opacity = "0" if not static else "1"
        rows.append(
            f'<g opacity="{opacity}"{transform}>'
            f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="13" '
            f'font-weight="600" fill="{LABEL_COLOR}">{escape(label)}</text>'
            f'<text x="{PAD_X + 120}" y="{y}" font-family="{FONT}" font-size="13" '
            f'fill="{VALUE_COLOR}">{escape(value)}</text>'
            f'{anim}'
            f'</g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8" fill="{BG}" stroke="{BORDER}" />
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{TITLE_H}" rx="8" fill="{TITLE_BG}" />
<rect x="0.5" y="{TITLE_H - 8}" width="{WIDTH - 1}" height="8" fill="{TITLE_BG}" />
<circle cx="22" cy="20" r="5" fill="#ff5f56" />
<circle cx="40" cy="20" r="5" fill="#ffbd2e" />
<circle cx="58" cy="20" r="5" fill="#27c93f" />
<text x="{WIDTH / 2}" y="25" font-family="{FONT}" font-size="12" fill="{DIM_COLOR}" text-anchor="middle">{escape(TITLE)}</text>
{"".join(rows)}
</svg>'''


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    static = os.environ.get("STATIC") == "1"

    svg = build_svg(static)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out}")
