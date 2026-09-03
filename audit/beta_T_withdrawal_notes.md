# Temperature-axis withdrawal, 2026-09-03: what the recomputed numbers can and cannot support

Eleven of the 31 source papers behind the temperature-axis cohort were withdrawn
after their deposited Jc series were checked against the source figures. The
register is `audit/withdrawn_beta_T_papers.csv`; the screen that ranked them is
`audit/extraction_integrity_beta_T_cohort.csv`. This note records the three
things a reader needs in order not to over-read the result.

## 1. The recomputation is provisional, and in a direction that flatters

| | before | after |
|---|---|---|
| fits | 414 | 260 |
| papers | 31 | 20 |
| pooled median beta_T | 1.234 | 1.463 |

| family | fits | papers | compounds | median beta_T |
|---|---|---|---|---|
| iron_chalcogenide_11 | 102 -> 89 | 9 -> 8 | 5 -> 5 | 0.936 -> 0.886 |
| iron_pnictide_111 | 21 -> 11 | 2 -> 1 | 1 -> 1 | 1.170 -> 1.512 |
| iron_pnictide_1111 | 76 -> 54 | 6 -> 4 | 4 -> 3 | 2.135 -> 2.346 |
| iron_pnictide_122 | 215 -> 106 | 14 -> 7 | 4 -> 2 | 1.331 -> 1.850 |

Leave-one-compound-out MAE on the temperature axis: chalcogenide 0.962 -> 0.588,
1111-type 1.721 -> 3.120, 122-type 1.118 -> 1.314. Two of the three families got
worse. The 122-type family drops to two compounds and the 111-type to one, so
neither can support a compound hold-out any more; the sensitivity table records
those as refused.

## 2. The screen is not independent of beta_T, so the improvement is not evidence

The signature the screen fires on is a shape in Jc(T, H). That shape maps onto a
particular beta_T, so selecting records by the screen selects on the outcome
variable. It does, in every family, and in opposite directions:

| family | median beta_T withdrawn | median beta_T retained |
|---|---|---|
| iron_chalcogenide_11 | 3.809 (n=13) | 0.886 (n=89) |
| iron_pnictide_111 | 0.609 (n=10) | 1.512 (n=11) |
| iron_pnictide_1111 | 0.190 (n=22) | 2.346 (n=54) |
| iron_pnictide_122 | 0.891 (n=109) | 1.850 (n=106) |

The chalcogenide MAE is the clearest case and must not be reported as a result.
Its move from 0.962 to 0.588 is one paper. Leave-one-paper-out leverage on the
pre-withdrawal value:

    drop 1002.0248v1.pdf   (withdrawn)  -13 fits -> 0.5881
    drop jallcom.2022.165358             -1      -> 0.9698
    drop mtcomm.2022.103433              -1      -> 0.9723
    drop 2511.19058v1.pdf               -19      -> 0.9776
    drop 0907.0147v2.pdf                -14      -> 0.9919
    drop 1611.08455v1.pdf               -15      -> 0.9990
    drop 1104.0477v2.pdf                -19      -> 1.0292
    drop 1111.3923v1.pdf                 -9      -> 1.0517
    drop 1108.0407v1.pdf                -11      -> 1.0594

Every retained paper either barely moves the metric or makes it worse. All of
the improvement is the removal of `1002.0248`, whose beta_T runs 3.658 to 3.994
against a family range of 0.163 to 1.881. Removing the only record capable of
producing a large residual narrows the bootstrap until it cannot produce a
failing resample: after the withdrawal the chalcogenide resample MAE spans 0.11
to 1.23 and 100% clears the threshold. That is a less informative interval, not
a stronger pass.

## 3. The cohort is not clean, and the deletion is selective

Running `audit_extraction_integrity.py` over the 29 arXiv papers of the original
cohort gives 9 FAIL, 18 CHECK, 2 PASS. All nine FAIL papers are now withdrawn,
along with two that the screen only marked CHECK. That leaves **16 CHECK papers
that nobody has read**, and three of the three CHECK papers that were read came
back unusable. The honest prior is that a substantial fraction of the surviving
20 papers is also unusable.

Because the deletion is selective on a quantity correlated with beta_T, and
because it has been applied to one tail of each family and not the other, every
median, residual and interval in the "after" column is biased by an unknown
amount and an unknown sign. The numbers above are reported so that both arms are
visible, not because the post-withdrawal arm is trustworthy.

## 4. Known-stale and known-failing, not yet fixed

- `data/phase_3_p57_de_novo_predictions.csv` and everything derived from it
  (`data/family_params.json`, Figure 5) are computed from a beta_T pool built
  directly from the fit table and have **not** been regenerated. The pool moved:
  chalcogenide n=102 mean 1.186 -> n=89 mean 0.803, 122-type n=215 mean 1.691 ->
  n=106 mean higher. `3DSC_MP.csv` is not in the deposit, so p56 and p57 cannot
  be regenerated from the repository as it stands.
- Three compounds left the fit table entirely: BaFeAs2Ru, KBa(FeAs)4,
  Nd2FeAs2O. `phase_3_p56` treats "not in the canonical fits" as a de-novo
  candidate, so the pipeline would now propose predicting compounds whose
  records were just withdrawn. The `KBa(FeAs)4` entry in
  `analysis/reclassify_records.py` is now vacuous.
- `analysis/verify_deposit.py` FAILS: it asserts 414 temperature-axis fits
  against the manuscript and the deposit now holds 260. The manuscript constant
  must not be edited to match until the manuscript itself is updated; the gate is
  working as intended.
- `README.md` still reports 419 for this file and is stale on several rows.
- `temperature_axis_summary.py` writes nothing without `--json`, so Table S10 has
  no deposited counterpart and no check catches drift. The chalcogenide value it
  reports has now moved 0.261 -> 0.962 -> 0.588 across three changes and nothing
  in the deposit records that history.
