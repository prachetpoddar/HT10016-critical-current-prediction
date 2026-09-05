# Figures 1 and 2, redrawn in the v22 visual language

Recorded 2026-09-05. Generators `analysis/manuscript_figure_1.py` and
`analysis/manuscript_figure_2.py`. Embedded by
`analysis/reembed_manuscript_figures.py` into `out_figs/*_final14.docx`.

## What changed

Both figures are drawn in the palette and typeface of the v22 manuscript the
author supplied: the cream canvas, the green section headers, the rounded
pastel panels, DejaVu Sans. v22's own Figure 1 image is referenced by
`word/document.xml` but missing from the archive, so there is no v22 Figure 1
to match and the palette is the only thing carried across.

Figure 2 keeps v22's layout and adds what the reply letter commits to: the
critical-scale resolution stage drawn explicitly between extraction and
fitting with its four provenance tiers and a heavy border, a label on every
arrow, and the refusal branch leaving dispatch. That answers Referee B item 5,
"there is no connection between Input and Predictor if you follow the arrows".

Figure 1 panel (b) now shows the gates that refused each family, which its
caption has promised since the first revision and which no version of the
panel had drawn.

## What an independent review broke

Eleven findings. Six were real defects in what I had just drawn.

**A rounded box of zero width is not invisible.** The dispatched bar was drawn
unconditionally, and `rounding_size=0.4` turned the zero-width patch into a
capsule about 0.8 units across, in the colour the legend defines as
dispatched, on the two families that dispatch nothing. Both zero-dispatch bars
carried a visible teal cap beside a label reading "0 / 29".

**The refusal reason was a plurality presented as a cause.** The first version
reported one gate per family, taken as the modal code per compound and then
the modal compound. Refusal is per target, and a compound routinely hits
several gates: every one of the 29 refused iron chalcogenides hits both the
reduced-field window and the above-Tc gate, and 17 also hit the family-level
field-axis gate. The reported reason was a 44 percent plurality, and one grid
point either way flipped it for 16 of the 29. The panel now lists every gate
with the number of refused compounds carrying it, and says the counts overlap.

**"Every anchor carries its tier" is not true of the anchor table.**
`phase_3_p31_jc_anchor_per_paper.csv` has no tier column. The tiers are
carried by the resolved critical scales in the provenance table, which is what
the stage assigns. Both figures said the wrong thing; both now say the right
one.

**"50 curve records"** in Figure 2 was the paper count under a different unit.
Figure 1 and Table I both call the same 50 papers. A reader dividing 3303
points by 50 curve records would have got 66 points per curve.

**"The closed-form comparison cohort"** labelled the 20 that survive the
two-axis gate. Table I's own supporting cell says both closed-form results
were computed on the pre-withdrawal 23 and are reported as such. The subtitle
now says so.

**"No value emitted"** on the refusal branch is stronger than the deposit.
Supplement Sec. 12 states that a dispatch row carries a prediction, a refusal
code, or both, and 321 refused rows in the deposited file do carry a computed
value with its interval. The branch now says the target is withheld.

## The assertion that guards these numbers

`figure_counts.TABLE_I` held six entries and checked five, one of which
compared two constants in the same module with each other and could not fail,
while six real Table I rows printed inside Figure 2 were not checked at all.
It now holds twelve and checks twelve, plus a guard that fires if the pinned
dict and the check list drift apart. Every one of the twelve was verified to
fire by mutating it and confirming the run refuses.

## Open, and not fixed here

The 35 in Table I is a count of distinct compound LABELS, and the labels come
from two naming systems. Cohort A records the registry's canonical family
formula, Cohort B the paper's stoichiometry, so `Pr2FeAs2O` and
`PrFeAsO0.6F0.12` are the same material from the same paper under two labels,
and `Ba(FeAs)2` at 38 K and `BaFe2As2` at 20 K are different dopings under one.
A mechanical reduction to (family, element set, dopant) takes 35 labels to 27
keys, and chemically obvious merges take it lower.

Nothing computed in the paper groups by label except leave-one-compound-out.
On the temperature axis, which is the axis carrying the surviving result, the
cohort has nine labels and no collision among them. On the field axis
`FeSe_Te_doped` and `FeTe0.5Se0.5` are the same material in two papers under
two labels, so a leave-one-compound-out there does not fully hold the material
out; the field axis is reported as not validated at family level, so no
positive claim rests on it.

This is a wording problem in a census row rather than a defect in a statistic,
and it is left for the author to decide.

## Resolved 2026-09-05: the label count is now stated

The author's decision was to reword and give the reduced count.
`analysis/compound_label_reduction.py` performs the reduction under a stated
rule and reports where the rule is wrong in each direction;
`analysis/apply_compound_label_edits.py` writes the result into the three
documents as `*_final15.docx`.

Table I row 3 is now "Distinct compound labels with fitted curves" and its
supporting cell says it is a label count. The abstract, the Fig. 1 caption,
Figure 1 panel (a), Figure 2, and three passages of the response all follow.
Section II.D gains a paragraph giving the two naming systems, the reduction of
35 labels to 27 composition keys, the two directions in which the rule errs,
the fact that no aggregation groups by label, and the state of the two
compound leave-one-out cohorts: nine labels denoting nine compositions on the
temperature axis, and on the field axis ten labels of which FeSe_Te_doped and
FeTe0.5Se0.5 name one material in two papers.

## The three-panel Figure 1, and what a second review broke

The author supplied the graphical overview that v22 referenced and the archive
did not contain, and asked for Figure 1 to be that figure. The layout is now
its three panels: the corpus funnel, the aggregation, the bounded prediction
scope. The content is not, because nearly every headline the reference printed
has been withdrawn since: the 23-fold MAE reduction, the 10.10 and 0.43 stage
errors, 23 fittable compounds, 186 partial fits, 88 high-confidence plus 130
graded predictions, 81.2 percent coverage, 218 of 239 retained, and a pooled
sub-1-dex compound leave-one-out error.

An independent review of the first draft of the new figure found eleven
defects. Six were serious enough to have reached the referees.

**The figure's boldest claim was not in the manuscript.** The amber pill read
"family label explains 0.52 of the between-paper variance in beta_T, p =
0.007". The strings 0.52, 0.524 and 0.007 occur nowhere in the manuscript.
That result is in the reply letter, paragraph 81. Figure 2 carried the same
number in a call-out and has been corrected the same way. Both now state the
applicability result of Sec. III.C, which is in the manuscript.

**The figure had the conditioning argument backwards.** It said the stage
comparison does not carry the claim and the sample-form variance
decomposition carries it instead. The reply letter, paragraph 38, retires
exactly that position: resting the claim on the diagnostic "will not do",
because sample form is nearly a relabelling of source paper and no family cell
can reach p below 0.10 under the only null that respects that structure. The
panel now says what the manuscript says: the diagnostic sets the rule the
predictor follows, and does not establish it to significance.

**The funnel re-asserted a provenance Sec. II.A exists to remove.** It put
"n = 934 (Elsevier + Springer)" at the mouth and the fitted census at the
outlet. Sec. II.A says the fitted cohort is not drawn exclusively from those
two publishers "because an earlier version of this manuscript implied
otherwise": 18 of the 20 temperature-axis source papers are arXiv preprints.
The panel now says so.

**The funnel bands were not the manuscript's screens.** "Form 3 fittability
criterion" was drawn first, but Form 3 is the functional form selected in
Sec. II.C after fitting, not a screen; "Applicability boundary" is that screen
and was drawn last; "Sample-form disambiguation" is an extraction step. The
bands are now the applicability window of Eq. (1), the partial-fit and
full-fit thresholds, and the cross-model agreement gate, in the order the
manuscript applies them.

**The Venn was not the gate logic.** The figure and its caption said the three
circles are how the five refusal codes group. refusal_flag is a first-match
precedence code: 501 of the 1054 reduced-field refusals also sit at or above
the validated reduced temperature, and 219 of the 540 missing-field refusals
are also above Tc, so a refused target routinely violates two or three at
once. Sec. II.D also applies anchor-density, monotonicity and population
screens the three circles do not represent. The panel now presents them as
necessary conditions and names what it leaves out.

**"Each refused target carries an explicit reason code" is false.** Sec. III.E
applies two screens at the reporting layer and says the deposited file "carries
these rows with an empty refusal code".

## The layout checker, and its own negative controls

The same review mutated analysis/figure_layout.py fifteen ways and eleven of
the mutations left both figures reporting "none overflowing": a pad loosened
to 2, outermost box winning instead of innermost, the extent replaced by the
anchor point, the raise removed, region() made a no-op. The cause was that
nothing in either figure sat near a boundary, and nothing asserted the check
fires at all.

Fixed: region() for a circle now inscribes the rectangle at the label's far
edge rather than its centre line, which the review demonstrated accepts
corners outside the circle by more than the radius; a tapering shape is
credited with its narrowest width; figure.dpi is pinned to the dpi savefig
writes at, because the same string measures 42.06 units at 72 dpi and 42.43 at
300; a quarter-unit clearance is required rather than bare containment; and
check() refuses a run in which nothing was recorded.

analysis/test_figure_layout.py is the negative control that was missing. Its
fixtures are built from the measured width of a real string and placed one
unit either side of the boundary, because the review's finding was that every
fixture in this repository sat far enough from its boundary to pass whatever
the check had been loosened to.
