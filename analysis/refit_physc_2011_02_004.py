#!/usr/bin/env python3
"""Refit the PrFeAsO0.6F0.12 field axis against the paper's own irreversibility
line, and report the residual, which the first version of this refit did not.

The paper (Physica C 471 (2011) 215, arXiv:1002.0208) states that Hirr, Hon and
Hp follow Hx(T) = Hx(0)(1 - T/Tc)^n with n about 1.7 for Hirr and Hirr(0) =
31.9 T. What it does not state next to that expression is the Tc used in it. The
deposited source rows carry tc_K = 51.0; the earlier refit implies 45.0; the
paper's own text gives a diamagnetic onset of about 48 K. All three are tried
here rather than one being chosen silently, because the whole point of the
refit is that the critical scale should come from the paper.

    python analysis/refit_physc_2011_02_004.py --src <LONG.csv> --out out.csv
"""
import argparse
import collections
import csv
import math

import numpy as np
from scipy.optimize import curve_fit

HIRR0 = 31.9
N_EXP = 1.7
CEILING = 30.0


def form3(x, log_jc0, beta):
    return log_jc0 + beta * x


def fit_isotherm(H, J, hc2):
    """Fit log10 Jc = log10 Jc,partial + beta log10(1 - H/Hc2) on one isotherm.

    Points at or above Hc2 are dropped, because 1 - H/Hc2 is not positive there
    and the model is undefined, not merely a poor fit.
    """
    keep = H < hc2 * 0.999
    H, J = H[keep], J[keep]
    if len(H) < 4:
        return None
    x = np.log10(1.0 - H / hc2)
    y = np.log10(J)
    (a, b), cov = curve_fit(form3, x, y, p0=[y.max(), 1.0],
                            bounds=([-np.inf, -CEILING], [np.inf, CEILING]),
                            maxfev=20000)
    se = float(np.sqrt(np.diag(cov))[1])
    resid = y - form3(x, a, b)
    rms = float(np.sqrt((resid ** 2).mean()))
    window = float((H.max() - H.min()) / hc2)
    return dict(n_pts=int(len(H)), Hc2_T_used=round(float(hc2), 4),
                H_axis_range_normalized=round(window, 4),
                beta=round(float(b), 4), SE_beta=round(se, 4),
                log_Jc_partial=round(float(a), 4), rms=round(rms, 5),
                at_ceiling=bool(abs(abs(b) - CEILING) < 1e-3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tc", type=float, nargs="+", default=[45.0, 48.0, 51.0])
    args = ap.parse_args()

    by_T = collections.defaultdict(list)
    for r in csv.DictReader(open(args.src)):
        by_T[float(r["temperature_K"])].append(
            (float(r["field_T"]), float(r["Jc_A_per_cm2"])))

    rows = []
    for T in sorted(by_T):
        H = np.array([h for h, _ in by_T[T]], float)
        J = np.array([j for _, j in by_T[T]], float)
        base = fit_isotherm(H, J, 120.0)          # the Tier-3 literature default
        if base:
            base.update(fixed_axis_value=T, Hc2_source="Tier_3_literature_default",
                        Tc_assumed="", provenance="literature default 120 T")
            rows.append(base)
        for tc in args.tc:
            hirr = HIRR0 * (1.0 - T / tc) ** N_EXP
            f = fit_isotherm(H, J, hirr)
            if not f:
                continue
            f.update(fixed_axis_value=T, Hc2_source="Tier_1_paper_Hirr",
                     Tc_assumed=tc,
                     provenance="arXiv 1002.0208 Eq.(5): Hirr(0)=31.9 T, n=1.7")
            rows.append(f)

    cols = ["fixed_axis_value", "Hc2_source", "Tc_assumed", "Hc2_T_used",
            "n_pts", "H_axis_range_normalized", "beta", "SE_beta",
            "log_Jc_partial", "rms", "at_ceiling", "provenance"]
    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    print("%-6s %-26s %-6s %-9s %-5s %-8s %-9s %-8s" %
          ("T", "Hc2 source", "Tc", "Hc2 used", "n", "window", "beta", "rms"))
    for r in rows:
        print("%-6.1f %-26s %-6s %-9.3f %-5d %-8.4f %-9.4f %-8.5f" %
              (r["fixed_axis_value"], r["Hc2_source"], r["Tc_assumed"],
               r["Hc2_T_used"], r["n_pts"], r["H_axis_range_normalized"],
               r["beta"], r["rms"]))
    print("\nwritten to %s" % args.out)


if __name__ == "__main__":
    main()
