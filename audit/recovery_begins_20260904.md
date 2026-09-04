# Recovery, first pass: the tool, and the first paper

Recorded 2026-09-04. Two tool defects fixed and demonstrated, one figure
re-extracted, one showcase number corrected.

## Three fixes to the digitiser, each demonstrated

**Outward-pointing ticks were invisible.** `axis_ticks.find_ticks` walked only
inward from the frame, so on a figure whose ticks point into the margin it
returned the two frame corners and nothing else. That is most published figures.
Added `direction` with `inward` (the default, so every existing call is
unchanged), `outward`, and `auto`, plus `find_ticks_dir` which reports which one
produced the answer. On Fig. 6(c) of `jallcom.2023.170384` the outward walk finds
exactly four majors on each axis where the inward walk found none.

**An inverted y axis passed silently.** The geometry calibration reads ticks top
to bottom on the left axis, so `first_major` is the value at the top. Supplying
them the other way round inverted the axis, and the result did not look wrong:
every point landed inside the plotted range and the curve simply ran upward. On
the validation figure that produced a 5 K series rising from 653 to 2.1e5 where
the paper falls from 1.5e6 to 5e3. Added `_check_orientation`, which refuses the
run and names the fix, with `allow_inverted` for a figure that really does
increase downward. **The guard was shown to fire on the exact spec that produced
the silent error.**

**A descending axis was rejected as an odd step.** `_round_step` returned False
for any negative step, so the correct top-to-bottom y spec was refused with "a
step of -1.0 per major tick, which is not a round number". Every y axis whose
values fall down the page is descending. Now only the magnitude is tested and
zero is still rejected.

## The tool validated before it was trusted

Re-traced Fig. 6(c) of `jallcom.2023.170384`, the one paper whose extraction was
independently verified against the printed page and found sound. Agreement
across 26 comparable points: **median 0.011 dex, a ratio of 1.02**. The 5 K
series reproduces to 1.53e6 against a deposited 1.53e6.

## `ceramint.2024.10.058` re-extracted

189 points across five series, tick-fit residual 0.0009 of the span on the y
axis, re-projection residual 0.005 px, and the overlay shows the recovered
points sitting on all five curves through the full field range.

At a common field of 0.7 T:

| sample | traced | deposited anchor | ratio |
|---|---:|---:|---:|
| Nitrogen-2 | 1843 | 2100 | 1.14 |
| Vac-2 | 1622 | 1200 | 0.74 |
| LSCO-CS | 797 | 1900 | 2.38 |
| Vac-1 | 699 | 1600 | 2.29 |
| Nitrogen-1 | 121 | 2200 | **18.2** |

The ranking is restored: Nitrogen-1, which the deposit ranks highest, is the
lowest curve on the page by a factor of fifteen.

## The showcase number was wrong in the direction that helps

The supplement offers these five rows as the illustration of the paper's
contribution: "five bulk specimens of the same compound from the same paper,
differing only in processing atmosphere, span 0.26 dex."

The traced spread is **1.18 dex**, not 0.26. Processing atmosphere moves the
critical current by a factor of fifteen across these five specimens, not a
factor of two. The example is better than the paper claims, once the numbers are
right.

## Next

`jallcom.2013.04.183` Fig. 8 and `s10854-026-16566-9` Fig. 9 are the next two,
carrying 4 anchor rows and 12 passing fits respectively.
