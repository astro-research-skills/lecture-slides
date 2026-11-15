# Layout — the figure owns its half, the content covers the page

Geometry rules for slide layout: how much space a figure gets, where the text goes, how empty space is diagnosed and filled, and how many pixels a content change is worth. Read this when placing figures, solving heights, or fixing a slide that reads unfinished. What content earns a slide at all is `density-target.md`; figure sourcing and caption *content* are `figures.md`.

**Part A — the figure owns its half of the slide.** "A figure that could be bigger is a slide that is wrong": a deck built on the old flat "images: 40–44vh" advice ended up with figures at 12vh, about one seventh of the slide area, buried under their own captions and squeezed by text boxes.

## 1. Defaults and the house frame

- **Two columns** (figure + text) is the default; three columns for comparison slides. The figure gets its half, and nothing sits under it (§2).
- **Size images by aspect ratio, not by habit.** Never hard-code a vh value by feel (§5).
- **The slide-number chip** occupies **x 1055–1148, y 760–796** (measured; stable across slides — x 1069 for single-digit page numbers, 1055 for two-digit). Keep *fills* as well as text clear of it: the hazard is a box **background rectangle** reaching y ≥ 760, not just glyphs. The DOM overflow check compares element rects to the slide frame only, so it reports clean while a box fill runs under the chip — check explicitly by rect intersection: `keybox.bottom > 760 && keybox.right > 1055`. **Do not pixel-scan for this**: colour thresholds catch antialiased text and the wrong y-window, which produced both a false alarm and a false clear in one session.
- **Reveal.js config**: `controls: false`, `transition: 'none'` (keyboard navigation only; stable renders). The house deck renders at 1180 × 820 with `margin: 0.04`.

**The figure owns its half (§2–§9).**

## 2. Nothing sits below the figure in its column

The failure mode: a two-column slide where the figure column also holds the keybox that comments on the figure. Column height becomes image + caption + box, so the image gets only what is left. That is how a **34vh figure becomes 19vh and then, after the next overflow patch, 12vh**.

Fix: move every box, table and formula that sits below the image out of the column, into a full-width row *under* the columns:

```html
<div class="cols">
  <div><!-- text --></div>
  <div class="figcol"><img …><p class="figcap src">…</p></div>
</div>
<div class="botrow"><!-- the keybox, now full width --></div>
```

This is a double win and always worth doing: a full-width box wraps to fewer lines than the same box at half width, so the row costs less than the column it vacated.

## 3. The caption is the source line, nothing else

Caption = one line: author, year, journal, figure number, link. No description, no reading guide, no "the point of this figure is…". Four-line captions were eating **60–90 px per slide**.

Where the descriptive prose goes: **into speech, not into the file.** The reading guide is what the lecturer *says* while the audience looks at the figure. Do not archive it in `<aside class="notes">` expecting it to be read — the instructor's finals hold 12 speaker-note words across 89 slides (§8), so a note is scratch space at best and never a safety net. If the prose contains something the deck needs, it becomes a visible element (§4), not a note.

House markup:

```html
<p class="figcap src"><span class="srctag">Fig. 2</span> Jordán+ 2006, ApJ 651, L25, Fig. 2 ↗
  <a href="https://arxiv.org/abs/astro-ph/0609371">astro-ph/0609371</a></p>
```

## 4. Before shortening a caption, find the load-bearing numbers

The dangerous step — captions in a dense deck accumulate real content. On the lecture-7 audit, **21 of 33 captions carried a number that appeared nowhere else on the slide**: the 22% BTFR scatter with H₀ = 75.5 ± 2.5, the 0.100 → 0.062 dex fundamental-plane drop, the (−1.06 ± 0.09) z M/L evolution slope, β = 5.0 ± 0.1, the exercise's 3.59 / 3.75 reference fits. Deleting them silently would have erased physics the deck asserts nowhere else.

**Procedure**: diff old captions against the new visible text, extract the numbers unique to each caption, and rescue each into a visible element — normally a one-line clause appended to the box that now sits under the figure:

```html
<p class="tiny center">Replacing L by dynamical M drops the scatter 0.100 → 0.062 dex (26% → 15%).</p>
```

(The source example used `.tiny center`; at final density the credit tier carries no content — write the rescued clause as a body-size `.take` line. See `density-target.md`.)

Citation fragments (arXiv id, volume, page) are *not* load bearing; they belong in the source line.

## 5. Size by aspect ratio, then solve for the space

Two constraints bind, and the tighter one wins:

- **Width fill**: `h = column_width / aspect_ratio`. Past this the image no longer fills its half, so extra height is wasted whitespace. Tall figures (ar < 1) hit this first and want **46–58vh**.
- **Vertical space**: `avail − botrow − caption − what the text column needs`.

Solve it in the browser rather than on paper: binary-search the largest `max-height` for which every column still fits at the real viewport, then write that value into the HTML:

```js
const fits = H => { img.style.maxHeight = H + 'px';
  return Math.max(...[...cols.children].map(c => c.getBoundingClientRect().height)) <= need; };
```

`scripts/solve_fig_height.py` runs this per column and writes results back keyed by `src=` identity — never by match position. Duplicated-attribute hazard (`qa-gate.md`): 17 of 34 `<img>` tags carried two `style` attributes, the solver wrote into the dead second one, and ten slides carried values that had never rendered.

## 6. The text column usually binds — do not steal width with `flex`

When a slide overflows after restructuring, it is almost never the image. Measure *which* column is tallest before fixing anything:

- **Text binds** → cut text (`writing.md` §1). Shrinking the image cannot help; the image is already shorter than the text beside it.
- **Figure binds** → lower `max-height` toward the width-fill value.

**Do not steal width from the text column with `flex`** to give the figure room: a narrower text column wraps to more lines, grows taller, and the slide overflows further than when you started. Extra column width is the only thing that enlarges a **width-bound** figure, so `flex` is worth one try once the text has been cut and the fill is still low — but it is a per-slide bet, not a rule: on one deck, seven wide-aspect slides were given `flex` and only two gained (**+16%, +17%**) while five regressed. Test each, keep the winners, revert the rest. A wide aspect ratio alone does not predict the win; whether the text column has spare lines does.

## 7. Diagnose from rendered pixels, never from the vh attribute

A `max-height` larger than the width-fill value is **inert**: the browser clamps the image to the column width and the extra vh does nothing, so editing the attribute tells you nothing about what changed. Measure the rendered box:

```js
[...slide.querySelectorAll('img')].map(im => im.getBoundingClientRect().height)
```

Compare rendered totals before and after across the whole deck — the only honest check that a pass worked, and the only way to tell a figure that is genuinely squeezed from one that simply cannot grow wider than its column. A slide reporting a "regression" in the attribute may be unchanged on screen.

## 8. When you cut text to free figure space, audit in both directions

Text cuts are the highest-risk edit in this workflow because the failure is silent: the slide still renders, still shows 0 overflow, and a fact is simply gone.

- **Run a numeric-token diff *and* an author-name diff** against the pre-edit file, per slide. The numeric diff catches dropped quantities but not a shortened citation; the author-name check catches the reverse. `Dressler, Lynden-Bell, Burstein, … 1987` → `Dressler, Lynden-Bell et al. 1987` is fine only because the full list survives in the notes.
- **The instructor deletes; he does not archive to notes.** Audit of his three final decks: **12 speaker-note words across 89 slides**, and **~75% of the draft's words simply removed** — nothing relocated. Do NOT dump cut bullets into `<aside class="notes">` expecting them to be used; they will not be read. The load-bearing exception: a number or claim that appears *nowhere else* in the deck must survive somewhere visible (a one-line clause on the slide, or the figure itself), because there is no notes safety net. Rhetoric, meta, and detail are free deletions.

If agents do the cutting, apply their output through the validator in `qa-gate.md` — one that refuses the write on any invariant break and applies the notes payload too; an applier that handled only the edits silently dropped eleven citations at once.

## 9. Inherited margins eat the budget you just measured

Stacking two figures in one column failed to fit until the real cause was found: the theme's `.reveal img { margin: 20px 0 }` plus the caption's own bottom margin added **117 px of invisible spacing** inside the column. The arithmetic said 691 px of children in a 716 px slot; the DOM said 808 px. Always dump the child boxes with their computed margins before trusting a height budget:

```js
[...figcol.children].map(c => ({h: c.getBoundingClientRect().height,
  mt: getComputedStyle(c).marginTop, mb: getComputedStyle(c).marginBottom}))
```

Zero them inside the figure column (`margin: 0` on `.figcol img`, `margin-bottom: 0` on `.figcol .figcap`). Worth more than any caption trim, and the difference between "two figures cannot share a column" and two figures sharing one comfortably.

## 10. Count lines before you cut words

Freeing vertical space buys figure height only if a **whole line disappears**. Removing a clause from the middle of a wrapped paragraph often changes no line count at all: on one deck a two-sentence bluebox trim was predicted to free **18 px and freed 3**, because the removed sentence shared its line with the sentence kept.

- Predict the gain in **lines**, not words — estimate how many wrapped lines the text occupies first (§20's 42 px arithmetic).
- Re-measure the rendered figure height immediately after the cut. If the gain is an order of magnitude below the prediction, the cut bought nothing and the cost is a lost sentence: **revert it**.
- A load-bearing physical claim is worth more than 3 px of figure.

**Part B — cover the page (§11–§18).** A slide that stops two thirds down reads as unfinished even when nothing is wrong with what is there.

## 11. Measure coverage, do not eyeball it

Rasterise every slide and compute, on a coarse grid, the largest empty axis-aligned rectangle and the ink coverage. **Coverage below ~0.82, or a void above ~12% of the page, is a defect worth naming by slide number.** Run the audit before and after, and report both numbers.

## 12. Three kinds of empty — only one is a bug

- **Inherent margin.** The band above the title, the gutter beside a centred block. Nothing to do.
- **Low ink, correct layout.** A scanned journal figure on white paper scores **~0.68** coverage while occupying the whole page. Never "fix" this; it is a property of the source image. Check the bounding box, not the ink.
- **A real void.** Content stops early, or one column is far shorter than its neighbour. The only kind you may act on.

## 13. Fill additively, not distributively — and never by centring

**Additive** = more pixels of something the student needs; always preferred. **Distributive** = stretching a block that is alone on its slide (a divider, a full-width table); acceptable only when the block genuinely has no neighbour to grow against. Rejected experiment: setting a section to a centred flex column so the existing content floats in the middle — tested on **43 slides**, it spread identical content into air above and below and scored *worse* than top alignment on the slides judged by eye. Centring hides a void, it does not fill one.

## 14. The dead space beside a short figure — the biggest single win (fallback only)

When the text column is much taller than the figure column, the figure is capped by its own `max-height`, not by width, and the space beside the text is wasted. Fix: move the slide's box **into the figure column, under the image** — the text column shortens, the figure column gains the box it was missing, and the void becomes content. Diagnose with the height gap between the two columns, not by looking:

```js
const f = cols.querySelector('.figcol').getBoundingClientRect().height;
const t = [...cols.children].find(c => !c.querySelector('img')).getBoundingClientRect().height;
// gap = t - f; if gap > 60 and the text column holds a box, move the box
```

Re-solve figure heights (§5) after every move; this recovered six slides in one pass. **Precedence caveat**: at final density the deck carries no boxes at all (`density-target.md` — every keybox/bluebox dies), so this recipe is subordinate to §2 and applies only to a deck that still carries one.

## 15. Full-width figures: only when the commentary below wraps small

Giving a figure the whole page width (`.figwide` plus an `.underrow` of commentary) is additive, but it pays **only if the text that moves below is short**. Measured across nine attempts:

| slide | figure ar | verdict |
|---|---|---|
| 23 | 2.44 | +226% area. Won decisively |
| 18 | 3.00 | +135%. Won |
| 29 | 1.70 | +24%. Won, then beaten by the column layout |
| 3  | 1.60 | +11%. Marginal |
| 36 | 1.74 | +5%. Noise |
| 11 | 2.00 | **no gain** |
| 13 | 1.96 | **no gain** |
| 16 | 1.89 | **lost 40%** |

Aspect ratio is **not** the predictor. The predictor is **how tall the commentary becomes when it wraps into two or three narrow cells**: a wide figure with three bullets underneath wins; a wide figure with a paragraph and a box underneath loses, because the wrapped text eats the height you freed. Always measure rendered area before and after, and revert the losers.

## 16. A table that owns its slide gets bigger type — grow the type, never the gaps

`.47em` table text is unreadable from the back of a lecture hall. Raising a slide-level table to **`.525em`** with **`.48em`** cell padding fills the page *and* fixes a real defect. Scope it to `section > table` so tables sharing a slide with a figure keep their small size, and re-check overflow afterwards: **two slides overflowed from this change alone** and needed tuning down. Do **not** stretch a sparse table's rows to fill — a table with inflated row gaps reads as emptier than a compact one. Grow the type, never the gaps.

## 17. Reordering: check dependencies, then hunt every slide that enumerates order

Moving whole slides is safe only if nothing references position. Before moving:

1. grep for `next slide`, `previous slide`, `above`, `below`, `#/` fragment links and slide numbers;
2. confirm the deck's own part structure — divider slides sit at fixed positions, so moves stay **inside** a part;
3. **then** search for any slide that lists the methods in order: a summary table, an agenda and a part divider all encode sequence, and they silently contradict a reordered body. One deck needed its s6 and s39 row orders swapped and its s7 divider subtitle reworded after a single move.

Prefer reordering that removes a **use-before-definition** — a slide that names a quantity the next slide defines. That is a real learning defect, and unlike whitespace it is invisible to every automated check.

## 18. When a slide is thin, read its notes before inventing filler

One deck's s13 had a two-panel figure and text that never mentioned the panels; the fix was not layout — the missing explanation was already sitting in that slide's `<aside class="notes">`. Before inventing filler for any under-filled slide, read its notes. Restoring a fact the slide should have had is additive in both senses. (Contrast §8: notes are not an *archive* for cut content; they are a quarry for content that belonged on the slide.)

## 19. Verify a layout change by the metric it moves, on the whole deck

Every change in this file is accepted or rejected on a full-deck rasterise: mean coverage, minimum coverage, count of slides below threshold, largest void per slide, plus 0 console errors, 0 broken images, 0 overflow and per-slide tag parity. A change that improves one slide and is silent about the other 42 is not finished.

**Part C — the pixel budget (§20).**

## 20. One body line is 42 px

At 32 px body type with the house line height, one line of a bullet is **~42 px** on the rendered slide. So an overflow measured in the browser at N px is exactly "cut N/42 lines". Measure the overflow from the DOM (`getBoundingClientRect` over every descendant, against the **787 px section box**) and cut a computed amount — do not trim by feel and re-render five times. On two-column slides, reducing the figure's `max-height` buys back only the difference between the image height and the text height; usually the text column is the constraint (§6). The overflow gate must walk every element that contains a text node, not a tag list — `qa-gate.md`.

## 21. Slide archetypes

The house primitives, one line each; the markup itself is `templates/deck.html`.

| Primitive | When |
|---|---|
| `.cols` + `.figcol` | default two-column: text beside a figure that owns its half (§1, §2) |
| `.botrow` | full-width row under the columns — where a box goes so nothing sits under the figure in its column (§2) |
| `.figwide` + `.underrow` | full-width figure with short commentary cells beneath — §15's winners only |
| `.bleed` / `.divider` | part divider: full-bleed picture, one orientation line, no prose |
| `.title-slide` / `.pillars` | slide 1 doubles as the agenda: deck title + four bold pillar sentences |
| `.qslide` | question slide: the question itself is the slide's content, body size, bold |
| `.take` | the take-home line: one bold sentence at body size, never a box; its rect must be measured for overflow (§20) |
| `.formula` | centred display equation line; `.center` as the alignment utility |
| table ladder + `tr.punch` | native table only as an orientation ladder whose last row (`tr.punch`) carries the verdict — `density-target.md` governs whether it may exist; geometry per §16 |
| `.src` / `.figcap.src` | credit tier for captions, citations and URLs — content rules live in `figures.md` |
