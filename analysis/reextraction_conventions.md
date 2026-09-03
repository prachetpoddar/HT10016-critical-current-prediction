# Conventions for the figure re-measurement

## legend_temperatures

Ordered by **Jc at the point nearest the left-hand side of the x axis, highest
first**, not by the legend's printed order.

This is the ordering the extractor uses. It ranks the curves it measured by
their Jc at the leftmost sampled column and pairs them against this list by
rank, so no colour ever has to be matched to a piece of legend text. That
pairing was the step most likely to mislabel an isotherm silently, and this
removes it.

Verified on two figures. 2012.13723 FIG. 4 ranks 1.93, 1.79, 1.45, 1.13, 0.71,
0.31, 0.14 x 1e6 for 4 through 28 K, so rank order and temperature order agree
and all seven label correctly. 2207.06629 Figure 4 does not: its black 4 K curve
measures 2.82e6 against a stated 3.9 MA/cm2 and so ranks below the 8 K curve at
3.23e6, which would swap the two labels.

Two guards follow from that second case:

- adjacent ranks within about 20% are treated as ambiguous and refused rather
  than assigned, which would have caught the 14% gap above;
- black series are excluded until the tick-contamination defect is fixed, since
  a mismeasured curve under rank matching becomes a mislabelled one, and a wrong
  label is harder to notice than a wrong number.

**Where the convention needs care.** It assumes one sample per panel. A panel
showing an as-grown and an annealed crystal at the same temperatures has
interleaved ranks, so rank order is not temperature order. Say so in `notes`,
and give that panel its own row.

## panel

The sub-panel letter holding the Jc isotherms. Blank when the figure is a single
plot. One row per panel: if two panels are different samples, orientations or
substrates, they need separate rows, because merging two panels under one key is
how the polycrystal and single-crystal series ended up identical in the current
deposit.

## x_axis and y_axis

`linear` or `log`. Blank if unsure, which is better than a guess: the tick
detector reads the axis type from tick geometry, and a wrong axis type is a
silent calibration error.

Usually x is linear and y is log. The exceptions found so far are 1002.0208
FIG. 5(b) and 2510.10264 FIG. 4, both of which have a log field axis.

## n_series

The number of curves in that panel, which should equal the count of entries in
legend_temperatures. It is a cross-check rather than an input: if the colour
probe finds six curves where you wrote seven, that says one is being missed
instead of letting six be extracted and called complete.

Count every plotted curve. Two samples at two temperatures each is 4, not 2.

## One row per figure, not per paper

The first manifest keyed what was needed off each paper's role, so the twelve
Tier-3 papers were listed as needing only a critical-field figure and their Jc
figures went unmentioned. That is backwards: those twelve carry all 34 of the
field-axis fits pinned at the exponent ceiling, so their Jc curves are the
higher priority and their critical fields the lower one.

10.1016/0921-4534(96)00225-0 is the case that exposed it. Fig. 5 on page 4 is
"Jc (A/cm2) vs. the applied field in T ... associated to the Bean model at 77 K
and with the H||c-axis configuration", which is precisely the measurement
wanted, and the manifest had asked for something else entirely. Its three fits
are all at the ceiling on a normalised field window of 0.038, and that window is
0.038 only because the critical field is a 130 T literature default rather than
anything this 77 K melt-textured YBaCuO sample was measured against.

A paper can therefore appear more than once, once per figure it owes.
