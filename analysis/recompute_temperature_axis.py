#!/usr/bin/env python3
"""
recompute_temperature_axis.py

Recompute the temperature-axis exponent from traced figure points, and set it
beside the deposited value.

The 260 fits in data/phase_3_p44_post_UCLA_beta_T_fits.csv all come from
extractions that were opened at their published figures and found to be
generated rather than read. Recomputing the axis therefore means refitting from
points measured off the page, not refitting the same numbers a different way.

This does that for every paper where a trace exists in data/reextraction, and
reports what changes. It is the start of the rebuild, not the whole of it.

The form fitted is the one the manuscript uses on this axis:

    log10 Jc = log10 Jc0 + beta_T * log10(1 - T / Tc)

at fixed field, so beta_T is the slope against the reduced temperature distance
from Tc. Tc is taken from the paper, and which Tc is used matters: the deposited
fit for 2305.10034v1 carries Tc = 28.0 K where that paper's Table 3 reports
13.3(2) K, and the exponent is not weakly sensitive to it.

    python3 analysis/recompute_temperature_axis.py

Run from the repository root. Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

DEP = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")

# trace file -> (deposited paper_id, Tc from the paper, where that Tc is stated)
TRACED = {
    "jallcom_2023_170384_fig6c_points.csv": (
        "2305.10034v1.pdf", 13.3,
        "Table 3 of the paper, Tc = 13.3(2) K for "
        "La0.87Sm0.13FeAs0.91P0.09O"),
}


# deposited fits use a particular temperature set; match it for comparability
TEMPS = {"2305.10034v1.pdf": (2.0, 5.0, 8.0)}


def fit_beta(sub, tc):
    """Slope of log10 Jc against log10(1 - T/Tc). Returns (beta, se, n)."""
    sub = sub[(sub.temperature_K < tc) & (sub.Jc_A_per_cm2 > 0)]
    if sub.temperature_K.nunique() < 3:
        return None
    x = np.log10(1.0 - sub.temperature_K.to_numpy() / tc)
    y = np.log10(sub.Jc_A_per_cm2.to_numpy())
    A = np.vstack([x, np.ones_like(x)]).T
    (m, c), *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ np.array([m, c])
    dof = max(len(x) - 2, 1)
    s2 = float(resid @ resid) / dof
    var = s2 * np.linalg.inv(A.T @ A)[0, 0]
    return float(m), float(np.sqrt(max(var, 0.0))), len(x)


def main():
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    dep = pd.read_csv(DEP)
    any_run = False
    for fn, (pid, tc, where) in TRACED.items():
        path = os.path.join("data", "reextraction", fn)
        if not os.path.exists(path):
            print("no trace yet: %s" % fn)
            continue
        any_run = True
        r = pd.read_csv(path)
        d = dep[dep.paper_id == pid]
        print("=" * 72)
        print("%s   trace %s" % (pid, fn))
        print("   Tc used here: %.1f K  (%s)" % (tc, where))
        print("   Tc in the deposited fit: %s K" % sorted(d.Tc_K.unique()))
        print("   compound in the deposited fit: %s" % sorted(d.compound_formula.unique()))
        temps = sorted(r.temperature_K.unique())
        # Match the deposited fit's own temperature set rather than using every
        # traced isotherm: it fitted three points from 2 to 8 K, and the 10 K
        # curve genuinely ends at 0.55 T on the page, so including it would
        # shrink the comparable field range to a single point.
        keep = TEMPS.get(pid)
        if keep:
            temps = [T for T in temps if T in keep]
        print("   traced temperatures: %s" % temps)

        # a common field grid where every traced isotherm has coverage
        lo = max(r[r.temperature_K == T].field_T.min() for T in temps)
        hi = min(r[r.temperature_K == T].field_T.max() for T in temps)
        grid = [g for g in np.arange(0.0, 6.01, 0.5) if lo <= g <= hi]
        print("   traced isotherms overlap over %.2f to %.2f T" % (lo, hi))
        print("\n   %8s %12s %12s %10s %10s" %
              ("H (T)", "beta_T here", "deposited", "n points", "ratio"))
        rows = []
        for g in grid:
            pts = []
            for T in temps:
                s = r[r.temperature_K == T].sort_values("field_T")
                pts.append((T, float(np.interp(g, s.field_T, s.Jc_A_per_cm2))))
            sub = pd.DataFrame(pts, columns=["temperature_K", "Jc_A_per_cm2"])
            out = fit_beta(sub, tc)
            if out is None:
                continue
            b, se, n = out
            near = d.iloc[(d.field_T - g).abs().argsort()[:1]]
            bd = float(near.beta_T.iloc[0]) if len(near) else np.nan
            rows.append((g, b, bd))
            print("   %8.2f %12.3f %12.3f %10d %10.2f"
                  % (g, b, bd, n, bd / b if b else np.nan))
        if rows:
            a = np.array([x[1] for x in rows])
            e = np.array([x[2] for x in rows])
            print("\n   recomputed beta_T: %.3f to %.3f, spread %.3f"
                  % (a.min(), a.max(), a.max() - a.min()))
            print("   deposited beta_T:  %.3f to %.3f, spread %.3f"
                  % (e.min(), e.max(), e.max() - e.min()))
            print("   median ratio deposited/recomputed: %.2f" % np.median(e / a))
            print("\n   A real Jc(T,H) surface gives a different temperature exponent at\n"
                  "   different fields. The deposited value is flat to three figures across\n"
                  "   thirteen fields, which is what a ladder produces and measurement does not.")
    if not any_run:
        print("no traces available yet for any temperature-axis paper")
    print("\n%d of the 260 deposited temperature-axis fits are covered by a trace so far"
          % int(dep.paper_id.isin([v[0] for v in TRACED.values()]).sum()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
