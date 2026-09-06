# Hossain's submission-readiness actions, and their disposition

Recorded 2026-09-06 from `HT10016_v34_Submission_Readiness_Actions.docx`, which
arrived by upload and is not in this repository. The list is written down here
because it very nearly was not: the upload is no longer reachable from the
working session, and four of its items had only a one-line paraphrase left.

Worked in the order given, one at a time.

## A, the data and consistency items

| item | action | status |
|---|---|---|
| A1 | One validation status, propagated everywhere it is stated | done, `2350a98` |
| A2 | Rebuild Fig. 3 and the headline sample-form statistics from the repaired anchor cohort | done, `710c57c` |
| A3 | Make the refusal claim consistent | done, `3da9255` |
| A4 | Remove stale candidate accounting from Supplement Secs. 9, 10, 12 and Table S6 | done, `17efd64` |
| A5 | Fix the public generator so the released prediction file reproduces exactly | done, `301a91c` |
| A6 | Revise the response after the data freeze | done, `9a7485b` |

## B, the writing items

| item | action | status |
|---|---|---|
| B1 | Predictive scope as the central idea | NOT DONE, see below |
| B2 | Title change | the authors' decision, not taken here |
| B3 | Four-step abstract | NOT DONE, see below |
| B4 | Move the unseen-paper result earlier | done, `2026-09-06` |
| B5 | Version history out of the manuscript, limitations stay | done, `e15acef` |
| B6 | Transitions | NOT DONE, see below |
| B7 | Letter 25 to 30% shorter, concern to test to change to surviving claim | done at 21.9%, `c869e4a` |

## Why B1, B3 and B6 are not done

Each is a change of framing rather than of fact, and the only record of what was
asked is a one-line paraphrase: "predictive scope as the central idea", "four-step
abstract", "transitions". Executing a framing instruction from a paraphrase means
guessing at the senior author's intent on the three items where intent is the
whole content. They are left for the source document to be supplied again.

B4 was executable from its paraphrase because it names a specific result and a
specific move, and both are checkable against the deposit.

## What B4 turned up

The source-paper holdout is the paper's most direct measurement of the
heterogeneity the framework exists for, and it sat in the last sentence of the
functional-form comparison in Sec. II.C. It is now in the abstract and in
Sec. I as well.

Checking it before promoting it found two defects in the response letter.

The within-compound range was given as 0.32 to 0.45 dex.
`audit/functional_form_comparison.csv` gives, on the current cohort, 0.472,
0.322 and 0.323 under a point-level split and 0.504, 0.388 and 0.367 under a
curve-level split. The range is 0.32 to 0.39 across the two forms that are not
withdrawn and 0.32 to 0.50 across all three. The 0.45 reproduces from nothing.

The gap was called "a factor of eight in critical current between predicting an
unseen measurement and predicting an unseen paper". Eight is the unseen-paper
error expressed as a factor, 10 to the 0.900, not the ratio between the two
regimes, which is 10 to the 0.578, about four. Both are corrected, and the
manuscript now prints the three paper-split values, 0.903, 0.900 and 0.949, so
a reader can form either quantity.
