# beta_T varies with field by more than the substructure separation it is meant to resolve

Recorded 2026-09-05, stage A and the end of the recovery. An independent review
found ten defects in the first version of this analysis; the largest of them
removed the result the first version reported, and what is left is smaller but
stands.

## What was claimed and withdrawn

The first version fitted beta_T(H) = b0 + b1 H, found the linear form preferred
over the constant on 13 of 16 papers by corrected AIC with 15 of 16 slopes more
than two standard errors from zero, and reported a reduced-field collapse.

**All three are withdrawn.**

The ten fits per paper are one curve family re-evaluated at ten fields chosen by
a constant in the rebuild script. They are interpolations of the same isotherms,
not ten observations. Rebuilding the table at other grid densities and running
the same comparison unchanged:

| N_FIELDS | 5 | 10 | 20 | 40 | 160 |
|---|---:|---:|---:|---:|---:|
| median t statistic | 6.89 | 7.88 | 10.93 | 15.63 | 33.02 |
| papers preferring linear | 10 | 13 | 15 | 15 | 15 |

The slopes move by under a percent; only the evidence moves, as the square root
of a number nobody measured. Residual lag-1 autocorrelation is 0.44 and the
effective sample size is under 4 of 10.

The reduced field was worse than that. `Hirr(Tmax)` was defined as the last
field at which the hottest isotherm carries data, and in twelve of sixteen
papers that equals the top of the analyst's own field grid to within one per
cent. Dividing by the grid top reproduces the claimed spread reduction exactly.
In five papers the hottest isotherm does not die inside the panel at all: it is
where the experimenter stopped sweeping.

And the line was not the last model. Applying the same rule one step further, a
quadratic beats the line on eleven of sixteen, and nine of sixteen papers have
an interior maximum rather than a monotone trend.

`1104.0477v2` should never have entered the comparison. Its Fig. 3(c) plots two
markers on the 4.5 K and 7.5 K isotherms joined by a straight line; its ten fits
are samples of that line and its apparent field dependence is a consequence of
six numbers. It carried the strongest single piece of evidence in the table.

## What survives

The variation itself. It is a property of the traced curves, so it does not move
when the field is sampled more finely.

| | |
|---|---:|
| median half-range of beta_T across a paper's own field span | **1.35** |
| the same over the eleven papers graded measured | 1.33 |
| worst | 3.85 (`2510.10264v1`) |
| median 95% half-width the individual fits report | 0.32 |

The variation across field is about four times the uncertainty each fit quotes.
Seven of sixteen papers are monotone in field and nine have an interior turning
point, so the shape is not one shape.

## The number that decides the manuscript's claim

| substructure | papers | median beta_T | median half-range |
|---|---:|---:|---:|
| iron_pnictide_122 | 7 | 1.900 | 0.839 |
| iron_chalcogenide_11 | 5 | 2.291 | 2.019 |
| iron_pnictide_1111 | 4 | 3.646 | 2.543 |

Separation across substructures **1.92**. Median within-paper half-range
**1.35**. The between-family signal is **1.3 times** the within-paper variation
that a single exponent per sample hides. On the eleven papers graded measured it
is 1.98 against 1.33, a ratio of 1.4.

So on the temperature axis the substructure-conditional effect is not comfortably
larger than the error introduced by holding the exponent fixed across field. It
is the same size.

## What this does not say

It does not establish a functional form for beta_T(H), and the shape varies
between papers. Establishing one needs isotherms sampled at fields the figures
do not share, which is a measurement these papers cannot supply.

It does not bear on the field axis, which is separately unresolved: see
`audit/field_axis_adjudicated_20260905.md`, where six non-randomly-chosen papers
disagree with their figures by an amount not distinguishable from the
temperature axis's, and ten passing papers have never been read at source.
