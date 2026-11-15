# lecture-slides

A [DeepSeek Harness](https://github.com/deepseek-ai) (DSH) skill that builds a course lecture deck the way the instructor actually ships one, on the first pass: a **Chinese planning document** first (narrative, physics per slide, verified numbers with sources, decision log), then an **English reveal.js deck** written at the instructor's measured density — one message per slide, ~24% of a normal draft's words, figure-dominant, exactly three type sizes — with **literature figures cropped from arXiv PDFs** and recorded with citation and licence, and finally an ordered **delivery gate** (static invariants, rendered overflow/console/broken-image checks, page-coverage audit) plus a vision review of the rendered slides.

The measured standard, not a vibe: an audit of 114 draft slides against 89 finished slides says the instructor keeps **0.24× the words** and roughly triples figure coverage. A deck drafted at ordinary density is not polished by that edit — it is rewritten. This skill drafts to the target instead of trimming toward it.

- **Output:** an offline-capable reveal.js deck (vendored runtime — presents in a room without wifi), its rendered PNGs, `FIGURE_SOURCES.md` provenance, the plan document, and the lecture's in-class exercise. **HTML, not `.pptx`** — the PowerPoint file is assembled by hand afterwards.
- **Modes:** `new`, `revise` (instructor reviewed page by page — complaints treated as *explanation debt*), `audit` (measure before editing), `port` (onto the current template).
- **Self-improving:** the skill reads and appends to [`lecture-slides/references/lessons.md`](lecture-slides/references/lessons.md).

## Install

DSH discovers skills at `~/.dsh/skills/<name>/SKILL.md`. Clone this repo anywhere and symlink the skill directory:

```bash
git clone git@github.com:astro-research-skills/lecture-slides.git
ln -s "$(pwd)/lecture-slides/lecture-slides" ~/.dsh/skills/lecture-slides
```

Then open a new DSH session. `lecture-slides/scripts/init_deck.sh` scaffolds each new deck with the house template and the vendored reveal.js runtime, so decks stay self-contained.

## Requirements

Python `numpy`, `Pillow`, and `playwright` (with Chromium); `pdftoppm`/`pdfinfo` from poppler for figure crops. `render_deck.py` tells you if Chromium is missing. `examples/make_figures.py` additionally needs `matplotlib`. The vendored reveal.js runtime (MIT + OFL fonts) is committed, so nothing needs downloading for normal use.

## Repository layout

```text
lecture-slides/
├── README.md
├── LICENSE                       # MIT
├── docs/research/                # the design research behind the skill
└── lecture-slides/               # the skill itself
    ├── SKILL.md                  # entry point: workflow, iron rules, modes, anti-patterns
    ├── references/               # pipeline, density target, writing, figures, layout,
    │                             # QA gate, exercises, lessons (loaded on demand)
    ├── templates/                # deck.html (house theme + 8 archetypes), plan, provenance
    ├── scripts/                  # deck_edit, render_deck, audit_deck, solve_fig_height,
    │                             # crop_fig, fetch_pdf, vendor, init_deck
    ├── assets/vendor/reveal/     # reveal.js 4.6.1 + theme fonts (offline)
    └── examples/                 # a gate-green worked deck + renders + QA report
```

## Sibling skills

Part of the [astro-research-skills](https://github.com/astro-research-skills) organization:

- [research-report](https://github.com/astro-research-skills/research-report) — session-work reports (BLUF-first HTML/Markdown with verification matrices).
- [research-copilot](https://github.com/astro-research-skills/research-copilot) — the astronomy publication pipeline: ADS/arXiv literature, AASTeX manuscripts, simulated refereeing.

## License and credits

- Code and text: [MIT](LICENSE), © 2026 Shangguan Jinyi.
- Vendored reveal.js (MIT) and Source Sans Pro fonts (SIL OFL 1.1) keep their own licenses — see `lecture-slides/assets/vendor/reveal/THIRD_PARTY_NOTICES.md`.
