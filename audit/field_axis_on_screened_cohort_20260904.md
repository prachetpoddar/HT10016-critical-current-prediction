# What the field axis supports once the flagged scales are removed

Recorded 2026-09-04. **Rewritten the same day.** The first version of this file
was computed from a screen whose two main tests were wrong, and its conclusion
was wrong with them. What it said, and what is actually the case:

| | first version | corrected |
|---|---|---|
| flagged papers | 7 | **3** |
| flagged fits, of 94 passing | 60 | **36** |
| MgB2-class fits flagged | 20 of 20 | **0 of 20** |
| families losing their field-axis validation | 2 of 3 | **none** |

The first version concluded that of the three dispatched families only the MgB2
class kept a field-axis validation worth the name. That was an artefact. The
MgB2 class is untouched, and removing the three genuinely defective papers
improves the other two families rather than destroying them.

## The corrected cohort

Of the 94 field-axis fits that pass physicality, 58 remain.

| family | as published | screened |
|---|---|---|
| MgB2-class | 20 fits, 7 compounds | 20 fits, 7 compounds |
| iron chalcogenide 11 | 21 fits, 3 compounds | 13 fits, 2 compounds |
| iron pnictide 1111 | 17 fits, 4 compounds | 17 fits, 4 compounds |
| iron pnictide 122 | 36 fits, 5 compounds | 8 fits, 3 compounds |

Every family still has enough compounds to hold one out.

## The four numbers the manuscript states

The published column reproduces the deposit exactly, which is what makes the
screened column comparable.

| family | published, conditioned | published, median | screened, conditioned | screened, median |
|---|---:|---:|---:|---:|
| MgB2-class | 0.7532 | 0.7506 | 0.7532 | 0.7506 |
| iron chalcogenide 11 | 1.0935 | 1.0943 | **0.6276** | **0.6276** |
| iron pnictide 1111 | 2.5713 | 2.6222 | 2.5713 | 2.6222 |
| iron pnictide 122 | 0.9729 | 0.9295 | **0.5083** | **0.4093** |

Two families are untouched and the other two get better. Removing the three
defective papers does not weaken the field-axis result; it strengthens the two
families that contained them, which is what one would expect if those papers
were adding noise rather than signal.

That cuts both ways, and the caution belongs here rather than in a footnote:
iron pnictide 122-type falls from five compounds to three and iron chalcogenide
11-type from three to two, so the improved errors rest on less evidence. A
smaller cohort with a smaller error is not automatically a better result.

## Repair versus removal, which is unchanged

Two papers in the first version's flag list record a correct critical field in
their own extraction file and do not use it, and substituting it refuses their
fits: `phpro.2015.06.160` at 26 T instead of 9 T drops its reduced span from
0.778 to 0.269, and `s10854-026-16566-9` at 78.1 T instead of 9.2 T from 0.489
to 0.058, so all 18 fail the 0.3 bound. That arithmetic is right, but it is no
longer a finding about those papers, because both of those larger values are
zero-temperature extrapolations and the scales in use are legitimate. It is
kept here only as the reason that substituting a bigger Hc2 is not a free fix
in general.

## What this does not decide

Thirty-six of the 94 passing field-axis fits come from three papers with a
demonstrably wrong critical-field scale, and two of those three have separate
defects found by reading the source: `physc.2009.11.051`'s field axis is in
kilo-oersted and `mtphys.2022.100783`'s polycrystal record is a copy of its
single crystal. Whether to withdraw them is still a decision, and the numbers
above say what it costs: nothing in two families, and a smaller but better
cohort in the other two.
