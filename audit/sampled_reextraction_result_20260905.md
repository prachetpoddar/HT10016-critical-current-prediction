# What re-extraction would do, and a defect it exposed on the way

Recorded 2026-09-05, running the experiment pre-registered at `8ddd1dc`. An
independent review found six defects; two changed the answer and one of them
found something larger than the experiment.

## The answer to the question asked

Refitting beta_H from a pixel trace of each figure, at the same temperature, for
the same sample, under the same Hc2:

| | fits |
|---|---:|
| covered | 60 of the 94 passing |
| comparable after unique matching | 36 |
| exponent essentially unchanged | 2 |
| exponent moves | 34 |
| still clearing Eq. (1)'s field clause | **36 of 36** |
| no traced isotherm at that temperature | 20 |
| no lever to fit against | 4 |

Median exponent shift **0.70 in log**, a factor of two.

So re-extraction **changes the manuscript's numbers rather than removing its
fits**. That part is robust: under hand-like six-point subsets the median shift
is 0.81 to 0.84 rather than 0.70, and 33 to 36 of the fits still move.

"Only two survive" is not robust and should not be quoted alone. The count
against threshold:

| shift below | 0.05 | 0.10 | 0.25 | 0.50 | 1.00 | 1.50 |
|---|---:|---:|---:|---:|---:|---:|
| fits inside | 0 | 2 | 2 | 8 | 25 | 31 |

At a factor of e the majority sit inside, and under any hand-like subsampling the
identity of the two survivors changes every time.

## Two claims of mine that were wrong, in opposite directions

`audit/field_axis_census_result_20260905.md` said sixteen fits across
`physc.2009.11.051` and `physc.2010.05.048` pass Eq. (1) only because
kilo-oersted numbers sit in a tesla column, and would fail once corrected. **That
is wrong.** I divided the reported span by ten without re-running the point
selection, and correcting the unit also admits more of the extraction's own
points. Re-run properly, all sixteen clear 0.3.

I then claimed the opposite mechanism: that the extractions cover only a fifth of
their figures and re-reading restores the window. **Also wrong.**
`physc.2010.05.048`'s extraction covers the full 0 to 50 kOe of its figure. Its
window was narrow because the H < Hc2 cut was applied to a column inflated
tenfold.

What stands from the census is narrower and still true: the points the deposit
actually fitted span 0.036 to 0.087 of Hc2, so the deposited
`H_axis_range_normalized` of 0.36 to 0.87 does not describe the fit it labels.

## The defect the experiment exposed, which is larger than the experiment

**Hc2 rises with temperature in three of these papers.**

| paper | Hc2 used, by temperature |
|---|---|
| physc.2009.11.051 | 2.5 T at 2 K, 4.5 at 10, 5.0 at 15, 5.5 at 20 (Tc 22 K) |
| physc.2010.05.048 | 3.5 T at 2 K, 4.0 at 4, 5.0 at 6, 8.5 at 8, 12.5 at 9, 25 at 11 (Tc 14 K) |
| mtphys.2022.100783 | 4.5 T flat to 18 K, then 5.0, 6.0, 7.0 |

An upper critical field falls with temperature and vanishes at Tc. These rise.

Three further checks agree. Traced points carry Jc well above zero at fields up
to twice their own Hc2, and at the last point below Hc2 the current is still a
third to two thirds of its maximum, where Hc2 is by definition where it
vanishes. The provenance files name the source: `physc.2010.05.048`'s anchor is
taken from a figure captioned "field dependence of magnetization" with the term
recorded as `ambiguous_label`, and `physc.2009.11.051`'s from a figure about an
interpolation index. And the deposit's own compound defaults for these
materials are 50 T and 47 T, ten to fourteen times larger.

**Under those defaults none of the sixteen fits clears the window at all.**
Whether they pass turns entirely on an anchor that cannot be an upper critical
field. That is not a re-extraction problem and hand re-extraction would not fix
it.

## Four more corrections made before this was written

- **No lever screen.** Four refits were ratios of a real decade-long fall in Jc
  to a regressor that barely moves: `physc.2010.05.048` at 9 K gave 15.5 against
  a deposited 1.4 on a lever of 0.112 dex. `adjudicate_field_axis.py` screens on
  exactly this and the first version of this script did not.
- **`mtphys.2022.100783` was excluded wholesale on a reason copied from another
  script.** Its deposited rows do carry panel labels. Two of its twenty fits are
  comparable; the other eighteen are at temperatures neither trace covers.
- **`phpro.2015.06.160`'s 15 K trace contains an annotation arrow.** Four points
  above 4.4 T, each of two to eight pixels, sit a decade and a half above the
  curve. Cleaned, that refit moves from 1.24 to 8.77.
- **The 0.3 threshold's attribution is unverified.** The repository states 0.3 as
  a bound on the reduced field of a prediction target; here it is applied to the
  normalised span of a fit, which is a different quantity.

## What this means for a hand pass

The experiment says a hand pass is worth doing and would not empty the deposit:
the fits survive the window, and their values change by about a factor of two.

It does not say a hand pass is sufficient. The three failures now on file in this
corpus that a hand pass cannot touch are a kilo-oersted axis written into a tesla
column, a file named for the wrong DOI, and an Hc2 that rises with temperature.
All three are unit, provenance and anchor errors. Reading the curve more
carefully fixes none of them.
