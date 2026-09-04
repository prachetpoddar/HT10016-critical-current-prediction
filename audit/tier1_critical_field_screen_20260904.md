# The critical-field scale behind the field-axis fits

Recorded 2026-09-04, corrected the same day after the first version of this
screen was challenged and two of its three tests turned out to be wrong.

## The result

**Three papers are flagged, carrying 36 of the 159 field-axis fits and 36 of
the 94 that pass.** All three had already been read at source before this
screen existed. The screen confirms three known cases and finds no new ones,
which is the honest strength of it.

| paper | fits | what the numbers show |
|---|---:|---|
| `mtphys.2022.100783` | 20 | the irreversibility field rises from 4.5 T at 18 K to 7.0 T at 21 K, and 7.0 T is separately recorded at 4.2 K, so the series looks written with its temperatures reversed |
| `physc.2009.11.051` | 8 | 2.5 T at 2 K rising to 5.5 T at 20 K, read from Fig. 4, the magnetic relaxation rate, which does not measure a critical field |
| `physc.2010.05.048` | 8 | 3.5 T at 2 K rising to 25.0 T at 11 K, from an M(H) figure, with the extraction's own term recorded as `ambiguous_label` |

An upper critical field falls with temperature. So does an irreversibility
field. Nothing legitimate rises.

## Two tests were wrong, and they were most of the screen

The first version reported seven papers and 60 fits. Both of the tests that
have gone were wrong in the direction that made the screen look productive.

**"The scale sits at or below the largest field measured" was wrong.** It
compared the assigned scale against the maximum field in the paper's raw
extraction file. The pipeline filters points to those below the scale before
fitting, so the raw file legitimately extends past it. Checked directly on
every flagged fit: the recorded `H_axis_range_normalized` equals the span of
the retained points exactly, and no fit in the table has a span at or above 1,
the maximum being 0.9987. The test was measuring the extraction file and
reporting it as a property of the fit. It flagged five papers and 42 fits, and
`matchemphys.2023.128348` and `matpr.2019.05.078` were flagged on nothing else.

**"A constant scale with a larger one unused" was wrong.** In both cases it
fired on, the larger value is a zero-temperature extrapolation.
`s10854-026-16566-9`'s 78.1 T is a WHH row with no temperature recorded at all,
sitting beside a proper Hc2(T) curve falling from 9.2 T at 11 K to 0.0 at 16 K.
`phpro.2015.06.160`'s 26 T and 31 T are Hc2(0) values tagged with each
compound's transition temperature, 18.9 K and 25.5 K, and its 9.0 T at 17.7 K
is an ordinary Hc2(T) point: an ac-susceptibility transition reaching 17.7 K on
the 9 T curve is Hc2(17.7 K) = 9 T. Both papers then use the lowest-temperature
Hc2 available as a low-temperature anchor, which is the deposit's documented
`extrapolated_to_low_T_anchor` convention, and it is conservative rather than
wrong. It flagged two papers and 18 fits.

I had already narrowed that second test once, after it fired on four papers
where a zero-temperature extrapolation legitimately exceeds a finite-temperature
value. Narrowing it left the same error in the two cases it still caught.

## What is no longer claimed

The first version said the applicability filter selects for the error it cannot
see, and offered that as the finding that outlived any single paper. The
observation behind it is real: no flagged fit is refused by the bound while 60
of the unflagged ones are, and the Tier 3 literature default supplies 8 of the
94 passing fits against Tier 1's 82. But on three papers that is as consistent
with those three being unusual as with a selection effect, and the version of
the claim that was interesting needed the 60 fits the broken tests supplied.
The screen still prints the split. It no longer calls it a mechanism.

## What is still true and was found by reading, not by screening

- `physc.2011.05.018` has no critical-current-versus-field figure at all, and
  its twenty extracted points and its critical field are without a source. See
  `audit/two_reextract_rows_20260904.md`.
- `physc.2009.11.051`'s field axis is in kilo-oersted and was recorded as
  tesla, a sixth instance of a defect the supplement documents for five papers.
- `mtphys.2022.100783`'s polycrystal record is a copy of its single crystal.
  See `audit/mtphys_2022_100783_duplicate_20260904.md`.

Those three came from opening the papers. No screen found them, and this one
would not have.
