# Every temperature-axis figure traced. The verdict, paper by paper.

Recorded 2026-09-05, closing the recovery the earlier notes left open. All
seventeen traceable Cohort A figures now have a pixel trace. An independent
review found three defects in the first version of this adjudication and all
three are corrected here; the corrections make the result harsher, not softer.

## What was corrected before this was reported

1. **The comparison was incoherent.** The deposited exponent is fitted under the
   compound-keyed Tc; the first version refit the figure under the paper's own
   Tc and divided one by the other. That mismatch alone produced three apparent
   recoveries. Both sides now use the same Tc, and the table reports it under
   the deposited Tc and under the paper's own.
2. **A median of ratios hid a disagreement that changes sign.** For
   `1903.00866v2` the deposited exponent rises with field while the figure's
   falls through zero: rank correlation exactly -1, median ratio 1.00. The rank
   correlation is now reported beside the ratio.
3. **"Outside the panel" was measured against the trace.** A trace that misses a
   curve's tail shrinks the apparent panel. It is now measured against the axis
   limits the calibration recovers from the ticks, which cuts the count from
   nine papers to six.

## What the figures say

**The extractions know each figure's isotherm list.** Sixteen of seventeen
record temperatures the figure plots, within 0.6 K. Two of those are not exact:
`1111.3923v1` records 4.0 K against a plotted 4.2 K, and `2510.10264v1` records
2.0 K against a nearest plotted 2.5 K. `2510.10264v1` also records a 5 K
isotherm that exists in no panel of that paper. Something read the page.

**Four papers have a field axis out by two to four orders of magnitude.**

| paper | recorded fields | the figure's axis |
|---|---|---|
| 1002.0208v2 | 1e-6 to 1.6e-3 T | 0.2 to 15 T |
| 1108.0407v1 | 5e-4 to 5e-3 T | 0.04 to 5 T |
| 2511.19058v1 | 1e-4 to 1e-2 T | 0.1 to 4.6 T |
| 0907.0147v2 | 1e-5 to 1.2e-3 T | no axis on the page carries it |

A fifth, `1502.05345v1`, carries two field blocks 571 times apart: eighteen
values from 2e-4 to 3.5e-3 T and seventeen from 2 to 34 T, in one paper.

**Six papers put Jc outside the printed panel**, by 1.0 to 2.3 dex: 0903.0004v2,
1108.0407v1, 1502.05345v1, 1903.00866v2, 2207.06629v1, 2511.19058v1.

**One figure cannot support its extraction at all.** `1104.0477v2` Fig. 3(c)
plots one marker on the 2.0 K isotherm, two on 4.5 K, two on 7.5 K, three on
10.0 K and three on 12.0 K. Everything between them is a straight connecting
segment. The extraction records a nineteen-value field grid from 0 to 18 T for
all five, and no isotherm in the figure has any data above 14 T.

## The exponent

Refitting beta_T from each traced figure inside each deposited row's own
temperature window, with the same Tc on both sides:

| | papers |
|---|---:|
| scored | **14** |
| beta_T reproduced from the figure | **0** |
| ratio below 1 | 13 (the fourteenth is 1.00, and anti-ordered) |
| ratio below 0.8 | 12 |
| cannot be scored: no recorded field lies on the figure's axis | 3 |

The median ratio is **0.42**, and the range is 0.09 to 1.00. The two nearest to
one are not agreement: `1903.00866v2` at 1.00 has a rank correlation of -1.00
between the deposited exponent and the figure's, and `2207.06629v1` at 0.94 has
-0.06. Using the paper's own Tc on both sides instead moves nothing: the ratios
change by at most 0.07.

So the failure is not scatter. The deposited temperature exponents are
systematically about **two and a half times too small**, in the same direction,
in every paper that can be scored.

## What this settles, and what it does not

It settles the question the earlier notes left open. The extractions are in
contact with the papers, at the level of the printed isotherm labels and often
the field range, so "generated from nothing" is wrong and stays withdrawn. But
none of them reproduces its figure's Jc values well enough for the fitted
temperature exponent to survive, and four have a field axis wrong by orders of
magnitude. The deposited temperature-axis exponents are not measurements of
these papers.

It does not identify a mechanism, and no claim about one is made here.

The permutation control is reported alongside every ratio and no ratio needed
it in the end: none of the seventeen reaches agreement with its own figure, so
there is nothing for a stranger to beat.
