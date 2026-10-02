#!/usr/bin/env python3
"""Render a photo as a pixelated dot-grid SVG (a static take on Aceternity's
PixelatedCanvas: square dots, sample-averaged color, dropout, white tint).

GitHub READMEs can't run canvas/JS, so the dot grid is baked into a PNG,
embedded in the SVG, and revealed top-to-bottom with a SMIL scanline.

Usage:
    python scripts/make_pixel_svg.py [Img/ffr.png] [pixel-portrait.svg]
"""
import base64
import io
import sys

import numpy as np
from PIL import Image

WIDTH, HEIGHT = 400, 500
SCALE = 2  # render at 2x so dots stay crisp on retina screens
CELL_SIZE = 3
DOT_SCALE = 0.9
BACKGROUND = (0, 0, 0)
DROPOUT_STRENGTH = 0.4
TINT_COLOR = (255, 255, 255)
TINT_STRENGTH = 0.2
# near-white source background fades to the canvas background
BG_KNOCKOUT = (0.78, 0.9)  # luminance where fade starts / is fully gone
RADIUS = 12  # rounded-xl
BORDER = "#262626"  # neutral-800

# crop box on the source (x0, y0, x1, y1), as fractions, to fit 4:5
CROP = (0.15, 0.2, 0.95, 0.766)

REVEAL_DURATION = 1.6  # seconds for the scanline to sweep down
SEED = 7

DEFAULT_SRC = "Img/ffr.png"
DEFAULT_OUT = "pixel-portrait.svg"


def crop_to_box(img: Image.Image) -> Image.Image:
    w, h = img.size
    x0, y0, x1, y1 = CROP
    return img.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))


def render_dots(src_path: str) -> Image.Image:
    cols, rows = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
    img = crop_to_box(Image.open(src_path).convert("RGB"))

    # sampleAverage: box-filter each cell down to one color
    colors = np.asarray(img.resize((cols, rows), Image.BOX), dtype=np.float32)
    src_lum = colors.mean(axis=2) / 255
    lo, hi = BG_KNOCKOUT
    opacity = np.clip((hi - src_lum) / (hi - lo), 0, 1)[..., None]
    tint = np.array(TINT_COLOR, dtype=np.float32)
    colors = colors * (1 - TINT_STRENGTH) + tint * TINT_STRENGTH
    colors = colors * opacity + np.array(BACKGROUND, dtype=np.float32) * (1 - opacity)

    # dropout: thin out flat regions, keep edges and detail dense
    lum = colors.mean(axis=2) / 255
    gy, gx = np.gradient(lum)
    edge = np.clip(np.hypot(gx, gy) * 8, 0, 1)
    drop_prob = DROPOUT_STRENGTH * (1 - edge)
    keep = np.random.default_rng(SEED).random((rows, cols)) >= drop_prob
    keep &= opacity[..., 0] > 0

    out = np.zeros((HEIGHT * SCALE, WIDTH * SCALE, 3), dtype=np.uint8)
    out[:] = BACKGROUND
    cell = CELL_SIZE * SCALE
    dot = max(1, round(cell * DOT_SCALE))
    inset = (cell - dot) // 2
    for r in range(rows):
        for c in range(cols):
            if keep[r, c]:
                y, x = r * cell + inset, c * cell + inset
                out[y:y + dot, x:x + dot] = colors[r, c]
    return Image.fromarray(out)


def build_svg(dots: Image.Image) -> str:
    buf = io.BytesIO()
    dots.save(buf, format="PNG", optimize=True)
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    w, h = WIDTH, HEIGHT
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">'
        f'<defs>'
        f'<clipPath id="round"><rect width="{w}" height="{h}" rx="{RADIUS}" /></clipPath>'
        f'<clipPath id="reveal"><rect width="{w}" height="0">'
        f'<animate attributeName="height" from="0" to="{h}" dur="{REVEAL_DURATION}s" '
        f'fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1" />'
        f'</rect></clipPath>'
        f'</defs>'
        f'<g clip-path="url(#round)">'
        f'<rect width="{w}" height="{h}" fill="rgb{BACKGROUND}" />'
        f'<image clip-path="url(#reveal)" width="{w}" height="{h}" '
        f'xlink:href="data:image/png;base64,{data}" />'
        f'<rect width="{w}" height="2" fill="#ffffff" opacity="0.6">'
        f'<animate attributeName="y" from="0" to="{h}" dur="{REVEAL_DURATION}s" '
        f'fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1" />'
        f'<set attributeName="opacity" to="0" begin="{REVEAL_DURATION}s" fill="freeze" />'
        f'</rect>'
        f'</g>'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{RADIUS}" '
        f'fill="none" stroke="{BORDER}" />'
        f'</svg>'
    )


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT

    svg = build_svg(render_dots(src))
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out}")
