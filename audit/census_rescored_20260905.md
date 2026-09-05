# The census, re-scored against the repaired anchors

Recorded 2026-09-05. Script `analysis/score_field_axis_census_repaired.py`,
table `audit/field_axis_census_repaired.csv`.

The census asks whether the field axis reproduces its own printed figures better
than the temperature axis does. Its statistic is the per-fit
|ln(deposited beta / figure beta)|, with the same anchor, the same temperature
and the same window on both sides. The anchor is on both sides, so the anchor
repair required it to be re-scored.

## The awkward part, stated rather than avoided

The census set of four papers was fixed in
`audit/field_axis_census_preregistration_20260905.md` before any tracing began,
so that the comparison could not be run on a set chosen after the fact. **Two of
the four were then withdrawn from the cohort by the anchor repair**, because
neither `physc.2009.11.051` nor `physc.2010.05.048` prints a critical field of
any kind. Dropping them and re-scoring the remaining two is precisely the move
the pre-registration exists to forbid, so all three arms are reported.

| arm | set | anchors | field median | p |
|---|---|---|---:|---:|
| A | the pre-registered four | deposited | 0.821 | **0.395** |
| B | the pre-registered four | repaired | 0.821 | **0.312** |
| C | the two that survive | repaired | 0.333 | 0.086, **post hoc** |

The comparison arm is repaired too. `adjudicate_temperature_axis.py` reports the
temperature axis's ratio under the deposited Tc and under the Tc each paper
prints, and arm A uses the first while arms B and C use the second, so a
repaired field arm is never set against an unrepaired temperature arm.

## What actually moved

Almost nothing. **Only one of the four census papers has an anchor the repair
touched**, `physc.2013.04.060`, whose per-sample irreversibility fields came out
of its own Tables 1 and 2. Its score moves from 0.012 to 0.015.
`matchemphys.2023.128348`'s anchor was confirmed rather than changed, and the
two withdrawn papers keep their deposited anchors here, because withdrawing a
fit is not a correction to its anchor's value. Arm B is close to arm A by
construction, and p moves from 0.395 to 0.312 on that account alone.

**Arm C is where the number changes, and it is the arm that does not count.**
Removing the two worst-agreeing papers takes the field median from 0.821 to
0.333 and p from 0.312 to 0.086. That is what removing the two worst members of
a four-member set does. It is reported so the size of the selection effect is
visible, not because it is a result.

## The temperature arm barely moves either

Median |ln ratio| is 0.880 under the deposited Tc and 0.868 under the Tc each
paper prints. Correcting Tc does not make those extractions reproduce their
figures any better, because it changes both sides of the ratio together. That is
the same monotone compression recorded in
`audit/headline_recomputed_20260905.md`, seen from the other side: the repair
improves how the exponents separate substructure families and does nothing for
how well the extractions match their own curves.

## What the census still says

Unchanged, on the arm that was pre-registered: **the field axis is not shown to
reproduce its figures better than the temperature axis**, p = 0.395 as deposited
and 0.312 with both arms repaired. Neither is significant, and the direction is
the same either way.

The secondary statistic is also unchanged and still orders the four papers
exactly by extraction route: the one hand-digitised paper agrees with its trace
to 0.004 dex, and the vision-pass papers to 0.119, 0.393 and 0.566. Comparing a
hand digitisation with a pixel trace of the same figure is close to a
self-comparison, so that paper is not a control for the others, and none of the
vision-pass extractions has been shown to reproduce a figure.

## What this leaves

The census cannot be repaired into a stronger result, and it should not be. Two
of its four papers no longer exist in the cohort, which halves an already small
pre-registered set, and the honest report is the one above: the pre-registered
comparison, and a note that selection on the survivors would give p = 0.086.

If a field-axis census is wanted that carries weight, it has to be
pre-registered again on the cohort as it now stands, and it needs more than four
papers.
