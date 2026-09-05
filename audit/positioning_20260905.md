# Where the response stands, item by item

Recorded 2026-09-05, against `out_a10/*_final9.docx`. This supersedes
`audit/referee_concessions_checklist_20260904.md`, which predates the anchor
repair, the withdrawal-ledger retraction, the protocol, and everything traced
since.

## How this was built

1. Enumerated the referee items from the letter itself rather than from the
   old checklist, because the checklist's numbering had drifted. Referee A has
   thirteen items, not ten; Referee B has eight, all expository.
2. For each item, located the paragraph that answers it and the evidence that
   answer rests on.
3. Traced each piece of evidence to the audit note that most recently touched
   it, and graded it by whether that note leaves the evidence standing.
4. Checked the letter against itself for statements that the later edits have
   made inconsistent.
5. Checked the two asks that are not the referees': the advisor's position that
   the letter over-concedes, and the Data Availability promise.

Grades. **Holds** means the answer and its evidence both stand. **Stronger**
means the evidence improved since the letter was written. **Conceded further**
means the answer is now a larger concession than it was, deliberately.
**Open** means something still has to be decided or written.

## Referee A

| # | objection | grade | basis |
|---|---|---|---|
| 1 | provide examples from the dataset | **Holds** | Tables S1, S4 and S5 rebuilt from surviving records; the eleven rows drawn from withdrawn material are gone. `audit/supplement_examples_20260905.md` |
| 2 | explain the vocabulary; the anchor is a pre-exponential factor | **Holds** | expository, unaffected |
| 3 | the expansion is used far from its limits | **Stronger** | the aggregate drift figures now reproduce and are given for both cohorts; the worked example is replaced with its grading stated. The referee's own concession at item 7 supplies the defence. `audit/exponent_drift_series.md` |
| 4 | orientation, current direction, MgB2 two-band and production-dependent | **Conceded further** | sample form now explains 4 percent in MgB2-class rather than 12, negative once bias-corrected, which agrees with the referee more completely. The test itself is conceded: the diagnostic cannot establish the regime distinction. `audit/jc_anchor_repair_20260905.md` |
| 5 | Fig. 5 left at 1 T is almost self-field | **Holds** | the redraw against reduced field stands; the envelope crossing is reported as a bound rather than a prediction |
| 6 | Jc vs H weak, spread at H = 0 small, excessive precision | **Stronger** | the mechanism is now exact: 4.2 K is the model's own reference temperature, so the temperature term is identically zero and the prediction is a family constant. A grid-point count the paper had wrong is corrected in the same answer. `audit/dispatch_spread_20260905.md` |
| 7 | "this crude model yields some acceptable results" | **Holds** | the referee's concession, adopted as the paper's own reason the parameterization works |
| 8 | limited to Elsevier and Springer? | **Holds** | 18 of the 20 temperature-axis sources are arXiv preprints, and that is now stated |
| 9 | "934 papers" exaggerates | **Holds** | Table I carries 934 / 50 / 35 / 3303 / 257 / 52 / 12, and the provenance table agrees with it |
| 10 | the 23-fold is an exaggeration | **Conceded further** | the three replacement figures are retired: two divided a four-family numerator by a three-family denominator, which is the error the same paragraph condemns. The letter now gives the two errors and the family count and no quotient. `audit/a10_traced_20260905.md` |
| 11 | none of these materials is applied anywhere | **Holds** | conceded as a limit on the work, with the reason extension is not a matter of adding data |
| 12 | La2FeAsO for LaFeAsO | **Holds** | corrected, and identified as systematic rather than a slip |
| 13 | overstates the contribution as compound-specific prediction | **Holds** | the abstract now states family-scope envelopes with an explicit refusal decision |

## Referee B

All eight items are expository: three models and their differences, the
inference procedure for an unseen compound, the regression model, what a
scaling exponent is, which expression is Form 3, the figure's arrows, and the
four assumptions. Nothing in the audit touches any of them. **Holds**, and item
1 is now more accurate, since the regression is named precisely rather than
left as a MAGPIE feature model.

## The advisor's ask

The position going in was that the letter over-concedes and that the claims the
referees called valuable should be strengthened. Tested against the current
state, that splits by axis rather than by claim.

**Where it is right.** The temperature axis is the claim the referees valued and
it is stronger than when the letter was written: the fraction of between-paper
variance the family label accounts for goes from 0.409 to 0.524 with a
permutation probability from 0.012 to 0.007, on matched cohorts. The letter does
not say so anywhere. Both negative theses are untouched. The frozen-axis
mechanism is a defence of the method that the letter never makes.

**Where it is not.** The field axis cannot be strengthened, because nothing on
it survives: the exponent separates no family on either cohort, the family-level
verdicts reverse under repair, and conditioning is not distinguishable from a
constant. The variance decomposition cannot be strengthened either, for the
reason item 4 now concedes.

So the honest reading of the ask is: strengthen the temperature axis, which the
letter under-sells, and concede the field axis further, which is the opposite
of over-conceding but applies to a different half of the paper.

## Two things the letter now says against itself

**The conditioning claim is parked on a diagnostic that cannot carry it.**
Paragraph 38, answering item 10, says "the conditioning claim no longer rests on
this ratio at all. It rests on the variance-decomposition diagnostic". Paragraph
20, answering item 4, says that diagnostic "cannot establish the regime
distinction it is used to draw". Eighteen paragraphs apart, in the same letter.

The same paragraph adds "all 96 per-paper anchor groups are identical before and
after the magnetic-field unit repair". True of that repair, and no longer the
whole story: the anchor repair of 2026-09-05 withdrew 26 of the 96 and rescaled
4 more, which paragraph 20 states.

**The field axis is written down in the manuscript and not in the letter.** Table
III and Sec. III.C now report the field axis as not validated at family level.
The letter never uses the phrase. A referee reading both will meet the
withdrawal in the table without an explanation beside it.

## What is left

- The two contradictions above, which are one paragraph rewrite.
- Sec. III.A's Spearman 0.635, located as a nine-family figure on the wrong
  column; the replacement is the rank result, which needs no interval.
- The dispatch scope, which the field-axis write-down leaves without a
  validating axis.
- The disclosure decision on the deposited prediction file.
- The Zenodo identifier the Data Availability statement promises. The letter
  does not mention it and the statement still promises it.
