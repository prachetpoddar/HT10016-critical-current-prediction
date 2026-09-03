# What the archive Jc screen actually found, and what it is worth

The screen (`_jc_screen/screen.py`, run on the user's machine) reads the text
layer of every PDF in the archive, finds figure captions, and grades each paper
by what the caption says the figure plots. It is a caption screen. It has never
looked at a figure.

    2597 unique PDFs screened

    A  Jc vs field, multiple isotherms      422
    B  Jc vs field, few isotherm labels      62
    C  Jc vs temperature only                64
    D  Jc figure caption, axis not named    418
    E  no Jc figure caption                 1631

966 papers carry a Jc figure caption; 671 of those also carry a current-density
unit string.

## Recall

17 of 17 on the papers whose figures have been opened by hand in this audit.
Three regex defects were found and fixed while establishing that: newlines were
not collapsed, so every caption that wrapped across a line was missed; the
superscript in `A/cm2` is dropped by `pdftotext`, so requiring it rejected real
captions; and "critical currents" without the word "density" was not matched.
Units were demoted from a gate to a confidence flag.

## Precision, measured

20 grade-A papers were drawn at random from the 414 outside the fit cohort
(seed 20260903), their figure pages rendered, and each figure read by eye.

**All 20 carry a real plotted critical-current figure.** There are no caption
false positives in the sample. One of the 20 (`9804161v1`) plots a critical
current `Ic` for a grain-boundary junction rather than a current density, so on
the strictest reading it is 19 of 20.

That is not the number that matters. The grade-A label claims *Jc against field
with multiple isotherms*, and that claim is much weaker than the caption
suggests:

| what the figure actually is | papers |
|---|---|
| Jc against field, three or more measurement temperatures | 7 |
| Jc against field, two measurement temperatures | 4 |
| Jc against field, one measurement temperature | 7 |
| Jc against temperature, not field | 2 |

The recurring reason is that the legend names something other than temperature.
In 8 of the 20 the legend keys doping level, sample name, pressure, sintering
temperature or substrate misorientation, and the measurement temperature appears
once, as free text in the corner of the panel. The screen counted the temperature
tokens in the caption and could not tell the difference.

So `n_temperature_labels` in the screen output measures captions, not isotherms.

**Scaled to the archive.** 7 of 20 gives 35% of grade-A papers carrying three or
more isotherms on a field axis: about 148 of the 422, with a Wilson 95% interval
of roughly 76 to 240. The pool available to the field-axis exponent work is
therefore of order one hundred and fifty papers, not four hundred.

## Three papers that looked like screen failures and were not

`0507652v1`, `1310.1613v1` and `MgB2_0104395` came back from an automated probe
with no detected axes box and no series colours, which looked like the screen
having graded a paper A that has no figure. All three were opened.

- `0507652v1` Figure 5: Jc against applied field, log y, two stacked panels at
  6 K and 20 K, four samples. Real.
- `1310.1613v1` FIG. 4: Jc against H, log y, six isotherms for H parallel c and
  three for H parallel ab. Real, and in colour.
- `MgB2_0104395` Figure 8: jc against field, log y, four panels, twelve
  isotherms each from 7.5 to 35 K. Real.

The failure was in the probe, and it is two separate defects.

**Monochrome figures return no series colours.** `series_colours` keeps only
non-grey colours, so a figure whose series are distinguished by filled and open
markers returns an empty list and reads as "no figure". Six of the 23 figures
read by eye in this audit are monochrome. Series separation on those needs
marker shape, which the digitiser does not currently do.

**Frame detection is scale-sensitive in the wrong direction.** `find_axes_boxes`
finds the frame of `0507652v1` p17 at render scale 3 and not at 4 or 6, and
`MgB2_0104395` p9 at 3 and 4 and not at 6. A hairline frame stays one pixel wide
however far the page is scaled up, so the run it must form gets longer while its
anti-aliased gaps stay, and the 85% coverage test fails. Any batch run of the
builder must sweep scale rather than fix it.

A third, smaller defect: an earlier probe reported that `1310.1613v1` yielded Jc
caption pages under `pdftotext` but none under pymupdf. That was wrong. Both
extractors find FIG. 4 on page 4. The probe had been matching captions
block-anchored on one route and flat on the other.

## What follows

The caption screen is sound and should be kept. What cannot be taken from it is
a count of usable figures, because a caption naming Jc and a field says nothing
about how many isotherms the plot carries or what its legend keys. A figure is
usable for a field-axis exponent only when it has been opened.

Two changes to the builder before any batch run:

- sweep render scale rather than fix it, and
- add marker-shape separation, or declare monochrome figures out of scope and
  count them, which on this sample is about a quarter of the pool.
