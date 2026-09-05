# The provenance table, brought into line with the withdrawals

Recorded 2026-09-05. Script `analysis/apply_provenance_status.py`, snapshot in
`audit/pre_provenance_status_20260905/`.

`data/provenance_table_fitcohort_full.csv` is the cohort definition, 62 rows,
one per paper the deposit says contributes. Eleven of those papers were
withdrawn on 2026-09-03 with a citation, the figure checked and a reason each.
The table was never updated. No row is deleted here; four columns are added and
one is corrected, so the pre-withdrawal state stays visible.

| new column | what it holds |
|---|---|
| `status` | contributing or withdrawn |
| `withdrawn_on`, `withdrawn_reason_ref` | the date and where the reason is written |
| `contributes` | what the row actually produces |
| `second_identifier_for_the_same_paper` | true for the one row that names a paper another row already names |
| `contribution_flag_original` | the flag the manuscript was written against, preserved |

## What the rows actually contribute

| | rows |
|---|---:|
| field axis only | 30 |
| temperature axis only | 19 |
| **withdrawn** | **11** |
| a second identifier for `1002.0208v2` | 1 |
| both axes | 1 |

Thirty-two rows carried the flag "fully fittable". Of those, seventeen
contribute to the temperature axis only, three to the field axis only, one to
both, and eleven are withdrawn. The flag describes what could in principle be
fitted, not what was.

## This is not only bookkeeping

`analysis/verify_deposit.py` computes three of the manuscript's printed counts
straight from this table. All three are pre-withdrawal:

| quantity | printed | correct |
|---|---:|---:|
| fitted curve papers | 62 | **50** |
| fitted curve compounds | 38 | **35** |
| extracted points | 4146 | **3303** |

The extracted-point count is overstated by 843, a fifth of what the manuscript
claims. The paper count includes eleven papers the audit removed for cause and
one identifier counted twice.

The fifty-one contributing rows describe fifty distinct papers: one paper holds
two rows, one per axis, and both are real extractions, so its points count once
each and its paper counts once.

`verify_deposit.py` now prints this table on every run. Its existing checks
still compare the deposit as published against the manuscript as written, so
they still pass; what the new block says is that both need editing, in the same
place, by the same amounts.

## What was fixed while doing it

The duplicate ledger spells the field-axis identifier with its `elsevier_`
prefix and the provenance table does not, so an equality test never fired and
`10.1016/j.physc.2011.02.004` was being counted as a paper in its own right
alongside `1002.0208v2`, which is the same paper, Physica C 471 (2011) 215. The
match is now a substring test and the row is marked rather than dropped, because
its extraction is real and its points belong in the total.
