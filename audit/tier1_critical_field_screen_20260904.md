# The critical-field scale behind the field-axis fits

Recorded 2026-09-04, after two Tier 1 values were checked by hand and both were
wrong. Two of two is not a rate, so every paper was screened.
`analysis/audit_tier1_critical_fields.py` writes
`audit/tier1_critical_field_screen.csv`.

## The result

**Seven of 31 papers are flagged, carrying 60 of the 159 field-axis fits and 60
of the 94 that pass.**

| test | papers | fits |
|---|---:|---:|
| the scale rises with temperature within a sample | 3 | 36 |
| the scale sits at or below the largest field measured | 5 | 42 |
| a constant scale with a larger one unused in the same file | 1 | 12 |

## What the applicability filter does with it

This is the part that outlives any single paper.

| | rejected by the bound | beta extreme | passes |
|---|---:|---:|---:|
| flagged papers | **0** | 0 | **60** |
| unflagged papers | 60 | 5 | 34 |

Median reduced span: 0.710 flagged, 0.149 unflagged.

By provenance tier, over all 159 fits:

| tier | rejected | beta extreme | passes |
|---|---:|---:|---:|
| Tier 1, paper-reported | 2 | 5 | 82 |
| Tier 2, per-substructure ratio | 5 | 0 | 4 |
| Tier 3, literature default | 53 | 0 | 8 |

Eq. (1) admits a curve when the measured field span exceeds 0.3 of the assigned
critical field. A scale that is too small makes that ratio larger. **The filter
therefore selects for the error it cannot see**, which is why the tier labelled
highest-confidence supplies 82 of the 94 passing fits while the literature
default supplies 8, and why not one of the 60 flagged fits is rejected.

The supplement already reports a symptom of this without the cause: the median
ratio of measured maximum to assigned scale is 0.80, and exceeds 0.9 on 15 of 94
curves. A scale that barely exceeds the data is what you get when the scale came
from the data.

## The first version of this screen was wrong

It keyed on the caption each extraction recorded, and an adversarial review took
it apart. Both of the tests it broke were wrong in the direction that flattered
the screen.

**It regressed the scale against temperature after averaging across samples.**
`physc.2013.04.060` appeared to rise, and the rise was entirely sample
composition: three samples at 4.2 K all assigned 10.5 T, five different samples
at 10 K all assigned 11.9 T. Grouped within a sample it does not rise. Three
papers rise, not four; 36 fits, not 44.

**It called six papers wrong for taking their scale from a
critical-current-versus-field figure.** Five of them state that as their own
method, and it is a standard one. `matchemphys.2023.128348` and
`physc.2013.04.060` both define the irreversibility field as the field where Jc
falls to 100 A/cm2, and `mtphys.2022.100783` obtains it by Kramer extrapolation
of the same curves. Reading Hirr off Jc(H) is not a defect, and the screen would
have published eight correct flags with six wrong reasons.

**And it cleared the worst case in the corpus.** `phpro.2015.06.160` states "we
estimate the value of upper critical field (Hc2(0)) approximately 26 T and 31 T".
Its extraction file records both. The fits use **9.0 T at every temperature**,
which is the ac-susceptibility rig's ceiling, in the caption's own words "in
field up to 9 T". The caption named a real measurement, so a keyword test passed
it. Only a numeric confrontation finds it.

The review's own summary of the lesson is better than mine: the screen tested
the note when the defect is in the number.

## The seven

| paper | fits | what the numbers show |
|---|---:|---|
| `mtphys.2022.100783` | 20 | rises within a sample, 4.5 T at 4.2 K to 7 T at 21 K; curves measured to 6 T against a scale of 4.5 T |
| `physc.2009.11.051` | 8 | rises, 2.5 T at 2 K to 5.5 T at 20 K; curves measured to 20 T against a scale of 2.5 T |
| `physc.2010.05.048` | 8 | rises, 3.5 T at 2 K to 12.5 T at 9 K; curves measured to 50 T against a scale of 3.5 T |
| `phpro.2015.06.160` | 6 | 9.0 T at every temperature, the rig's ceiling, with 26 T and 31 T unused in the same file |
| `s10854-026-16566-9` | 12 | 9.2 T at every temperature, with 78.1 T recorded in the same file |
| `matchemphys.2023.128348` | 4 | curves measured to 3 T against a scale of 3 T |
| `matpr.2019.05.078` | 2 | curves measured to 4 T against a scale of 2.5 T |

A scale at or below the largest field measured is not a judgement call. The
fitted form is `log10 Jc = log10 Jc,partial + beta * log10(1 - H/Hc2)`, so the
reduced field reaching 1 puts the model at a logarithm of zero, and
`physc.2009.11.051` reaches 8.

## What is not established

- The three papers whose exposure could not be checked because their extraction
  file is not deposited are reported as unchecked, not as clean. So are the four
  MAGLAB records and `physc.2011.02.004`, whose critical fields are not
  extracted at all but fitted by `analysis/refit_physc_2011_02_004.py`; three of
  its six curves have a measured maximum above its fitted scale.
- No Tier 2 or Tier 3 value shows any of the three defects. That inverts the
  usual reading of the tier ladder and is worth saying out loud: the pathology
  is exclusive to the tier the deposit calls highest-confidence.
- Two further defects the review found by reading PDFs, which no deposit-only
  screen can reach: `matchemphys.2023.128348` records what appear to be Jc
  values in its field column, and the PDF filed under
  `10.1016/j.jallcom.2023.170146` is a different paper entirely, the Tamegai
  Physica C article that is `physc.2009.11.051`.

## What this does not decide

Nothing here is applied. Sixty of the 94 passing field-axis fits rest on a
critical field this screen flags, including all 20 from the MgB2 class, which is
the only family the routine dispatches. What the field-axis result can still
claim is the decision that follows, and it is not one to take from a screen
alone.
