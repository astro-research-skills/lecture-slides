#!/usr/bin/env python3
"""Rasterise a house-style reveal.js deck and run the **rendered** gate on it.

Generalised from `slides/lecture8/dsh/render_slides.py`, which had
`BASE = dirname(__file__)` and the deck name baked in. Reference:
`references/qa-gate.md` (staged gate, stage 3) and `references/layout.md` §B;
the overflow rule itself is source guide §10.11, the column diagnostic is §8.3.

What it does per slide, after `Reveal.isReady()` with `transition:'none'`:
  screenshot `slide-NN.png`, then collect console/page errors, broken images,
  overflow, rendered image sizes, and figure-column vs text-column heights.

The two defects this fixes in the original:

1. §10.11 — the original overflow check iterated a hand-written tag list
   (`p,li,h1,h2,h3,span,table,.figcap`). The house take-home line is `div.take`,
   whose only text sits inside a `<b>`, so neither the div nor the bold was ever
   measured: five slides pushed their take-away past the bottom frame while the
   gate reported **zero overflows**. Here: walk `section.querySelectorAll('*')`
   and keep every element with a *direct text node*.
2. §10.11/§6 — the original compared element rects to the slide frame only, which
   is the right box but the wrong *set*: nothing measured the section's own box,
   so an image (not text) that pushes the slide past the frame was invisible.
   Both signals are reported now, plus background images (`data-background-image`
   and any `url()` the browser computed for an element or its ::before/::after),
   which the original never looked at at all.

Measured, not assumed: under reveal 4.6.1 a `<section>` is content-sized, so a
section box never escapes its own children — when content overflows, the SECTION
grows past the frame. The frame (`.slides`'s rect, 1133×787 at 1180×820 / margin
0.04) is therefore the authority for elements; the section's escape is a second,
complementary signal.

Usage:
    python3 render_deck.py DECK.html [--out DIR] [--width 1180] [--height 820] [--strict]

`--out` defaults to `<deck dir>/render`. Exit: 1 when console errors, broken
images or overflow slides are non-zero AND `--strict` was passed; otherwise 0
with the summary always printed. Missing assets are reported, never fatal.
"""

import argparse
import json
import os
import re
import sys
import glob

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("playwright is required: pip install playwright && playwright install chromium",
          file=sys.stderr)
    sys.exit(2)

SLIDE_JS = r"""
() => {
  const TOL = 2;
  const sec = Reveal.getCurrentSlide();
  const F = document.querySelector('.slides').getBoundingClientRect();
  const S = sec.getBoundingClientRect();
  const box = b => ({top: Math.round(b.top), left: Math.round(b.left),
                     right: Math.round(b.right), bottom: Math.round(b.bottom),
                     w: Math.round(b.width), h: Math.round(b.height)});
  const over = b => ({                        // px beyond each edge of the frame
    top: Math.round(F.top - b.top), right: Math.round(b.right - F.right),
    bottom: Math.round(b.bottom - F.bottom), left: Math.round(F.left - b.left)});
  const out = {frame: box(F), section: box(S), section_over: over(S),
               overflows: [], imgs: [], bgs: [], columns: [], chip: []};

  // ---- every element that holds a direct text node (§10.11) ------------------
  for (const el of sec.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) continue;
    el.__fill = (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent')
                || cs.backgroundImage !== 'none';
    const texts = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim().length);
    if (!texts.length) continue;
    const b = el.getBoundingClientRect();
    if (b.width < 1 && b.height < 1) continue;
    const o = over(b);
    if (Math.max(o.top, o.right, o.bottom, o.left) > TOL) {
      out.overflows.push({tag: el.tagName.toLowerCase(),
                          cls: (el.className || '').toString().trim().slice(0, 40),
                          text: (el.innerText || texts[0].textContent).trim().replace(/\s+/g, ' ').slice(0, 60),
                          over: o, rect: box(b)});
    }
    // §6 known blind spot: the slide-number chip owns x 1055-1148, y 760-796
    // §6: the hazard is a FILL reaching the chip, not glyphs — text is excluded here
    const chip = {left: F.left + 1055 * (F.width / 1180), right: F.left + 1148 * (F.width / 1180),
                  top: F.top + 760 * (F.height / 820), bottom: F.top + 796 * (F.height / 820)};
    if (el.__fill && b.bottom > chip.top && b.top < chip.bottom && b.right > chip.left && b.left < chip.right)
      out.chip.push({tag: el.tagName.toLowerCase(), cls: (el.className || '').toString().slice(0, 30),
                     text: (el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 40)});
  }

  // ---- rendered image sizes --------------------------------------------------
  sec.querySelectorAll('img').forEach(im => {
    const b = im.getBoundingClientRect();
    out.imgs.push({src: im.getAttribute('src') || '', ok: im.complete && im.naturalWidth > 0,
                   natural_w: im.naturalWidth, natural_h: im.naturalHeight,
                   disp_w: Math.round(b.width), disp_h: Math.round(b.height),
                   ar: im.naturalHeight ? +(im.naturalWidth / im.naturalHeight).toFixed(3) : null,
                   complete: im.complete});
  });

  // ---- every background image the browser actually computed -------------------
  const urls = new Set();
  const attr = sec.getAttribute('data-background-image');
  if (attr) attr.split(',').forEach(u => urls.add(u.trim()));
  for (const el of [sec, ...sec.querySelectorAll('*')])
    for (const pe of ['', '::before', '::after'])
      for (const m of (getComputedStyle(el, pe || null).backgroundImage || '')
             .matchAll(/url\(["']?([^"')]+)["']?\)/g))
        urls.add(m[1]);
  out.bgs = [...urls].filter(Boolean);

  // ---- figure column vs its sibling text column (§8.3) -----------------------
  for (const cols of sec.querySelectorAll('.cols, .underrow')) {
    const kids = [...cols.children];
    if (kids.length < 2) continue;
    const fig = kids.find(k => k.querySelector('img'));
    const txt = kids.find(k => k !== fig);
    if (!fig || !txt) continue;
    out.columns.push({fig_cls: (fig.className || '').toString().trim().slice(0, 30),
                      fig_h: Math.round(fig.getBoundingClientRect().height),
                      text_h: Math.round(txt.getBoundingClientRect().height),
                      gap: Math.round(txt.getBoundingClientRect().height - fig.getBoundingClientRect().height)});
  }
  return out;
}
"""

PROBE_JS = r"""
async (urls) => {
  const load = u => new Promise(res => {
    const im = new Image();
    im.onload = () => res({url: u, ok: im.naturalWidth > 0, w: im.naturalWidth});
    im.onerror = () => res({url: u, ok: false, w: 0});
    im.src = u;
    setTimeout(() => res({url: u, ok: im.naturalWidth > 0, w: im.naturalWidth, timeout: true}), 4000);
  });
  return Promise.all(urls.map(load));
}
"""


def render(deck, out, width=1180, height=820):
    """Rasterise + measure `deck`; returns the qa record (see qa_report.json)."""
    deck = os.path.abspath(deck)
    out = os.path.abspath(out)
    os.makedirs(out, exist_ok=True)
    for f in (glob.glob(os.path.join(out, "slide-*.png"))
              + glob.glob(os.path.join(out, "montage.png"))):
        os.remove(f)   # only files this script owns; never the caller's other artefacts

    qa = {"deck": deck, "viewport": [width, height], "slides": [],
          "console_errors": [], "broken_images": [], "overflow_slides": [],
          "background_images": [], "load_error": None}
    # a validator that only runs when the page loads is a validator that never fails
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.on("console", lambda m: qa["console_errors"].append("console: " + m.text)
                if m.type == "error" else None)
        page.on("pageerror", lambda e: qa["console_errors"].append("pageerror: " + str(e)))
        try:
            page.goto("file://" + deck)
            page.wait_for_function("typeof Reveal !== 'undefined' && Reveal.isReady()", timeout=45000)
            # `transition:'none'` does NOT cover background images: reveal fades those on
            # their own clock (`backgroundTransition`, default fade/800ms), so a screenshot
            # taken 200ms after Reveal.slide() catches the previous slide's plate at low
            # opacity and the gate measures a tint that is not on the slide. Force both.
            page.evaluate("Reveal.configure({transition: 'none', backgroundTransition: 'none'})")
        except Exception as exc:
            qa["load_error"] = str(exc).splitlines()[0]
            browser.close()
            return qa
        page.wait_for_timeout(1200)          # fonts + first paint

        total = page.evaluate("Reveal.getTotalSlides()")
        pending = []
        for i in range(total):
            page.evaluate("Reveal.slide(%d)" % i)
            page.wait_for_timeout(260)
            info = page.evaluate(SLIDE_JS)
            num = page.evaluate("Reveal.getSlidePastCount()") + 1
            png = "slide-%02d.png" % num
            page.screenshot(path=os.path.join(out, png))
            for b in info["bgs"]:
                pending.append((num, b))
            if info["overflows"] or max(info["section_over"].values()) > 2:
                qa["overflow_slides"].append(num)
            qa["slides"].append({
                "slide": num, "png": png,
                "imgs": info["imgs"], "background_images": info["bgs"],
                "overflows": info["overflows"], "section_over": info["section_over"],
                "frame": info["frame"], "section": info["section"],
                "columns": info["columns"], "chip_collisions": info["chip"]})
            for im in info["imgs"]:
                if not im["ok"]:
                    qa["broken_images"].append({"slide": num, "src": im["src"], "why":
                                                "loaded but empty" if im["complete"]
                                                else "did not load"})
        # ---- background images: prove they load, at the size the browser asked for
        uniq = sorted({u for _, u in pending})
        probed = page.evaluate(PROBE_JS, [resolve(deck, u) for u in uniq]) if uniq else []
        okmap = {p["url"]: p for p in probed}
        for num, u in pending:
            p = okmap.get(resolve(deck, u))
            qa["background_images"].append({"slide": num, "url": u,
                                            "ok": bool(p and p["ok"]),
                                            "natural_w": p["w"] if p else 0})
            if p and not p["ok"]:
                qa["broken_images"].append({"slide": num, "src": u, "why": "background-image"})
        browser.close()

    montage(out, width, height)
    with open(os.path.join(out, "qa_report.json"), "w", encoding="utf-8") as fh:
        json.dump(qa, fh, indent=1)
    return qa


def resolve(deck, url):
    """Absolute `file://` form of a deck-relative asset URL (remote URLs pass through)."""
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) or url.startswith("/") or url.startswith("//"):
        return url            # already absolute — os.path.normpath("file:///a") == "file:/a",
                              # and re-prefixing it invented two ERR_FILE_NOT_FOUND hits
    return "file://" + os.path.normpath(os.path.join(os.path.dirname(deck), url))


def montage(out, width, height):
    """Tile every `slide-NN.png` into `montage.png` — the one view that shows the whole deck."""
    from PIL import Image
    files = sorted(glob.glob(os.path.join(out, "slide-*.png")))
    if not files:
        return None
    ims = [Image.open(f).convert("RGB") for f in files]
    cols = 5
    rows = (len(ims) + cols - 1) // cols
    tw, th, pad = max(180, width // 5), max(125, height // 5), 4
    canvas = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * th + (rows + 1) * pad), "#222")
    for i, im in enumerate(ims):
        x = pad + (i % cols) * (tw + pad)
        y = pad + (i // cols) * (th + pad)
        canvas.paste(im.resize((tw, th)), (x, y))
    canvas.save(os.path.join(out, "montage.png"))
    return os.path.join(out, "montage.png")


def report(qa, out):
    """Print the per-slide table and the one-line verdict the gate is judged by."""
    if qa["load_error"]:
        print("ERROR: deck did not load: %s" % qa["load_error"])
        print("       (reveal.js must be reachable from the deck; vendored paths only "
              "work offline — a CDN deck needs network, and a gate that needs network "
              "is not a gate)")
        return 1
    frame = qa["slides"][0]["frame"] if qa["slides"] else None
    print("deck: %s" % qa["deck"])
    print("out:  %s%s" % (out, "   frame: %d×%d px (section box is content-sized under "
                                "reveal; the frame is the authority)"
                          % (frame["w"], frame["h"]) if frame else ""))
    print("\nslide  imgs  bimgs  overflow  sec-over  col-gap(fig/text)  png")
    for s in qa["slides"]:
        so = s["section_over"]
        worst = max(so.values())
        gap = "; ".join("%d/%d" % (c["fig_h"], c["text_h"]) for c in s["columns"]) or "—"
        print("  %02d    %2d     %2d       %2d      %+5d     %-16s  %s"
              % (s["slide"], len(s["imgs"]), len(s["background_images"]), len(s["overflows"]),
                 worst, gap, s["png"]))
        for o in s["overflows"][:4]:
            print("        overflow  <%s%s> “%s”  over: top %d right %d bottom %d left %d"
                  % (o["tag"], ("." + o["cls"].replace(" ", ".")) if o["cls"] else "",
                     o["text"], o["over"]["top"], o["over"]["right"], o["over"]["bottom"],
                     o["over"]["left"]))
        if worst > 2 and not s["overflows"]:
            print("        section itself escapes the frame by %d px (non-text child pushes it)"
                  % worst)
        for c in s["chip_collisions"][:2]:
            print("        NOTE  content reaches the slide-number chip region: <%s%s> “%s”"
                  % (c["tag"], ("." + c["cls"].replace(" ", ".")) if c["cls"] else "", c["text"]))
    for b in qa["broken_images"][:8]:
        print("  broken image  s%02d  %s  (%s)" % (b["slide"], b["src"], b["why"]))
    for e in qa["console_errors"][:8]:
        print("  console error  %s" % e[:160])
    print("\nslides=%d console_errors=%d broken_images=%d overflow_slides=%d"
          % (len(qa["slides"]), len(qa["console_errors"]), len(qa["broken_images"]),
             len(qa["overflow_slides"])))
    return 0


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
    ap = argparse.ArgumentParser(prog="render_deck.py",
                                 description="rasterise a house deck + run the rendered gate")
    ap.add_argument("deck", nargs="?", default=None, help="the deck (or pass --deck)")
    ap.add_argument("--deck", dest="deck_opt", default=None,
                    help="the deck, for callers that prefer an explicit flag")
    ap.add_argument("--out", default=None, help="output dir (default: <deck dir>/render)")
    ap.add_argument("--width", type=int, default=1180)
    ap.add_argument("--height", type=int, default=820)
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when console errors / broken images / overflow slides are non-zero")
    args = ap.parse_args(argv)
    args.deck = resolve_deck(ap, args)
    if not os.path.exists(args.deck):
        print("no such deck: %s" % args.deck, file=sys.stderr)
        return 2
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.deck)), "render")
    qa = render(args.deck, out, args.width, args.height)
    report(qa, out)
    if qa["load_error"]:
        return 1
    bad = qa["console_errors"] or qa["broken_images"] or qa["overflow_slides"]
    return 1 if (args.strict and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
