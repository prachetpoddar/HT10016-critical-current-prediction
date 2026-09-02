# Figures 1 and 2, the hand-built artwork

These two are not produced by a script in `analysis/`. They are Inkscape
drawings, and the `.svg` here is the source of record; the `.png` beside it is
what the manuscript embeds, rendered at 3000 px wide.

`analysis/manuscript_figure_1.py` and `manuscript_figure_2.py` produce a
different pair of figures in a plain matplotlib style. Those were carried in an
intermediate revision of the manuscript and are kept because they are
reproducible, but the artwork here is what the paper uses.

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

## Numbers these figures assert

Figure 1: 934 screened PDFs, 23 fittable compounds, 16x MAE reduction,
Stage 1 10.10, Stage 2 0.43, Stage 3 0.84, 82 high-confidence plus 130 graded
predictions, 80.7% Hc2 coverage, 212 retained of 233 evaluated, MAE below 1 on
2 of 4 families.

Figure 2: 934 Elsevier and Springer articles, 16x MAE reduction, Stage 1 10.10
and Stage 2 0.43, MAE below 1 at 2 of 4 testable substructures, 233 candidates,
80.7% Hc2 coverage.

Three quantities in Figure 1 are pipeline artefacts with no counterpart in the
manuscript and are therefore not checked by `analysis/verify_deposit.py`:
`186 partial-fits (v3.2.2B)`, `n = 662 vision-pass cache entries`, and the
version tags themselves.
