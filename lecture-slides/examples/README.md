# Worked example

An eight-slide deck that uses every archetype with real content, so that the rules in
`../references/` can be seen rather than inferred. It is not a lecture and not a template:
read it, then scaffold from `../templates/deck.html`.

| file | what it is |
|---|---|
| `demo-deck.html` | the deck: title/agenda, two-column, full-width figure, question, part divider, orientation ladder, mirrored two-column, closing line |
| `make_figures.py` | regenerates the five `[course]` plates and schematics in `assets/` (matplotlib) |
| `assets/FIGURE_SOURCES.md` | the licence and verification trail for those five assets |
| `render/` | what the gate produced: `slide-NN.png`, `montage.png`, `qa_report.json` |

## The three commands, and what each answers

```bash
python3 scripts/deck_edit.py  check        examples/demo-deck.html     # markup invariants, per section
python3 scripts/render_deck.py --deck      examples/demo-deck.html --strict
python3 scripts/audit_deck.py  --deck      examples/demo-deck.html --orientation-ladder 6
```

- `deck_edit.py check` — tag parity per section, duplicate `style` attributes, a stray `>`
  after a close tag, every local asset resolving. It edits nothing.
- `render_deck.py` — rasterises all eight slides and runs the *rendered* gate: console
  errors, broken images, overflow over every element holding a direct text node, rendered
  image sizes, and figure-column vs text-column heights. `--strict` makes a failure an exit
  code instead of a sentence.
- `audit_deck.py` — the static density verdicts plus the rendered coverage/void audit. Its
  output is the deck's scorecard: eleven PASS/FAIL lines, each naming the threshold's
  provenance and the slides that miss it.

`--orientation-ladder 6` and `--void-ok 4,8` are how a *declared* exception is made: slide 6
is the one native table the house style allows (and only because it is a ladder whose last row
carries the punchline), and slides 4 and 8 are breath slides where emptiness is the design.
Both are printed in the verdict line — an exemption you cannot see is an exemption you cannot
audit.

## What the example demonstrates that the prose cannot

- **Density is achieved by deletion, not by shrinking.** 38 words per slide median here, and
  the take-away line is one sentence per slide.
- **A figure earns its space.** Each figure slide carries ≥30% of the frame in image, and the
  two-column slides match the figure against a text column of comparable height — the void
  metric measures exactly that mismatch, which is why the text column gained a fifth bullet
  during the build.
- **The gate finds what the eye forgives.** Three defects in this example were invisible in
  the numbers and obvious in the PNG: two matplotlib labels drawn on top of their own
  annotations, and a background plate the renderer caught mid-fade because
  `transition:'none'` does not cover backgrounds.

## Current scorecard

```
deck_edit check   0 violations over 8 sections
render_deck       0 console errors, 0 broken images, 0 overflow slides
audit_deck        11 PASS, 0 FAIL   (median 38 words/slide, median occupancy 0.91,
                                    void inside content block ≤ 20% on every slide)
```