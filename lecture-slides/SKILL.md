---
name: lecture-slides
description: "Build or revise the lecture slides / course teaching deck — 课件/幻灯片/讲义/做幻灯片/第N讲 — with a Chinese planning document first, then an English reveal.js deck at the instructor's measured density, literature figures cropped from arXiv PDFs, and an ordered delivery gate. Use when the user asks for lecture slides, a course deck, teaching slides, or to revise, densify, audit, or port an existing deck — and for the in-class exercise and student-report guide. Not .pptx authoring (office-pptx), conference talk slides, research reports (research-report), or manuscripts and refereeing (astro-paper, astro-referee). Detail: one message per slide, ~24% of a normal draft's words, figure-dominant, exactly three type sizes; every number is verified against the paper and carries its primary citation; figures are recorded with citation and licence; the gate is static invariants, rendered overflow/console/broken-image checks, a page-coverage audit, and a vision review of the rendered slides. Produces offline HTML (reveal.js, vendored runtime) — the .pptx is assembled by hand afterwards."
---

# lecture-slides

Make a lecture deck the way the instructor actually wants it, on the first pass.

The anti-goal is measured, not rhetorical: a normal draft runs ~5,300 words, and the instructor keeps ~1,280 of them — **0.24×** — while roughly tripling the space his figures occupy. A deck drafted at ordinary slide density is not polished by that edit, it is rewritten. So this skill front-loads the two things that survive the cut — **the plan** and **the figures** — and holds the deck to the density from the first slide written.

Everything here was distilled from one instructor's ten-chapter working guide, written across four astronomy lectures and two audits (114 draft slides, 89 final slides, three finished decks measured). The numbers are calibration from that course, and they are quoted as measurements so you can tell a law from a local habit.

## Before you build

1. **Read `references/pipeline.md`** — the working order, the four modes, the deliverables tree. It tells you which of the other files you need for this job.
2. **Read `references/density-target.md` before writing anything**, not after. It is the target the deck is drafted *to*; reading it at delivery time only buys you a rewrite.
3. **Fix the inputs; ask only what you cannot infer** (bundle the questions): lecture number and title, the course's language pair (this course plans in Chinese, presents in English — follow the user's), the mode (`new` | `revise` | `audit` | `port`), and where the deck lives (`slides/lectureN/dsh/`). If the user pointed at an existing deck, the mode is `revise` or `port`, not `new`.
4. **Scaffold, don't improvise.** `bash scripts/init_deck.sh slides/lectureN/dsh --name lectureN` gives you the plan document, the deck from the house template, the vendored reveal.js and the provenance file. Every deck is self-contained and opens from `file://`.

## The workflow

| # | Step | Governed by | Automated by |
|---|---|---|---|
| 1 | Plan document (`第N讲课程框架.md`) answering the five questions | `pipeline.md` §1 | `templates/plan.zh-CN.md` |
| 2 | Figure list per slide, sourced from the literature and cropped | `figures.md` | `scripts/fetch_pdf.sh`, `scripts/crop_fig.py` |
| 3 | Deck built short from the start, one message per slide | `density-target.md`, `writing.md` | `templates/deck.html` |
| 4 | Render → gate → fix, in stage order | `qa-gate.md` | `scripts/render_deck.py`, `scripts/audit_deck.py`, `scripts/deck_edit.py` |
| 5 | Figure heights solved in the browser, coverage audited | `layout.md` | `scripts/solve_fig_height.py` |
| 6 | Vision review of every new or modified rendered slide | `qa-gate.md` §6 | a vision-capable subagent on `render/slide-NN.png` |
| 7 | Exercise + student report guide | `exercises.md` | `exercise/01_*.py … run_all.py` |
| 8 | Plan document updated: changes, verification record, decision log | `pipeline.md` §1 | — |

The `.pptx` is assembled by hand in PowerPoint afterwards. This skill produces the HTML deck, the renders, the plan and the provenance — no conversion, and no pretending a converter would preserve the layout.

## Iron rules

1. **Plan before HTML.** The plan is the contract: narrative, physics per slide, figures, exercise, report topic. Never start the deck first. (`pipeline.md` §1)
2. **Density is a starting condition, not a final polish.** The instructor's own in-progress deck measured 22 slides / 543 words / median 20 words per slide — already below the finished-deck density. Draft short. (`density-target.md` §7)
3. **Never draw a schematic where a published figure exists.** Literature first, in a fixed order of reliability; a `[course]` drawing carries the tag, the numbers it uses, and their source. (`figures.md`)
4. **The figure owns its half of the slide.** Nothing sits below it in its column; the caption is the source line only. A figure that could be bigger is a slide that is wrong. (`layout.md` §2–§3)
5. **Exactly three type roles: title, message, credit.** Anything that is neither a message the audience reads at body size nor a credit at 11–16 pt gets deleted, not shrunk. (`density-target.md` §5)
6. **Bold is the only emphasis**, and it means "this is the sentence to remember". No boxes, no coloured emphasis, no italics for emphasis. (`density-target.md` §6)
7. **Every number is verified against the paper, not memory**, and every claim carries its primary citation on the slide. A figure credit is a claim too. (`figures.md`, `writing.md`)
8. **The gate is run, not believed** — and after a large change, cross-checked against one independent observer reading the delivered pixels. A clean verdict after a rewrite is a claim to be tested. (`qa-gate.md`)
9. **No `.pptx`, no CDN.** The deck is HTML with a vendored runtime so it presents in a room without wifi.

## Modes

| Mode | When | What it means |
|---|---|---|
| `new` | a lecture from scratch | the full eight steps |
| `revise` | the instructor reviewed the deck page by page | complaints are **explanation debt**, not formatting: decode the figure, state the membership criterion, give the error budget, quote the share, define the zero, fix the title. Word count may legitimately rise — record the trade. |
| `audit` | an existing deck to be measured before it is touched | report numbers before/after (words/slide median and max, bullets, tables, boxes, figure area, coverage, largest void) and edit nothing until they are on the table |
| `port` | an existing deck onto the current template | theme and markup first, full static gate second, content rules last |

## Files

| Task | File |
|---|---|
| Working order, modes, deliverables tree, what goes in the plan vs the deck | `references/pipeline.md` |
| The measured density bar, what survives, what dies, structure moves, type roles | `references/density-target.md` |
| Bullet economy, banned constructions, explanation debt, titles, numbers and citations | `references/writing.md` |
| Sourcing, cropping, relevance, `[course]` schematics, licences, render-size legibility | `references/figures.md` |
| The figure's half of the slide, page coverage, empty space, the 42 px line budget | `references/layout.md` |
| The six-stage delivery gate and the consolidated checklist | `references/qa-gate.md` |
| In-class exercise and student report guide | `references/exercises.md` |
| Accumulated lessons — read before building, append after a correction | `references/lessons.md` |
| House deck (CSS + eight slide archetypes), plan skeleton, provenance table | `templates/deck.html`, `templates/plan.zh-CN.md`, `templates/FIGURE_SOURCES.md` |
| Guarded editing, rendering, auditing, height solving, cropping, fetching, vendoring, scaffolding | `scripts/deck_edit.py`, `render_deck.py`, `audit_deck.py`, `solve_fig_height.py`, `crop_fig.py`, `fetch_pdf.sh`, `vendor.sh`, `init_deck.sh` |
| A gate-green worked deck (8 slides, every archetype), its figure generator and its provenance trail | `examples/demo-deck.html`, `examples/make_figures.py`, `examples/assets/FIGURE_SOURCES.md`, `examples/render/` |

## Anti-patterns

| Pattern | Why it fails | Do instead |
|---|---|---|
| Writing the deck first, then the plan | Every later question (which figure, which claim, which order) reopens the deck | Plan document first; it holds the numbers and their verification |
| Drafting at 300 words/slide and planning to trim | The instructor's cut is ~90% on a draft that dense; the deck you wrote is not the deck he keeps | Draft at 20–70 words/slide |
| Nested sub-bullets and `.small`/`.tiny` content | The detail tier does not exist in the finals — 13–22% of draft words sat there and were deleted, not enlarged | Promote to body size or cut; there is no fourth type role |
| A table of comparison | 20 of 20 draft tables died; the three that earned their place came back as *figures* | One bold sentence, or an annotated plot |
| A keybox/bluebox for the take-home | 63 boxes → 0 | One bold body-size line |
| Descriptive captions ("as we can see, the slope…") | The reading guide is spoken; 13–22% of draft words were caption prose | Caption = author, year, journal, figure, link |
| A schematic where a paper has the figure | Invents what the literature already shows honestly | Search Commons → reviews → papers; crop and verify |
| Hard-coding a vh value for a figure | Three successive "fixes" shrank a figure to 12vh | Solve the height in the browser, measure rendered boxes |
| Trusting "0 problems" after a rewrite | The gate measured a tag list and missed the take-away line on five slides | Walk every text-bearing element; cross-check with a rendered-page review |
| Reporting an exercise done after reading its code | Self-reported success is not evidence | `python run_all.py` from a clean checkout, and land the published value |

## Setup

The vendored reveal.js runtime (≈1.9 MB, MIT + OFL fonts) is committed under `assets/vendor/reveal/`, so a scaffolded deck presents offline with nothing to install. Run `bash scripts/vendor.sh` only to re-pin it, or to repair a damaged copy; `--check` verifies without writing.

Python needs `numpy`, `Pillow` and `playwright` (with a Chromium); `pdftoppm`/`pdfinfo` come from poppler. `render_deck.py` will tell you if Chromium is missing. `examples/make_figures.py` additionally needs `matplotlib`.