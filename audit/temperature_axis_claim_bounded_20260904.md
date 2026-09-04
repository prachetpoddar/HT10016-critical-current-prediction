# "All 260" was wrong. What the evidence actually supports.

Recorded 2026-09-04, after the claim that all 260 temperature-axis fits come
from generated extractions was challenged as another overclaim. The challenge
was right on the count and on the missing link. The verdict survives, on
stronger ground than it was first put.

## The correction

**"All 260" is wrong.** 258 of the 260 fits come from the eighteen arXiv papers
that were opened. The other **two come from Elsevier files I never examined**
and simply asserted over. Those two are `jallcom.2022.165358` and
`mtcomm.2022.103433`, each contributing a single fit and each carrying a
different `source` value in the fit table that I did not read.

Since then, `jallcom.2022.165358` has been opened. Fig. 7(a) plots Jc against
H in tesla, 0 to 9 T, at 4, 6, 8, 10, 11, 12 and 13 K. At the extraction's field
of 2 T the figure reads about 9e4 at 4 K and about 10 at 12 K; the extraction
records 12000 and 1500. It is defective, and its recorded 14 K series does not
exist on the page. `mtcomm.2022.103433` has no PDF in the corpus and **cannot be
checked**.

Corrected: **259 of 260 fits rest on extractions demonstrated defective; one
cannot be assessed.**

## The link that had been skipped

The same omission that invalidated the field-axis claim two days ago: nothing had
verified that the deposited fits were computed from the data the audits graded.

`analysis/reconcile_temperature_axis.py` now checks it. For every fit row it
refits beta_T from the wide file, restricted to that row's own recorded
temperature window, and requires both the slope and the point count to match.

| | fits |
|---|---:|
| reproduced exactly | **257** |
| not reproduced | 1 (`1502.05345v1` at 34 T) |
| paper absent from the wide file | 2 (the Elsevier pair above) |

The audits were pointed at the right data.

## The verdict does not rest on the figure readings alone

The first report leaned on eighteen separate readings of eighteen figures. Three
properties of the source need no figure and no judgement:

| property | papers |
|---|---|
| every Jc value at two significant figures or fewer | **17 of 18** |
| every isotherm on one identical field grid | 16 of 18 |
| **every isotherm terminating at the same field** | **18 of 18** |

The third is the strongest. A measured isotherm ends where Jc falls into the
noise, and that field is lower the higher the temperature; the figures in these
papers show exactly that, with 20 K curves dying at a quarter of the field the
2 K curves reach. All eighteen extractions have every isotherm ending at the
same field.

The two papers where roundness does not fire were checked separately rather than
excused. `1502.05345v1` is not round, but three of its five series follow
Jc = J0 x 2^(-H/2) to within **0.021 dex over 34 T**, consecutive ratios 1.9947
with a standard deviation of 0.031. `0806.2839v1` has two field grids, and its
2 K and 20 K series have identical consecutive-ratio statistics, mean 1.2662 and
standard deviation 0.1386 in both, which is one shape rescaled.

## What stands

- The claim of scope was wrong by two fits and is corrected.
- The chain from fits to graded data is now verified rather than assumed.
- The fabrication verdict is supported by the data's own structure independently
  of any figure reading, and by fourteen papers whose own text contradicts their
  extraction.

The pattern worth naming: this is the third time in this session that a count was
stated more broadly than the evidence supported, and the second time the missing
piece was the link between a deposited fit and the extraction behind it. The
check now exists as a script rather than as an intention.
