# How strong is the variance-decomposition diagnostic?

Written while looking for results to strengthen. The honest answer is that the
per-family regime labels are weaker than the manuscript presents them, and the
evidence is in the deposit already.

## The deposit's own preferred test clears no family

`analysis/permutation_test.py` shuffles `sample_form` within paper, because
sample form is near-collinear with source paper and a naive shuffle breaks that
structure. Re-run at the current cohort, 20000 shuffles, seed 20260901:

| scope | n | eta^2 | p naive | p paper-clustered |
|---|---|---|---|---|
| aggregate | 60 | 0.3139 | 0.0002 | 0.2316 |
| conventional_AlB2 | 15 | 0.1159 | 0.2117 | 0.6663 |
| cuprate_BSCCO | 9 | 0.0964 | 0.7752 | 1.0000 |
| iron_chalcogenide_11 | 10 | 0.7687 | 0.0155 | 0.1657 |
| iron_pnictide_1111 | 6 | 0.1433 | 0.7986 | 0.8019 |
| iron_pnictide_122 | 9 | 0.3452 | 0.2772 | 0.3674 |
| other_unclassified | 3 | 0.9880 | 0.3320 | 1.0000 |

Not one family reaches p < 0.05 under the clustered null, and neither does the
pooled ratio. The naive column is what makes the chalcogenide result look
significant, and it is the column the clustering was written to distrust.

## Two of six labels do not survive bias correction

eta^2 is upward-biased at small n. Its expectation under the null is
(k-1)/(n-1), which for `iron_pnictide_1111` at n=6, k=3 is 0.400, inside band B.
Its observed 0.1433 is below chance.

| family | n | k | eta^2 | omega^2 | chance eta^2 |
|---|---|---|---|---|---|
| conventional_AlB2 | 15 | 2 | 0.1159 C | 0.0448 C | 0.071 |
| cuprate_BSCCO | 9 | 2 | 0.0964 C | -0.0289 C | 0.125 |
| iron_chalcogenide_11 | 10 | 3 | 0.7687 A | **0.6802 B** | 0.222 |
| iron_pnictide_1111 | 6 | 3 | 0.1433 C | -0.3329 C | 0.400 |
| iron_pnictide_122 | 9 | 3 | 0.3452 B | **0.1144 C** | 0.250 |
| other_unclassified | 3 | 2 | 0.9880 A | 0.9646 A | 0.500 |

Outcome A for the iron chalcogenides, which is the paper's clearest
conditioning result, is 0.6802 on the bias-corrected statistic and would be
Outcome B.

## Three of six labels flip on one deletion

Exhaustive leave-one-physical-sample-out at the current cohort:

| family | eta^2 | flips |
|---|---|---|
| conventional_AlB2 | 0.1159 C | 0 of 15 |
| cuprate_BSCCO | 0.0964 C | 0 of 9 |
| iron_chalcogenide_11 | 0.7687 A | 1 of 10, A to B at 0.6046 |
| iron_pnictide_1111 | 0.1433 C | 1 of 6, C to A at 0.7450 |
| iron_pnictide_122 | 0.3452 B | 2 of 9, B to A at 0.8449 and B to C at 0.0764 |
| other_unclassified | 0.9880 A | 0 of 3 |

This revision withdrew fourteen rows. One more would move three of the six.

## What the corrections did and did not touch

Across the eight distinct deposited states of the anchor table, no correction
changed `log10_Jc_anchor` or `substructure` on any surviving row. The unit fix
acted on `Jc_anchor_A_per_cm2`, a column the diagnostic does not read, and 19
`sample_form` relabels were confined to `iron_pnictide_1111`. So the labels
holding across those states is a statement about which columns were edited, not
about the estimator's stability. The pooled ratio is the counterexample inside
the same table: it crosses the C/B boundary at the first withdrawal, 0.2671 to
0.3139.

## Three impossible anchor fields, in the cell that carries Outcome A

| paper | sample | form | H_anchor_T |
|---|---|---|---|
| iop_10.1088_0953-2048_29_3_035013 | FTS_6K | thin_film | -0.014277 |
| iop_10.1088_0953-2048_29_3_035013 | FTS_15K | thin_film | -0.000962 |
| springer_10.1038_s41598-022-24044-5 | FST_6K | thin_film | -0.001095 |

All three are `iron_chalcogenide_11 / thin_film`. A negative field is a
digitiser or axis-calibration output, not a measurement setpoint, which means
the anchor layer carries per-paper scale error. `analysis/axis_ticks.py` says
so directly: a per-paper scale error moves `log10_Jc_anchor` by log10(k) and
does corrupt the variance decomposition. The claim that the diagnostic is
independent of the field scale is therefore false; independence from the fitted
exponents beta_T and beta_H is true, because the anchor table shares no column
with the fit tables.

## What is defensible

The pre-registered bands are a decision rule for choosing a prediction scope,
and they should be reported as one. They are not a hypothesis test, and at the
present cohort sizes they cannot be: five of six families have fewer than
sixteen physical samples across two or three cells. Reported as a decision rule
with its leave-one-out range and its clustered p-value beside it, the diagnostic
is honest and still does the job the paper needs. Reported as an empirical
finding of three distinct regimes, it is not supported.

## One thing that is genuinely strong and is not stated

The refusal accounting. Of 2097 candidate-grid targets, 1934 are refused,
92.2%, every one carrying one of five named reason codes and none uncoded. A
literature-derived predictor that declines to answer nine times in ten, and can
say which gate declined and why for every one, is an unusual thing to be able
to state. Referee B praised exactly this, "a curated set of models that each
have a different applicability domain alongside a framework for identifying
which can be used for a particular inference", and the manuscript currently
carries it as a limitation rather than as the result.
