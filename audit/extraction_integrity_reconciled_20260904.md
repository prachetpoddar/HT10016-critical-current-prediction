# The deposit already screened this, and the screen was never acted on

Recorded 2026-09-04. `analysis/reconcile_extraction_integrity.py` writes
`audit/extraction_integrity_reconciled.csv`. Nothing is changed.

## What was already there

`audit/extraction_integrity.csv` screens 50 extracted point sets for the
signatures of a fabricated or misread figure, in its own vocabulary:
`arithmetic` for a ladder of evenly spaced values, `grid_quantized` for values
snapped to a coarse grid, `duplicate_series` for one series copied from
another, `shifted_series` for one series that is another displaced, and
`field_beyond_hc2` for a curve whose fields run past its assigned critical
scale. It reaches FAIL on 15 files and CHECK on 16.

It names, precisely and before any of this session's work, the defects that
were re-derived here from the publisher PDFs:

| paper | verdict | signatures | what was re-derived from the PDF |
|---|---|---|---|
| `mtphys.2022.100783` | FAIL | `duplicate_series shifted_series` | the polycrystal record is a copy of the single crystal, displaced by one rung |
| `physc.2011.05.018` | FAIL | `arithmetic duplicate_series field_beyond_hc2 grid_quantized` | the paper has no critical-current-versus-field figure at all |
| `physc.2009.11.051` | FAIL | `arithmetic grid_quantized shifted_series` | the field axis is in kilo-oersted, recorded as tesla |
| `physc.2010.05.048` | CHECK | `field_beyond_hc2`, round fraction 0.05 | a competent read of a real figure whose field unit is wrong |

The fourth is worth dwelling on: a low round fraction with `field_beyond_hc2`
is exactly the signature of good values on a mislabelled axis, and the screen
graded it CHECK rather than FAIL for that reason.

## What was never done with it

| | files |
|---|---:|
| withdrawn already | 5 |
| never entered the cohort | 11 |
| **still in the analysis** | **15** |

The 15 live files carry:

| | |
|---|---:|
| anchor rows | 37 of 96 |
| field-axis fits | 102 of 159 |
| **passing field-axis fits** | **60 of 94** |
| of which from a FAIL file | 40 |

So the deposit screened its own extractions, found fifteen problems, withdrew
five records on other grounds, and left the rest in.

## A note on how this session reached the same place

The critical-field screen written earlier today flagged seven papers carrying
60 of the 94 passing fits. Two of its three tests were wrong and were retracted,
which cut the defensible flag list to three papers and 36 fits.

The deposit's own extraction screen independently flags **the same seven
papers**, carrying the same 60 passing fits, on entirely different evidence: it
tests the shape of the extracted point sets, not the critical field attached to
them.

That is not vindication of the retracted tests. A wrong test that reaches a
right answer is still a wrong test, and the two that were removed were removed
for good reasons: they compared the fit against an unfiltered extraction the
pipeline had already filtered, and they read a zero-temperature extrapolation
as an unused larger value. But it does mean the seven-paper set is not an
artefact of those errors, because a screen that predates them and works on
different evidence selects it too.

## What this leaves to decide

Fifteen flagged files are live. Ten are FAIL and carry 40 of the 94 passing
field-axis fits; five are CHECK and carry 20 more. Four of the fifteen have
been read at source this session and every one of the four turned out to be
what its signature said.

The remaining eleven have not been read. That is the cheapest way to find out
whether the screen's precision holds at four out of four or falls off, and it
is the question on which the disposition of 60 passing fits and 37 anchor rows
should turn.
