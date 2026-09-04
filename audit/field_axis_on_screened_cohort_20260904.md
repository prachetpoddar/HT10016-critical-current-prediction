# What the field axis supports once the flagged scales are removed

Recorded 2026-09-04. `analysis/field_axis_on_screened_cohort.py`. Nothing is
changed; this establishes what is left.

## Repair does not rescue the flagged fits

Two of the seven flagged papers have a correct critical field recorded in their
own extraction file and simply do not use it. Substituting it:

| paper | scale used | scale recorded | reduced span | passes the 0.3 bound |
|---|---:|---:|---|---|
| `phpro.2015.06.160` | 9.0 T | 26 T | 0.778 to 0.269 | 6 of 6 to **0 of 6** |
| `s10854-026-16566-9` | 9.2 T | 78.1 T | 0.489 to 0.058 | 12 of 12 to **0 of 12** |

Correcting the scale upward moves those 18 fits from admitted to refused. That
is the applicability filter's selection effect running backwards, and it means
the question is not what the numbers become after repair but what the field axis
can support at all.

## The surviving cohort

Of the 94 field-axis fits that pass physicality, 34 survive the screen.

| family | as published | screened | of the survivors, unchecked |
|---|---|---|---|
| MgB2-class | 20 fits, 7 compounds | 14 fits, 7 compounds | 14 fits, 7 compounds |
| iron chalcogenide 11 | 21 fits, 3 compounds | **1 fit, 1 compound** | 1 fit |
| iron pnictide 1111 | 17 fits, 4 compounds | 17 fits, 4 compounds | 17 fits |
| iron pnictide 122 | 36 fits, 5 compounds | **2 fits, 2 compounds** | 2 fits |

Unflagged is not verified. Every surviving fit in the MgB2 class and in the
1111 family comes from a paper whose extraction file is not deposited, so it
could not be tested against its own measured field range and is reported
unchecked rather than clean.

## The four numbers the manuscript states

The published column reproduces the deposit exactly, which is what makes the
screened column comparable.

| family | published, conditioned | published, median | screened, conditioned | screened, median |
|---|---:|---:|---:|---:|
| MgB2-class | 0.7532 | 0.7506 | **0.8961** | **0.8839** |
| iron chalcogenide 11 | 1.0935 | 1.0943 | not testable | not testable |
| iron pnictide 1111 | 2.5713 | 2.6222 | 2.5713 | 2.6222 |
| iron pnictide 122 | 0.9729 | 0.9295 | 0.8348 | 0.8348 |

MgB2-class survives with all seven compounds and an error 19 per cent larger.
The 1111 family is untouched, because none of its fits is flagged. Iron
chalcogenide 11-type falls to a single compound, which leaves nothing to hold
out, so it has no field-axis validation at all. Iron pnictide 122-type keeps two
compounds and two fits, which is testable only in the arithmetic sense.

## What this means for the paper

Of the three families the dispatch routine addresses, only the MgB2 class
retains a field-axis validation worth the name, and it is the only family that
actually dispatches. That is the reason this is not fatal.

What does not survive is the claim that the field axis is validated across the
dispatched families. Two of the three lose it, one of them entirely.

## A mistake made and corrected in this file

The first version of this script passed `min_train_compounds=3` to the
leave-one-out, on the reading that the paper requires three anchor compounds
within a family, and reported iron chalcogenide 11-type as untestable even as
published. That is the family-size reading of K, and `8d43b4c` already reverted
it on the implementation: `K_MIN` and `K_MAX` bound `len(anchors)`, an anchor is
one measured triple, and Fig. 4 varies K from one to three while holding the
cuprate cohort at three compounds, which a family-size reading forbids. K counts
measured points supplied with a query. The published leave-one-compound-out
applies no compound gate, so neither does this, and the published column now
reproduces the deposit to four decimal places.

The only condition left is the method's own: leave-one-compound-out needs at
least two compounds to have anything to train on.
