# Replacing the 30 percent adoption threshold

Recorded 2026-09-06.

## What was wrong

Sec. III.D and the abstract turn on a bar: "Both fall below the 30% adoption
threshold, which marks the level at which a universal law would substantially
exceed the gain observed from family-conditional aggregation." Nothing in the
repository derives 30. It appears only as a literal in figure code. The
quantity the sentence names as its own benchmark is given in the next
paragraph: family-conditional aggregation improves median holdout error from
0.613 dex to 0.604, a gain of 0.009 dex, which is 1.47 percent. The printed bar
is twenty times its stated benchmark.

Lowering the bar to 1.47 is not the repair, because the two are different
quantities. 13.0 percent is a reduction in within-cell scatter of log10 Jc
under a reduced-variable grid; 1.47 percent is a reduction in an out-of-sample
prediction error under family conditioning. Neither converts into the other.

## An attempt that was withdrawn

A script was written to put both schemes on one scale, the manuscript's own
statistic, and to read the bar off the family-conditional result: 27.4 percent
on the curve unit, 42.7 on the raw. An independent review broke it. Against the
correct null for a nominal coarsening, a random regrouping of the same
compounds into labels with the same size profile, the family grouping's excess
is -2.4 percent on the curve unit and +0.4 on the raw, at probabilities of 0.60
and 0.41. The family label carries no information beyond compound identity on
this statistic, and three of the seven family labels in this cohort are a
single compound from a single paper. It cannot define a threshold. The script
was deleted rather than published.

This does not touch the temperature-axis conditioning result, which is a
different statistic on a different quantity, the fitted exponent rather than
the raw scatter, and which is tested against a paper-clustered null.

## What replaces it

A collapse claim is a claim that particular coordinates carry structure, so it
should be tested against coordinates that do not. `analysis/scaling_collapse_test.py`
runs two such tests on the point-level rebuild cohort: 6070 records from 27
papers, 18 compounds, 7 families and 171 curves.

### Rotation

Standardize the two reduced coordinates and bin on a grid rotated by a random
angle. The geometry and the cloud's local contiguity are unchanged; only the
meaning of the axes is destroyed. Four hundred rotations:

| statistic | physical grid | rotated grids | p |
|---|---:|---:|---:|
| median within-cell SD | 39.31% | 41.60% | 0.823 |
| pooled | 19.49% | 19.06% | 0.228 |
| mean | 39.64% | 37.91% | 0.140 |

Under the manuscript's own statistic the physical reduced axes are not better
than a random rotation of themselves. Under the other two they are nominally
better and neither reaches significance.

The label-shuffle null used in earlier work is not adequate here. It destroys
contiguity as well as meaning, so any local binning of a two-dimensional cloud
beats it, which is why random-coordinate binning measures at -0.02 percent: a
true result that tells us nothing. The rotation keeps everything except the
claim under test.

### Unreduced coordinates

Bin the same records on laboratory temperature and applied field, without
dividing by the critical scales.

| binned on | cells | reduction | compounds per cell |
|---|---:|---:|---|
| T/Tc and H/Hc2,0 | 73 | 39.31% | median 4, 3 of 73 hold one |
| T/Tc and H | 44 | 61.12% | median 3, 15 of 44 hold one |
| T and H/Hc2,0 | 57 | 49.12% | median 4, 12 of 57 hold one |
| T and H | 42 | **67.01%** | median 2, 17 of 42 hold one |

Dividing through by the critical scales makes the collapse worse, with more
cells. Paired on the same resampled curves, the unreduced grid beats the
reduced one by 27.7 points, 95 percent interval 4.7 to 37.5, and the reduced
coordinates win on 0.8 percent of five hundred draws. The direction holds in
every one of the seven leave-one-family-out refits, at minimum cell sizes of 3,
5, 8 and 12, and with the duplicate digitisation of one figure removed.

The mechanism is in the last column. The laboratory grid wins by separating
compounds rather than by collapsing them: seventeen of its forty-two cells hold
a single compound, against three of seventy-three. Measurements cluster at a
few conventional temperatures and low fields, and that convention tracks the
material. That is the paper's own thesis arriving from a new direction, and it
is a stronger negative result about universal scaling than the threshold
comparison it replaces.

## What this changes in the manuscript

The 30 percent bar goes, in the abstract, Sec. III.D, Table III row 1 and the
conclusion. What replaces it is a test rather than a threshold: reduced-variable
scaling is not distinguishable from a random rotation of its own axes under the
statistic the paper reports, and it is beaten by the unreduced laboratory
variables, which win by isolating compounds. The headline negative result is
unchanged and better supported. The 13.0 percent figure can stay as a
descriptive statistic; it stops being the thing compared against an undefined
bar.
