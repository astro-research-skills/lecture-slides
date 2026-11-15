#!/usr/bin/env python3
"""Crop a published figure out of a rendered PDF page.

Rendered page PNGs (from `pdftoppm -r 300 -png paper.pdf pg`) are scanned for horizontal
ink bands; the figure is the large band between the running head and the caption paragraph.
`--band auto` takes the tallest band above `--min-h`; `--band N` takes the N-th; explicit
`--y0/--y1/--x0/--x1` override detection. Afterwards, **read the crop back with a vision
model** — the crop is a claim until someone has looked at it (`references/figures.md` §1).

Usage:
    pdftoppm -r 300 -png 0710.3740.pdf /tmp/pg
    python3 crop_fig.py --page /tmp/pg-01.png --out assets/lg_mass.png
    python3 crop_fig.py --page /tmp/pg-01.png --out assets/lg_mass.png --band 1
    python3 crop_fig.py --page /tmp/pg-03.png --out assets/panel.png --y0 120 --y1 900 --x0 300 --x1 1700
"""
import argparse
import os

import numpy as np
from PIL import Image


def bands(mask, min_h=6):
    """Rows holding ink, grouped into (y0, y1) runs at least `min_h` tall."""
    prof = mask.sum(axis=1)
    out, start = [], None
    for i, v in enumerate(prof):
        if v > 0 and start is None:
            start = i
        elif v == 0 and start is not None:
            if i - start >= min_h:
                out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(prof)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="crop_fig.py",
                                 description="crop the figure out of a rendered PDF page")
    ap.add_argument("--page", required=True, help="rendered page PNG (300-400 dpi)")
    ap.add_argument("--out", required=True, help="output PNG")
    ap.add_argument("--band", default="auto", help="'auto' (tallest band >= --min-h) or a band index")
    ap.add_argument("--min-h", type=int, default=250, help="ignore bands shorter than this (px)")
    ap.add_argument("--pad", type=int, default=14, help="white padding kept around the crop (px)")
    for k in ("y0", "y1", "x0", "x1"):
        ap.add_argument("--" + k, type=int, default=None)
    args = ap.parse_args(argv)

    if not os.path.exists(args.page):
        print("no such page: %s" % args.page, file=__import__("sys").stderr)
        return 2
    im = Image.open(args.page).convert("RGB")
    ink = np.asarray(im.convert("L")) < 240
    H, W = ink.shape

    y0, y1 = args.y0, args.y1
    if y0 is None or y1 is None:
        bs = bands(ink)
        big = [b for b in bs if b[1] - b[0] >= args.min_h]
        if not big:
            print("no ink band >= %d px; bands seen: %s" % (args.min_h, bs), file=__import__("sys").stderr)
            return 1
        if args.band == "auto":
            y0, y1 = max(big, key=lambda b: b[1] - b[0])
        else:
            y0, y1 = big[int(args.band)]
        print("bands=%s\nchosen y=(%d,%d) h=%d" % (bs, y0, y1, y1 - y0))

    x0, x1 = args.x0, args.x1
    if x0 is None or x1 is None:
        cols = np.where(ink[y0:y1, :].any(axis=0))[0]
        if not len(cols):
            print("the chosen rows hold no ink", file=__import__("sys").stderr)
            return 1
        x0, x1 = int(cols.min()), int(cols.max()) + 1

    x0 = max(0, x0 - args.pad)
    y0 = max(0, y0 - args.pad)
    x1 = min(W, x1 + args.pad)
    y1 = min(H, y1 + args.pad)
    crop = im.crop((x0, y0, x1, y1))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    crop.save(args.out)
    print("wrote %s: %dx%d px, box=(%d,%d,%d,%d)"
          % (args.out, crop.size[0], crop.size[1], x0, y0, x1, y1))
    print("now read the crop back with a vision model: frame, axis titles, ticks, legends "
          "inside; no caption prose (figures.md §1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())