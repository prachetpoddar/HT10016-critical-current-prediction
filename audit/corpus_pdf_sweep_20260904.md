# A filename-versus-content sweep of every PDF, and what it found

Recorded 2026-09-04. Nothing in the data changed.

Asked to list the papers that still need surfacing, the right first step was to
confirm they are not already here. They mostly were. The DOI-named search used
until now missed them because they are filed under other names.

## The sweep

Every one of the 113 distinct PDFs in the corpus was opened, its first two pages
read, and every DOI in that text compared against the DOI in its filename.

**Exactly one PDF fails**: `10.1016_j.jallcom.2023.170146.pdf` carries the
internal DOI `10.1016/j.physc.2009.11.051`. It is Tamegai et al., Physica C 470
(2010) S360-S362, the paper already established as printing a kilo-oersted axis.
No two PDFs are byte-identical, so nothing else is a silent duplicate.

## Three of the four "missing" papers were here

| wanted | found as | pages |
|---|---|---|
| `physc.2011.02.004` Bhoi, PrFeAsO0.60F0.12 | **`1002.0208v2.pdf`** (the arXiv preprint) | 8 |
| `s41598-025-24806-x` Cu-substituted FeTeSe | **`10.1038_s41598-025-24806-x.pdf`** | 15 |
| `physc.2009.05.098` Tamegai, SmFeAsO | only the 1-page stub, in three places | 1 |

## What reading them settled

**`physc.2011.02.004` is resolved and sound.** FIG. 5(a) of the preprint plots
J_L in A/cm2 against **H in tesla**, 0 to 16 T, over 5 to 35 K. The extraction
matches at every endpoint, and the 30 K series stops at 7.95 T where the printed
curve dies. Six passing fits cleared by reading rather than by inference.

**`s41598-025-24806-x` is a new kilo-oersted paper.** Fig. 5 plots jc_ab against
**H_int in kilo-oersted**, 0 to 46 kOe, which is 4.6 T. The extraction records
0, 10, 20, 30, 40 into a `field_T` column: a factor of ten, the same defect as
`physc.2009.11.051` and `physc.2010.05.048`. Everything else about the record is
competent. The three Tc values 13.0, 17.6 and 12.8 K match the caption exactly,
and the odd temperatures 5.07 and 6.86 K are 0.39 Tc for each sample, which is
what the paper specifies. Two anchor rows, no field-axis fits. This was the last
unread flagged file, and the first pass called its PDF absent twice.

**The MgB2 source behind `jallcom.2023.170146` is identified by citation.**
Reference 22 of `10.1007_s10854-026-16870-4` is Arvapalli, Miryala, Jirsa, Sakai
and Murakami, *Pinning behavior in bulk MgB2 prepared using boron powder refined
via high-energy ultra-sonication*. The journal name is broken across a page in
that PDF, so it cannot be read out here. The paper itself is not in the corpus.

## Where the field axes now stand

| unit class | papers | passing fits |
|---|---:|---:|
| tesla, read | 12 | 58 |
| kilo-oersted, read | 3 | 16 |
| oersted, read | 1 | 0 |
| gauss, read | 1 | 2 |
| probable kilo-oersted, inferred | 1 | 8 |
| consistent with tesla, inferred | 1 | 6 |
| no field figure | 1 | 0 |
| MAGLAB, not a printed figure | 9 | 4 |
| unverifiable | 2 | 0 |

The 22 passing fits on unread axes are now 14, and only one paper needs a
document nobody here has.

## Still needed

1. **Physica C 469 (2009) 915-920**, Tamegai et al., pages 2 to 6. Eight passing
   fits and nine anchor rows turn on whether its axis is kilo-oersted.
2. **Confirmation of what DOI 10.1016/j.jallcom.2023.170146 is**, and its PDF, so
   the MgB2 record can be tied to a paper.
