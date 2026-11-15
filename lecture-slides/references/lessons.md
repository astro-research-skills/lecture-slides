# Lessons — lecture-slides

The skill's own memory: how this work fails *while believing it succeeded*. Read before
building or revising a deck. Each entry keeps the observed failure that forced a rule; the
full rule now lives in the file named at the entry's end — the entry carries only its
one-sentence version.

**Entry format:** one bullet = the lesson in bold, one line of the observed failure with its
mechanism, the rule it became and where that rule now lives, a source tag. Durable (recur on
the next deck), generalisable (not one lecture's detail), deduped.

**Append when:** the user corrects the deck, or a defect slips past a verdict that looked
clean. Newest first.

**Budget:** ≤120 lines. Over budget → distill oldest entries into the matching
`references/*.md` and trim here.

**Does not belong here:** project-specific facts (one deck's numbers, one lecture's slide
indices — those go in the course's framework document and `FIGURE_SOURCES.md`), secrets.

**Reading the source tags:** entries tagged `guide §n` come from the 885-line course guide this
skill replaced; it was deleted when the skill was built, so the tag is provenance, not a live
link. The rule it cites is in the file named at the end of the same entry.

---

- **A gate that fails the reference deck is miscalibrated, not strict** — the void bar was
  ported as ">12% is a defect" and then failed nine of the instructor's own twenty-five shipped
  slides: measured inside the content block, those finals run median 10.5%, p90 17.2%, max
  19.0%. Rule: calibrate every threshold against the finals before trusting it, print the
  distribution beside the verdict, and fix the *measurement* first — page-level void also
  counts the symmetric bands around a vertically centred block, and reveal's progress bar and
  page chip stretch the ink bounding box to the page edge unless masked. (→ `qa-gate.md` §4)
- **`transition: 'none'` does not cover backgrounds** — reveal fades `data-background-image`
  on its own clock, so a screenshot 200 ms after a slide change catches the previous plate at
  partial opacity; a slide read as a pale pink wash in the PNG and as white in the browser.
  Rule: set `backgroundTransition: 'none'` in the deck *and* force it in the renderer, because
  a gate must not depend on the deck remembering. (→ `qa-gate.md` §4)
- **Green numbers hide collisions inside a generated figure** — two matplotlib annotations
  were drawn on top of their own axis labels while all eleven verdicts passed. Rule: generated
  figures get the same vision read as crops; a schematic's label positions are code, and code
  does not notice that it overlaps itself. (→ `figures.md`)
- **A script and its docs drift within one build** — every reference file documented
  `--deck DECK.html` while the scripts accepted only a positional path, so the documented
  command failed on first copy-paste. Rule: after writing a reference, run the exact commands
  it names; a usage line is a promise, and verify the promise. (→ `pipeline.md` §5)
- **A gate reporting "0 problems" after a large rewrite is a claim to be tested, not
  trusted** — the overflow check enumerated tags (`p, li, h1…h3, span, table, .figcap`);
  the take-away line was a `div.take` with its text inside a `<b>`, so five slides pushed
  past the bottom frame while the gate reported zero overflows, and one rendered-page review
  found them straight away. Rule: the gate walks every element containing a text node, and
  a clean verdict after a content restructure gets cross-checked against one independent
  observer before it is believed. (guide §10.11 → `qa-gate.md`)
- **A writer that reads back the attribute it just wrote verifies its own bug** — 17 of 34
  `<img>` tags carried two `style` attributes; HTML honours the first, the height solver
  wrote into whichever it found after `src=` (the dead one), so ten slides carried values
  that had never rendered while every verification re-read its own write and reported
  success; fixing the writer recovered +4.8% figure area deck-wide, 21–42% on nine slides.
  Rule: match elements by identity (`src=`) and rewrite the whole tag — never zip solver
  output against regex matches by index; assert no duplicate attributes in the gate.
  Symptom: exactly 0.0% area gain after a legitimate height change. (2026-10-12, guide
  §8.10 → `qa-gate.md`, `scripts/solve_fig_height.py`)
- **A document-wide regex edit lands on the wrong slide; the guard must be mechanical** — a
  box move written as "first `keybox` with `font-size:.6em`" while editing slide 29 matched
  slide 9's box (both used that size): slide 9 silently lost its commentary, slide 29 gained
  another method's paragraph; a companion removal stopped at the first nested `</div>` and
  left a tail. Rule: every slide edit is section-scoped — take the `<section>` body, edit
  that string, splice by the section's offsets, and assert the text arrived at the
  destination *and* vanished from its origin; a wrong-section splice is invisible to tag
  parity and overflow checks. (2026-10-12, guide §8.11 → `qa-gate.md`, `scripts/deck_edit.py`)
- **A validator written from the misunderstanding that caused the bug is worth nothing until
  it has refused a known-bad input** — after the tag-parity miss, re-introducing the exact
  defect was the only proof the new check worked. Rule: regression-test every guard — feed
  it the broken edit, confirm it prints `NOT WRITTEN`, confirm the file is untouched.
  (guide §7.7 → `qa-gate.md`)
- **Predict a trim's gain in lines, not words, and re-measure** — a two-sentence box trim
  predicted to free 18 px freed 3, because the removed sentence shared its wrapped line with
  the kept one. Rule: estimate the wrapped-line count first; re-measure rendered figure
  height immediately after; if the gain is an order of magnitude below prediction, the cut
  bought nothing — revert it. A load-bearing claim is worth more than 3 px.
  (guide §7.9 → `layout.md`)
- **A `max-height` larger than the width-fill value is inert — editing the attribute tells
  you nothing** — a slide reporting a "regression" in the vh attribute may be pixel-identical,
  because the browser clamps the image to the column width. Rule: diagnose from rendered
  boxes (`getBoundingClientRect`), compared before/after across the whole deck; it is the
  only way to tell a genuinely squeezed figure from one that cannot grow wider than its
  column. (guide §7.6 → `layout.md`)
- **"Two figures cannot fit in a column" was 117 px of inherited margins** — the theme's
  `.reveal img { margin: 20px 0 }` plus the caption's bottom margin: the height arithmetic
  said 691 px of children in a 716 px slot, the DOM said 808 px. Rule: before trusting any
  height budget, dump the child boxes with their computed margins, and zero the margins
  inside the figure column. (guide §7.8 → `layout.md`)
- **Crediting a figure is a claim and gets the same verification as a measurement** — a
  figure was cited as "Li & White 2008, MNRAS 384, 145": a truncation of 384, **1459**, and
  the arXiv id first tried belonged to an unrelated solar-physics paper. Rule: check author,
  year, volume, first page, title and abstract numbers against the PDF's own front matter —
  not against a summary written earlier in the session. (guide §10.10 → `figures.md`)
- **A journal figure answers the author's question, not the lecturer's** — asked for figures
  showing the Local Group's structure, the search of the papers already on hand returned six
  crops that did not answer it; the instructor found a better one on Wikimedia Commons in
  two minutes. Rule: a general "what figures exist for X" search starts at Wikimedia
  Commons / the Wikipedia article, then reviews, then primary papers; record licence from
  the file description page and put author, licence and the crop note *in the slide
  caption*. (guide §10.12 → `figures.md`)
- **Judge every figure at the size the audience sees it** — a 300 dpi crop can be perfectly
  sharp and still unreadable rendered 600 px wide on the slide. Rule: check the delivered
  pixels — tick numerals ≥9 px, axis titles ≥11 px, no legend text smaller than the plot's
  body; a crop that only works zoomed is the wrong figure: crop tighter or replace
  it. (guide §10.9 → `figures.md`)
