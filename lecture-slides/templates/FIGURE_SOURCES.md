# Lecture N — figure sources

<!--
  One row per asset in assets/. This file is the licence trail and the verification
  record, not a bibliography: every asset that appears on a slide appears here, and
  nothing appears on a slide that is not here.

  Read `figures.md` for the sourcing ladder, the crop procedure and the licence rules.
  The three fields people skip are the three that matter: the licence (for a Commons
  image, in the SLIDE caption too), the pixel size (it caps what the layout can do),
  and the verification line (who read the crop back, and what they checked).
-->

Every figure in the deck is either a crop of a published figure or a `[course]` schematic.
Crops were rendered from the paper's PDF at 300–400 dpi and cut with `scripts/crop_fig.py`
or a direct PIL bounding box, then **read back as an image** by a vision-capable model to
confirm that the frame, axis titles, tick numerals and legends are inside the crop, that
nothing important is clipped, and that no caption prose leaked in.

Citations were checked against the article record itself (arXiv e-print, Crossref, or the
scanned original). Where a citation could not be confirmed, that is stated plainly rather
than guessed.

## In use in the deck

| # | Slide | File | Crop of | px (w×h) | Source, licence and verification |
|---|---|---|---|---|---|
| 1 | S3 | `authorYYYY_figN.png` | whole Fig. N | 1800×1200 | Author, A., & Author, B. YYYY, "Title", Journal **Vol**, Page, Fig. N, arXiv:0000.00000. One sentence naming the panels and the axis titles that must survive at slide size. Numbers used on the slide, quoted from the PDF itself: ⟨…⟩. Licence: publisher figure, used for teaching; credit line on the slide is "Author+ YYYY, Journal Vol, Page". Verified by vision read: all four ticks and the axis title inside the frame; caption text excluded. |
| 2 | S6 | `authorYYYY_figN.jpg` | whole image, title band cropped | 2400×1500 | Author, C. YYYY, "Title", Wikimedia Commons, `File:Name.jpg`, **CC BY-SA 4.0**. What the drawing shows and what it does **not** (state the scale caveat in the caption if there is one). Modifications: <cropped the baked-in title band, downsampled to N px> — so the slide caption must say "title cropped" as well as credit + licence. Verified by vision read. |
| 3 | S22 | `topic_schematic.png` | drawn for this course | 1400×900 | **`[course]` schematic**, matplotlib. What it draws and which *numbers of this slide* feed it (⟨±925 km s⁻¹ / 70 ≈ ±13 Mpc⟩), so the drawing is a picture of the slide's own arithmetic and not a simulation. Generation script kept beside the asset. No external data. |

## Retired / candidates

| File | Crop of | Why not used |
|---|---|---|
| `cand_*.png` | <full citation as above> | <replaced by N on slide Sx because …; or "carries the numbers but not the structure"> |

## Asset budget

<!-- §8.6: a figure that will not grow is often an asset that cannot. Print this table
     before planning any enlargement; an upscale factor above ~1.5x means re-source. -->

| File | px wide | display width on slide | upscale factor | verdict |
|---|---|---|---|---|
| `authorYYYY_figN.png` | 1800 | 550 px | 0.31× | fine, can be enlarged |
| `old_scan.png` | 620 | 550 px | 0.89× | at the limit; do not widen |