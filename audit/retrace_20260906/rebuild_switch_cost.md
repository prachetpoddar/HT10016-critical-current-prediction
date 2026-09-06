# What switching to the figure-rebuilt exponents costs

Recorded 2026-09-06, before making the switch. The rebuild is
`data/temperature_axis_rebuilt_from_figures.csv`, produced by refitting the
temperature exponent from a pixel trace of each source figure.

The control first: recomputing the published compound leave-one-out errors on
the deposited cohort with an independent implementation returns 0.546, 0.513
and 0.580, which are the printed values to three digits. So the comparison
below is like for like.

## Coverage

The rebuild is a subset of the same sources, not a different corpus. It covers
16 of the 18 papers in the deposited cohort and adds none. The two it misses
are `0907.0147v2`, whose recorded fields match no axis on its page, and
`1009.4896v1`. The iron pnictide 111-type family, one paper and eleven fits,
disappears with them.

## Side by side

| | deposited, repaired | rebuilt, all grades | rebuilt, measured grade |
|---|---:|---:|---:|
| fits | 257 | 160 | 110 |
| papers | 18 | 16 | 11 |
| compounds | 9 | 8 | 6 |
| median exponent | 1.285 | 2.576 | 2.025 |
| family separation, eta squared | 0.524 | 0.359 | 0.845 |
| permutation p | 0.007 | 0.035 | 0.001 |
| chalcogenide median | 0.82 | 2.91 | 2.08 |
| 1111 median | 2.12 | 4.11 | 3.63 |
| 122 median | 1.43 | 1.87 | 1.80 |
| compound LOO, chalcogenide | **0.546** | **1.435** | 0.944 |
| compound LOO, 1111 | **0.513** | **2.415** | not scorable |
| compound LOO, 122 | **0.580** | **1.184** | 0.965 |
| sd of the exponent, 122 scope | 0.563 | 1.174 | 1.074 |

## The consequence, stated plainly

The family separation survives on every version, at 0.035 on the full rebuild
and 0.001 on the measured-grade subset. That is the result Sec. III.C leans on
and it holds.

The applicability claim does not. Sec. III.C reports that all three assessable
families fall below the screening-grade threshold of 1 on the temperature axis,
at 0.546, 0.580 and 0.513. On the full rebuild every one of them is above it,
at 1.435, 1.184 and 2.415. That reverses the paper's one positive applicability
result. On the measured-grade subset two of the three clear the threshold, at
0.944 and 0.965, and the third cannot be scored because the 1111 family holds
too few compounds once the extrapolated and thin fits are dropped.

The median exponent doubles, from 1.285 to 2.576, which moves Figure 5's
temperature curves for two of three families, the propagated uncertainty on the
122 scope from 0.563 to 1.174 in the exponent, and every place the paper quotes
a family median.

## What this means for the choice

Making the rebuild primary is defensible and is what the adjudication points
at: none of the deposited exponents reproduces from its own figure, median
ratio 0.42 over fourteen scorable papers. But it is not a clean substitution.
Taken at all grades it converts a positive applicability result into a negative
one. Taken at measured grade only it keeps the positive result on two families
and drops the third, on eleven papers and six compounds, and the grade filter
is itself a selection that would have to be pre-registered rather than chosen
after seeing which side of the threshold it lands on.
