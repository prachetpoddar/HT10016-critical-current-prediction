# Pre-registration: the field-axis census

Written **before** any of the six papers below was traced, and committed on its
own so the record shows it was fixed in advance.

## Why this is pre-registered

The stage C comparison failed on selection, not on arithmetic. Its six scorable
papers were not sampled: every trace in `data/reextraction` had been built as
remediation for a paper already under suspicion, and four of the six were
established as defective before they were traced. No result from such a set can
be read as a rate.

The remedy proposed was a random sample of the untraced papers. On enumeration
there is no need to sample: **there are exactly ten untraced papers among the
sixteen that pass both deposited gates, and six of them have a PDF in the
corpus.** So this is a census of what can be checked, not a draw from it, and
the only way it can go wrong is if a paper is dropped after its answer is known.
That is what this file exists to prevent.

## The complete target list, fixed now

Every paper below will be traced and every one will be reported, whatever it
shows. None will be dropped for being awkward, and none will be added.

| paper | compound | passing fits | temperatures (K) | Hc2 used (T) | Hc2 provenance |
|---|---|---:|---|---:|---|
| elsevier_10.1016_j.physc.2009.05.098 | SmFeAsO0.8F0.2 | 8 | 2, 5, 10, 15, 20, 25, 30, 35 | 86.00 | Tier 3 literature default |
| elsevier_10.1016_j.physc.2009.11.051 | Ba(Fe0.93Co0.07)2As2 | 8 | 2, 10, 15, 20 | 4.75 | Tier 1 direct match at 2.0 K, term Hc2 |
| elsevier_10.1016_j.physc.2010.05.048 | FeTeSe | 8 | 2, 3, 4, 5, 6, 7, 8, 9 | 4.75 | Tier 1 direct match at 2.0 K, term ambiguous |
| elsevier_10.1016_j.physc.2013.04.060 | MgB(2-x)Cx x=0.0386 | 8 | 4.2, 10 | 11.90 | Tier 1 direct match at 4.2 K, term Hirr/Birr |
| elsevier_10.1016_j.jallcom.2023.170146 | MgB2 | 6 | 10, 15, 20, 25, 30, 35 | 2.75 | Tier 1 direct match at 10.0 K, term Hirr/Birr |
| elsevier_10.1016_j.matchemphys.2023.128348 | MgB2 | 4 | 20 | 3.00 | Tier 1 direct match at 20.0 K, term Hirr/Birr |

Six papers, **42 of the 46 untraced passing fits**.

PDFs are at
`/mnt/user-data/uploads/SuperconductorWorkflow/kappa_pipeline/analysis/v3_2_9_path_2_prep/phase_3_p19_elsevier_pdfs/`
except `physc.2009.05.098`, which is also in `pdfs_for_page_review`.

## What cannot be assessed, recorded now rather than later

Four passing papers are MAGLAB records: `MAGLAB_11_6K`, `MAGLAB_Ni122_4_2K`,
`MAGLAB_P122_4_2K`, `MAGLAB_Sm1111_4_2K`. One fit each, four fits in total. No
source document for any of them exists anywhere in the corpus, so no figure can
be compared. They are unassessable and will be reported as such, not quietly
excluded.

## The scoring rule, fixed now

Unchanged from `analysis/adjudicate_field_axis.py` as committed at `6caeaea`:

1. For each passing fit, refit `log10 Jc = log10 Jc,partial + beta_H * log10(1 - H/Hc2)`
   from the traced figure at the same temperature, under the **same** `Hc2_T_used`,
   over points with H strictly below Hc2.
2. The primary statistic is the **per-fit** median of |log(deposited/figure)|.
   The per-paper median is reported alongside; it is not the headline, because
   aggregating first lets a paper with twelve fits count the same as one with two.
3. The paper is the independent unit for any significance test.
4. Where a figure plots several specimens or panels, each deposited
   `sample_identifier` is matched to its own series or panel. Pooling them was a
   stage C defect and is not repeated.
5. A fit is reported as unscorable, with the reason, when the figure does not
   plot its temperature, when its `Hc2` leaves under 0.05 dex of lever in
   `log10(1 - H/Hc2)`, or when the traced isotherm has fewer than four points
   below `Hc2`.

## The comparison this is for

Stage C found the six previously traced papers a median 0.639 in log from their
figures against the temperature axis's 0.880, Mann-Whitney p = 0.133 — not
distinguishable, on a set chosen for suspicion. The census asks the same
question on a set chosen by nothing.

Committed before tracing.
