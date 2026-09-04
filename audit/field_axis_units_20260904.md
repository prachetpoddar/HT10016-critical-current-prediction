# The magnetic-field-unit audit, deposited

Recorded 2026-09-04. Table `audit/field_axis_units.csv`, checker
`analysis/field_unit_audit.py`.

## The claim

The main text and the supplement both state:

> A dual-model audit of the printed axis label on every Jc-versus-field figure
> in the fitted cohort found five papers in which kilo-oersted had been recorded
> as tesla, a factor of ten. Two other papers printing kilo-oersted and gauss
> had been converted correctly, so unit handling was not deterministic in the
> original protocol.

No list, no rule and no script for that audit was in the repository. This
deposits all three.

## The rule

    1 kOe = 0.1 T      1 Oe = 1e-4 T      1 G = 1e-4 T      1 mT = 1e-3 T

and, because the same protocol must handle it and one paper shows it was not
handled:

    1 A/m2 = 1e-4 A/cm2

## What the printed axes actually are

Across the 31 identifiers in the fit cohort:

| unit class | papers | fits | passing | anchors |
|---|---:|---:|---:|---:|
| tesla | 10 | 78 | 50 | 37 |
| kilo-oersted | 3 | 26 | 16 | 3 |
| oersted | 1 | 6 | 0 | 4 |
| gauss | 1 | 2 | 2 | 4 |
| no field figure | 1 | 6 | 0 | 1 |
| not a printed figure (MAGLAB) | 9 | 9 | 4 | 9 |
| unverified or unverifiable | 6 | 32 | 22 | 33 |

## The claim cannot be true as written

The audit is described as covering **every** Jc-versus-field figure in the
fitted cohort. Six papers have no figure in this corpus that could have been
covered:

- `physc.2009.05.098` and `physc.2011.02.004` are held as one-page abstracts.
  Between them they carry 15 fits, 14 of them passing.
- `iop_10.1088_0953-2048_29_3_035013` has no PDF at all. Seven fits.
- `jallcom.2023.170384` and `phpro.2012.03.421` have PDFs whose Jc figures were
  not opened here. Four fits, two passing.
- `jallcom.2023.170146` has a PDF filed under its DOI that is a **different
  paper**: Tamegai et al., Physica C 470 (2010) S360, Ba(Fe,Co)2As2 with Tc
  24 K and a kilo-oersted axis. The record's own data is a user digitisation of
  an MgB2 ultra-sonicated-boron figure with Tc 39 K over 0.02 to 4.9 T, and its
  Tier 1 critical-field ladder of 5.0, 4.0, 3.0, 2.0, 1.5 T at 10, 15, 20, 30,
  35 K is physically right for bulk MgB2. The data is coherent; the filing is
  not. Six passing fits sit on a record whose DOI and PDF disagree.

**Twenty-two of the 94 passing field-axis fits rest on a printed field axis
that nobody has read.** `analysis/field_unit_audit.py --strict` fails on
exactly that and will keep failing until those six papers are resolved.

## Two additions to the corrected set

Beyond the two kilo-oersted papers found earlier in this session
(`physc.2009.11.051` and `physc.2010.05.048`), reading the sources in this pass
found:

- `physc.2016.05.023`: the field axis of Fig. 3 is **H (kOe)**, 0.1 to 50 kOe.
  Its extraction CSV is not in the corpus, so whether the conversion was applied
  cannot be checked here. All ten of its fits are already bounded out by the
  applicability criterion, so nothing downstream moves.
- `jpcs.2026.113652`: the field axis of Figure (9) is **H (Oe)** and the
  conversion to tesla was applied correctly, but the **current** axis is
  **A/m2** and was read as A/cm2, so the values are about 100 times too large.
  This is the same class of defect as the field-unit error, on the other axis,
  and the deposited claim does not mention the current axis at all.

`matpr.2019.05.078` prints its field axis in **gauss** and the conversion was
applied correctly, which matches the claim's "two other papers ... converted
correctly" in kind if not in identity.

## The guards were shown to fire

Three defects were planted in a scratch copy and the checker went red on each:
an identifier removed from the audit table, a unit class outside the vocabulary,
and the unread axes relabelled as read (which correctly silenced the exposure
report rather than being hard-coded).
