# Analysis choices the documents do not state

Recorded 2026-09-06, after the reduced-variable scaling work showed that the
13.0 percent figure moves between 9 and 46 percent on a convention the paper
never defines. The question asked was whether that is an isolated case. It is
not.

An independent sweep of every reported result produced thirteen findings. Four
are verified here against the deposit; the rest are recorded as reported and
are marked as not yet independently checked.

## Verified

### The 30 percent adoption threshold is defined against a 1.47 percent benchmark

Sec. III.D: "Both fall below the 30% adoption threshold, which marks the level
at which a universal law would substantially exceed the gain observed from
family-conditional aggregation." The next sentence gives that gain: median
holdout error 0.604 dex against 0.613 dex, "a gain of 0.009 dex that is below
bootstrap precision". Nine thousandths of 0.613 is **1.47 percent**.

So the threshold is set twenty times higher than the quantity its own sentence
defines it against, and nothing in the repository derives it: 30 appears only
as a literal in figure code. At any bar below 13.0 percent the headline
negative result reverses, and the pooled summary that
`audit/headline_numbers_recheck.md` recommends, 6.78 percent, still clears a
bar derived the way the sentence describes.

This is the single most exposed number in the paper. It is load-bearing for the
abstract, Sec. III.D, Table III row 1 and the conclusion, and it is the only
place where an adoption decision is made against a threshold with no stated
construction.

### A predictor with no family label clears the same bar on all three families

Sec. III.C reports compound leave-one-out errors of 0.546, 0.580 and 0.513 on
the repaired 257-fit cohort and concludes that all three fall below the
screening-grade threshold of 1, supporting Table III's claim that applicability
is family dependent.

Replacing the family median with a single global median over all families and
scoring the same folds:

| family | family-conditional | global median | ratio |
|---|---:|---:|---:|
| iron chalcogenide 11 | 0.546 | 0.559 | 0.98 |
| iron pnictide 1111 | 0.513 | 0.786 | 0.65 |
| iron pnictide 122 | 0.580 | 0.529 | **1.09** |

All three clear the bar of 1 with no family label at all, and on the 122 family
the family-conditional predictor is worse than the family-agnostic one. The
threshold test does not distinguish the two predictors, so it cannot carry the
claim that applicability is family dependent. The threshold of 1 is itself a
constant in `analysis/compound_leave_one_out.py` with no derivation in either
document, and the pipeline's own screening-grade constant is a different one.

### The dispatch file emits values for 144 compounds in two families

The abstract, Sec. III.E, Table IV and the conclusion all say 84 compounds
receive a prediction, all MgB2-class. The deposited file carries a
`predicted_log_Jc` on 484 rows covering **144 compounds, 102 MgB2-class and 42
iron pnictide 122-type**. The 84 is the count with an empty refusal code.

Both readings are live and the supplement states the mechanism, but Table IV
prints "0" dispatched for the 122 family beside 240 rows of that family that
carry an emitted value, and the paper never gives the 144.

### Supplement Sec. 12 reports on a cohort that no longer exists

It states results "at the reference point T = 4.2 K and H = 1 T" for "53
non-refused candidates" of the 11-type and "37" of the 122-type. In the
deposited file there are **zero** non-refused rows at 1 T, **zero** non-refused
chalcogenide rows and **zero** non-refused 122-type rows. Every 1 T target is
refused for lying below the validated reduced field, which Sec. III.E states.
The section's conclusion, that the committed-scope predictions are retained as
the headline values, rests on it.

## Reported by the sweep, not yet independently verified

Recorded so they are not lost. Each needs the same treatment as the four above
before it is acted on.

1. **The 0.29 dex propagated uncertainty** is computed on the iron pnictide
   122 scope, which dispatches nothing. On the MgB2 class, the only family that
   dispatches, the same propagation is reported to give 0.49 dex at 4.2 K and
   0.58 at 20 K. The evaluation anchor, 22 K and 50 T, is a hard-coded modal
   pair rather than a property of the candidate cohort, and the stated
   direction of the correlation caveat is reported to be sign-wrong: with both
   partial derivatives negative, a positive correlation reduces the propagated
   variance, making 0.29 an upper bound rather than the lower bound the text
   claims.
2. **Stage 3's 0.84** is reported to be a resubstitution figure from the same
   generator whose Stage 1 and Stage 2 numbers Sec. III.A withdraws, and to be
   9.01 under genuine leave-one-substructure-out on the matched seven-family
   cohort. The same Table III cell is reported to mix three cohorts.
3. **The 52-fit field cohort** is 63 in the deposit; the difference is a
   T/Tc < 0.7 clause applied to the field axis in audit code and stated in
   neither document, along with a retention floor of 0.05 and a three-point
   minimum that appear nowhere.
4. **The exposure ratio 0.88** is reported to divide by the unrepaired anchor
   while the cohort is the repaired one, and the three internally consistent
   readings all give 0.836, reversing the sentence's conclusion that exposure
   rises.
5. **Fig. 5's 0.31 dex band** is reported to span 0.20 to 0.355 across
   populations, and to be an MgB2-only statistic drawn identically around two
   families that dispatch nothing.
6. **Table II**, the functional-form comparison that selects the model for the
   whole paper, is reported to have no source in the deposit, and its split is
   reported to be point-level within a compound, which is the leakage Sec. II.D
   criticises.
7. **The K-anchor validation** is reported to compare two nearly disjoint
   held-out point sets in different interpolation regimes, with the reduction
   moving between 37.5 and 47.9 percent depending on which compound is called
   non-monotonic.
8. **The regime cut points** 0.3 and 0.7 are hard-coded and printed nowhere,
   and applying the bias correction the paper invokes for MgB2 to every family
   is reported to move both iron families across the lower cut.
9. **The 15 MgB2 temperature fits** are described as having one fit resting on
   three points and one with an rms of 6.3; the file is reported to have six
   fits on three points and a maximum rms of 0.474.

## What survives every construction tried

The temperature-axis conditioning result. Recomputed with means instead of
medians, with the two-paper family filter relaxed, bias-corrected, and at fit
level rather than paper level, it stays between 0.40 and 0.56 with a
permutation probability at or below 0.011. Table I's counts are exact. The
field-axis "no verdict" conclusion is insensitive to the 52 against 63 cohort
choice.
