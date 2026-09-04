# The temperature axis was never screened, and the first paper opened is bad

Recorded 2026-09-04. Found by following the CSVs in the upstream tree that name
PDFs. Nothing in the data changed.

## What the CSV search turned up

Five files in the upstream tree carry PDF names. Four are worklists that map a
filename to a DOI. The fifth,
`data_agent2/agent2_dataset_v3_2_1.csv`, is different: 6574 extracted points
across 80 arXiv preprints, each row carrying its `pdf_name` and page.

That corpus is not the one this session has been auditing. Every integrity check
in this repository, and every source reading of the last two days, has been
aimed at Cohort B, the Elsevier and Springer papers behind the **field-axis**
fits. The arXiv corpus feeds `data/phase_3_p44_post_UCLA_beta_T_fits.csv`: **260
temperature-axis fits across 20 papers**, 18 of them arXiv, and every one of the
260 is marked `ok`.

Because those points live in one wide file rather than per-paper long tables,
the screen that found the Cohort B defects was never pointed at them.
`analysis/screen_cohort_a.py` now points it at them.

## What the screen says

| verdict | papers | temperature-axis fits |
|---|---:|---:|
| CHECK | 16 | **221** |
| PASS | 2 | 37 |

Fifteen of the sixteen CHECKs are flagged on round-number fraction alone, which
this screen's own documentation calls "a flag and not a finding". Round
fractions run from 0.54 to 0.91. For comparison, the Cohort B files that turned
out to be fabricated ran 0.17 to 0.93, so the profile is similar but that is
suggestive rather than conclusive.

One paper carries a real signature.

## `1903.00866v2`, opened, and it is fabricated

Pyon, Takahashi, Veshchunov, Tamegai et al., *Large and significantly
anisotropic critical current density induced by planar defects in CaKFe4As4
single crystals*. Twenty-one of the 260 fits. Flagged `non_monotonic` on seven
of seven series.

Fig. 4 plots Jc in A/cm2 on a log axis against **H in kilo-oersted**, 0 to 50,
at 2, 5, 10, 15, 20, 25 and 30 K. The extraction's field axis is right: it runs
0 to 5.00, which is the printed 0 to 50 kOe correctly converted. The values are
not.

| | extraction | Fig. 4 |
|---|---|---|
| heads, 2 K down to 30 K | 1e6, 8e5, 6e5, 5e5, 4e5, 3e5, 2e5 | about 3e6, 1.5e6, 1.05e6, 7e5, 6e5, 5e5, 3e5 |
| tails at the far field | 5e5, 4e5, 3e5, 2e5, 1e5, 1e4, 1e3 | all between about 7e4 and 1.6e5 |

Three things give it away. The heads are a round arithmetic ladder. The tails
span three decades where the printed curves span a factor of two. And the
extracted curves form a clean fan that never crosses, where the printed 25 K
curve ends above the printed 10 K one.

This is the same shape of defect as the Cohort B fabrications, on a different
corpus, feeding a different axis of the paper.

## What this does and does not establish

It establishes that the temperature-axis corpus was never screened, that
screening it flags 221 of its 260 fits for a look, and that the first paper
opened is fabricated.

It does not establish that the other fifteen are. They carry no signature beyond
a high round fraction, and the two Cohort B papers that turned out sound
(`matchemphys.2023.128348` and `jallcom.2023.170384`) also had high round
fractions. Those fifteen have to be opened, and their PDFs are on disk.

One caveat on the screen itself: the wide file carries no sample-form or
sample-id column, so the series here are grouped by compound and temperature.
The duplicate and shifted tests therefore see a different grouping than they
would on a native long table. The round-fraction and arithmetic tests do not
depend on it.
