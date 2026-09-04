#!/usr/bin/env python3
"""
apply_unit_repairs.py

Produce corrected point sets for the papers whose extracted values track their
printed curves and whose only defect is a unit.

Not every defective record needs re-tracing. Five of them were checked against
the page and their critical-current values are right; what is wrong is the scale
written beside them. Tracing those again would replace good numbers with
slightly worse ones. They need arithmetic, and the arithmetic has to be
deposited rather than described.

Each rule below names the printed axis, the figure it was read from, and the
factor. Nothing is applied to the live tables here: the corrected sets are
written to data/reextraction/ alongside the traced ones, so the two paths end in
the same place and can be compared.

    python3 analysis/apply_unit_repairs.py [--write]

Run from the repository root.
"""
import argparse
import glob
import os
import sys

import pandas as pd

OUT = os.path.join("data", "reextraction")
SRC = "/mnt/user-data/uploads/SuperconductorWorkflow"

# paper key -> (field factor, current factor, printed axis, where it was read)
RULES = {
    "physc.2009.05.098": (
        0.1, 1.0, "H (kOe), 0 to 50",
        "Fig. 2, Physica C 469 (2009) 915. Verified value by value: the nine "
        "low-field readings track the printed curves (3.90e5 against about 4e5 "
        "at 2 K, down to 1.55e3 against about 1.3e3 at 40 K), each series' "
        "recorded field maximum lands where its printed curve terminates, and "
        "the paper's own 'about 2e5 A/cm2 at T = 5 K' matches the recorded "
        "2.28e5. Only the scale is wrong."),
    "s41598-025-24806-x": (
        0.1, 1.0, "H_int (kOe), 0 to 46",
        "Fig. 5, Sci. Rep. 15 (2025) 40940. The three Tc values 13.0, 17.6 and "
        "12.8 K match the caption exactly, the odd temperatures 5.07 and 6.86 K "
        "are 0.39 Tc as the paper specifies, and the recorded currents track "
        "the printed curves to about thirty per cent."),
}

# Checked and REJECTED for this route. Each was assumed to be a unit-only defect
# and each turned out to have wrong values as well, so each needs tracing. The
# rejections are kept here because the assumption was made once and should not
# be made again.
NEEDS_TRACING = {
    "physc.2010.05.048":
        "Fig. 3 is a kilo-oersted axis, but the recorded 2 K series runs 1e6 "
        "down to 2.6e5 in a smooth exponential where the printed curve starts "
        "near 5e5 and is flat around 2e5 with a fishtail. The paper states 4e5 "
        "at 2 K under zero field against a recorded 1e6. Shape and scale both "
        "wrong, so dividing the field by ten would leave a wrong curve.",
    "physc.2011.05.018":
        "Fig. 2(e) is a kilo-oersted axis, but the recorded 680 C series at 2 K "
        "falls only from 1e5 to 8e4 across the range where the printed curve "
        "falls from about 1e5 to about 1.4e4. Five to six times high at the far "
        "end, and two of the 600 C points sit beyond that panel's 10 kOe range.",
    "jpcs.2026.113652":
        "The current axis is A/m2 and the field axis is oersted, but converting "
        "does not reconcile the numbers: the recorded 2.5e6 to 4e6 becomes 250 "
        "to 400 A/cm2 where the printed panels span 3e7 to 4e8 A/m2, which is "
        "3e3 to 4e4 A/cm2. The recorded values are not the printed ones in any "
        "unit. The 'rescaled x0.01' repair on file is also a guess.",
}


def find(key):
    return [p for p in glob.glob(os.path.join(SRC, "**", "*_LONG.csv"),
                                 recursive=True)
            if key in os.path.basename(p)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    os.makedirs(OUT, exist_ok=True)

    print("unit repairs: the value is right, the scale beside it is not\n")
    print("%-24s %7s %9s %7s  %s" % ("paper", "rows", "H factor", "Jc", "printed axis"))
    total = 0
    for key, (hf, jf, axis, why) in RULES.items():
        ps = find(key)
        if not ps:
            print("%-24s %7s  no extraction CSV in the corpus" % (key, "-"))
            continue
        d = pd.concat([pd.read_csv(p) for p in ps], ignore_index=True)
        before = (d.field_T.min(), d.field_T.max(),
                  d.Jc_A_per_cm2.min(), d.Jc_A_per_cm2.max())
        d["field_T"] = d.field_T * hf
        d["Jc_A_per_cm2"] = d.Jc_A_per_cm2 * jf
        d["repair"] = "H x %g, Jc x %g" % (hf, jf)
        d["printed_axis"] = axis
        print("%-24s %7d %9g %7g  %s" % (key, len(d), hf, jf, axis))
        print("       %.4g-%.4g T and %.3g-%.3g A/cm2  ->  %.4g-%.4g T and %.3g-%.3g"
              % (before[0], before[1], before[2], before[3],
                 d.field_T.min(), d.field_T.max(),
                 d.Jc_A_per_cm2.min(), d.Jc_A_per_cm2.max()))
        total += len(d)
        if args.write:
            f = os.path.join(OUT, "%s_unit_repaired.csv" % key.replace(".", "_"))
            d.to_csv(f, index=False)
            print("       written %s" % f)
    print("\n   %d rows across %d papers" % (total, len(RULES)))
    print("\n   checked and rejected for this route, needing a trace instead:")
    for k, why in NEEDS_TRACING.items():
        print("      %-22s %s" % (k, " ".join(why.split())[:120] + "..."))
    if not args.write:
        print("   nothing written; pass --write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
