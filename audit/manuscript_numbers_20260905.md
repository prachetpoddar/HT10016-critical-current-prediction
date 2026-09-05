# Table I, as published and repaired

Recorded 2026-09-05, after the decision to report the repaired cohort as primary
and keep the deposited one in the supplement. Script
`analysis/manuscript_numbers_repaired.py`, tables
`audit/manuscript_numbers_repaired.csv` and
`audit/supplement_fit_disposition.csv`.

## The eight printed quantities

| Table I row | published | repaired | moves |
|---|---:|---:|---|
| papers contributing fitted curves | 62 | **50** | yes |
| distinct compounds with fitted curves | 38 | **35** | yes |
| critical-current data points extracted | 4146 | **3303** | yes |
| temperature-axis partial fits | 260 | **257** | yes |
| field-axis partial fits passing | 94 | **52** | yes |
| field-axis source papers | 16 | **12** | yes |
| per-paper anchors behind Fig. 3 | 96 | 96 | no |
| candidate compounds evaluated | 183 | 183 | no |

Six of the eight move. Two do not, and it is worth saying why rather than
leaving it to be checked: no withdrawn paper appears in the anchor table, and
the prediction side is downstream of the fits but not of the anchors, so neither
is touched.

Where each repaired number comes from:

- **50 papers, 35 compounds, 3303 points**: the provenance table restricted to
  `status == contributing`, after the eleven withdrawals of 2026-09-03. One
  paper holds two rows, one per axis, so it counts once as a paper and twice as
  an extraction.
- **257 temperature-axis fits**: `apply_anchor_repairs.py`. Three of the 260 are
  not refitted, two whose paper has no rows in the extraction at all and one
  whose deposited rule was never reproduced. None is a cost of the repair.
- **52 field-axis fits over 12 papers**: `fit_protocol.py --report` on the
  cohort the anchor repair leaves.

## What became of the 94

This is the supplement's mapping table, and it is the reason for keeping the
deposited cohort visible: the halving is not a claim, it is a list.

| disposition | fits |
|---|---:|
| **kept** | **52** |
| dropped, paper withdrawn (`physc.2009.05.098`, `physc.2009.11.051`, `physc.2010.05.048`) | 24 |
| dropped, T/Tc above 0.7 under the repaired Tc | 11 |
| dropped, fails the field clause under the repaired anchor | 7 |

By paper:

| paper | kept | dropped |
|---|---:|---:|
| `mtphys.2022.100783` | 15 | 5 |
| `s10854-026-16566-9` | 8 | 4 |
| `physc.2013.04.060` | 7 | 1 |
| `1002.0208v2` | 6 | 0 |
| `jallcom.2023.170146` | 4 | 2 |
| `matchemphys.2023.128348` | 4 | 0 |
| `jallcom.2023.170384` | 2 | 0 |
| `matpr.2019.05.078` | 2 | 0 |
| four MAGLAB records | 4 | 0 |
| `phpro.2015.06.160` | 0 | 6 |
| `physc.2009.05.098`, `physc.2009.11.051`, `physc.2010.05.048` | 0 | 24 |

Two papers leave entirely for reasons already on file: `phpro.2015.06.160`
because its recorded 9.0 T anchor is the maximum applied field its own figure
states, and its own Hc2(0) of 26 and 31 T puts every fit below the 0.3 bound;
and the three withdrawn papers because none of them prints a critical field of
any kind.

## What does not change with the numbers

The substructure result is a temperature-axis result and it survives. Matched on
the seventeen papers both cohorts share, eta squared goes from 0.436 to 0.524
and the permutation p from 0.016 to 0.007. The field axis does not separate
substructure families under either cohort, eta squared 0.055 deposited and 0.038
repaired, permutation p 0.93 and 0.98, so that is not a claim the repair removes.
It was never supported.

## What still has to be written

1. Table I, six rows.
2. The substructure claim restated as a temperature-axis result, with the field
   axis reported as not separating rather than omitted.
3. A supplementary table carrying `audit/supplement_fit_disposition.csv`, so the
   94 to 52 is auditable row by row.
4. The disclosure: what was found, what changed, and the fact that eleven papers
   were withdrawn for defects in their extractions.

Nothing above is a new measurement. Every repaired number traces to a script in
this repository, named in `audit/manuscript_numbers_repaired.csv`.

## A defect found while writing this

The first version of the mapping matched a deposited fit to its repaired
disposition on paper and temperature alone. `physc.2013.04.060` carries eight
samples across two temperatures, so that match took the first of three and
reported eight kept where seven survive, and the total came out 53 against the
protocol's 52. The match now includes the sample and the two agree.
