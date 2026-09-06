# Table II, rebuilt

Recorded 2026-09-06. Table II is the comparison that selects Form 3 for the
whole paper. Its generator was not in the deposit, its holdout was drawn point
by point inside a compound, its caption claimed the three forms shared a split
when none of them did, and the three forms were scored on different rows and on
different numbers of compounds. `analysis/functional_form_comparison.py`
rebuilds it. Two independent adversarial passes were run against that module;
both found material defects, and the conclusions below are what survived the
second.

## What is now in the deposit

`data/functional_form_input.csv`, the fitter's input reduced to the columns it
reads, value for value identical to the original in the same row order, and
`data/form3_per_compound_fits_as_published.csv`, the original's own per-compound
output. The module reproduces that table on all 23 fittable compounds to a
worst relative disagreement of 1.7e-8, with training and holdout sizes matching
exactly, before it reports anything. That pins the filters, the skip rule and
the position of Form 3 in the random stream.

The two constants the original imports from a package that is not in the
repository were recovered rather than guessed: alpha = 0.047 and the Form 1
field floor 1e-6, the only value among the decades at which Form 1 returns the
published median 0.597 and mean 0.672 together. An earlier stub guessed 1e-3
and returned 0.603, which is why an earlier pass called Form 1 unreproducible.
That claim is withdrawn: all three of Table II's numbers reproduce. Note the
limit of this: two constants were recovered against two published aggregates,
so Form 1's agreement is a fit, not an independent reproduction. Form 3's is
independent.

## What the comparison shows

Every construction below runs on the rows all three forms keep, with one split
drawn once and handed to all three, so a difference between two numbers is a
difference between two functional forms. A single split is a coin toss at these
sample sizes, and an independent review found the ordering changing on a third
of draws, so nothing rests on one split: each compound is scored over twenty
seeds and the comparison is the direction of the paired difference across
compounds.

Post-withdrawal cohort, well-conditioned compounds, exponent bound 50:

| split | Form 1 | Form 2 | Form 3 | n | 3 over 2 | 3 over 1 |
|---|---:|---:|---:|---:|---|---|
| point | 0.508 | 0.513 | 0.484 | 15 | 11/15, p 0.118 | 14/15, p 0.001 |
| curve | 0.537 | 0.544 | 0.493 | 13 | 9/13, p 0.267 | 11/13, p 0.022 |
| source | 0.936 | 0.971 | 1.102 | 7 | 4/7, p 1.000 | 5/7, p 0.453 |

Three things follow, and they hold at exponent bounds of 10, 50 and 200 and on
the cohort as published as well as after the withdrawals.

**Form 3 is distinguishable from Form 1 and is the better form.** Eleven to
sixteen compounds of thirteen to seventeen, at probabilities between 0.000 and
0.039 under both point and curve holdouts.

**Form 3 is not distinguishable from Form 2.** The paired sign test never
reaches 0.05 under any construction, bound or cohort except one corner
(bound 200, point split, p 0.049). Table II prints 0.352 against 0.260, a
margin of 0.092 dex. On the compounds all three forms can score, that published
margin is 0.012. Under a shared split on shared rows the two forms are within
0.03 dex of each other and the sign of the difference moves with the seed.

So the empirical basis Sec. II.C cites for adopting Form 3 over Form 2 is not
there. The basis over Form 1 is. The reason to prefer Form 3 is that it fits
independent temperature and field exponents against a temperature-independent
field scale, which is what the rest of the paper needs, and that should be
said instead of a margin that does not survive.

**Nothing generalizes to an unseen source.** Under a source-paper holdout every
form's median error sits between 0.90 and 1.10 dex, against 0.48 to 0.54 under
a point split. That is a factor of eight to thirteen in critical current. It is
computed on seven or eight compounds and the median is set by two of them, so
it is a direction rather than a measurement, but the direction is the paper's
own conclusion about cross-source heterogeneity arriving from a different route.

## Two compounds that should not be in the comparison at all

The conditioning diagnostic flags four compounds whose fitted field exponent
runs away. Two of them are extraction defects, not fits:

- **HfRe2**, source `2205.06500v1.pdf`, carries 128 rows whose field runs from
  1e-6 to 1e-5 T against a literature critical field of 10 T, so the largest
  reduced field in the compound is 1e-6. The published Table II fit gives it a
  Form 3 field exponent of 2.87e6 and a Form 2 exponent of 4.8e5.
- **Fe9Se8**, source `1108.0407v1.pdf`, carries 88 rows from 0 to 0.005 T
  against a critical field of 8 T. Form 3 exponent 3408, Form 2 exponent 514.

This is the same signature the withdrawal ledger cites when it withdraws
`1612.02839v1`: "over fields of 1e-6 to 1e-4 T, which are the log-axis minor
ticks with the decade shifted". Neither paper is in the ledger. HfRe2 appears in
no current cohort, so it affects Table II only. Fe9Se8 carries 11 rows of the
current repaired temperature-axis cohort and has been reextracted.

## The curve unit, stated as the limitation it is

`(source, compound_raw, temperature)` is the finest holdout unit the deposited
corpus supports, and it is not reliably a curve. `compound_raw` is the figure
legend string, which for most groups restates the temperature rather than
naming the sample, and where it does name a sample it varies in format within
one source. Of the held-out rows under this key, 283 of 1098 share an exact
source, temperature and field coordinate with a training row; twenty-nine of
those agree in critical current to 1e-9, which is duplicated extraction of one
measurement rather than two samples on a shared field grid. The source-level
holdout has no such ambiguity, which is part of why it is reported beside the
curve level rather than instead of it.
