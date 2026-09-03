# The six Bi2.1Sr1.9CaCu2O8 field-axis fits are not readings of their source

`10.1038/s41467-025-55880-4` contributes 36 deposited curve points and 6
field-axis fits. The paper cannot support them.

## What the paper is

It is a superconducting-diode-effect study on exfoliated Bi2Sr2CaCu2O8+d flakes,
53.5 nm and 23.8 nm thick, patterned into devices s1, s6 and s8. Its measured
quantities are the two polarity-dependent critical currents Ic+ and |Ic-|, in
**microamps**: 51.3 uA against 32.7 uA in Fig. 2b, an asymmetry of 26 uA in
Fig. 3b, 75 uA in Fig. 4c. Its field sweeps run to **25 mT**.

Over the whole 8-page text:

    occurrences of "A/cm"            0
    occurrences of "current density" 0

There is no current density in the paper, in any units.

## What the deposit says

`data/extraction_examples/s41467_025_55880_4_field_axis.csv`, 36 rows, all
`extraction_method = vision_pass_round3`, all `confidence = High`:

| field | value |
|---|---|
| Jc_A_per_cm2 | 195000 to 350000 |
| temperature_K | 30.0, 53.0, 75.5 |
| field_T | 0.01 to 0.25 |
| doping_or_composition | s1, s2 |
| hc2_T | 100.0 (literature default) |

Four independent contradictions:

1. **The quantity does not exist in the paper.** Jc in A/cm2 against a paper that
   reports only Ic in microamps and never writes a current density.
2. **The field range is an order of magnitude too large.** 0.25 T against a
   paper whose SDE field sweep reaches 25 mT.
3. **The temperatures are lifted from a different discussion.** 53 K is where the
   paper says diode efficiency peaks at 22 per cent, 75 K is where it says the
   efficiency becomes zero, and 30 K is the condition on its typical V-I curves.
   They are not a set of Jc isotherms.
4. **One of the two samples does not exist.** The paper's devices are s1, s6 and
   s8. The string "s2" appears in it only as "Supplementary Fig. 2".

## What it does to the fits

    springer_10.1038_s41467-025-55880-4  s1  53.0 K  n=6  beta=29.999  window=0.0024
    springer_10.1038_s41467-025-55880-4  s1  30.0 K  n=6  beta=29.999  window=0.0024
    springer_10.1038_s41467-025-55880-4  s1  75.5 K  n=6  beta=29.999  window=0.0024
    springer_10.1038_s41467-025-55880-4  s2  53.0 K  n=6  beta=29.999  window=0.0024
    springer_10.1038_s41467-025-55880-4  s2  30.0 K  n=6  beta=29.999  window=0.0024
    springer_10.1038_s41467-025-55880-4  s2  75.5 K  n=6  beta=29.999  window=0.0024

All six sit at the exponent ceiling of 30 with a normalised field window of
0.0024, so they are among the 34 ceiling fits and among the 75 Tier-3 fits that
fail the applicability gate. Removing them removes 6 ceiling fits.

## The one thing not checked

The archived PDF is the main text only. Supplementary figures are not in the
archive and could not be examined. Nothing in the main text refers to a
current-density figure in the supplement: the supplementary figures it names are
I-V linearity (Fig. 8), efficiency antisymmetry (Fig. 10) and device fabrication
(Figs. 11 and 12). So the conclusion rests on the complete main text and on the
absence of any current-density language anywhere in it, and it would be
overturned only by a supplementary figure the paper never mentions.

## Recommended action

Withdraw the 6 field-axis fits and the 36 source rows, and record the paper in
`audit/withdrawn_records.csv` with this file as the reason.
