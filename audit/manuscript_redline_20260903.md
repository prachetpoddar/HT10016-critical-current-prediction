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

**No change. An earlier version of this redline said the deposit could not
identify these 15 papers. That was wrong.** It read the `source` column of
`h1b_per_paper_form3_fits.csv`, which carries the extraction-pass label, and
missed the `phase_f_filename` column beside it, which carries the arXiv
identifier of each source paper. The 15 physical MgB2 rows resolve to 15
distinct arXiv preprints, and their sample forms are six bulk, five thin film,
three wire and one tape, so "15 MgB2 fits across 15 arXiv sources, spanning
bulk, thin-film, wire and tape specimens, with a median betaT of 1.14" is
correct as printed and fully traceable from the public deposit.

Two of the 15 are weak enough to be worth a clause, since this cohort supplies a
dispatched exponent. `MgB2__0108265` fits with an rms of 6.33 in log10 Jc and is
still flagged physical, and `MgB2__0201261` rests on three points and returns a
temperature exponent of 0.011. Adding "two of the fifteen are poorly constrained"
would be more accurate than the present sentence and costs nothing.

---

## 6. Sec. III.C, field axis. Two conclusions change.

**From:** "The same protocol on the field-axis cohort gives 0.641 for iron
chalcogenide 11-type, 0.753 for MgB2-class, and 0.973 for iron pnictide
122-type, with iron pnictide 1111-type at 3.07 ... repeating the field-axis test
with a substructure-median predictor ... gives 0.558, 0.751, 0.929, and 3.13,
preserving the ordering."

**To:** "The same protocol on the field-axis cohort gives 0.753 for MgB2-class,
0.973 for iron pnictide 122-type and 1.093 for iron chalcogenide 11-type, with
iron pnictide 1111-type at 2.571. Repeating the test with a substructure-median
predictor gives 0.751, 0.929, 1.094 and 2.622."

Two things the old text asserts are no longer true.

**Iron chalcogenide 11-type no longer passes on the field axis.** At 1.093 it is
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

## 9. Supplement, recomputed

**Scale of the exposure.** Recomputed on the current 94-fit passing cohort by
matching each fit back to its source curve in the extraction dataset and keeping
the points the fit actually used, that is those below the assigned scale. The
match is sound: the fitted window reproduces on 90 of the 94 curves and the
point counts agree on the same 90. The four that differ are the PrFeAsO
isotherms whose scale changed in this round.

| statement | printed | recomputed |
|---|---|---|
| median ratio of measured maximum to assigned scale | 0.86 | **0.800** |
| curves whose ratio exceeds 0.9 | 15 of 77 | **15 of 94** |
| field-axis curves in the three dispatched families | 80 | **77** |
| assigned scales that are an irreversibility field or unlabelled | 31 of 80 | **30 of 77** |
| curves clearing the 0.3 span against the literature Hc2,0 | 26 of 80 | **28 of 77** |

Two statements in the same passage could not be recomputed.

"Fifty-four of the 80 field-axis curves ... take their scale from one of those
eight papers" needs the list of eight papers from the dual-model critical-field
audit, which is not in the deposit and which I could not locate in the workflow
folder. Either the list is deposited or the sentence is dropped.

"13 qualify once the magnetic-field unit corrections are also applied" needs the
pre-correction extraction dataset to compare against. The deposit and the
workflow folder both hold the corrected version only, so the comparison cannot
be redone.

**The archive size.** The supplement says "the 2615 unique PDFs in the archive".
That is the row count of the deposited `data/caption_sweep.csv`, and **21 of its
rows are not papers**: eleven matplotlib toolbar icons, each carrying one
character of extracted text (`back.pdf`, `filesave.pdf`, `forward.pdf`,
`hand.pdf`, `help.pdf`, `home.pdf`, `matplotlib.pdf`, `move.pdf`,
`qt4_editor_options.pdf`, `subplots.pdf`, `zoom_to_rect.pdf`), and ten figures
generated by this project.

**2615 becomes 2594.** The 137 papers whose captions name both a critical field
against temperature and a critical current against field are unaffected: all 137
are real papers.

An independent enumeration run for this audit counts 2587 papers over the same
folder tree, agreeing to seven papers in about 2590. The difference is files
added or moved between the two runs.

**Separately, and not a manuscript edit.** Four of the filenames published in
`caption_sweep.csv` are `cross_class_kappa_jc0.pdf`,
`kappa_jc_extended_correlation.pdf`, `kappa_vs_tc_scatter.pdf` and
`roberts_1976_critical_fields_compilation.pdf`. The manuscript is under a
constraint not to reference Roberts 1976 or to point forward to the kappa-Jc0
work, and these filenames are in a public deposit. Worth a decision before the
next release.

---

## 10. Additions the audit supports

**Data availability.** The deposit now carries 585 points re-measured directly
from two published figures with their calibration files, tick-label fits,
re-projection residuals and overlay images. This is a direct answer to Referee
A1 and should be named in the Data Availability statement.

**A withdrawal to disclose.** `10.1038/s41467-025-55880-4` contributed 36 source
points, 6 field-axis fits and 2 anchor rows. The paper reports no current
density in any units. This belongs in the text, not only in the deposit.

**The exponent ceiling, named.** All 28 remaining fits at the ceiling of 30 come
from seven papers, 23 of them cuprate, and every one takes its critical field
from a literature default. Referee A9 asks whether the extreme errors are driven
by cuprate fits; this answers the question with the records rather than with a
qualification.

**Referee A11.** The temperature-axis table records the 1111 compounds as
`Pr2FeAs2O`, `La2FeAs2O` and `Sm2FeAs2O`. The referee flagged `La2FeAsO` for
`LaFeAsO` in the prose; the same error is in the data.

---

## What is not covered here

Referee A2, A4, A6, A10 and A12, and all of Referee B, are exposition and
framing. Nothing in this audit bears on them.

---

## Appendix: the two replacement passages in full

Written to be dropped in, in the manuscript's own register.

### Sec. III.B, replacing the matched-cohort ratio

> Stage 2 groups the extracted exponents by sample form within each substructure
> and uses the median of each (substructure, sample form) cell. Comparing the two
> stages requires care. The Stage 1 error is computed across nine substructure
> families and the Stage 2 error across the five families that carry populated
> sample-form cells, so the ratio of 10.10 to 0.43 compares different cohorts.
> Restricting to the matched five-family cohort removes that particular defect
> but not the more serious one: in both comparisons the predictor for a family
> is built from a pool that contains that family's own fits, so neither figure
> is a statement about generalization.
>
> We therefore report the comparison under leave-one-substructure-out, in which
> the held-out family is withheld at every stage. On that protocol no reading of
> Stage 2 reaches a two-fold reduction on any cohort we can construct, the best
> being 1.77-fold. Stage 3, which reports a substructure-level central tendency
> with an explicit interquartile range, reaches 1.73-fold on means and 1.99 on
> medians across all families, and 2.32 and 2.23 once the cuprate families are
> removed. Its interquartile bound covers the residual in four of four families
> on the latter cohort. These are the figures we carry forward, and we no longer
> present a single fold-improvement headline. All are computed on betaH and
> inherit the field-scale qualification of Section III.F.

### Summary sentence, replacing the 16-fold line

> Substructure conditioning reduces field-exponent error about two-fold under
> leave-one-substructure-out validation, and the interquartile bound reported
> with it covers the residual in four of four families once the cuprate families
> are removed.

### Sec. III.C, replacing the 122 paragraph

> The 122-type family carries two compounds on this axis, Ba(FeAs)2 with 85 fits
> and K(FeAs)2 with 21. A leave-one-compound-out across two compounds measures
> how well each predicts the other rather than how well a family median
> generalizes, and we report it as that. MgB2-class materials cannot be assessed
> on this axis by leave-one-compound-out at all, because the 260-fit
> temperature-exponent cohort contains no MgB2 fits: the MgB2 literature in this
> corpus reports field sweeps at fixed temperature far more often than
> temperature sweeps at fixed field. The dispatch nevertheless emits
> temperature-dependent MgB2-class predictions, and we state where that exponent
> comes from rather than leaving it implicit. It is drawn from a separate
> per-paper Form 3 cohort of 15 MgB2 fits across 15 arXiv sources, spanning
> bulk, thin-film, wire and tape specimens, with a median betaT of 1.14; two of
> the fifteen are poorly constrained, one fitting with an rms of 6.3 in log10 Jc
> and one resting on three points. That cohort is large enough to supply a family
> median but too small and too concentrated in one compound to support a
> leave-one-compound-out test, which is why the MgB2-class temperature axis is
> dispatched but not validated, and why Table III records it as not assessable
> rather than as passing.

---

## Applied

`analysis/apply_manuscript_edits.py` applies all of the above to the two
documents. It works at run level, so the subscripts in betaT, Hc2 and log10 Jc
survive, and it refuses to write anything if any single edit fails to find its
target.

**44 edits, all applied.** Outputs are `HT10016_revised_corrected.docx` and
`SUPPLEMENTAL_MATERIAL_revised_corrected.docx`, with the inputs preserved
alongside as `..._asfound.docx`.

### Edits the first pass missed, found by sweeping the documents afterwards

The redline above was written from the passages I had read. Sweeping both
documents for every stale token found nine more, which is the same propagation
failure this deposit has had at every previous revision:

- the **abstract** and Sec. II.A each repeat the cohort size in prose (69 papers,
  43 compounds, 4387 points),
- **Table II** repeats the anchor count, the three variance ratios and every
  leave-one-out figure,
- Sec. III.D repeats the anchor count a third time,
- the archive size appears twice more in the main text,
- the Fig. 3 caption breaks the marker count down by family (13, 16, 15, which
  had to become 10, 16, 15),
- the supplement calls the anchor file "the 110-row file",
- and the conclusions repeat the 16-fold claim.

**One of those was a live contradiction rather than a stale number.** Sec. III.A
prints "for iron chalcogenide 11-type materials the ratio is 0.73" and Table II
prints "73%", while Figure 3, generated from the deposit, prints 0.77. The
deposited decomposition gives 0.7687. The text was wrong and the figure was
right.

### Supplement Table S1, rebuilt

The provenance table was static and still described a 69-paper cohort with
three families that no longer contribute. `analysis/rebuild_supplement_table_s1.py`
recomputes it from `provenance_table_fitcohort_full.csv`. Iron other,
Conventional A15 and Cuprate HBCCO leave the table, and the total becomes 64
papers, 39 compounds and 4211 points, matching Table I.

**One column needs your eye.** "Paper-reported Hc2" is recomputed as the count
of papers whose critical field carries a Tier 1 or Tier 2 provenance, which
gives 21 against the 37 the table printed. The original definition is not
recorded anywhere I could find, so if it meant something wider than Tier 1 and
Tier 2 the column needs redoing.

### Verification

`analysis/verify_deposit.py` now exits zero. Every count Table I prints is read
back out of the corrected document by `analysis/read_manuscript_counts.py` and
matches the deposit.

Two quantities the verifier checks are printed nowhere in either document,
"papers contributing anchor rows" and "physical samples". They are now labelled
as not printed rather than counted as agreeing.
