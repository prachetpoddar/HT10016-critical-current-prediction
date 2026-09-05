# The Hc2 anchors, and what a hand extraction does differently

Recorded 2026-09-05. Both results below were overstated in their first form and
an independent review cut each roughly in half. The corrected versions are
smaller and both still stand.

## A. The Hc2 anchors

Whether a field-axis fit clears Eq. (1) is (Hmax - Hmin)/Hc2, so the anchor
decides membership of the cohort. The temperature axis turned out to rest on a
compound-keyed constant presented as paper-reported; this asks the same of the
field axis, where the provenance is better.

### Two anchors rise with temperature

An upper critical field falls with temperature and vanishes at Tc. Within one
sample:

| paper | anchor by temperature | rank correlation |
|---|---|---|
| physc.2010.05.048 | 3.5 T at 2 K to 12.5 T at 9 K, seven consecutive rises | +1.00 |
| physc.2009.11.051 | 2.5 T at 2 K to 5.5 T at 20 K | +1.00 |

I first reported five samples. Two of the five were the same ladder counted
twice under `irradiated` and `unirradiated`, which carry identical anchors, and
two more were `mtphys`, whose Polycrystal and Single crystal rows are a
documented duplicate and whose anchor is flat at 4.5 T with a single step at
21 K. Three ladders, two of them real.

### Current above the anchor

I first reported 48 of the 94 passing fits, over 9 papers, as having data that
reaches or passes its own Hc2. That was wrong in four ways, each of which the
review isolated and each of which is now screened in code:

| screen applied | fits | papers |
|---|---:|---:|
| as first reported | 48 | 9 |
| the trace's series matched to the fit's own sample, and traced points sitting on the frame or on a tick dropped | 45 | 9 |
| sources the repository itself grades as inventing high-field points removed | 23 | 8 |
| the anchor required to have been read at the data's own temperature | **19** | **6** |
| the anchor required to be labelled `term_Hc2` rather than an irreversibility field | **6** | **2** |

Only the last line is impossible. An anchor recorded as an irreversibility field
is a criterion, not a hard bound, and `matchemphys.2023.128348` refutes the
stronger claim outright: extrapolating its traced curves to that paper's own
Jc = 100 A/cm2 criterion gives 3.14 T against a recorded 3.00, agreement to four
per cent. The anchor is confirmed, not contradicted.

The six that survive every screen are two fits of `matpr.2019.05.078`, whose
curve runs to 1.87 times its anchor, and four of `physc.2009.11.051`, at 1.97.

**And none of this contaminates a fit.** The fitter filters H < Hc2 and the
largest normalised range among the 94 is 0.999. This is evidence about the
anchor, not about the points any fit was made from.

### One test withdrawn

I reported eight papers implying dHc2/dT below 0.5 T per kelvin, against a
stated range of 1 to 5. That test does not work. It computes a chord rather than
a slope, it is monotone in which row is picked (0.125 at 2 K rising to 2.750 at
20 K for one sample), the 1-to-5 range is contradicted by the deposit's own
best-provenance anchors at 0.55 and 0.80, and seven of the eight papers were
already named by the other tests. It is withdrawn.

### What does stand on provenance alone

Eight passing fits rest on an anchor whose term the deposit itself records as
`ambiguous_label`, all of them `physc.2010.05.048`. Eight more rest on an 86 T
literature default, all `physc.2009.05.098`. Both facts are in the deposit and
need no figure.

## C. What the hand extractions do differently

Eight hand-digitised extraction files against nineteen vision-pass files, on
properties that need no figure. Two separate the routes and they are not equally
useful.

**Significant figures separates completely and is nearly worthless.** Hand files
carry two significant figures or fewer on 0.00 to 0.02 of their values; vision
files on 0.05 to 1.00, median 1.00. But rounding the three good hand files to two
significant figures on export flips all three into the vision range, while
degrading their agreement with their own figures by 0.002 to 0.004 dex and
moving beta_H by 0.005 in log, twenty times below the deposit's own quoted error.
Within the vision arm it does not predict agreement at all: rank correlation
0.16, p = 0.74. It identifies who wrote the file. That is useful for triage and
useless as a quality test.

**Non-monotonicity separates in the direction that matters and cannot be faked.**

| | files | median isotherm ever rises with field |
|---|---:|---|
| vision | 19 | **none of them** |
| hand | 8 | three, at 0.97, 0.89 and 0.74 |

A measured Jc(H) in these materials shows a second peak. An isotherm that never
once rises with field is a claim about the sample, not a neutral reading. Every
vision file in this corpus makes that claim; three of eight hand files do not.

The separation is not a multiple-comparisons artefact: permuting the route
labels twenty thousand times, the probability that any of the seven properties
separates cleanly is below one in twenty thousand.

## The checklist this gives

For a new extraction, before anyone reopens the figure:

1. Does any isotherm rise with field anywhere? If none does, ask why.
2. Does the field range cover the printed axis, or a corner of it? Hand files
   here span a median of 2.1 decades against the vision files' 1.0.
3. How many points per isotherm? Hand files here carry a median of 20, vision
   files 6.
4. Is the axis unit the one printed on the page? Two of the eight hand files
   fail this, and it is the single most damaging error in the corpus.
5. Is the file named for the paper it came from? One of the eight hand files
   fails this too.

Points 4 and 5 are the two failures that hand digitisation has actually produced
here. Neither is a reading error and neither would be caught by any of the tests
above.

---

## Superseded, same day

Section A above says the two rising ladders could not be explained. They can.
The deposit's own `*_HcT_supplementary.csv` files name the figure each anchor
was read from, and neither of these two names a critical-field figure. Neither
paper prints a critical field at all, and six of the recorded values are above
the highest field either paper applies to its sample. See
`audit/anchor_provenance_repaired_20260905.md`.

Two statements above are corrected there:

- the claim that the `physc.2009.11.051` grid matches the relaxation-rate
  figure. The grid 2, 10, 15, 20 K matches that paper's Fig. 3, the
  Jc-versus-field figure. The over-claim stands; "supports nothing" does not.
- the screen "the anchor required to be labelled `term_Hc2`", which treated
  `ambiguous_label` as the weaker claim. The fits file consumes those values in
  the Hc2 slot, so the effective claim is an Hc2 and the screen was letting the
  least certain class through.
