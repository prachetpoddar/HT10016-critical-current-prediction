#!/usr/bin/env python3
"""Withdraw two records whose deposited series are not readings of their papers.

Both surfaced from the Hc2 and Tc cross-table checks as a labelling
inconsistency. Reading the two papers to settle the labels showed the labels
were the symptom.

The case below is what survived an independent adversarial review. Three of the
seven arguments first offered were broken by that review and are not used here:
that each fixed temperature equals 0.7 times the deposited Tc, which is the
correct way to assign a temperature to a figure whose caption says t = 0.7 and
whose panels print none; that the compound label is fatal, when it is a
one-field mislabel a correction could fix; and that a deposited point at 10 T
lies past a 90 kOe axis, which is one point of eleven and a nine per cent
extrapolation. The review also found one of the six transition temperatures is
right, not wrong, so that count is corrected here.

10.1016/j.physc.2009.03.028, Prozorov et al., Physica C 469 (2009) 667.
  The paper reports no critical current density and explicitly declines to,
  pointing instead to other work. Its figures are magneto-optical images, M(T),
  Tc(x), magnetisation loops in emu, normalised loops, Tc against ln Hp,
  relaxation, and creep rate. There are no tables.

  The Bean route is the only defence and it fails on the numbers. Taking the
  loop width from the paper's own Fig. 7 for x = 0.074 and normalising to the
  1 T value, Bean gives 1.08 at 5 K and 1.33 at 10 K, that is a Jc that rises
  with field, which is the fishtail the whole paper is about. The deposit gives
  0.083 and 0.082, a monotonic fall. That is a factor of 13 to 16 in the wrong
  direction, not a coarse reading.

  Nine deposited curves, from six crystals spanning Tc 9 to 23 K, at four
  temperatures, out of two different figures, collapse onto one normalised
  shape: the coefficient of variation across all nine is 1.5 per cent at 1 T,
  2.8 per cent at 2 T and 6.6 per cent at 3 T. The paper's central result, its
  Fig. 9, is that these shapes differ systematically with Tc. Independent
  digitisation cannot agree to 1.5 per cent; a template scaled per curve does.

  For x = 0.038 the source panel shows the branches merged above about 1.5 T,
  so the sample is reversible and the Bean current is zero, and the panel holds
  no data past 3 T. The deposit asserts 700, 400 and 150 kA/cm2 at 3, 4 and
  5 T, and gives that sample the same 5 T current as x = 0.058, whose loop is
  still open there.

  Five of the six transition temperatures disagree with the paper's Fig. 3, by
  5.2 K for x = 0.10. The one that agrees, 22.8 K for x = 0.074, is the one
  printed as text in the Fig. 1 caption. Text-stated numbers were carried across
  correctly and figure-read numbers were not, which is what a record built
  without opening the figures looks like. The fixed temperatures inherit those
  errors at 0.7 times their size.

10.1016/j.physc.2014.03.020, Inoue et al., Physica C 504 (2014) 73.
  Its Fig. 2(b) is the only critical-current-against-field object in the paper
  and holds two curves, "wire" and "HIP wire", at 4.2 K, on a y axis running to
  10^4 A/cm2.

  The deposited series peaks at 5e4 A/cm2, which is five times above the top
  gridline of that axis and 5.4 times the largest current reported anywhere in
  the paper, the tape at 9.2 kA/cm2.

  The discrepancy is not a scale error. Against the wire curve the deposit runs
  about 100 times high at 1 T, 40 at 2 T, 15 at 4 T, 8 at 5 T and 3.8 at 9 T.
  The deposit falls by a factor of 250 across its range; the paper's wire falls
  by about 25. No unit slip or rescale produces a varying factor with the wrong
  curvature.

  All eleven values are round to one significant figure on a smooth decay.

  Corroborating, and not the argument: the compound is recorded as BaFe2As2,
  the undoped parent, which is not a superconductor, in a paper titled "Effects
  of high-pressure sintering on critical current density in Co-doped BaFe2As2
  wires".

Neither record is a coarse reading of anything in its cited paper. The errors
are structured, a shared template and a smoothly varying discrepancy factor on
uniformly round values, rather than scattered, which is what real digitisation
error looks like.

    python analysis/withdraw_two_records_20260903.py --dry-run
    python analysis/withdraw_two_records_20260903.py
"""
import argparse
import csv
import datetime
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, AUDIT = os.path.join(ROOT, "data"), os.path.join(ROOT, "audit")
FITS = os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv")
ANCHORS = os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv")
PROV = os.path.join(DATA, "provenance_table_fitcohort_full.csv")
WITHDRAWN = os.path.join(AUDIT, "withdrawn_records.csv")

RECORDS = [
    dict(token="physc.2009.03.028",
         identifier="10.1016/j.physc.2009.03.028",
         citation="Prozorov et al., Physica C 469 (2009) 667",
         reason="the paper reports no critical current density and declines "
                "to. The only defence, reconstruction through the Bean model, "
                "fails on the numbers: the loop width in the paper's Fig. 7 "
                "gives a Jc that RISES with field, 1.08 at 5 K and 1.33 at "
                "10 K relative to 1 T, which is the fishtail the paper is "
                "about, while the deposit falls to 0.083 and 0.082, a factor "
                "of 13 to 16 in the wrong direction. Nine deposited curves "
                "from six crystals at four temperatures out of two figures "
                "collapse onto one normalised shape, coefficient of variation "
                "1.5 per cent at 1 T, in a paper whose central result is that "
                "the shapes differ with Tc. For x = 0.038 the source panel is "
                "reversible above about 1.5 T and holds no data past 3 T, "
                "while the deposit asserts 700, 400 and 150 kA/cm2 at 3, 4 and "
                "5 T. Five of six transition temperatures disagree with the "
                "paper's Fig. 3, by 5.2 K for x = 0.10, and the one that "
                "agrees is the one printed as text"),
    dict(token="physc.2014.03.020",
         identifier="10.1016/j.physc.2014.03.020",
         citation="Inoue et al., Physica C 504 (2014) 73",
         reason="the deposited series peaks at 5e4 A/cm2, five times above "
                "the top gridline of the only critical-current-against-field "
                "figure in the paper and 5.4 times the largest current it "
                "reports anywhere. Against that figure's wire curve the "
                "deposit runs about 100 times high at 1 T, 40 at 2 T, 15 at "
                "4 T, 8 at 5 T and 3.8 at 9 T, falling by a factor of 250 "
                "across its range where the paper's wire falls by about 25, so "
                "no unit slip or rescale accounts for it. All eleven values are "
                "round to one significant figure. Corroborating: the compound "
                "is recorded as BaFe2As2, the undoped parent, which is not a "
                "superconductor")
]


def read(path):
    with open(path, newline="") as fh:
        r = csv.DictReader(fh)
        return list(r), list(r.fieldnames)


def write(path, rows, cols):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    stamp = datetime.datetime.now().strftime("%Y%m%d")
    backup = os.path.join(AUDIT, "pre_withdrawal_" + stamp + "b")
    tokens = [r["token"] for r in RECORDS]

    counts = {}
    for path, field in ((FITS, "arxiv_id"), (ANCHORS, "paper_id"),
                        (PROV, "identifier")):
        rows, cols = read(path)
        keep = [r for r in rows if not any(t in r[field] for t in tokens)]
        counts[os.path.basename(path)] = (len(rows) - len(keep), len(keep))
        if not args.dry_run:
            os.makedirs(backup, exist_ok=True)
            dst = os.path.join(backup, os.path.basename(path))
            if not os.path.exists(dst):
                shutil.copy2(path, dst)
            write(path, keep, cols)

    for k, (removed, left) in counts.items():
        print("   %-46s removed %2d, %d left" % (k, removed, left))

    if not args.dry_run:
        wrows, wcols = read(WITHDRAWN)
        for rec in RECORDS:
            if any(r.get("identifier") == rec["identifier"] for r in wrows):
                continue
            e = {c: "" for c in wcols}
            e.update(identifier=rec["identifier"], citation=rec["citation"],
                     withdrawn=datetime.date.today().isoformat(),
                     reason=rec["reason"],
                     status="removed from the fit, anchor and provenance tables")
            wrows.append(e)
        write(WITHDRAWN, wrows, wcols)
        print("\n   registered in audit/withdrawn_records.csv")
        print("   now rerun: analysis/regenerate_regime_tables.py, "
              "analysis/compound_leave_one_out.py, analysis/verify_deposit.py")
    else:
        print("\nnothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
