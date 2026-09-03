# Full-repository sweep

Answering three questions across all 198 tracked files, after seven rounds in
which each "everything is consistent" was followed by a new finding.

## 0. The mechanism, and the checker nobody ran

`analysis/check_documents.py` has been in the deposit the whole time. It holds a
`SUPERSEDED` registry mapping a stale string to its replacement, and it reads
the .docx files directly. It was never run in this session.

    cd /home/claude && python3 ht_gh/analysis/check_documents.py --files \
        HT10016_revised_corrected.docx \
        SUPPLEMENTAL_MATERIAL_revised_corrected.docx \
        RESPONSE_TO_REFEREES_corrected.docx

    19 superseded value(s) stated as current; the package is not consistent

Nineteen, against four artifacts that five other checks call clean. Among them:
the manuscript and the letter both still carry the 26.8% anchor-count reduction,
which is (1.267 - 0.927)/1.267, a four-compound K=3 value against a
three-compound K=1 value. That is the exact cohort-mismatch error the same
paragraph claims to have corrected. `audit/external_anchor_count.csv` gives the
matched pair as 1.267 to 0.694, a reduction of 45.2%.

Every checker in the deposit must be run, not the ones written most recently.

## 1. Has the diagnostic finding already been explained?

Not in anything the referees will read. `audit/diagnostic_strength.md` covers
all of it and was written by this session an hour ago. The manuscript, the
supplement and the response letter address none of it.

The sharpest instance: the document set reports exactly one p-value for the
variance decomposition, in Sec. III.A, and it is the record-level one.

> "a label-permutation test cannot distinguish this low ratio from a weak
> sample-form signal concealed by sampling noise (p = 0.21)"

0.21 is `perm_p_naive` for `conventional_AlB2`. The paper-clustered value for
the same family is 0.6663. `analysis/permutation_test.py` says in its own
docstring that the record-level null "is the wrong one for this cohort" because
sample form is nearly collinear with source paper, and that the clustered null
"is a much harder test and it is the honest one". The paper quotes the null its
own code rejects, and quotes it only for the family where a null result supports
the choice made. No p-value or interval is given for 0.77 or 0.35, the two
labels the conditioning claim rests on.

`README.md` says both nulls "are read in the Supplemental Material". The
supplement contains no occurrence of "permut".

## 2. Stale values traced to source

### 2.1 The repair plan, 13 of 20 repairs never applied

`audit/repair_plan.csv` marks 20 rows non-sound, each with a named repair. Its
commit says "Nothing is corrected here". Joining against the live anchor table:

| paper | rows | planned | status |
|---|---|---|---|
| physc.2009.03.028 | 6 | withdrawn (re-extract) | applied |
| physc.2014.03.020 | 1 | rescaled x0.1 | withdrawn instead |
| **physc.2011.05.018** | 2 | **withdrawn (re-extract)** | **still live** |
| **physc.2009.11.051** | 2 | **withdrawn (re-extract)** | **still live** |
| **jallcom.2013.04.183** | 4 | **rescaled x10** | **not applied** |
| **jpcs.2026.113652** | 4 | **rescaled x0.01** | **not applied** |
| **mtphys.2022.100783** | 1 | **dropped (duplicate)** | **still live** |

All five source papers are complete and reachable in the upstream tree. The two
"withdrawn (re-extract)" papers were never entered in
`audit/withdrawn_records.csv`, which is why `verify_deposit.py` cannot see them.

### 2.2 Outcome A rests on two rows the repair plan says to withdraw

`physc.2011.05.018`'s two rows ARE the entire `polycrystal` cell of
`iron_chalcogenide_11`, at log10 Jc 4.699 and 5.000 against 6.07 for single
crystal and 5.96 for thin film. Outcome A is that gap.

| | eta^2 | band | n |
|---|---|---|---|
| baseline | 0.7687 | **A** | 10 |
| withdraw physc.2011.05.018 as planned | **0.0385** | **C** | 8 |

That extraction is graded FAIL, tier A in `audit/extraction_integrity.csv` with
flags `arithmetic duplicate_series field_beyond_hc2 grid_quantized`, and
`audit/isotherm_head_test.csv` flags its round heads. The paper's clearest
conditioning result rests on two anchor values from one Tier-A-FAIL extraction
the deposit's own plan marks for withdrawal.

### 2.3 Other traced defects

- The substructure matcher misses `Fe0.975Cu0.025Te0.66Se0.34` (an 11-type
  chalcogenide, no "FeTe" or "FeSe" substring) and `Ba_Fe_Co_2As2` (the
  underscore spelling of a 122 that `provenance_table_fitcohort_full.csv` calls
  `iron_pnictide_122`). Reclassifying both: chalcogenide 0.7687 A to 0.3737 B,
  and `other_unclassified` dissolves. Its 0.9880 Outcome A is three unrelated
  samples pooled because their formulas were spelled unusually.
- `physc.2010.05.048`'s anchor is 4.0e5 A/cm2 with n=110; the deposited source
  excerpt `data/extraction_examples/physc_2010_05_048_field_axis.csv` gives
  1.0e6 at the same point with 80 rows. Correcting it moves the chalcogenide to
  0.8527.
- 11 of 60 physical-sample groups average rows taken at different temperatures,
  9 at different fields. The worst spans 2.399 dex. `MAGLAB_11`, in the
  Outcome-A cell, averages a 1.0 T row with a 1.18e-5 T row.
- 40 of the 94 passing field-axis fits come from FAIL-graded extractions; 13
  from PASS-graded.
- `mtphys.2022.100783` contributes 8 polycrystal field-axis fits that are its
  own single-crystal fits re-indexed, agreeing to nine decimal places. Removing
  the duplicates moves the 122 family's field-axis compound-LOO from 0.9729 to
  1.0535, across the screening threshold of 1.0, which would close its dispatch.

### 2.4 Retraction

`audit/diagnostic_strength.md` says the three negative `H_anchor_T` values
corrupt the variance decomposition. That is too strong and is withdrawn. The
decomposition never reads `H_anchor_T`; correcting the sign changes eta^2 by
exactly zero, and removing the three rows gives 0.7553, still Outcome A. The
local slope at each isotherm head puts the worst propagated error at 0.0098 dex.
The negative fields are a real defect in the deposit, and they are evidence that
the anchor layer carries per-paper axis error, but they are not what Outcome A
depends on. What it depends on is 2.2.

## 3. Where refusal is fitted rather than principled

### 3.1 Three thresholds read off the retained set

`data/phase_3_p56_candidate_tier_assignment.csv` refuses 21 records against
per-family "empirical floors". Each floor equals the lowest Tc it must not
exclude:

| family | floor | lowest retained Tc | margin above | highest refused Tc |
|---|---|---|---|---|
| conventional_AlB2 | 4.50 | 4.500 | 0.000 | 3.640 |
| iron_chalcogenide_11 | 5.00 | 5.000 | 0.000 | 3.350 |
| iron_pnictide_122 | 5.10 | 5.110 | 0.010 | 2.997 |

`analysis/calibration_domain_screen.py` says so itself: "that is a circular
derivation". To the authors' credit this is the one fitted threshold the deposit
already flags.

### 3.2 A named-record exclusion selected on the outcome variable

`analysis/external_anchor_count.py:45` carries `NON_MONOTONIC = "Tl-1223_pure"`,
a hardcoded exclusion with no deriving code. The quantity that identifies it,
`K3_rho`, is the rank correlation between the predictor's own output and the
truth: a measure of how badly the predictor did, not a property of the
compound's data. Excluding it raises the headline anchor-count reduction from
26.8% to 45.2%. It is also the framework's stated non-monotonicity refusal code,
which fires on zero of 2097 dispatch targets.

### 3.3 Thresholds sitting between adjacent records

| gate | value | nearest below | nearest above | verdict |
|---|---|---|---|---|
| dispatch reduced field | 0.30 | 0.1667 | 0.32258 | 7.5% from emitting nothing |
| fit-level field span | 0.30 | 0.2672 | 0.3499 | principled, wide gap |
| dispatch reduced temperature | 0.70 | 0.69662 | 0.71174 | between two records |
| family screening MAE | 1.00 | 0.9729 | 1.0935 | between two families |
| T_FLOOR | 4.20 | 3.64 | 4.50 | principled, wide gap |

The temperature gate I added yesterday sits 0.48% above one surviving record,
and that record at 0.696621 is above the 0.694444 empirical support the gate's
own docstring cites. The 122 family's field-axis PASS at 0.9729 is decided by
two FAIL-graded papers; the chalcogenide's FAIL at 1.0935 is decided by one.

### 3.4 One gate, one target

`audit/field_window_gate.csv`: all 40 `family_fails_field_axis_validation`
refusals are `iron_chalcogenide_11`. The other failing family is hard-excluded
upstream and never reaches the grid. So that gate's entire observable effect is
closing the one family besides MgB2 whose targets clear the reduced-field bound.
And the gate exists only on the field axis: nothing applies a temperature-axis
family gate, and `conventional_AlB2`, the only family that dispatches, has no
temperature-axis leave-one-out at all, while every one of its 163 emitted
predictions uses a beta_T term.

### 3.5 Three of five named refusal codes fire on nothing

Sec. II names five: insufficient anchor density, non-monotonic behaviour,
unpopulated substructure, missing critical-field anchor, target above Tc. The
first two fire on zero of 2097; the anchor-density gate is not implemented at
all. The two codes doing 61% of the refusing, reduced field and reduced
temperature, are not on that list. They were added in this revision.

## 4. Re-extraction that was possible and not done

- Two re-extractions were completed to measurement grade and never merged.
  `data/reextraction/2012.13723_fig4_points.csv` (265 points, tick-fit residual
  5.9e-5) and `2207.06629_fig4_points.csv` (319 points). Both papers are live in
  the 260-fit temperature-axis table on the superseded v3.2.1 source. Refitting
  on the deposit's own window moves 2012.13723 from median beta_T 0.978 to 2.14
  and 2207.06629 from 1.568 to 1.84. Both are 122; the 25 fits are 24% of that
  family.
- 14 of the 20 surviving temperature-axis papers are graded LADDER by
  `audit/isotherm_head_test.csv`, the deposit's own screen for records needing
  replacement, and carry 196 of the 260 live fits. All 18 arXiv PDFs are
  reachable.
- 20 of 260 temperature-axis fits are near-exact duplicates within 9 papers.
- Two Tier-3 papers with a readable critical scale, `cjph.2024.09.042` and
  `1611.08455v1`, were named in `audit/table_corrections_20260903.md` and never
  refit. Tier 3 is 61 fits with 28 at the exponent ceiling. The one refit that
  was done moved six fits from median beta 6.2 to 0.22 and all six across the
  applicability gate.
