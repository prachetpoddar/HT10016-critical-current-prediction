# What the manuscript now has to change, and how it lands against the referees

## First, a retraction that changes the size of the problem

`verify_deposit.py` carried a dictionary of counts labelled as what the
manuscript prints. It was not. Every value in it equals what the deposit itself
held at commit 18c8426, the commit that introduced it. The check was comparing
the deposit with a snapshot of the deposit.

The nine "manuscript" mismatches reported through this session were therefore
the wrong sizes, and one quantity was reported as agreeing when it does not.
`analysis/read_manuscript_counts.py` now reads the counts out of
`HT10016_revised.docx` and records the table row each came from in
`audit/manuscript_printed_counts.csv`.

## Table I, as it stands against the deposit

| Table I row | manuscript prints | deposit holds | change |
|---|---|---|---|
| Papers contributing fitted curves | 69 | **64** | -5 |
| Distinct compounds with fitted curves | 43 | **39** | -4 |
| Critical-current data points extracted | 4387 | **4211** | -176 |
| Temperature-axis partial fits | 419 | **260** | **-159** |
| Field-axis partial fits passing physicality | 95 | **94** | -1 |
| Field-axis source papers | 17 | **16** | -1 |
| Per-paper anchors behind Fig. 3 | 110 | **103** | -7 |
| Candidate compounds evaluated | 185 | **183** | -2 |

Eight counts already typed here are not yet located anywhere in the manuscript
text, so they are neither verified nor refuted: papers contributing anchor rows,
physical samples, dispatched compounds, dispatch tuples, emitted targets,
candidate records, and the four calibration counts. Finding them is outstanding.

## The validation numbers move, and one conclusion flips

These are not renumberings. They are reruns of
`analysis/compound_leave_one_out.py` on the current cohort, and they were run
both before and after today's three corrections so the two causes can be
separated.

**Temperature axis.** Unchanged by today; entirely the earlier eleven-paper
withdrawal.

| family | manuscript | now | below the threshold of 1 |
|---|---|---|---|
| iron chalcogenide 11 | 0.261, 5 compounds, 37 fits | **0.588**, 5 compounds, 89 fits | 92% then, **100% of 1991** now |
| iron pnictide 122 | 1.092, 3 compounds | **1.314, 2 compounds**, 106 fits | 38% then, **30%** now |
| iron pnictide 1111 | 1.721, 4 compounds | **3.120, 3 compounds**, 54 fits | 8% then, **21%** now |

The paper's conclusion survives: iron chalcogenide 11-type is still the only
family that clears the screening-grade threshold on this axis, and its bootstrap
support is now 100 per cent rather than 92. The point estimate is worse and the
122 family is down to two compounds, so the sentence in Sec. III.C about holding
out BaFe2As2 from 198 fits no longer describes anything that exists.

**Field axis.** Here one conclusion does flip, and it flipped before today.

| family | manuscript | now |
|---|---|---|
| conventional AlB2 | 0.753 | 0.753 |
| iron chalcogenide 11 | 0.641 | **1.094** |
| iron pnictide 122 | 0.973 | 0.973 |
| iron pnictide 1111 | 3.066 | **2.571** (today: the PrFeAsO refit) |

Section III.C currently says iron chalcogenide 11-type "passes on the field axis
as well". At 1.094 it does not. That sentence, and the graded applicability
claim built on it, has to change. The 1111 improvement is today's refit.

**And a sign change caused by today's corrections.** On the per-paper field-axis
leave-one-out, the conditioned Stage 2 predictor was better than the pooled
median before today (1.053 against 1.141 over 68 and 88 fits) and is worse after
(1.257 against 1.158 over 82 and 94 fits). The six PrFeAsO fits that crossed the
applicability gate carry small exponents and enter the conditioned pool. The two
rows are different predictors on different cohorts, so this is not a like-for-
like comparison, but the direction is no longer favourable and reporting it as
though it were would be wrong.

## How this lands against the two referee reports

**A1, provide examples of the extracted data.** Answered, and now further than
asked. The repository is public, carries per-curve extraction examples, and adds
585 points re-measured from figures with their calibration files and overlays.

**A3, the power-law form is a Ginzburg-Landau expansion used far from its
limits.** This is the deepest criticism and the audit has made it sharper, in
the referee's favour. Fits whose critical scale came from a literature default
run to the exponent ceiling of 30; fits whose scale is read from the paper have
a median exponent of 1.40 and none at the ceiling. Refitting one paper against
its own irreversibility line moved the exponent from a median of 6.2 to 0.22
while leaving the residual essentially unchanged, which is direct evidence that
Form 3 is an empirical parameterisation rather than a physical law. The
defensible response is to concede A3 and adopt the reframing the referee offers
in A12, using this as the quantitative demonstration.

**A5, Jc(H) changes suspiciously weakly and the H = 0 spread is suspiciously
small.** Now partly explained rather than defended. Tier-3 field fits have a
median normalised window of 0.08, meaning the fitted curves barely span any
field at all, which is exactly the appearance the referee describes. The
excessive-precision complaint (0.388 dex) is a trivial fix throughout.

**A7, are the data limited to Elsevier and Springer.** Answered quantitatively
for the first time. A caption screen over all 2597 unique PDFs in the archive
finds 966 carrying a Jc figure caption and 422 that name field sweeps with
several isotherms. The fitted cohort of 64 papers is a small fraction of that,
and the honest statement is that the corpus is a convenience sample whose size
is now measured.

**A8, "934 papers" exaggerates; report the real numbers.** The manuscript already
answered this with Table I. Seven of its eight rows are now wrong, all downward,
and the temperature axis by 38 per cent. This has to be presented as an audit
finding rather than a quiet correction, because the referee's suspicion was
correct and the paper is stronger for saying so.

**A9, the 23-fold claim is an exaggeration driven by cuprate fits from a crude
model.** The referee's instinct is now traceable to specific records. Six
cuprate BSCCO field-axis fits, all pinned at the exponent ceiling, came from a
superconducting-diode-effect paper that reports no current density in any units;
they have been withdrawn. Twenty-eight ceiling fits remain, all Tier-3.

**A11, La2FeAsO.** Trivial, unaddressed.

**A2, A4, A6, A10, A12 prose, and B-main, B1 to B6.** Untouched by this work.
They are exposition and framing tasks: the statistical vocabulary, the Talantsev
self-field comparison, the aggregation walkthrough, the inference procedure for
an unseen compound, the four assumptions, and the Figure 2 arrows.

## Against Hossain's position

His position going into the resubmission is that the response letter
over-concedes and that the claims the referees called valuable should be
strengthened. This session's work cuts against that in the short term. Every
correction shrinks the evidence base, one family loses its field-axis pass, and
a fabricated record was found inside the deposit.

There is a real counterweight, and it is the argument worth making. The paper no
longer has to concede A3, A5 and A9 as generic weaknesses. It can say which fits
were unusable, why, and what was done about them, and it can show that the
subset with a properly sourced critical scale is well conditioned: 82 passing
fits, none at the ceiling, median exponent 1.40. That is a stronger position
than defending the previous numbers, and it converts the referees' three
strongest criticisms from objections into results.

The strategic decision that is not mine: the temperature axis is now 260 fits
over 20 papers, one family rests on a single paper, and the 122 family has two
compounds. Whether that axis is still reportable at the strength the manuscript
claims is a judgement for the authors.
