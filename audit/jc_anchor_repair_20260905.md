# The 96 Jc anchors repaired, and what happens to Fig. 3

Recorded 2026-09-05. Script `analysis/apply_jc_anchor_repairs.py`. Deposits
`data/phase_3_p31_jc_anchor_per_paper_repaired.csv`,
`audit/jc_anchor_repairs.csv`, `audit/variance_decomposition_repaired.csv`,
snapshot in `audit/pre_jc_anchor_repair_20260905/`.

This was the last unrepaired data layer. The table carries the anchors behind
Fig. 3, the sample-form variance decomposition, Table I row 8, and referee
concessions A4 and A6. The reading pass of 2026-09-04 graded every row and
`audit/what_this_costs_20260904.md` set out what to do with them. Nothing was
ever applied.

## The result, stated first

**The variance decomposition does not survive as a positive result.** After the
repair no family is evaluable at a useful resolution, two of them fall below
chance once the small-sample bias is removed, and the aggregate does not reach
significance under the null the deposit itself prefers.

| family | n | forms | eta2 | omega2 | p clustered | labellings |
|---|---:|---:|---:|---:|---:|---:|
| aggregate | 60 to 36 | 5 to 5 | 0.314 to 0.423 | 0.261 to 0.342 | 0.229 to **0.054** | many |
| conventional_AlB2 | 15 to 13 | 2 to 2 | 0.116 to 0.044 | 0.045 to **-0.039** | 0.667 to 1.000 | 3 |
| cuprate_BSCCO | 9 to 4 | 2 to 1 | 0.096 to none | -0.029 to none | 1.000 to none | 0 |
| cuprate_LSCO | 5 to 0 | 1 to 0 | never evaluable | | | |
| cuprate_RBCO | 3 to 3 | 1 to 1 | never evaluable | | | |
| iron_chalcogenide_11 | 12 to 5 | 3 to 2 | 0.374 to 0.809 | 0.219 to 0.701 | 0.515 to 0.249 | 4 |
| iron_pnictide_1111 | 6 to 6 | 3 to 3 | 0.143 to 0.143 | **-0.333** | 0.796 | 60 |
| iron_pnictide_122 | 10 to 5 | 3 to 2 | 0.488 to 0.374 | 0.318 to 0.137 | 0.288 to 0.303 | 10 |

Four things in that table matter more than the numbers.

**Omega squared goes negative for two families.** Eta squared is biased upward
and the bias grows as n falls, which is what the repair does everywhere. With
the leading bias term removed, `conventional_AlB2` is -0.039 and
`iron_pnictide_1111` is -0.333. Those are not weak positives. They are below
what the grouping produces by chance.

**The per-family p-values cannot go low.** The clustered null permutes one form
label per paper, so with few papers there are few labellings to draw. After the
repair `iron_chalcogenide_11` has four, `conventional_AlB2` three and
`iron_pnictide_122` ten, which put floors of 0.25, 0.33 and 0.10 under their
p-values. A family that cannot reach 0.05 has not failed a test; it was never
given one.

**The aggregate's rise is not attributable to the repair.** Removing the same
number of rows at random, as whole papers, 2000 draws, reaches the observed
0.423 in 23 percent of draws, with a median of 0.282 and a 5th to 95th range of
0.164 to 0.608. Removing a fifth of a cohort perturbs a variance ratio, and this
perturbation is inside what chance supplies.

**The ratio rises because the denominator collapses.** Between-form sums of
squares fall from 17.39 to 5.79 while within-form falls from 38.00 to 7.89.
Separation between sample forms gets smaller in absolute terms, not larger. A
rise in eta squared reported without that reads as the opposite of what
happened.

## What was applied

Kept 70 of 96. No row deleted; withdrawn rows keep their place and carry a
reason.

| action | rows | papers |
|---|---:|---|
| Jc times 10 | 4 | `jallcom.2013.04.183` |
| field divided by 10 | 11 | `physc.2009.05.098`, `s41598-025-24806-x` |
| withdrawn | 26 | nine papers, plus one row of a tenth |

The field repairs cannot move the decomposition. The statistic reads
`log10_Jc_anchor`, `sample_form`, `substructure` and `paper_id`; `H_anchor_T` is
on no path into it. That is a property of the code path, stated rather than
tested, because a check that re-applies the divisor and compares passes for any
divisor and any paper and is therefore not evidence. What is asserted instead is
that the linear and log Jc columns agree on every row, which a rescale that
touched one and not the other would break.

`audit/what_this_costs_20260904.md` says "96 now, 76 after repairs, 19
withdrawn". Its own per-family table on the same page sums to 77, and 96 minus
19 is 77, so the note is internally inconsistent and the 76 is the error.

## Three repair rules removed by review

The first version of this repair followed the 2026-09-04 list and rescaled
three papers it should have withdrawn. Each is contradicted by a file already in
this repository, and each contradiction is later and better evidenced than the
list. Finding them was an adversarial review, not this script.

| paper | was going to be | is | why |
|---|---|---|---|
| `jpcs.2026.113652` | Jc times 0.01 | withdrawn | `analysis/apply_unit_repairs.py` rejects it in its own words: the recorded values are not the printed ones in any unit, and the rescale on file is a guess. `audit/flagged_source_reading.csv` adds that the extracted Co0 panel does not exist in the source, whose panels are Co1, Co2 and Co3 |
| `physc.2010.05.048` | field over 10 | withdrawn | the same file rejects the field route explicitly: the axis is kilo-oersted but the shape is wrong too, so dividing the field by ten would leave a wrong curve |
| `physc.2009.11.051` | field over 10 | withdrawn | `audit/full_repo_sweep_20260903.md` plans it withdrawn and re-extracted, it is on the still-to-trace list, and its field-axis fits were withdrawn on 2026-09-05 because the paper has no critical-field figure at all |

**This changed the answer, and it changed which answer was wrong.** With
`jpcs.2026.113652` rescaled by the guessed factor, the aggregate came out at
0.4875 with p 0.011 and would have been reported as the decomposition becoming
significant. That entire result came from four rows of one flagged paper: the
guessed factor alone, with no withdrawal and no other repair, already gives
0.581 at p 0.004. At the A/m2 to A/cm2 factor the audit actually names it gives
0.409 at p 0.136. A p-value that is a property of the exponent chosen for one
untraced paper is not a p-value.

The three that survived tracing are kept for the same reason the others went.
`jallcom.2013.04.183` was read off the page independently and matches to under
two percent; `physc.2009.05.098`'s nine readings track the printed curves with
each series ending where its curve does; `s41598-025-24806-x`'s three Tc values
match its caption exactly.

## What this does to the referee concessions

**A4 and A6 lose their supporting figures.** Both rest on the decomposition
reading 0.116 for `conventional_AlB2` against 0.374 for `iron_chalcogenide_11`.
Those reproduce exactly from the deposited anchors, and the script requires them
before it changes anything. After repair they are 0.044 and 0.809, on 13 and 5
samples, with p floors of 0.33 and 0.25, and the first is negative once
corrected for bias. The physics positions in A4 and A6 stand. The numbers
offered for them do not.

## What the script does not do

It does not touch Fig. 3, `phase_3_p31_variance_decomposition.csv` or the p58
stability table. Those read the unsuffixed path and still carry deposited
values. Nothing consumes the repaired table yet, and that is deliberate until
the reporting decision is made.

The one row graded weak rather than defective, the `mtphys.2022.100783` single
crystal at 1.3 to 1.7 times off with a wrong tail, is kept. Dropping it moves the
aggregate from 0.423 to 0.427.

Two cohorts for this statistic exist in the repository and give different
answers: `permutation_test.py` gives `iron_chalcogenide_11` 0.374 and
`phase_3_p58_variance_stability.py` gives 0.403, because the MAGLAB records
encode the isotherm in `paper_id` and only one of the two strips it. The
response letter quotes 0.374, so this repairs that one. Any statement about the
family ordering has to name which cohort it is on, and the deposit's own
bootstrap already puts the probability that chalcogenide exceeds 122 at 0.48.
