# Where the anchors came from, and what that costs

Recorded 2026-09-05. Scripts `analysis/hc2_anchor_provenance_repair.py` and
`analysis/cohortB_tc_anchor_check.py`. Tables `audit/hc2_anchor_provenance.csv`
and `audit/cohortB_tc_anchors.csv`.

Yesterday's anchor audit found two upper critical fields that rise with
temperature and could not say why. The reason is in the deposit's own files.
Every paper in the Cohort B extension carries an `*_HcT_supplementary.csv` whose
`notes` column names the figure each anchor was read from, and for several
papers that figure does not measure a critical field. The `Hc2_source` string in
the fits file records only a temperature and a term, and the term is asserted
rather than derived.

An independent review cut the first version of both results. Its findings are
folded in below and the corrected numbers are larger, not smaller, in one place
and smaller in another. Where a count is a floor rather than a total, it says so.

## The rule, fixed before the tables were read

A named source figure supports an anchor only as strong as what it measures.

| the figure measures | the strongest field it supports |
|---|---|
| a phase diagram, a stated upper critical field, or resistivity, susceptibility or magnetisation against **temperature** in an applied field | Hc2 |
| a Jc-versus-field curve, a magnetisation loop against **field**, a pinning-force curve | an irreversibility field, however the row labels it |
| anything else, or literature data from other samples | nothing |

A row is over-claimed when its recorded term is stronger than its own named
figure supports. An `ambiguous_label` row counts as claiming an Hc2, because the
fits file consumes its value in the Hc2 slot whatever the label says. Ranking it
at zero, as the first version did, made the least certain class the one class
that could never be flagged.

## What the 166 anchor rows rest on

| the named figure is | rows |
|---|---:|
| a phase diagram or a critical field against temperature | 78 |
| a Jc-versus-field or magnetisation-versus-field curve, or a pinning force | 41 |
| a body-text statement that names a field | 11 |
| **a figure of literature data from other samples** | 5 |
| **the relaxation-rate figure** | 5 |
| **a body-text note that names no field** | 9 |
| **no source at all** | 17 |

Fifty-four captions were located in their own paper. Two were not, and both are
notes that describe a figure rather than quote its caption. Six were checked
against a PDF that the check itself found is a different paper: the file held
under `10.1016/j.jallcom.2023.170146` prints `doi:10.1016/j.physc.2009.11.051`
on its first page, which confirms from the document itself the filing error
recorded on 2026-09-04.

## The two rising ladders

Neither paper reports a critical field of any kind. The script locates the
absence on every run: the strings `upper critical` and `irrevers` do not occur
in `physc.2009.11.051` or in `physc.2010.05.048`.

| | physc.2009.11.051 | physc.2010.05.048 |
|---|---|---|
| what the ladder is sourced from | the relaxation-rate figure, S against H | Fig. 2, the magnetisation loops |
| recorded term | **`Hc2`** | `ambiguous_label` |
| the named figure's temperatures | 5 and 15 K | several |
| temperatures recorded | 2, 5, 10, 15, 20 K | 2 to 11 K in ten steps |
| the ladder | 2.5 T at 2 K to 5.5 T at 20 K | 3.5 T at 2 K to 25.0 T at 11 K |
| the largest field the paper applies | 5 T | 5 T |

The last line is the harder falsification and it does not depend on my reading
of any figure. Both papers state the same instrument, an MPMS-XL5, and both
Fig. 3 axes run from 0 to 50 kOe, which is 5 T. One recorded value for
`physc.2009.11.051` and five for `physc.2010.05.048` are above the highest field
either paper applies to its sample. They cannot have been read from these
papers.

`physc.2009.11.051` also carries the stronger label. Its rows record
`source_term = Hc2` for a paper in which that quantity is never printed.

Correction to yesterday's note, which said the anchor grid matched the
relaxation-rate figure: the grid 2, 10, 15, 20 K matches **Fig. 3**, the
Jc-versus-field figure, not Fig. 4. So the note names the wrong figure of the
right paper, and Fig. 3 could in principle yield an irreversibility field. The
over-claim stands; "the figure supports nothing" is contestable on that row
alone and is not what the withdrawal below rests on.

## A ladder that runs backwards inside its own file

Twenty-nine rows are contradicted by another row of the same ladder, meaning the
same paper, figure, term, orientation and sample, at a higher temperature. Both
Hc2 and the irreversibility field fall as temperature rises, so those rows are
wrong whatever figure they name. Sorted by how far the inversion runs:

| paper | worst inversion | factor |
|---|---|---:|
| s41598-025-24806-x | 2.0 T at 9.2 K against 20.0 T at 11.0 K | 10.0 |
| matchemphys.2023.128348 | 1.11 T at 10 K against 9.34 T at 15 K | 8.4 |
| physc.2010.05.048 | 3.5 T at 2 K against 25.0 T at 11 K | 7.1 |
| matpr.2019.05.078 | 2.5 T at 5 K against 6.0 T at 20 K | 2.4 |
| physc.2009.11.051 | 2.5 T at 2 K against 5.5 T at 20 K | 2.2 |
| mtphys.2022.100783 | 4.5 T at 18 K against 7.0 T at 21 K | 1.6 |
| physc.2010.03.003 | 113.4 T at 10 K against 114.0 T at 12.3 K | 1.01 |

The last line is digitisation noise on a ladder that is otherwise the right way
up. The first three are not.

The `matchemphys` line is the clearest single defect in the anchor layer, and it
is quoted from the paper on every run of the script. Its eight table rows are
the paper's own sentence: "Jc decreased from 1.11 x10^5 A/cm2 at 10 K to
9.34 x10^5 A/cm2 at 15 K in sample X01". Those are **critical current densities
in units of 10^5 A/cm2, written into the field column as tesla**. No passing fit
uses them: this paper's four fits take the 3.0 T anchor read from its Fig. 5,
which a separate check confirmed against the paper's own Jc = 100 A/cm2
criterion to four per cent. The defect is in the table, not in the cohort.

## Anchors held from a higher temperature

Thirty-three of the 75 passing fits that match an anchor row use a row read at a
different temperature from the fit, and 32 of the 33 hold a value measured at a
**higher** temperature down to the fit's, by up to 13.8 K. Both fields rise as
temperature falls, so this understates the denominator of
`(Hmax - Hmin)/Hc2` and makes a fit easier to pass. Fifteen are
`mtphys.2022.100783`, twelve `s10854-026-16566-9`, five `phpro.2015.06.160`.

This is the same direction as recording an irreversibility field in the Hc2
slot, and it affects more fits. Both errors enlarge the cohort. The reverse
error also exists and must not be described as though it did not:
`s41598-025-24806-x` records 190, 370 and 400 T as `Hc2`, and
`physc.2013.04.060` records 23.6 T at 4.2 K. Anchors that are far too large
shrink the ratio and keep fits out.

## What this costs the cohort

Of the 94 passing field-axis fits:

| | fits | papers |
|---|---:|---:|
| rest on an anchor whose recorded term is stronger than its own figure supports | **29** | 5 |
| rest on a row that names no source, or a figure of other samples' data | **19** | 3 |
| use an anchor held down from a higher temperature | **33** | 3 |
| sit at T/Tc above 0.7 | **19** | 5 |

These sets overlap. Both of the first two are floors: where two rows of a paper
share an anchor value and only one is over-claimed, the fit is counted as
over-claimed, but where the two disagree in class the fit falls out of the
second count.

Per paper, with what is wrong:

| paper | passing fits | the defect |
|---|---:|---|
| `physc.2009.11.051` | 8 | no critical field in the paper; ladder rises; one value above the instrument's maximum; term recorded as `Hc2` |
| `physc.2010.05.048` | 8 | no critical field in the paper; ladder rises by a factor of seven; five values above the instrument's maximum; kilo-oersted axis |
| `physc.2013.04.060` | 8 | three anchors from a figure of other groups' MgB2 data, five from rows with no source named |
| `physc.2009.05.098` | 8 | an 86 T literature default on a kilo-oersted axis; corrected, the span is 0.053 of it and the field clause fails |
| `mtphys.2022.100783` | 20 | 15 anchors held down from a higher temperature; 3 collide with an unsourced row; 8 fits above T/Tc = 0.7 |
| `phpro.2015.06.160` | 6 | the anchor is 9.0 T, exactly the maximum field its own figure states, while the same file records 26 T at 18.9 K from the paper's body text |
| `matpr.2019.05.078` | 2 | `Hc2` recorded from a Jc-versus-field figure |
| `s10854-026-16566-9` | 12 | all twelve anchors held down from 11.0 K |

The `phpro.2015.06.160` line is the one with the largest single consequence and
it is not a provenance point but an arithmetic one. Substituting that paper's
own body-text 26 T for the 9.0 T taken off the axis of a figure that only goes
to 9 T drops the normalised range from 0.778 to 0.269, and all six of its fits
fail the 0.3 bound.

## The applicability window is applied on one clause of two

Eq. (1) is stated to apply where `T/Tc < 0.7` and `(Hmax - Hmin)/Hc2 > 0.3`.
On the fit cohort:

- the field clause partitions it exactly. No passing fit violates it, and
  `physicality = H_axis_applicability_bound` accounts for precisely the 60 fits
  that do.
- the temperature clause is not applied at all. **Nineteen of the 94 passing
  fits sit above T/Tc = 0.7**, the worst at 0.955, across five papers.

`Tc_K_anchor` appears nowhere in the repository as a screen on this cohort. The
scripts named `apply_temperature_window_gate.py` and
`build_reporting_exclusions.py` gate the dispatch and prediction tables, not the
fits.

## The Cohort B Tc anchors

The temperature axis turned out to rest on a compound-keyed constant declared
paper-reported. The field axis was supposed to be better, because its
`Tc_provenance` reads "paper-reported (Cohort B extraction)" and 19 of its 62
papers have a PDF here. All nineteen were opened. Each reading below is a phrase
the script locates in the paper, so none of it rests on a report that cannot be
reproduced.

| verdict | papers |
|---|---:|
| matches the printed value | 3 |
| matches one of several samples' printed values | 3 |
| **disagrees with every value the paper prints** | **8** |
| the paper prints no Tc for the sample it measures | 2 |
| cannot be checked: one-page deposits, and one PDF that is a different paper | 3 |

The eight that disagree:

| paper | recorded | printed |
|---|---:|---|
| `matchemphys.2023.128348` | 39.0 | 37.7 for all four bulks |
| `jallcom.2013.04.183` | 110.0 | 74.38, 64.11, 66.0, 74.18 |
| `cjph.2024.09.042` | 14.0 | 44.5, 41.0 and 10.0; no sample near 14 K |
| `physc.2010.05.048` | 14.0 | 12.0 |
| `jallcom.2023.170384` | 26.0 | 13.3 |
| `mtphys.2022.100783` | 22.0 | 24.1, 25.7, 24.4 |
| `physc.2009.11.051` | 22.0 | 24.0 |
| `phpro.2015.06.160` | 20.0 | 18.9 and 25.5 |

Four of the eight are a literature value for the family rather than the sample:
26 K is LaFeAsO(1-x)Fx, 22 K is the title of Sefat's paper on Co-doped BaFe2As2,
39 K is MgB2. In two of those the number is physically present in the PDF, inside
a reference title or a comparison sentence. This is the same defect as the
temperature axis's 38.0 K, in a cohort whose provenance was supposed to be
per-paper.

Two of the errors change a gate. `physc.2010.05.048`'s 9 K fit sits at
T/Tc = 0.643 against the recorded 14 K and at **0.75 against the paper's 12 K**,
so the Tc error is what keeps it inside the temperature window, in the one place
that window is quoted.

## What was checked and did not hold

- The first version of the caption check compared a note's words against the
  whole document with the separators stripped. It returned yes for an invented
  caption naming a figure the paper does not have, and yes for one paper's
  caption checked against another paper. It now finds the figure number first
  and compares only the window after it, and the script carries a self-test that
  plants both known-bad inputs and requires a no. `--selftest` runs it.
- The first version trusted the PDF filename. One file in this corpus is not the
  paper it is filed under, and it is a paper this audit reports on. The DOI
  printed on the document is now compared with the identifier before its text is
  used.
- The within-file monotonicity test first compared every row of a paper against
  every other, which flagged 65 rows, most of them legitimate: a c-axis field is
  smaller than an ab-plane field at a higher temperature, and a strand or a
  pressure is not the same ladder. Restricted to rows sharing a paper, figure,
  term, orientation and sample, it flags 29.
