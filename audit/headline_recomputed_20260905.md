# Does the exponent separate substructure families?

Recorded 2026-09-05. Script `analysis/headline_on_repaired_cohort.py`, table
`audit/headline_on_repaired_cohort.csv`.

The manuscript separates substructure families by their fitted exponent. This
recomputes that on the cohorts that survive the anchor repair and the stated
protocol, against the deposited cohorts, on the papers each pair shares.

## The statistic, and what it replaces

Papers are the unit of analysis, so each paper contributes one median exponent
per family. The statistic is eta squared, the fraction of between-paper variance
in the exponent that the family label accounts for, with a p from twenty
thousand shuffles of the family label across papers.

The first version of this compared a between-family difference of medians
against the largest between-paper standard deviation inside one family. An
independent review broke it three ways and all three are corrected here.

- **The cohorts were not the same cohort.** The repaired temperature table drops
  two papers whose fit rule was never reproduced, for reasons unrelated to Tc,
  and both are single-fit chalcogenide papers carrying a full paper's weight. On
  the matched intersection the deposited axis already cleared the bar, so the
  flip I reported was cohort composition. Every comparison below is matched.
- **A range over group medians and the standard deviation of one group are not
  comparable.** They differ in units of dispersion, in how they grow with the
  number of groups, and in sample size. That line is retired.
- **The bootstrap was upward biased by an amount that differed between the two
  cohorts**, so most of the apparent tightening of its interval was differential
  bias. It is replaced by the permutation test.

## The result

| cohort | papers | eta squared | permutation p |
|---|---:|---:|---:|
| field axis, deposited passing | 16 | 0.055 | 0.93 |
| field axis, admitted under the protocol | 12 | 0.038 | 0.98 |
| temperature axis, deposited | 19 | 0.409 | **0.012** |
| temperature axis, repaired Tc | 17 | 0.524 | **0.007** |

Matched, on the papers each pair shares:

| | papers | before | after |
|---|---:|---|---|
| temperature axis, Tc repair | 17 | eta 0.436, p 0.016 | **eta 0.524, p 0.007** |
| field axis, repair and protocol | 12 | eta 0.031, p 0.988 | eta 0.038, p 0.978 |

**The field axis does not separate substructure families, before or after.** Its
eta squared is 0.03 to 0.06, and the observed value is lower than most random
relabellings of the family across papers. Whatever the field-axis exponents
carry, it is not the substructure.

**The temperature axis does separate them, and the repair strengthens it.**
Matched on the same seventeen papers, correcting the Tc anchors takes eta
squared from 0.436 to 0.524 and p from 0.016 to 0.007. It was already
significant before the repair, so this is a strengthening rather than a rescue,
and the earlier claim that the between-family signal did not beat the
within-family scatter is withdrawn: it was an artefact of comparing a range with
a standard deviation.

## What the repair does to the exponents

The mechanism I gave first was wrong. I said the deposited Tc was a constant per
family, so every paper inside a family was forced to the same wrong value and
the resulting errors appeared as within-family scatter. The anchor is a constant
per **compound**, not per family, and in `iron_pnictide_1111`, the family that
carries most of the change, the four papers carried three different Tc values:
55.0, 51.0 and 28.0.

What actually happens is a monotone compression. Lowering Tc toward the data
lengthens the lever of log(1 - T/Tc), which shrinks the exponent, and the size
of the shrink tracks the size of the Tc correction: the rank correlation between
the fractional change in Tc and the change in the exponent is 0.83 across the
eighteen papers. The three papers whose Tc was cut hardest move most,
`2305.10034` from 6.15 to 2.13, `2308.10492` from 4.53 to 1.69 and
`2510.10264` from 3.26 to 2.11. The exponent range narrows from 0.163 to 6.200
down to 0.262 to 3.699, and the median from 1.46 to 1.27.

That compression is why the between-family difference in exponent units also
falls, from 1.78 to 1.18, while the scale-free statistic rises. Reporting the
difference alone would have made the repair look like a loss; reporting eta
squared alone would hide that every exponent moved. Both are in the table.

## The census

`analysis/score_field_axis_census.py` is unchanged by any of this: it compares
how well each axis reproduces its own printed figures, not exponents, and its
pre-registered statistic still gives p = 0.395, the field axis not
distinguishable from the temperature axis. Its secondary statistic still orders
the four census papers exactly by extraction route, with the single
hand-digitised paper agreeing to 0.004 dex and the vision-pass papers at 0.119
to 0.566. It has not been re-run against the repaired anchors, and it should be
before anything is reported from it.

## Guards

Four, all firing: the permutation test separates a planted family effect from
noise, where the noise arm is the median over twenty null draws rather than one,
because a single random table of twelve papers reaches eta squared near 0.5 often
enough that testing one measures the draw; eta squared is near one on the planted
effect; both statistics are unchanged by a tenfold rescale of every exponent; and
the matching helper actually restricts to shared papers. The family join now
refuses to guess: an unresolved or ambiguous key raises, and on the temperature
axis the regex join is checked against the deposit's own substructure column.

## What this means for the manuscript

The substructure claim, as far as this evidence goes, is a temperature-axis
result. It survives the anchor repair and is slightly stronger after it. The
field-axis cohort, which is where the anchor problems were worst and where the
cohort fell from 94 fits to 52, contributes nothing to it.
