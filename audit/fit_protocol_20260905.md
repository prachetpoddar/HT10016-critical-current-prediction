# The fitting protocol, stated

Recorded 2026-09-05. Module `analysis/fit_protocol.py`, table
`audit/fit_protocol_applied.csv`. Run `--selftest` for the guards and
`--report` for what each decision costs.

Three things about the protocol were undocumented or inconsistent, and new data
pushed through the old code would inherit all three. Each is now a decision,
stated once and implemented once. An independent review broke the third and
corrected the first; both are recorded below as they now stand.

## Decision 1: retention

    keep a point when  1 - H/Hc2 >= 0.05

The old rule, `H < Hc2`, puts no floor on the reduced field, so a point
arbitrarily close to the anchor takes unbounded leverage over the slope.
`1002.0208v2` retains one at 1 - H/Hc2 = 0.0011, whose abscissa is -2.96 while
the rest of that isotherm sits near -0.3.

**The floor is a choice, not a measurement.** The first version of this argued
for it twice from the same fact: that four fits of `jallcom.2023.170146` behave
as though a floor near 0.05 were already applied, and that every paper's closest
retained point sits at 0.057 or above. Both come from the 0.95 reconstruction
factor in `apply_anchor_repairs.py`, which is 1 minus the floor. Under the old
rule as stated, that paper's closest retained point is at 0.015, not 0.057, and
sweeping the factor bounds the implied floor only to 0.0475 to 0.055, from those
same four fits.

Measured against the old rule as stated, the floor drops **20 points across 15
fits in 4 papers and moves the exponent by up to 0.835**. It does not cure the
case it was written for: `1002.0208v2`'s exponents run 0.068 to 1.015 with it
and 0.099 to 1.015 without, and all six are admitted either way. It bounds the
leverage; it does not make those fits good.

## Decision 2: the temperature clause applies to both cohorts

    a fit is inside the window when  T/Tc < 0.7

The manuscript states this as part of the applicability window. It was imposed
on the temperature axis and not on the field axis at all. It now applies to
both, and it costs **13 of the 70 surviving field-axis fits**.

The clause acts differently on the two axes and that is not an inconsistency.
On the temperature axis T is the swept variable, so the clause cuts the fit
window and the fit survives with fewer points. On the field axis T is frozen, so
the clause discards the whole fit. Same clause, different variable.

One claim from the first version is withdrawn. It said the retention floor is
not binding on the temperature axis because every Cohort A fit has
1 - T/Tc >= 0.306. That is entailed by the clause itself and carries no
information, and it is also wrong at the third figure: the minimum is 0.3056,
across the eleven fits of `1009.4896v1`.

## Decision 3: the field clause stays, and is stated for what it is

    the clause          (Hmax - Hmin)/Hc2 > 0.3, on the retained points
    reported beside it  the lever, the span of log10(1 - H/Hc2)

The first version replaced the clause with a minimum lever, on the argument that
the lever cannot be satisfied by shrinking the anchor alone. **That argument is
wrong.** The floor pins the smallest retained reduced field at 0.05, so
shrinking the anchor until a data point lands just inside the floor maximises
the lever, and it is the same move that maximises the ratio. On this cohort
every one of the ten fits that fall short of the lever clears it on unchanged
data at a smaller anchor.

There is no anchor-independent criterion to be had. The abscissa of the fit is
log(1 - H/Hc2), so every property of the fit is a property of the anchor. The
only repair is to make the anchor trustworthy, which is what the anchor repair
does, and then to say plainly what the clause is: a statement that the measured
field span is a large fraction of the recorded critical field, informative
exactly to the extent that the recorded critical field is right.

The two criteria on this cohort:

| | fails the lever | has the lever |
|---|---:|---:|
| **fails the clause** | 7 | 0 |
| **clears the clause** | 3 | 60 |

Neither contains the other in general. A fit spanning 0.5 T on a 10 T anchor has
the lever and fails the clause; the module's self-test plants that case.

## What the protocol admits

| | fits | papers |
|---|---:|---:|
| deposited passing | 94 | 16 |
| after the anchor repair withdrew three papers | 70 | 13 |
| **admitted under the stated protocol** | **52** | **12** |

The 18 refused: 7 fail the field clause, 11 sit outside the temperature window.
Seven of the eighteen also fall short of the lever, and so do three of the
fifty-two admitted.

Admitted exponents: median **1.459**, range 0.068 to 10.693. Both endpoints are
already on file as problems, the low one `1002.0208v2` and the high one
`jallcom.2023.170384`.

## Sensitivity, which is not good

The cohort is not stable against the thresholds.

- Moving the lever threshold from log10(2) = 0.301 to 0.32, six per cent, would
  drop eight fits and move the median exponent from 1.4 to 0.8. Twelve fits of
  `s10854-026-16566-9` sit in a spike at 0.316. The lever is reported and not
  gated partly for this reason.
- `MIN_PTS` at 6 instead of 3 would take the cohort to about half.
- The temperature clause between 0.51 and 0.749 moves the cohort from 37 to 54.

None of these is a defect in the code. They are a statement about a cohort of
fifty-odd fits over twelve papers, which is small enough that any threshold near
the middle of the distribution moves the answer.

## Guards

Eight, all firing, covering: the floor is inclusive at its boundary and drops
what is inside it; the floor bounds the lever; the ratio is passed by shrinking
the anchor on unchanged data; the lever is passed by the same shrink; neither
criterion contains the other; the temperature clause is one function; a planted
exponent comes back exactly; and a two-point fit is refused.

Two mechanical defects the review found are fixed: `H_FLOOR` was bound at
definition time so a caller sweeping it silently got the shipped value, and the
report re-cut the retained set at the repaired anchor, which credited four
`phpro.2015.06.160` fits with clearing a bound the anchor repair records them as
failing.

## Still open

Nothing downstream calls this module yet. Which protocol the manuscript reports,
and therefore which cohort, is a decision rather than a repair.
