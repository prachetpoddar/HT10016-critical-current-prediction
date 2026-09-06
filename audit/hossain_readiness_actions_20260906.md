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
| B1 | Predictive scope as the central idea | done |
| B2 | Title change | the authors' decision, see below |
| B3 | Four-step abstract | done |
| B4 | Move the unseen-paper result earlier | done, `c484a56` |
| B5 | Version history out of the manuscript, limitations stay | done, `e15acef` |
| B6 | Transitions | done |
| B7 | Letter 25 to 30% shorter, concern to test to change to surviving claim | done at 21.9%, `c869e4a` |

The source document was supplied again on 2026-09-06 and B1, B3 and B6 were
worked from its actual text rather than from the paraphrase. The full text is
transcribed below so this cannot happen a third time.

## B2, the title

The suggestion is "Determining Predictive Scope for Superconducting Critical
Current from Heterogeneous Literature", with the instruction to keep the current
prediction-focused title only if the final validation matrix supports that
wording. It does not. The matrix says no family carries a validated field axis,
the one family that emits is not assessable on the axis where the test can be
run, and the framework's output is a scope decision rather than a per-compound
prediction. On the paper's own evidence the suggested title is the better
supported one. The choice is the authors' and has not been made here.

## What the actual text asked for that the paraphrase did not carry

B3 asks for the stale conditioning ratios to come out of the abstract. The
deposited-anchor comparison, 37%, 49% and 12%, is now given only in Table III
and Sec. III.A, where both cohorts belong; the abstract gives the repaired
81%, 37% and 4% once, with the confounding qualification A2 asks to keep.

B1 has two halves and only one was in the paper: which measurements may be
compared, and whether the scale that normalizes them was measured on the same
specimen. The second is what the critical-field provenance audit of Sec. III.F
is about. Sec. I now states both and Sec. III.F opens by pointing back, so the
audit reads as part of the result rather than as an apology for it.

A6 asks for the source-paper holdout to be stated with its scope. The letter
still headed it "Nothing generalizes across source papers", which is broader
than eight compounds support, and now uses the scoped wording the actions
document supplies.

A3's done-when was checked rather than assumed. The manuscript states in
Sec. III.E, and again in the limitation that follows it, that no dispatched
field-axis output is offered as a validated prediction.

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

## The actions document, transcribed

Transcribed 2026-09-06 from `HT10016_v34_Submission_Readiness_Actions.docx`,
which is not in the repository and was reachable only through an upload.

HT10016 v34: Submission-Readiness Actions

A. Must implement before resubmission

1. Establish one validation-status matrix and use it everywhere.

Verified issue: The manuscript currently gives incompatible validation statements. Table III says the field axis is not validated at family level, MgB₂-class is not assessable on the main temperature-axis LOCO test, and the independently rebuilt temperature exponents no longer clear the screening threshold. Section III.E nevertheless says 11-type, 122-type, and MgB₂-class all carry a validated temperature axis, while Table IV labels 11-type “Temperature and field” and 122-type/MgB₂-class “Field only.” The abstract and conclusion also refer to “three validated substructure families.”

Action: Create one final family-by-axis validation table directly from the final analysis, then propagate that exact status to the abstract, Table III, Sec. III.E, Table IV, Figure 5 caption, conclusion, Supplement, and response. Do not use “validated family” unless the stated test supports that family on that axis.

Done when: One validation status exists for each family and axis, with no contradictory sentence, table, caption, or response statement.

Where to check: Manuscript: abstract p. 1; Table III pp. 39–40; Sec. III.E/Table IV pp. 42–43; conclusion p. 58.

2. Regenerate Figure 3 and the headline sample-form statistics from the repaired anchor cohort.

Verified issue: The abstract still reports the deposited-anchor values 37%, 49%, and 12%, whereas the repaired cohort gives 81%, 37%, and 4%. More importantly, the Figure 3 caption explicitly says the panels still plot anchors “as deposited,” even though 26 of 96 anchor rows are withdrawn and 15 are rescaled. The Supplement states that the anchor table drops from 96 rows to 70 after repair.

Action: Rebuild Figure 3 from the repaired anchors. Recompute plotted sample counts, cell medians, interquartile ranges, and variance ratios from that file. Update Table I’s “anchors behind Fig. 3” count from the final generator. Update the abstract to the repaired values. Keep the key qualification: sample form is strongly confounded with source paper, so the ratios define an operational conditioning rule rather than an independently established sample-form effect.

Done when: Figure 3, its caption, Table I, abstract, Sec. III.A, Table III, Supplement, and response all use the same repaired anchor cohort and statistics.

Where to check: Manuscript: abstract p. 1; Table I p. 8; Fig. 3 p. 27; Table III p. 39. Supplement: Sec. 15/Table S4 pp. 12–13. Response: p. 16.

3. Make the refusal claim consistent with what the model actually emits.

Verified issue: The response opens with “The framework declines to predict outside its validated scope.” The manuscript simultaneously states that the field axis is not validated at family level, while the surviving 163 outputs over 84 MgB₂-class compounds still use the field term and are explicitly not offered as validated field-axis predictions.

Action: Choose one internally consistent position. Preferred: if the field axis remains unvalidated, do not call field-dependent outputs validated predictions; label them conditional/illustrative family-envelope evaluations, or refuse them. The abstract, response opening, Sec. III.E, Figure 5, Table IV, and conclusion must use the same terminology.

Done when: No emitted quantity is called a validated prediction when the same manuscript declares its axis unvalidated.

Where to check: Response: pp. 1 and 4. Manuscript: Table III p. 40; Secs. III.E–F pp. 42–55; conclusion p. 58.

4. Remove stale candidate-accounting and dispatch text from the Supplemental Material.

Verified issue: Supplement Sec. 9 still says the 11-type family has 55 candidate records, while current Table IV uses 49 and Sec. 10 uses the current total of 233 records. Sec. 12 also evaluates “53 non-refused” 11-type and 37 non-refused 122-type candidates at 4.2 K and 1 T and says those committed-scope predictions are retained as headline values, whereas the current manuscript refuses all 0.1 T and 1 T targets and dispatches neither iron-based family. Table S6 commentary still discusses low-field behavior inside the now-refused region.

Action: Regenerate Supplement Secs. 9, 10, 12 and the Table S6 explanatory text from the final candidate table and gate logic. If Sec. 12 is retained as a pre-gate sensitivity diagnostic, label it explicitly as pre-gate and do not call those rows non-refused or headline predictions.

Done when: No candidate count, “non-refused” label, or headline value in the Supplement conflicts with the main dispatch accounting.

Where to check: Supplement: Sec. 9 p. 5; Sec. 10 pp. 5–6; Sec. 12 p. 8; Table S6 commentary pp. 15–16.

5. Fix the public generator so the released prediction file is exactly reproducible.

Verified issue: The response states that the deposited prediction file does not reproduce exactly from its own generator: two records use a different sample-form commitment, and regeneration restores six withdrawn candidates because the withdrawal ledger is not enforced. The restored candidates are refused, but this remains avoidable and weakens the reproducibility claim.

Action: Make the withdrawal ledger an input to the generator; make sample-form commitment deterministic and identical to the released file; fix the random seed or store the released bootstrap realization. Regenerate the final prediction file from scratch and verify all deterministic columns and reported counts.

Done when: A clean run of the deposited pipeline generates the same candidate list, scope assignments, refusal codes, deterministic predictions, and counts as the released files.

Where to check: Response: p. 15, paragraph beginning “The deposited prediction file does not reproduce from its own generator.”

6. Revise the response only after the final data freeze.

Verified issue: The response says the Figure 3 anchor count “does not move,” while the Supplement says the anchor table drops from 96 to 70 rows after repair. It also says “Nothing generalizes across source papers,” although that test is limited to eight compounds with more than one source, and it says the framework predicts only inside validated scope while later acknowledging unvalidated field-axis output.

Action: After Items 1–5 are frozen, revise the response once. Use scope-specific wording, for example: “Generalization across unseen source papers is poor for all three tested parameterizations on the eight compounds with multiple sources.” Correct the Figure 3 anchor-count statement. Keep the audit transparent, but structure each reply as concern → test → correction → surviving claim. Remove superseded intermediate numbers and version-history details that no longer answer the reviewer.

Done when: Every response number and claim points to the final manuscript/Supplement, and the letter reads as a controlled scientific revision rather than a running audit log.

Where to check: Response: pp. 1, 9, 15–17, especially the opening summary and “What we now report.”

B. Writing and story improvements — no new analysis required

1. Make “predictive scope” the paper’s central idea.

The strongest surviving message is that literature-derived prediction fails unless the comparison class and the normalizing scales have defensible provenance. State this early: before predicting a process-sensitive property, determine which measurements can be compared and whether the normalizing scale belongs to the same specimen. This turns the critical-field audit into part of the science rather than an apology.

2. Consider a title that matches the result that survived the audit.

A potential title is “Determining Predictive Scope for Superconducting Critical Current from Heterogeneous Literature.” It directly reflects the robust contribution. Keep the current prediction-focused title only if the final validation matrix genuinely supports that wording.

3. Rewrite the abstract as a clean four-step argument.

Use problem → method → robust findings → general implication. Lead with the ill-defined regression target. Then give only the repaired dataset size and the robust findings: reduced-variable scaling does not organize the corpus, while temperature-axis substructure separation survives independent rebuilding. End with scope/refusal and the provenance lesson. Remove stale conditioning ratios and any candidate-output detail that is not fully validated.

4. Move the unseen-paper generalization result earlier.

The source-paper holdout is one of the clearest demonstrations of why the problem matters: performance is much worse when an entire source paper is unseen than when points from a known source/compound are held out. Bring this result forward and state the eight-compound scope beside it.

5. Remove revision-history prose from the main scientific narrative.

The manuscript repeatedly says “an earlier version,” “previously reported,” “we withdraw,” and “does not reproduce.” Keep that history in the response and audit Supplement. The published manuscript should present the final method, repaired cohort, final limitations, and final results. This will make the paper read as science rather than as a forensic report.

6. Make paragraph transitions carry the argument forward.

Use transitions that explain why the next analysis is necessary: “Having established that reduced-variable scaling does not collapse the literature, we next ask which physical grouping retains reproducible signal.” “To determine whether that signal survives extraction uncertainty, we rebuild the temperature exponents directly from the source figures.” “Having identified the limits of family-level applicability, we finally test how refusal changes the candidate output.”

7. Tighten the response letter by about 25–30%.

Keep every correction needed to answer the reviewers, but compress repeated histories of earlier wrong numbers and intermediate versions. A shorter concern → test → change → surviving claim structure will read as more confident and more final.

Recommended order of work: freeze the repaired data and family-by-axis validation matrix → regenerate Figure 3 and Supplement/candidate outputs → fix the public generator → synchronize manuscript and Supplement → revise the response letter last → run one final numerical text audit. Submission is ready only when all six mandatory items above are closed.

