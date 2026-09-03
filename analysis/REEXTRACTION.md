# Re-extraction workflow

Rebuilding the Jc data by measuring the published figures instead of asking a
model to read them.

## Why the previous route failed and why this one can be checked

Twenty-one source records have now been withdrawn because their deposited
series are not readings of the figures they claim. The failure was not
carelessness in a particular paper; it was structural. A vision-language model
asked to read a plot it cannot resolve returns numbers of the right order and
the right shape, and nothing in the output distinguishes that from a real
reading. The defects only became visible when someone opened the PDF.

So the requirement for the replacement is not accuracy, it is **falsifiability**:
every number must come from a transformation a reader can recompute, and the
transformation must carry its own error.

`analysis/figure_digitizer.py` does three things that make that true.

**The calibration is read, not typed.** The axis tick labels of a published
figure are real text in the PDF with exact coordinates. The tool extracts them,
fits value against page coordinate by least squares, and reports the residual.
For the worked example below the tick labels miss a straight line by 6 parts in
100 000 of the axis span. A hand-entered pixel coordinate has no such number
attached to it.

**The series are sampled column by column.** A Jc(H) trace is single-valued in
field, so every pixel column inside the frame carries at most one value of each
series. Taking the centroid of the matching pixels per column is immune to
markers that touch each other, to a line drawn through them, and to marker size
changing along the curve. Connected-component blob detection fails on all
three, and fails silently.

**Annotations are removed using the PDF's own text layer.** Legends and panel
labels sit inside the frame and are often the same colour as a series. Their
bounding boxes are known exactly, so they are masked rather than guessed at.

Every run writes a calibration JSON next to the points: the tick labels used,
the fitted slope and intercept, the fit residual, the detected frame in pixels,
and the axis span those imply. The conversion from pixel to physical value can
be recomputed from that file alone.

## Worked example: 2012.13723 FIG. 4

Ba(0.6)K(0.4)Fe2As2 thin film on CaF2, H parallel to c, seven isotherms.

    python analysis/figure_digitizer.py \
        --spec analysis/reextraction_specs/2012.13723_fig4.json --overlay

Result: 266 points over seven isotherms.

| check | value |
|---|---|
| x tick labels recovered from the PDF | 0, 1, 2, 3, 4, 5, 6, 7 |
| y tick labels recovered from the PDF | 1e4, 1e5, 1e6 |
| tick-fit max residual | 5.9e-05 (x), 4.5e-05 (y) of the axis span |
| re-projection residual | 0.005 px |
| axis span implied by the fit | x -0.01 to 7.01, y 4.9e3 to 3.0e6 |

Three independent checks that the numbers are the paper's:

1. **Against the paper's own text.** It states a self-field Jc at 4 K of
   2.2 MA/cm2. The lowest field sampled is 0.09 T, not zero, and the curve is
   steep there; the recovered value is 1.93e6, 12% below the quoted self-field
   figure. It states Jc stays above 1e5 A/cm2 at 28 K; the recovered 28 K
   isotherm starts at 1.36e5.
2. **Physical ordering.** Jc falls monotonically with temperature at every
   field: 1.93e6, 1.79e6, 1.45e6, 1.13e6, 7.10e5, 3.10e5, 1.36e5 at low field
   for 4 to 28 K. The extractor is told nothing about temperature ordering, so
   this is a constraint the output satisfies rather than one imposed on it.
3. **Against the fabrication signatures.** 0.0% of the recovered values sit at
   two significant figures or fewer, and 266 of 266 are distinct. The vision
   route ran at 85-100% and 0.29 respectively; the papers that were withdrawn
   ran at 0.09.

## A finding about the screen itself

`audit_extraction_integrity.py` grades this re-extraction **CHECK**, on
`non_monotonic`, because each isotherm carries 3 to 16 small rises with field.
That is measurement scatter in a real digitisation, and it is exactly what the
withdrawn records lacked: they had **zero** rises across 60 to 128 steps.

The screen tests for defects that fabricated data has. It does not test for the
absence of the noise that real data must have. Strict monotonicity across a long
series is itself a strong fabrication signature, and none of the current
signatures fire on it. Two changes follow:

- add a `too_smooth` signature for a long series with no rises at all, and
- distinguish scatter (isolated single-point rises) from a genuine second
  magnetisation peak (a sustained run of rises), so that neither is graded the
  same as a ramp.

Until then, a CHECK verdict carrying only `non_monotonic` should be read as
evidence for a real extraction, not against it.

## Authoring a spec

Per figure, a human supplies only what is printed in the paper:

- the page and a crop that contains the axes box,
- whether each axis is linear or logarithmic,
- the legend: one marker colour and one temperature per series.

Colours are best taken from the figure rather than guessed. To list them:

    python - <<'PY'
    import pymupdf, numpy as np, collections
    # render the clip, then quantise and count colours inside the frame
    PY

Everything else, including the axis ranges, is measured. The spec deliberately
does **not** accept axis minimum and maximum values, because a typed axis range
is the one place where a mistake reproduces the original failure exactly.

## Priority order

Ranked by what it repairs in the manuscript, not by convenience:

1. **The 13 papers behind the 83 Tier-3 field-axis fits.** Their Hc2 comes from
   a literature default and their normalised field windows collapse to a median
   of 0.08, which is why 34 of them pin at the exponent ceiling of 30. The 83
   Tier-1 fits, whose Hc2 was read from the paper's own figure, have a median
   exponent of 1.47 and none at the ceiling. Reading Hc2(T) for those 13 papers
   is the single change that would most strengthen the field-axis result.
2. **The 21 withdrawn temperature-axis papers**, to rebuild the beta_T cohort.
3. **The anchor table.** One (T, H, Jc) point per physical sample is far cheaper
   than a full curve, and the variance decomposition is the paper's
   pre-registered outcome.
4. **The 137 archived PDFs** whose captions name both an Hc2(T) figure and a
   Jc(H) figure, of which only 20 are currently used.

## Status of the cohort re-measurement, and two limits found

`analysis/figure_spec_builder.py` drafts a spec by finding the axes box on the
page, reading the tick labels, probing the series colours inside the frame and
pairing each `N K` legend label with the nearest coloured marker to its left.

It does not work well enough to be trusted unattended. Over the 26 cohort PDFs
it locates a Jc figure with a usable frame in 11, and its legend pairing
recovers a complete set of series in none of them. Since a wrong colour silently
relabels an isotherm, which is the exact failure this whole exercise exists to
remove, the builder is an assistive probe: it reports the box, the ticks and the
candidate colours, and a person confirms the legend before anything is measured.

**Black series are unreliable.** The plot frame, the tick marks and the axis
annotations are the same colour as a black data series, and masking the PDF text
layer removes the annotations but not the ticks. On 2207.06629 the seven
coloured isotherms come out in the right order and at the right magnitudes while
the black 4 K series reads 2.82e6 against the paper's stated 3.9 MA/cm2 and
below its own 8 K curve. Until a marker-shape or tick-exclusion test is added,
treat any black series as unmeasured rather than as measured.

**Detection rate.** 11 of 26 papers yield a figure the builder can frame at all.
The rest need the crop supplied by eye. Realistic throughput with confirmation is
a handful of papers per sitting, not a single batch run.

Completed so far:

| paper | figure | points | check against the paper |
|---|---|---|---|
| 2012.13723 | FIG. 4 | 266 | 1.93e6 at 0.09 T against a stated 2.2 MA/cm2 self-field |
| 2207.06629 | Figure 4 | 319 | coloured series ordered correctly; black 4 K series wrong |

Both are 0.0% at two significant figures or fewer, with 266 of 266 and 315 of
319 distinct values.
