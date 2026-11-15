#!/usr/bin/env python3
"""Draw the illustrative plates used by examples/demo-deck.html.

These are **`[course]` schematics of the skill's own rules**, not measurements: every number
they display is a number this skill states elsewhere, and each caption says so. Nothing here
pretends to be data. The decorative plates (`bg_*.png`) carry no numbers at all.

Usage:
    python3 make_figures.py            # writes the PNGs beside this script, into assets/
    python3 make_figures.py --out DIR

Reference: `references/figures.md` §3 (a schematic needs the tag, its numbers and their source).
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#1F3A5F"
ACCENT = "#B4432F"
GRAY = "#666666"
PALE = "#E8EDF4"


def _save(fig, path, dpi=200):
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote %s" % path)


def fig_cut(out):
    """What the density bar removes: words go down, figure area goes up. Two axes, because
    the two quantities share no units — one axis each, never one axis for both."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 5.2))
    for ax, draft, final, unit, fmt, ratio in (
            (ax1, 5300, 1280, "words per deck", "{:,.0f}", "0.24\u00d7"),
            (ax2, 15, 38, "figure area per slide (%)", "{:.0f}%", "2.5\u00d7")):
        ax.barh([0, 1], [draft, final], 0.52, color=[PALE, INK], edgecolor=[GRAY, INK])
        for y, v in ((0, draft), (1, final)):
            ax.text(v * 1.02, y, fmt.format(v), va="center", ha="left", fontsize=11,
                    color=GRAY if y == 0 else INK)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["ordinary\ndraft", "instructor's\ndeck"], fontsize=9)
        ax.set_xlabel(unit, fontsize=10)
        ax.set_xlim(0, max(draft, final) * 1.22)
        ax.tick_params(labelsize=9)
        ax.set_title(ratio, fontsize=12, color=ACCENT, loc="right")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    _save(fig, os.path.join(out, "fig_cut.png"))


def fig_cover(out):
    """Two slide frames: one with a void band (dashed, labelled), one that covers the page."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0))
    for ax, verdict, defect in ((axes[0], "void 24% — a defect", True),
                                (axes[1], "void 7% — finished", False)):
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 71)
        ax.axis("off")
        ax.add_patch(Rectangle((0, 0), 100, 71, facecolor="white", edgecolor=GRAY, lw=1.2))
        ax.add_patch(Rectangle((4, 40), 92, 6, facecolor=INK, alpha=.85))       # title
        if defect:
            ax.add_patch(Rectangle((4, 8), 44, 26, facecolor=PALE, edgecolor=GRAY))
            ax.add_patch(Rectangle((54, 8), 42, 26, facecolor=PALE, edgecolor=GRAY))
            ax.add_patch(Rectangle((4, 8), 92, 26, fill=False, edgecolor=ACCENT,
                                   lw=1.6, ls=(0, (5, 4))))
            ax.annotate("", xy=(88, 36), xytext=(88, 60),
                        arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1.2))
            ax.text(80, 48, "dead band", color=ACCENT, fontsize=9.5, rotation=90,
                    ha="right", va="center")
        else:
            ax.add_patch(Rectangle((4, 8), 44, 30, facecolor=PALE, edgecolor=GRAY))
            ax.add_patch(Rectangle((54, 8), 42, 30, facecolor=PALE, edgecolor=GRAY))
            for i in range(5):
                ax.add_patch(Rectangle((4, 33.5 - i * 4.0), 30, 1.8, facecolor=GRAY, alpha=.55))
                ax.add_patch(Rectangle((54, 33.5 - i * 4.0), 28, 1.8, facecolor=GRAY, alpha=.45))
        ax.text(50, -7, verdict, ha="center", va="top",
                color=ACCENT if defect else INK, fontsize=11)
    _save(fig, os.path.join(out, "fig_cover.png"))


def fig_types(out):
    """The three type roles, as a stack. No fourth tier exists."""
    fig, ax = plt.subplots(figsize=(5.65, 4.3))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    rows = [(78, 16, "TITLE", "58 px = 43.5 pt", INK),
            (44, 22, "MESSAGE", "32 px = 24 pt", "#2E5C8A"),
            (22, 10, "CREDIT", "16.8 px = 12.6 pt", GRAY)]
    for y, hh, name, size, colour in rows:
        ax.add_patch(Rectangle((6, y), 88, hh, facecolor=colour, alpha=.14, edgecolor=colour))
        ax.text(10, y + hh / 2, name, va="center", fontsize=13, color=colour, weight="bold")
        ax.text(94, y + hh / 2, size, va="center", ha="right", fontsize=10, color=GRAY)
    # the label lives in the gap ABOVE the lowest row, never on top of a size tag
    # the gap between MESSAGE and CREDIT is the message of this figure: label it there
    ax.annotate("", xy=(50, 32.6), xytext=(50, 43.4),
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=1.2, ls=(0, (4, 3))))
    ax.text(52, 38, "nothing in between", color=ACCENT, fontsize=9.2, va="center")
    _save(fig, os.path.join(out, "fig_types.png"))


def _plate(out, path, cmap_name=None, seed=7):
    """A decorative plate: a smooth synthetic field. No data, no axes, no numbers."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, 420)
    y = np.linspace(0, 1, 290)
    xx, yy = np.meshgrid(x, y)
    z = np.zeros_like(xx)
    for _ in range(26):
        cx, cy = rng.random(), rng.random()
        s = 0.04 + rng.random() * 0.12
        a = (rng.random() - 0.35) * 1.6
        z += a * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s))
    z += 0.25 * np.sin(4.2 * xx + 0.7) * np.cos(3.1 * yy)
    cmap = cmap_name or "magma"
    fig = plt.figure(figsize=(11.8, 8.2), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(z, cmap=cmap, origin="lower", interpolation="bicubic")
    ax.axis("off")
    if cmap == "magma":
        ax.set_facecolor("#101a2b")
    fig.savefig(os.path.join(out, path), dpi=100, facecolor="#101a2b" if cmap == "magma" else "white")
    plt.close(fig)
    print("wrote %s" % os.path.join(out, path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "assets"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    fig_cut(args.out)
    fig_cover(args.out)
    fig_types(args.out)
    _plate(args.out, "bg_part.png", seed=7)                    # dark plate: the divider
    _plate(args.out, "bg_title.png", cmap_name="Blues_r", seed=19)  # cool: a 22% wash on white


if __name__ == "__main__":
    main()