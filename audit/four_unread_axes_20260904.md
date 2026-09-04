# The four unread field axes

Recorded 2026-09-04. Table `audit/field_axis_units.csv`, checker
`analysis/field_unit_audit.py`. Nothing in the data changed.

Twenty-two of the 94 passing field-axis fits rested on a printed field axis
nobody had read. This resolves one, narrows two, and turns up a new probable
defect in the fourth.

## Resolved

**`jallcom.2023.170384`, 2 passing fits.** The full text is in the corpus and
was simply never opened. Zhigadlo et al., La0.87Sm0.13FeAs0.91P0.09O single
crystal. Fig. 6(c) plots critical current density in A/cm2 against **mu0H in
tesla**, 0 to 6 T, at 2, 5, 8 and 10 K for H parallel to c.

The extraction matches the panel at every endpoint:

| T | figure | extraction | field range |
|---|---|---|---|
| 2 K | 3e6 down to 6e4 | 3.34e6 down to 6.45e4 | 0.008 to 6.00 T |
| 5 K | 1.5e6 down to 5e3 | 1.53e6 down to 4.98e3 | 0 to 3.00 T |
| 8 K | 8e5 down to 2.5e3 | 8.16e5 down to 2.41e3 | 0 to 1.49 T |
| 10 K | 5e5 down to 2.6e3 | 4.72e5 down to 2.56e3 | 0 to 0.49 T |

Each series terminates where its curve does. This is the best digitisation seen
in the cohort. One separate defect: the extraction header records Tc 26.0 K and
Hc2 86.0 T where Table 3 of the paper gives Tc 13.3 K and mu0Hc2//c(0) = 7(1) T.

## Narrowed on internal evidence, figure still unread

**`physc.2011.02.004`, 6 passing fits.** Bhoi et al., Physica C 471 (2011)
258-264, seven pages, of which the corpus holds page one. The extraction is a
356-point user digitisation reaching 14.6 T, an ordinary laboratory field for a
1111 magnetization study, with no repeated ceiling and no decade anomaly. The
abstract states a power law H^-5/8 for JL(H); the deposit's six exponents run
0.099 to 1.015 and bracket 0.625. Consistent with tesla.

**`jallcom.2023.170146`, 6 passing fits.** The DOI and the filed PDF are
different papers, as recorded earlier. Searching every PDF in the corpus for
"ultra-sonicated" and for "P45", the two strings the record's own supplementary
file quotes from its source caption, returns nothing: the true source paper is
not here at all. On internal evidence the axis is tesla. Fields run 0.03 to
4.9 T against a per-temperature irreversibility ladder of 5.0, 4.0, 3.0, 2.0 and
1.5 T at 10, 15, 20, 30 and 35 K, which is right for bulk MgB2 and which a
kilo-oersted misread would place at 0.3 to 49 T.

## New probable defect

**`physc.2009.05.098`, 8 passing fits.** Tamegai et al., *Magneto-optical
imaging of iron-oxypnictide SmFeAsO1-xFx and SmFeAsO1-y*, Physica C 469 (2009)
915-920, six pages, of which the corpus holds page one.

Four things point the same way:

1. Eight of the nine isotherms end at exactly **46.055046**. A repeated
   non-round ceiling across isotherms is a digitised axis endpoint, and the
   whole axis is quantised on a 0.091743 grid, which is a pixel pitch.
2. Read as tesla, that is a 46 tesla applied field in a study whose method is a
   SQUID magnetometer and magneto-optical imaging. No such apparatus reaches it.
3. Read as kilo-oersted it is 4.6 T on a 50 kOe full scale, which is the
   standard 5 T magnetometer range, and which is the same full scale printed on
   Fig. 3 of `physc.2016.05.023` by the same group.
4. The abstract states intragranular currents "over 1e5 A/cm2 at low
   temperatures and low fields"; the extraction's 2 K maximum is 3.9e5 A/cm2,
   which agrees and is unaffected by the field unit.

This is inference, not a reading. The figure is on a page the corpus does not
hold. But if it is confirmed, the measured span falls from 0.53 to 0.053 of the
86 T default and **all eight passing fits fail the applicability criterion of
Eq. (1)**.

The same shape of question applies to `iop_10.1088_0953-2048_29_3_035013`, a
magneto-optical and SHPM field sweep on FeSe0.5Te0.5 whose seven isotherms all
end near 9.03. That record carries no passing fits, all seven being bounded out
already, so nothing downstream turns on it.

## What is still needed

Two full texts, neither obtainable from here:

- **Physica C 469 (2009) 915-920**, Tamegai et al. Pages 2 to 6. This is the
  one that matters: 8 passing fits and 9 anchor rows.
- **Physica C 471 (2011) 258-264**, Bhoi et al. Pages 2 to 7.

And one identification: which paper the DOI 10.1016/j.jallcom.2023.170146
belongs to, given that the record's data is an MgB2 ultra-sonicated-boron figure
and the PDF filed under it is a 2010 Physica C pnictide paper.
