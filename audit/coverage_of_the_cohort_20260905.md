# What happened to the rest of the papers

Recorded 2026-09-05, and **corrected the same day after the pipeline author
pointed out that the papers exist upstream.** The first version of this note
said twelve papers produce no fit and no record of why. There is a record, in
this repository, in ledgers this audit wrote itself, and the script did not look
at them. The retraction is below and the correct accounting with it.

Script `analysis/coverage_map.py`, table `audit/coverage_map.csv`.

## Retraction

I reported that twelve rows of the provenance table produce no fit in either
table and that "the deposit carries no record of the selection". Every one of
the twelve is accounted for:

| disposition | rows |
|---|---:|
| withdrawn, with a citation, the figure checked and a reason, in `audit/withdrawn_beta_T_papers.csv` | 11 |
| duplicate identifier of a paper that does contribute, in `audit/duplicate_papers.csv` | 1 |

The eleven were withdrawn on 2026-09-03 for defects each recorded in full: axes
in A/m2 read as A/cm2, field axes that are log-tick ladders, isotherms that are
exact arithmetic ramps, a record interleaving two series three orders of
magnitude apart, and a compound filed under the wrong substructure. The twelfth,
`10.1016/j.physc.2011.02.004`, is Physica C 471 (2011) 215, which is arXiv
`1002.0208`, and it contributes under the arXiv key.

The standing rule for this project is that a claim of missing or defective data
is rechecked against the whole repository before it is reported. I did not
follow it. `coverage_map.py` now joins the withdrawal and duplicate ledgers and
refuses to call a row unaccounted for without checking them.

## The funnel, reconstructed from the pipeline's own code

The generator is
`phase_3_p44_cohort_A_post_UCLA_consolidation.py`. Its selection rules are:

1. iron-bearing compounds only, `stoich_Fe > 0`
2. `Jc > 0` and `T/Tc` in `[0, 0.7)`
3. group by paper, compound and field; keep groups with at least three distinct
   temperatures
4. `physicality = ok` when `-5 < beta_T < 15`

Applying those rules to `agent2_dataset_v3_2_1.csv`:

| stage | rows | papers |
|---|---:|---:|
| candidate PDFs in `_jc_screen/mine_pdf_list.txt` | | 2596 |
| extracted Jc points | 6574 | 80 |
| iron-bearing | 3400 | 43 |
| valid for beta_T, T/Tc below 0.7 | 2853 | 43 |
| groups with at least three isotherms at one field | 412 fits | 29 |

The pipeline's own output file adds the Cohort A extension and two Elsevier
records and holds **419 fits over 33 papers**. Every deposited paper's fit count
reproduces exactly under these rules, so the reconstruction is right.

## Where the 419 becomes 260

| | fits | papers |
|---|---:|---:|
| the pipeline's `phase_3_p44_post_UCLA_beta_T_fits.csv` | 419 | 33 |
| withdrawn in `audit/withdrawn_beta_T_papers.csv` (2026-09-03) | -154 | -11 |
| withdrawn in `audit/withdrawn_records.csv` (2026-09-01) | -5 | -2 |
| **the copy in this repository** | **260** | **20** |

The arithmetic closes exactly. The repository's copy is the post-withdrawal
cohort, and the withdrawals are this audit's own, not the pipeline's.

## What is still true, and it is smaller

**The provenance table was not updated when the withdrawals were made.** It
still lists all eleven withdrawn papers as contributing, and flags them "fully
fittable". Anyone reading `data/provenance_table_fitcohort_full.csv` as the
cohort definition gets 62 papers where 50 contribute and 11 were removed for
cause.

**"Fully fittable" does not mean what it says.** Thirty-two rows carry that flag
and exactly one paper, `1002.0208v2`, contributes to both axes. The label
describes what could in principle be fitted, not what was.

**The Tc anchor is a hardcoded dictionary, confirmed at source.** The generator
carries `TC_LOOKUP`, a per-compound constant table with per-substructure
defaults for anything not in it: `Ba(FeAs)2` 38.0, `Fe2TeSe` 14.5, `Sm2FeAs2O`
55.0, `Pr2FeAs2O` 51.0, falling back to 38.0 for any unlisted 122 and 50.0 for
any unlisted 1111. This is the mechanism behind
`audit/tc_anchor_not_paper_reported_20260905.md`, now visible in the code rather
than inferred from the values.

**No failure is recorded at the point of selection.** A group with fewer than
three isotherms is skipped with a bare `continue`, so it leaves no row.
`physicality` records `beta_extreme`, and no fit in the file carries it, so the
only silent drop is the isotherm-count rule. That is a small point next to what
I claimed, but it is the true version of it.

## Coverage of what does contribute

Fifty papers contribute at least one fit. Thirty-seven have a PDF in this
corpus, twenty-four have a pixel trace, and thirteen have neither, among them
`10.1007/s10854-026-16566-9`, whose twelve passing field-axis fits are the third
largest block in that cohort. So a little under half the contributing papers
have never been compared against a figure, and a quarter cannot be from what is
here. That part of the first version stands.
