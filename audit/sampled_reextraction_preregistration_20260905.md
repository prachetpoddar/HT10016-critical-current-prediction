# Pre-registration: does re-extracting by hand change the fitted exponents?

Written before the refits below were run.

## The question

Stage C established that hand digitisation reproduces the published figures and
the vision passes do not, on twelve papers with a pixel trace. It did not ask
what that costs the manuscript, because it measured extracted Jc values, not the
fitted exponent the deposit carries.

This asks the next question directly: **if every vision-pass extraction were
replaced by a careful reading of the same figure, how much would beta_H move,
and would the fits still pass Eq. (1)?**

A pixel trace stands in for a hand re-extraction. Stage C measured the two
against each other on three papers and found them 0.003 to 0.023 dex apart, so
the substitution is defensible, and it is the only version of the experiment
that can be run without weeks of manual work.

## The sample, fixed now

Every vision-pass paper that has a pixel trace of its own figure and at least one
passing field-axis fit. That is a census of what can be tested, not a draw:

| paper | route | passing fits |
|---|---|---:|
| matchemphys.2023.128348 | vision_pass | 4 |
| matpr.2019.05.078 | vision_pass | 2 |
| phpro.2015.06.160 | vision_pass | 6 |
| mtphys.2022.100783 | vision_pass | 20 |
| s10854-026-16566-9 | vision_pass | 12 |
| physc.2009.11.051 | vision_pass_round3 | 8 |
| physc.2010.05.048 | vision_pass_round3 | 8 |

Seven papers, 60 of the 94 passing fits. All seven will be reported, including
the two that stage C could not score.

## What will be measured, fixed now

For each passing fit, beta_H is refit from the traced figure at the same
temperature, for the same sample, under the same Hc2, over points with H strictly
below Hc2. Three numbers per fit:

1. **How far the exponent moves**, as |ln(refit / deposited)|.
2. **Whether the fit still passes Eq. (1)'s field clause**, recomputing
   (Hmax - Hmin)/Hc2 from the traced points that survive the H < Hc2 filter,
   with the field unit corrected where a figure is in kilo-oersted.
3. **Whether the refit rests on enough points**, at least four below Hc2.

The headline is the count of passing fits that survive re-extraction unchanged,
survive with a materially different exponent, or stop passing at all.

## What this cannot settle, stated now

A pixel trace is not a hand re-extraction by the author. It fixes reading
fidelity and nothing else. The two hand-digitisation failures already on file in
this corpus, `physc.2009.05.098` writing a kilo-oersted axis into a tesla column
and `jallcom.2023.170146` filed under a DOI whose PDF is a different paper, are
both unit and provenance errors that this experiment cannot produce and cannot
detect. A real hand pass would have to guard against those separately.

Committed before the refits.
