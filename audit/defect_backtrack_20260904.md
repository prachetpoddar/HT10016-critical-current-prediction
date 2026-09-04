# Backtracking every defect to the fit row it touches

Recorded 2026-09-04, after the count of 64 defective fits was challenged as
implausible. Nothing in the data changed. One count was too high and is
corrected here.

## The link that was never checked

Every defect had been established by comparing a publisher figure against an
extraction CSV in the uploads tree. Nothing had checked that the deposited fit
rows were computed from those same CSVs rather than from some later, repaired
version. That is the link the count rests on, and it is the same class of error
that invalidated the tier-1 screen earlier in this session.

For every fit row, the field span implied by its source CSV was recomputed under
the pipeline's own filter to points below `Hc2_T_used`, and compared against the
deposited `H_axis_range_normalized` and `n_pts`.

| result | fit rows |
|---|---:|
| exact match on span and point count | 114 |
| exact on span, point count differs (the source file holds two magnetization branches) | 6 |
| small residual difference, a point or two dropped by a further criterion | 10 |
| no source CSV in the corpus | 29 |
| **total** | **159** |

Two details fell out of this. The filter is strict, `H < Hc2` rather than
`H <= Hc2`, which accounts for most of the apparent mismatches. And the ten
residual cases fall in `jallcom.2023.170146`, `iop_10.1088_0953-2048_29_3_035013`
and `s41598-022-24044-5`, none of which is counted defective.

**Every one of the fit rows counted as defective reconciles exactly to the
extraction CSV that was graded against its figure.** The chain holds.

## But one paper was counted too harshly

`mtphys.2022.100783` supplies the largest single block, and it had been counted
as twenty defective fits on the strength of the polycrystal record being a copy
of the single-crystal one. That reasoning convicts the polycrystal record. It
does not convict the single-crystal record, and the two were lumped together.

The repository holds its own re-extraction of both panels of the paper's Fig. 6,
made earlier in this session. Comparing the deposited values against those
traced curves at 4.2 K:

| H (T) | polycrystal deposited | traced Fig. 6(b) | ratio |
|---|---:|---:|---:|
| 0.5 | 800000 | 59892 | 13.4 |
| 1.0 | 700000 | 43156 | 16.2 |
| 2.0 | 600000 | 32957 | 18.2 |
| 4.0 | 400000 | 28054 | 14.3 |
| 6.0 | 200000 | 2898 | 69.0 |

| H (T) | single crystal deposited | traced Fig. 6(a) | ratio |
|---|---:|---:|---:|
| 0.5 | 900000 | 587719 | 1.53 |
| 1.0 | 800000 | 525779 | 1.52 |
| 2.0 | 700000 | 414452 | 1.69 |
| 4.0 | 500000 | 397816 | 1.26 |
| 6.0 | 300000 | 1059 | 283 |

The polycrystal record is wrong by a decade and more, as established. The
single-crystal record is not. At 0.5 to 4 T it sits 1.3 to 1.7 times above the
traced curve, which is poor digitisation rather than fabrication. Its tail is
wrong: the traced curve has collapsed to about 1000 A/cm2 by 6 T where the
deposit says 300000. And its structure is synthetic, every isotherm being the
previous one shifted down by a constant 100000 at every field, on a file holding
26 distinct values across 100 points, all multiples of 5000.

That is a real defect, but not the same defect, and it should not have been
counted at the same strength. Its twelve fits move to a separate band.

## The corrected count

| state | papers | fits | passing | anchors |
|---|---:|---:|---:|---:|
| defective, figure opened and contradicts | 12 | 88 | **52** | 41 |
| weak, values 1.3x to 1.7x off with a wrong tail | 1 | 12 | **12** | 1 |
| clean, figure opened and agrees | 8 | 37 | 20 | 31 |
| unresolved provenance | 2 | 13 | 6 | 13 |
| no printed figure (MAGLAB) | 9 | 9 | 4 | 10 |
| **total** | **31** | **159** | **94** | **96** |

The 52 split 24 from a kilo-oersted field axis recorded as tesla and 28 from
values that contradict the printed curves.

## Why the number is large without being surprising

It is not that two thirds of the work is wrong. It is that **seven papers of
thirty-one** are wrong, and a single critical-current figure with eight
isotherms generates eight fits, so a handful of bad papers carries a large share
of the rows. The concentration is extreme: two records alone,
`mtphys.2022.100783` polycrystal and `s10854-026-16566-9`, supply 20 of the 52.

And the repository's own screen said as much before any figure was opened.
`audit/extraction_integrity.csv` flagged fifteen live files carrying 60 of the
94 passing fits. The reading pass reached 52 by a different route, on different
evidence, which is corroboration rather than a new claim.
