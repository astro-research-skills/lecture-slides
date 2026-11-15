# Exercises and the student report guide

How to design the in-class coding exercise and the student report guide that every lecture
ships alongside its deck. Read when writing an exercise, its README, or a report task. The
deck-side rules referenced here live in `density-target.md`, `writing.md` and `qa-gate.md`.

## 1. Exercise: three scripts, one punchline

Three stages — explore → standardize/fit → derive the key result — as numbered standalone
scripts plus a `run_all.py` driver. The course's own layout, as shipped in
`slides/lecture2/exercise/` and `slides/lecture4/exercise/`:

| Stage | Lecture 2 — M4 distance | Lecture 4 — Cepheid Leavitt law |
|---|---|---|
| explore / fetch | `01_download_m4_gaia.py` — ESA Gaia Archive query, saves the field catalogue | `01_download_gaia_light_curves.py` — Gaia DR3 epoch photometry via DataLink |
| standardize / select / fit | `02_select_m4_members.py` — quality cuts, proper-motion clump | `02_measure_periods.py` — GLS periodogram over 1.5–50 d, folded curves |
| derive the key result | `04_estimate_m4_parallax.py` — weighted-mean parallax → naive distance | `03_period_magnitude_relation.py` — intensity-mean `M_G`, PL fit about pivot |
| driver | `run_all.py` runs the four steps in order | `run_all.py` runs 01–03 |

Every stage must do two named things, and the README lists both:

- **Print its numbers** to stdout — L2 `01` prints the fetched source count, `02` prints
  input / after-cuts / member counts, `04` echoes the full parallax-and-distance report;
  every script's last line names where its output went.
- **Save its artefacts** — `data/` for intermediate CSVs, `figures/` for PNGs, `results/` for
  the final table/report; `requirements.txt` pins the environment.

Layout rules observed in the shipped directories:

- Each script also runs standalone (`python 02_measure_periods.py`); the chain is wired
  through files on disk, not shared state. The README gives the per-step command, what it
  prints, and what to look at.
- Slow one-off queries run once and ship their output: `00_select_nearest_sample.py` (L4)
  contains the full archive query defining the sample, but the result table
  (`data/nearest_10_gaia_cepheids.csv`) is checked in because archive queries are slow.
- Three or four numbered scripts are both fine; what must survive is the three-stage order.
  L2 inserts `03_plot_m4_diagnostics.py` (sky, proper-motion, CMD, parallax plots) as the
  explore stage's visual step.
- Group variant: `slides/lecture3/exercise/` splits one dataset between two groups
  (`GROUP_A_PLEIADES.md`, `GROUP_B_NGC6397.md`) with a `JOINT_COMPARISON.md` at the end.
  Each sheet follows: question → procedure → questions to answer → deliverables → teaching note.

## 2. Real, public data only

The source list: **Pantheon+, CDS catalogs, CSP photometry**. In practice this course used
Gaia DR3 through the ESA Gaia Archive in all three exercise directories, plus public tables
behind it (Baumgardt–Vasiliev globular-cluster pages, SIMBAD/CDS). Same bar for report-guide
data: **CDS, GitHub, survey releases** — nothing that needs a private login or a favour.
Download scripts reuse local files and fetch only what is missing (L4), so the exercise runs
offline from checked-in `data/` and refreshes when online.

## 3. The expected result must match the published value — within stated simplifications

So the exercise must carry three explicit pieces, or the rule cannot be checked:

1. **A reference value with citation and tolerance.** L2: Baumgardt & Vasiliev (2021) place
   M4 near 1.83–1.85 kpc against the exercise's 1.8906 ± 0.0358 kpc (0.01 mas systematic
   floor included). L4: the reference line is Breuval et al. 2022, ApJ 939, 89, Table 4,
   `M_G = (−3.112±0.060)[log P−0.7] − (3.578±0.058)`, drawn dashed on the student's fit.
2. **A named simplifications list, in the README.** L2's "Teaching caveat": no
   source-by-source parallax zero-point correction; formal error reported separately from a
   representative spatial-systematic floor. L4 lists its omissions likewise: zero-point
   uncertainty, photometric systematics, extinction, binarity, instability-strip width.
3. **An agreement verdict.** Where the simplifications guarantee a miss, the README says so
   and converts it into work: the ten-star L4 fit is "intentionally crude. Its disagreement
   is a prompt for students to diagnose the assumptions, not evidence against the Leavitt
   law" — the follow-ups are exactly the missing physics (add literature extinctions, apply
   the zero-point treatment, re-fit in a Wesenheit magnitude).

## 4. The punchline connects to the lecture's message

The exercise exists so students reproduce the lecture's central claim in their own hands.
The source's example: the exercise's H₀ = 71.9 → 68.3 result — in the final deck that
punchline moved out of prose and into an annotated figure (`density-target.md`, structure
moves). Design the lecture's message first, then the exercise that lands it; not the reverse.

## 5. Test the scripts end to end before delivery

Checklist item 38 — this is also a gate item (`qa-gate.md`). `python run_all.py` from a clean
checkout must exit 0, print its numbers, write every artefact named in §1, and land inside
the expectation of §3. Never report an exercise "done" from reading the code. The exercise
results go into the framework document's verification record (`pipeline.md`), which is
updated after every revision round.

## 6. Student report guide

- The paper must **extend** the lecture, not restate its content.
- Its data must be publicly available: CDS, GitHub, survey releases (§2 applies).
- The guide is written to a fixed skeleton before delivery (checklist item 39); the grading
  bar is in the guide, not only in speech.

| Section | Content |
|---|---|
| Paper choice | one that extends the lecture — checked against "not the same content" |
| 30-min structure | the timed structure the report session follows |
| Key numbers | the values the student must reproduce or confront (§3's pattern) |
| Data path | where the data live: CDS, GitHub, survey release |
| Reading list | the paper plus the background it assumes |
| Pitfalls | the traps the instructor already knows about |
| What excellent looks like | the explicit bar for a top grade |

## 7. What the instructor cuts: exercise prompts are not slides

The finals carry no pedagogy layer — course-map slides, think-pair-share prompts,
discussion-question slides, reference-list slides, cross-lecture pointers ("recap of L2",
"you will fit this in the exercise") were deleted, ~1,100 words per deck (`density-target.md`,
what-dies list; the cut list also appears in `writing.md`, annotated "one mention is enough").
Therefore:

- Exercise prompts, procedures and discussion questions belong in the exercise README and in
  speech. On the deck, the exercise appears at most once — as physics, i.e. the punchline of
  §4 — or not at all.
- The detail the students need (cut values, reference fits, caveats) is the README's job;
  nothing about the exercise workflow earns slide area.

## 8. Exercise README skeleton

```markdown
# Exercise: recover <key result> from <public dataset>
## Purpose          the lecture message this lands (§4)
## Data             dataset + public route (archive query, CDS, GitHub, survey release);
                   what ships in data/ and how to refresh it
## Steps            01_… explore · 02_… standardize/fit · 03_… derive — per step: run
                   command, what it prints, what it saves, what to notice
## Expected result  reference value + citation + tolerance; full simplifications (§3)
## Deliverables     figures, results files, short interpretation (L3 asks for ~150 words
                   plus one self-identified limitation of the selection)
## Pitfalls         selection bias, zero points, aliases, margins — what makes a wrong
                   answer look right
## References       data documentation + the reference-value papers
```
