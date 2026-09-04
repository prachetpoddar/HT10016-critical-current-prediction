# Every paper behind the temperature axis was opened, and every one is fabricated

Recorded 2026-09-04. Eighteen papers, read at their published figures. Nothing
in the data changed.

## The result

`data/phase_3_p44_post_UCLA_beta_T_fits.csv` holds **260 temperature-axis fits
across 20 papers**, every one marked `ok`. Eighteen have PDFs on disk. All
eighteen were opened and compared against the printed figure.

**Eighteen of eighteen are defective.** Not one is sound.

| paper | fits | what the figure says |
|---|---:|---|
| `0806.2839v1` | 11 | four series are one ladder rescaled by powers of ten; text says 1.2e6 intragrain, extraction 5.0e5 |
| `0903.0004v2` | 15 | printed 2 K curve is flat at 1.33e6 at 5 T, extraction 5.0e4, a factor of 27 |
| `0906.0444v1` | 11 | printed curves are flat plateaus above 10 kOe; the irradiated panel, the paper's headline, is absent |
| `0907.0147v2` | 14 | field column spans 1e-5 to 1.2e-3 T against a printed axis of 0.02 to 12 T |
| `1002.0208v2` | 17 | field column spans 1e-6 to 1.6e-3 T; the printed axis is 0 to 16 T. Zero points in range |
| `1009.4896v1` | 11 | printed 2 K is 7e4 at 48 kOe, extraction 500, a factor of 140; the paper's fishtail is absent |
| `1104.0477v2` | 19 | reports data to 18 T, past both the axis and the instrument's stated 14 T limit |
| `1108.0407v1` | 11 | printed axis 0 to 50 kOe, extraction 0 to 0.005 T, exactly 1000x too small |
| `1111.3923v1` | 9 | the extraction's 12 K value implies a pinning force ten times the paper's own printed maximum |
| `1502.05345v1` | 18 | every series is exactly Jc = J0 x 2^(-H/2T); text says 6.3 MA/cm2 self-field, extraction 1.0e6 |
| `1611.08455v1` | 15 | ten published curves collapsed to five; Jc(9 K) is Jc(7 K) shifted by one index, exactly |
| `1903.00866v2` | 21 | tails span three decades where the printed curves span a factor of two |
| `2012.13723v3` | 8 | median 1.36x against the repository's own deposited trace of the same figure |
| `2207.06629v1` | 17 | median 2.08x against the repository's own deposited trace |
| `2305.10034v1` | 13 | supplies eight points past where the printed 8 K curve ends |
| `2308.10492v1` | 16 | printed 1.8 K is a flat plateau near 5.5e5 to 20 T, extraction 4.0e4, a factor of 14 |
| `2510.10264v1` | 13 | 20 K at 1 T reads about 2e2 on the page, extraction 1.0e4 |
| `2511.19058v1` | 19 | printed axis 0.1 to 50 kOe, extraction tops out at 0.01 T, the plot's first tick |

## One signature, everywhere

Every one of the eighteen is the same construction: **a round-number ladder,
shifted one rung per temperature, on an invented uniform field grid.** Values
are drawn from {1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8} times a power of ten. Series
that should terminate at different fields all terminate at the same one. Curves
that plateau, cross, or show a fishtail are replaced by smooth monotone decay.

Five papers additionally have their **field axis wrong by 100 to 10000 times**.
Six have the wrong compound formula recorded: `Fe2TeSe`, `Pr2FeAs2O`,
`La2FeAs2O`, `Ba(FeAs)2`, `Sm2FeAs2O`, `Fe9Se8`.

Fourteen of the eighteen papers state a Jc value in their own text. In all
fourteen the stated value contradicts the extraction and agrees with the figure
as read.

## The control that settles it

`2305.10034v1` is the arXiv preprint of `jallcom.2023.170384`. The same figure
was extracted twice, once into each cohort, and both extractions are in the
deposit.

| | agreement with an independent trace of Fig. 6(c) |
|---|---|
| Cohort B extraction | median 0.011 dex, a ratio of **1.02** |
| Cohort A extraction | median 0.195 dex, a ratio of 1.57, worst point **57x** |

The Cohort A 8 K series reads 2.0e5, 1.8e5, 1.6e5, 1.4e5, 1.2e5, 1.1e5, 1.0e5,
9e4, 8e4, 7e4, 6e4, 5e4, 4e4 on a uniform 0.5 T grid out to 6 T. The printed
8 K curve ends at 2.0 T. Eight of those thirteen points correspond to nothing on
the page.

Same paper, same figure, same deposit. One extraction is right to two per cent
and the other is a ladder. The defect is in the Cohort A pipeline, not in the
papers and not in the difficulty of the figures.

## What this means for the manuscript

The field-axis result was already reduced to 42 of 94 passing fits, of which
only 20 rest on a figure anyone has read. The temperature axis was the other
half of Eq. (1) and was assumed sound throughout. It is not. All 260 of its fits
come from extractions that were generated rather than read.

Nothing here is unrecoverable in principle: eighteen legible figures are on
disk and the tracer now works. But the temperature axis has to be rebuilt from
the figures before any exponent computed from it can be quoted.

## Method

Each paper was audited independently against its own PDF: locate the
Jc-versus-field figure, record the printed axis labels and units verbatim, read
values off the figure at named fields, compare, and check shape, terminations
and round-number structure. Fourteen audits also quote a Jc value from the
paper's own text as a check that does not depend on reading the figure at all.
