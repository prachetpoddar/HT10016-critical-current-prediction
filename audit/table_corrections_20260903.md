# Three table corrections applied, and the numbers the manuscript now needs

`analysis/apply_table_corrections_20260903.py`, idempotent, backs up to
`audit/pre_table_corrections_20260903/` and never overwrites that backup.

## 1. `10.1038/s41467-025-55880-4` withdrawn

The source is a superconducting-diode-effect study on BSCCO flakes whose text
contains zero occurrences of "A/cm" and zero of "current density"; its currents
are Ic in microamps and its field sweep reaches 25 mT. Evidence in
`audit/withdraw_s41467_field_axis.md`.

Removed: 6 field-axis fits, **all six at the exponent ceiling**; 2 anchor rows,
one of them sample "s2" which is not a device in the paper; 1 provenance row;
36 source curve points.

## 2. One paper was being counted as two

`1002.0208v2` (temperature axis, 17 fits) and
`10.1016/j.physc.2011.02.004` (field axis, 6 fits) are the same paper, Physica C
471 (2011) 215. A `paper_key` column now carries `1002.0208v2.pdf` on both, so a
paper-clustered leave-one-out or permutation test groups them. Neither record was
deleted, because both hold real measurements. Mapping in
`audit/duplicate_papers.csv`.

Any paper-clustered statistic run before this change treated one paper as two.

## 3. PrFeAsO0.6F0.12 moved onto the paper's own irreversibility line

`analysis/refit_physc_2011_02_004.py` refits the six isotherms against
Hirr(T) = 31.9 T (1 - T/Tc)^1.7, which the paper states, instead of the 120 T
literature default, and **records the residual, which the first version of this
refit did not**.

The paper does not print the Tc used in that expression. The deposited source
rows say 51.0 K, the earlier refit implies 45.0 K, and the paper's own text gives
a diamagnetic onset of about 48 K. All three were run. 48 K is adopted, as the
only one with a source in the paper, and the spread is the honest uncertainty:

| T (K) | beta at Tc=45 | at Tc=48 | at Tc=51 |
|---|---|---|---|
| 7 | 0.98 | 1.02 | 1.04 |
| 15 | 0.22 | 0.25 | 0.27 |
| 25 | 0.04 | 0.10 | 0.18 |
| 30 | 0.23 | 0.34 | 0.64 |

The exponent is insensitive to Tc at low temperature and varies by a factor of
about three at 30 K. That has to be carried as an uncertainty, not hidden.

**The refit is better conditioned, not a better fit.** This is the check the
earlier version omitted, and it does not go the flattering way:

| T (K) | rms, Tier 3 | rms, Tier 1 |
|---|---|---|
| 7 | 0.178 | 0.184 |
| 10 | 0.163 | 0.165 |
| 15 | 0.149 | 0.148 |
| 20 | 0.125 | 0.103 |
| 25 | 0.157 | 0.137 |
| 30 | 0.167 | 0.176 |

The residual is essentially unchanged. What changes is the window, 0.07-0.12 to
0.60-0.999, so all six cross the pre-registered applicability gate, and the
exponent, from a median of 6.2 to 0.22. The claim to make is that the Tier-3
exponents were an artefact of a critical scale an order of magnitude too large,
not that the data fit Form 3 better.

## The field axis, before and after

| tier | n before | n after | median beta before | after | at ceiling before | after | passing before | after |
|---|---|---|---|---|---|---|---|---|
| Tier 1 | 83 | 89 | 1.47 | 1.40 | 0 | 0 | 76 | 82 |
| Tier 2 | 9 | 9 | 2.22 | 2.22 | 0 | 0 | 4 | 4 |
| Tier 3 | 83 | 71 | 24.20 | 24.05 | 34 | 28 | 8 | 8 |

## The variance decomposition moved, and stayed in its band

Recomputed from the corrected anchor table through
`analysis/figure_4_source.py`:

| | before | after |
|---|---|---|
| physical samples | 69 | 67 |
| aggregate eta^2 | 0.340884 | 0.347291 |
| cuprate_BSCCO eta^2 | 0.062039 | 0.096426 |

Both stay inside their pre-registered bands, aggregate in B (0.3 to 0.7) and
BSCCO in C (below 0.3). No family changed regime.

## What the manuscript must now say

`analysis/verify_deposit.py` passes every internal-consistency check and fails
only where the manuscript has not caught up. The deposit's values are:

| Table I quantity | manuscript | deposit |
|---|---|---|
| papers contributing anchor rows | 35 | **34** |
| physical samples | 69 | **67** |
| anchor rows | 105 | **103** |
| papers contributing fitted curves | 65 | **64** |
| distinct compounds with fitted curves | 40 | **39** |
| critical-current data points extracted | 4247 | **4211** |
| temperature-axis partial fits | 414 | **260** |
| field-axis partial fits passing physicality | 88 | **94** |
| field-axis papers passing | 15 | **16** |

The field axis is the only one of these that moved upward, and it did so because
six fits crossed the applicability gate once their critical scale came from the
paper rather than from a default.

## Still open

The exponent ceiling still holds 28 Tier-3 fits, and 63 of the 71 remaining
Tier-3 fits still fail the applicability gate. Only two of the thirteen Tier-3
papers have a critical scale that can be read from them at all
(`10.1016/j.cjph.2024.09.042` Fig. 10 and `1611.08455v1` Fig. 5a, the latter
printing Hirr(0)(1-T/Tc)^n with n = 2 on the figure). Whether the rest can be
repaired or must be withdrawn is unresolved.
