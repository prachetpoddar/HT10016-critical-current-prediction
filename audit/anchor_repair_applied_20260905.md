# The anchor layer, repaired

Recorded 2026-09-05. Script `analysis/apply_anchor_repairs.py`, ledger
`audit/anchor_repairs.csv`, snapshots in `audit/pre_anchor_repair_20260905/`.
The deposited tables are untouched; the repaired ones are written beside them
as `*_repaired.csv`, so every number in the manuscript can still be traced to
what produced it.

An independent review found the first version of this repair wrong in eight
ways, three of which changed the answer. What is below is the corrected
version, and the eight are listed at the end.

## Reproduction before change

Both fit rules are recovered from the extractions before anything is altered,
and the script refuses to write if they are not.

| | recovered |
|---|---|
| beta_H, passing field-axis fits | **94 of 94** |
| beta_T, temperature-axis fits | **257 of 260** |

A further invariant runs on every pass: the 111 reproduced fits whose anchor
does not move must come back unchanged. They do, to 1e-4 on the normalised
range and 1e-3 on the exponent, which is the tolerance the reproduction gate
itself accepted.

## The temperature axis

Seventeen Cohort A Tc anchors are replaced by the value the paper prints for
the sample whose figure was extracted, each with a quote on file in
`analysis/tc_anchor_audit.py`. One more, `1009.4896v1`, is relabelled: that
paper states no Tc for its sample at all, so the anchor stays and the claim
that it is paper-reported does not.

**The repair costs no fits.** Correcting the Tc re-cuts the window on 57 of the
260 fits and none of them falls below three points. It also **adds** points to
39 fits, in the three papers whose corrected Tc is higher than the family
constant: `1108.0407v1` (8.0 to 9.8 K), `1111.3923v1` (14.5 to 17.7 K) and
`2511.19058v1` (8.0 to 9.0 K). The three fits not scored are two whose paper has
no rows in this extraction and one whose deposited rule was never recovered.
None of the three is a cost of the repair, and the first version of this note
reported two of them as such.

beta_T moves by a median of 0.137 and by up to 4.026.

## The field axis

Fifteen Cohort B Tc anchors are corrected per sample, using the sample
identifier the fits table already carries.

**Three papers leave the cohort.**

| paper | fits | why |
|---|---:|---|
| `physc.2009.11.051` | 8 | the paper contains no occurrence of "upper critical" or "irrevers" anywhere and has no critical-field figure; the source note names a figure that measures neither; the values rise monotonically with temperature within one sample |
| `physc.2010.05.048` | 8 | the same, with a ladder rising by a factor of seven |
| `physc.2009.05.098` | 8 | the field axis is kilo-oersted read as tesla and the anchor is an 86 T literature default that does not scale with it, so the corrected span is 0.053 of it |

**Two papers are repaired rather than withdrawn.**

`physc.2013.04.060` was withdrawn in the first version for having no source. It
has two tables of sources. Its Table 1 prints Birr at 10 K for five strands
(MgB2 11.0, +SiC 16.9, +ZrB2 13.1, +Ag 14.5, +TiC 11.9) and its Table 2 prints
Birr at 4.2 K for three (11.2, 15.3, 23.6), both defined by the paper as the
field at which Jc falls to 100 A/cm2. The deposit mis-transcribed two of them,
recording MgB2 at 11.9 T, which is the TiC value, and +ZrB2 at 14.5 T, which is
the Ag value, and omitting +Ag; all five 10 K fits then used a single 11.9 T.
With the paper's own per-sample values, seven of its eight fits clear the field
clause with exponents of 3.6 to 5.6.

`phpro.2015.06.160`'s anchor of 9.0 T is the maximum applied field its own
figure states. The paper prints Hc2(0) = 26 T for the Ni-doped crystal and 31 T
for the K-doped one. The first version applied 26 T to both, which is the other
sample's number, and described 26 T as a value "at 18.9 K", which is that
sample's Tc and not a measurement temperature. With the correct per-sample
values the normalised range falls to 0.269 and 0.226 and **all six fits fail the
field clause**, exactly as `audit/anchor_provenance_repaired_20260905.md`
predicted.

**The cohort.**

| | fits | papers |
|---|---:|---:|
| passing before | 94 | 16 |
| passing after the repair | **63** | **12** |

Applying the temperature clause to this cohort, which the deposit does not do,
would take a further 11.

## Two arguments withdrawn from the withdrawal reasons

The first version withdrew `physc.2009.11.051` and `physc.2010.05.048` partly on
their kilo-oersted field axis and partly on their values exceeding the 5 T
maximum of the MPMS-XL5 both papers state. Neither clause holds.

- The **unit clause is scale-invariant** where the anchor was read off the same
  kilo-oersted figure as the data. Dividing both by ten leaves
  `(Hmax - Hmin)/Hc2` exactly where it was: 0.720, 0.400, 0.360 and 0.873 before
  and after for `physc.2009.11.051`. It does no work on either paper. It does
  work on `physc.2009.05.098`, whose anchor is a literature default that does
  not scale, and that is the one withdrawal of the three it supports.
- The **instrument clause contradicts it.** If the recorded values are in
  kilo-oersted, then 25.0 is 2.5 T and nothing exceeds 5 T. The two clauses
  cannot both be true, and the first version deposited both, sixteen times.

What remains is what the papers print, which is nothing: neither contains an
upper critical field or an irreversibility field anywhere in its text, and
neither has a figure that measures one.

Separately, the "over-claimed term" flag raised against `physc.2013.04.060` on
2026-09-05 was wrong in spirit. That paper explicitly replaces Hc2 with Birr
throughout, defines the reduced field as B/Birr, and cites Bc2 ~ 1.2 Birr.
Recording an irreversibility field there is the paper's own convention, not an
over-claim. The same is true of `phpro.2015.06.160`, whose text says the reduced
field for these curves should be built on Hirr rather than Hc2, which is a third
reason not to substitute its Hc2(0).

## What the review found in the first version

1. **A join on the wrong column.** The fits table carries both `arxiv_id` and
   `paper_key` and they differ on one paper. Keying on `paper_key` lost six fits
   of `1002.0208v2`, whose extraction is filed under its arXiv id, and the loss
   was then printed as a property of the data. All six reproduce exactly. The
   cohort is 63, not 56.
2. **The refit widened the retention window.** Re-cutting `H < Hc2` with the
   larger repaired anchor admitted a 10 T point `phpro.2015.06.160`'s deposited
   fit never had, taking its normalised range to 0.346 and rescuing all six fits
   the audit had already shown fail. The clause asks what fraction of Hc2 the
   measurement spans; the span belongs to the measurement and only the
   denominator is repaired.
3. **The Hc2 table was keyed by paper, not by sample**, which is the error the Tc
   table had been built to avoid.
4. **The conservatism claim was inverted.** Hc2(0) held at every temperature
   overstates Hc2, it does not understate it.
5. **`physc.2013.04.060` was withdrawn for having no source** when it has two
   tables of per-sample sources.
6. **The kilo-oersted and instrument clauses**, above.
7. **The temperature axis refitted fits whose rule was never reproduced**, which
   the docstring promised it would not. It now skips them on both axes.
8. **The ledger wrote one row per fit rather than one per change**, inflating 53
   repairs to 123, and the honesty caveats defined for the Tc corrections were
   never printed. Both are fixed, and the caveats are printed on every run.

Two guards were added and both fire on every run: every correction key must
match at least one row, and every reproduced fit whose anchor did not move must
come back unchanged.

## Still open

`analysis/verify_deposit.py` and everything else in `analysis/` read the
deposited tables, not the repaired ones. Nothing yet marks the deposited numbers
as superseded, and that is a deliberate stopping point: which set the manuscript
reports is a decision, not a repair.
