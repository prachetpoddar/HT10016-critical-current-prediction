# Cross-table checks on the upper critical field, which had none

`verify_deposit.py` checked that one physical sample carries one sample form
across every table, and that the Jc anchor's two columns agree. It contained
**zero** occurrences of Hc2. The critical field is the other quantity carried in
more than one deposited table and the one the whole field-axis result depends
on, and nothing compared its values between tables.

`analysis/audit_hc2_tables.py` adds six checks, and `verify_deposit.py` now runs
it.

## A check that fired and was wrong

The first version required the anchor table's `Hc2_T` to equal the provenance
table's `Hc2_anchor_T` everywhere, by analogy with the sample-form check. It
reported 37 disagreements.

Checking those rows before reporting them showed the check was wrong, not the
data. **Every disagreeing row carries a Tier 1 or Tier 2 provenance**, and the
two columns hold different quantities in that case: the anchor table keeps the
reference value for the compound, the provenance table keeps the value resolved
from the paper. For MgB2 in `jallcom.2023.170146` that is 15.5 T against 5.0 T,
and the 5.0 T is the point of a Tier-1 resolution.

The invariant that survives is: **the two agree wherever the provenance is a
literature catalog value or a Tier-3 default, and may differ only where it is
Tier 1 or Tier 2.** That holds on 74 of 75 joined rows.

## What the corrected checks find

**One defect I introduced today, now fixed.** Moving the six PrFeAsO0.6F0.12
fits onto the paper's own irreversibility line updated the fit table and left
the provenance table saying `Tier_3_literature_default` at 120 T. That is the
half-applied correction `apply_table_corrections_20260903.py` exists to prevent,
and it was caught only because this check was written. The provenance row now
reads 24.4013 T with `Tier_1_paper_Hirr_at_7.0K_arXiv_1002.0208_Eq5`, matching
the scale at the paper's lowest fitted isotherm, which is how the other Tier-1
rows are written.

**Three inconsistencies across two papers, predating today, unresolved.**

| paper | quantity | anchor table | provenance table |
|---|---|---|---|
| 10.1016/j.physc.2014.03.020 | Hc2 | 50 T | 60 T |
| 10.1016/j.physc.2014.03.020 | Tc | 22.0 K | 20.0 K |
| 10.1016/j.physc.2009.03.028 | Tc | 12.0 K | 22.0 K |

The Hc2 pair is a plain contradiction: the provenance is
`Tier_3_literature_default` on both sides, so the same literature default is
recorded as two different numbers, and the fit uses 60.

Neither can be settled from the deposit. `physc.2014.03.020` names 25 K in the
one place its text gives a transition temperature, and that is in a sentence
about a cited material rather than its own sample. `physc.2009.03.028` reports
Tc as a function of doping from about 9 K to 22.8 K, so 12.0 and 22.0 could each
be a real value for a different composition, and which one belongs to the
extracted curve is a question for the figure.

Both need a reading of the source paper. Until then `verify_deposit.py` reports
this line as failed, which is the correct state: the deposit contradicts itself
in two places and nobody had looked.

## The four checks that pass

- A Tier-3 fit uses the literature default: all 71 agree.
- The provenance tier matches the fit table's tier, per paper.
- The provenance anchor is a value the fits actually use.
- Every Hc2 in five deposited tables is positive and below 250 T.
- No withdrawn record still carries an Hc2 in the fit or provenance tables.
