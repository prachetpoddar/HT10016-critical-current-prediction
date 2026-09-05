# What happened to the rest of the papers

Recorded 2026-09-05. Script `analysis/coverage_map.py`, table
`audit/coverage_map.csv`.

The census covers four papers, which invites the question of what happened to
everything else. The answer has two halves. The census's four are fully
accounted for and the accounting was already on file. The larger set is not, and
checking it turned up a gap the audit had not looked at.

## The census's four, reconciled

`audit/field_axis_census_preregistration_20260905.md` and its amendment
partition the sixteen papers that carry a passing field-axis fit:

| | papers | passing fits |
|---|---:|---:|
| traced for the census | 4 | 28 |
| reported from an existing source reading | 1 | 8 |
| unassessable, no source document in the corpus | 5 | 10 |
| already traced before the census | 6 | 48 |
| **total** | **16** | **94** |

The repository agrees. Of the sixteen, nine carry a pixel trace, two have a PDF
and no trace, and five have neither. The two with a PDF and no trace are exactly
the two the amendment excluded with a stated reason: `physc.2009.05.098`, whose
PDF is page one of a six-page paper in all three places it appears, and
`jallcom.2023.170146`, whose file under that DOI is a different paper. So the
census is four because ten of the sixteen were already traced or already read,
and the remaining two cannot be traced from what is here.

That accounting stands. Nothing was dropped after its answer was known.

## The gap the accounting does not cover

The provenance table holds 62 rows, one per paper the deposit says contributes.
Sorting them by what they actually produce:

| flag on the row | nothing | both axes | field only | temperature only |
|---|---:|---:|---:|---:|
| fully fittable | **11** | **1** | 3 | 17 |
| Cohort B only | 1 | 0 | 27 | 0 |
| Cohort A only | 0 | 0 | 0 | 2 |

Two things fall out.

**Thirty-two rows are flagged "fully fittable" and one paper contributes to both
axes.** `1002.0208v2` is the only paper that appears in both fits tables. The
label describes what could in principle be fitted, not what was, and read as a
statement about the cohort it is wrong by a factor of thirty.

**Twelve rows produce no fit at all, and every one of them has both a source
document and an extraction.**

| identifier | temperature rows | isotherms | fields | field rows |
|---|---:|---:|---:|---:|
| `1204.0339v2` | 170 | 5 | 17 | 0 |
| `1003.0946v2` | 158 | 5 | 26 | 0 |
| `1801.05074v1` | 156 | 12 | 13 | 0 |
| `1002.0248v1` | 104 | 7 | 13 | 0 |
| `1802.09868v1` | 99 | 6 | 21 | 0 |
| `2403.19981v1` | 78 | 6 | 13 | 0 |
| `2110.15577v1` | 68 | 4 | 17 | 0 |
| `1109.5479v1` | 57 | 3 | 19 | 0 |
| `1612.02839v1` | 57 | 3 | 19 | 0 |
| `1108.5583v3` | 30 | 3 | 10 | 0 |
| `0904.2442v1` | 20 | 4 | 9 | 0 |
| `10.1016/j.physc.2011.02.004` | 0 | 0 | 0 | 356 |

**1353 extracted rows, from papers the deposit's own provenance table lists as
contributing, that produce no fit and no record of why.** Eleven of the twelve
are flagged fully fittable. Several carry more isotherms and more fields than
papers that do contribute: `1801.05074v1` has twelve isotherms, more than any
paper in the temperature-axis cohort.

Neither fits file records a failure. The temperature file is 260 rows, all
`ok = True` and all `physicality = ok`, so a paper that did not make it is simply
absent rather than recorded as excluded. There is no way, from the deposited
tables alone, to tell a paper that was tried and failed from one that was never
tried.

## Coverage of everything that does contribute

Fifty papers contribute at least one fit.

- 37 have a PDF in this corpus, 13 do not.
- 24 have a pixel trace, 26 do not.
- 13 have neither, and among them are the four MAGLAB records and
  `10.1007/s10854-026-16566-9`, whose twelve passing field-axis fits are the
  third largest block in that cohort.

So a little under half the contributing papers have never been compared against
a figure, and a quarter cannot be, because nothing to compare against is in the
corpus.

## What this changes

Nothing already reported. The census result stands as scored, and the four-paper
set was correctly derived. What it adds is a second, larger question that the
audit had not asked: the cohort as deposited is a subset of the cohort as
declared, the difference is twelve papers and 1353 extracted rows, and the
deposit carries no record of the selection.

Whether those twelve failed a gate, failed to fit, or were never attempted is
not answerable from what is here. It needs the code that built the fits tables,
which is not in this repository.
