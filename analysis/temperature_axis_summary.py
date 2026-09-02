#!/usr/bin/env python3
"""
temperature_axis_summary.py

Isolates the temperature-axis validation, generating Table S10 of the
Supplemental Material.

Why this exists. Every field-axis number in this paper is conditional on the
resolved critical field, and Sec. III.F reports at length how weak that layer
is. The temperature axis does not have that problem: it is anchored on Tc, which
the source paper usually reports for the sample it measured, so what survives
here survives independently of the critical-field provenance issue. The referee
asked to see that separately and this is it, on the frozen cohort, with no new
model and no new fitting.

The protocol is the one Sec. III.C already uses: hold out each compound in the
family, predict its fits by the median beta_T of the remaining fits, and score
the mean absolute error over fits. Families with one compound cannot be held out
and are reported as such rather than omitted, so the table accounts for every
temperature-axis fit in the deposit.

    python analysis/temperature_axis_summary.py
    python analysis/temperature_axis_summary.py --json out.json

Run from the repository root.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

FITS = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
THRESHOLD = 1.0
NAMES = {"iron_chalcogenide_11": "Iron chalcogenide 11-type",
         "iron_pnictide_122": "Iron pnictide 122-type",
         "iron_pnictide_1111": "Iron pnictide 1111-type",
         "iron_pnictide_111": "Iron pnictide 111-type",
         "iron_other": "Iron, unclassified",
         "conventional_AlB2": "MgB2-class"}


def loo(s):
    """Mean absolute error, each compound held out, substructure median."""
    res = []
    for c in s.compound_formula.unique():
        train = s[s.compound_formula != c]
        if train.empty:
            continue
        for _i, r in s[s.compound_formula == c].iterrows():
            res.append(abs(r.beta_T - train.beta_T.median()))
    return (float(np.mean(res)), len(res)) if res else (float("nan"), 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    t = pd.read_csv(FITS)

    rows = []
    for fam, s in t.groupby("substructure"):
        n_c = s.compound_formula.nunique()
        if n_c < 2:
            rows.append(dict(family=NAMES.get(fam, fam), compounds=n_c,
                             papers=s.paper_id.nunique(), fits=len(s),
                             mae="n/a",
                             outcome="one compound, cannot be held out"))
            continue
        mae, _n = loo(s)
        rows.append(dict(family=NAMES.get(fam, fam), compounds=n_c,
                         papers=s.paper_id.nunique(), fits=len(s),
                         mae="%.3f" % mae,
                         outcome="passes" if mae <= THRESHOLD else "fails"))
    rows.sort(key=lambda r: (r["mae"] == "n/a", r["mae"]))

    print("Table S10  temperature-axis validation, threshold %.1f in the "
          "exponent\n" % THRESHOLD)
    print("   %-26s %5s %6s %5s %8s   %s"
          % ("family", "cmpd", "papers", "fits", "MAE", "outcome"))
    for r in rows:
        print("   %-26s %5d %6d %5d %8s   %s"
              % (r["family"], r["compounds"], r["papers"], r["fits"],
                 r["mae"], r["outcome"]))
    print("\n   %d fits in total, which is every temperature-axis fit in the "
          "deposit" % sum(r["fits"] for r in rows))
    print("   These are anchored on Tc and do not use a resolved critical "
          "field, so they carry none of the qualification of Sec. III.F.")

    if args.json:
        with open(args.json, "w") as f:
            json.dump({"S10": rows}, f, indent=1)
        print("\nwritten to %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
