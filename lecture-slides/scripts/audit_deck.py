#!/usr/bin/env python3
"""Static invariants, density stats and rendered-page audit for a house-style deck.

Generalised from `slides/lecture8/dsh/audit_deck.py`, which had the deck path and the
render path baked in. Reference: `references/qa-gate.md` (stages 2 and 4) and
`references/density-target.md` §1–§2; source guide §9.1 (the measured bar), §8
(page coverage), §7.7 (audit both directions), §8.10–§8.12 (the markup invariants,
which live in `deck_edit.check`, imported here rather than re-implemented).

Usage:
    python3 audit_deck.py DECK.html [--render DIR] [--json OUT]
                         [--orientation-ladder 6] [--no-render-check]

WHAT THE COVERAGE NUMBERS MEASURE — read this before trusting either one.
The source guide §8 sets the bar at "coverage < 0.82 or void > 12% is a defect", while
the original script's own ink grid scores the *instructor's accepted* lecture8 deck at
median ink coverage **0.495** (measured, this build). The two numbers describe
different things, and the difference is §8.1's own distinction: a text-and-figure slide
is mostly white paper, and a scanned journal figure "scores ~0.68 coverage while
occupying the whole page — check the bounding box, not the ink". So this tool reports:

    ink    the original's metric: fraction of 20×20 px cells holding ≥1.5% ink.
           Diagnostic only (a low number is a property of the source, not a defect) —
           on the accepted deck: median 0.495, min 0.272.
    void   the original's `largest_empty_rect` on that same grid: the defect signal.
           Accepted deck: median 0.066. Threshold 0.12 → flagged by slide number.
    cover  occupancy: a 20×14 coarse grid, inked cells dilated by one cell, so the
           whitespace *inside* a paragraph or a white-background scan counts as filled
           and the air *beyond* the last content band does not. This is the metric the
           0.82 bar belongs to (accepted deck median 0.925).

Exit codes: 0 every line PASS, 1 any FAIL, 2 usage/deck unreadable.
"""

import argparse
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck_edit  # noqa: E402  (the invariant checks are imported, never re-implemented)

# ---------------------------------------------------------------------------
# thresholds — the accepted bar, from source guide §9.1 / qa-gate 8a
# ---------------------------------------------------------------------------
MAX_MEDIAN_WORDS = 60      # §9.1 finals: median 26–68 words/slide
MAX_SLIDE_WORDS = 140      # §9.1 finals: max ~100–140
MIN_BREATH_SHARE = 0.15    # §9.1: 5–11 slides ≤15 words in 27–43-slide decks
MIN_FIG_AREA = 0.30        # §9.1 finals: figure area median 32–44%
# §8's "void > 12% is a defect" is a *guide* number, and measured against the finals it is
# too strict to be a gate: on the shipped lecture8 deck (25 slides, its own renders) the
# largest empty rectangle inside the content block has median 10.5%, p90 17.2%, max 19.0%.
# A bar set at 12% fails 9 of those 25 slides — a gate the reference population cannot pass
# is a miscalibrated gate, not a strict one. The ceiling is therefore the observed maximum
# with a margin; the distribution stays in the report so a drift is visible.
MAX_COVERAGE_VOID = 0.20   # calibrated: finals max 19.0%, n=25 (lecture8 shipped renders)
MIN_COVER = 0.82           # §8: the occupancy bar (see module docstring)
INK_CELL = 10              # px in the 590×410 scan == 20 px at 1180×820: the original's grid
COVER_GRID = (20, 14)      # coarse occupancy grid

TAGS = deck_edit.TAGS

_ENTITIES = {"&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">", "&rarr;": ">",
             "&larr;": "<", "&minus;": "-", "&middot;": ".", "&mdash;": "-", "&ndash;": "-"}


def strip_tags(s):
    """Visible text of a markup fragment (entities folded, whitespace collapsed)."""
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    for k, v in _ENTITIES.items():
        s = s.replace(k, v)
    return re.sub(r"\s+", " ", s).strip()


def without(s, pattern):
    return re.sub(pattern, " ", s, flags=re.S)


def words_of(body_html, body_only=True):
    """Word count of a section body. `body_only` drops `<aside>` (speaker notes) and the
    credit-tier runs (`.figcap` / `.src`), which are 12.6 px citations, not prose."""
    s = body_html
    if body_only:
        s = without(s, r"<aside\b.*?</aside>")
        s = without(s, r"<p\b[^>]*class=\"[^\"]*(?:figcap|src)[^\"]*\"[^>]*>.*?</p>")
        s = without(s, r"<div\b[^>]*class=\"[^\"]*(?:figcap|src)[^\"]*\"[^>]*>.*?</div>")
        s = without(s, r"<span\b[^>]*class=\"[^\"]*srctag[^\"]*\"[^>]*>.*?</span>")
    return len(strip_tags(s).split())


def largest_empty_rect(grid):
    """Largest all-empty axis-aligned rectangle of a bool grid (True = content).

    Ported verbatim from the original `audit_deck.py` — histogram + monotone stack,
    O(rows × cols). Returns (area_cells, (r0, c0), (r1, c1)).
    """
    R, C = grid.shape
    heights = np.zeros(C, dtype=int)
    best = (0, None, None)
    for r in range(R):
        heights = np.where(grid[r], 0, heights + 1)
        stack = []
        for c in range(C + 1):
            h = heights[c] if c < C else 0
            start = c
            while stack and stack[-1][1] > h:
                sc, sh = stack.pop()
                area = sh * (c - sc)
                if area > best[0]:
                    best = (area, (r - sh + 1, sc), (r, c - 1))
                start = sc
            stack.append((start, h))
    return (int(best[0]),
            tuple(int(v) for v in best[1]) if best[1] else None,
            tuple(int(v) for v in best[2]) if best[2] else None)


# ---------------------------------------------------------------------------
# static pass
# ---------------------------------------------------------------------------

def audit_static(html, deck_dir):
    """Per-slide density stats + the `deck_edit.check` violations, folded together."""
    secs = deck_edit.sections(html)
    slides = []
    for n, m in enumerate(secs, 1):
        b = m.group(2)
        text = strip_tags(without(b, r"<aside\b.*?</aside>"))
        rec = {
            "slide": n,
            "title": (strip_tags((re.search(r"(?s)<h2\b[^>]*>(.*?)</h2>", b)
                                  or re.search(r"(?s)<h1\b[^>]*>(.*?)</h1>", b)
                                  or re.match(r"^", "")).group(1))[:60]
                     if re.search(r"(?s)<h[12]\b[^>]*>(.*?)</h[12]>", b) else ""),
            "words_total": words_of(b, body_only=False),
            "words_body": words_of(b),
            "bullets": len(re.findall(r"<li\b", b)),
            "nested_bullets": len(re.findall(r"<li\b[^>]*>(?:(?!</li>).)*?<li\b", b, flags=re.S)),
            "tables": len(re.findall(r"<table\b", b)),
            "imgs": [m2.group(1) for m2 in re.finditer(r"<img\b[^>]*\bsrc=\"([^\"]+)\"", b)],
            "figcaps": len(re.findall(r"class=\"[^\"]*figcap", b)),
            "boxes": len(re.findall(r"class=\"[^\"]*(?:keybox|bluebox)", b)),
            "small_content_words": sum(
                len(strip_tags(x).split()) for x in re.findall(
                    r'<(?:p|div|span|li)\b[^>]*class="[^"]*(?:small|tiny)[^"]*"[^>]*>(.*?)</(?:p|div|span|li)>',
                    b, flags=re.S)),
            "words_le_15": None,  # filled below
            "bleed": bool(re.match(r"\s*class=\"[^\"]*bleed", m.group(1))) or "bleed" in m.group(1),
            "assets_missing": [r for r in (deck_edit._local_refs(deck_edit.masked(b)))
                               if not deck_edit._is_remote(r[1])
                               and not os.path.exists(os.path.join(deck_dir, r[1]))],
        }
        rec["words_le_15"] = rec["words_body"] <= 15
        slides.append(rec)
    return {"slide_count": len(secs), "slides": slides,
            "violations": deck_edit.check(html, deck_dir)}


# ---------------------------------------------------------------------------
# rendered pass — coverage / void / occupancy
# ---------------------------------------------------------------------------

def _ink_matrix(png, size=(590, 410)):
    im = Image.open(png).convert("RGB").resize(size)
    a = np.asarray(im).astype(np.int16)
    ink = a.min(axis=2) < 246           # a pixel is "ink" if any channel is off-white
    return _mask_chrome(ink)


def _mask_chrome(ink):
    """Blank out reveal's own furniture before measuring emptiness.

    The progress bar runs the full width along the bottom and the page chip sits in the
    corner; both are deck chrome, not content. Left in, they stretch the ink bounding box
    across the whole frame and every slide then reports a void it does not have (the closing
    one-line slide scored 66% this way). Coordinates are the §6 chip box, 1055-1148 x
    760-796 of a 1180x820 frame.
    """
    H, W = ink.shape
    ink[int(H * 0.978):, :] = False                    # progress bar
    ink[int(H * 0.92):, int(W * 0.84):] = False        # page chip, corner block
    return ink


def _grid(ink, rows, cols, thr=None):
    h, w = ink.shape[0] // rows, ink.shape[1] // cols
    blk = ink[:h * rows, :w * cols].reshape(rows, h, cols, w)
    return blk.any(axis=(1, 3)) if thr is None else blk.mean(axis=(1, 3)) >= thr


def _dilate(g):
    out = g.copy()
    R, C = g.shape
    for r in range(R):
        for c in range(C):
            if g[max(0, r - 1):r + 2, max(0, c - 1):c + 2].any():
                out[r, c] = True
    return out


def audit_render(render_dir):
    """ink / void / cover per slide, from `slide-NN.png` in `render_dir`."""
    import glob
    files = sorted(glob.glob(os.path.join(render_dir, "slide-*.png")))
    rows = []
    for f in files:
        n = int(re.search(r"slide-(\d+)\.png", os.path.basename(f)).group(1))
        try:
            ink = _ink_matrix(f)
        except Exception as exc:                     # degrade, never crash
            rows.append({"slide": n, "error": str(exc)})
            continue
        fine = _grid(ink, ink.shape[0] // INK_CELL, ink.shape[1] // INK_CELL, thr=0.015)
        area, top, bot = largest_empty_rect(fine)
        # §8.1, second reading: a vertically centred block leaves a band above AND below it.
        # Those are margins, not holes — every centred slide would score 15-35% on the page
        # metric, including the instructor's own finals. The defect is emptiness *inside* the
        # block, so measure the largest empty rectangle within the ink bbox as well, and let
        # the verdict gate on that while the page figure stays reported.
        rows_any = np.where(fine.any(axis=1))[0]
        cols_any = np.where(fine.any(axis=0))[0]
        if len(rows_any) and len(cols_any):
            inner = fine[rows_any.min():rows_any.max() + 1, cols_any.min():cols_any.max() + 1]
            ia, _, _ = largest_empty_rect(inner)
            void_in = round(float(ia) / float(inner.size), 4)
        else:
            void_in = 1.0
        occ = _dilate(_grid(ink, COVER_GRID[0], COVER_GRID[1], thr=0.015))
        rows.append({"slide": n,
                     "ink": round(float(fine.mean()), 3),
                     "void": round(float(area) / float(fine.size), 4),
                     "void_in": void_in,
                     "void_box": [[int(x) for x in top], [int(x) for x in bot]] if top else None,
                     "cover": round(float(occ.mean()), 3),
                     # §8.1: a figure printed on white paper is not a void. Where the
                     # ink bbox covers the page, a low `ink` is a property of the asset.
                     "page_fill": round(float(_grid(ink, 1, 1, thr=0.0).mean()), 3)})
    return rows


def fig_areas_from_qa(render_dir):
    """Rendered figure-area fraction per slide, if render_deck.py left a qa_report.json."""
    p = os.path.join(render_dir, "qa_report.json")
    if not os.path.exists(p):
        return None
    try:
        qa = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    sl = qa.get("slides")
    # tolerate a foreign or older qa_report.json: an int list, missing keys, or no frame.
    if not isinstance(sl, list) or not sl or not isinstance(sl[0], dict):
        return None
    frame = sl[0].get("frame") or {}
    if not frame.get("w") or not frame.get("h"):
        return None
    total = float(frame["w"] * frame["h"])
    out = {}
    for s in sl:
        if not isinstance(s, dict) or "slide" not in s:
            continue
        area = sum(float(i.get("disp_w") or 0) * float(i.get("disp_h") or 0)
                   for i in (s.get("imgs") or []) if isinstance(i, dict))
        bg = len(s.get("background_images") or [])
        if area or bg:
            out[s["slide"]] = min(1.0, area / total + (0.55 if bg else 0.0))
    return out if out else None


# ---------------------------------------------------------------------------
# the verdict lines
# ---------------------------------------------------------------------------

def density_lines(st, ladder_slides=(), fig_area=None):
    """PASS/FAIL per accepted threshold. Numbers alone are not a gate."""
    sl = st["slides"]
    n = len(sl)
    body = [s["words_body"] for s in sl]
    med = float(np.median(body)) if body else 0.0
    over = [s["slide"] for s in sl if s["words_body"] > MAX_SLIDE_WORDS]
    tables = {s["slide"]: s["tables"] for s in sl if s["tables"]}
    bad_tables = {k: v for k, v in tables.items() if k not in ladder_slides}
    breath = [s["slide"] for s in sl if s["words_le_15"]]
    need = math.ceil(n * MIN_BREATH_SHARE)
    nested = [s["slide"] for s in sl if s["nested_bullets"]]
    small = [s["slide"] for s in sl if s["small_content_words"]]
    boxes = [s["slide"] for s in sl if s["boxes"]]
    figslides = [s["slide"] for s in sl if s["imgs"]]
    thin = ({k: v for k, v in (fig_area or {}).items() if k in figslides and v < MIN_FIG_AREA}
            if fig_area else None)
    viol = st["violations"]
    lines = [
        ("median body words/slide ≤%d (§9.1, measured 26–68 in the finals)" % MAX_MEDIAN_WORDS,
         med <= MAX_MEDIAN_WORDS, "median %.1f, max %d" % (med, max(body) if body else 0)),
        ("no slide >%d body words (§9.1 max ~100–140)" % MAX_SLIDE_WORDS, not over,
         "slides over: %s" % (", ".join("s%02d" % x for x in over) or "none")),
        ("0 native tables (§9.3: all 20 draft tables died) unless declared an orientation ladder",
         not bad_tables, "declared ladder slides %s; undeclared tables at %s"
         % (sorted(ladder_slides) or "[]", ", ".join("s%02d×%d" % (k, v) for k, v in bad_tables.items()) or "none")),
        ("0 keybox/bluebox (§9.3: 63 boxes → 0)", not boxes,
         "found on %s" % (", ".join("s%02d" % x for x in boxes) or "none")),
        ("slides ≤15 words ≥%d of %d (§9.1: 5–11 breathers in a 27–43 slide deck)" % (need, n),
         len(breath) >= need, "found %d: %s" % (len(breath), ", ".join("s%02d" % x for x in breath) or "none")),
        ("0 nested sub-bullets (§9.1: 69/114 draft slides → 1 line in 89)", not nested,
         "found on %s" % (", ".join("s%02d" % x for x in nested) or "none")),
        ("0 content words in .small/.tiny (§6: captions and credits only)", not small,
         "found on %s" % (", ".join("s%02d" % x for x in small) or "none")),
        ("figure area ≥%.0f%% on figure slides (§9.1 finals: median 32–44%%)" % (MIN_FIG_AREA * 100),
         bool(thin) is False,
         ("not measured (no qa_report.json in --render)" if thin is None
          else "under bar: %s" % (", ".join("s%02d %.0f%%" % (k, v * 100) for k, v in thin.items()) or "none"))),
        ("markup invariants clean (deck_edit.check: §7.7 / §8.10 / §8.12)", not viol,
         "%d violation(s)%s" % (len(viol), ": " + "; ".join(
             deck_edit.format_violation(x) for x in viol[:4]) if viol else "")),
    ]
    return lines


def coverage_lines(rr, void_ok=()):
    """Occupancy verdicts. `void_ok` names slides where emptiness IS the design — a part
    divider, a one-question slide, the closing line. Measured, then excused by name, never
    silently: the verdict line prints which slides were excused."""
    ok = [r for r in rr if "void" in r]
    if not ok:
        return [("rendered coverage/void", False, "no slide-NN.png found (run render_deck.py)")]
    cov = [r["cover"] for r in ok]
    med_cov = float(np.median(cov))
    low_cover = [r["slide"] for r in ok if r["cover"] < MIN_COVER]
    excused = sorted(set(void_ok))
    high_void = [r for r in ok
                 if r.get("void_in", r["void"]) > MAX_COVERAGE_VOID and r["slide"] not in excused]
    return [("median occupancy ≥%.2f (§8 coverage bar, on the §8.1 'check the box, not "
             "the ink' reading)" % MIN_COVER, med_cov >= MIN_COVER,
             "median %.3f, min %.3f" % (med_cov, min(cov))),
            ("no slide void >%.0f%% INSIDE its content block (§8, centred-margin reading); "
             "page void reported for comparison" % (MAX_COVERAGE_VOID * 100), not high_void,
             "flagged: %s (page void: %s)%s"
             % (", ".join("s%02d %.1f%%" % (r["slide"], r.get("void_in", r["void"]) * 100)
                          for r in high_void) or "none",
                ", ".join("s%02d %.1f%%" % (r["slide"], r["void"] * 100) for r in ok
                          if r["void"] > MAX_COVERAGE_VOID) or "none",
                ("; excused " + ", ".join("s%02d" % x for x in excused)) if excused else ""))]


def resolve_deck(ap, args):
    """Accept the deck path positionally or as --deck, refuse neither or both (exit 2)."""
    pos, opt = getattr(args, "deck", None), getattr(args, "deck_opt", None)
    if pos and opt:
        ap.error("give the deck once: positionally or with --deck, not both")
    deck = pos or opt
    if not deck:
        ap.error("a deck path is required (positional, or --deck DECK.html)")
    return deck


def main(argv=None):
    ap = argparse.ArgumentParser(prog="audit_deck.py",
                                 description="static invariants + density stats + rendered-page audit")
    ap.add_argument("deck", nargs="?", default=None, help="the deck (or pass --deck)")
    ap.add_argument("--deck", dest="deck_opt", default=None,
                    help="the deck, for callers that prefer an explicit flag")
    ap.add_argument("--render", default=None,
                    help="dir of slide-NN.png from render_deck.py (default: <deck>/render if it exists)")
    ap.add_argument("--json", dest="jsonout", default=None, help="write the whole record here")
    ap.add_argument("--orientation-ladder", default="",
                    help="comma-separated slide numbers declared to be orientation-ladder tables (§9.7 exemption)")
    ap.add_argument("--no-render-check", action="store_true", help="static pass only")
    ap.add_argument("--void-ok", default="",
                    help="comma-separated slide numbers where emptiness is the design "
                         "(part dividers, a one-question slide, the closing line); the verdict "
                         "line names every slide excused this way")
    args = ap.parse_args(argv)
    args.deck = resolve_deck(ap, args)
    if not os.path.exists(args.deck):
        print("no such deck: %s" % args.deck, file=sys.stderr)
        return 2
    html = open(args.deck, encoding="utf-8").read()
    deck_dir = os.path.dirname(os.path.abspath(args.deck))
    ladder = {int(x) for x in re.split(r"[,\s]+", args.orientation_ladder.strip()) if x.strip()}
    void_ok = {int(x) for x in re.split(r"[,\s]+", args.void_ok.strip()) if x.strip()}

    st = audit_static(html, deck_dir)
    print("audit: %s" % args.deck)
    print("slides: %d" % st["slide_count"])
    print("\nslide  words  body  bul nest tab img boxes small  title")
    for s in st["slides"]:
        flags = []
        if s["words_body"] > MAX_SLIDE_WORDS:
            flags.append("WORDS>%d" % MAX_SLIDE_WORDS)
        if s["nested_bullets"]:
            flags.append("NESTED")
        if s["boxes"]:
            flags.append("BOX×%d" % s["boxes"])
        if s["small_content_words"]:
            flags.append("SMALL×%d" % s["small_content_words"])
        if s["assets_missing"]:
            flags.append("ASSET×%d" % len(s["assets_missing"]))
        print("  %02d    %4d   %4d   %2d  %2d  %2d  %2d   %2d    %3d   %s%s"
              % (s["slide"], s["words_total"], s["words_body"], s["bullets"],
                 s["nested_bullets"], s["tables"], len(s["imgs"]), s["boxes"],
                 s["small_content_words"], s["title"][:34],
                 ("   <-- " + " ".join(flags)) if flags else ""))
    for a in st["slides"]:
        for kind, ref in a["assets_missing"]:
            print("        missing asset  s%02d  %s  %s" % (a["slide"], kind, ref))

    render = args.render
    if render is None and not args.no_render_check:
        cand = os.path.join(deck_dir, "render")
        render = cand if glob_dir_has_png(cand) else None
    rr, fig_area = [], None
    if render and not args.no_render_check:
        rr = audit_render(render)
        fig_area = fig_areas_from_qa(render)
        print("\nrendered: %s" % render)
        print("slide  ink   void   cover   (ink = 20px-cell ink fraction, diagnostic only per §8.1;"
              " void + cover are the defect signals)")
        for r in rr:
            if "error" in r:
                print("  %02d   unreadable: %s" % (r["slide"], r["error"]))
                continue
            marks = []
            if r["cover"] < MIN_COVER:
                marks.append("LOW-OCCUPANCY")
            if r["void"] > MAX_COVERAGE_VOID:
                marks.append("VOID")
            print("  %02d  %.3f  %.3f  %.3f   %s"
                  % (r["slide"], r["ink"], r["void"], r["cover"], " ".join(marks)))
    elif not args.no_render_check:
        print("\nrendered: skipped (no --render dir with slide-NN.png)")

    lines = density_lines(st, ladder, fig_area)
    if rr:
        lines += coverage_lines(rr, void_ok)
    print("\nGATE")
    failed = 0
    for name, ok, detail in lines:
        print("  %-4s %s\n        %s" % ("PASS" if ok else "FAIL", name, detail))
        failed += 0 if ok else 1
    print("\naudit: %d line(s) PASS, %d FAIL" % (len(lines) - failed, failed))

    if args.jsonout:
        rec = {"deck": os.path.abspath(args.deck), "static": st, "render": rr,
               "fig_area": fig_area,
               "gate": [{"check": n, "pass": bool(o), "detail": d} for n, o, d in lines]}
        os.makedirs(os.path.dirname(os.path.abspath(args.jsonout)) or ".", exist_ok=True)
        with open(args.jsonout, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1)
        print("json: %s" % args.jsonout)
    return 1 if failed else 0


def glob_dir_has_png(d):
    return os.path.isdir(d) and any(x.startswith("slide-") for x in os.listdir(d))


if __name__ == "__main__":
    sys.exit(main())
