# The 19 superseded values, traced to the deposit

Recorded 2026-09-04. `analysis/check_documents.py --docs <folder>` reports 19
values stated as current that it believes are superseded. This file traces each
one to the deposited table that decides it, rather than to the checker's
suggested replacement.

That distinction turned out to matter. `check_documents.py` is a denylist of
known-bad strings with hand-written replacements, and the replacements are not
recomputed from anything. Five of them are themselves stale, and two of the
flags are false positives that would have corrupted correct prose. Taking the
checker's word for all 19 would have introduced four new errors while fixing
fifteen.

An independent review of the first version of this ledger refuted two of its
conclusions. Both refutations are recorded below at the entries they overturn,
because the first version had them the other way round.

## Summary

Of the 19 as reported:

| verdict | count |
|---|---:|
| the document is stale, the checker's replacement is right | 8 |
| the document is stale, the checker's replacement is ALSO stale | 6 |
| the document is stale for a different reason than the checker gives | 2 |
| the document is stale but the correct value is not deposited anywhere | 1 |
| false positive, the prose is correct | 1 |
| **flagged** | **18** |

That is 18 and not 19 because two flags fire on the same manuscript sentence.

After this pass the checker reports **25**, not 17. One false positive was
removed and `MARKERS` was tightened, and the tightening surfaced eight
occurrences that had been exempted by grammar rather than by claim. See the last
section.

## Where the checker's own replacements are stale

Correct these in `SUPERSEDED` before using them, or the next reader repeats the
mistake:

| the checker says the value should be | the deposit says |
|---|---|
| 105 anchor records | 96 |
| 85 dispatched compounds | 84 |
| six cuprate papers are in the fitted cohort | five |
| 0.71, with 6 of 7 | 1.00, with 6 of 7 |
| 105 records are 69 samples | 96 records are 60 samples |

## The entries

### 1. "nine populated families" (manuscript)
Stale. `analysis/verify_deposit.py` computes seven: conventional_AlB2,
cuprate_BSCCO, cuprate_LSCO, cuprate_RBCO, iron_chalcogenide_11,
iron_pnictide_1111, iron_pnictide_122. The sentence is wrong twice over. It
names four cuprate substructures where the deposit has three, and it lists
"MgB2-class" and "one conventional family" as two entries when they are one
family, `conventional_AlB2`. The fitted cohort, a different population, has
eight; nine is wrong under either reading.

### 2, 3, 5, 9, 16. The anchor-count reduction, 26.8% (manuscript, supplement, letter)
Stale, and the error is the one the same section says it is correcting.
`python3 analysis/external_anchor_count.py`:

    K=1, all four            1.5918
    K=1, three monotonic     1.2668
    K=3, all four            0.9266
    K=3, three monotonic     0.6944

The matched three-compound pair is 1.267 to 0.694, a **45.2%** reduction. The
documents pair 1.267 with 0.927, which is the four-compound K=3 value, and get
26.8%. The manuscript labels 0.927 as the value "on the remaining three
monotonic cuprates", which it is not.

`analysis/manuscript_figure_4.py` computes the reduction on the matched pair and
annotates the deposited Figure 4 with "45.2% reduction on the matched cohort".
The printed caption says 26.8%. The figure and its own caption disagree.

### 4. "0.751, 0.929, 1.094 and 2.622" (manuscript) — NOT what it looked like
The first version of this ledger called these stale and proposed replacing them
with 0.753, 0.973, 1.093 and 2.571 from
`data/phase_3_p47_compound_leave_out_MAE.csv`. **That was wrong**, and applying
it would have destroyed the sentence.

The paragraph reads: "The same protocol on the field-axis cohort gives 0.753 for
MgB2-class, 0.973 for iron pnictide 122-type and 1.093 for iron chalcogenide
11-type, with iron pnictide 1111-type at 2.571. ... Repeating the field-axis test
with a substructure-median predictor, matching the temperature-axis protocol
exactly, gives 0.751, 0.929, 1.094 and 2.622." The p47 column is the first
sentence. The second is a different predictor, and the two are stated as a
contrast.

~~The real defect is that no deposited file reproduces 0.751, 0.929, 1.094 or
2.622.~~ **Retracted, see the section on the two remaining clusters below.** The
four reproduce exactly from the deposited tables, and
`analysis/verify_redline_numbers.py` was already asserting them when this was
written. The checker's `\b1\.094\b` pattern is a false positive as written and
is removed.

### 6. "leaving 123 compounds reported" (manuscript, Table IV caption)
Stale, and it exposes a stale deposited table.
`data/phase_3_p56_candidate_tier_assignment.csv` marks 123 compounds as
emitting, across three families.
`data/phase_3_p57_de_novo_predictions.csv` emits 84 compounds, all MgB2-class,
and the 84 are a strict subset of the 123. The tier table was last regenerated
at `0ee3a29`, before the field-window gate (`fbba543`, `8d43b4c`) and the
temperature-window gate (`cea6c85`) were applied to the prediction file.

Table IV's body is correct and carries 84. Only the caption carries 123, so the
table contradicts itself. `analysis/verify_deposit.py` now binds the two files
and fails until the tier table is regenerated.

### 7, 17. "only as an external validation set" (manuscript, letter)
Stale. `data/provenance_table_fitcohort_full.csv` has 62 papers, five of them
cuprate: cuprate_BSCCO 3, cuprate_LSCO 1, cuprate_RBCO 1. The checker says six;
the deposit says five.

### 8. "1.11, with 5 of 9" (supplement)
Stale, and the checker's replacement is stale too.
`phase_3_p39_multi_stage_predictor.stage1_loso_rank_order()` gives rank-position
errors 1, 1, 0, 0, 1, 3, 1 over seven held-outs: mean absolute error exactly
**1.00**, with **6 of 7** within one rank position. The checker's suggested 0.71
is the pre-classifier-fix value.

The bare figure 1.11 also appears in the manuscript, where the checker's pattern
does not reach it because the pattern requires ", with 5 of 9".

### 10. "a median factor of 5.1 across the 41 fits it affects" (supplement, and the manuscript and letter carry it too)
Stale; the checker's 6.7 across 38 fits is right. The affected subset is the fits
whose `Hc2_source` contains `extrapolated_to_low_T_anchor`, which is the case the
sentence describes: the resolution routine returning a series endpoint. That
subset is 38 fits with a median `Hc2_T_default / Hc2_T_used` of 6.667. No other
subset gives 41: direct matches are 43 at 7.14, the two together are 81 at 6.67,
and every fit where the two columns differ is 98 at 6.43. The 41 and the 5.109
reproduce exactly from the pre-2026-09-03 snapshots, so the sentence is a
correct statement about a superseded cohort.

### 11. "One row is one physical sample from one paper" (supplement)
Stale. `data/phase_3_p31_jc_anchor_per_paper.csv` holds 96 rows over 60 physical
samples. A row is one (paper, sample, isotherm temperature) record;
`aggregate_per_physical_sample` in `analysis/figure_4_source.py` strips a
`_<num>K` suffix from `sample_id` and `paper_id` before grouping, which is what
collapses 96 to 60. One specimen in `physc.2009.05.098` contributes nine rows
from 2 K to 40 K. The same paragraph then says the anchor is taken "at the lowest
temperature and field at which that sample was measured", which is false for
eight of those nine.

### 12. The Nb3Sn wire rows of Table S5 (supplement)
Stale, but not for the reason given. The checker says Table S5 no longer contains
them. It does contain them: the printed table's first row is
`S0011-2275(97)00151-3 / Nb3Sn`, span 0.791, exponent 1.12 (0.03), exactly as the
prose describes.

The defect is that the row should not be there. That identifier is in
`audit/withdrawn_records.csv`, and
`data/phase_3_form3_fits_partial_cohortB_v2.csv`, which Table S5 says it
excerpts, holds zero rows for it. Two other printed rows are withdrawn the same
way: `physc.2010.03.003 / FeTe0.61Se0.39` and `0921-4534(94)00021-2 /
HgVBaCaCuO`. `analysis/build_supplement_tables.py` prints "withdrawn identifiers
excluded from every table: 7" and regenerates a different Table S5; the printed
table predates it. Table S4 carries withdrawn rows the same way.

### 13. The Ba(Fe,Ru)2As2 row of Table S5 (supplement) — FALSE POSITIVE
The prose is correct. `data/phase_3_form3_fits_partial_cohortB_v2.csv` holds
exactly one Ba(Fe,Ru)2As2 row, from `phpro.2012.03.421`, with `Hc2_T_used` 15.3,
`Hc2_T_default` 60.0, normalised span 0.03268 and beta 19.0568. The printed table
row and the sentence describing it both reproduce it. The checker's entry tracks
the regenerated Table S5, which happens not to select this row, rather than the
file. Remove the pattern.

### 14. "the 2151-row candidate prediction file" (supplement)
Stale throughout the paragraph, not only in the flagged number.
`data/phase_3_p57_de_novo_predictions.csv` holds 2097 rows with 163 emitted
predictions and five refusal codes: `H_below_validated_reduced_field` 1054,
`Hc2_unavailable` 540, `T_above_Tc` 207, `T_above_validated_reduced_temperature`
93, `family_fails_field_axis_validation` 40. The paragraph says 2151 rows, 1386
emitted and 225 above the transition temperature, and names two of the five
codes. Only the 540 survives.

### 15. The 41.8% description (letter)
The letter describes the error as comparing a four-compound value against a
three-compound one. 41.8% is 1.592 to 0.927, both four-compound. The
mismatched pair is the 26.8%, which is 1.267 (three) against 0.927 (four). The
letter should carry the matched pair, 1.267 to 0.694, 45.2%.

### 18. "at least three anchor compounds are available within the family" (letter) — I RETRACT MY RETRACTION
The first version of this ledger called this a false positive, on the evidence
that the manuscript says the same thing in Sec. II.D and that commit `fbba543`
adopted the anchors-available reading. **Both halves of that were wrong.**

`8d43b4c`, ninety minutes after `fbba543`, reverted it: "predictor/constants.py
sets K_MIN = 1 and K_MAX = 5, validators.py enforces those against len(anchors),
and an Anchor in monotonic.py is one measured (T, H, log_Jc) triple for the
compound being predicted. K counts measured points supplied with a query. ... The
manuscript sentence was the defect; it is corrected in Sec. II.D and in the Fig.
4 caption."

`analysis/manuscript_figure_4.py` labels its axis "anchor measurements per
candidate, K", which is the same reading. So the checker's entry is the later
position and the correct one.

The manuscript sentence that `8d43b4c` says it corrected is still there,
unchanged. A commit message asserting a document edit is not evidence the edit
landed, and nothing in this deposit was checking.

### 19. "nine substructure families" (letter)
Stale, as entry 1. Seven.

## Found while tracing, outside the 19

- `analysis/phase_3_p39_multi_stage_predictor.py` was pushed with a
  `SyntaxError`. Commit `b17da65` replaced a block whose start fell inside the
  string literal `"max_chi_mean"` and whose end fell inside
  `"other_unclassified"`, leaving `DESCRIPTOR = "max_ch` on one side and
  `sified"` on the other. Nothing imports it among the four `check_*` scripts,
  so nothing noticed. `verify_deposit.py` now parses every deposited script.
- The corrected classifier had left `analysis/multi_stage_loso.py`'s mirrored
  copy behind. The mirror's own assertion caught it, on `Ba_Fe_Co_2As2`.
- `README.md`'s cohort table, headed "computed rather than quoted", is quoted
  and wrong on five of six rows: 37, 71, 107, 35 and 8 against the deposit's 32,
  60, 96, 32 and 7.
- Table S6 of the supplement prints refused predictions as delivered ones. Its
  `Co0.05Fe0.95Se` rows at 4.2 K show 5.996, 5.961 and 5.772 with the refusal
  column reading "none". In the deposit those three rows carry
  `predicted_log_Jc` of NaN with refusal flags
  `H_below_validated_reduced_field`, `H_below_validated_reduced_field` and
  `family_fails_field_axis_validation`; the printed numbers are the
  `withheld_log_Jc` column. 1187 refused rows carry a withheld value, so the
  paragraph's claim that a refused row carries "no value" is also wrong.
- The manuscript, supplement and letter disagree with each other in matched
  sentences about the field-scale audit: median ratio 0.86 against 0.80, 15 of
  77 against 15 of 94, 31 of 80 against 30 of 77.
- The supplement says the cuprates contribute seven distinct compounds to the
  fitted cohort; the provenance table and the supplement's own Table S1 give
  five.
- The supplement says 4 of 46 iron chalcogenide 11-type fits reach the ceiling;
  `audit/multi_stage_loso.csv` gives 51 fits for that family.
- Table S1's "Paper-reported Hc2" column follows
  `analysis/rebuild_supplement_table_s1.py`, which prints 22, rather than
  `analysis/build_supplement_tables.py`, which computes 13 from the same deposit
  because it excludes withdrawn papers. Two deposited generators, one printed
  column.
- `MARKERS` in `check_documents.py` contained bare `"was "` and `"were "`, which
  exempts any sentence in the past tense. That is why the 5.1 was reported in the
  supplement and not in the manuscript and letter, which also carry it.

## The exemption list was exempting grammar

`MARKERS` is the weaker of the two ways a sentence can name a superseded value
without failing; the stronger is to name the replacement alongside it. Six of
its phrases did not say anything about a past state of this work: `rather than`,
`against the`, `instead of`, `before`, `in place of`, and the bare `was ` and
`were `. They are gone.

What that hid:

- The manuscript's "The rank-position error remains 1.11, so Stage 1 serves as a
  rank-signal and classification step **rather than** a final predictor."
- The 5.1 field-scale factor in the manuscript and the letter, both in
  past-tense sentences.
- Three more occurrences of the nine-families count and one more of the
  anchor-count reduction.

The count therefore went from 17 to 25 with no new defect introduced. Eight of
the eight are the same defects already listed above, in copies that were not
being reported.

Four of the newly surfaced sentences are genuine retractions that name the wrong
value and explain why it is wrong without naming the right one, for example
"Comparing this against the four-compound one-anchor value of 1.592 gives a 41.8%
reduction, but that ratio compares different cohorts". Those clear the check by
naming the replacement in the same sentence, which the prose should be doing
anyway.


## What was applied

`analysis/apply_traced_value_edits.py` carries 29 edits into the three
artifacts and the letter's markdown copy. Every number it writes is recomputed
from the deposit at run time; it refuses to write if any find misses. The
checker goes from 25 to 1.

The one that remains is the Nb3Sn sentence, which needs Tables S4, S5 and S6
regenerated rather than reworded.

## What was deliberately not applied

Four clusters the deposit does not settle on its own.

1. ~~**The printed Tables S4, S5 and S6.**~~ **Done, see below.** S4 and S5 print rows from papers in
   `audit/withdrawn_records.csv` that the deposited files no longer hold. S6
   prints refused predictions as delivered ones, taking `withheld_log_Jc` and
   showing the refusal column as "none".
   `analysis/build_supplement_tables.py` regenerates all three from the current
   deposit and excludes the withdrawn identifiers, but its output differs from
   the printed tables in more than those rows, so swapping them is an editorial
   decision rather than a repair.

2. **0.751, 0.929, 1.094 and 2.622.** Nothing in this deposit reproduces the
   substructure-median field-axis run. Either the run is recovered and
   deposited, or the sentence goes.

3. **The field-scale audit numbers.** The three documents give three different
   readings of the same audit: median ratio 0.86 against 0.80, 15 of 77 against
   15 of 94, and 31 of 80 against 30 of 77. Which is right is not decidable
   from the fit table alone; the generator that produced them has to be
   identified first.

4. ~~**The calibration screen.**~~ **Done.**
   `analysis/repair_tier_table_emission.py` recomputes the six
   prediction-derived columns of `phase_3_p56_candidate_tier_assignment.csv`
   from the prediction file. `verify_deposit.py` passes.

Also outstanding, from the review and not from the checker: the supplement's
"seven distinct cuprate compounds" against the deposit's five, its "4 of 46"
iron chalcogenide fits against 51, and Table S1's "Paper-reported Hc2" column,
where two deposited generators give 22 and 13 from the same data.


## The printed tables, rebuilt

`analysis/apply_supplement_table_rebuild.py` replaces Tables S4, S5 and S6 with
the rows `analysis/build_supplement_tables.py` generates from the deposit, and
rewrites the prose that names rows. `check_documents.py` now reports no
superseded value stated as current, and all four checkers pass.

What came out:

- Three rows of Table S4, one from `physc.2010.03.003` and two from
  `S0011-2275(97)00151-3`, and three of Table S5, those two papers plus
  `0921-4534(94)00021-2`. All are in `audit/withdrawn_records.csv` and the
  deposited files hold no rows for any of them.
- The three `Co0.05Fe0.95Se` rows of Table S6 at 4.2 K, printed as delivered
  predictions with the refusal column reading "none". In the deposit those rows
  carry `predicted_log_Jc` of NaN with the flags
  `H_below_validated_reduced_field`, `H_below_validated_reduced_field` and
  `family_fails_field_axis_validation`; the printed numbers are
  `withheld_log_Jc`.

Two changes to the generator were needed first. `REFUSAL_PROSE` had no entry
for `T_above_validated_reduced_temperature`, so the newest refusal code printed
as a raw identifier. And Table S5's selection rule sorted the refused fits on
span alone, which picks the three cuprates at the regression ceiling and drops
the scale-resolution failure the prose is about. The rule now also keeps the fit
whose resolved scale sits furthest below its literature value. That is
`LaFeAsO`, 5.8 T resolved against 86 T in the literature, and not the
`Ba(Fe,Ru)2As2` the old prose named, which is a smaller shortfall.

## A correction to this ledger's own account of Table S6

The entry above first said the supplement's claim that a refused row carries
"no value" is wrong because 1187 refused rows carry a withheld value. That
reasoning was wrong: `withheld_log_Jc` is a separate column and those rows carry
no prediction.

The claim is still wrong, for a different reason. `Hc2_unavailable` refuses one
prediction target rather than a candidate, so a row refused on the field axis
can still carry the temperature-axis value the remaining gates allow, and 321 of
the 540 such rows do, in `predicted_log_Jc` itself. That is what the paragraph
now says.


## The tier table, repaired

Six columns of `data/phase_3_p56_candidate_tier_assignment.csv` are a function
of the prediction file and were all stale, not only the ones that decide who
emits: not one of the 84 compounds that still emit carried the right
`n_viable_predictions` either.

| quantity | before | after |
|---|---:|---:|
| emitting compounds | 123 | 84 |
| emitting records | 173 | 86 |
| viable predictions summed over records | 4104 | 175 |

The candidate set is not regenerated and does not need to be: the prediction
file still covers the same 183 compounds through the same 233 records, and the
script refuses to write if that stops being true. Regenerating it would need
`3DSC_MP.csv`, which is not in this deposit.

`tier` and `refusal_detail` are untouched. They come from the
calibration-domain screen, which is a transition-temperature rule against an
empirical floor and does not read the prediction file, so neither window gate
can have moved them. `analysis/calibration_domain_screen.py` confirms it: 233
records, 212 retained, 21 refused, 82 high confidence, 130 graded, all
unchanged and all matching the manuscript.

Two cross-checks that were not tautological and now pass. No
calibration-refused record is marked as emitting. And Table IV's body
reproduces from the repaired table exactly as printed: 49 / 29 / 0 for iron
chalcogenide 11-type, 79 / 51 / 0 for iron pnictide 122-type, 105 / 103 / 84
for MgB2-class, 233 / 183 / 84 in total.

Section III.E's "removes six predictions across two iron-chalcogenide
candidates" also holds. `Fe1Te1` and `Fe1Se0.05Te0.95` carry nine grid tuples
each; six of the eighteen carry a computed value the screen acts on, three per
compound, and the other twelve are refused for a target temperature above the
transition temperature with no value at all.


## The last two clusters

### The four that were called unreproducible: 0.751, 0.929, 1.094, 2.622

**This ledger was wrong about them, and the code that shows it was already in
the repository when the claim was written.**

They are the field-axis leave-one-compound-out error with sample-form
conditioning switched off, which is
`analysis/compound_leave_one_out.loo(frame, "beta", False)`. The conditioned
half of the same contrast, `loo(frame, "beta", True)`, is the deposited p47
column. Run today on the current deposit:

| substructure | conditioned | substructure median |
|---|---:|---:|
| conventional_AlB2 | 0.7532 | 0.7506 |
| iron_pnictide_122 | 0.9729 | 0.9295 |
| iron_chalcogenide_11 | 1.0935 | 1.0943 |
| iron_pnictide_1111 | 2.5713 | 2.6222 |

Rounded, that is the manuscript's 0.753, 0.973, 1.093, 2.571 and its 0.751,
0.929, 1.094, 2.622, all eight exact.
`analysis/verify_redline_numbers.py` lines 87 to 97 has asserted the pair since
`2d0fb33`, a day before this ledger claimed they had no source.

The real gap was narrower and is now closed. `run()` in
`compound_leave_one_out.py` called `loo` with `form_conditioned=True` hardcoded
on the field axis, so only the conditioned column was ever written to
`data/phase_3_p47_compound_leave_out_MAE.csv`. The unconditioned run existed as
a code path and an assertion and in no file, which is why it read as unsourced.
It is now two more columns in that CSV, `substructure_median_loo_mae` and
`substructure_median_loo_median_residual`, and all eight values are bound in
`analysis/check_claims_against_deposit.py`, which takes it from 62 bound
numbers to 70. The bindings were demonstrated to fire: changing 2.622 to 2.900
in the deposit makes the check report the disagreement.

A defect in the checker turned up while adding them. Its patterns capture with
`([\d.]+)`, which at the end of a sentence swallows the full stop, so a
document reading "2.571." disagreed with a deposit reading 2.571. The captured
token now has a trailing period stripped, which fixes every pattern rather than
the one that exposed it.

### The field-scale audit, three documents and three readings

The supplement's readings have a generator and the manuscript's have none.

`analysis/recompute_supplement_numbers.py` computes them, and its own docstring
says why it exists: "Both were static numbers with no generator, which is how
they came to describe a cohort that no longer exists." Its results were carried
into the documents by `analysis/apply_manuscript_edits.py`, but the two edits
sit in `SUPP_EDITS` with no counterpart in `MS_EDITS`. The supplement was
corrected and the manuscript and the letter were not. That is the whole
mechanism.

| quantity | manuscript and letter | supplement | recomputes here |
|---|---|---|---|
| median measured maximum over assigned scale | 0.86 | 0.80 | needs the extraction dataset |
| curves above 0.9 | 15 of 77 | 15 of 94 | needs the extraction dataset |
| three-family field-axis curves | 80 | 77 | **77** |
| irreversibility field or unlabelled | 31 of 80 | 30 of 77 | **30 of 77** |
| taking their scale from the eight audited papers | 54 of 80, 68% | 54 of 80, 68% | **56 of 77, 73%** |

The 80 is not recoverable. No deposited fit table produces it and neither does
any of the six pre-correction snapshots in `audit/`; every one gives 77 for the
three dispatched families. The manuscript and the letter now carry the
supplement's numbers.

One caveat is recorded rather than hidden. The exposure ratio needs the
per-point extraction dataset, which this deposit does not carry, so 0.80 and 15
of 94 cannot be recomputed here. Reconstructing that dataset from the per-paper
extraction files reproduces the median exactly at 0.800 and matches 90 of the
94 curves, giving 14 of 90; the four unmatched curves are the whole difference.
The irreversibility split does not depend on it and recomputes from deposited
tables alone.

The eight-paper count was wrong in both documents and is now recomputable.
`audit/dual_model_critical_field_agreement.csv` is deposited, sixteen papers
with a verdict each, and the eight that matter are the AGREE_NO_DATA rows where
both extraction models independently found the paper prints no critical field.
`recompute_supplement_numbers.py` joins it to the fit table under a rule stated
in the code, stripping the publisher prefix the fit table's `arxiv_id` carries
and the audit table does not. Seven of the eight contribute curves, 56 of 77,
73%. `physc.2011.05.018` contributes none.

`recompute_supplement_numbers.py` also no longer requires `--source`. The
classification and the eight-paper count read deposited tables only, and
demanding an argument nobody can supply made them unreachable.

## Still open, and not from the checker

`analysis/verify_redline_numbers.py` reports six numbers in
`audit/manuscript_redline_20260903.md` that no longer match the deposit: papers
62 against 64, compounds 38 against 39, extracted points 4146 against 4211,
anchors 96 against 103, Figure 3 records 56 against 59, and markers 37 against
41. The deposit and the manuscript agree on all six; it is the redline that
describes the superseded cohort. That is an internal audit note rather than a
submitted artifact, so it is recorded here rather than repaired.
