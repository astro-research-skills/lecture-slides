#!/usr/bin/env python3
"""Mechanical guard for house-style reveal.js decks — the checks that catch the
failures every other gate is blind to.

Implements source-guide §8.11 (section-scoped editing), §7.7 (per-slide structural
tag parity), §8.10 (duplicate attributes) and §8.12 (stray `>>`) **as code**, not as
prose rules, because all four are invisible to the render gate and to a vision pass:

  * §8.11 — two live incidents came from a document-wide `re.search`: an edit written
    as "the first .keybox with font-size:.6em" matched *slide 9* while editing slide
    29. Tag parity, image count and overflow all stay green after a wrong-section
    splice, because each of those checks is still satisfied.
  * §8.10 — 17 of 34 `<img>` tags carried two `style` attributes. HTML honours the
    first and discards the rest, so the height solver wrote into dead markup and every
    verification run re-read the value it had just written.
  * §8.12 — four slides carried `</div>>`. The browser parses the trailing `>` as a
    *text node*: a visible `>` printed at the bottom of the column while tags balanced,
    images loaded, nothing overflowed and the console stayed clean.
  * §7.7 — parity must be counted *inside each section*: a global tally passes when two
    slides each lose a tag of the same kind and cancel out. Two traps in the count
    itself: substring counting makes `<b` match `<br>` and `<i` match `<img>`, so use
    `<%s\\b` and `</%s>`; void elements (`img br hr meta link input`) have no close tag
    at all and are left out of the list.

The guard is mechanical, not disciplinary: `put()` re-runs `check()` on the candidate
document and raises *without returning*, so a bad splice never reaches the disk.
`selftest` re-introduces the exact defects (§7.7: "a validator written from the same
misunderstanding as the bug is worth nothing until it refuses a known-bad input").

Library:
    from deck_edit import sections, body, put, edit, check
    check(html, assets_dir="…") -> [{"slide": 4, "kind": "…", "detail": "…"}]

CLI:
    python3 deck_edit.py check DECK.html [--assets-dir DIR] [--sections]
    python3 deck_edit.py selftest

Exit codes: 0 clean, 1 violations found (or a selftest assertion failed), 2 usage.
"""

import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------
# the four invariants
# ---------------------------------------------------------------------------

#: One `<section>` = one slide. Non-greedy so slides are document order; the house
#: style never nests sections (vertical stacks would break this — see qa-gate.md).
SECTION_RE = re.compile(r"(?s)(<section(?:\s[^>]*)?>)(.*?)(</section>)")

#: Structural tags that must balance *inside each section* (source §7.7 list).
#: Void elements are deliberately absent — they have no closing tag.
TAGS = ["div", "ul", "li", "p", "b", "i", "sub", "sup", "a", "span",
        "table", "tr", "td", "th", "aside"]
#: Void elements (§7.7): no closing tag exists, so they must stay OUT of TAGS.
VOID = ["img", "br", "hr", "meta", "link", "input"]
assert not set(VOID) & set(TAGS), "void elements have no </tag>; they break any parity list"

#: Comment / style / script contents are not markup: blank them before any count so a
#: `<div>` written inside a template comment cannot trip parity, and a CSS `>` in a
#: selector cannot trip the stray-`>` check. Each block is matched by its OWN opener and
#: closer — an alternated pattern lets an unclosed `<!--` swallow the rest of the file.
STRIP_BLOCKS = [re.compile(r"(?s)<!--.*?-->"),                      # whole node
                re.compile(r"(?s)<style\b[^>]*>(.*?)</style>"),     # contents only
                re.compile(r"(?s)<script\b[^>]*>(.*?)</script>")]   # … tags stay markup


class DeckInvariantError(AssertionError):
    """Raised by put()/edit() when the candidate document breaks an invariant."""


def masked(html):
    """`html` with comment/style/script blocks blanked out (length and newlines kept).

    Offsets stay valid against the original document, so the same section indices and
    the same splice offsets work on both strings.
    """
    out = list(html)
    for pat in STRIP_BLOCKS:
        for m in pat.finditer(html):
            for i in range(m.start(), m.end()):
                if out[i] != "\n":
                    out[i] = " "
    return "".join(out)


def sections(html):
    """All `<section>…</section>` matches, in document order (1-based slides)."""
    return list(SECTION_RE.finditer(html))


def body(html, n):
    """The inner text of slide `n` (1-based). Empty string if there is no such slide."""
    secs = sections(html)
    if not 1 <= n <= len(secs):
        raise IndexError("no slide %d (deck has %d sections)" % (n, len(secs)))
    return secs[n - 1].group(2)


def put(html, n, new_body):
    """Splice `new_body` into slide `n` by that section's own offsets.

    Re-runs `check()` on the candidate document and **raises without returning** if any
    invariant breaks (§8.11: the guard must be mechanical). Returns the new document
    only when it is clean.
    """
    secs = sections(html)
    if not 1 <= n <= len(secs):
        raise IndexError("no slide %d (deck has %d sections)" % (n, len(secs)))
    m = secs[n - 1]
    cand = html[: m.start(2)] + new_body + html[m.end(2):]
    bad = check(cand)
    if bad:
        raise DeckInvariantError(
            "put(slide %d) refused — %d invariant violation(s), nothing returned:\n  %s"
            % (n, len(bad), "\n  ".join(format_violation(v) for v in bad)))
    return cand


def edit(html, n, needle, replacement):
    """Replace `needle` with `replacement` inside slide `n` only.

    Asserts `needle` occurs **exactly once within that section** before replacing, then
    routes the splice through `put()`. Returns the new document.
    """
    b = body(html, n)
    found = b.count(needle)
    if found != 1:
        raise DeckInvariantError(
            "edit(slide %d): needle occurs %d time(s) inside this section, need exactly 1 "
            "(§8.11 — never let a slide edit match outside its own <section>)" % (n, found))
    return put(html, n, b.replace(needle, replacement, 1))


# ---------------------------------------------------------------------------
# the checker
# ---------------------------------------------------------------------------

def _attr_names(tag_inner):
    """Attribute names of one start tag, with quoted values removed first."""
    unquoted = re.sub(r'"[^"]*"' + "|'[^']*'", " ", tag_inner)
    return [m.group(1).lower() for m in re.finditer(r"([a-zA-Z_:][\w:.-]*)\s*=", unquoted)]


def _local_refs(text):
    """Local asset references in `text`: img src, data-background-image, style url(...)."""
    out = []
    for pat, kind in ((r"<img\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"']", "img src"),
                      (r"data-background-image\s*=\s*[\"']([^\"']+)[\"']",
                       "data-background-image"),
                      (r"url\(\s*[\"']?([^\"')]+)[\"']?\s*\)", "css url()")):
        for m in re.finditer(pat, text):
            out.append((kind, m.group(1).strip()))
    return out


def check(html, assets_dir=None):
    """Every invariant violation in `html`, as a sorted list of dicts.

    kind is one of: tag-parity | duplicate-attribute | stray-'>>' | missing-asset |
    section-structure. Global findings carry slide 0.

    `assets_dir`: resolve local asset references against it (None = skip that check).
    Remote (`http(s):`, `data:`) and absolute references are never checked here — the
    render gate is what proves a URL actually loaded.
    """
    secs = sections(html)
    plain = masked(html)
    out = []

    # -- section-structure: a `<section>` whose open/close counts disagree ----------
    n_open = len(re.findall(r"<section(?:\s[^>]*)?>", html))
    n_close = len(re.findall(r"</section>", html))
    if n_open != n_close:
        out.append({"slide": 0, "kind": "section-structure",
                    "detail": "%d <section> open / %d close" % (n_open, n_close)})

    # -- stray '>>' anywhere in markup (§8.12) -------------------------------------
    for m in re.finditer(r">>", plain):
        line = plain.count("\n", 0, m.start()) + 1
        snippet = plain[max(0, m.start() - 40):m.start() + 2].replace("\n", " ")
        out.append({"slide": _slide_of(secs, m.start()), "kind": "stray-'>>'",
                    "detail": "line %d: '…%s' — a '>' after a close tag is parsed as a "
                              "text node and prints (escaped maths is fine, this is not)"
                              % (line, snippet.strip())})

    # -- duplicate attributes on any element (§8.10) --------------------------------
    for m in re.finditer(r"(?s)<([a-zA-Z][\w:-]*)\b([^<>]*)>", plain):
        names = _attr_names(m.group(2))
        dupes = sorted({a for a in names if names.count(a) > 1})
        if dupes:
            out.append({"slide": _slide_of(secs, m.start()), "kind": "duplicate-attribute",
                        "detail": "<%s> carries %s twice — HTML honours the first and "
                                  "discards the rest, so later writes to it are dead "
                                  "markup: %s" % (m.group(1), ", ".join(dupes),
                                                  _clip(m.group(0)))})

    # -- per-slide tag parity (§7.7) ------------------------------------------------
    for i, m in enumerate(secs, 1):
        b = masked(m.group(2))
        for t in TAGS:
            o = len(re.findall(r"<%s\b" % t, b))
            c = len(re.findall(r"</%s>" % t, b))
            if o != c:
                out.append({"slide": i, "kind": "tag-parity",
                            "detail": "<%s> open %d / close %d inside this slide "
                                      "(counted per section, not globally)" % (t, o, c)})
        if assets_dir:
            for kind, ref in _local_refs(b):
                if _is_remote(ref):
                    continue
                if not os.path.exists(os.path.join(assets_dir, ref)):
                    out.append({"slide": i, "kind": "missing-asset",
                                "detail": "%s '%s' does not resolve under %s"
                                          % (kind, ref, assets_dir)})
    out.sort(key=lambda v: (v["slide"], v["kind"]))
    return out


def _slide_of(secs, pos):
    """1-based slide number containing document offset `pos`, else 0 (outside slides)."""
    for i, m in enumerate(secs, 1):
        if m.start() <= pos < m.end():
            return i
    return 0


def _clip(s, n=70):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n] + "…"


def _is_remote(ref):
    return ref.startswith(("http://", "https://", "data:", "//", "mailto:", "#")) or "\n" in ref


def format_violation(v):
    return "slide %2d  %-20s %s" % (v["slide"], v["kind"], v["detail"])


# ---------------------------------------------------------------------------
# selftest — refuse known-bad input, accept known-good (§7.7)
# ---------------------------------------------------------------------------

def _doc(slides):
    head = ('<!DOCTYPE html><html><head><meta charset="UTF-8">'
            '<style>.cols{display:flex} .a>.b{color:red}</style></head><body>'
            '<div class="reveal"><div class="slides">'
            '<!-- template comment: mentions <div>, </div>> and two style= attrs -->')
    return head + "".join(slides) + ('</div></div>'
                                     '<script src="vendor/reveal/reveal.js"></script>'
                                     '<script>Reveal.initialize({margin: 0.04});</script>'
                                     '</body></html>')


def _good_slide(src="assets/a.png"):
    """A house-style slide: void elements present, ONE style attr, balanced tags."""
    return ('<section><h2>Balance</h2><div class="cols"><div><ul>'
            '<li><b>Claim.</b> One clause, then a line<br>break.</li></ul></div>'
            '<div class="figcol"><img src="%s" alt="x" style="max-height:200px">'
            '<p class="figcap src">Author+ Year, Journal</p></div></div></section>' % src)


def _trap_slide():
    """One section holding the §7.7 counting traps AND a real nested-<div> imbalance.

    `<b>` paired + `<br>` present  → substring counting sees "<b" twice, "</b>" once
    and cries parity over a slide that is fine; `<img>` does the same to `<i`.
    The genuine defect is the leaked `<div><div>` pair with one close tag missing.
    """
    return ('<section><h2>Traps</h2><div class="cols"><div><ul>'
            '<li><b>Paired bold.</b> plus a break<br>here</li></ul>'
            '<img src="assets/a.png" alt="not italic">'
            '<div><div></div></div>'
            '<div><div>leaked</div></section>')


def selftest(assets):
    """Build known-bad documents in memory; assert the guard refuses each.

    Returns [(name, ok, note)]; the CLI exits 1 if any assertion fails. Each case
    also asserts the *other* invariants stayed quiet, so a checker that merely
    reports everything cannot pass this either.
    """
    results = []

    def only(v, kind):
        return [x for x in v if x["kind"] == kind]

    def others(v, keep):
        return [x for x in v if x["kind"] not in keep]

    # ---- known-good: house style, void elements, remote + local refs, escaped maths
    good = _doc([_good_slide(),
                 '<section class="bleed"><div class="bg" style="--bg:url(\'assets/a.png\')">'
                 '</div><p class="src">Image: Author, CC BY-SA 4.0</p></section>',
                 '<section><table><tr><th>Rung</th><th>Method</th></tr>'
                 '<tr class="punch"><td>4</td><td>z &lt; 1 and &gt; 100 Mpc</td></tr></table>'
                 '<aside class="notes">spoken only</aside>'
                 '<img src="https://example.org/x.png" alt="remote"></section>'])
    v = check(good, assets)
    results.append(("known-good deck accepted", not v,
                    format_violation(v[0]) if v else "0 violations over 3 sections"))
    # and the fixture really does carry the trap the naive check would fall for
    trap_b = len(re.findall("<b", _trap_slide())) != len(re.findall(r"<b\b", _trap_slide()))
    trap_i = len(re.findall("<i", _trap_slide())) != len(re.findall(r"<i\b", _trap_slide()))
    results.append(("<b/<i substring trap present in fixture", trap_b and trap_i,
                    "naive counting sees <b %d times vs regex %d" %
                    (len(re.findall("<b", _trap_slide())),
                     len(re.findall(r"<b\b", _trap_slide())))))

    # ---- bad 1: duplicate style on an <img> (§8.10 — the solver then writes dead markup)
    dup = _doc([_good_slide().replace('style="max-height:200px"',
                                      'style="max-height:200px" style="max-height:340px"'),
                _good_slide()])
    v = check(dup, assets)
    hits = only(v, "duplicate-attribute")
    results.append(("duplicate style attr refused",
                    len(hits) == 1 and hits[0]["slide"] == 1 and not others(v, {"duplicate-attribute"}),
                    format_violation(hits[0]) if hits else "NOT CAUGHT"))

    # ---- bad 2: `</div>>` (§8.12 — survived a full rasterise; found only in the pixels)
    stray = _doc([_good_slide(),
                  '<section><div class="cols"><div><ul><li><b>Claim.</b></li></ul></div></div>></section>'])
    v = check(stray, assets)
    hits = only(v, "stray-\'>>\'")
    results.append(("stray '>' after close tag refused",
                    len(hits) == 1 and hits[0]["slide"] == 2 and not others(v, {"stray-\'>>\'"}),
                    format_violation(hits[0]) if hits else "NOT CAUGHT"))

    # ---- bad 3: the trap slide — must report the div imbalance, and NOTHING about b/i
    v = check(_doc([_good_slide(), _trap_slide()]), assets)
    hits = only(v, "tag-parity")
    kinds = {x["detail"].split(">")[0].lstrip("<") for x in hits}
    results.append(("nested-div imbalance refused; <b/<br not reported",
                    "div" in kinds and "b" not in kinds and "i" not in kinds
                    and len(hits) == 1 and hits[0]["slide"] == 2,
                    " | ".join(format_violation(x) for x in hits) or "NOT CAUGHT"))

    # ---- bad 4: a local asset that does not resolve (remote refs must stay quiet)
    v = check(_doc([_good_slide("assets/not_there.png")]), assets)
    hits = only(v, "missing-asset")
    results.append(("missing local asset refused",
                    len(hits) == 1 and hits[0]["slide"] == 1,
                    format_violation(hits[0]) if hits else "NOT CAUGHT"))
    v = check(_doc([_good_slide("https://example.org/x.png")]), assets)
    results.append(("remote src not a missing-asset", not only(v, "missing-asset"),
                    "%d violation(s)" % len(v)))

    # ---- bad 5: put() must raise instead of returning a broken document
    try:
        d = _doc([_good_slide(), _trap_slide()])
        moved = put(d, 2, body(d, 2) + "<b>unmatched</b></b>")
        results.append(("put() raises without returning", False,
                        "returned a document carrying " + format_violation(check(moved, assets)[0])))
    except DeckInvariantError as e:
        results.append(("put() raises without returning", True, str(e).splitlines()[0]))

    # ---- bad 6: edit() must refuse a needle that is not unique inside its own slide
    d = _doc([_good_slide(), _good_slide()])
    try:
        edit(d, 1, "<div", "<div class=\"x\"")
        results.append(("edit() refuses a non-unique needle", False, "spliced anyway"))
    except DeckInvariantError as e:
        results.append(("edit() refuses a non-unique needle", True, str(e).splitlines()[0]))
    # ---- bad 7: … and must refuse a unique needle that writes a duplicate attribute
    try:
        edit(d, 1, 'style="max-height:200px"', 'style="max-height:200px" style="max-height:9px"')
        results.append(("edit() refuses a dirty write", False, "duplicate style accepted"))
    except DeckInvariantError as e:
        results.append(("edit() refuses a dirty write", True, str(e).splitlines()[0]))
    # ---- good path: a clean, unique, section-scoped write returns the new document
    try:
        nd = edit(d, 2, "<h2>Balance</h2>", "<h2>Mirrored slide</h2>")
        ok = ("Mirrored slide" in body(nd, 2)) and ("Mirrored slide" not in body(nd, 1))
        results.append(("edit() lands the write in the named slide only", ok,
                        "slide 2 changed, slide 1 untouched"))
    except DeckInvariantError as e:
        results.append(("edit() lands the write in the named slide only", False, str(e)))
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(prog="deck_edit.py",
                                 description="Mechanical invariant guard for house decks")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check", help="print every invariant violation in a deck")
    c.add_argument("deck")
    c.add_argument("--assets-dir", default=None,
                   help="resolve img/background refs here (default: the deck's own directory)")
    c.add_argument("--no-assets", action="store_true", help="skip asset resolution")
    c.add_argument("--sections", action="store_true", help="list per-slide offsets instead")
    sub.add_parser("selftest", help="assert the guard refuses known-bad documents")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        import tempfile
        png = bytes.fromhex(  # a real 1x1 PNG: the asset check passes on a file, not a name
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
            "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082")
        with tempfile.TemporaryDirectory() as td:
            os.mkdir(os.path.join(td, "assets"))
            with open(os.path.join(td, "assets", "a.png"), "wb") as fh:
                fh.write(png)
            results = selftest(td)
        failed = 0
        for name, ok, note in results:
            print("%-4s %-52s %s" % ("PASS" if ok else "FAIL", name, note))
            failed += 0 if ok else 1
        print("\nselftest: %d/%d guard assertions held" % (len(results) - failed, len(results)))
        return 1 if failed else 0

    if args.cmd == "check":
        if not os.path.exists(args.deck):
            print("no such deck: %s" % args.deck, file=sys.stderr)
            return 2
        html = open(args.deck, encoding="utf-8").read()
        secs = sections(html)
        if args.sections:
            print("%d sections in %s" % (len(secs), args.deck))
            for i, m in enumerate(secs, 1):
                head = re.sub(r"\s+", " ", m.group(2)).strip()[:64]
                print("  slide %2d  open %7d  body %7d-%7d  close %7d  %s"
                      % (i, m.start(1), m.start(2), m.end(2), m.end(3), head))
            return 0
        adir = None
        if not args.no_assets:
            adir = args.assets_dir or os.path.dirname(os.path.abspath(args.deck))
        v = check(html, adir)
        print("deck_edit check: %s — %d sections, %d violation(s)"
              % (args.deck, len(secs), len(v)))
        for x in v:
            print("  " + format_violation(x))
        return 1 if v else 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
