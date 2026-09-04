# The four rows marked "withdrawn (re-extract)"

Recorded 2026-09-04. `audit/repair_plan.csv` marks four anchor rows
"withdrawn (re-extract)" and none of them has been acted on. Both source papers
are in `phase_3_p19_elsevier_pdfs/`, so both were read.

Neither needs re-extracting in the sense the label implies. One paper contains
no such measurement at all, and the other was misread in a way that a
re-extraction alone would not catch.

## 10.1016/j.physc.2011.05.018 — the extraction has no source

The paper is a magneto-optical imaging study. Its five figures are X-ray
diffraction with a transition-temperature curve, optical images of the two
samples, differential magneto-optical images, local magnetic induction profiles,
and magneto-optical images of flux penetration. **There is no
critical-current-versus-field figure.**

It reports one critical current density, twice: "Jc calculated from M-H curve is
estimated to be 5 x 10^4 A/cm2 at 5 K under zero field for sample resintered at
680 C, while the Jc for the sample resintered at 600 C is a little larger", and
"Jc is estimated to be 5 x 10^4 A/cm2 at 5 K for both samples". The evaluation
is by the Bean model "with the assumption of field-independent Jc", which is the
paper saying in as many words that it has no field dependence to report.

The deposit holds twenty extracted points for this paper, two samples at 2 K and
5 K, over 0 to 20 T for one sample and 0 to 50 T for the other. Fifteen distinct
values across those twenty points, in exact arithmetic ladders:

    600 C, 2 K   50000  48000  46000  44000  42000     step 2000
    600 C, 5 K   20000  19000  18000  17000  16000     step 1000
    680 C, 2 K  100000  95000  90000  85000  80000     step 5000
    680 C, 5 K   50000  48000  46000  44000  42000     identical to 600 C, 2 K

A Jc(H) curve does not fall linearly, and one of the four is a copy of another.

Its two anchors are log10 4.698970 and 5.000000, which are 5x10^4 and 1x10^5
exactly, both recorded at 2 K and zero field. The paper gives 5x10^4 at 5 K for
both samples.

Its upper-critical-field row is invented too. It cites "Fig. 2 (c) and (d) show
corresponding magnetic hysteresis curves for samples reinserted at 680 C and
600 C". Fig. 2 of that paper is optical images and has no panels (c) or (d), and
the paper reports no critical field anywhere. This is one of the eight papers
the dual-model audit put in `AGREE_NO_DATA`, where both extraction models
independently found no critical-field data, and it is the one of those eight
that contributes no field-axis curve.

Nothing here can be re-extracted, because there is nothing to extract. The
damage is confined to two anchor rows; the paper contributes no field-axis fit
and has no row in the provenance table.

## 10.1016/j.physc.2009.11.051 — real data, read off the wrong axis

Fig. 3 is a genuine critical-current-versus-field figure: eight curves,
unirradiated broken and irradiated solid, at 2, 10, 15 and 20 K, on a
logarithmic Jc axis from 10^3 to 10^7.

Its field axis is **H (kOe), 0 to 50**, which is 0 to 5 tesla.

The deposit records this paper's fields as 0.2 to 20 with the unit tesla. Read
as kilo-oersted, which is what the axis says, those are 0.02 to 2 T. This is the
same defect the supplement already documents for five other papers, where
kilo-oersted was recorded as tesla, a factor of ten. This is a sixth.

The magnitudes are wrong as well, and not by a constant. The paper states that
Jc is "about 6.4 x 10^5 A/cm2 at T = 5 K under zero field" unirradiated and
"reaches 4.0 x 10^6 A/cm2" irradiated. The deposited 2 K anchors are 1.0 x 10^6
irradiated and 6.0 x 10^5 unirradiated. The unirradiated one sits close to the
figure's unirradiated 2 K curve, which starts near 8 x 10^5. The irradiated one
is about five times below the figure's irradiated 2 K curve, which starts near
5 x 10^6. The irradiated series appears to have been read off the unirradiated
lines.

**The upper critical fields attached to this paper are the worst of it.** The
fits use 2.5, 4.5, 5.0 and 5.5 T at 2, 10, 15 and 20 K. An upper critical field
falls with temperature; these rise. The supplementary row that supplies them
says they come from "Field dependence of interpolation index S at 5 K and 15 K",
which is Fig. 4, the magnetic relaxation rate, not a critical field measurement
at all, and it lists five temperatures where the figure it cites has two. They
carry `Tier_1_per_paper_data` and reach the fit table as
`Tier_1_direct_match_at_2.0K_term_Hc2`, which is the highest-confidence
provenance the deposit has.

Eight field-axis fits rest on this, and they pass the applicability filter with
normalised spans of 0.36 to 0.87. The span is the measured field range over the
resolved critical field, and both come from the same misreading, so whether the
ratio survives a unit correction cannot be settled from the numbers: the
critical fields are not merely in the wrong unit, they are from the wrong
figure.

## What this means beyond these two papers

The provenance tier is not evidence. `Tier_1_per_paper_data` means an extraction
said the value came from the paper, not that anyone checked it did. Here one
Tier 1 value is read from a relaxation-rate figure and another cites a figure
panel that does not exist. Table S1's "Paper-reported Hc2" column counts these
tiers, and `analysis/build_supplement_tables.py` already disagrees with the
printed column, 13 against 22, for a related reason.

## What is decided and what is not

Nothing is changed by this note. The dispositions that follow from it:

  1. `physc.2011.05.018` has no field-dependent critical current to extract. Its
     two anchor rows and its critical-field row rest on nothing.
  2. `physc.2009.11.051` has real data on a kilo-oersted axis. Its curves can be
     re-extracted; its critical fields cannot be repaired by re-extraction,
     because they are from a figure that does not measure them.
  3. Whether the other Tier 1 critical fields in the deposit were checked
     against their cited figures is not known. Two of two examined here were
     not.
