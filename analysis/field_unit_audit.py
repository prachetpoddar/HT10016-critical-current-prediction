#!/usr/bin/env python3
"""
field_unit_audit.py

Bind audit/field_axis_units.csv to the fitted cohort and report what the
magnetic-field-unit claim actually rests on.

The supplement and the main text both state that a dual-model audit of the
printed field-axis label on *every* critical-current-versus-field figure in the
fitted cohort found five papers in which kilo-oersted had been recorded as
tesla, and two more printing kilo-oersted and gauss that had been converted
correctly. No list, no rule and no script for that audit was ever deposited.

This deposits one. audit/field_axis_units.csv carries, for each of the 31
identifiers in the fit cohort, whether a PDF exists in the corpus, which figure
was opened, the field-axis label as printed, and how that was established.

The conversion rule the protocol must apply, stated once:

    1 kOe = 0.1 T        1 Oe  = 1e-4 T        1 G = 1e-4 T        1 mT = 1e-3 T

and the corresponding rule for the current axis, which the same protocol must
also apply and which is the defect found in jpcs.2026.113652:

    1 A/m2 = 1e-4 A/cm2

    python3 analysis/field_unit_audit.py [--strict]

Run from the repository root. Changes nothing. --strict exits non-zero when any
identifier in the cohort is absent from the audit table, when any row claims a
unit class the vocabulary does not contain, or when any paper carrying passing
field-axis fits has an unverified or unverifiable field axis.
"""
import argparse
import os
import sys

import pandas as pd

FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
ANCHORS = os.path.join("data", "phase_3_p31_jc_anchor_per_paper.csv")
UNITS = os.path.join("audit", "field_axis_units.csv")

# the only unit classes a row may claim
VOCAB = {"tesla", "kilo-oersted", "oersted", "gauss", "millitesla", "none",
         "consistent with tesla", "probable kilo-oersted",
         "not a printed figure", "unverified", "unverifiable", "unresolved"}

# a class in this set means the axis was not established from a printed figure
UNSETTLED = {"unverified", "unverifiable", "unresolved",
             "consistent with tesla", "probable kilo-oersted"}

TO_TESLA = {"tesla": 1.0, "kilo-oersted": 0.1, "oersted": 1e-4,
            "gauss": 1e-4, "millitesla": 1e-3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")

    u = pd.read_csv(UNITS)
    f = pd.read_csv(FITS)
    a = pd.read_csv(ANCHORS)

    fails = []

    bad = sorted(set(u.unit_class.dropna()) - VOCAB)
    if bad:
        fails.append("unit_class values outside the vocabulary: %s" % bad)

    cohort = set(f.arxiv_id)
    absent = sorted(cohort - set(u.identifier))
    if absent:
        fails.append("in the fit cohort but not in the audit table: %s" % absent)
    stray = sorted(set(u.identifier) - cohort)
    if stray:
        fails.append("in the audit table but not in the fit cohort: %s" % stray)

    g = f.groupby("arxiv_id").agg(
        fits=("physicality", "size"),
        passing=("physicality", lambda s: int((s == "ok").sum())))
    anc = a.paper_id.value_counts().rename("anchors")
    t = u.set_index("identifier").join(g).join(anc)
    t[["fits", "passing", "anchors"]] = t[["fits", "passing", "anchors"]].fillna(0).astype(int)

    print("field-axis units across the fitted cohort\n")
    cols = ["unit_class", "pdf_in_corpus", "figure_read", "printed_field_axis",
            "fits", "passing", "anchors"]
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 26)
    print(t[cols].sort_values(["unit_class", "passing"],
                              ascending=[True, False]).to_string())

    print("\n   by unit class")
    for k, v in t.groupby("unit_class")[["fits", "passing", "anchors"]].sum().iterrows():
        print("      %-22s papers %2d   fits %3d   passing %3d   anchors %3d"
              % (k, int((t.unit_class == k).sum()), v.fits, v.passing, v.anchors))

    exposed = t[t.unit_class.isin(UNSETTLED) & (t.passing > 0)]
    if len(exposed):
        print("\n   passing field-axis fits whose printed axis was never read:")
        for i, r in exposed.iterrows():
            print("      %-46s passing %2d   %s" % (i, r.passing, r.note))
        if args.strict:
            fails.append("%d papers carry passing fits on an unread field axis"
                         % len(exposed))

    print("\n   conversion rule the protocol must apply")
    for k, v in sorted(TO_TESLA.items(), key=lambda kv: -kv[1]):
        print("      1 %-14s = %g T" % (k, v))
    print("      1 A/m2         = 1e-04 A/cm2   (current axis, same protocol)")

    if fails:
        print("\n   FAILED")
        for m in fails:
            print("      " + m)
        return 1
    print("\n   the audit table covers every identifier in the fit cohort")
    return 0


if __name__ == "__main__":
    sys.exit(main())
