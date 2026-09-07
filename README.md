# Substructure-conditional critical current density prediction

Data and analysis code for manuscript HT10016, submitted to *PRX Intelligence*.

Poddar, Chowdhury and Hossain, *Substructure-Conditional Critical Current Density
Prediction from Heterogeneous Superconductor Literature*.

Every count, ratio, figure and validation result in the manuscript and the
Supplemental Material is produced by the code here from the tables here. Where
the paper applies a screen at the reporting layer rather than inside the
dispatch routine, that screen is written out in `audit/`, so no printed number
depends on a step that exists only in the prose.

## Reproducing, in five commands

Run from the repository root. `pandas`, `numpy` and `matplotlib` are the only
requirements for the first four; `python-docx` and `Pillow` for the checks that
read the documents.

    python3 analysis/verify_deposit.py
    python3 analysis/rebuild_dispatch.py
    python3 analysis/check_figures.py out_final52/HT10016_revised_final52.docx
    python3 analysis/final_consistency_check.py out_final52
    python3 analysis/check_claims_against_deposit.py --dir out_final52

Each exits non-zero on failure, and together they are the whole verification
surface.

`verify_deposit.py` prints the cohort counts, the per-substructure
classification and a set of internal consistency checks. It exists because this
deposit twice shipped disagreeing with itself: a withdrawal applied to the
source tables and not to the derived decomposition, and a unit correction that
reached two fields out of four. Both are invisible to an author reading the
prose and obvious to a reader running the code.

`rebuild_dispatch.py` rebuilds `data/phase_3_p57_de_novo_predictions.csv` in a
scratch copy of the repository and compares it with the deposited file cell by
cell. The dispatch table is the output of four scripts run in order, not one,
and this is the only place that order is written down:

    analysis/phase_3_p57_de_novo_predictions.py   the predictor
    analysis/withdraw_records.py                  removes withdrawn records
    analysis/apply_field_window_gate.py           the reduced-field clause
    analysis/apply_temperature_window_gate.py     the reduced-temperature clause

Running the first alone returns 2151 rows against the deposited 2097, and two
of the five refusal codes. The verify mode writes nothing under the repository.

`check_figures.py` regenerates all five manuscript figures and compares them
with the committed PNGs, compares every image embedded in the document with its
committed PNG, and checks that every display extent matches its image's aspect
ratio. The regeneration half is conditional on where it is run: matplotlib
sizes the canvas from rendered text extents, so a figure redrawn on a machine
that did not draw it can differ by a pixel of width.
`figures/render_env.json` records the machine that did, and away from it that
check reports `n/a` rather than claiming the deposit is broken.
`audit/figure_5_cross_platform_20260904.md` measures one such case.
`analysis/test_check_figures.py` plants nine known defects and requires the
checker to catch each one.

`final_consistency_check.py` asserts the printed counts against the deposited
tables and checks the three documents against each other: that no withdrawn
figure appears outside the sentence that retires it, that a number printed in
two documents is the same number, and that the revision has created no
statement contradicting another.

`check_claims_against_deposit.py` binds individual numeric claims in the
documents to the deposit quantity each is supposed to equal.

## Figures

| manuscript | generator | output |
|---|---|---|
| Fig. 1, framework overview | `analysis/manuscript_figure_1.py` | `figures/manuscript_figure_1.png` |
| Fig. 2, runtime architecture | `analysis/manuscript_figure_2.py` | `figures/manuscript_figure_2.png` |
| Fig. 3, sample-form conditioning | `analysis/figure_4_source.py` | `figures/manuscript_figure_3.png` |
| Fig. 4, anchor-count sensitivity | `analysis/manuscript_figure_4.py` | `figures/figure_4_anchor_count.png` |
| Fig. 5, family-scope envelopes | `analysis/manuscript_figure_5.py` | `figures/manuscript_figure_5.png` |
| Fig. S1, extraction examples | `analysis/manuscript_figure_s1_extraction_examples.py` | `figures/figure_S1_extraction_examples.png` |

Figure 3's generator is named `figure_4_source.py` because the name predates the
figure renumbering and several other scripts import from it. It is also the
library that performs per-physical-sample aggregation and the variance
decomposition, so `verify_deposit.py` imports it without needing a plotting
stack.

## The cohort, computed rather than quoted

Regenerate this table with `python3 analysis/readme_counts.py`, and check it
with `python3 analysis/readme_counts.py --check README.md`.

| quantity | value |
|---|---:|
| source papers contributing fitted curves | 50 |
| distinct compound labels | 35 |
| extracted critical-current points | 3303 |
| temperature-axis fits | 257 |
| field-axis fits passing physicality | 52 |
| field-axis source papers | 12 |
| per-paper anchor rows, as deposited | 96 |
| per-paper anchor rows, after repair | 70 |
| physical samples behind Fig. 3, after repair | 36 |
| source papers behind Fig. 3, after repair | 20 |
| candidate records evaluated | 233 |
| distinct candidate compounds | 183 |
| compounds receiving a dispatched target | 84 |
| prediction targets emitted | 163 |
| prediction targets refused | 1934 |

## Withdrawn and repaired records

Both cohorts are deposited, so either version can be reproduced.

`audit/withdrawn_records.csv` carries seven record-level withdrawals with the
figure checked and the reason for each. `audit/withdrawn_beta_T_papers.csv`
carries eleven temperature-axis papers withdrawn after their figures were
opened: three record a current axis in A/m² as A/cm², two record the minor ticks
of a logarithmic field axis as field values, six carry isotherms that are exact
arithmetic ramps, and one interleaves two series three orders of magnitude apart
inside a single isotherm.

The anchor repair of Sec. III.F withdraws 26 of the 96 per-paper anchor rows and
corrects a scale error on 15 more. `analysis/withdraw_records.py` applies the
withdrawals and regenerates everything downstream in the same run.
`audit/supplement_fit_disposition.csv` gives the disposition of all 94
field-axis fits individually, 52 kept and 42 dropped with the reason for each.

## data/

| file | rows | what one row is |
|---|---:|---|
| `phase_3_p31_jc_anchor_per_paper.csv` | 96 | one critical-current anchor, per paper per sample per isotherm |
| `phase_3_p31_jc_anchor_per_paper_repaired.csv` | 96 | the same, with the repair, the withdrawal reason and the as-deposited value |
| `phase_3_p31_variance_decomposition.csv` | 8 | the sample-form variance decomposition on the deposited anchors |
| `phase_3_p31_variance_decomposition_repaired.csv` | 7 | the same on the repaired anchors, which is what Fig. 3 draws |
| `phase_3_form3_fits_partial_cohortB_v2.csv` | 159 | one field-axis Form 3 fit, with both critical-field values and the provenance tier |
| `phase_3_p44_post_UCLA_beta_T_fits.csv` | 260 | one temperature-axis Form 3 fit, as deposited |
| `phase_3_p44_post_UCLA_beta_T_fits_repaired.csv` | 260 | the same with the repaired exponent and a reproduction flag; 257 carry both |
| `phase_3_p47_compound_leave_out_MAE.csv` | 4 | one family's compound leave-one-out validation result |
| `phase_3_p57_de_novo_predictions.csv` | 2097 | one candidate at one grid point, with its prediction or its refusal code |
| `provenance_table_fitcohort_full.csv` | 62 | one source paper, with its contribution status |
| `reduced_variable_scaling.csv` | 66 | one populated bin of the reduced-variable grid |
| `anchor_form_permutation.csv` | 6 | one family on one cohort, with both exact permutation nulls |
| `caption_sweep.csv` | 2615 | one archived PDF, with the caption types detected in it |

## analysis/

- `phase_3_p57_de_novo_predictions.py` builds the candidate dispatch table. Six
  refusal codes are implemented and five fire on this corpus. It reads each
  family's conditioning regime from the deposited variance decomposition, so a
  change to the diagnostic reaches the predictor rather than leaving the two to
  disagree.
- `figure_4_source.py` collapses multi-isotherm records to one row per physical
  sample and computes the variance decomposition. This is the aggregation the
  published ratios use. It reproduces the deposited-cohort ratios before drawing
  anything, so a change to it stops the run rather than silently redrawing
  Fig. 3.
- `anchor_form_permutation.py` enumerates both permutation nulls behind
  Sec. III.A exhaustively, on both cohorts, and checks its own effect-size
  primitive against the deposited decomposition before either null runs.
- `functional_form_comparison.py` scores the three candidate functional forms on
  identical rows under point, curve and source-paper holdouts.
- `final_consistency_check.py`, `check_claims_against_deposit.py`,
  `check_figures.py`, `verify_deposit.py` and `rebuild_dispatch.py` are the
  verification surface described above.
- `build_reporting_exclusions.py` regenerates the reporting-layer screens.
- `cross_model_agreement.py` runs a second independent reader over the vision
  cache and records field-level agreement with the first pass. It needs an API
  key in the environment, reads it from there only, and never writes it out.

## audit/

`audit/` is the evidence for the corrections the paper reports on itself, and
the response to referees points to it. It is not scratch work.

`reporting_layer_exclusions.csv` lists every tuple the paper removes after
dispatch, with the criterion for each. Two screens apply: a candidate record
whose transition-temperature anchor lies below 4.2 K cannot be evaluated at the
reference point, which removes 21 of the 233 records and retains 212; and six
emitted tuples across two iron-chalcogenide candidates extrapolate more than
five standard deviations above their family mean at the 0.77 Tc grid point.
Both fall on candidates that emit nothing, so neither changes a reported count.

`dispatch_spread_20260905.md` traces where the narrow dispatch spread comes from
and records what it can and cannot support. `field_window_gate.csv` and
`temperature_window_gate.csv` record every target the two applicability clauses
refuse, with the value withheld. `hossain_readiness_actions_20260906.md` records
the submission-readiness actions and the disposition of each.

Section 17 of the Supplemental Material carries the audit trace in the form a
referee reads; `audit/` carries the files behind it.

## What is not here

Source articles are not redistributed, being subject to publisher copyright. The
tables carry article identifiers, extraction provenance and figure identifiers
so that any value can be traced to its source figure.

Intermediate revisions of the three documents are no longer tracked. The
submitted set is in `out_final52/`; earlier stages remain in the git history.

## Licence

Data and documentation CC BY 4.0; code MIT. See `LICENSE`.
