# Disclosure draft for the response to referees

Recorded 2026-09-05. Drafted to be inserted into
`RESPONSE_TO_REFEREES_corrected.md` under "Changes we made on our own", after
the existing paragraphs on the critical-field scale. Every number traces to a
script named in `audit/manuscript_numbers_repaired.csv`.

---

## A further audit of the anchors and the fitting protocol

The audit of the critical-field scale described above did not stop where we
first reported it. Continuing it turned up four further defects, three of them
in places we had not looked. We report all four, and what they do to the
results.

**Eleven papers were withdrawn and one table was not updated.** Between 1 and 3
September we withdrew eleven papers from the temperature-axis cohort after
opening their figures. The defects were not marginal. Three record a current
axis in A/m2 as A/cm2, which puts the values above the depairing limit. Two
record the minor ticks of a logarithmic field axis as field values, so the field
range is a few gauss. Six carry isotherms that are exact arithmetic ramps, in
one case with successive isotherms separated by the same constant step, which no
measurement produces. One interleaves two series three orders of magnitude apart
inside a single isotherm. Each withdrawal is recorded with its citation, the
figure checked, and the reason.

The temperature-axis fit count in Table I reflects those withdrawals. The
provenance table does not, because withdrawing a paper never removed its
provenance row, and three of Table I's counts are computed from that table. The
result is that Table I is internally inconsistent: its 260 temperature-axis fits
exclude the withdrawn papers and its 62 contributing papers include them. The
corrected counts are 50 papers, 35 compounds and 3303 extracted points. The
extracted-point count was overstated by 843, a fifth of the figure we printed.

**The critical-temperature anchor is a lookup table, not a paper-reported
value.** We described the critical-field scale as read from figures. The
critical-temperature scale is not read at all. The routine that fits the
temperature-axis exponent carries a dictionary keyed on the idealised compound
string, with per-substructure defaults for anything absent from it, so every
Ba(FeAs)2 record takes 38.0 K and every unlisted 1111 record takes 50.0 K. The
deposit labels these values paper-reported.

Opening the papers, six of the eighteen on the temperature axis are wrong by 5 K
or more against the value the paper prints for the sample whose figure was
extracted, the largest by 25.9 K. On the field-axis cohort, of the nineteen
papers whose source document we hold, three anchors match what their paper
prints, three match one of several samples, eight disagree with every printed
value, two papers print no critical temperature for the sample they measure, and
three cannot be checked. Four of the eight disagreements are a literature value
for the family rather than for the sample.

We have replaced every anchor we could check with the value the paper prints,
with the sentence quoted in the deposit for each. On the temperature axis this
costs no fits and adds points to 39 of them, because three papers had a lower
anchor than their true one.

**The applicability window was applied to one axis and not the other.** The
window we state has two conditions, a reduced temperature below 0.7 and a
measured field span above 0.3 of the critical field. The temperature condition
is imposed on the temperature axis, by cutting the fit window against the
anchor, and it was not imposed on the field-axis cohort at all. Nineteen of the
94 field-axis fits sat above the stated bound, the highest at 0.955. It is now
applied to both.

**The field condition contains nothing independent of its own scale.** The
condition compares the measured span with the critical field, and the same
critical field selects the points the fit uses and forms the abscissa the
exponent is fitted against. Written out, the condition says that the critical
field is at most 3.3 times the measured span, and nothing about the sample
enters it. It is satisfied by a small scale, which is the direction in which a
scale read from a curve endpoint is wrong. We considered replacing it with a
condition on the range of the abscissa, and did not, because that quantity is
gamed by the same choice of scale: on our own cohort every fit that fails it
passes on unchanged data at a smaller scale. There is no scale-free criterion
available here, and we now state the condition for what it is rather than
implying it tests the data.

**The extracted curves carry less structure than the figures they come from.**
For eight papers we hold both an extraction and an independent pixel trace of
the same printed figure. Put on the same isotherms, the same field window and
the same code, the extraction carries four to twenty times less interaction
between the temperature and field dependences than the figure does, in eight of
the nine comparisons. The ninth is the one extraction in that set digitised by
hand, and it carries slightly more. Measured against the precision each source
is written at, eight of the extracted surfaces are as close to a product of one
temperature curve and one field curve as their recorded precision can show, and
no traced figure is.

This matters for the exponent that the field axis reports. Fitted on a surface
with no interaction, the field exponent returns the field curve that was swept
rather than a property of the sample. It is consistent with the fact that the
extraction route predicts that exponent completely: hand digitisations give 0.003
to 0.023 and machine extractions 0.120 to 2.409, with no overlap.

## What this does to the results

We tested the substructure separation again with papers as the unit and a
permutation test over the family labels, which needs no distributional
assumption and is unchanged by a rescaling of the exponents.

On the temperature axis the families separate, and correcting the anchors makes
the separation stronger. Matched on the seventeen papers common to both
versions, the fraction of between-paper variance the family accounts for rises
from 0.44 to 0.52, with a permutation probability falling from 0.016 to 0.007.

On the field axis the families do not separate, under either version. The
fraction is 0.055 before the repair and 0.038 after, with permutation
probabilities of 0.93 and 0.98. This is not a result the repair removes. It was
not present in the data as deposited either, and we had not tested it with a
statistic that could have shown so.

We therefore state the substructure result as a temperature-axis result, and we
report the field axis as not separating the families rather than omitting it.

## What we now report

Table I is restated on the repaired cohort: 50 contributing papers, 35
compounds, 3303 extracted points, 257 temperature-axis fits, and 52 field-axis
fits from 12 source papers. The anchor count behind Figure 3 and the candidate
compound count do not move, because no withdrawn paper appears in the anchor
table and the candidate side does not depend on the anchors.

The field-axis cohort falls from 94 fits to 52. Because that is a large change,
the Supplemental Material now carries the disposition of all 94 individually: 52
kept, 24 on the three papers whose anchors we withdrew, 11 above the reduced
temperature bound once the anchor is corrected, and 7 below the field bound once
the scale is corrected. The deposited cohort remains in the deposit, so a reader
can reproduce either version.

---

# Edits to passages already in the response

## 1. The Table I ladder

`RESPONSE_TO_REFEREES_corrected.md`, the answer to "934 papers exaggerates the
effective dataset size".

Replace:

> Table I of Section II.A now gives the full ladder in one place: 934 articles
> screened, 62 contributing fitted curves, 38 distinct compounds, 4146 extracted
> critical-current points, 23 fully fittable compounds, 260 temperature-axis
> fits, 94 field-axis fits drawn from 16 source papers, and 96 per-paper anchors
> behind Figure 3.

with:

> Table I of Section II.A now gives the full ladder in one place: 934 articles
> screened, 50 contributing fitted curves, 35 distinct compounds, 3303 extracted
> critical-current points, 257 temperature-axis fits, 52 field-axis fits drawn
> from 12 source papers, and 96 per-paper anchors behind Figure 3. The counts
> for contributing papers, compounds and extracted points are lower than in the
> previous revision because eleven papers were withdrawn from the cohort and
> their provenance rows had not been removed with them; the reasons are set out
> below.

The count of fully fittable compounds is dropped from the ladder. The label
recorded which papers could in principle contribute both exponents rather than
which did, and of the papers carrying it exactly one contributes to both axes.

## 2. The field-axis scale paragraph

The existing passage reports the scale audit and ends with the five papers whose
kilo-oersted axis was recorded as tesla. Append:

> Two of those five have since been withdrawn from the field-axis cohort for a
> different reason. Neither paper contains an upper critical field or an
> irreversibility field anywhere in its text, and neither has a figure that
> measures one, yet the deposit recorded a per-temperature scale for both, in
> one case rising by a factor of seven with temperature. The unit correction is
> not what removes them. A scale read in kilo-oersted from the same figure as
> the data cancels in the ratio the applicability condition uses, so it leaves
> that condition where it was. What removes them is that there is nothing in
> either paper for the scale to have been read from.

## 3. Where the Supplemental Material has to change

- Section 13, the critical-field audit: add the two withdrawals above and the
  correction that the unit error does not by itself move the applicability
  condition.
- Table S1, which links every fitted exponent to a literature record: rebuild on
  the 50 contributing papers, with the withdrawn rows kept and marked rather
  than deleted.
- A new table carrying `audit/supplement_fit_disposition.csv`, the disposition
  of all 94 deposited field-axis fits.
- The critical-temperature provenance, currently given as paper-reported, has to
  be restated. It was a lookup table keyed on the compound string.

## What is deliberately not in this draft

No claim that the extractions were generated rather than read. The evidence
supports a weaker statement, which the draft makes: the extracted surfaces carry
much less interaction than the printed figures they came from, and by an amount
that tracks how the extraction was made. How that came about is not something we
can establish from the deposit.

No new physical claim of any kind. Every number is a recount or a refit of
material already in the paper.
