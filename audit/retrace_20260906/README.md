# Retracing the three negative claims

Recorded 2026-09-06, at the author's request, before deciding to submit.

Scripts `analysis/retrace_variance_decomposition.py` and
`analysis/retrace_stage_comparison.py`; tables in this directory. An
independent review of both scripts found nineteen defects, and what follows is
what survived it.

## Claim 1, universal scaling does not organize the data

**The arithmetic reproduces exactly.** From `data/reduced_variable_scaling.csv`
the median of the per-cell standard deviations is 1.2382 dex and the global
standard deviation, reconstructed from the per-cell n, mean and standard
deviation, is 1.4232 dex. That gives 13.00 percent on the standard-deviation
scale and 24.31 percent on the variance scale, against 13.0 and 24.3 printed.
The grid is 9 by 9, 66 cells are populated, and no cell holds fewer than five
records, all as stated.

**The convention had to be adjudicated.** The reconstruction assumes the
deposited per-cell standard deviations use ddof = 1. Under ddof = 0 the same
algebra gives 13.44 and 25.08, and `audit/headline_numbers_recheck.md` records
that reading as a deposit problem. 13.44 does not round to 13.0, so ddof = 1 is
the convention the published figures were computed under. This is stated here
rather than assumed.

**Three things cannot be checked from the deposit.**

No script in the repository generates `data/reduced_variable_scaling.csv`, and
git carries it only in the release commit 8ad8d43. No point-level table sits
behind it. So the binning can be checked at its last arithmetic step and
nowhere earlier.

The table's 5422 records have no counterpart in any deposited census. The
whole pre-withdrawal corpus is 4146 extracted points across 62 provenance
rows, and the rows flagged fully fittable carry 2383 points across 32 papers.
The binning holds more records than either.

The 400-draw critical-field perturbation has no script and no deposited
output, so the sensitivity statement rests on a computation the deposit does
not contain.

**A note on the statistic, which runs against the paper's own interest.** The
median of per-cell standard deviations weights every cell equally, from 5
records to 594, while the global standard deviation is weighted by record. The
pooled within-cell standard deviation is 1.3268, which would give 6.8 percent
and 13.1 percent. Since the paper's conclusion is that the reduction is too
small to adopt universality, the pooled figure would strengthen it. The
reported statistic is the one less favourable to the paper's own argument.

## Claim 2, sample form is a required conditioning variable

**All six values reproduce.** Deposited 0.1159, 0.3737 and 0.4877 against the
printed 0.12, 0.37 and 0.49; repaired 0.0442, 0.8090 and 0.3743 against 0.04,
0.81 and 0.37. Sample counts 15, 12, 10 and 13, 5, 5.

The collapse to one record per physical sample strips an isotherm suffix from
`sample_id` and, for the MAGLAB records, from `paper_id` through an enumerated
map. A general pattern reads `MAGLAB_11_6K` as 11.6 K rather than specimen 11
at 6 K; this retrace fell into that trap and returned 13 and 11 samples before
the enumeration was used.

**This retrace is not independent of the published route, and says so.**
`analysis/figure_4_source.py` already contains the same regex, the same
enumerated map and the same four grouping keys. The rule was read from it. So
what is verified is the arithmetic downstream of the rule, not the rule.

**The exact clustered p, and one defect in it.** Enumerating the full support
gives 0.6667, 0.5143, 0.2857 and 0.8000 on the deposited families, against the
deposit's sampled 0.6663, 0.5151, 0.28565 and 0.79905. The p floors are 0.17,
0.007, 0.007 and 0.017 deposited, and 0.33, 0.25 and 0.10 repaired.

For the deposited 122 family the observed statistic is not a member of the
null's support. One paper carries two sample forms, the clustered null gives
each paper one label, and the per-record eta squared of 0.4877 is a value no
arrangement of the null can produce; the null's own identity arrangement gives
0.5092. Both p values are now reported: 0.2857 against the per-record
statistic and 0.1857 against the null-consistent one. The deposit carries the
first. Neither is near significance, so no conclusion moves.

**Two deposited tables disagree on the same quantity.**
`data/phase_3_p58_variance_stability.csv` gives 0.4029 on 13 samples and
0.5599 on 11 for the chalcogenide and 122 families, because it strips only
`sample_id` and not `paper_id`. Its own docstring says the method follows
`figure_4_source.py` exactly and that the permutation is clustered on the
source paper; it does neither.

## Claim 3, conditioning reduces cross-family exponent error

**All four values reproduce.** From `audit/multi_stage_loso.csv`, 12.2948 and
14.8812 across the seven families and 1.1908 and 0.5479 on the three
physicality-passing families, against 12.3, 14.9, 1.19 and 0.55.

**The unconditioned arm is Stage 1**, a monolithic regression on one
compositional descriptor, which lacks family conditioning as well as
sample-form conditioning. The comparison the manuscript labels "without
sample-form conditioning" therefore differs from the conditioned arm in two
respects, not one.

**The deposited table carries a better control than either arm.**
`stage3_abs`, the substructure-aggregate median, averages 9.0065 across the
seven families, below both 12.2948 and 14.8812.
`audit/a10_baseline_trace.py` states this in its own docstring and the
manuscript does not carry the number.

**The four numbers are computed on the deposited cohort.**
`audit/a10_on_repaired_cohort.csv` gives 12.0150 and 16.5085, and 1.5581 and
0.8857, on the repaired cohort, and 1.5645 and 0.6694 on the admitted one. No
other cohort produces the four quoted values. Table III's scope cell for this
row names neither cohort and says "matched five-family cohort" while the
result reports seven families and three.

**A claim of mine that did not survive review.** I reported that the direction
of this comparison depends on which of four conditional readings is used.
`stage2_nearest_family_abs` and `stage2_nearest_no_form_abs` are numerically
identical on every fold, so there are three readings and not four, and the
second is the no-form control rather than a rival conditional predictor. Their
equality is evidence that form conditioning contributes nothing, which
supports the manuscript. The apparent win of the nearest reading on the
seven-family arm is also carried by one fold: `cuprate_RBCO`'s target sits at
the fitter's 30.0 ceiling and its nearest family is pinned at the same
ceiling, giving an error of 8e-9. Dropping that fold reverses it.

**A second claim of mine that did not survive.** I reported that "removing any
single family moves the comparison across unity" fails on the physicality arm.
It fails only when the comparator is Stage 1. The sentence's antecedent is the
out-of-sample median, which is `stage3_abs`, and against that the physicality
arm ranges from 0.544 to 1.517 and does cross unity. The manuscript is right
and my rebuttal was wrong.

## The rebuild of claim 1, and what it actually shows

Recorded 2026-09-06. Script `analysis/rebuild_reduced_variable_scaling.py`.

Since `data/reduced_variable_scaling.csv` has no generator and no point-level
source, the test was rebuilt from `data/reextraction/`, which holds digitised
temperature, field and critical-current triples with their calibration and
overlay images, joined to the critical scales in the provenance table. The
cohort is 6596 points from 27 papers, which is not the manuscript's.

**The rebuild cannot arbitrate the 13.0 and 24.3 figures, and two conclusions
reported from it have been withdrawn.**

### Withdrawn: that the rebuild confirmed and strengthened the refutation

The first version reported 8.66 percent, below the manuscript, and called the
refutation confirmed. Its record key was paper and measurement temperature.
Every series in `data/reextraction` is a field sweep at one fixed temperature,
so that key merges distinct samples measured at the same temperature in one
paper: 19 of 133 groups swallow two to five real curves, and they are exactly
the papers whose within-paper spread is the physics, irradiated against
unirradiated, five dopants, four samples.

### Withdrawn: that binning every digitised point is a density artifact

The second version reported the raw point figure of 46.22 percent as an
artifact, on the argument that a densely digitised curve makes a cell look
smooth. That was tested and it is false. Decomposing the within-cell variance
into within-curve and between-curve parts, the median cell carries 0.8 percent
of its variance within a single curve and the mean 3.4 percent. The scatter
inside a bin is between curves, which is exactly what the test is about.
Binning every point is the right primary unit.

| unit | cells | records | SD reduction | variance reduction |
|---|---:|---:|---:|---:|
| every digitised point | 67 | 6057 | 46.22% | 71.08% |
| one per curve per cell | 53 | 601 | 15.97% | 29.39% |
| one per paper per cell | 34 | 309 | 8.86% | 16.93% |

### What the gap actually is

A cell's internal scatter grows with the number of compounds sharing it, in
both tables. The deposited cells hold seven compounds at the median and this
rebuild's hold five, and at matched compound counts the deposited cells still
scatter more: 1.265 against 1.018 dex for cells holding five or more
compounds, 1.013 against 0.785 for cells holding three or four.

So the difference between 46 percent here and 13.0 percent published is a
difference of cohort and not of method. This rebuild covers 27 papers and
about a dozen distinct materials, and half its points sit in papers that share
a single substructure critical-scale constant, so its cells are narrower and
collapse more. It cannot stand in for the published cohort.

### What still stands

The published arithmetic reproduces exactly and its denominator convention is
independently confirmed. Its input table has no generator and no point-level
source anywhere in the repository or in git history, and its 5422 records
match no deposited census: the whole pre-withdrawal corpus is 4146 extracted
points and the rows flagged fully fittable carry 2383. The 400-draw
perturbation has no script and no deposited output.

One sensitivity is worth recording even though it did not change the verdict.
On a cell set held fixed across densities, thinning each curve sixteenfold
moves the reduction from 39.7 to 26.6 percent, because whole curves drop out
of cells as they thin rather than because curves are smooth. And
`1611_08455v1` figure 5b is digitised twice into files carrying identical
values, with nothing marking either canonical.

## Does the retrace strengthen claim 1? A third answer, and a third retraction

I proposed that the published statistic cannot isolate the reduced variables,
because it compares reduced-binned scatter against ungrouped global scatter, so
that any binning of a monotonic function would produce a reduction. I proposed
comparing reduced coordinates against absolute ones instead.

**The premise is false.** Binning the same 6070 points on two uniform random
coordinates, 9 by 9, floor 5, over 200 draws, gives a median reduction of minus
0.02 per cent, with a 5th to 95th percentile band of minus 0.99 to plus 1.04.
Binning by itself buys nothing. The published statistic has an exactly zero
null and does measure how much of log Jc a reduced-coordinate grid captures.

**The replacement test does not survive either.** Absolute binning appeared to
beat reduced binning, 67.0 against 39.3 per cent, but equal-width bins over the
absolute range are degenerate: five of the 42 kept cells hold 68 per cent of
the records, against 37 per cent for the top five reduced cells. Restricting to
cells that hold more than one compound removes most of the gap, 0.935 against
0.984 dex, and that residue is noise: bootstrapping over papers gives a
difference of minus 0.050 with a bootstrap standard deviation of 0.215 and a
sign that flips in 4 of 27 jackknife refits.

Every principled variant reverses it. The pooled summary gives 1.291 reduced
against 1.456 absolute, favouring reduced, with the sign stable in 27 of 27
refits. Equal-occupancy bins favour reduced at every resolution tested. A
grid-free nearest-neighbour version, excluding neighbours from the same curve,
favours reduced at every neighbourhood size. Out of sample, leave-one-paper-out
prediction from reduced cell means beats a constant model, 1.670 against 1.744
in RMSE, while absolute coordinates lose to a constant outright.

So reduced coordinates carry a small signal, absolute coordinates carry none,
and the reduced-versus-absolute comparison does not strengthen the manuscript.

## What does strengthen it

**The pooled summary.** `1 - median within / global` is not a variance
decomposition and can be negative; on the deposited file's own `log_Jc_norm`
column it is minus 11.3 per cent. The pooled within-cell standard deviation is
bounded and is what the sentence claims to compute. On the deposited file it
gives 6.78 per cent and 13.09, against the printed 13.00 and 24.31. That is
half the reduction, further below the 30 per cent threshold, from the summary
that can actually be defended.

**The out-of-sample statement.** Reduced-coordinate cell means barely beat a
constant model, which is a cleaner way to say the grid organises very little
than an in-sample within-bin ratio.

**A correction to this repository.** `audit/headline_numbers_recheck.md` said
the printed figure could not be reproduced from the deposit because the global
standard deviation needs the raw points. It does not: the law of total variance
recovers 1.4232 exactly from the per-cell counts, means and standard
deviations, and the reduction is 13.00 and 24.31 to the digit. That section is
corrected.

## The curve-motion question, and where it lands

The author objected that the analysis should use every digitised point and
should capture the material's response to stimulus, and that collapsing a curve
to one record per cell destroys exactly that. Both halves are right, and
following them through changes what claim 1 should say.

**Where the variance lives.** On this cohort, of the variance of log10 Jc that
the published test bins, 82.2 percent is between papers, 11.6 percent is
between curves inside a paper, and 6.2 percent is the motion along a curve. The
test is 94 percent a test of prefactor agreement and 6 percent a test of curve
shape.

**The temperature axis cannot be tested here at all.** All 171 digitised curves
in `data/reextraction` are isothermal field sweeps. Removing a per-curve
prefactor therefore sets the mean of every temperature row to exactly zero, so
the temperature axis carries no information after centring and only the field
response is testable on this cohort.

**The coarse grid is not an artifact for the published quantity.** At the
published 9 by 9 resolution only about 1 percent of within-cell scatter is one
curve moving across its bin, because prefactor differences dominate so
completely. Refining the field axis to 18 and 36 bins moves the median rule
from 46.2 to 42.0 percent and the pooled rule from 18.5 to 20.5. The published
statistic is stable against grid refinement.

**On the shape alone, reduced coordinates do not beat absolute ones.** Once the
prefactor is removed, absolute coordinates win on quantile bins, on the R
squared of a best universal one-dimensional function, and on pairwise shape
mismatch after offset removal; equal-width bins are the only framing that
favours reduced coordinates, and that advantage is a binning artifact.

**Two errors of mine, corrected here.** I reported 42.72 percent for the
centred quantity in reduced coordinates. That used bin edges over the occupied
range; on the manuscript's fixed 0 to 0.9 grid it is 37.86 percent. And I
reported that the collapse is real at high reduced field and absent at low
reduced field. It is not: at h below 0.1, where 55 percent of the records sit,
76 percent of the within-cell scatter is a single curve falling across one
over-wide bin, and the between-curve disagreement there is lower than at
h of 0.2 to 0.35, not higher.

**What this means for the claim.** The paper's conclusion is not weakened by
any of it, and the reason it holds is sharper than the reason the paper gives.
Universal reduced-variable scaling fails here not because the curve shapes
disagree, since they partly agree, but because the prefactor does not collapse
at all and the prefactor is 94 percent of the variance. That statement is
robust to grid refinement, to the record unit, and to the summary rule, and it
is the one worth making.

## Is the prefactor the intercept?

Yes, in the sense that matters, and the paper already has two names for it.

`log Jc,partial` in Form 3 is the intercept: the value the fit extrapolates to
zero reduced coordinate. It depends on the fitted exponent and on the critical
scale. `log10 Jc anchor` is the measured value at a curve's lowest measured
temperature and field, and Sec. III.A runs the variance-decomposition
diagnostic on it precisely because it uses no fitted exponent and no
critical-field scale. This retrace used a third variant, the curve's mean over
the window, which correlates 0.959 with the value at its lowest field and sits
a median 0.54 dex below it.

**The split depends on which one you pick, and the mean is the most
favourable.** Referred to the curve mean, the variance is 93.8 percent
magnitude and 6.2 percent motion. Referred to the value at the lowest measured
field, which is the anchor's definition, it is 74.8 and 25.2. Centring on the
mean minimises the residual by construction, so it maximises the magnitude
share. The magnitude dominates either way, but 94 percent is the high end of
the range and should be quoted as such.

For scale: the deposited anchor has a standard deviation of 0.894 dex over its
96 rows, against 0.398 dex for the motion along a curve in this cohort. The
anchor varies about twice as much as the curve moves.

**What this connects.** Claim 1 and claim 2 are about the same quantity and the
manuscript does not say so. Claim 1 fails because the anchor does not collapse
under reduced coordinates, and it is most of the variance. Claim 2 asks what
explains the within-family scatter of that same anchor, and answers that sample
form is the rule the predictor follows without being established to
significance. Stated together they are one argument: the anchor is what fails
to collapse, and the paper's diagnostic is an attempt to explain the anchor's
scatter by an experimental variable rather than by a universal law.

One caution on the linkage. The re-extraction curves can be matched to the
deposited anchor rows only at paper level, on 11 papers, which is the wrong
unit because the anchor is defined per sample at one temperature. At that unit
the correlation is 0.47 to 0.54, which is too coarse to verify the numerical
correspondence. What is verified here is the definitional one.
