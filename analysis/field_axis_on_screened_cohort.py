#!/usr/bin/env python3
"""
field_axis_on_screened_cohort.py

What the field-axis result becomes when the fits whose critical-field scale
fails audit/tier1_critical_field_screen.csv are removed.

Why this and not a repair. Sixty of the 94 passing field-axis fits rest on a
scale the screen flags, and the two papers whose scale is merely too small
cannot be rescued by correcting it: raising phpro.2015.06.160 from 9 T to the
26 T its own paper states drops the reduced span from 0.778 to 0.269, and
raising s10854-026-16566-9 from 9.2 T to the 78.1 T in its own extraction file
drops it from 0.489 to 0.058. All 18 then fail the 0.3 bound. Correcting the
scale moves those fits from admitted to refused rather than saving them, which
is the applicability filter's selection effect running in reverse.

So the question is not what the numbers become after repair. It is what the
field axis can still support at all. This recomputes, on the surviving cohort:

  * the per-family compound leave-one-out error, both conditioned on sample
    form and pooled, which are the two sets of four numbers the manuscript
    states as a contrast;
  * whether each family still meets the population and anchor-count conditions
    the paper imposes on itself;
  * how much of what survives is verified rather than merely unflagged, which
    is not the same thing: a paper whose extraction file is not deposited
    cannot fail the exposure test and is reported unchecked.

    python3 analysis/field_axis_on_screened_cohort.py

Run from the repository root. Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compound_leave_one_out as clo          # noqa: E402

DATA = "data"
SCREEN = os.path.join("audit", "tier1_critical_field_screen.csv")
# NOT a family-size gate. The first version of this script passed
# min_train_compounds=3 to loo(), on the reading that the paper requires three
# anchor compounds within a family, and refused iron chalcogenide 11-type as
# untestable. That is the family-size reading of K, and commit 8d43b4c already
# reverted it on the implementation: K_MIN and K_MAX bound len(anchors), an
# Anchor is one measured triple, and Fig. 4 varies K from one to three while
# holding the cuprate cohort at three compounds, which a family-size reading
# would forbid. K counts measured points supplied with a query. The published
# leave-one-compound-out applies no compound gate at all, so neither does this.
K_MIN = 0
# A leave-one-compound-out fold still needs something to train on, which is a
# property of the method rather than a rule the paper imposes.
MIN_COMPOUNDS = 2


def main():
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")
    if not os.path.exists(SCREEN):
        sys.exit("run analysis/audit_tier1_critical_fields.py --csv first")

    scr = pd.read_csv(SCREEN)
    flagged = set(scr.loc[scr.verdict != "none", "paper_id"])
    unchecked = set(scr.loc[scr.detail.astype(str).str.contains("unchecked"),
                            "paper_id"]) - flagged

    _bt, ok = clo.load(DATA)
    keep = ok[~ok.arxiv_id.isin(flagged)]
    print("field-axis fits passing physicality: %d over %d compounds"
          % (len(ok), ok.compound_formula.nunique()))
    print("   surviving the critical-field screen: %d over %d compounds\n"
          % (len(keep), keep.compound_formula.nunique()))

    print("%-24s %-22s %-22s %s" % ("family", "as published", "screened",
                                    "of the survivors"))
    print("%-24s %-22s %-22s %s" % ("", "fits / compounds", "fits / compounds",
                                    "unchecked"))
    fams = sorted(ok.substructure.unique())
    for fam in fams:
        g = ok[ok.substructure == fam]
        k = keep[keep.substructure == fam]
        u = k[k.arxiv_id.isin(unchecked)]
        print("   %-21s %6d / %-13d %6d / %-13d %d fits / %d compounds"
              % (fam, len(g), g.compound_formula.nunique(),
                 len(k), k.compound_formula.nunique(),
                 len(u), u.compound_formula.nunique()))

    print("\nwhether the family can be tested at all")
    print("   leave-one-compound-out holds one compound out and trains on the "
          "rest, so a\n   family needs at least %d compounds. This is the "
          "method, not the paper's\n   anchor-count rule, which counts "
          "measured points per query and not\n   compounds per family.\n"
          % MIN_COMPOUNDS)
    print("%-24s %-28s %s" % ("family", "as published", "screened"))
    for fam in fams:
        g = ok[ok.substructure == fam]
        k = keep[keep.substructure == fam]

        def state(s):
            n = s.compound_formula.nunique()
            if n == 0:
                return "no fits"
            if n < MIN_COMPOUNDS:
                return "%d compound, nothing to train on" % n
            return "%d compounds, testable" % n
        print("   %-21s %-28s %s" % (fam, state(g), state(k)))

    print("\nthe four numbers the manuscript states, recomputed\n")
    print("   %-24s %19s %19s" % ("family", "as published", "screened"))
    print("   %-24s %9s %9s %9s %9s"
          % ("", "conditioned", "median", "conditioned", "median"))
    for fam in fams:
        g = ok[ok.substructure == fam]
        k = keep[keep.substructure == fam]
        a1, _m, _f, _r = clo.loo(g, "beta", True, min_train_compounds=K_MIN)
        a2, _m, _f, _r = clo.loo(g, "beta", False, min_train_compounds=K_MIN)
        b1, _m, _f, _r = clo.loo(k, "beta", True, min_train_compounds=K_MIN) \
            if len(k) else (np.nan, 0, 0, 0)
        b2, _m, _f, _r = clo.loo(k, "beta", False, min_train_compounds=K_MIN) \
            if len(k) else (np.nan, 0, 0, 0)

        def s(v):
            return "  refused" if v != v else "%9.4f" % v
        print("   %-24s %s %s %s %s" % (fam, s(a1), s(a2), s(b1), s(b2)))

    print("\n   a blank is a family left with too few compounds to hold one "
          "out." )
    return 0


if __name__ == "__main__":
    sys.exit(main())
