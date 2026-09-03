# The headline numbers, re-derived on the current cohort

Three numbers carry the paper's claims. They were checked before drafting any
manuscript edit, because two of the three turn out not to need editing and the
third needs more than editing.

## 1. Universality, 13.0 per cent on the standard-deviation scale

**Unaffected by anything in this audit.** The claim is computed from
`data/reduced_variable_scaling.csv`, and that file has one version in the
repository's history. No withdrawal has ever touched it, so the number cannot
have drifted.

The protocol is recoverable: one minus the median within-bin standard deviation
over the global standard deviation, which is how the original component-E run
reported it (it gave 13.8 per cent before the August correction to 13.0). On the
deposited file that gives **13.43 per cent, and 25.06 per cent on the variance
scale**, against 13.0 and 24.3 printed.

The residual 0.4 point gap is a deposit problem rather than a result problem.
The global standard deviation needs the raw points, and the deposit contains
only the binned summary, so a reader cannot reproduce the printed figure
exactly. Referee A asked four separate times to see the data behind a claim.
Depositing the per-point table behind this bin summary would close that.

## 2. The 16-fold conditioning improvement

**This one does not survive, and the manuscript and the response letter both
still state it.**

`analysis/multi_stage_loso.py`, rerun on the current cohort, withholds the
held-out family at every stage rather than letting a family's own fits into its
own prediction. Across the readings of Stage 2 it can construct:

| cohort | best Stage 2 reading | fold improvement on Stage 1 |
|---|---|---|
| all families with a descriptor | nearest_no_form | 1.77 |
| cuprates removed | nearest_no_form | 1.77 |

Stage 3 reaches 1.73-fold on means and 1.99 on medians on the full cohort, 2.32
and 2.23 with cuprates removed. **No reading of Stage 2, on any cohort, reaches
even a two-fold improvement.** The manuscript states sixteen, at Sec. III.B and
again in the summary, and the response to Referee A9 defends it.

The 23-fold figure was already withdrawn and replaced by 16-fold. The 16-fold
has the same defect: it compares a held-out family against a predictor that saw
that family's own fits.

## 3. Where the extreme errors come from, which is Referee A9's question

A9 asks whether the ten-orders error is "driven largely by the cuprate fits that
stem from crude model". It is, and it is now traceable to individual papers. All
28 remaining fits at the exponent ceiling of 30 come from seven papers, and
every one is a Tier-3 fit whose critical field is a literature default:

| compound | source | fits at the ceiling |
|---|---|---|
| Bi2Sr2-xNixCa2Cu3O | 10.1016/j.jallcom.2013.04.183 | 8 |
| Bi1.6Pb0.4Sr2Ca2Cu3O10 | 10.1016/j.jpcs.2026.113652 | 6 |
| Bi2Sr2CaCu2O8 | 10.1038/s41598-025-95932-9 | 6 |
| YBaCuO | 10.1016/0921-4534(96)00225-0 | 3 |
| FeSeTe | 10.1016/j.cjph.2024.09.042 | 3 |
| SmFeAsO0.8F0.2 | 10.1016/j.physc.2009.05.098 | 1 |
| FeSe0.5Te0.5 | 10.1088/0953-2048/29/3/035013 | 1 |

23 of the 28 are cuprate. Five of the seven papers have a Jc figure whose page
is now known, so they can be re-measured; two cannot, one being archived as a
first page only and one absent from the archive.

This converts A9 from a criticism into a result. The referee's diagnosis was
correct, the mechanism is a critical scale an order of magnitude too large
rather than the functional form alone, and the affected records can be named.

## What this means for the drafting order

Table I and the derived prose are mechanical once the field-axis applicability
question is settled. The 16-fold claim is not mechanical: it needs either a
genuine leave-one-substructure-out number in its place, or the conditioning
claim restated at the scope the validation actually supports.
