# The temperature axis, recomputed from the figures

Recorded 2026-09-05. The earlier notes established that the deposited beta_T
values do not reproduce their own published figures. This one replaces them.
`analysis/rebuild_temperature_axis.py` builds the axis from two inputs and
nothing else: a pixel trace of each published figure, and the Tc that paper
reports for the sample the figure shows.

Ten defects found by independent review were fixed before this was written, and
one of them changed a physical input: `1611.08455v1` is now anchored at 13.7 K,
the AC-susceptibility onset the paper states for both its crystals, rather than
the 16 K resistive onset. Fig. 5(b) takes its jc from the width of the
magnetisation loop, so the magnetic onset is the matching convention. That one
correction moves the paper's exponent from 6.93 to 4.96.

## The table

`data/temperature_axis_rebuilt_from_figures.csv`. 160 fits over 16 papers.
`0907.0147v2` has no usable trace and `1009.4896v1` states no Tc for its sample.

The independent unit is the **paper, not the fit**. The ten fits per paper are
one curve family re-evaluated at ten fields, so nothing here should be quoted
with n = 160.

| | |
|---|---|
| Tc | the paper's own, for the sample the figure shows |
| Jc | read off the figure by the digitiser |
| field grid | ten fields across the span every contributing isotherm covers |
| window | Eq. (1)'s T/Tc < 0.7, applied per point before the fit |

The window is not a formality. It removes at least one isotherm in eleven of the
sixteen papers, and it lowers the exponent in eight of those eleven. The deposit
never bound on it because its inflated Tc made every window look cool: the
largest deposited coverage was T_max/Tc = 0.694.

## The finding that matters most

**beta_T is not constant within a paper.** Across the ten fields, low field
first:

```
1111.3923v1     1.62  1.73  1.80  1.84  1.90  2.05  2.38  3.08  4.49  8.86
1502.05345v1    1.68  1.65  1.67  1.73  1.70  1.84  2.09  2.62  3.56  8.12
2510.10264v1    3.13  3.21  3.21  3.13  2.87  2.70  2.98  4.11  6.68 10.40
2305.10034v1    1.74  1.94  2.13  2.32  2.51  2.71  2.93  3.93  5.33  8.18
1903.00866v2    1.35  1.44  1.49  1.41  1.25  1.04  0.76  0.46  0.15 -0.13
```

The exponent rises from the lowest field to the highest in **13 of 16** papers,
and in `1903.00866v2` it changes sign, meaning Jc rising with temperature. The
median within-paper standard deviation of beta_T is **0.85**, against a median
95% half-width from the fits' own residuals of **0.32**. The real variation is
close to three times the quoted uncertainty, and it is systematic in field, not
noise.

This is physically unsurprising. Approaching the irreversibility field, Jc
collapses steeply with temperature and any single power in (1 - T/Tc) has to
steepen with it. But it means the manuscript's form, one beta_T per sample over
the window, is not what these figures support. A referee reading the table above
will ask which of the ten numbers is the exponent, and there is no answer that
is not a choice.

## Against the deposit, like for like

Both sides restricted to the same sixteen papers and weighted one paper per
paper, because a paper contributing 21 deposited fits would otherwise count
nearly three times as heavily as one contributing 8.

| substructure | deposited | rebuilt |
|---|---:|---:|
| iron_chalcogenide_11 | 0.483 | 2.291 |
| iron_pnictide_1111 | 2.804 | 3.646 |
| iron_pnictide_122 | 1.580 | 1.900 |

| | deposited | rebuilt |
|---|---:|---:|
| separation across substructures | **5.81** | **1.92** |
| spread across papers | 18.8 | 6.7 |

Bootstrapping the sixteen papers, 2000 draws: the rebuilt separation is 1.92
with a 95% interval of **[1.34, 4.31]**, and the spread 6.7 with **[2.4, 6.7]**.
Leaving out any single paper moves the separation by up to 13%.

So the honest statement is that the substructure separation on the temperature
axis **falls by roughly a factor of three when the axis is measured rather than
extracted, and what remains is not distinguishable from no separation at all**.
The interval includes values near 1.3, and the deposited 5.81 lies outside it,
so the change itself is real even though the residual separation is not
established.

Quoting the separation over all twenty deposited papers, 2.65, against the
rebuilt 1.92 would compare two different cohorts. It is not the comparison made
here, and the earlier draft of this work made exactly that error.

## What still needs deciding

Three things, none of which the data settle on their own.

`0806.2839v1` rests on three isotherms across a 0.18 dex lever in
log10(1 - T/Tc), the shortest in the cohort. Its exponent of 7.70 is the largest
in the table and it is one number, the 2 K to 20 K Jc ratio divided by 0.18. The
trace is faithful and the value is insensitive to Tc, but it is an extrapolation
rather than a measurement and it sets the top of the 6.7 spread.

`1611.08455v1` plots two crystals at overlapping temperatures. The rebuild uses
sample B because the trace captured more of its isotherms, which is an artefact
of tracing rather than a reason. Sample A carries a jc an order of magnitude
larger and the paper says so.

Four papers rest on three isotherms, where a two-parameter fit leaves one
residual and the standard error means very little. Their exponents should carry
their field ranges rather than a standard error.
