# Density target — the instructor's measured density

What "the instructor's density" actually is, measured rather than guessed: the 2026-10-20 audit of this course's three finished pptx decks against their HTML drafts (L5 32→27 slides, L6 43→34, L9 39→28; 89 final slides, 114 draft slides). Read this before drafting a deck and again before delivering — a draft that misses these targets earns a 75% rewrite, not a polish. Every number below is calibration from the audited decks, not a universal law.

## 1. The headline numbers

| Metric | Draft (avg of L5/L6/L9) | Final (instructor) |
|---|---|---|
| total words | ~5,300 | ~1,280 (**0.24×**) |
| words / slide (median) | ~130 | **26–68** |
| words / slide (max) | ~400 | ~100–140 |
| slides ≤15 words | 0 | **5–11 per deck** |
| bullets / slide (median) | 3 (but 2-line, nested) | **3–5, one line each** |
| nested sub-bullets | 69/114 slides | **1 line in 89 slides** |
| tables | 20 | **0** |
| keybox/bluebox | 63 | **0** |
| figures / slide (median) | 0.5–1 | **1.5–2** |
| figure area / slide (median) | ~15% | **32–44%** |
| body font floor | 0.42–0.5em (`.tiny`) | **20pt** (18pt absolute floor) |
| speaker-note words | 700+ | **12 across 89 slides** |

**The one line: the instructor keeps ~24% of the words and roughly triples the figure coverage.** Text and figures trade places — every word cut becomes figure area or white space, never a smaller font.

Reconciled bullet budget, stated once here: draft to **≤4 bullets per slide**, median 3, one line each; the finals measure 3–5 because a 5-bullet slide is always a flat label list, never nested prose. More than 4 real points → split the slide.

Totals footnote: the final word counts include OMML equation text recovered from `a14:m/m:t` (L5 875, L6 1,259, L9 1,737; L7 543). With it included, the ratios and medians above shift by <1.5% and stand.

## 2. What survives the cut — keep these

- **The physics logic chain, verbatim.** L9's width–luminosity slide kept the draft's four-step causal chain word-for-word: "More ⁵⁶Ni → hotter ejecta → Fe III stays ionized → B-band persists". If the draft reasoned correctly, the reasoning is the value; keep it, drop everything around it.
- **Load-bearing numbers with their citation.** "M_B = −19.253 ± 0.027 (SH0ES)", "σ ≈ 0.6 mag (Kowal 1968)", "ρ₀ ≈ 0.1 M☉/pc³". A number that *is* the point survives even at full precision.
- **The verdict / punchline.** "Only SNe Ia come from white dwarfs"; "Classes are observational; engines are physics"; "In the 1% era, the science of distance becomes the science of systematics."
- **People, dates, and portraits.** History slides gain faces (Herschel, Shapley, Oort, Genzel, Townes, Freedman, Riess). The draft named them; the final *shows* them and bolds the name.
- **A question or metaphor in the title.** "Why does a standard candle have to pulsate?", "a lighthouse built by the helium flash", "Second Careers of the Rejected". Titles are rhetorical; bullets are not (`writing.md`).

## 3. What dies — delete it, do not shrink it

- **Every table.** All 20 draft tables died. Three came back as *figures* (a plotted ladder, an annotated sky map); the rest were replaced by one bold sentence or a picture the lecturer points at. §7's mid-build evidence is the only thing that has since cast doubt — unresolved, and not yet a license.
- **Every keybox/bluebox.** 63 → 0. The take-home becomes a plain bold body-size line (§6). Resolving the guide's own contradiction: at final density there are no boxes at all; the box-relocation advice in `layout.md` is the fallback for a deck that still carries one, and is subordinate to this.
- **Every nested sub-bullet and every `.small`/`.tiny` content run.** The audit's central finding: 13–22% of every draft's words sat in `.small` (0.6em), `.tiny` (0.5em) or `.figcap`, and essentially all of it was deleted, not enlarged. The detail tier does not exist in the finals: if it was too small to read, it was too minor to include.
- **The pedagogy / meta layer.** Course-map slides, "where we are in the course", think-pair-share prompts, "Part N in one sentence" dividers, discussion-question slides, reference-list slides, cross-lecture pointers ("recap of L2", "you will fit this in the exercise"). ~1,100 words/deck.
- **Hedges and caveats that are not the point.** "A small SD contribution is not excluded", "Ic and SLSN progenitors still indirect". The instructor keeps a caveat only when it *is* the lesson (e.g. "w(z) inherits a redshift-dependent bias").
- **Descriptive figure captions.** Caption prose was part of that 13–22% deleted-small-text run. The finals keep a 3–15-word source line at 11–16pt ("Turatto 2003, Fig. 2"). The reading guide is *spoken* — and since the finals hold 12 speaker-note words across 89 slides, "spoken" lives in the lecture, not archived in notes. Caption mechanics: `figures.md` and `layout.md`.

## 4. How the instructor re-arranges — the six structure moves

1. **The title slide is the agenda.** 60pt title + four 32pt bold pillars (the deck's parts) + 24pt contact line. No separate "course map" slide. Build the pillars into slide 1.
2. **Dividers become full-bleed pictures, 0 words.** The draft's "Part 1 / Leaving the Milky Way" text panels survive as 63–80%-area photographs with the part title baked into the image. A divider's job is a visual breath + one line of orientation, not a paragraph.
3. **One paper = one slide = one claim.** The H₀-debate became 7 alternating testimony slides (Freedman / Riess portrait + a single bold claim + "Author (Year)"), replacing the draft's 111-word audit tables. Decompose a dense comparison into a sequence of one-claim slides.
4. **Repeated titles group a build-up.** Consecutive slides share a title to signal one argument unfolding: "Single degenerate vs double degenerate" ×2 (define, then test), "Two Candles…" ×9, "Measuring R₀" ×2. Repeat the title instead of coining a new one when a slide continues the same thread; the audience tracks the argument, not a list of topics.
5. **The wordiest slides go last.** Mechanism/history slides that legitimately carry 100–140 words (the ⁵⁶Ni decay chain, "what SNe cannot decide alone") sit in the back third; the front is picture-dominant. Do not spread the dense slides evenly.
6. **Detail is absorbed *into* the figure.** The R₀-century timeline, the Galactic-address table, the exercise's punchline (H₀ = 71.9 → 68.3) all moved from prose into an annotated plot. When a table dies, ask whether its content belongs inside the image, not in a smaller font.

## 5. Type roles — exactly three tiers, no fourth

| Role | Size | Lives in |
|---|---|---|
| Title | 44–60pt (deck title 60pt; slide titles ~44pt, often inheriting from the master) | titles |
| Message / body | 20–28pt, median 24pt | **the floor for anything the audience reads** |
| Credit / source / URL | 11–16pt | citations, figure sources, links only |

Decision rule per fragment: is this a 24pt message, or is it an 11pt credit? If it is neither, cut it. Do not create a 14pt middle tier. The drafts' `.small`/`.tiny` *content* — the thing the instructor called "tiny information" — maps to nothing in the finals: it was either promoted to 24pt body or deleted (§3).

## 6. Bold is the only emphasis, and it means "take-home"

The finals have no colored boxes, no italics-for-emphasis, no highlight bars. **Bold marks the one sentence per slide the audience should remember** — the measured bold share is 11–37% of words (calibration from the three audited decks). Two patterns:

- **Bold the whole claim line** when it is the punchline: "**0.07 mag makes a big difference!**", "**Diversifying candles and anchors is the only road to the truth**".
- **Bold only the lead-in label** when the bullet is a list item: "**Test 1:** surviving companion: …", "**Old (delayed) component**", "**Arnett's rule:** L_peak ≈ L_decay". The label is bold, the support is plain. This is how a 9-bullet slide stays grabbable: scan the bold labels, get the argument.

Use the accent color (brick red) sparingly — the instructor reserves it for the odd hero word ("SPIN!") and lets bold do the rest.

## 7. Building at final density — mid-build evidence (L7, 2026-10-20), and one open question

His in-progress "Distances from Galaxy Properties" deck (22 of a planned ~35 slides built) answers the question the finished decks cannot: does he draft long and trim, or build short from the start? **He builds short from the start — density is a starting condition, not a final polish.**

- **22 slides, 543 words, median 20 words/slide, 10 slides ≤15 words**, 2 figures/slide at 47% median area — already at (in fact below) the finished-deck density of §1.
- **The title slide is a template with four 32pt "Key point" slots still unfilled.** The four-pillar agenda is a slot to fill, so a draft must hand over the four pillar *sentences*, each ≤6 words.
- **Type roles at build time**: 60pt deck title, 32pt pillar / inline heading, 20–24pt body, 16pt bold person name, 14pt citation, 11pt URL. Same three tiers as §5, with a dedicated bold slot for a person's name beside a 14pt paper citation.
- **Draft-to-final ratio on the built portion ≈ 8–9%** (≈6,800 draft words → 543) — harsher than the 22–26% of the finished L5/L6/L9, because that draft was written at 326 words/slide. Only a draft that is already sparse survives a ~90% cut.
- **Open question — native tables on "map" slides. Not settled; do not present it as settled either way.** This is the only one of his decks with native tables (2), both on the two orientation slides (rung/limit ladder; statistics vs dynamics). Both are *styled* — navy header band, zebra rows, and on F4 a highlighted final row with a drop shadow — so they are deliberate, not pasted scaffolding. Counter-evidence: 20/20 draft tables died in his finished decks, one cell is a transcription mangle, and the same citation sits at 12pt on one slide and 14pt on the next. Working hypothesis: a **4–5 row ladder/comparison table** survives on an orientation slide when its last row carries the punchline; prose tables still die. **Re-check at v3 of this deck.** Until that re-check resolves it, the drafting rule stays §3: zero tables.

## 8. Checking density mechanically

`scripts/audit_deck.py --deck <file.html>` computes the static per-slide stats — words, bullets, nesting depth, tables, boxes, type tiers, figure area — no rendering needed. The deck passes the density gate when all of these hold (thresholds from the finals in §1):

- median ≤60 words/slide
- no slide >140 words
- 0 tables
- 0 keybox/bluebox
- nothing the audience must read outside body size — no content words in `.small`/`.tiny`/`.figcap` (§3, §5)
- figure area ≥30% on figure slides
- ≤15-word slides present (the finals carry 5–11 per deck; a deck with none is not at density)

The staged audit procedure and the delivery checklist live in `qa-gate.md`; making the figures physically big is `layout.md`; writing the surviving words is `writing.md`.
