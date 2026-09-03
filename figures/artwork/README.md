# Figures 1 and 2, the hand-built artwork

These two are not produced by a script in `analysis/`. They are Inkscape
drawings, and the `.svg` here is the source of record; the `.png` beside it is
rendered at 3000 px wide and then cropped to its own content with a uniform
margin.

**The manuscript does not embed these.** An earlier version of this file said
it did, and that was wrong. The Figures 1 and 2 in the .docx are the plain
matplotlib pair from `analysis/manuscript_figure_1.py` and
`manuscript_figure_2.py`, which is a different visual style, and `figures/`
carries that pair. Figure 2's generator reproduces the embedded image pixel for
pixel; Figure 1's depends on the cohort and is regenerated whenever the tables
move. `analysis/check_figures.py` asserts both, and asserts that what is in the
document is what is in `figures/`. Commit 176d750 copied this artwork over
`figures/manuscript_figure_1.png` and `_2.png`, which is exactly the style swap
`manuscript_figure_1.py`'s own docstring warns about; that has been undone.

That crop matters for Figure 2. Its canvas carries 456 px of empty white on
the right against none on the left, so an untrimmed render sits off-centre
inside its own frame and looks off-centre on the page however the paragraph is
aligned. `render_artwork.py` trims each PNG to its drawing and re-pads evenly,
84 px for Figure 1 and 40 px for Figure 2, which reproduces 3036x2019 and
2584x2145. The trim was dropped when that script was rewritten and has been
restored. Every figure's display extent in the manuscript is computed from the
embedded pixel dimensions, by `analysis/reembed_manuscript_figures.py`, so
nothing is stretched.

`analysis/manuscript_figure_1.py` and `manuscript_figure_2.py` produce the
pair the paper actually uses. Their counts come from
`analysis/figure_counts.py`, which recomputes them from the deposited tables on
every run, so a withdrawal moves the figure on the same run that moves the
data. Four quantities have no deposited source and are named as constants
there: the retrieval corpus, the v3.2.1 fittable-compound cohort, the v3.2.2B
partial-fit count, and the vision-pass cache size.

## Two things a future editor needs to know

The SVGs carried every label twice: once as live `<text>` and once as glyph
outline paths underneath, left over from a matplotlib export that was then
edited in Inkscape. With the true Helvetica installed the two coincide exactly
and you see one clean label. Edit only the live text and the outline keeps
showing the old value underneath. The duplicate outline layer has been removed
from `manuscript_figure_1.svg` (407 paths, each one wholly inside a live text
element's box, so no artwork was touched), which is why the numbers can now be
edited in one place. `manuscript_figure_2.svg` never had the duplicate.

Both files set their text in Helvetica. Rendering without it substitutes a
metric clone and shifts glyphs by a fraction of a pixel, which is invisible on
its own but was what made the duplicated layer show as a halo. Render with
Helvetica present, or accept the substitution now that the duplicate is gone.

## Numbers this artwork asserts

The gold callout in both figures read `16 x MAE reduction` until the prose
withdrew that ratio; both now read `validation scope` over the per-stage
leave-one-substructure-out errors, which is where the conditioning claim rests.
The three stage figures are `analysis/multi_stage_loso.py`'s all-families
cohort: Stage 1 12.30, best Stage 2 11.54, Stage 3 9.01, the same numbers the
manuscript prints.

Figure 1: 934 screened PDFs, 23 fittable compounds, 175 partial-fits (v3.2.2B),
662 vision-pass cache entries, 85 dispatched of 183 candidates, 80.7% Hc2
coverage, MAE below 1 on 2 of 4 families.

Figure 2: 934 Elsevier and Springer articles, 23 fittable, 175 v3.2.2B fits,
662 vision cache entries, seven refusal conditions, 233 candidate records, 85
of 183 dispatched, MAE below 1 at 2 of 4 testable substructures.

Two of Figure 1's right-panel claims have no check anywhere and are carried
here so that the next person knows to read them: `80.7% Hc2 coverage` and
`< 1 MAE, 2 of 4 families`. Both predate this revision.

## What still needs a decision, not an edit

The labels fit and the numbers match the deposit, but three passages of the
manuscript describe dispatches that the reduced-field gate has closed, and
those are claims rather than counts. They are listed at the top of
`analysis/apply_figure_caption_edits.py`.
