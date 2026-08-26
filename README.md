# Substructure-conditional critical current density prediction

Data and analysis code for manuscript HT10016, submitted to *PRX Intelligence*.

Poddar, Chowdhury and Hossain, *Substructure-Conditional Critical Current Density
Prediction from Heterogeneous Superconductor Literature*.

Every count, ratio and validation figure reported in the manuscript and the
Supplemental Material can be reproduced from the files here. Where the paper
applies a screen at the reporting layer rather than inside the dispatch routine,
that screen is encoded explicitly in `audit/` so no count depends on a step that
exists only in the text.

## Layout

    data/      deposited tables, one row per record as described below
    analysis/  the scripts that produce every derived number
    audit/     reporting-layer screens and robustness checks
    figures/   figure source artwork as published

## data/

| file | rows | what one row is |
|---|---:|---|
| `phase_3_p31_jc_anchor_per_paper.csv` | 110 | one critical-current anchor, per paper per sample per isotherm |
| `phase_3_p31_variance_decomposition.csv` | 12 | the sample-form variance decomposition, per substructure |
| `phase_3_form3_fits_partial_cohortB_v2.csv` | 186 | one field-axis Form 3 fit, with both critical-field values and the provenance tier |
| `phase_3_p44_post_UCLA_beta_T_fits.csv` | 419 | one temperature-axis Form 3 fit |
| `phase_3_p47_compound_leave_out_MAE.csv` | — | compound leave-one-out validation results |
| `phase_3_p57_de_novo_predictions.csv` | 2151 | one candidate at one grid point, with its refusal code or its prediction |
| `provenance_table_fitcohort_full.csv` | 69 | one source paper contributing fitted curves |
| `reduced_variable_scaling.csv` | 66 | one populated bin of the reduced-variable grid |
| `caption_sweep.csv` | 2615 | one archived PDF, with the caption types detected in it |

## analysis/

- `phase_3_p57_de_novo_predictions.py` builds the candidate dispatch table.
  Four refusal conditions are implemented; two of them fire on this corpus.
- `figure_4_source.py` collapses multi-isotherm records to one row per physical
  sample and computes the variance decomposition. This is the aggregation the
  published ratios use.
- `phase_3_p58_variance_stability.py` is the robustness analysis for those
  ratios. See `audit/` for its output.
- `caption_sweep.py` screens the archive for papers whose captions name both a
  critical field against temperature and a critical current against field.
- `build_reporting_exclusions.py` regenerates the reporting-layer screens.
- `cross_model_agreement.py` runs a second independent reader over the vision
  cache and records field-level agreement with the first pass. It needs an API
  key in the environment, reads it from there only, and never writes it out.
  Papers in the fitted cohort are tagged and are processed first, so a partial
  run still answers at that scope. `summarise_agreement.py` reduces its output
  to the agreement rate and the manual-adjudication fraction.

## audit/

`reporting_layer_exclusions.csv` lists every tuple the paper removes after
dispatch, with the criterion for each. Two screens apply, and they overlap:

1. A candidate record whose transition-temperature anchor lies below 4.2 K, the
   lowest absolute grid temperature, cannot be evaluated at the reference point.
   21 of 239 records fail this; 218 are retained.
2. Six emitted tuples across two iron-chalcogenide candidates, `Fe1Te1` and
   `Fe1Se0.05Te0.95`, extrapolate to log10 Jc near 9.5 at their 0.77 Tc grid
   points, more than five standard deviations above the family mean.

Both screens fall on the same two compounds, so either alone takes the reported
candidate count from the 125 the dispatch emits to the 123 the paper reports.
`reporting_layer_summary.json` carries that arithmetic.

`phase_3_p58_variance_stability.csv` and `..._ordering.json` report the
robustness of the sample-form variance ratios under a bootstrap clustered on the
source paper, under leave-one-paper-out, and against a label permutation null.
The point estimates reproduce the published 0.73, 0.60 and 0.12. The intervals
around them are wide, and the ordering between families is not resolved at this
cohort size. Read that file before quoting the ratios as separable magnitudes.

## Reproducing

    python3 analysis/phase_3_p58_variance_stability.py
    python3 analysis/build_reporting_exclusions.py

Both run from the repository root and need only `pandas` and `numpy`.

The cross-model agreement run needs `anthropic` and `pymupdf`, an API key, and
the PDF directories, which are not redistributed here. From the analysis folder
that holds them:

    export ANTHROPIC_API_KEY=...
    python3 <path>/analysis/cross_model_agreement.py --dry-run
    python3 <path>/analysis/cross_model_agreement.py

## What is not here

Source articles are not redistributed, being subject to publisher copyright.
The tables carry article identifiers, extraction provenance, and figure
identifiers so that any value can be traced to its source figure.

## Licence

Data and documentation CC BY 4.0; code MIT. See `LICENSE`.
