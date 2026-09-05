# The seven blocked statistics, recomputed

Recorded 2026-09-05. Scripts `analysis/recompute_blocker_statistics.py` and
`analysis/rerun_closed_form_without_withdrawn.py`. Deposits
`audit/blocker_statistics_repaired.csv`,
`audit/form3_per_compound_without_withdrawn.csv` and the repaired base under
`audit/repaired_base_20260905/`.

`audit/repaired_cohort_edits_20260905.md` left seven passages unrenumbered
because each quotes a cohort size beside a statistic computed on that cohort.
These are the replacements. Two adversarial reviews ran before anything here
was reported. The first found sixteen defects, seven of which changed an
answer; the second found ten more, four of which changed an answer. Every one
is either fixed or printed beside the number it qualifies. The section headed
"what the reviews changed" lists them, because several are not bugs that can be
fixed away: they are properties of the repaired cohort that make a
like-for-like comparison impossible, and the honest output is the comparison
plus the reason it does not mean what it looks like.

The deposited arm of every statistic reproduces the deposited file exactly,
including the bootstrap strata, and the run aborts if it does not. That is what
makes the two columns comparable at all.

## 1. Temperature-axis leave-one-compound-out

| family | fits | compounds | MAE | resamples below 1.0 | spread |
|---|---:|---:|---:|---:|---:|
| iron_chalcogenide_11 | 89 to 87 | 5 to 3 | 0.588 to 0.546 | 100% to 100% | 0.365 to 0.330 |
| iron_pnictide_122 | 106 to 105 | 2 to 2 | 1.314 to 0.580 | 30% to 98% | 0.961 to 0.466 |
| iron_pnictide_1111 | 54 to 54 | 3 to 3 | 3.120 to 0.513 | 21% to 100% | 1.456 to 0.438 |

Spread is the mean absolute deviation of a family's exponents from their own
median. It matters because the resample fraction counts resamples whose error
falls below a fixed 1.0, and predicting every fit by its family's median with
nothing held out already gives an error equal to that spread. The Tc repairs
compress the exponents, so a family can cross the bar without the predictor
improving.

That is most of what moves the 1111 fraction, whose spread crosses 1.0. It is
not all of it: 122 sits below 1.0 in both arms and still moves from 30 to 98
percent, and the error divided by the spread falls in both moving families,
1.37 to 1.24 and 2.14 to 1.17, which compression alone would not produce.

The ratio's level carries nothing. The median minimises mean absolute
deviation, so an out-of-sample error over an in-sample optimum is at least 1
for any data whatever. Only the change between arms is readable.

Two caveats that belong with the table. `iron_chalcogenide_11` loses two of its
five compounds, both single fits, so its unchanged ratio compares a five-fold
estimator with a three-fold one. `iron_pnictide_122` has two compounds in both
arms, so every fold there predicts a held-out compound from exactly one other,
and its 98 percent rests entirely on that stratum. For 1111 the deposited
three-compound stratum is 0 of 758 and the two-compound stratum is 396 of 1116,
so the published 21 percent was carried by its weakest stratum.

## 2. Composition of the temperature cohort

|  | deposited | repaired |
|---|---:|---:|
| fits | 260 | 257 |
| distinct compounds | 11 | 9 |
| MgB2 fits | 0 | 0 |
| Ba(FeAs)2 | 85 | 84 |
| K(FeAs)2 | 21 | 21 |

The two compounds that disappear are single fits, `FeSe0.5Te0.5_K_doped` and
`FeSeTe`. The absence of MgB2 is not a consequence of the repair; the deposited
cohort has none either, and the manuscript sentence reads as though it were.

Eleven of the 257 are `iron_pnictide_111`, which no leave-one-out table covers.
That is a property of the family list in `compound_leave_one_out.py`, and it is
true of the deposited cohort as well.

## 3. Scale of the exposure

Four rules, because they give different answers and only one can stand beside
the published figure.

| rule | median | above 0.9 | window reproduced |
|---|---:|---:|---:|
| published rule, divide by Hc2_T_used | 0.883 | 11 of 52 | 49 of 52 |
| divide by the repaired anchor | 0.836 | 8 of 52 | 47 of 52 |
| the points that produced range_repaired | 0.836 | 7 of 52 | 52 of 52 |
| the points the protocol retains | 0.836 | 7 of 52 | n/a |

The like-for-like row is the first, and the script refuses to report unless
that rule returns the published 0.800 and 15 of 94 when run on the deposited
passing cohort, which it does.

**Exposure rises.** The share of curves whose measured maximum exceeds nine
tenths of the assigned scale goes from 15 of 94, 16 percent, to 11 of 52, 21
percent, and the median from 0.80 to 0.88. An earlier version of this
calculation divided by the repaired anchor and printed 0.836 beside the
published 0.80, which reads as roughly flat and is not the same quantity.

The protocol's retention floor caps the ratio at 0.95 by construction, so on
the last row "above 0.9" can only mean between 0.90 and 0.95. On the published
rule it means no such thing: six of the eleven are also above 0.95, the largest
0.9989.

## 4. Per-paper leave-one-out on the field exponent

| predictor | fits | papers scored | MAE | residual resample | paper resample |
|---|---:|---:|---:|---|---|
| Stage 2, deposited | 82 | 13 | 1.257 | [1.006, 1.612] | [0.933, 1.716] |
| Stage 2, repaired | 19 | 6 | 1.572 | [1.201, 1.958] | [0.800, 2.253] |
| pooled, deposited | 94 | 16 | 1.158 | [0.900, 1.497] | [0.827, 1.605] |
| pooled, repaired | 52 | 12 | 1.361 | [1.039, 1.789] | [0.741, 2.130] |

**The two Stage 2 rows are not the same statistic.** Stage 2 conditions on
substructure and sample form, so a fit whose cell is represented by no other
paper cannot be scored. On the deposit that drops 12 of 94 and leaves a cohort
that is 73 percent iron-based. On the repaired cohort it drops 33 of 52 and
leaves 19 fits that are 89 percent MgB2:

| cell | deposited | repaired |
|---|---:|---:|
| iron_pnictide_122, single crystal | 26 | 0 |
| iron_chalcogenide_11, single crystal | 20 | 0 |
| iron_pnictide_1111, polycrystal | 14 | 0 |
| conventional_AlB2, wire | 10 | 9 |
| conventional_AlB2, bulk | 10 | 8 |
| iron_pnictide_122, thin film | 2 | 2 |

1.257 to 1.572 is the iron-family error set beside the MgB2 error. It is not
Stage 2 degrading by 0.32 in exponent units. What degraded is Stage 2's reach:
it can score 87 percent of the deposited cohort and 37 percent of the repaired
one.

**Read the paper resample.** The deposited intervals resample residuals
independently, and residuals are clustered by paper: in the repaired Stage 2
arm one paper supplies 7 of 19. Resampling papers instead widens the repaired
Stage 2 interval from [1.201, 1.958] to [0.800, 2.253], which contains 1.0.
Any claim that the repaired field-axis error is above the screening threshold
does not survive. Neither version carries the uncertainty in the training
median, whose pools go down to a single fit, so both are floors on the width.

## 5. Compounds whose per-compound Form 3 fit converges

23 of 27 as published; **20 of 24** with the eleven withdrawn papers removed.

Three compounds disappear entirely because every row they had came from a
withdrawn paper: `BaFeAs2Ru`, `KBa(FeAs)4`, `Nd2FeAs2O`.

Five survivors lose rows and are refitted:

| compound | points | beta_T | beta_H | holdout R2 |
|---|---|---|---|---|
| Ba(FeAs)2 | 1026 to 657 | -0.162 to 0.889 | 11.99 to 12.85 | 0.276 to 0.768 |
| Fe2TeSe | 516 to 412 | 0.458 to 0.172 | 1.32 to 3.27 | -0.017 to 0.035 |
| K(FeAs)2 | 309 to 231 | 0.799 to 0.780 | 11.57 to 2.60 | 0.307 to 0.265 |
| LiFeAs | 96 to 66 | 1.001 to 1.365 | 2.93 to 8.64 | 0.009 to 0.979 |
| Sm2FeAs2O | 93 to 73 | -16.45 to -3.50 | 25.74 to 42.21 | 0.516 to 0.380 |

Each move is data loss and a redrawn holdout together. The original fitter
draws one random stream per compound and Forms 1, 2 and 3 consume it in order,
so removing rows re-randomises the split. The convergence count is unaffected,
because status depends only on the point and temperature counts, and no
compound keeps its Form 3 set while changing.

**"Converges" is the manuscript's word and the code does not support it.**
`fit_form` calls `least_squares` and returns the parameters without reading
`success` or `status`, so "ok" means the call did not raise. The gate that
decides the count is data sufficiency: at least 20 points passing the Form 3
filter and at least 3 distinct temperatures. Several of the 23 are fits nobody
would call converged, `Sm2FeAs2O` at beta_T of -16.5 and `Fe2TeSe` at a
negative holdout R squared among them. The rerun keeps the published rule,
because a like-for-like recount has to; the word has to change in the
documents.

The rerun reproduces the deposited Form 3 table first. Convergence status and
the holdout split match exactly on all 27 compounds; the worst relative
disagreement in any fitted parameter is 5.3e-7, which is the optimiser's
tolerance. The `kappa_pipeline.predictor` package is not in this repository, so
its two constants are supplied as a stub. Neither enters the Form 3 predictor,
the Form 3 filter or the random stream, but one of them is a guess, so every
`form1_` column is dropped before anything is written.

## What the reviews changed

Numbers that moved because a review found the first calculation wrong:

| statistic | first answer | after review |
|---|---|---|
| scale-of-exposure median | 0.836, 8 of 52 | 0.883, 11 of 52 |
| published-rule window reproduction | 43 of 52 | 49 of 52 |
| repaired Stage 2 interval | [1.201, 1.958] | [0.800, 2.253] |
| deposited Stage 2 interval | [1.007, 1.587] | [1.006, 1.612] |
| pooled repaired MAE | 1.364 | 1.361 |

Causes, in the same order. The denominator was the repaired anchor where the
published figure divides by the deposited one. The window check compared a
published-rule window against a repaired-rule column. The residual resample
treats readings of one figure as independent. The deposited arm ran at seed 0
where the deposit used 20260901, which leaves point estimates unchanged and
moves intervals. The scored field exponent was the no-floor fit, which is
bit-identical to the anchor table's `beta_repaired`, so the cohort was defined
by the stated protocol and the numbers were the ones the protocol rejects; it
differs on 3 of 52 by up to 0.183.

Two claims withdrawn as printed, because they were false against the numbers
beside them. That the resample fraction moves purely because the exponent
spread crosses 1.0: `iron_pnictide_122` sits below 1.0 in both arms and still
moves. That the leave-one-out predictor is worse than the in-sample family
median: it is, but that is true of any predictor and any data, because the
median minimises the quantity it is being compared against.

Guards. Two of the eight in the recompute script were tautologies, comparing a
column against the column it had been assigned from three lines earlier. The
reversed assignment they were written to catch passed both and moved the
repaired Stage 2 error from 1.57 to 1.04. They are replaced by checks against
the deposited files. The admission rule is now pinned, the bootstrap strata are
checked against the deposited stratum table, the paper resample is required to
reproduce the point estimate it accompanies, the cell table is required to
total the number of fits the predictor scores, and the published scale rule is
required to return the published figure before any row is reported. In the
rerun script, passing the wrong identifier column silently dropped zero rows
and reported a null rerun as complete; that now raises.

## Where this leaves the documents

Every blocked passage has a value now, but four of the seven cannot be
renumbered, only rewritten:

- the temperature leave-one-out passage needs the absolute threshold and the
  compression stated, or three MAEs falling by up to a factor of six will read
  as the repair improving the predictor;
- the exposure passage reverses direction and has to say so;
- the Stage 2 passage has to say the two cohorts are different material
  classes, or 1.257 to 1.572 reads as degradation;
- the Form 3 row needs "converges" replaced by the data-sufficiency rule it
  actually applies.
