# Was it anchored extrapolation rather than generation? Mostly I cannot tell.

Recorded 2026-09-05, after the question was raised that the temperature-axis
series could be a calculation built on a few real readings extrapolated across
the panel, rather than generated. That is a reasonable mechanism and it is the
kind of work anchoring calls for. It was tested against the three papers whose
figures have a pixel trace, and then attacked by an independent reviewer.

The outcome is mixed and it costs the previous verdict most of its scope.

## What the hypothesis gets right

The extractions are in contact with the papers. For all three traced papers the
extracted isotherm temperatures match the figure's exactly: 7 of 7 for
`2012.13723v3`, 8 of 8 for `2207.06629v1`, 3 of 3 for `2305.10034v1`. The field
ranges match too.

That contact is at the level of printed text, not curves. The reviewer opened
the overlays: `2207.06629v1` prints its temperatures as labels inside the plot
area and `jallcom.2023.170384` carries them in a legend box. Recovering the
isotherm list requires reading no curve, so this does not by itself distinguish
a reader from a generator that OCRs the panel.

## What kills it for one paper

`2207.06629v1` uses only the mantissas {1, 1.5, 2, 3, 4, 5, 6, 8} across all 136
values: an eight-rung-per-decade ladder. Every isotherm is one 17-element
sequence shifted by an integer number of rungs, 0 / -1 / -2 / -3 / -4 / -5 / -6
/ -8 for 4 K through 32 K.

The consequence is a signature no reading can produce. The deposited beta_T is
**exactly periodic in applied field with period 4.0 T**, to one part in 1e8:

    beta_T(0.0) = beta_T(4.0) = beta_T(8.0) = 1.329562
    beta_T(0.5) = beta_T(4.5)               = 1.501217
    beta_T(1.0) = beta_T(5.0)               = 1.619771
    beta_T(1.5) = beta_T(5.5)               = 1.842774

A critical-current temperature exponent that repeats every 4 T is fixed by the
ladder's step size and its rung-shift schedule. No coarse reading, and no
extrapolation from one, generates it.

Run across all eighteen, exact periodicity appears in **one paper only**. It is
decisive where it fires and silent elsewhere.

## What kills the test that looked like recovery

Refitting beta_T from the traced figure gave a deposited/figure ratio of 0.97
for `2207.06629v1`, which looked like the extraction had recovered the real
temperature exponent. A permutation control removes that reading:

| deposited from | figure from | median ratio |
|---|---|---:|
| 2012.13723v3 | 2012.13723v3 (its own) | 0.50 |
| 2012.13723v3 | 2207.06629v1 (a stranger) | **0.62** |
| 2207.06629v1 | 2012.13723v3 (a stranger) | 0.81 |
| 2207.06629v1 | 2207.06629v1 (its own) | 0.97 |

`2012.13723v3` agrees better with a figure it has never seen than with its own.
Both papers are Ba-122 at Tc = 38 K over the same 4 to 24 K window, and beta_T
sits between 1.5 and 2.2 across that whole material class, so a ratio anywhere
in 0.5 to 1.0 is what chance delivers. The 0.97 is not evidence of contact with
that figure.

## Two things previously claimed that do not hold

1. **"Every isotherm terminates at the same field in 18 of 18, which cannot
   happen in a real measurement."** The second clause is true and the first is
   still a fact about the data, but it does not discriminate. Evaluating
   anything on a common field grid produces common termination, including the
   anchored-extrapolation mechanism proposed here. It was presented as the
   strongest evidence and it is not evidence for generation over anchoring.

2. **"A generator has no way to know the isotherm temperatures."** False. They
   are printed on the page as text.

## Separately surfaced

The deposited row for `2305.10034v1` carries Tc = 28.0 K where that paper's
Table 3 reports 13.3(2) K, and records the compound as La2FeAs2O where the
figure is captioned La0.87Sm0.13FeAs0.91P0.09O. With Tc = 13.3 the ratio for
that paper moves from 0.41 to 1.17. No beta_T for it means anything until the
Tc is fixed.

## Where this leaves the verdict

| | papers |
|---|---:|
| generation proven on structure alone | **1** (`2207.06629v1`) |
| traced, but the discriminating test has no power | 2 |
| no trace and no decisive test available | **15** |

The earlier statement that eighteen of eighteen are fabricated is **withdrawn as
to mechanism and as to scope**. What survives is that all eighteen are heavily
quantised (eight to forty-six distinct mantissas for up to 231 values) and that
their isotherms are near-parallel translations of one another (mean scatter of
the inter-isotherm log ratio 0.011 to 0.178 dex). Both are consistent with a
coarse reading as well as with generation. They mean the series carry little
independent information; they do not establish how the series were made.

Deciding the remaining fifteen requires a pixel trace of each figure and a
per-paper Tc taken from the paper. Until then no global claim about the
temperature axis should be made in either direction.

This is the third count in this session stated more broadly than the evidence
supported. The pattern is the same each time: a property that is real is
promoted to a discriminator without a control that shows it discriminates. The
permutation control now exists as code.
