# The Tc every temperature-axis fit uses is not paper-reported

Recorded 2026-09-05, as stage B of the recovery. Written after an independent
review corrected four of the readings below and forced three of the caveats.

## The finding

`data/provenance_table_fitcohort_full.csv` records `Tc_provenance` as
"paper-reported (v3.2.1 / Cohort A vision pass)" for all 31 Cohort A rows.
Within Cohort A the value is a strict function of the idealised parent-compound
string, which `analysis/tc_anchor_audit.py` now asserts rather than claims:

| compound string | rows | Tc carried |
|---|---:|---:|
| Ba(FeAs)2 | 10 | 38.0 K |
| Fe2TeSe | 5 | 14.5 K |
| Sm2FeAs2O | 2 | 55.0 K |
| Pr2FeAs2O | 2 | 51.0 K |

All 14 distinct compound strings carry exactly one Tc each. The ten Ba(FeAs)2
rows are Rb-substituted, Co-doped, P-doped, Ni-doped and K-doped samples whose
measured Tc runs from 19 K to 40 K. Across all 62 rows there is one
counterexample, so the claim is made for Cohort A only.

## Against the papers

Seventeen of the eighteen arXiv papers state a Tc for the sample whose figure
was extracted. `1009.4896v1` does not; the only temperatures in it are
measurement temperatures.

**Wrong by 5 K or more, six papers.**

| paper | deposited | the paper's own sample | error |
|---|---:|---:|---:|
| 2510.10264v1 | 51.0 | 25.1 K, underdoped PrFeAs(O,F) | +25.9 |
| 2308.10492v1 | 38.0 | 19.3 K, BaFe1.908Ni0.092As2 | +18.7 |
| 0903.0004v2 | 38.0 | 22.6 K, Rb-substituted BaFe2As2 | +15.4 |
| 2305.10034v1 | 28.0 | 13.3 K, La0.87Sm0.13FeAs0.91P0.09O | +14.7 |
| 0906.0444v1 | 38.0 | 24.0 K, Ba(Fe0.93Co0.07)2As2 | +14.0 |
| 1502.05345v1 | 38.0 | 30.7 K, P-doped BaFe2As2 film | +7.3 |

All six are overestimates. Five more are wrong by less than 5 K. Six are
differences of convention: the paper reports several Tc for the same sample
(onset, midpoint, zero resistance) and the deposited value sits within a kelvin
of one of them, so those are not errors and are not counted as such.

The weakest of the six is `2308.10492v1`, whose sentence carries a citation.
The other five are unambiguous statements about the authors' own samples.

`analysis/audit_cohort_anchors.py` already tested a weaker version of this: it
flags a row when the anchor appears nowhere in the paper's text. That test
catches none of the six, because in each case the wrong number happens to appear
somewhere on the page.

## What correcting the anchor does

beta_T is refit from the same extraction rows with only Tc changed, over 246
fits and 17 papers. One row is excluded because its deposited beta_T does not
reproduce under its own Tc (`1502.05345v1` at 34 T, already on file).

| paper | fits | deposited | corrected | shift |
|---|---:|---:|---:|---:|
| 2305.10034v1 | 13 | 6.151 | 2.126 | 0.35 |
| 2308.10492v1 | 16 | 4.529 | 1.686 | 0.37 |
| 2510.10264v1 | 13 | 3.262 | 0.937 | 0.29 |
| 1502.05345v1 | 17 | 2.904 | 1.781 | 0.61 |
| 0906.0444v1 | 11 | 2.500 | 1.035 | 0.41 |
| 0903.0004v2 | 15 | 1.580 | 0.800 | 0.51 |
| 1108.0407v1 | 11 | 0.483 | 0.681 | 1.41 |
| 1111.3923v1 | 9 | 0.337 | 0.490 | 1.46 |

The three largest deposited exponents in the whole cohort belong to the three
papers with the largest Tc errors. They were large because Tc was too high.

## Three caveats the review forced, which belong in any use of this

**The 246 fits are not 246 independent measurements.** Each paper's isotherms
are near-parallel translations of one another, so the shift is very close to a
Tc-only rescaling: the ratio correlates at 0.99982 with a geometric factor
computed from the temperatures and the two Tc values alone, using no Jc value at
all. The independent units are the 17 papers.

**The size of the collapse depends on which statistic is quoted.**

| statistic | deposited | corrected | factor |
|---|---:|---:|---:|
| max/min, per-paper medians | 18.83 | 5.74 | 3.28 |
| max/min, per-fit values | 38.04 | 16.10 | 2.36 |
| sd of log10, per-paper medians | 0.35 | 0.20 | 1.73 |
| Q3/Q1, per-fit values | 2.78 | 2.03 | 1.37 |
| Q3/Q1, per-paper medians | 2.46 | 1.87 | 1.32 |

Report it as 1.3 to 3.3 depending on the statistic, never as 3.3 alone. Across
substructures the median exponent separation goes from 2.90 to 1.63.

**A wrong Tc does not produce the collapse.** Drawing a random Tc for each paper
from its family's plausible range, floored above that paper's own highest fitted
temperature, over 400 draws: the observed corrected spread of 5.74 sits against
a null median of 27.4 with a 5th percentile of 9.85, p < 0.005 on max/min and on
the standard deviation of the log. The deposited Tc set is statistically
indistinguishable from a random draw. This is the check that makes the collapse
mean something, and it did not exist until the review asked for it.

## What this does and does not bear on

It bears on Referee A's first concession, the deposit the referee was invited to
check: a provenance column says paper-reported and is not. It bears on the
substructure separation in the temperature-axis exponents, a large part of which
is the anchor rather than the physics.

It says nothing about whether the Jc series are readings of the published
figures. `audit/anchored_vs_generated_20260905.md` stands, including its
instruction that no global claim about the temperature axis should be made in
either direction until the fifteen untraced figures are traced.
