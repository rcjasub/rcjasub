#!/usr/bin/env python3
"""Prep a source photo for ASCII conversion: cut out the background,
boost local contrast, and composite onto white.

Usage:
    python scripts/prep_photo.py <source-photo> [output-path]
"""
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

DEFAULT_OUTPUT = "source-prepped.png"
CROP_MARGIN = 0.08  # fraction of subject size to pad on each side


def prep_photo(src_path: str, out_path: str = DEFAULT_OUTPUT) -> None:
    src_bytes = Path(src_path).read_bytes()
    cutout_bytes = remove(src_bytes)
    cutout = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")

    alpha_mask = cutout.getchannel("A").point(lambda a: 255 if a > 10 else 0)
    bbox = alpha_mask.getbbox()
    if bbox:
        x0, y0, x1, y1 = bbox
        mx = int((x1 - x0) * CROP_MARGIN)
        my = int((y1 - y0) * CROP_MARGIN)
        x0, y0 = max(0, x0 - mx), max(0, y0 - my)
        x1, y1 = min(cutout.width, x1 + mx), min(cutout.height, y1 + my)
        cutout = cutout.crop((x0, y0, x1, y1))

    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, cutout).convert("L")

    gray = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    Image.fromarray(contrasted).save(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: prep_photo.py <source-photo> [output-path]")
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT
    prep_photo(sys.argv[1], out)
