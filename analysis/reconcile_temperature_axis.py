#!/usr/bin/env python3
"""
reconcile_temperature_axis.py

Verify that the deposited temperature-axis fits were computed from the data
they were graded against, and test the fabrication verdict on structure alone.

Two checks, in that order, because the first is the one that was skipped when
the same claim was made about the field axis and had to be retracted.

  1. Reconciliation. For every row of phase_3_p44_post_UCLA_beta_T_fits.csv,
     refit beta_T from agent2_dataset_v3_2_1.csv restricted to that row's own
     recorded temperature window, and require the slope and the point count to
     match. A fit that does not reconcile was computed from something else, and
     grading its source would prove nothing.

  2. Structure. Three properties that need no figure and no judgement:
     whether every Jc value in a paper carries two significant figures or
     fewer, whether every isotherm sits on one identical field grid, and
     whether every isotherm terminates at the same field. Real isotherms end
     where Jc falls into the noise, which happens at a different field for
     every temperature.

    python3 analysis/reconcile_temperature_axis.py

Run from the repository root. Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

DEP = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
WIDE = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
        "agent2_dataset_v3_2_1.csv")


def sigfigs(v):
    if not (v > 0):
        return 9
    s = ("%.10g" % (v / 10 ** np.floor(np.log10(v)))).rstrip("0").rstrip(".")
    return len(s.replace(".", ""))


def main():
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    if not os.path.exists(WIDE):
        sys.exit("the upstream wide file is not mounted: %s" % WIDE)
    b = pd.read_csv(DEP)
    d = pd.read_csv(WIDE)

    exact = nosrc = 0
    bad = []
    for _i, r in b.iterrows():
        g = d[d.pdf_name == r.paper_id]
        if not len(g):
            nosrc += 1
            continue
        s = g[np.isclose(g.field_T, r.field_T, atol=1e-9)]
        s = s[(s.temperature_K >= r.T_min) & (s.temperature_K <= r.T_max)
              & (s.Jc > 0)]
        if len(s) < 2:
            bad.append((r.paper_id, r.field_T, "too few source rows"))
            continue
        x = np.log10(1.0 - s.temperature_K.to_numpy() / r.Tc_K)
        y = np.log10(s.Jc.to_numpy())
        A = np.vstack([x, np.ones_like(x)]).T
        (m, _c), *_ = np.linalg.lstsq(A, y, rcond=None)
        if abs(m - r.beta_T) < 0.001 and len(s) == r.n_T_pts:
            exact += 1
        else:
            bad.append((r.paper_id, r.field_T,
                        "beta %.3f vs %.3f, n %d vs %d"
                        % (m, r.beta_T, len(s), r.n_T_pts)))
    print("1. reconciliation of the %d deposited fits\n" % len(b))
    print("   reproduced exactly from the wide file: %d" % exact)
    print("   not reproduced:                        %d" % len(bad))
    print("   paper absent from the wide file:       %d" % nosrc)
    for t in bad[:5]:
        print("      %s" % (t,))

    print("\n2. structure of the source, per paper\n")
    print("   %-18s %6s %8s %7s %9s" %
          ("paper", "points", "<=2 s.f.", "grids", "same end"))
    n2 = n1g = n1e = 0
    papers = [p for p in sorted(b.paper_id.unique()) if p.endswith(".pdf")]
    for p in papers:
        g = d[d.pdf_name == p]
        if not len(g):
            continue
        f2 = np.mean([sigfigs(v) <= 2 for v in g.Jc if v > 0])
        grids = {tuple(sorted(gg.field_T.round(6)))
                 for _T, gg in g.groupby("temperature_K")}
        ends = {max(t) for t in grids}
        n2 += f2 > 0.99
        n1g += len(grids) == 1
        n1e += len(ends) == 1
        print("   %-18s %6d %8.2f %7d %9d"
              % (p, len(g), f2, len(grids), len(ends)))
    n = len(papers)
    print("\n   every Jc value at two significant figures or fewer: %d of %d" % (n2, n))
    print("   every isotherm on one identical field grid:          %d of %d" % (n1g, n))
    print("   every isotherm terminating at the same field:        %d of %d" % (n1e, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
