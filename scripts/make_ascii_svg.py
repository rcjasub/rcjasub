#!/usr/bin/env python3
"""Convert a prepped grayscale photo into a self-typing monochrome ASCII SVG.

Each row wipes in left-to-right (staggered top to bottom) using SMIL
animation baked into the SVG, so it plays wherever GitHub renders it.

Usage:
    python scripts/make_ascii_svg.py [source-prepped.png] [output.svg]
"""
import sys

from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)

COLS = 100
ROWS = 53

FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.05
PAD = 6
FILL = "#8b949e"  # monochrome, readable on light and dark backgrounds

ROW_STAGGER = 0.045  # seconds between row starts
ROW_DURATION = 0.5  # seconds for a row's wipe-in

DEFAULT_SRC = "source-prepped.png"
DEFAULT_OUT = "ascii-portrait.svg"


def image_to_rows(src_path: str) -> list[str]:
    img = Image.open(src_path).convert("L").resize((COLS, ROWS))
    pixels = img.load()
    rows = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            brightness = pixels[x, y]
            idx = round((255 - brightness) / 255 * (len(RAMP) - 1))
            chars.append(RAMP[idx])
        rows.append("".join(chars))
    return rows


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(rows: list[str]) -> str:
    width = PAD * 2 + COLS * CHAR_W
    height = PAD * 2 + ROWS * CHAR_H

    defs = []
    body = []
    for i, row in enumerate(rows):
        row_width = COLS * CHAR_W
        y = PAD + (i + 1) * CHAR_H - CHAR_H * 0.25
        begin = round(i * ROW_STAGGER, 3)

        clip_id = f"clip{i}"
        clip_anim_id = f"clipAnim{i}"
        cursor_anim_id = f"cursorAnim{i}"

        defs.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{PAD + i * CHAR_H}" width="0" height="{CHAR_H}">'
            f'<animate id="{clip_anim_id}" attributeName="width" '
            f'from="0" to="{row_width}" begin="{begin}s" dur="{ROW_DURATION}s" '
            f'fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1" />'
            f'</rect></clipPath>'
        )

        body.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text x="{PAD}" y="{y}" font-family="ui-monospace, SFMono-Regular, '
            f'Consolas, monospace" font-size="{FONT_SIZE}" fill="{FILL}" '
            f'xml:space="preserve">{escape(row)}</text>'
            f'</g>'
        )
        body.append(
            f'<rect x="0" y="{PAD + i * CHAR_H}" width="{CHAR_W}" height="{CHAR_H * 0.85}" '
            f'fill="{FILL}">'
            f'<animate id="{cursor_anim_id}" attributeName="x" from="0" '
            f'to="{row_width}" begin="{begin}s" dur="{ROW_DURATION}s" fill="freeze" />'
            f'<set attributeName="opacity" to="0" begin="{cursor_anim_id}.end" fill="freeze" />'
            f'</rect>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}" '
        f'height="{height:.1f}" viewBox="0 0 {width:.1f} {height:.1f}">'
        f'<defs>{"".join(defs)}</defs>'
        f'{"".join(body)}'
        f'</svg>'
    )


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT

    rows = image_to_rows(src)
    svg = build_svg(rows)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out}")
