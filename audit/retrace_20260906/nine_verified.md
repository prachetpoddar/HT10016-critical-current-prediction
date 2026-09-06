# The nine, verified and attacked

Recorded 2026-09-06. Each of the nine findings carried forward from
`unstated_conventions.md` was retraced against the deposit and then given to an
independent reviewer with instructions to break it. Two broke. Two were
weakened to a narrower statement. Five survive, four of them with a corrected
number.

The order below is the order in which they should be acted on, not the order
they were found in.

## Survives, and is the sharpest thing in the paper

### The K-anchor error is in dex and is labelled as a dimensionless exponent

`analysis/external_anchor_count.py` line 51:

    d["abs_err"] = (d.predicted_log_Jc - d.actual_log_Jc).abs()

That is a difference of base-10 logarithms of critical current, in dex. It is
printed as an exponent error in three places: Sec. III.A and Table III ("One
anchor gives 1.592 exponent error"), the Fig. 4 caption ("mean absolute error
in the dimensionless field-dependence exponent"), and Supplement Sec. 4
("dimensionless exponent errors").

Sec. II.A polices this exact distinction in the opposite direction: "An earlier
version of this manuscript reported exponent errors in dex, which made a value
such as 10.10 read as ten orders of magnitude in current." The repair the paper
says it made throughout was not made here.

### Table II's caption says the splits are identical across forms; they are not

`run_closed_form_fits.py::run_per_compound` creates one `default_rng(42)` per
compound and consumes it inside the form loop, so each form draws a different
permutation. Measured over all 23 fittable compounds, **zero** have identical
Form 1 and Form 3 holdout sets, and every overlap sits at the chance rate. For
MgB2 the two forms filter to the same 2055 points and share 81 of 411 holdout
points against a chance expectation of 82.

The caption's phrase "identical splits across forms" is what makes the three
mean absolute errors comparable. It does not hold for any compound.

### Table II's split is point-level inside a compound, which Sec. II.B rejects

The same function shuffles that compound's own rows and cuts 80/20, so every
held-out point sits on a curve whose other points trained the model. Sec. II.B:
"Random k-fold pooling can place measurements of the same compound in both
training and test folds, which overstates generalization for a
literature-derived predictor." That is the procedure behind Table II, and
Table II is what selects Form 3 for the whole paper.

Two further caption defects: the generator groups by compound
(`mp_formula`), not by paper, and the printed statistic is the median across
compounds. On means the three values are 0.672, 0.578 and 0.519, so the Form 2
to Form 3 margin falls from 26 percent to 10 percent on an aggregator neither
document states.

Nothing in the deposit generates Table II. The fitter and its input dataset
are both outside the repository.

**Retracted from the earlier note:** the claim that Form 1's 0.597 cannot be
reproduced. It reproduces at `LOG_H_EPS = 1e-6` (median 0.5974, mean 0.6719,
matching both published Form 1 figures). The stub in
`audit/closed_form_rerun/` guessed 1e-3. All three of Table II's numbers
reproduce. Refitting after the withdrawals gives 0.534 / 0.315 / 0.223, so the
ordering and the choice of Form 3 are unchanged.

### The 15 MgB2 temperature fits are described wrongly in both particulars

`data/h1b_per_paper_form3_fits.csv`, the 15 rows with `physical_beta_T`, median
beta_T 1.1396, which pins the cohort.

- "one resting on three points": six rows have `n_data_points == 3`
  (0201261, 0204068, 0306083, 0311055, 1102.5625, 1412.2265), seven by
  `n_distinct_T`. No filter recovers one.
- "one fitting with an rms of 6.3 in log10 Jc": the largest rms in the file is
  0.474094. The 6.3 is `MgB2__0108265`, whose rms is 6.332371e-14 with
  `beta_T = 3.14e-13` and `log_Jc_0 = 6.000000000000087`: a fit to a constant,
  and the best-conditioned row in the cohort rather than the worst. The
  exponent was dropped in transcription.

Two of the six three-point fits return beta_T of 0.011 and 0.211, and they sit
in the support of the median that is dispatched to every MgB2-class candidate.

### Stage 3's 0.84 is a resubstitution figure called a leave-one-out error

In `analysis/phase_3_p39_multi_stage_predictor.py`, `sub_med` is built from the
full cohort and `s3_pred = sub_med.get(sub)` for the held-out family, so the
held-out family predicts itself. The deposited artifact
`data/phase_3_p39_multi_stage_mae_decomposition.csv` records
`stage3_abs_residual = 4.44e-16` for `conventional_AlB2`, which is the
signature. Sec. III.A calls 0.84 "a leave-one-substructure-out error in the
field exponent". It is not one, and it reproduces from no cohort in the current
deposit: resubstitution on the current cohort gives 0.347, and the genuine
leave-one-substructure-out value on the cuprates-removed arm that the very next
sentence relies on is **0.816**.

The paragraph immediately above it withdraws Stages 1 and 2 for exactly this
defect, from the same generator and the same run.

Separately, Table III's conditioning row declares a scope of "matched
five-family cohort" and reports numbers from cohorts of seven families
(12.3 / 14.9), three families (1.19 / 0.55) and four families (the interquartile
coverage). None of the three is five.

**Corrected from the earlier note:** the genuine value to quote is 0.816, not
9.006. The 9.006 is the seven-family all-fits arm, which is not the arm the
manuscript's own sentence points at.

### The variance-ratio regime cuts are undisclosed and unstable

`regime_from_variance_ratio` in
`analysis/phase_3_p39_multi_stage_predictor.py` cuts at 0.7 and 0.3, duplicated
in `phase_3_p57_de_novo_predictions.py` and `regenerate_regime_tables.py`.
Neither document states them anywhere. This is a different pair of numbers from
the applicability window (reduced temperature below 0.7, reduced field above
0.3), which is stated three times and is not at issue.

The paper applies an omega-squared bias correction to the MgB2 family and says
so. Applying the same correction uniformly, using the repository's own
`retrace_variance_decomposition.py`, which reproduces every published eta
squared:

| cohort | family | eta2 | regime | omega2 | regime |
|---|---|---:|---|---:|---|
| deposited | iron chalcogenide 11 | 0.3737 | B | 0.2192 | **C** |
| deposited | iron pnictide 122 | 0.4877 | B | 0.3180 | B |
| repaired | iron chalcogenide 11 | 0.8090 | A | 0.7007 | A |
| repaired | iron pnictide 122 | 0.3743 | B | 0.1371 | **C** |

The one surviving Regime A assignment clears its cut by 0.0007. No dispatched
output changes, because the families that move emit nothing. The finding is an
undisclosed and unstable classification rule, not a wrong result.

## Weakened to a narrower statement

### The 0.29 dex propagation

Two limbs survive. The manuscript states a residual standard deviation of 1.158
in beta_T; the deposited 106-fit iron pnictide 122 cohort gives 1.1712, and no
mask, cohort or estimator variant reproduces 1.158. The other two components,
0.265 and 0.920, reproduce to four digits, which pins the intended
construction. Separately, 1.15781 is a deposited number: it is the pooled
per-paper field-axis validation error in `blocker_statistics_repaired.csv`,
printed two paragraphs later in the same supplement section as "1.158 over 94".
The collision is worth stating; the attribution is inference and should not be
asserted.

Second limb: the supplement says that where the terms are positively correlated
the independent quadrature understates the aggregate, so 0.29 should be read as
a lower bound. Using the supplement's own measured correlations from the same
section (-0.00, +0.36, -0.05) the correlated propagation gives **0.253 dex**.
The caveat points away from its own measurements. Note that the mechanism must
be stated carefully: the beta_T to beta_H cross term does increase variance
under positive correlation; the reduction comes from the two anchor-exponent
pairs, which dominate.

Third: on the MgB2 class, the only family that dispatches, the same propagation
gives 0.486 dex at 4.2 K and 0.573 dex at 20 K.

**Retracted:** the claim that the (22 K, 50 T) evaluation anchor is not the
candidate cohort's mode. It is the mode, by 144 rows to 63, and Fig. 5's caption
says the grid uses each family's most common anchor. **Retracted:** the framing
that the 122 scope is concealed. It is disclosed three times.

### Figure 5's 0.31 dex band

Mechanically true: `HALF = 0.30583` computed over 163 non-refused rows that are
all MgB2-class, and drawn with the same scalar around all three families. But
the caption discloses both halves, and the regenerated figure is md5-identical
to the embedded image, so the figure is what the code produces.

**Retracted:** the 0.103 half-width attributed to the 122 family. That family
emits nothing and has no emitted half-width; its withheld median is 0.1217.

What replaces this finding is worse and was not in the original sweep:
`analysis/fit_family_params.py`, which `manuscript_figure_5.py` names as the
regenerator of `data/family_params.json`, **crashes on the deposited prediction
file**, because no non-refused row exists for two of the three families. The
family parameters behind Figure 5's three curves are a frozen artifact from a
cohort state that is not in the deposit, and the module docstring's claim that
reading them from the dispatch table is what lets the figure be checked against
the withdrawals describes a check that cannot be run.

## Broken

### The 52 against 63 field-axis cohort

Retracted. The arithmetic is right (63 by Eq. (1) as printed, 52 with the
temperature clause, and the deposit's own `passing_repaired` column is 63) but
the choice is disclosed, in the response letter, under its own heading: "The
applicability window was applied to one axis and not the other... It is now
applied to both", with the cost given to the fit, "11 above the reduced
temperature bound once the anchor is corrected".

The charge that `MIN_LEVER_DEX` conflicts with the lever bound in
`apply_anchor_repairs.py` also fails: `admits()` does not gate on the lever at
all.

Two small things remain, for the author rather than a referee. The disclosure
lives only in the response letter, while Eq. (1) still reads "respectively" and
Sec. III.C still attributes 52 to "the stated fitting protocol", so a reader of
the manuscript alone cannot get 52 from what is printed. And the response letter
says "the Supplemental Material now carries the disposition of all 94
individually"; the supplement's fifteen sections contain no such table, although
`audit/supplement_fit_disposition.csv` carries all 94 rows.

### The 0.88 exposure ratio

Retracted. Dividing by the pre-repair anchor is the correct like-for-like
choice when the ratio is being compared across two cohorts, it is documented at
length in `recompute_blocker_statistics.py::scale_ratio`, and
`audit/blocker_statistics_20260905.md` records that an earlier version divided
by the repaired anchor, printed 0.836, and was reverted deliberately. The claimed
inversion of the tail fraction is 16.0 percent to 15.4 percent, which is flat.

One clause is worth adding: neither document says the denominator is the
pre-repair anchor, and "the assigned scale" reads as the scale now in force.

## What still survives every construction tried

The temperature-axis conditioning result, eta squared 0.524 with a
paper-clustered permutation probability of 0.007. Table I's counts. The choice
of Form 3 itself, which holds after the withdrawals even though every number in
Table II moves.
