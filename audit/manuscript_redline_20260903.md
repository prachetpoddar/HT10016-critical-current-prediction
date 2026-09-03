# Manuscript and supplement redline

Every change below is against `HT10016_revised.docx` and
`SUPPLEMENTAL_MATERIAL_revised.docx` as they stand on 2026-08-26, which are the
current files: they carry the August corrections (16-fold, 4.7-fold, 13.0 per
cent, 24.3 per cent, 1.592, 1.166, 41.8 per cent, 2.81).

Each entry names the deposited file the new value comes from. Nothing here is
carried over from a previous write-up.

---

## 1. Table I

| row | from | to | source |
|---|---|---|---|
| Papers contributing fitted curves | 69 | **64** | `provenance_table_fitcohort_full.csv` |
| Distinct compounds with fitted curves | 43 | **39** | same |
| Critical-current data points extracted | 4387 | **4211** | same, `n_Jc_points` summed |
| Temperature-axis partial fits | 419 | **260** | `phase_3_p44_post_UCLA_beta_T_fits.csv` |
| Field-axis partial fits passing physicality | 95 | **94** | `phase_3_form3_fits_partial_cohortB_v2.csv` |
| ... from N source papers | 17 | **16** | same, distinct `arxiv_id` among passing |
| Per-paper anchors behind Fig. 3 | 110 | **103** | `phase_3_p31_jc_anchor_per_paper.csv` |
| Candidate compounds evaluated | 185 | **183** | `phase_3_p56_candidate_tier_assignment.csv` |

The candidate-compound row is the one change not caused by this audit. The
deposit has held 183 throughout; the mismatch was masked because the verifier's
constant had been seeded from the deposit. Confirm 183 before changing it.

---

## 2. Sec. II.A, source composition

**From:** "Twenty-nine of the 33 source papers behind the temperature-axis
exponent cohort are arXiv preprints"

**To:** "Eighteen of the 20 source papers behind the temperature-axis exponent
cohort are arXiv preprints"

The remaining two are `10.1016/j.jallcom.2022.165358` and
`10.1016/j.mtcomm.2022.103433`. Source: the 20 distinct `paper_id` values in the
temperature-axis fit table.

The same sentence appears in the supplement, Sec. on provenance, with the same
figures, and the supplement additionally says "the 69 source papers" twice.
Both become **64**.

---

## 3. Fig. 3 caption

**From:** "Of the 110 per-paper anchor records of Table I, 61 fall in the three
families shown ... The 61 collapse to the 44 markers drawn"

**To:** "Of the 103 per-paper anchor records of Table I, 59 fall in the three
families shown ... The 59 collapse to the 41 markers drawn"

Source: the anchor table filtered to `iron_chalcogenide_11`,
`iron_pnictide_122` and `conventional_AlB2`, then aggregated per physical sample
through `analysis/figure_4_source.py`.

The figure itself does not change. The three plotted families are unaffected by
the withdrawal, and their ratios remain 0.77, 0.60 and 0.12.

---

## 4. Sec. III.C, temperature axis

**From:** "Using the 419 temperature-axis fits ... Iron chalcogenide 11-type
reaches 0.261 across five compounds and 37 fits, with 92% of bootstrap resamples
below the screening-grade threshold of 1 ... Iron pnictide 122-type reaches
1.092 across three compounds, with only 38% of resamples below threshold. Iron
pnictide 1111-type reaches 1.721 across four compounds, with 8% below threshold."

**To:** "Using the 260 temperature-axis fits ... Iron chalcogenide 11-type
reaches 0.588 across five compounds and 89 fits, with every scorable bootstrap
resample below the screening-grade threshold of 1 ... Iron pnictide 122-type
reaches 1.314 across two compounds, with 30% of resamples below threshold. Iron
pnictide 1111-type reaches 3.120 across three compounds, with 21% below
threshold."

The conclusion is unchanged: iron chalcogenide 11-type is the only family that
clears the threshold on this axis, and its bootstrap support is now complete
rather than 92 per cent. Source: `analysis/compound_leave_one_out.py`,
`audit/temperature_axis_leave_one_out.csv`.

**A caution to add.** Two of the five chalcogenide compounds contribute one fit
each, so "five compounds" overstates the compound diversity behind 0.588.

---

## 5. Sec. III.C, the 122 paragraph

**From:** "The 122-type result is dominated by a single compound. Holding out
BaFe2As2, which supplies 147 of the 198 fits, gives 1.230; the other two
compounds give 0.686 and 0.701. The family figure is therefore largely a
statement about how well two compounds predict a third"

**To:** "The 122-type family now holds two compounds, Ba(FeAs)2 with 85 fits and
K(FeAs)2 with 21. A leave-one-compound-out across two compounds is a statement
about how well each predicts the other, and we report it as that rather than as
a family-level generalization test."

**And in the same paragraph, on the MgB2 temperature exponent.**

**From:** "a separate per-paper Form 3 cohort of 15 MgB2 fits across 15 arXiv
sources ... with a median βT of 1.14"

**To:** "a separate Form 3 cohort of 15 physical MgB2 fits with a median βT of
1.14"

The median reproduces exactly from `h1b_per_paper_form3_fits.csv`: 15 of its 16
MgB2 rows are flagged physical and their median is 1.140. The phrase "across 15
arXiv sources" does not. That file records two extraction-pass labels in its
`source` column and no paper identifier, so the deposit cannot say which papers
these 15 fits came from. Either the per-paper provenance is added to the deposit
or the claim is dropped. Referee A asks four times to see the data behind a
number, and this is a dispatched exponent whose sources cannot be traced.

---

## 6. Sec. III.C, field axis. Two conclusions change.

**From:** "The same protocol on the field-axis cohort gives 0.641 for iron
chalcogenide 11-type, 0.753 for MgB2-class, and 0.973 for iron pnictide
122-type, with iron pnictide 1111-type at 3.07 ... repeating the field-axis test
with a substructure-median predictor ... gives 0.558, 0.751, 0.929, and 3.13,
preserving the ordering."

**To:** "The same protocol on the field-axis cohort gives 0.753 for MgB2-class,
0.973 for iron pnictide 122-type and 1.094 for iron chalcogenide 11-type, with
iron pnictide 1111-type at 2.571. Repeating the test with a substructure-median
predictor gives 0.751, 0.930, 1.094 and 2.622."

Two things the old text asserts are no longer true.

**Iron chalcogenide 11-type no longer passes on the field axis.** At 1.094 it is
above the screening-grade threshold of 1. The graded applicability claim in the
next paragraph, and Table III, follow from this.

**The ordering is no longer the same on both axes.** Chalcogenide is first on
the temperature axis and third on the field axis. The sentence claiming a
preserved ordering has to go.

Neither change is caused by the corrections applied today. Both predate them.
Today's refit improved 1111 from 3.129 to 2.571.

---

## 7. Sec. III.C, the graded applicability claim

**From:** "Iron chalcogenide 11-type is the only family that passes on the
temperature axis ... and it passes on the field axis as well. Iron pnictide
122-type and MgB2-class pass on the field axis only"

**To:** "Iron chalcogenide 11-type is the only family that passes on the
temperature axis, whose critical scale is directly reported, and it does not
pass on the field axis. MgB2-class and iron pnictide 122-type pass on the field
axis only, and their validation inherits the qualification of Section III.F.
Iron pnictide 1111-type fails on both axes."

No family now passes on both axes. That is a weaker claim than the manuscript
makes and it should be stated plainly rather than absorbed into the table.

---

## 8. Sec. III.B and the summary, the conditioning claim

**From (Sec. III.B):** "On the matched five-family cohort the reduction is
16-fold on means and 4.7-fold on medians."

**From (summary):** "Substructure and sample-form conditioning reduces
field-exponent error 16-fold on means and 4.7-fold on medians relative to
monolithic regression."

**To (Sec. III.B):** "Both figures are in-sample: the predictor for a held-out
family is built from a pool that contains that family's own fits. Under a
leave-one-substructure-out protocol, in which the held-out family is withheld at
every stage, no reading of Stage 2 reaches a two-fold reduction on any cohort we
can construct, the best being 1.77-fold. Stage 3, which reports a
substructure-level central tendency with an explicit interquartile range,
reaches 1.73-fold on means and 1.99 on medians across all families, and 2.32 and
2.23 with the cuprates removed. We report the leave-one-substructure-out figures
and no longer present the matched-cohort ratio as a headline."

**To (summary):** "Substructure conditioning reduces field-exponent error about
two-fold under leave-one-substructure-out validation, and the interquartile
bound reported with it covers the residual in four of four families once the
cuprates are removed."

Source: `analysis/multi_stage_loso.py`, `audit/multi_stage_loso.csv`.

This also revises the reply to Referee A9 in the response letter, which
currently offers 16-fold and 4.7-fold as the corrected figures.

---

## 9. Supplement, the field-scale exposure section

"the median ratio of measured maximum to assigned scale is 0.86, and for 15 of
77 curves it exceeds 0.9" needs recomputing on the 94-fit passing cohort. Not
yet done.

"A caption-scoped screen over the 2615 unique PDFs in the archive finds 137
whose figure captions name both" needs reconciling with the screen run in this
audit, which counts **2597** unique PDFs, 966 carrying a Jc figure caption and
422 naming field sweeps with several isotherms. The difference in the archive
size needs explaining before either number is printed.

---

## 10. Additions the audit supports

**Data availability.** The deposit now carries 585 points re-measured directly
from two published figures with their calibration files, tick-label fits,
re-projection residuals and overlay images. This is a direct answer to Referee
A1 and should be named in the Data Availability statement.

**A withdrawal to disclose.** `10.1038/s41467-025-55880-4` contributed 36 source
points, 6 field-axis fits and 2 anchor rows. The paper reports no current
density in any units. This belongs in the text, not only in the deposit.

**Referee A11.** The temperature-axis table records the 1111 compounds as
`Pr2FeAs2O`, `La2FeAs2O` and `Sm2FeAs2O`. The referee flagged `La2FeAsO` for
`LaFeAsO` in the prose; the same error is in the data.

---

## What is not covered here

Referee A2, A4, A6, A10 and A12, and all of Referee B, are exposition and
framing. Nothing in this audit bears on them.
