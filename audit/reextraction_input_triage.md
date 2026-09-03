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

## The result, after every page in the first row was opened

The first pass was an automated prediction. All 26 papers in its top row have now
been rendered and read. Seven changed row, so the probe held on 19 of 26.

| verdict | papers | what you do |
|---|---|---|
| nothing needed | 19 | page found, figure in colour, legend keys temperature; confirm the legend I propose |
| series count or temperatures needed | 6 | monochrome, or the temperature is not on the figure |
| page number needed | 13 | no figure caption found, caption on a caption-list page, or the caption points at the wrong plot |
| borderline | 1 | current density only on a secondary axis |
| already measured | 2 | 2012.13723, 2207.06629 |

Per paper, with what was actually seen on each page:
`audit/reextraction_input_triage.csv`.

### The seven that changed, and why

- `1801.05074v1` p4 has **no Jc plot at all**. Its Fig. 2(b) puts 1/J on the x
  axis, which is what the colour probe scored. Withdrawn temperature-axis paper.
- `10.1016/j.cjph.2024.09.042` p6 Fig. 5 plots the **anisotropy ratio**
  gamma = Jc(H parallel c) / Jc(H perpendicular c), a dimensionless quantity, not
  Jc. Its Hc2 figure on p9 is genuine, so only the Jc half needs a page.
- `2510.10264v1` p5 (a) and (b) are log-log Jc(B) fans of about fifteen colour
  curves with **no legend**. Only the end members are labelled: 2.5 K and 20 K in
  (a), 2 K and 16 K in (b). The intermediate temperatures are not on the plot.
- `10.1016/j.ceramint.2024.10.058` p5 Fig. 4 has a legend keying sample name
  (LSCO-CS, Vac-1, Vac-2, Nitrogen-1, Nitrogen-2) and **no measurement
  temperature anywhere on the figure**. The 5 K in the paper belongs to Fig. 3.
- `10.1016/j.physc.2014.03.020` p2 Fig. 2(b) keys sample (wire, HIP wire); 4.2 K
  appears only in panel (a) corner text.
- `1612.02839v1` p9 Fig. 6(a) uses **colour for sample condition** (as-grown
  black, annealed red) and in-plot text for temperature (5 K, 13.5 K), so colour
  and temperature are decoupled and a colour-keyed read would mislabel it.
- `1108.5583v3` p2 plots dB/dx (G/um); j (kA/cm2) is only a right-hand twin axis.

The pattern behind five of the seven is the same one the archive precision work
found: **the legend keys something other than temperature.** Colour separability
and temperature labelling are independent properties, and the probe only measured
the first.

### The two monochrome ones

- `10.1016/0921-4534(96)00225-0` p4 Fig. 5. Bean critical current against field,
  linear y, three series, legend keys doping (CeO2, PtO2, CeO2+PtO2) rather than
  temperature. 77 K comes from the caption. This is a Tier-3 paper, so it matters.
- `0903.0004v2` p4 panel (b). jc against field, log y, three series, legend
  2 K / 5 K / 10 K as open square, diamond and triangle.

### The thirteen that need a page

`0904.2442v1`, `1002.0248v1`, `1003.0946v2`, `1104.0477v2`, `1611.08455v1`,
`1801.05074v1`, `2110.15577v1`, `10.1016_j.cjph.2024.09.042`,
`10.1016_j.jpcs.2026.113652`, `10.1038_s41467-025-55880-4`,
`10.1016_j.physc.2009.03.028`, `10.1016_j.physc.2009.05.098`,
`10.1016_j.physc.2011.02.004`.

Reasons differ:

- `1002.0248v1` p8, `2110.15577v1` p7 and `1611.08455v1` p15 are arXiv preprints
  whose captions sit in a caption list with the figures further on. A page number
  fixes it.
- `10.1016_j.physc.2009.05.098` and `10.1016_j.physc.2011.02.004` are archived as
  the first page only and cannot be measured from what is on disk. `1002.0208v2`
  is the same paper as the second and is complete, so use that and drop the DOI
  copy, which also removes a duplicate that currently breaks independence in the
  leave-one-paper-out.
- `10.1016_j.physc.2009.03.028` p4, `10.1016_j.cjph.2024.09.042` p6 and
  `1801.05074v1` p4 have a Jc caption pointing at a page whose plots are not Jc.

Six of the thirteen are withdrawn temperature-axis papers, so they are the lowest
priority in the set.

## What this does not establish

Every page in the first row has now been opened, so the 19 rest on a reading of
the figure rather than on the probe. What they do not rest on is a measurement:
each still needs its legend confirmed before anything is digitised, because a
wrong colour silently relabels an isotherm.

The probe's measured precision on this task was **19 of 26**. It scores colour
separability, which is necessary and not sufficient: five of its seven misses are
figures where the legend keys sample, doping or condition rather than
temperature, and two are pages whose colour came from something that is not a Jc
plot at all. A high saturated pixel count can come from a photograph: on
`10.1016_j.physc.2009.03.028` the 411334 saturated pixels are magneto-optical
frames.

The 13 in the third row have not been exhaustively searched. Each was checked at
the page its caption pointed to; a Jc figure could still exist elsewhere in those
papers.

Two defects in the probe, both worth fixing before it is run over the wider
archive:

- `find_axes_boxes` does not terminate in any reasonable time on a raster scan
  (`10.1016_j.physc.2009.03.028` p4), because a scanned page is full of long dark
  runs. It needs a candidate cap or an early bail on page darkness.
- The colour count is a count of quantisation bins, not of series. Anti-aliasing
  puts three to four bins on one plotted colour, so the number is usable as a
  colour-versus-monochrome discriminator and not as a series count.
