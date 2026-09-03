# The temperature-axis cohort is built on a superseded extraction generation

This corrects a claim made earlier in this audit. The round-number values in the
temperature-axis source are not invented. They are the output of the first
extraction pass, which was superseded three times and never merged back.

## The chain

    batch_results_iter1.csv          2026-04-14   first extraction pass
      -> data_agent2/jc_complete.csv 2026-04-27
      -> agent2_dataset.csv -> ... -> agent2_dataset_v3_2_1.csv   2026-04-27
      -> phase_3_p44_post_UCLA_beta_T_fits.csv                    2026-09-02

    scope_z_extraction_outputs       2026-04-30   second pass
    phase_f_vision_extraction_outputs 2026-05-04  third pass
    phase_1_full_extraction_outputs  2026-05-05   fourth pass

The source frozen on 27 April is the one the 414 fits are computed from. The
three later passes are in the same repository, cover 25 of the 31 cohort papers,
and were never merged into it.

## What iteration 1 looks like

For 2012.13723, `batch_results_iter1.csv` holds 56 rows with `compound` set to
`"4 K"`, which is the figure legend rather than a formula, `has_table` False, a
field grid on the integers 0 to 7, and Jc values 1e6, 8e5, 6e5, 5e5, 4e5, 3e5,
2e5, 1.5e5. `agent2_dataset.csv` then matched the string `"4 K"` to Materials
Project entry mp-981, SrF2, with a match score of 100. SrF2 is the substrate.

That is a real reading of a real figure by an early and coarse reader: values to
one or two significant figures sampled on the axis ticks. It is not fabrication,
and describing it that way was wrong.

## What the later passes give, and why they are better

For the same paper and the same figure, all three later passes independently
return 2.2e6 A/cm2 at 4 K and zero field. The paper's own text states "The
self-field Jc at 4 K is as high as 2.2 MA/cm2". A pixel measurement of the
figure (analysis/figure_digitizer.py) gives 1.93e6 at the lowest sampled field
of 0.09 T. Iteration 1 says 1e6.

Across the 10 cohort papers where a later-generation value can be compared with
the iteration-1 maximum, one agrees within 25% and nine differ, with a median
ratio of 0.32. In four of those the later value matches a figure the paper
states in its own text and the iteration-1 value does not:

| paper | iteration 1 | later passes | the paper's own text |
|---|---|---|---|
| 2012.13723 | 1e6 | 2.2e6 | "self-field Jc at 4 K is as high as 2.2 MA/cm2" |
| 1108.0407 | 1e5 | 2.2e4 | "Jc(0) at 1.8 K are about 2.2x10^4 A/cm2" |
| 0907.0147 | 1e6 | 1e5 | "1x10^5 Amp/cm2 at low field and 1.8 K" |
| 1104.0477 | 1e6 | 5.9e4 | figure gives about 4.5e4 self-field for this film |

## What this does and does not fix

It does not rebuild the cohort. The later passes are anchor-level: 110 curve
points in total across 25 papers, one to eight per paper, against roughly 80 to
160 per paper in iteration 1. They can establish that an iteration-1 value is
wrong. They cannot supply the many points per isotherm that a beta_T fit needs.

So the position is: the temperature-axis exponents rest on a source that three
later passes contradict, and the material to replace it does not exist in the
repository at the density required. Either the figures are re-measured
(analysis/figure_digitizer.py), or the temperature-axis result is withdrawn.

## Note on the isotherm-head signature

`analysis/isotherm_head_test.py` separates this source from the named route
completely, and that separation is real. What it detects is the coarse
axis-tick reading of iteration 1, not invention. The test is still the right
screen for finding records that need replacing; the verdict it supports is
"superseded, re-extract", not "fabricated".
