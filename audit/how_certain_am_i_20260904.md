# What I am sure of, what I am not, and one retraction

Recorded 2026-09-04, in answer to a challenge that the scope loss looked too
large. The challenge was right on the most important point.

## The retraction

`physc.2011.05.018` was recorded, before the context break and never re-checked
this session, as a paper that "contains no critical-current-versus-field figure
at all". **That is false.** Fig. 2(e) and 2(f) of Ding et al., Physica C 471
(2011) 651-655 are exactly such figures: Jc in A/cm2 on a log axis against
**H in kilo-oersted**, panel (e) to 50 kOe and panel (f) to 10 kOe, at 2 K and
5 K. The caption states it plainly: "The magnetic field dependence of critical
current densities (e) and (f) are calculated from the data in (c) and (d)."

The real defects there are milder: the axis is kilo-oersted, the decay is far
too shallow (a flat -2000 ladder where panel (e) falls by a factor of seven
across its range), and two of the 600 C points sit at 20 kOe on a panel that
stops at 10.

## The error in the cost estimate

The estimate treated "defective" as "withdrawn", and then reported that
`cuprate_LSCO` disappears, `cuprate_BSCCO` stops being decomposable, and
`iron_chalcogenide_11` falls below the method's own two-compound requirement.

That inference does not follow. **A record whose values contradict its figure
does not have to be withdrawn if the figure is legible. It has to be
re-extracted.** Every one of the thirteen papers in the defective set has a
readable critical-current-versus-field figure in hand, and all thirteen have now
been opened in this session. The repository already contains a working figure
tracer, `analysis/extract_mtphys_fig6.py`, which re-extracted 356 and 478 points
from the two panels of `mtphys` Fig. 6 with published calibration cross-checks.

So no family is forced out. `cuprate_LSCO` rests on `ceramint.2024.10.058`,
whose Fig. 4 is a clean linear plot of five well-separated curves and is among
the easiest in the corpus to digitise correctly. The same holds for
`jallcom.2013.04.183` Fig. 8, `s10854` Fig. 9, `phpro` Fig. 3, `matpr` Fig. 2(a),
`jpcs` Figure (9) and `s41598-025-95932-9` Fig. 4(b).

The cost is re-extraction labour, not lost scope. The earlier note overstated it
and is superseded on that point.

## What I remain confident in

These rest on a figure opened at high resolution with a large, unambiguous gap:

- `matpr.2019.05.078`: the printed axis tops out near 2200 A/cm2 and the
  extraction reports 1e6. Two and a half decades, not a reading error.
- `ceramint.2024.10.058`: a linear axis, five separated curves, and the sample
  the extraction ranks highest is the lowest on the page by about a factor of ten.
- `jallcom.2013.04.183`: a linear axis in units of 1e4 A/cm2, a decade low, and
  half the rows belong to a 25 K figure the paper never printed.
- `physc.2009.05.098`, `physc.2016.05.023`, `s41598-025-24806-x`,
  `physc.2011.05.018`, `physc.2010.05.048`: the printed field axis reads kOe.
  This is a label, not a judgement.
- `mtphys.2022.100783` polycrystal: 13x to 69x against the repository's own
  traced curve, not against my reading of a page.

## What is softer than it was stated

- The magnitude ratios for `s10854-026-16566-9` (quoted 2.6x to 33x),
  `phpro.2015.06.160` (1.5x to 77x) and `s41598-025-95932-9` (1.5x to 50x) are
  eye estimates off logarithmic axes. The direction is not in doubt; a factor
  quoted as 33 could be 15 or 60. They should be re-derived by tracing before
  any of them is repeated in a document.
- `physc.2009.11.051`'s values are round ladders and one series sits about five
  times below the printed curve, but that too is an eye estimate.
- The per-family variance ratios recomputed here do not reproduce the deposited
  ones, which aggregate per paper. No band value should be quoted from them.

## The honest summary

The count of rows that currently disagree with their sources stands at 52
defective and 12 weak, and every one of those rows reconciles to the extraction
CSV that was graded. What does not stand is the conclusion drawn from it. Almost
nothing here is unrecoverable. It is wrong, and it is fixable by reading the
figures again with the tracer rather than by eye.
