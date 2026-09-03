# What each paper actually needs from you before it can be re-measured

The manifest asked for a page, a figure number, a panel, two axis types, a series
count and a legend for all 41 PDFs. Most of that does not have to be typed.

One property decides it: **whether the series are separable by colour.** If they
are, the page can be found from the caption, the axis types come from tick
geometry, the series come from the colours and the legend is read off the render,
so nothing needs to be entered. If they are not, colour separation returns
nothing and a visual count of overplotted black curves is exactly where reading a
figure has been shown to wobble, so the series count and the temperature list
have to come from you.

    python analysis/reextraction_input_triage.py out.json 0 41

finds the caption pages, renders each at scale 4, locates the plot frame and
counts distinct saturated colours inside it and on the page. Calibration: the two
figures already measured score 45909 saturated pixels with 6 distinct colours
(2012.13723 FIG. 4, seven coloured isotherms) and 19695 with 8 (2207.06629
Figure 4, seven coloured plus one black).

## The result

| verdict | papers | what you do |
|---|---|---|
| nothing needed | 26 | the page is found and the figure is in colour; confirm the legend I propose |
| series count and temperatures needed | 2 | monochrome figure |
| page number needed | 11 | no figure caption found, or the caption sits on a caption-list page |
| already measured | 2 | 2012.13723, 2207.06629 |

Per paper: `audit/reextraction_input_triage.csv`.

### The two monochrome ones

- `10.1016/0921-4534(96)00225-0` p4 Fig. 5. Bean critical current against field,
  linear y, three series, and the legend keys doping (CeO2, PtO2, CeO2+PtO2)
  rather than temperature. 77 K comes from the caption. This is a Tier-3 paper,
  so it matters.
- `0903.0004v2` p4 panel (b). jc against field, log y, three series, legend
  2 K / 5 K / 10 K as open square, diamond and triangle.

Both were read by eye, so what is written above is the metadata; what is still
needed is your confirmation that the series count is right, because that is the
number a monochrome figure can lose.

### The eleven that need a page

`0904.2442v1`, `1002.0248v1`, `1003.0946v2`, `1104.0477v2`, `1611.08455v1`,
`2110.15577v1`, `10.1016_j.jpcs.2026.113652`, `10.1038_s41467-025-55880-4`,
`10.1016_j.physc.2009.03.028`, `10.1016_j.physc.2009.05.098`,
`10.1016_j.physc.2011.02.004`.

Three distinct reasons, and they need different things:

- `1002.0248v1` p8, `2110.15577v1` p7 and `1611.08455v1` p15 are arXiv preprints
  whose captions sit in a caption list with the figures further on. The caption
  route lands on the list rather than the plot. A page number fixes it.
- `10.1016_j.physc.2009.05.098` and `10.1016_j.physc.2011.02.004` are archived as
  the first page only. Neither can be measured from what is on disk.
  `1002.0208v2` is the same paper as `physc.2011.02.004` and is complete, so use
  that one and drop the DOI copy, which also removes a duplicate that currently
  breaks independence in the leave-one-paper-out.
- `10.1016_j.physc.2009.03.028` p4 carries magneto-optical frames and one M-H
  loop. There is no Jc plot on the page the caption points to.

Five of the eleven (`0904.2442v1`, `1002.0248v1`, `1003.0946v2`, `2110.15577v1`,
`1204.0339v2`) are withdrawn temperature-axis papers, so they are the lowest
priority in the set.

## What this does not establish

Of the 26 in the first row, 5 were opened and read by eye this session. The other
21 rest on the colour probe alone, calibrated on two figures. A high saturated
pixel count can come from a photograph rather than a plot: on
`10.1016_j.physc.2009.03.028` the 411334 saturated pixels are magneto-optical
images, and that paper is only in the third row because it was opened. So treat
"nothing needed" as a prediction that the first render will confirm or not, and
expect a few to fall back into the other rows.

Two defects in the probe, both worth fixing before it is run over the wider
archive:

- `find_axes_boxes` does not terminate in any reasonable time on a raster scan
  (`10.1016_j.physc.2009.03.028` p4), because a scanned page is full of long dark
  runs. It needs a candidate cap or an early bail on page darkness.
- The colour count is a count of quantisation bins, not of series. Anti-aliasing
  puts three to four bins on one plotted colour, so the number is usable as a
  colour-versus-monochrome discriminator and not as a series count.
