# QA gate — the ordered delivery check for a deck

The last thing that runs before a deck is called finished: six stages, from millisecond static assertions to a read of the delivered pixels, with the consolidated checklist at the end wrapping them in a plan-first pre-flight and a courseware handoff. Run it top to bottom and stop at the first failure. Rules owned by other files are not restated here — thresholds live in `layout.md` §11, density in `density-target.md`, prose in `writing.md`, figures in `figures.md`.

## 1. Stage 1 — static invariants

`python3 scripts/audit_deck.py --deck <deck>.html` — pure text over the HTML, no browser.

**The gate asserts; it does not report.** On any break it refuses the write and prints `NOT WRITTEN`. A problem list appended to a log is not a gate: the ten-slide `style` incident below survived "verification" precisely because each run printed a success it had itself caused.

- **Per-section tag parity.** Count opens and closes *inside each* `<section>`, for every structural tag: `div ul li table aside p b i sub sup a code span tr td th`. A global tally is not enough — a global `<li>` count of 80 open / 79 close reads as one careless hand-edit, and a global tally also passes when two slides each lose a tag of the same kind and cancel out. Two traps when writing this by hand:
  - substring counting makes `<b` match `<br>` and `<i` match `<img` — use `<%s\b` and `</%s>`;
  - void elements (`img br hr meta link input`) have no closing tag, so leave them out of the list entirely.
- **No duplicate attributes on any element.** Found 2026-10-12: **17 of 34 `<img>` tags carried two `style` attributes.** HTML honours the first and discards the rest, so the second was dead text. The height solver wrote its result into whichever `max-height` it found *after* `src=` — for those 17 tags, the dead one. **Ten slides carried values that had never rendered and never would,** while every verification run reported success because it re-read the attribute it had just written. Fixing the writer recovered **+4.8% figure area, and 21–42% on nine slides at once**. Two rules follow: never write an attribute by position in a tag (match the element by identity — `src=` — and rewrite the whole tag; a writer that zips solver output against regex matches by index also breaks on any slide holding two figures), and assert the invariant:

  ```python
  dup = sum(1 for m in re.finditer(r'(?s)<img\b[^>]*>', s)
            if len(re.findall(r'\bstyle\s*=', m.group(0))) > 1)
  assert dup == 0, "duplicate style attrs: %d" % dup
  ```

  Symptom to watch for: a re-render after a legitimate height change reports **exactly 0.0% area gain** across the deck. That means the write landed in dead markup, not that the layout was already optimal.
- **No `>>` anywhere in the markup.** Four slides carried `</div>>`. Browsers parse the trailing `>` as a **text node**, so it printed a visible `>` at the bottom of the column while every other gate stayed green: tags balanced, images intact, no overflow, no console error. It survived a full-deck rasterise and was found only by reading the rendered PNG at full size. Origin: a splice that concatenated a close tag with the next line's leading `>`. Check the surviving `&gt;` hits are genuine mathematics (`> 100 Mpc`, `σ_e > 200 km/s`), not damage.

  ```python
  assert '>>' not in s, "stray '>' after a close tag renders as visible text"
  ```
- **Every `img src` resolves** on disk under `assets/` (`http:`, `https:`, `data:` exempt).
- **Regression-test the guard by re-introducing the defect it missed.** A validator written from the same misunderstanding that caused the bug is worth nothing until it has refused a known-bad input: feed it the exact broken edit, confirm `NOT WRITTEN`, confirm the file is untouched.

## 2. Stage 2 — section-scoped editing

Two live incidents on 2026-10-12, both from `re.search` over the whole document:

1. A box move written as "find the first `keybox` with `font-size:.6em`" matched **slide 9's** box while editing **slide 29**, because both happen to use that size. Slide 9 silently lost its commentary; slide 29 gained a paragraph about PNLF that belonged to another method entirely.
2. A removal written `(?s)<div class="keybox".*?</div>\n` stopped at the **first nested `</div>`**, leaving the tail of the old block behind.

The guard is mechanical, not disciplinary — take the section body, edit that string, splice back by the section's own offsets (`scripts/deck_edit.py`, importable and used by the gate):

```python
GS = lambda t: list(re.finditer(r'(?s)(<section(?:\s[^>]*)?>)(.*?)(</section>)', t))
def body(t, n): return GS(t)[n-1].group(2)
def put(t, n, nb):
    m = GS(t)[n-1]; return t[:m.start(2)] + nb + t[m.end(2):]
b = body(s, 29)
assert b.count(needle) == 1          # unique *within the slide*
s = put(s, 29, b.replace(needle, replacement, 1))
```

Then assert the text **arrived** *and* **vanished from its origin**: `assert 'What will change that' in body(s,29)` and `assert 'Why it is back' in body(s,9)`. A wrong-section splice is invisible to tag parity, image count and overflow — every one of those checks is still satisfied.

## 3. Stage 3 — rendered gate

`python3 scripts/render_deck.py --deck <deck>.html` (Chromium at 1180×820, `transition: none`) rasterises every slide and writes `render/slide-NN.png` + `render/qa_report.json`. Required: **0 console errors, 0 broken images, 0 overflow.**

- **The overflow check must walk every element that holds a direct text node**, not a hand-written tag list. The incident: the gate iterated `p, li, h1, h2, h3, span, table, .figcap`. The house take-away line is `div.take` whose text sits inside `<b>`, so neither the div nor the bold was ever measured — **five slides pushed their take-away past the bottom frame while the gate reported zero overflows**, and a vision review found them straight away. Walk `section.querySelectorAll('*')`, keep elements with a non-empty direct text child, compare each rect against the section box.
- The frame test still cannot see a block whose **fill** runs under the page-number chip; check that by rect intersection as its own assert — geometry and the pixel-scan trap in `layout.md`.
- **A gate that reports "0 problems" after a large rewrite is a claim to be tested, not trusted.** When a change adds or restructures content, cross-check the zero against one independent observer (Stage 6).

## 4. Stage 4 — rendered-pixel audit

`audit_deck.py`'s rendered half, over `render/slide-NN.png`: coarse-grid ink **coverage** and the **largest empty axis-aligned rectangle** per slide, written to `render/audit.json`. Thresholds and their calibration: `layout.md` §11.

- Run the audit **before and after** the pass and report both numbers.
- **Measure the void inside the content block, not the page.** A vertically centred slide
  leaves a band above *and* below its content; on the instructor's shipped lecture8 renders
  that page-level number reads 12–24% on fourteen of twenty-five finished slides. The defect
  is emptiness *inside* the block (a dead band between title and bullets, between figure and
  take-away), so `audit_deck.py` reports both and gates on the block-level one. Deck chrome —
  the progress bar and the page chip — is masked before measuring, or the bounding box
  stretches to the page edge and every slide reports a void it does not have.
- **Calibrate the bar against the finals, not against a round number.** The measured
  distribution on lecture8's 25 renders: block-level void median 10.5%, p90 17.2%, max 19.0%;
  coverage median 0.91. A bar at 12% would fail nine of those slides — a gate the reference
  population cannot pass is miscalibrated, not strict. Ours sits at 20%, with the distribution
  printed beside it so a drift stays visible.
- The acceptance metric is whole-deck: mean coverage, minimum coverage, count of slides below threshold, largest void per slide, plus 0 console errors, 0 broken images, 0 overflow and per-slide tag parity. A change that improves one slide and is silent about the other 42 is not finished.
- Name the offending slides by number; a real void is the only kind of empty you may act on (`layout.md`).
- **Declared breath slides**: `--void-ok 4,8` excuses the slides where emptiness *is* the
  design (a part divider, a one-question slide, the closing line). The verdict line prints
  every slide excused this way, so an exemption can never be silent.
- **Backgrounds fade independently of slides.** `transition:'none'` does not cover
  `data-background-image`: reveal fades those on its own clock, so a screenshot taken 200 ms
  after a slide change catches the *previous* plate at partial opacity and the audit measures
  a tint that is not on the slide. This bit the worked example: slide 2 read as a pale pink
  wash that existed only in the PNG. Set `backgroundTransition:'none'` in the deck, and
  `render_deck.py` forces it as well, because the gate must not depend on the deck
  remembering.

## 5. Stage 5 — content invariants no static check can see

- **Numeric-token diff *and* author-name diff** against the pre-edit deck, per slide. A numeric diff catches dropped quantities but not a shortened citation; an author-name check catches the reverse. `Dressler, Lynden-Bell, Burstein, … 1987` → `Dressler, Lynden-Bell et al. 1987` is fine only because the full list survives in the notes. Procedure: `layout.md`.
- **Nothing load-bearing was deleted.** A number or claim that appears nowhere else must survive somewhere visible; the instructor keeps ~0 speaker notes, so notes are not an archive (`density-target.md`).
- **If agents did the cutting, the applier must apply their notes payload too** — an applier that handles only the edits silently drops every preserved fact. That is how eleven citations went missing at once.
- **Every figure verified for relevance by a vision read of the rendered slide**, and every number and citation verified against the paper's own front matter — `figures.md`.
- **Titles state this slide's claim or question**, and the explanation-debt items hold: figure decoded, membership criterion, error budget, share of budget, zero point, title-not-anecdote — the list is in `writing.md`.

## 6. Stage 6 — deck-level reviews

Only a rendered-page read gives you these; no script can:

- **Numerically fine, visually empty.** The Malmquist schematic had all three curves drawn at m ≈ −15, outside the plotted range: the slide showed a limit line, a shaded band and nothing else. Read the delivered pixels.
- **"0 problems after a big rewrite" deserves one independent observer** — a vision-capable reviewer on the rendered pages, or a ruler on the pixels, for every slide whose content changed substantially. Run it on all new and modified slides, and on every course-made plot: the DOM cannot see text collisions inside an image.
- **Sequence defects:** a use-before-definition, or a slide that enumerates order (agenda, summary table, part divider) contradicting a reordered body — `layout.md`.

## 7. Tooling hazard: never name a helper script after a stdlib module

A `/tmp/.../struct.py` transform script shadowed Python's `struct`. `sys.path[0]` is the *script's* directory, so every playwright run re-imported it and silently re-applied the transform to the deck. **Symptom: an edit you just made reverts itself.** Standard-library shadowing raises no error. It only produces a deck that will not stay fixed. Rename the helper.

## 8. Consolidated pre-delivery checklist

Ordered stages; run top to bottom; do not present while any box is unchecked.

**Stage 0 — contract and provenance (before any HTML)**
- [ ] 1. Plan document written and saved (Chinese, with time allocation and the five questions); HTML not started before it
- [ ] 2. Every figure from the literature, or marked `[course]` with its three conditions (visible tag, the numbers it uses and their source, no journal plate imitated)
- [ ] 3. Every figure documented in `assets/FIGURE_SOURCES.md` with citation + link

**Stage 1 — static invariants (`scripts/audit_deck.py`, refuses the write)**
- [ ] 4. Tag parity counted *per section*, every structural tag, void elements left out
- [ ] 5. No duplicate attributes on any element — the second `style` is asserted, not inspected
- [ ] 6. No `>>` anywhere; surviving `&gt;` confirmed to be real mathematics
- [ ] 7. Every `img src` resolves under `assets/`
- [ ] 8. The validator has refused the known-bad input it was written for, and left the file untouched

**Stage 2 — edit hygiene (`scripts/deck_edit.py`)**
- [ ] 9. Every slide edit section-scoped; text asserted present in the target slide *and* absent from its origin
- [ ] 10. No helper script shadows a stdlib module name

**Stage 3 — rendered gate (`scripts/render_deck.py`)**
- [ ] 11. 0 console errors, 0 broken images, 0 overflow
- [ ] 12. Overflow walks every element with a direct text node, take-away line included
- [ ] 13. Box fills clear of the page-number chip, by rect intersection (`layout.md`)
- [ ] 14. The gate's zero cross-checked against a rendered-page review wherever content changed substantially

**Stage 4 — rendered pixels**
- [ ] 15. Coverage + largest void audited on every slide, thresholds per `layout.md` §11, **run before and after with both numbers reported**; real void separated from a white-background scan before acting
- [ ] 16. Figure heights solved in the browser and **rendered** heights compared before/after across the deck — never the `max-height` attribute

**Stage 5 — content**
- [ ] 17. Density gate: median ≤60 words/slide, no slide >140 words, 0 tables, 0 keybox/bluebox, every content word at body size (nothing the audience must read in `.small`/`.tiny`), figure area ≥30% on figure slides
- [ ] 18. ≤4 bullets per slide, one line each, no nested sub-bullets
- [ ] 19. No hyphen-chained compounds in bullet text (read-aloud test); no trailing explanatory asides
- [ ] 20. No course meta, no cross-lecture pointers, no hedges that are not the lesson
- [ ] 21. Title slide carries the four-part agenda; part dividers are full-bleed figures
- [ ] 22. Every claim line bold-or-labelled, so the argument scans from the bold alone
- [ ] 23. Numeric-token diff *and* author-name diff against the pre-edit deck, per slide
- [ ] 24. Every number/claim cut from a slide re-appears visibly somewhere or was deleted deliberately — notes are not an archive
- [ ] 25. Every figure verified relevant by a vision read; every number verified against the original paper; every citation checked against the PDF front matter (volume, first page, title, arXiv id)
- [ ] 26. Figures judged at render size: tick numerals ≥9 px, axis titles ≥11 px in the delivered image
- [ ] 27. Overflow cut by arithmetic: N px = N/42 body lines, not by feel
- [ ] 28. Every figure slide's first bullet decodes the figure: x axis, y axis, what one mark is, what the curve means
- [ ] 29. Every group/cluster slide states the membership criterion operationally: radius + velocity + an independent distance
- [ ] 30. Every "this was wrong" slide ends with an error budget: which errors, how many magnitudes, the factor they multiply out to
- [ ] 31. Every claimed cause quotes its share of the required budget
- [ ] 32. The zero point is defined before the first velocity difference, and the frame slide is measured, not asserted
- [ ] 33. Titles state this slide's claim or question: no anecdotes, no restatement of the previous slide, nothing that survives being moved
- [ ] 34. A general figure search started at Wikimedia Commons / the Wikipedia article, and any Commons image carries author, licence and "changes were made" in the slide caption

**Stage 6 — deck-level review**
- [ ] 35. Vision QA on every new and modified slide, including all course-made plots
- [ ] 36. Delivered pixels read for "numerically fine, visually empty" figures
- [ ] 37. Reorder-dependency check: positional wording and fragment links grepped, moves kept inside a part, every slide that enumerates order reconciled to the new sequence

**Stage 7 — courseware and handoff**
- [ ] 38. Exercise scripts tested end-to-end; the expected result matches the published value within the simplifications
- [ ] 39. Student report guide written
- [ ] 40. Plan document updated: what changed and why, verification record, decision log
