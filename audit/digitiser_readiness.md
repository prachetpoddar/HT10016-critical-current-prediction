# Nothing has been extracted yet, and the digitiser cannot run on any of the nine

Finding the page is not the same as measuring the figure. Two figures have been
digitised in total, both located before this pass. For the nine papers whose Jc
figure was found by the text search, the count of extracted points is zero, and
`figure_digitizer.py` as written cannot produce one for any of them.

## Two independent requirements, and how each figure fares

The digitiser needs two things. Its calibration is **read, not typed**: the axis
tick labels must be real text in the PDF with coordinates, which is what gives
the fitted axis and its residual. And each series must be separable, which at
present means **one colour per series**.

| paper | page | tick labels in the text layer | hues found vs series present | blocker |
|---|---|---|---|---|
| 2012.13723v3 | 4 | yes, 31 | 7 / 7 | none, measured |
| 2207.06629v1 | 4 | yes, 19 | 8 / 8 | black series reads wrong |
| 0904.2442v1 | 6 | yes, 10 | 4 / 8 | filled against open markers |
| 1104.0477v2 | 9 | yes, 77 | 3 / 5 | colour reuse, plus 3 literature curves in frame |
| 1801.05074v1 | 10 | yes, 10 | 2 / 12 | frame lands on the wrong panel |
| 1002.0248v1 | 9 | **no** | 4 / 7 | both |
| 1003.0946v2 | 24 | **no** | 3 / 6 | both |
| 1611.08455v1 | 20 | **no** | no frame at any scale | both |
| 2110.15577v1 | 18 | **no** | 7 / 7 | calibration only |
| 10.1016/j.cjph.2024.09.042 | 5 | **no** | 5 / 5 | calibration only |
| 10.1016/j.jpcs.2026.113652 | 10 | **no** | 2 / 4 | both |

Six of the nine have no tick-label text at their figure, because the figure is
an embedded raster or its labels are outlined. On `10.1016/j.cjph.2024.09.042`
p5 the page carries 483 words and none of them is inside the figure.

**A correction.** An earlier check in this session counted numeric words per
*page* and reported five of nine as having a usable text layer. That counted body
text and page numbers. Counting only words at the detected plot frame gives three
of nine, and one of those three frames the wrong panel.

## The colour count overstates separability

The probe that produced the triage counts distinct saturated colours. Papers
routinely carry more series than hues, because a second dimension is encoded by
filled against open markers: `0904.2442v1` puts four temperatures times two
irradiation states on four hues, and `1611.08455v1` puts five temperatures times
two samples on two. Reading those with a colour key alone would merge two curves
into one, which is a data error, not a missing series.

So colour separability, which the triage measured, is necessary and not
sufficient. The series count has to come from the figure.

## What would unblock what

**Calibration without a text layer.** `analysis/axis_ticks.py` already reads an
axis from tick geometry alone: it returns logarithmic against linear and the
pixels per decade, measured at 6.57 against a predicted 6.5 on a log axis and
1.00 on two linear ones. For exponents that is sufficient on its own, because
beta is invariant under any scale on Jc and beta_H under any scale on the field
provided Hc2 carries the same scale. Only the anchor needs one labelled value per
axis. That is the route already proposed for this work, and it is not yet wired
into `figure_digitizer.py`, which has only the read-the-labels path.

Wiring it in unblocks `2110.15577v1` and `10.1016/j.cjph.2024.09.042`
immediately, since both have one clean hue per series.

**Marker-shape separation** is needed for the other four, and for the black
series in `2207.06629`. Without it, filled and open markers of one hue cannot be
told apart.

**Frame detection** needs the scale sweep already recorded, plus a fix for
`1611.08455v1`, where no frame is found at scale 3, 4 or 5.

## What can be reconstructed now, with no extraction at all

Three changes need no new measurement:

1. **Withdraw the six `10.1038/s41467-025-55880-4` field-axis fits.** The source
   paper reports no current density in any units. See
   `audit/withdraw_s41467_field_axis.md`. All six sit at the exponent ceiling.
2. **Drop the duplicate.** `10.1016/j.physc.2011.02.004` and `1002.0208v2` are
   the same paper in two cohorts, which breaks independence in the
   leave-one-paper-out and the permutation test. Keep the complete arXiv record.
3. **Merge the `physc.2011.02.004` refit**, already computed in
   `data/reextraction/physc_2011_02_004_field_axis_refit.csv`, once its residual
   is recorded alongside the Tier-3 residual.

Those three are the only table changes available today.
