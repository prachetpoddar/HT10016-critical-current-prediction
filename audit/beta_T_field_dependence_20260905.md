# Where the temperature exponent's field dependence lives

Recorded 2026-09-05. Script `analysis/beta_T_variation_source.py`, table
`audit/beta_T_variation_source.csv`. Corrections to
`analysis/field_dependent_exponent.py` and to two earlier notes are recorded at
the end.

The open item from the retrace was whether beta_T's variation with applied
field, reported at a median half-range of 1.35 against a quoted 0.32, is a
property of the material or of the anchor. It is a property of the material,
and the deposited extraction does not carry it.

## The fit rule, reproduced before anything was changed

log10 Jc regressed on log10(1 - T/Tc) over each fit's own [T_min, T_max] at its
own field, every extraction row kept and no per-temperature collapse, recovers
the deposited beta_T for **257 of the 258** fits that have an extraction.

The one that does not is worth naming. `1502.05345v1` at 34 T is deposited at
2.2578 where the rule gives 2.9042 on the same five points. Every other field of
that paper reproduces and lies between 2.827 and 2.940. **That single departure
carries 83 per cent of that paper's deposited half-range**, so the one fit in
258 that the rule does not reproduce is the extreme value that sets the paper's
apparent field dependence.

## In the deposit, beta_T barely moves with field

Median half-range across a paper's own fields: **0.290** over the 17 papers with
a rectangular fit window, against a between-substructure difference of 1.75.

## Whether that residue is writing precision cannot be settled

The deposited values sit on a coarse geometric ladder, eight to forty-six
distinct mantissas over 39 to 231 values. Rounding an exactly separable surface
to that kind of precision gives beta_T a spread from nothing. Taking each
paper's own additive fit, which has a constant beta_T before it is written down
at all, and writing it down four ways:

| how the numbers are written | median half-range |
|---|---:|
| every cell at the paper's finest precision | 0.389 |
| every cell at the paper's median precision | 0.357 |
| each cell at its own recorded precision | 0.185 |
| snapped to the paper's own observed mantissa ladder | 0.163 |
| **observed** | **0.290** |

The observed value sits inside that range, so the spread is of the same order as
what quantisation can inject. It is not more than that. The four models disagree
by a factor of two and a half, the per-paper rank correlation between the null
and the observed spread is 0.48 at p = 0.05, and the per-paper ratio of null to
observed runs from 0.08 to 39. **The quantisation account is not established and
is not reported as though it were.** The first version of this note said
quantisation reproduced essentially all of the spread, on the strength of a
median of ratios of 0.96 between two uncorrelated distributions. An independent
review removed it.

## The printed figures carry it, and the extraction does not

This is the result. Same paper, same isotherms, the same fields, the same Tc,
the same fitting rule, both arms through the same code:

| paper | isotherms | fields | extraction | its own figure | its figure's reading floor |
|---|---:|---:|---:|---:|---:|
| `0903.0004v2` | 3 | 13 | 0.927 | **1.780** | 0.362 |
| `2308.10492v1` | 5 | 8 | 0.441 | **2.525** | 0.919 |
| `1009.4896v1` | 5 | 7 | 0.262 | **2.398** | 0.309 |
| `1611.08455v1` | 4 | 5 | 0.076 | **1.539** | 1.287 |
| `0906.0444v1` | 8 | 7 | 0.287 | **1.062** | 0.121 |
| `0806.2839v1` | 3 | 9 | 0.031 | **0.555** | 0.243 |
| `2012.13723v3` | 6 | 5 | 0.117 | **0.337** | 0.320 |
| `2207.06629v1` | 6 | 13 | 0.263 | **0.289** | 0.080 |

Median extraction **0.263**, median figure **1.300**, the figure larger in
**8 of 8**. Restricted to interior fields, dropping the lowest and highest each
arm survives on, it is 0.245 against 0.877 and the figure is larger in 6 of 6,
so this is not an edge or extrapolation artefact.

The figure arm carries its own floor: the scatter of a trace about a smooth
curve, propagated through an exactly separable surface of the same shape, which
is what reading a real figure produces from nothing. The figure half-ranges run
1.1 to 8.8 times that floor, median 3.2. **Two of the eight are within 1.5 times
it** (`1611.08455v1` and `2012.13723v3`) and should not be leaned on.

## What was excluded, and why it is not neutral

Nine of the twenty papers have no figure comparison. The reasons matter:

| paper | why |
|---|---|
| `1002.0208v2` | extraction fields 1e-6 to 1.6e-3 T, figure 0.21 to 15 T |
| `1108.0407v1` | extraction 0 to 0.005 T, figure 0.04 to 4.99 T |
| `2511.19058v1` | extraction 1e-4 to 0.01 T, figure 0.10 to 4.6 T |
| `1104.0477v2` | extraction 0 to 18 T, figure 0.21 to 14 T, no overlap on its grid |
| `1502.05345v1` | overlap on two points |
| `1111.3923v1`, `2510.10264v1` | only two isotherm labels match the figure's |
| `0907.0147v2`, `2305.10034v1` | no trace |

Four of those extractions disagree with their own printed figure's field axis by
three or four orders of magnitude. Those papers remain in the deposit tables
above with no flag, and their contribution to "beta_T barely moves with field"
is a statement about a field axis that is not the paper's.

`1903.00866v2` is excluded from every table here. Its extraction holds 0.0005 to
0.005 T and 0.5 to 5.0 T, which are the same physical fields on two unit scales
from different pages, and the deposit fits beta_T at both as though they were
different fields. Its deposited half-range of 1.425, the largest in the cohort,
is a spread across unit systems. It also carries 66 duplicated cells up to 60
times apart.

## What this settles, and what it costs

The field dependence of beta_T is real. It is in the printed curves, it is three
times the reading floor at the median, and it is four to five times what the
deposited extraction of the same figures carries. The extraction has been
flattened, which is the retrace's account of how these surfaces were made, and
this is the sharpest measurement of that flattening in the repository: the
interaction the surfaces should carry is measurable in the figures and is gone
from the deposit.

What it does not support is the comparison the earlier note drew.

## Corrections

**`analysis/field_dependent_exponent.py` compared a ratio with a half-range.**
It printed "separation across substructures 1.92" beside "median within-paper
half-range 1.35" and called the first 1.3 times the second. 1.92 is a ratio of
substructure medians and 1.35 is a half-range in exponent units. Multiplying
every exponent by ten leaves the ratio alone and multiplies the half-range by
ten. The like-for-like pair is the **difference** between substructure medians,
1.75, against the half-range, 1.35, and 1.75/1.35 is the 1.3 the sentence always
used. The script now prints the difference and says so.

**1.92 is not the manuscript's number.** It is this repository's own pixel-trace
rebuild. The deposited separation is 5.81 on the same 16 papers and 2.65 over
all 20. Setting the manuscript's claim against 1.92 attributes the audit's own
number to the thing being audited, and picks the value most favourable to the
audit.

**Neither number is a point estimate.** The rebuilt separation carries a
bootstrap interval of 1.34 to 4.31, and the between-family difference of 1.75 is
smaller than the between-paper scatter of the same quantity inside a single
substructure: 1.18, 2.28 and 0.82 for the three families.

**`audit/anchored_vs_generated_20260905.md` said "nine to forty-six distinct
mantissas" while its own earlier line lists eight for `2207.06629v1`.** It now
says eight.

## Guards added after review

The self-test now covers `additive_surface`, which nothing tested and whose
grand-mean term can be dropped while leaving the surface separable, shifting
every cell against the rounding grid with no visible symptom; `round_sig` at the
decade carry, below one, and against its own post-condition; and `paper_table`
against a synthetic frame carrying both a duplicated cell and two field scales.
