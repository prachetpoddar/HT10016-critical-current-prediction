# The temperature-axis separation, attacked

Recorded 2026-09-06, before writing the family-conditional section. The section
was to rest on this result, so it was given to an independent reviewer first.
It did not survive in the form the manuscript states it, and the reasons were
already in this repository.

## What the manuscript says

Sec. III.C: the fraction of between-paper variance in the temperature exponent
that the family label accounts for is 0.524 with a permutation probability of
0.007 after the anchor repair, 0.436 at 0.016 before it on the matched
seventeen papers, and "this is the one result in the paper that improved under
every correction".

All of that arithmetic reproduces exactly. Three things around it do not hold.

## 1. The result is created by a deletion that selects on the outcome

Running the same statistic back through the cohort's own history:

| cohort | papers | families | eta squared | omega squared | p |
|---|---:|---:|---:|---:|---:|
| before the eleven withdrawals | 31 | 4 | 0.107 | 0.012 | **0.355** |
| after them, exponent as deposited | 19 | 3 | 0.409 | 0.360 | 0.012 |
| after the transition-temperature repair | 17 | 3 | 0.524 | 0.493 | 0.008 |

There is no separation at all before the withdrawals. Four fifths of the rise
is that one step, and `audit/beta_T_withdrawal_notes.md` section 2 already says
what is wrong with reading it as evidence, in this project's own words: "The
screen is not independent of beta_T, so the improvement is not evidence... It
does, in every family, and in opposite directions." Its own table gives the
withdrawn and retained medians: 3.809 against 0.886 for the chalcogenide
family, 0.190 against 2.346 for the 1111 family. The screen removed the high
tail of the family that ends up low and the low tail of the family that ends up
high. That note was written on 2026-09-03 and nothing since has connected it to
the headline separation.

## 2. The exponents behind it do not reproduce from their own figures, and the
   repository has already rebuilt them

`audit/temperature_axis_adjudicated_20260905.md` reports that all seventeen
traceable figures were pixel-traced and the exponents refit inside each
deposited row's own window with the same transition temperature on both sides:
fourteen scorable, **zero reproduce**, median ratio 0.42, range 0.09 to 1.00,
and the two nearest to unity are anti-ordered.

The rebuilt exponents are deposited at
`data/temperature_axis_rebuilt_from_figures.csv`, and no analysis in the
repository has ever run the headline statistic on them. Running it, unchanged:

| exponent set | papers | chalcogenide | 1111 | 122 | eta squared | p |
|---|---:|---:|---:|---:|---:|---:|
| deposited, repaired | 17 | 0.94 | 2.12 | 1.18 | 0.524 | 0.007 |
| rebuilt from the traces | 16 | 2.29 | 3.65 | 1.90 | 0.359 | 0.035 |
| rebuilt, measured grade only | 11 | 2.21 | 3.65 | 1.84 | 0.845 | 0.001 |

A family-level separation survives on both exponent sets, which matters. What
does not survive is anything said about which families separate. On the
deposited exponents the separating contrast is chalcogenide against 1111
(eta squared 0.735, p 0.005) and the pair involving 122 is unresolved. On the
rebuilt exponents that inverts: chalcogenide against 1111 gives 0.198 at p 0.24,
and the pair that separates is 1111 against 122 at p 0.010. The per-paper rank
correlation between the two exponent sets is 0.14.

## 3. "Improved under every correction" is false as printed

At the reproducibility step the probability moved the wrong way: 0.0117 on the
19 deposited papers against 0.0158 on the 17 matched papers before the anchor
repair. The eta squared rose and the probability rose with it. Both are printed
as the result, so the sentence is false on one of the two numbers it names.

Separately the anchor repair is itself family-differential, so the correction
that strengthens the separation is correlated with the label under test.

## 4. Two things the review could not break

The label does beat a compound-level null. Regrouping this cohort's eight
compounds into three labels with the real compound-count profile is
exhaustively enumerable at 280 partitions: the observed 0.524 sits against a
null median of 0.106 and a 95th percentile of 0.410, an exact probability of
2/280. Conditioning also on the paper counts leaves 30 partitions and gives
1/30. So this result is not in the same position as the within-cell scatter
finding, where the family label is indistinguishable from a random regrouping
of the same compounds. The two are different statistics against different
nulls and they do not stand or fall together.

Stability holds. Leave one paper out over all 17 gives eta squared between 0.455
and 0.625 with probabilities from 0.003 to 0.022, none crossing 0.05, and a
bootstrap over papers gives a 95 percent interval of 0.25 to 0.84.

## What this costs

The family-conditional section cannot be written on the per-family contrasts,
because they invert between two exponent sets that both sit in the deposit. The
family-level separation itself is defensible on either set and against a
compound-level null, but it cannot be called the result that improved under
every correction, and it cannot be reported without the pre-withdrawal value
beside it and without stating that the exponents do not reproduce from their
own figures.

The narrowest defensible claim is that the substructure label accounts for a
significant share of between-paper variance in the temperature exponent on both
the deposited and the figure-rebuilt exponents, at probabilities of 0.007 and
0.035, while the ordering of the families differs between them and no
per-family statement is supported.
