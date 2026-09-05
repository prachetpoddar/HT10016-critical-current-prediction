# The cohort retraced through freeze-one-axis, mobilise-the-other

Recorded 2026-09-05. Scripts `analysis/separable_surface_test.py` and
`analysis/frozen_axis_retrace.py`. Tables `audit/separable_surface.csv` and
`audit/frozen_axis_retrace.csv`.

The proposal was that the results were built by freezing one of Eq. (1)'s two
factors and mobilising the other. Tested against everything in the repository,
it holds, and it reorganises most of what the last four days found into one
account.

**I first reported the opposite and was wrong.** An independent review found two
defects that produced the wrong sign, both now fixed and both recorded at the
end of this note.

## What the mechanism predicts

Eq. (1) is a product of a temperature factor and a field factor. A family of
isotherms produced by holding one factor fixed and sweeping the other satisfies

    log Jc(T, H) = a(T) + b(H)

exactly. Every isotherm is one field curve shifted vertically, and the shift
carries all of the temperature dependence.

A measured Jc(T, H) does not. The field dependence steepens as temperature
rises, because the field that matters is H/Hc2(T) and Hc2 falls with
temperature. That interaction term is the physics, and its size is what this
measures, in dex.

## The test, paired

For eight papers the repository holds both a deposited extraction and a pixel
trace of the same printed figure. Put both arms on the same isotherms, the same
field window, the same number of sample fields and the same code path, so the
only difference is where the numbers came from:

| paper | isotherms | window (T) | extraction | its own figure | ratio |
|---|---:|---|---:|---:|---:|
| `physc.2009.11.051` irradiated | 4 | 0.20 to 4.92 | 0.006 | 0.136 | **0.05** |
| `physc.2009.11.051` unirradiated | 4 | 0.20 to 4.92 | 0.013 | 0.136 | **0.10** |
| `s10854-026-16566-9` x = 1% | 3 | 0.5 to 5 | 0.022 | 0.187 | **0.12** |
| `phpro.2015.06.160` | 4 | 1 to 10 | 0.052 | 0.429 | **0.12** |
| `s10854-026-16566-9` x = 3% | 3 | 0.5 to 5 | 0.029 | 0.187 | **0.15** |
| `s10854-026-16566-9` x = 2% | 3 | 0.5 to 5 | 0.034 | 0.187 | **0.18** |
| `physc.2010.05.048` | 8 | 0.07 to 4.93 | 0.058 | 0.269 | **0.22** |
| `s10854-026-16566-9` x = 0% | 3 | 0.5 to 5 | 0.049 | 0.187 | **0.26** |
| `jallcom.2023.170384` (hand) | 4 | 0 to 6 | 0.452 | 0.372 | **1.22** |

Eight of the nine extractions carry four to twenty times less interaction than
the figure they claim to be a reading of. The ninth is the one extraction in the
set that was digitised by hand, and it carries slightly more, which is what a
reading of a real curve does.

The ordering holds at three, five and nine sample fields. Nothing here is
reported that does not survive all three.

## The same result across all the surfaces

| route | surfaces | interaction, dex, median | recorded precision |
|---|---:|---:|---:|
| hand | 6 | **0.402** | 11 figures |
| pixel trace | 24 | **0.173** | full |
| vision extraction | 15 | **0.036** | 1 to 2 figures |

The precision column matters, and it is why the first version of this test gave
the wrong answer. Rounding an exactly separable surface to one significant
figure injects about 0.04 dex of interaction on its own, so a vision extraction
cannot show separability below its own rounding floor whatever it is. Measured
against that floor rather than against zero:

- **eight vision surfaces sit within five times their own rounding floor**, four
  of them within 1.4 times. They are as separable as their recorded precision
  can show.
- **no traced figure does.** The pixel arm sits about three thousand times above
  its floor, and the hand arm is written at eleven figures, which imposes no
  floor at all, and still carries the most interaction of the three.

## What that makes the two exponents

If the surface a fit is made from has no interaction, then beta_H recovers the
field curve that was swept and beta_T recovers the temperature curve that was
frozen. Neither recovers a property of the sample beyond what went in. The
substructure separation the manuscript reports is a separation between the
curves used to build each family's surfaces.

This is consistent with, and now explains, the earlier finding that the
extraction route predicts the exponent completely: hand-digitised beta_H falls
in 0.003 to 0.023 and vision-pass beta_H in 0.120 to 2.409, with no overlap.

## The gates, retraced

The anchor is the scale of the frozen factor, Hc2 or Tc. It does three jobs in
the same fit: it selects the retained points, it forms the abscissa, and it
forms the applicability clause. Nothing independent of it enters.

**The field clause is an identity.** `(Hmax - Hmin)/Hc2 > 0.3` says

    Hc2 < span / 0.3 = 3.33 x span

and where the grid starts at zero, span is the top of the extracted field range.
A rule of that form reproduces the deposited pass and fail on 100% of the 153
fits with a grid. That is arithmetic working, not a measurement, and it is
reported only to show the reconstruction is right. What follows from it is not
arithmetic: **the clause is passed by making the anchor small relative to the
extraction's own field range, and nothing about the sample enters.** Fits that
clear it have a median anchor of 0.9 times the top of their own data; fits
bounded out have a median of 20 times.

**The retention rule is not the one the deposit states.** If the fitter dropped
points at or above Hc2, `kept = grid < Hc2` would reproduce the deposited
statistic everywhere it can be reconstructed. It reproduces 134 of 153, while
`kept = grid < 0.95 Hc2` reproduces 141. Two cases read by hand:
`s41598-022-24044-5` at 10 K drops its 17.91 T point against an 18 T anchor, and
`jallcom.2023.170146` at 10 K drops 4.83 and 4.91 T against a 5.0 T anchor.
There is a second criterion, and it is recorded nowhere.

**The temperature clause is imposed by cutting the window.** All 260
temperature-axis fits are marked passing, and that file records no failure of
any kind, so "all of them pass" is a property of the deposit rather than of the
fits. The largest T_max/Tc anywhere is 0.694 against a clause at 0.7. The
extraction is not what was truncated: across the 17 papers with both an
extraction and a trace, the number of isotherms above 0.7 Tc agrees paper by
paper, 15 in each. The cut happens at the fit. **130 of 258 fits have extraction
data above their own T_max**, and every one of those had data above 0.7 Tc. The
remaining 128 were never truncated, so the clause was not binding on them.

**And it is imposed on one axis only.** Nineteen of the 94 passing field-axis
fits sit above T/Tc = 0.7, over five papers, the worst at 0.955.

## What this reorganises

The anchor defects found over the last two days are not independent errors:

| what was found | what it is under this account |
|---|---|
| two Hc2 ladders that rise with temperature | the anchor is a free parameter of the construction, not a measurement, so nothing constrains its sign |
| anchors sourced from a relaxation-rate figure, magnetisation loops, and other groups' data | the anchor needed a number, not a critical field |
| eight Cohort B Tc anchors that are a family literature constant | the same, on the frozen factor of the other axis |
| the field clause never failing on a passing fit | it cannot: it is a statement about the anchor |
| beta_H predicted completely by extraction route | the exponent is a property of the curve that was swept |

One thing it does not explain, and I am not claiming it does. Data running past
the anchor into the tail is ordinary, and five of the eight papers whose anchor
lies below the top of their own data carry only 0.2 to 3 per cent of peak
current up there. Only two carry a lot, 92 and 82 per cent, and for those two
the traced figures end at 4.93 and 4.92 T against extractions running to 50 and
20, so it is the extraction's field axis that is wrong there and not the anchor.

## The two defects that gave the wrong sign

Both were found by an independent review of the first version of this test.

1. **An unreachable bar.** The test asked whether any surface was separable to
   better than 1e-6 dex, found none, and reported the mechanism refuted. At one
   significant figure the floor is 0.04 dex, four orders of magnitude above the
   bar. The refutation was of the bar, not of the mechanism.
2. **An unmatched comparison.** `physc.2010.05.048`'s extraction was scored on a
   0 to 50 T window against a trace of the same figure on a 0.07 to 4.93 T
   window, and the result, 0.356 against 0.269, was reported as the extraction
   being less separable than its own figure. Matched, it is 0.058 against 0.269,
   a factor of five the other way. That was the only counterexample offered and
   it does not exist.

A third defect silenced a whole arm. The sample-splitting column was chosen from
`doping_or_composition`, whose values in the hand files are `FTS_4.2K`,
`FTS_6K` and so on, one per isotherm. Splitting on it took every hand surface
apart into single isotherms and the hand arm scored nothing at all. A sample
column is now required to carry more than one temperature, and the hand arm,
recovered, carries the most interaction of the three routes, which is the
control the account needs.

## Left open

Whether the beta_T variation with applied field reported on 2026-09-05, a
half-range of 1.35 against a quoted 0.32, survives this account. The Cohort A
extraction is held in a different file that this test has not scored, and a
perfectly separable surface would give the same beta_T at every field. Either
the Cohort A surfaces carry interaction the Cohort B ones do not, or the
variation comes from the anchor in the abscissa rather than from the data. That
is one script away and it is the next thing to settle.
