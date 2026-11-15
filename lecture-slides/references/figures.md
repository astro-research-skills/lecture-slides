# Figures — sourcing, relevance, legibility, provenance

Everything about getting a figure onto a slide and being honest about it: where it comes from, whether it shows the slide's point, when you may draw one instead, whether it survives render size, and what gets recorded. Read this before placing or replacing any figure. Whether the figure's *content* earns the slide at all is `density-target.md`; caption geometry and height solving are `layout.md`.

## 1. Never draw a schematic when a published figure exists

The sourcing ladder, ranked by reliability. Climb down it only when the rung above has nothing:

| Rank | Source | What it buys / costs |
|---|---|---|
| 1 | arXiv PDF → `pdftoppm` at 300 dpi → PIL crop | Best: original vector-quality figures |
| 2 | ar5iv asset URLs | Fast but unreliable — check for the ~20 KB placeholder image |
| 3 | Agency press images — ESO, ESA/Hubble, NASA/CXC | Beautiful, but sometimes not exactly the right figure |
| 4 | ADS scanned PDFs | Pre-1990 papers; grainy but authentic |

Course-made figures enter only where no literature equivalent exists (e.g. the precision timeline plot), and then only under rule 3.

The per-figure workflow:

1. **Identify what each slide needs to show** — before searching.
2. **Search** arXiv, ADS, ESA/Hubble, ESO, NASA/CXC for the original figure. For a general "what figures exist for X" request, start at rule 7 instead.
3. **Download the PDF** with `scripts/fetch_pdf.sh` (fetch with validation), render the page at **300 dpi** with `pdftoppm`.
4. **Crop with PIL** — `scripts/crop_fig.py`: exclude the caption text, keep axis labels and legends.
5. **Verify the crop** by reading it back with a vision-capable model (rule 2 covers the slide-level check). On a two-column page the tallest ink band spans text *and* figure, so `--band auto` returns the column pair: find the empty column gap and pass `--x0/--x1` (in the 300 dpi render, e.g. gap at x 1173–1271 → `--x0 1271`).
6. **Document it** in `assets/FIGURE_SOURCES.md` with full citation and link (rule 8).

## 2. Relevance: does this figure show *this slide's* key point?

Before placing, ask: "Does this figure directly illustrate the key point of this slide?" Three failure modes observed in this course, each with its fix:

| Placed | Slide was about | Why it failed | Fix |
|---|---|---|---|
| Artist's impression of the progenitor channel | ejecta composition | wrong topic | simulation figure of the layered debris |
| Hubble residual vs host-mass plot | the mass step | the step had already been corrected away — the plot is flat by construction | Sullivan et al. 2010 Fig. 4, which shows the step |
| Gamma-ray spectrum | *why* ⁵⁶Ni sets the luminosity | shows the detection, not the physics | decay-chain diagram (Diehl 2022 Fig. 4) + ejecta composition plot (Iwamoto 1999 Fig. 14) |

**Verification step**: after placing every figure, ask a vision-capable model to look at the *rendered slide* and confirm the figure matches the caption and the slide topic. This caught multiple mismatches. Run it on every new or modified slide; the gate mechanics live in `qa-gate.md`.

## 3. Self-drawn schematics are allowed — under three conditions

Lecture 8 used eighteen literature crops and drew two figures. Both drawn ones were places where no published figure shows the mechanism at lecture scale: a cluster in real space versus redshift space (fingers of God), and a flux limit cutting through a magnitude spread (Malmquist bias). The conditions:

1. Mark it **`[course]`** in the caption, visibly.
2. Print on the slide the numbers the drawing uses, with their source — the fog schematic's "±925 km s⁻¹ becomes ±13 Mpc" works because the next bullet quotes the Norma dispersion.
3. Never imitate a journal plate: no fake axes ranges, no invented data, no fabricated uncertainty. Draw the *geometry* of the effect, not a simulation of it.

## 4. Judge a figure at render size, not at source resolution

A 300 dpi crop can be perfectly sharp and still unreadable when the slide renders it 600 px wide. The check is on the delivered pixels, not the source PDF:

- tick numerals at least **~9 px** tall;
- axis titles at least **~11 px**;
- no legend text smaller than the body of the plot.

If a crop only works when zoomed, it is the wrong figure for the slide — crop tighter (drop panels; drop the legend if the caption carries it) or replace it (back to rule 1's ladder). The height it renders at is solved in `layout.md`; a solved height is only legal if it clears the floors above. And read the delivered image, not the data: a figure can be numerically fine and visually empty (see `qa-gate.md`).

## 5. Low-resolution assets silently cap what any layout can do

Several assets in the reference deck are 525–950 px wide. A 550 px column already renders them at ~1x, so no amount of CSS buys more detail, and full-page width would upscale them into mush. Before planning any figure enlargement, print the asset table:

| Field | Why |
|---|---|
| intrinsic px width × height | the ceiling on real detail |
| aspect ratio | the input to `layout.md`'s height solve |
| upscale factor at intended display width | display px ÷ asset px |

Re-source from the publisher when the factor exceeds **~1.5x**; do not enlarge.

## 6. Citations are numbers too

Number hygiene on the slide is `writing.md` §11; this rule is the same discipline applied to the credit line, which is a claim like any other.

A figure credit is a claim and gets the same verification as a measurement. In this build a figure was sourced from "Li & White 2008, MNRAS 384, 145" — a truncation of **384, 1459** ("Masses for the Local Group and the Milky Way", arXiv:0710.3740). The first arXiv id tried under the truncated reference belonged to an unrelated solar-physics paper. Check author, year, volume, **first page** and title against the PDF's own front matter, and quote the abstract's numbers from the PDF, not from a summary written earlier in the session.

## 7. A general figure hunt starts at Wikimedia Commons

For any request that is "what figures exist for X", not "what does paper Y's Fig. 3 show". Evidence: asked for figures showing the Local Group's structure, the stack of papers in hand returned six crops — Aitoff maps, velocity–distance diagrams, an orbit integration. The instructor found a better figure in two minutes, on Wikipedia: the Wikimedia file *Local Group and nearest galaxies* (Antonio Ciccolella, CC BY-SA 4.0) — a drawn 3-D view with the Milky Way at the centre, M31 and M33 above it, the far-side galaxies, and shells marked at 2, 4, 6 and 8 million light-years. It answers "what does the Local Group look like" in a way no journal figure in the stack did, because **journal figures answer the authors' question, not the lecturer's**.

Search order:

1. **Wikimedia Commons and the Wikipedia article** for the object — first, not last. Commons files carry a licence, are usually purpose-drawn for teaching, and are already at slide-friendly aspect ratios. Search `site:commons.wikimedia.org` plus the object name, and read `Category:<object>` — the category page is a browsable gallery.
2. **The review literature** — a review's figures are often redrawn for teaching; a research paper's are not.
3. **The primary papers** — rule 1's ladder.

Licence and honesty duties:

- Check the licence on the **file description page**, not the image: author, licence, and whether the uploader claims own work. Record all three in the provenance file (rule 8).
- **CC BY-SA** obliges the credit *and* the licence to appear **in the slide**, plus an indication that changes were made if the image was cropped. So the caption itself reads `A. Ciccolella, Wikimedia Commons, CC BY-SA 4.0 … title cropped` — not just the sources file.
- Two things Commons illustrations get wrong: **scale statements** (this one: the galaxy photographs are not to scale — the positions are) and **provenance of the data** behind a drawing. State both in the caption or a bullet.
- A dark, poster-like illustration can beat a clean plot as an opening image, but it will not carry numbers. Pair it with the quantitative claim in the text rather than replacing it.

## 8. Provenance: `assets/FIGURE_SOURCES.md`

One row per asset, recording: the slide it appears on, the source paper with full citation and link, the figure/panel number, the licence, the crop box or transform, and the verification status. The starting skeleton is the sibling template `templates/FIGURE_SOURCES.md`.

| slide | asset | source (citation + link) | fig/panel | licence | crop box / transform | verified |
|---|---|---|---|---|---|---|
| 3 | `hubble1929_fig1.png` | Hubble 1929, PNAS **15**, 168, Fig. 1 | Fig. 1 | ADS scan | scanned PDF → `pdftoppm` 300 dpi → crop to axes | vision QA pass |
| 7 | `liwhite2008_lg_mass.png` | Li & White 2008, MNRAS **384**, 1459, arXiv:0710.3740 | Fig. 1 | literature crop | arXiv PDF → 300 dpi → PIL box | vision QA pass |
| 22 | `fog_schematic.png` | `[course]` own drawing | — | — | matplotlib | vision QA pass |

The crop box must be reproducible — page, dpi and box coordinates — so a re-crop after a layout change gives the same figure. Rule 6 applies to every citation in this file: volume, first page, arXiv id and title verified against the PDF front matter, never from session memory.
