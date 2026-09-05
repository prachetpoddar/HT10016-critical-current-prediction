# The field axis, put through the same test. It is not shown to be better.

Recorded 2026-09-05, stage C. An independent review found fourteen defects in
the first version of this comparison and every correction moved the answer
against the field axis. The claim that it is materially better than the
temperature axis is withdrawn.

## What is genuinely different about the field axis

The anchor defect that dominated the temperature axis is not present. Hc2 is not
a constant keyed to the compound string: nine compounds of thirty-one carry more
than one value, and 89 of 159 fits carry a Tier 1 anchor. That said, "read from
the paper at a named temperature" describes **35** of those 89; the rest are
extrapolated to a low-temperature anchor, interpolated between two temperatures,
computed from a fitted formula, or carry a term the deposit itself records as
`ambiguous_label`.

The deposit also refuses fits the temperature axis never refused: 60 fail
Eq. (1)'s field clause and 5 have no fitted exponent at all, leaving 94 over 16
papers. Those three numbers are one partition rather than three tests: the
applicability flag is the field clause restated, and the smallest passing
normalised range, 0.3499, could not have been anything but just above the
threshold.

## What the figures say

Six of the sixteen passing papers have a pixel trace of their own figure. On
those, refitting beta_H from the trace at the same temperature, under the same
Hc2, over the same H < Hc2 window:

| paper | fits scored | ratio |
|---|---:|---:|
| 1002.0208v2 | 6 | 0.97 |
| jallcom.2023.170384 | 2 | 1.28 |
| s10854-026-16566-9 | 12 | 0.67 |
| mtphys.2022.100783 | 2 | 2.40 |
| phpro.2015.06.160 | 4 | 2.42 |
| matpr.2019.05.078 | 2 | 2.57 |

Five of 28 fits land inside 0.8 to 1.25.

## Why the first version of this was wrong

- **`elsevier_10.1016_j.physc.2016.05.023` was scored against the trace of
  `1611.08455v1`.** Those are different papers by the same group. physc.2016.05.023
  measures FeSe and FeSe0.86S0.14 and its own extraction is not in the corpus.
  The mapping is removed and its 1.49 withdrawn.
- **`s10854` was scored entirely against panel (a).** Its twelve fits are four
  MWCNT substitution levels across three temperatures and all four panels are
  traced; nine of twelve pairs were compared with the wrong curve. Per panel the
  ratios run 0.49, 0.50, 0.39 at x=0%, up to 1.74, 1.65, 1.68 at x=3%, a
  monotone trend the pooled version erased. The paper moves from 0.44 to 0.67.
- **Three papers had their specimens pooled into one curve.** `matpr` plots a
  monocrystal and a polycrystal at 5 K; pooling them gave one exponent of 0.643
  where the two are 0.478 and 0.922. `ceramint` and `jallcom.2013.04.183` were
  pooled the same way.
- **The headline was a median of paper medians.** Per fit the median ratio is
  1.01 and the median distance from agreement is 0.537 in log; per paper the
  signed median is 1.84. Aggregating first let one paper with twelve low-ratio
  fits count the same as one with two high ones.
- **The rank statistic had no power.** One paper ranked "first of one", because
  no other figure could score it. Expected rank-first count 1.97, observed 3,
  p = 0.25.

## The comparison that was claimed, tested

| | papers | median distance from agreement, in log |
|---|---:|---:|
| field axis | 6 | 0.639 |
| temperature axis | 14 | 0.880 |

Mann-Whitney, field closer to agreement: **p = 0.133**. Per fit it is 0.537 with
p = 0.036, but 28 fits over 6 papers are not 28 independent comparisons.

What separates the two axes is direction, not accuracy. The field-axis errors
run upward, signed median 1.84; the temperature-axis errors run downward, signed
median 0.42. A signed median near one is not agreement when the errors run both
ways.

## The selection problem, which no correction fixes

The six scored papers were not sampled. Every trace in `data/reextraction` was
built as remediation for a paper already under suspicion, and four of the six
were established as defective before they were traced: `matpr` reports 1e6 where
its figure peaks near 2e3, `phpro` reports 1e6 against a stated 3.9e5,
`s10854`'s x=0% series reproduces its x=3% panel, and `mtphys`'s polycrystal
rows duplicate its single-crystal rows. The other two are carry-overs from the
temperature-axis work.

They cover 28 of the 94 passing fits and 6 of the 16 passing papers. Nothing
here extrapolates to the other ten, which include five papers contributing six
to eight fits each and none of which has ever been read at source.

## Where this leaves the two axes

The temperature axis is settled: none of its fourteen scorable papers reproduces
its figure, and the anchor behind every fit was a compound-keyed constant
presented as paper-reported.

The field axis is not settled and is not cleared. It is better provenanced and
it gates itself, but on the only six papers that can be checked it disagrees
with the published figures by an amount not distinguishable from the temperature
axis's. Clearing it would take tracing a random sample of the ten untraced
passing papers, which is the obvious next unit of work and has not been done.
