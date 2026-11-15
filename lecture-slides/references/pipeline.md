# Pipeline — the working order for one lecture

The sequence a lecture is built in, the four modes that change it, and where each reference and script applies. Read it at the start of a new or reopened lecture, before any HTML.

## 1. The order

Plan first, always. The plan document (`第N讲课程框架.md`) is the contract with yourself: **never start the HTML until it is written**, and update it after every revision round. Planning language is Chinese; the slides are English.

| # | Step | Governs | Automates |
|---|---|---|---|
| a | **Plan document** from `templates/plan.zh-CN.md`, once the reading is done. It answers the plan's five questions: the narrative (one sentence per part); the physics on each slide; which figure goes where; the in-class exercise; the student report topic. Plus time allocation and the verified-number table. | `templates/plan.zh-CN.md` | — |
| b | **Figure list and sourcing** per slide: identify what each slide must show, source from the literature, crop, verify each crop by a vision read, record provenance. | `figures.md` | `scripts/fetch_pdf.sh`, `scripts/crop_fig.py`, `templates/FIGURE_SOURCES.md` |
| c | **Build the deck short from the start.** Density is a starting condition, not a final polish (the L7 mid-build evidence in `density-target.md`): draft at the finished density, do not draft long and trim. Copy the template rather than a previous lecture's HTML. | `density-target.md`, `writing.md`, `layout.md` | `templates/deck.html` |
| d | **Render + gate loop**, in stage order, until the gate is green. | `qa-gate.md` | `scripts/render_deck.py`, `scripts/audit_deck.py`, `scripts/solve_fig_height.py`, `scripts/deck_edit.py` |
| e | **Vision review of every new or modified slide** — figure relevance, legibility at render size, label collisions inside images, bottom-edge clipping. The DOM gates cannot see any of it. | `qa-gate.md` §6, `figures.md` | a vision-capable subagent on `render/slide-NN.png` |
| f | **Exercise and student report guide** — real public data, three scripts (explore → standardize/fit → derive the result), the report guide on a paper that extends the lecture. | `exercises.md` | `exercise/01_*.py 02_*.py 03_*.py` |
| g | **Update the plan document**: what changed and why, the verification record (rendering, visual QA, exercise results), the decision log. | `templates/plan.zh-CN.md` | — |
| h | **Hand over the HTML deck.** The `.pptx` is assembled by hand in PowerPoint from these pages; this skill produces no conversion. | — | — |

## 2. The four modes

| Mode | Trigger | What differs |
|---|---|---|
| `new` | A lecture from scratch | The full order a → h. |
| `revise` | The instructor reviewed the deck page by page after it passed the gate | Complaints are read as **explanation debt**, not formatting: figure not decoded, membership unstated, no error budget, no share of the budget, zero point missing, title an anecdote (`writing.md`). Every answer goes into the deck *and* into the plan's decision log. Expect the word count to rise: a page-by-page "explain this" round adds information, and the round's cost is recorded as a deliberate trade, not silently absorbed. |
| `audit` | An existing deck measured, not rewritten yet | Run the measurement half of the gate first: words/slide median and max, bullets, nested bullets, tables, keybox/bluebox count, `.small`/`.tiny` content words, figure area per slide, coverage and largest void. Nothing is edited until those numbers are on the table, and every accepted change reports both the before and the after number. |
| `port` | An existing deck moved onto the current template | Replace theme/classes/reveal config from `templates/deck.html` first, then run Stage 1 in full — old markup is where duplicate `style`, `>>` and unsolved figure heights come from (`qa-gate.md`). Content rules from `writing.md` apply only after the port renders clean. |

## 3. Deliverables and their layout

One directory per lecture, next to the hand-assembled deck. Real example, `slides/lecture8/`:

```
slides/lecture8/
├── lecture8.pptx                 # assembled by hand in PowerPoint — not produced here
└── dsh/
    ├── 第8讲课程框架.md            # the plan: narrative, slide list, verified numbers, decision log
    ├── lecture8.html             # the deck (25 slides delivered)
    ├── assets/                   # cropped figures + FIGURE_SOURCES.md
    ├── refs/                     # fetched source PDFs — the evidence behind every number
    ├── render/                   # slide-NN.png, montage.png, qa_report.json, audit.json
    ├── render_deck.py  audit_deck.py  crop_fig.py  fetch_pdf.sh   # optional local copies
    ├── exercise/                 # three scripts + README (+ data)
    └── Student_Report_Guide_<topic>.md
```

**The skill's, not the lecture's:** `templates/*` and `scripts/*`. The scripts take the lecture as an argument — `python3 <skill>/scripts/render_deck.py --deck slides/lectureN/dsh/lectureN.html` — so they are normally run straight from the skill directory, and `init_deck.sh` does not copy them into the lecture. A lecture may keep its own copies (the earlier lectures do, from before the port) but nothing depends on them, and a copy must never be edited in place: when a script is wrong, fix the skill.

**The lecture's own:** the plan document, the deck HTML, `assets/` and its `FIGURE_SOURCES.md`, the `refs/` PDFs, `render/` output, the exercise scripts and data, the report guide.

## 4. Where things go when a lecture is long

Two documents, and they must not merge:

- **The plan** (`第N讲课程框架.md`, Chinese) holds the *numbers and their verification*: one table per part with value · source (journal, volume, page, arXiv id) · **where it was verified** (abstract, table n, section n of the PDF), a separate "not yet verified / deliberately avoided" list naming the slides that therefore stay qualitative, and the decision log — dated entries, one per change, each with its reason. Carry the version in the title (lecture8's reads `v1.4`) and bump it every round.
- **The deck** (English) holds the *message*: what survives the density bar and nothing else.

When content outgrows a slide, it goes into the plan (the number, its provenance, the decision to omit it), or into a figure. It does **not** go into `.small`/`.tiny` text on the slide, and not into speaker notes — see `density-target.md`. The plan's slide list and the deck must agree on slide count and order; a reordering is recorded in the decision log the same round it happens.

## 5. Scripts at a glance

Six scripts, one job each. Every one takes the deck as `--deck DECK.html` or positionally, and exits 0 clean / 1 violations / 2 usage.

| script | answers | touches the deck? |
|---|---|---|
| `deck_edit.py` | Does the markup hold — tag parity per section, duplicate `style`, a stray `>` after a close tag, every asset resolving? | no (`check`); `put`/`edit` write through the invariants, refusing rather than returning a broken document |
| `render_deck.py` | What does it actually look like: console errors, broken images, overflow over every element with a direct text node, rendered image sizes, figure-vs-text column heights? | writes `render/` only |
| `audit_deck.py` | Is it dense enough and is the frame used: words/slide, bullets, tables, boxes, breath slides, figure area, coverage and void? | no |
| `solve_fig_height.py` | How tall may each figure be before its slide overflows — solved in the browser, 4 px granularity? | yes with `--apply`, by `src=` identity, section-scoped |
| `crop_fig.py` | Where does a published figure end and its caption begin, in a 300 dpi page render? | no |
| `fetch_pdf.sh` | Is that arXiv PDF complete (parses, has ≥ N pages, retried 4×)? | no |

Two more are scaffolding rather than gates: `init_deck.sh` builds a lecture directory (deck from the template, vendored runtime *including* the theme fonts, `assets/`, `render/`, `exercise/`, optional plan), and `vendor.sh` re-pins the reveal.js bundle and rewrites its manifest between the table markers, with `--check` for verify-only.
