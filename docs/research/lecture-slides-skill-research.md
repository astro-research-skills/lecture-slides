# lecture-slides — where the skill came from, and what changed in the port

Design record for the `lecture-slides` skill. It exists because the skill's rules are almost
all *measured*, and a reader deserves to know what was measured, on what, and which parts are
calibration rather than law.

## Source

One 885-line working guide, `llm/course_slides_skills.md`, written by the instructor across
lectures 5–8 of the astronomy course and amended twice. It was never a specification; it was
a lessons file that grew:

| Evidence behind the guide | What it produced |
|---|---|
| 2026-10-20 audit of three finished `.pptx` decks against their HTML drafts (L5 32→27, L6 43→34, L9 39→28 slides; 114 drafts, 89 finals) | the measured density bar: 5,300 → 1,280 words, 0.24× |
| 2026-10-12 incident log (duplicate `style` on 17/34 `<img>`, a wrong-section splice, `</div>>`) | the static invariants and the section-scoped editing guard |
| 2026-10-20 mid-build sample of the in-progress L7 deck (22 slides, 543 words) | density is a starting condition, not a final polish |
| 2026-10-21 page-by-page instructor review of L8 | the *explanation debt* chapter (figure decoding, membership criterion, error budget, share of budget, zero point, titles) |
| the 43-slide page-coverage experiment and the nine full-width-figure attempts | the coverage/void thresholds and the "measure, revert the losers" discipline |

The guide is now retired: the skill is the single source of truth, and the workspace copy was
deleted. This note is the only remaining pointer to that provenance.

## Ported 1:1 — where each chapter lives now

| Guide chapter | Skill file |
|---|---|
| §1 plan first | `references/pipeline.md` |
| §2–§3 figures, relevance | `references/figures.md` |
| §4 concise text, §5 hyphen chains | `references/writing.md` |
| §6 practical rules (citations, layout, QA, exercises, plan doc) | split: `writing.md`, `layout.md`, `qa-gate.md`, `exercises.md`, `pipeline.md` |
| §7 the figure owns its half | `references/layout.md` A |
| §8 cover the page | `references/layout.md` B |
| §9 the measured density target | `references/density-target.md` |
| §10 the explanation debt | `references/writing.md` §§5–10, plus `figures.md` (10.7, 10.9, 10.10, 10.12), `qa-gate.md` (10.11) |
| the 32-item checklist | `references/qa-gate.md` §8, reordered into stages |
| §7.10 the `struct.py` hazard, §8.10–8.12 | `references/qa-gate.md` §§1–2, 7 |

Every measured number, threshold, pixel value and citation survived. Where a number was a
measurement on these particular decks, it is marked as calibration.

## Changed in the port — the "update as needed" part

1. **The checklist was reordered and renumbered.** It had §8.10–8.12 wedged between items 20
   and 21, and an `8a/8b/8c` run inside an eight-item list. It is now seven stages, 40 items,
   monotonic, in the order a deck is actually delivered.
2. **The bullet budget contradicted itself** (§4 said ≤4; §9.1 measured 3–5 in the finals).
   Resolved once, in `density-target.md §1`: draft to ≤4, median 3; the finals reach 5 only as
   a flat label list.
3. **§7.1 vs §8.3 vs §9.3 were in conflict** — "nothing below the figure", "move the box under
   the figure", "every box dies". Resolved by precedence: at final density there are no boxes,
   so §8.3 survives only as the fallback for a deck that still carries one.
4. **The native-table question stays open.** §9.3 says every table dies (20/20); §9.7 records
   two styled orientation ladders in the instructor's own in-progress deck. Both facts are in
   `density-target.md §7`, marked unresolved, with the re-check trigger (v3 of that deck) and
   the drafting rule that follows from the majority of the evidence: zero tables.
5. **Hack scripts became CLIs.** `render_slides.py` and `audit_deck.py` hard-coded one deck's
   filename and directory. They are now `render_deck.py --deck …` / `audit_deck.py --deck …`,
   and the regex guards are importable (`deck_edit.py`) instead of copy-pasted.
6. **Blind spots became code.** The source guide warns that the overflow check enumerated tags
   and missed the take-away line; `render_deck.py` walks every element holding a text node. The
   guide warns that a writer reading back its own attribute verifies its own bug;
   `solve_fig_height.py` writes by `src=` identity and asserts no duplicate attributes.
7. **A validator that has never refused anything is now self-tested.** `deck_edit.py selftest`
   builds the three known-bad documents (duplicate `style`, `</div>>`, `<b`/`<br>` imbalance) and
   asserts the check refuses each.

## Added, because the guide's workflow was missing it

- **A vendored reveal.js runtime.** Every deck in the corpus loads reveal.js from jsDelivr. The
  skill's decks carry `vendor/reveal/` — 1.9 MB including the theme fonts that `white.css`
  imports eagerly — so a lecture presents in a room without wifi. `init_deck.sh` copies it, and
  a deck stays one folder you can hand over.
- **A worked, gate-green example.** `examples/demo-deck.html` exercises all eight archetypes and
  passes every gate. Its purpose is to prove the template and the gates agree: if the house CSS
  drifts, the example fails first.
- **The plan document as a template.** Two real `第N讲课程框架.md` files (L7 122 KB, L8 26 KB) were
  reduced to their structure: five planning questions, time allocation, per-slide claim list,
  verified-numbers table with the *place of verification*, a "not verified / deliberately
  avoided" section, and a dated decision log.
- **An asset-budget table in `FIGURE_SOURCES.md`.** The guide's §8.6 says low-resolution assets
  cap the layout, but nothing forced the numbers onto the page; the template now has the table.

## Deliberately not ported

- **`.pptx` generation.** The instructor assembles the deck by hand in PowerPoint; the workspace
  contains no converter, and a lossy HTML→PPTX step would fight every layout rule in the skill.
  `pipeline.md` states the handoff instead of pretending.
- **Course content and personal timings.** Astronomy facts, the 60-minute split, the specific
  lectures' numbers — all of that belongs to each lecture's plan document.
- **The guide's own history.** Where the guide said "amended 2026-10-20 after auditing…", the
  skill keeps only what a future deck needs; the audit's *findings* are the rules, its
  bookkeeping is not.

## Open questions carried forward

1. **Native ladder tables** — unresolved (see above). If the instructor's v3 deck keeps them,
   the drafting rule changes from "zero tables" to "4–5 row styled ladders, last row = punchline".
2. **Do the density numbers generalise?** They are measured on one instructor's astronomy
   lectures. The skill states them as calibration; a second course would produce a second table,
   and the thresholds would need re-measuring rather than copying.
3. **`figure area ≥30%` is a proxy** computed from rendered image boxes, not from ink on the
   page. It correlates with the instructor's 32–44% measured on finals, but the two are not the
   same quantity.
## What building the worked example changed

The eight-slide example was built last, on purpose: it is the first place where the template,
the CSS and the three gates meet real content, and it corrected four things the prose could not.

1. **The void bar was miscalibrated, and the example proved it.** The guide's "void > 12% is a
   defect" was ported as a constant. Measured on the instructor's own shipped lecture8 renders,
   the largest empty rectangle inside the content block reads median 10.5%, p90 17.2%, max
   19.0% — so a 12% gate fails nine of those twenty-five finished slides. The bar is now 20%,
   with the distribution printed beside it, and the measurement was fixed first: page-level void
   includes the symmetric bands above and below a vertically centred block (every centred slide
   scores 15–35% on that), and reveal's progress bar and page chip stretch the ink bounding box
   to the page edge unless they are masked out. Before the fix the example's one-line closing
   slide reported a 67% void that did not exist.
2. **`transition: 'none'` does not cover backgrounds.** Reveal fades `data-background-image` on
   its own clock, so a screenshot 200 ms after `Reveal.slide()` catches the *previous* plate at
   partial opacity. Slide 2 of the example read as a pale pink wash in the PNG and as white in
   the browser. Both the template and `render_deck.py` now set `backgroundTransition: 'none'` —
   the renderer because a gate must not depend on the deck remembering.
3. **Numbers can be green while the slide is wrong.** Two matplotlib annotations were drawn on
   top of their own labels; every density verdict passed. A vision read of the rendered PNG is
   what caught them, which is the guide's stage-6 rule surviving contact with a machine gate.
4. **Two thresholds pull against each other.** `figure area ≥ 30%` wants a taller figure;
   the void metric wants the figure column and the text column to end together. On a two-column
   slide those are the same lever — figure *aspect ratio* — and the example's slide 7 needed a
   fifth bullet in the text column as well as a 1.31 aspect to satisfy both. That interaction is
   not in the guide; it is now in `layout.md` §5 as the thing to adjust.

The scripts also gained what a generalised version needs and a single-deck version never did:
`--deck` alongside the positional path (every reference file documented the flag that the
scripts did not accept), a `--void-ok` declaration that is printed in the verdict line rather
than applied silently, and tolerance for a foreign `qa_report.json` — the instructor's own
lecture8 renders have an older schema and crashed the audit on first contact.
