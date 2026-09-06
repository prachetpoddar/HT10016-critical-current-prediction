# The two field-axis candidates, checked against the whole repository

Recorded 2026-09-06. Both were reported earlier as new withdrawal candidates
on the strength of the Table II input alone. A full repository pass changes
both findings, and turns up a third that matters more than either.

## Fe9Se8, source 1108.0407v1: retracted, this is a known and repaired defect

The finding as reported was that the source carries 88 rows running 0 to
0.005 T against a literature critical field of 8 T, giving a fitted field
exponent of 3408, and that it is not in the withdrawal ledger.

The repository already holds the diagnosis, in
`audit/cohortA_all_eighteen_read_20260904.md`:

> `1108.0407v1` | 11 | printed axis 0 to 50 kOe, extraction 0 to 0.005 T,
> exactly 1000x too small

and the repair, in `audit/temperature_axis_adjudicated_20260905.md`, which
records the field range moving from 5e-4 to 5e-3 T to 0.04 to 5 T. The
reextracted point file `data/reextraction/1108_0407v1_fig5d_points.csv` carries
299 points running 0.0400 to 4.993 T, and the eleven Fe9Se8 rows in the current
repaired temperature-axis cohort all carry `reproduced = True` against it.

So the defect was found, diagnosed to the factor, and fixed. Nothing about the
current cohorts needs to change and no withdrawal is warranted. What is true is
narrower: Table II's input predates the repair and holds the source in its
defective form.

## HfRe2, source 2205.06500v1: narrowed, and it was never screened

The source carries 128 rows whose field runs 1e-6 to 1e-5 T against a
literature critical field of 10 T, so the largest reduced field in the compound
is 1e-6, and the published Table II fit gives it a field exponent of 2.87e6.

A full pass finds it in only two places: `data/caption_sweep.csv`, the
retrieval corpus, where it scores zero on every family flag, and the Table II
input. It is in no fit cohort, no provenance table, and no audit disposition.
It was never opened and never screened, so this is one reading of one deposited
column and nothing else. Its signature matches the class the screen found in
every one of the eighteen it read, `1002.0208v2` most closely, whose "field
column spans 1e-6 to 1.6e-3 T; the printed axis is 0 to 16 T". That is a reason
to read the source, not a finding. Until the figure is compared against the
extraction, the defensible statement is that Table II's cohort contains at
least one source carrying the signature of a defect class that the screen
confirmed in every case it examined.

## What the pass turned up instead

None of the eighteen sources that failed the read is in the withdrawal ledger,
and all eighteen are in the Table II input. The project's answer to them was
reextraction rather than withdrawal, and fourteen carry a repaired point file
under `data/reextraction`. Table II's input is the pre-reextraction dataset, so
it holds all eighteen in the form the screen rejected, and the "withdrawals
removed" rerun beside it removes eleven different papers and leaves the
eighteen untouched.

The comparison was therefore rerun a third time with the eighteen removed:
4975 rows, 62 sources, 24 compounds. The conclusions are unchanged and are
sharper.

| cohort | split | Form 1 | Form 2 | Form 3 | n | 3 over 2 | 3 over 1 |
|---|---|---:|---:|---:|---:|---|---|
| withdrawals removed | point | 0.508 | 0.513 | 0.484 | 15 | 11/15, p 0.118 | 14/15, p 0.001 |
| screen-failed removed | point | 0.491 | 0.369 | 0.286 | 16 | 11/16, p 0.210 | 14/16, p 0.004 |
| screen-failed removed | curve | 0.619 | 0.544 | 0.493 | 15 | 11/15, p 0.118 | 14/15, p 0.001 |
| screen-failed removed | source | 1.173 | 1.144 | 1.097 | 7 | 6/7, p 0.125 | 5/7, p 0.453 |

Form 3 beats Form 1 on every cohort and both fine-grained splits, at
probabilities between 0.001 and 0.004. Form 3 does not separate from Form 2 on
any of them. No form reaches a median below 1.09 dex under a source holdout.
The section's claim as rewritten in v24 holds on all three cohorts.

The third cohort is now a permanent arm of
`analysis/functional_form_comparison.py`, with the eighteen listed explicitly
and two assertions: every one of them must be present in the input, and the
set must stay disjoint from the withdrawal ledger.

## What still needs doing

Read `2205.06500v1` against its printed figure. It is the only outstanding
question here, and it touches Table II alone.
