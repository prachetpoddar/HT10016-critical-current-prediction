# The field-axis census: not better than the temperature axis

Recorded 2026-09-05. The census pre-registered at `6b802ce` and amended at
`a955ba3` is complete. Four defects in my first report of it were found by
independent review; two were fatal and both had flattered the field axis. The
corrected result is below.

## What was wrong with the first report

**The significance came from a units mistake.** I compared a census statistic
computed in base-10 logs against a temperature-axis statistic computed in
natural logs. The factor ln(10) = 2.303 applied to one arm is exactly what moved
two census papers from above the temperature median to below it. In either base
consistently, p goes from 0.025 to **0.245**.

**The statistic reported was not the one pre-registered.** The pre-registration
fixes the primary statistic as the per-fit median of
|log(deposited beta_H / figure beta_H)|. What I reported was the median of
|log10(extracted Jc / figure Jc)| over data points, which never touches beta_H,
the quantity the manuscript actually deposits.

Two more, both real and both corrected in the specs: five legend swatches of
`physc.2013.04.060` Fig. 2 entered the data at 11.5 to 11.7 T, and `open_frame`
was set on that panel so the implied-span check was vacuous on two sides.

## The result on the pre-registered statistic

| | papers | median \|ln ratio\| |
|---|---:|---:|
| census, pre-registered, per paper | 4 | **0.821** |
| census, per fit | 27 fits | 0.765 |
| temperature axis | 14 | 0.880 |

Mann-Whitney, field closer to agreement: **p = 0.395**.

**The field axis is not shown to be better than the temperature axis.** On a set
chosen by nothing, its exponents sit about as far from their figures as the
temperature axis's do. Every bootstrap interval on the difference includes zero.

Per paper, on the pre-registered statistic: `physc.2013.04.060` 0.012,
`matchemphys.2023.128348` 0.650, `physc.2010.05.048` 0.992,
`physc.2009.11.051` 1.260.

## The finding that is worth more than the comparison

The secondary statistic, how well the extracted Jc matches the figure, orders
the four papers **exactly** as their extraction method does:

| paper | extraction method | median \|log10\| | points within 0.1 dex |
|---|---|---:|---|
| physc.2013.04.060 | user digitisation | 0.004 | 60 of 63 |
| matchemphys.2023.128348 | vision_pass | 0.119 | 9 of 20 |
| physc.2009.11.051 | vision_pass_round3 | 0.393 | 5 of 28 |
| physc.2010.05.048 | vision_pass_round3 | 0.566 | 1 of 52 |

I had presented the first row as the control the whole exercise was missing: an
independent trace reproducing an extraction to half a per cent, showing the
tracing pipeline is not what produces the disagreements elsewhere. **It is not a
control.** That extraction was made by hand from the same figures, so comparing
it with a pixel trace is close to comparing a trace with a trace. It is one of
only seven hand-digitised files in the corpus.

What the row does show is that a hand digitisation of these figures is
reproducible to half a per cent, which is a fact about the figures and about the
digitiser, not about the vision passes. **No vision-pass extraction anywhere in
this work has been shown to reproduce its figure.**

## Two unit findings, confirmed on the page

`physc.2009.11.051` Fig. 3 and `physc.2010.05.048` Fig. 3 both plot H in
kilo-oersted, and both extractions write those numbers into a `field_T` column.
The deposited fits did not correct it: `H_axis_range_normalized` = 0.5714 for
the 2 K fit of `physc.2010.05.048` reproduces exactly as (5 - 0)/3.5 with the
kilo-oersted numbers read as tesla. Sixteen passing fits across the two papers
therefore pass Eq. (1)'s field clause only because of the unit error. Corrected,
their spans fall by a factor of ten and none passes.

`matchemphys.2023.128348` Fig. 5 is labelled Jc (kA/cm2) but its tick values are
A/cm2. Two independent confirmations: the paper's four stated self-field values
match the printed decades to within 8 per cent, and the paper defines Hirr as
the field where Jc reaches 100 A/cm2 and gives 3.0 T at 20 K, which the trace
meets at 104 A/cm2 at 3.13 T. Read as kA/cm2 that point would lie a decade below
anything on the panel. The extraction read it correctly.

## Coverage, stated plainly

The census covers 28 of the 94 passing fits and 4 of the 16 passing papers. Of
the other twelve: six were traced because they were already suspected and cannot
be read as a rate; ten fits across five papers can never be checked because no
source figure for them exists in the corpus, including six under a DOI whose
filed PDF is a different paper; and one paper's extraction is not in the
extension directory at all.

Nothing here licenses a rate over the deposit. What it licenses is this: on the
only four papers that could be chosen without bias, the field-axis exponents are
about as far from their published figures as the temperature-axis exponents are,
and the one extraction that does reproduce its figure was made by a different
method from the rest.
