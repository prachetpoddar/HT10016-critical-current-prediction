# The repaired cohort, put into the documents

Recorded 2026-09-05. Script `analysis/apply_repaired_cohort_edits.py`. Outputs
`HT10016_revised_repaired.docx`, `SUPPLEMENTAL_MATERIAL_revised_repaired.docx`
and `RESPONSE_TO_REFEREES_repaired.docx`, built from the `_final` versions of
2026-09-04.

Twelve edits, every one located, and the script refuses to write if any target
is missing.

## Applied

**Table I**, six cells:

| row | was | now |
|---|---:|---:|
| papers contributing fitted curves | 62 | 50 |
| distinct compounds with fitted curves | 38 | 35 |
| critical-current data points extracted | 4146 | 3303 |
| temperature-axis partial fits | 260 | 257 |
| field-axis partial fits passing | 94 | 52 |
| field-axis source papers | 16 | 12 |

**Prose that repeats those counts**: the abstract, the Fig. 1 caption, Sec. 11
of the supplement, the Table S1 caption, and the Table I ladder in the response.

**The disclosure**, nineteen paragraphs, inserted into the response after the
paragraph on the attempted rebuild of the critical scale.

## Not applied, and why

A number quoted beside a statistic computed on that cohort is not renumbered.
Changing 94 to 52 next to a median computed over the 94 would put the documents
back into the state this exercise exists to get them out of. Seven passages are
in that class and the script locates each on every run:

| document | passage | what has to happen |
|---|---|---|
| main text | "Using the 260 temperature-axis fits" | per-family counts and bootstrap fractions recomputed on 257 |
| main text | "the 260-fit temperature-exponent cohort contains no MgB2 fits" | true at 257, but the number moves with the above |
| main text, supplement, response | "15 of 94 curves" exceeding 0.9 | the scale audit's ratio statistic re-run on 52 |
| supplement | "1.158 over 94 fits from the same 16 papers" | a pooled median and bootstrap interval, both move |
| supplement | "the 23 compounds whose per-compound aggregate Form 3 fit converges" | re-derived, see below |

**The 23 needs re-deriving, not renumbering.** The supplement defines it as the
compounds whose per-compound aggregate Form 3 fit converges. That fit is
computed by `run_closed_form_fits.py` on `agent2_dataset_v3_2_1.csv`, which
still contains all eleven withdrawn papers, so the count is drawn from data the
audit removed. The Table I row carrying it is left untouched until it is
recomputed, which is why Table I has one row still on the old cohort.

That is a known inconsistency and it is recorded here rather than hidden. Row 5
of Table I does not yet belong with rows 2, 3, 4, 6 and 7.

## What the three documents are, and are not

They carry the corrected census and the disclosure. They are not finished. Seven
statistics have to be recomputed and written in before anything is sent, and one
Table I row is still on the pre-withdrawal cohort.
