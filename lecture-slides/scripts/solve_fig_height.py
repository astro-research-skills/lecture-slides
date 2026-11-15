#!/usr/bin/env python3
"""Solve each figure's `max-height` in the browser, and optionally write it back.

Eyeballed heights are the reason figures end up at 12vh. For every slide with a
`.figcol img` this asks the *rendered* page the only question that has an answer: how tall
may this image be before something in its section crosses the frame? — and binary-searches
it at 4 px granularity. The binding constraint is then one of two, and it says which:

  * **text column** — the image can grow until the text beside it overflows;
  * **width fill**     — the image is already as tall as its column makes it; a larger
    `max-height` is inert, because the browser clamps the width (`layout.md` §7).

Writing back is where two incidents came from, so both are guarded here: elements are
matched **by `src=`**, never by their position among regex matches (§8.10 — a writer that
zips solver output against matches by index breaks on any slide with two figures), and the
write is **section-scoped** through `deck_edit.put`, which re-runs the invariants and refuses
rather than returning a broken document (§8.11). After writing, the rendered heights are
measured again: if none changed, the value was inert and this says so instead of reporting a
success it did not cause.

Usage:
    python3 solve_fig_height.py --deck slides/lectureN/dsh/lectureN.html
    python3 solve_fig_height.py --deck DECK.html --apply --json render/fig_heights.json

Reference: `references/layout.md` §5, §7; `references/qa-gate.md` §2.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck_edit                                                      # noqa: E402
import render_deck                                                    # noqa: E402

SEARCH_JS = r"""
([h]) => {
  const TOL = 2;
  const sec = Reveal.getCurrentSlide();
  const F = document.querySelector('.slides').getBoundingClientRect();
  const im = window.__solver_img;
  if (!im) return {ok: false, why: 'no image'};
  im.style.maxHeight = h + 'px';
  const S = sec.getBoundingClientRect();
  let bad = (S.bottom - F.bottom > TOL) || (S.right - F.right > TOL) || (S.top - F.top < -TOL);
  let worst = Math.round(S.bottom - F.bottom);
  for (const el of sec.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const texts = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim().length);
    if (!texts.length) continue;
    const b = el.getBoundingClientRect();
    if (b.width < 1 && b.height < 1) continue;
    const over = Math.max(F.top - b.top, b.right - F.right, b.bottom - F.bottom, F.left - b.left);
    if (over > TOL) { bad = true; worst = Math.max(worst, Math.round(b.bottom - F.bottom)); }
  }
  const bb = im.getBoundingClientRect();
  return {ok: !bad, disp_h: Math.round(bb.height), disp_w: Math.round(bb.width), worst: worst};
}
"""

PICK_JS = r"""
(i) => {
  Reveal.slide(i);
  const sec = Reveal.getCurrentSlide();
  const imgs = [...sec.querySelectorAll('.figcol img')];
  window.__solver_img = imgs[0] || null;
  const im = window.__solver_img;
  const col = im ? im.closest('.figcol') : null;
  return {n: imgs.length,
          src: im ? (im.getAttribute('src') || '') : '',
          ar: im && im.naturalHeight ? +(im.naturalWidth / im.naturalHeight).toFixed(3) : null,
          col_w: col ? Math.round(col.getBoundingClientRect().width) : null,
          cur: im ? (im.style.maxHeight || '') : ''};
}
"""

NEXT_JS = r"""
() => {
  const sec = Reveal.getCurrentSlide();
  const imgs = [...sec.querySelectorAll('.figcol img')];
  const i = imgs.indexOf(window.__solver_img);
  window.__solver_img = imgs[i + 1] || null;
  const im = window.__solver_img;
  const col = im ? im.closest('.figcol') : null;
  return {n: imgs.length,
          src: im ? (im.getAttribute('src') || '') : '',
          ar: im && im.naturalHeight ? +(im.naturalWidth / im.naturalHeight).toFixed(3) : null,
          col_w: col ? Math.round(col.getBoundingClientRect().width) : null};
}
"""

MEASURE_JS = r"""
() => {
  const out = {};
  for (const im of document.querySelectorAll('.figcol img'))
    out[im.getAttribute('src')] = Math.round(im.getBoundingClientRect().height);
  return out;
}
"""


def solve(page, frame_h, lo=60, step=4):
    """Largest max-height (multiple of `step`) for which the slide does not overflow."""
    page.evaluate(SEARCH_JS, [frame_h + 400])
    if page.evaluate(SEARCH_JS, [lo])["ok"] is False:
        return None, page.evaluate(SEARCH_JS, [lo])
    hi, best = frame_h + 400, lo
    while hi - lo > step:
        mid = (lo + hi) // 2 // step * step
        if mid <= lo:
            break
        r = page.evaluate(SEARCH_JS, [mid])
        if r["ok"]:
            best, lo = mid, mid
        else:
            hi = mid
    return best, page.evaluate(SEARCH_JS, [best])


def set_max_height(tag, h):
    """Rewrite an <img> tag's max-height without ever creating a second style attribute."""
    m = re.search(r'\bstyle\s*=\s*"([^"]*)"', tag)
    if m:
        css = re.sub(r'max-height\s*:\s*[^;"]*;?', '', m.group(1)).strip().strip(';')
        css = (css + ";" if css else "") + "max-height:%dpx" % h
        return tag[:m.start(1)] + css + tag[m.end(1):]
    return tag[:-1].rstrip() + ' style="max-height:%dpx">' % h


def rewrite_section_body(body, src, h):
    """Set max-height on the <img> inside `body` whose src is exactly `src`, by identity."""
    pat = re.compile(r'<img\b[^>]*>')
    hits = 0
    out = body
    for m in list(pat.finditer(body)):
        tag = m.group(0)
        sm = re.search(r'\bsrc\s*=\s*"([^"]*)"', tag)
        if not sm or sm.group(1) != src:
            continue
        out = out[:m.start()] + set_max_height(tag, h) + out[m.end():]
        hits += 1
        break
    return out, hits


def main(argv=None):
    ap = argparse.ArgumentParser(prog="solve_fig_height.py",
                                 description="solve (and optionally write back) figure max-heights")
    ap.add_argument("deck", nargs="?", default=None)
    ap.add_argument("--deck", dest="deck_opt", default=None)
    ap.add_argument("--apply", action="store_true", help="write the solved values into the deck")
    ap.add_argument("--json", dest="jsonout", default=None)
    ap.add_argument("--step", type=int, default=4)
    args = ap.parse_args(argv)
    pos, opt = args.deck, args.deck_opt
    if pos and opt:
        ap.error("give the deck once: positionally or with --deck, not both")
    deck = pos or opt
    if not deck:
        ap.error("a deck path is required (positional, or --deck DECK.html)")
    if not os.path.exists(deck):
        print("no such deck: %s" % deck, file=sys.stderr)
        return 2

    from playwright.sync_api import sync_playwright
    deck_abs = os.path.abspath(deck)
    html = open(deck_abs, encoding="utf-8").read()
    secs = deck_edit.sections(html)
    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1180, "height": 820})
        page.goto("file://" + deck_abs)
        page.wait_for_function("typeof Reveal !== 'undefined' && Reveal.isReady()", timeout=45000)
        page.evaluate("Reveal.configure({transition: 'none', backgroundTransition: 'none'})")
        page.wait_for_timeout(900)
        frame = page.evaluate(SLIDE_JS_FRAME)
        before = {}
        total = page.evaluate("Reveal.getTotalSlides()")
        for i in range(total):
            page.evaluate("Reveal.slide(%d)" % i)
            page.wait_for_timeout(180)
            before.update(page.evaluate(MEASURE_JS))
            info = page.evaluate(PICK_JS, i)
            if not info["n"]:
                continue
            for _ in range(info["n"]):
                cur = page.evaluate("window.__solver_img ? window.__solver_img.getAttribute('src') : ''")
                h, r = solve(page, frame["h"], step=args.step)
                col_w, ar = info["col_w"], info["ar"]
                width_fill = round(col_w / ar) if (col_w and ar) else None
                bound, clamped = "text column", False
                if h is None:
                    bound, h = "cannot fit", 0
                elif width_fill is not None and h > width_fill:
                    # above width-fill every value renders the same; report the smallest one
                    h = int((width_fill + args.step - 1) // args.step * args.step)
                    bound, clamped = "width fill", True
                results.append({"slide": i + 1, "src": cur, "h": h, "ar": ar,
                                "width_fill": width_fill, "bound": bound,
                                "width_clamped": clamped,
                                "disp_h_before": before.get(cur),
                                "disp_h_at_h": r.get("disp_h") if r else None})
                info = page.evaluate(NEXT_JS)
                if not info["src"]:
                    break
        frames_after = dict(before)
        browser.close()

    # ---- write back, section-scoped, by src identity
    applied = 0
    if args.apply:
        for rec in results:
            idx = rec["slide"] - 1
            if idx >= len(secs) or not rec["h"]:
                continue
            body = secs[idx].group(2)
            new_body, hits = rewrite_section_body(body, rec["src"], rec["h"])
            if not hits:
                print("  ! slide %d: no <img src=\"%s\"> in that section — skipped"
                      % (rec["slide"], rec["src"]))
                continue
            if new_body == body:
                continue
            html = deck_edit.put(html, idx + 1, new_body)   # refuses on any invariant break
            applied += 1
        open(deck_abs, "w", encoding="utf-8").write(html)

    # ---- report
    print("deck: %s   frame %dx%d" % (deck_abs, frame["w"], frame["h"]))
    print("\nslide  src                                   h(px)  ar    width-fill  bound")
    for rec in results:
        print("  %2d   %-36s %5s  %-5s %-10s  %s"
              % (rec["slide"], rec["src"][-36:], rec["h"], rec["ar"],
                 rec["width_fill"], rec["bound"]))
    inert = [r for r in results if not r.get("width_clamped")
             and r["disp_h_at_h"] is not None and r["disp_h_before"] == r["disp_h_at_h"]]
    print("\napplied: %d section write(s)" % applied)
    if inert:
        print("inert: %d image(s) keep their rendered height — the value is clamped by column "
              "width, not by the attribute (layout.md §7): slides %s"
              % (len(inert), ", ".join(str(r["slide"]) for r in inert)))
    if args.jsonout:
        os.makedirs(os.path.dirname(os.path.abspath(args.jsonout)) or ".", exist_ok=True)
        json.dump({"deck": deck_abs, "frame": frame, "results": results, "applied": applied},
                  open(args.jsonout, "w", encoding="utf-8"), indent=1)
        print("wrote %s" % args.jsonout)
    return 0


SLIDE_JS_FRAME = "() => { const b = document.querySelector('.slides').getBoundingClientRect();" \
                 " return {w: Math.round(b.width), h: Math.round(b.height)}; }"

if __name__ == "__main__":
    sys.exit(main())