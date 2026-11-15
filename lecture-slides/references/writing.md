# Writing — the words on the slide

How to write the text itself: bullets, titles, emphasis, numbers and citations, at the density the instructor actually ships. Read this whenever you compose or trim slide prose. The measured density bar lives in `density-target.md` — this file takes its budgets from there and does not re-derive them. Figure sourcing is `figures.md`; page geometry is `layout.md`; the audit is `qa-gate.md`.

## 1. One message per slide; every bullet serves it

Each slide has **one message**. Every bullet must serve that message or it is cut. The per-slide budget is pinned in `density-target.md §1` — take it from there, do not re-derive it: bullets/slide median **3–5, one line each**; draft to **≤4**; a 5-bullet slide must be a flat label list. If there is more to say, split the slide; do not shrink the font (`density-target.md §1`: text and figures trade places, never a smaller font).

Per bullet: **≤2 lines, one clause each. No nested sub-bullets** — the finals contain 1 nested line across 89 slides; the drafts had 69 slides with nesting (`density-target.md §1`). Two things that earned their survival stay: **load-bearing numbers with their citation** ("M_B = −19.253 ± 0.027 (SH0ES)", "σ ≈ 0.6 mag (Kowal 1968)", "ρ₀ ≈ 0.1 M☉/pc³") and **the verdict / punchline** ("Only SNe Ia come from white dwarfs"). Everything else competes for the line budget.

## 2. No hyphen-chained compounds; the read-aloud test

Ban hyphen-**chained compounds** in bullet text. They make bullets long and hard to deliver. The test: **read the bullet aloud — if you pause to breathe mid-phrase, it is too long.**

Failed → succeeded pairs from the source, kept verbatim:

| Draft (fails) | Final (works) |
|---|---|
| "the Phillips-relation-based width-luminosity correction reduces the Hubble-diagram scatter to the 0.17-mag level" | "the Phillips relation reduces the scatter to 0.17 mag" |
| "a sub-Chandrasekhar-mass double-detonation scenario with a helium-shell ignition" | "sub-Chandrasekhar double detonation, helium shell first" |

Rules that produce the right side:

- No "X-based" or "X-driven" constructions — just say the noun.
- No "X-luminosity-Y relation" — split into two short phrases.
- **Em-dashes (—) are structural connectives and stay.** The instructor's own finals keep them: "The bet of 1938 — and the first supernova Hubble diagram"; "Two engines — and a 70-year taxonomy". Do not ban them.
- **Ranges keep the en-dash** (0.1–1.0 M☉) — it is not a hyphen.
- **Hyphenated surnames stay** (Bland-Hawthorn) — they are proper nouns.

What he actually removes is not the dash: it is **the trailing explanatory aside stuffed into a bullet**. Cut the aside; if the clause still reads aloud in one breath, keep the sentence.

## 3. No decoration text

Delete-list from the text audit round, verbatim — these seven phrases died:

1. "the story of this lecture is…" — the story is in the plan, not the slides
2. "today we will see exactly…" — unnecessary setup
3. "the course's theme of… at its highest stakes" — course meta
4. "the debate continues as we speak" — journalism, not physics
5. "This is exactly where the field's intellectual effort is concentrated" — decoration
6. "you will fit this yourselves in today's exercise" — one mention is enough
7. "was the rehearsal; this is the main stage" — rhetorical metaphor

The categories they belong to: course meta-commentary, cross-lecture pointers ("recap of L2", "you will fit this in the exercise"), and hedged asides ("not excluded", "still indirect"). The whole pedagogy/meta layer runs ~1,100 words/deck in a draft (`density-target.md §3`).

**The principle: rhetoric belongs in the title, not the bullets.** Titles are rhetorical by design — "a lighthouse built by the helium flash" and "Second Careers of the Rejected" survived the cut. Bullets are not.

## 4. What to keep

Numbers with citations, the logic chain, the physical argument, the takeaway. The logic chain survives **verbatim**: L9's width–luminosity slide kept the draft's four-step causal chain word-for-word — "More ⁵⁶Ni → hotter ejecta → Fe III stays ionized → B-band persists". If the draft reasoned correctly, the reasoning is the value; keep it, drop everything around it (`density-target.md §2`).

**A caveat earns its place only when the caveat *is* the lesson.** "A small SD contribution is not excluded" and "Ic and SLSN progenitors still indirect" were cut; "w(z) inherits a redshift-dependent bias" stayed.

**A cut is deleted, not moved to the speaker notes.** The finals hold 12 note-words across 89 slides (`density-target.md §1`) — cut bullets dumped into `<aside class="notes">` will not be read. The one writing-side exception: a number or claim that appears *nowhere else* in the deck must survive somewhere visible (a one-line clause on the slide, or the figure itself). Deletion discipline and the cut-audit: `layout.md`.

## 5. A figure at the top of a slide borrows against the first bullet

If a slide opens with a plot, the first line of text **owes the reader three things**: what the horizontal axis is, what the vertical axis is, and what one mark is (plus, where there is one, what the curve or reference line means). Not "the figure shows…" — the decoded sentence:

> **Reading it:** distance from the group's centre across, radial velocity up; points are galaxies, the curve is the speed needed to escape.

A label like `SGX (km s⁻¹)` is not an explanation — the audience does not know that "supergalactic" is a coordinate system, still less that a velocity is being used as a distance. Decode it in words on the slide. Only after that sentence may the bullet make its claim.

**The cover-the-figure test:** cover the figure. Can a reader who has never seen it still say what is plotted? If not, the first bullet is wrong.

## 6. Every structure slide answers "how do you know it is a member?"

Groups and clusters are not defined by looking similar; membership is a *measured* criterion. State it where the structure is introduced, once, **in operational form**:

> **Membership:** projected radius under ~1.5 Mpc, velocity inside the dispersion — then a distance that agrees.

The three-part pattern — **radius, velocity, independent distance** — is what distinguishes a cluster member from a foreground galaxy, and it is exactly where the course's theme (distance measurement) enters the story of structure. Leaving it out produced the two questions that came back from the review: *"what does 'not one object' mean?"* and *"how do we know these belong together?"*

## 7. "Why the number was wrong" is the slide; "that it was wrong" is trivia

Students arrive already knowing H₀ ≈ 500 in 1929 was too big. Repeating the fact teaches nothing. The slide must convert it into an **error budget**: which errors, how large, and do they multiply out to the observed factor?

> 4.1 mag of error in the distance modulus = 10^(4.1/5) = 6.6 in distance, and 500/75 = 6.7.

**General rule: every historical "this was wrong" slide ends with a factor that closes the arithmetic.** A wrong number with no error budget is trivia; with one, it is a lesson about calibration.

## 8. When a claim rests on a quantity, give the quantity's share

The review asked whether A3627 really is the centre of the Great Attractor. The answer is a number, not a hedge: one cluster supplies ~1.1 × 10¹⁵ M☉ against the ~5 × 10¹⁶ M☉ the flow requires — **about 2%**. Saying "it is still debated" is worthless; saying "one cluster is 2% of what is needed, so the Attractor must be a complex along that sightline" is the slide.

**Rule: if a structure, object or mechanism is claimed to explain a measured effect, quote its share of the required budget on the slide.** A hedge is worthless where a number exists.

## 9. Define the zero before measuring a difference

A peculiar velocity is a difference, and a difference needs a frame. A deck cannot say "we move at 627 km s⁻¹" and then "every redshift is expansion plus a peculiar term" without answering the question the audience is already asking: *standing still relative to what?*

Order that works:

1. **Announce the puzzle** — motion as a question: 627 km s⁻¹ — against what?
2. **Define and measure the frame** — the CMB dipole: T(θ) = T₀(1 + β cos θ), β = 1.23 × 10⁻³, implying 369.8 ± 0.9 km s⁻¹.
3. **Then the consequences follow.**

Never put the frame slide *after* the slides that need it.

## 10. A title states this slide's claim or question; an anecdote is not a title

Three titles were rejected in one review — with their replacements:

| Rejected | Why | Replacement that worked |
|---|---|---|
| "Shapley: the heaviest concentration, counted twice" | "counted twice" is a joke about the discovery history, not what the slide shows | "Shapley: the densest thing we can see" |
| "Laniakea: a supercluster defined by what falls where" | a restatement of the previous slide's idea, so the title teaches nothing new | "Laniakea: a basin 160 Mpc across" |
| "The centre was hidden behind the Milky Way" | true, but the slide is about *where the mass is and whether A3627 is it* — the dust is the mechanism of the difficulty, not the subject | "The centre sits behind our own dust" (with the argument in the body) |

**The move-test: if a title can be moved to another slide unchanged and nothing breaks, it names the topic, not this slide's claim.** Rewrite it against this slide's claim or question (§3: the rhetoric goes here, not in the bullets).

## 11. Numbers and citations on the slide

- **Verify every number** against the original paper; use a research subagent for literature searches. Never trust secondary sources or memory.
- **Cite the primary source on the slide** — author, year, journal, figure number, arXiv link. Not "recent studies show…".
- **Flag unverified numbers honestly.** If you cannot confirm a value, say so on the slide or omit it.
- **Citations are numbers too** — they get the same verification (volume, first page, title, arXiv id against the PDF's front matter). Full procedure and the failure story: `figures.md`. Figure credits on the slide are sized per `density-target.md §5`.

What you could not verify is flagged, never smoothed over. Per-slide numeric and author-name cut-audits: `layout.md`; the mechanical checks: `qa-gate.md` via `scripts/audit_deck.py`.
