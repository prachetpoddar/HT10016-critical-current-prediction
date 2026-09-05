#!/usr/bin/env python3
"""
test_anchored_extrapolation.py

Discriminate two explanations for the temperature-axis extractions:

  H_gen     the series were produced by evaluating a model on a grid, with no
            contact with the published figure
  H_anchor  a few real points were read off the figure and a model was
            interpolated and extrapolated through them onto a grid

Both hypotheses predict smooth, grid-regular, parametrically exact series, so
smoothness alone cannot separate them.  Three properties can.

  1. SEPARABILITY.  Is log Jc(H,T) a rank-1 surface, f(T) + g(H)?  A real
     Jc(H,T) is not: the field dependence steepens as T rises and the
     irreversibility field collapses.  A constructed surface usually is.
     Separability is evidence of construction under either hypothesis; it is
     reported because it bounds how much independent information the numbers
     can carry.

  2. SHARED PARAMETERS ACROSS PAPERS.  Anchoring is per-figure: the fitted
     decay constants should differ from paper to paper because the figures do.
     A common generator leaves the same constants everywhere.

  3. CONTACT WITH THE FIGURE.  Under H_anchor the extraction must agree with
     the figure within reading error somewhere - at the anchors.  2305.10034v1
     is the arXiv preprint of jallcom.2023.170384, whose Cohort B extraction of
     the same figure was validated against an independent trace.  The two
     extractions of one figure can therefore be compared directly.

    python3 analysis/test_anchored_extrapolation.py

Run from the repository root.  Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

DEP = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
WIDE = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
        "agent2_dataset_v3_2_1.csv")


def load():
    dep = pd.read_csv(DEP)
    wide = pd.read_csv(WIDE)
    return dep, wide


def surface(wide, paper):
    """Return the (T x H) log10 Jc matrix for one paper, NaN where absent."""
    sub = wide[wide["pdf_name"] == paper]
    sub = sub[(sub["Jc"] > 0)]
    if sub.empty:
        return None, None, None
    piv = sub.pivot_table(index="temperature_K", columns="field_T",
                          values="Jc", aggfunc="median")
    M = np.log10(piv.values.astype(float))
    return M, piv.index.values, piv.columns.values


def rank1_residual(M):
    """
    Fit M ~ f(T) + g(H) by the standard additive (two-way) decomposition and
    report the residual.  A rank-1 surface in log space is exactly separable.
    """
    ok = np.isfinite(M)
    if ok.sum() < 6:
        return None, None
    A = np.where(ok, M, np.nan)
    # two-way additive fit, iterated to handle missing cells
    f = np.zeros(A.shape[0])
    g = np.zeros(A.shape[1])
    mu = np.nanmean(A)
    for _ in range(200):
        f = np.nanmean(A - mu - g[None, :], axis=1)
        g = np.nanmean(A - mu - f[:, None], axis=0)
    R = A - (mu + f[:, None] + g[None, :])
    r = R[ok]
    return float(np.sqrt(np.nanmean(r ** 2))), float(np.nanmax(np.abs(r)))


def main():
    if not os.path.exists(WIDE):
        sys.exit("wide file not found: %s" % WIDE)
    dep, wide = load()

    papers = sorted(dep["paper_id"].unique())
    print("=" * 78)
    print("1. SEPARABILITY  -  is log Jc(H,T) exactly f(T) + g(H)?")
    print("=" * 78)
    print("%-22s %6s %6s %10s %10s" % ("paper", "nT", "nH", "rms(dex)", "max(dex)"))
    sep = {}
    for p in papers:
        M, T, H = surface(wide, p)
        if M is None:
            print("%-22s %6s %6s %10s %10s" % (p[:22], "-", "-", "absent", "-"))
            continue
        rms, mx = rank1_residual(M)
        if rms is None:
            print("%-22s %6d %6d %10s %10s" % (p[:22], M.shape[0], M.shape[1], "too few", "-"))
            continue
        sep[p] = rms
        print("%-22s %6d %6d %10.5f %10.5f" % (p[:22], M.shape[0], M.shape[1], rms, mx))

    if sep:
        v = np.array(list(sep.values()))
        print("\nexactly separable to < 0.01 dex : %d of %d papers"
              % (int((v < 0.01).sum()), len(v)))
        print("separable to < 0.05 dex         : %d of %d papers"
              % (int((v < 0.05).sum()), len(v)))
    return sep


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Controls: the same statistics computed on figures actually traced from the
# page.  2012.13723v3 and 2207.06629v1 are two of the eighteen papers and both
# have a pixel trace in data/reextraction, so the extraction and the figure can
# be compared on the same paper rather than by analogy.
# ---------------------------------------------------------------------------

TRACES = {
    "2012.13723v3.pdf": os.path.join("data", "reextraction", "2012.13723_fig4_points.csv"),
    "2207.06629v1.pdf": os.path.join("data", "reextraction", "2207.06629_fig4_points.csv"),
    "2305.10034v1.pdf": os.path.join("data", "reextraction", "jallcom_2023_170384_fig6c_points.csv"),
}


def trace_surface(path):
    t = pd.read_csv(path)
    t = t[t["Jc_A_per_cm2"] > 0]
    return t


def controls():
    print()
    print("=" * 78)
    print("1b. SEPARABILITY OF THE TRACED FIGURES  (the control)")
    print("=" * 78)
    print("Same statistic, computed on points read off the page by the digitiser.")
    print("%-22s %6s %6s %10s %10s" % ("paper", "nT", "nH", "rms(dex)", "max(dex)"))
    for p, path in TRACES.items():
        t = trace_surface(path)
        # put the trace on a common field grid by log-log interpolation
        temps = sorted(t["temperature_K"].unique())
        lo = max(t.groupby("temperature_K")["field_T"].min())
        hi = min(t.groupby("temperature_K")["field_T"].max())
        if not (hi > lo):
            print("%-22s %6d %6s %10s" % (p[:22], len(temps), "-", "no overlap"))
            continue
        grid = np.geomspace(max(lo, 1e-3), hi, 12)
        M = np.full((len(temps), len(grid)), np.nan)
        for i, T in enumerate(temps):
            s = t[t["temperature_K"] == T].sort_values("field_T")
            x = np.log10(np.clip(s["field_T"].values, 1e-4, None))
            y = np.log10(s["Jc_A_per_cm2"].values)
            M[i] = np.interp(np.log10(grid), x, y, left=np.nan, right=np.nan)
        rms, mx = rank1_residual(M)
        print("%-22s %6d %6d %10.5f %10.5f" % (p[:22], len(temps), len(grid), rms, mx))


def contact(dep, wide):
    """
    3. CONTACT WITH THE FIGURE.  For each paper that has both an extraction and
    a trace, compare the extraction to the figure at the extraction's own
    field/temperature points.  Under anchored extrapolation some points are
    real readings and must agree within reading error.
    """
    print()
    print("=" * 78)
    print("3. CONTACT WITH THE FIGURE")
    print("=" * 78)
    for p, path in TRACES.items():
        t = trace_surface(path)
        sub = wide[(wide["pdf_name"] == p) & (wide["Jc"] > 0)]
        if sub.empty:
            print("\n%s : no extraction rows" % p)
            continue
        print("\n%s" % p)
        print("  %6s %8s %12s %12s %10s" %
              ("T(K)", "H(T)", "extraction", "figure", "diff(dex)"))
        diffs = []
        for T in sorted(sub["temperature_K"].unique()):
            s = t[np.isclose(t["temperature_K"], T, atol=0.6)].sort_values("field_T")
            if len(s) < 3:
                continue
            x = np.log10(np.clip(s["field_T"].values, 1e-4, None))
            y = np.log10(s["Jc_A_per_cm2"].values)
            e = sub[sub["temperature_K"] == T].sort_values("field_T")
            for _, r in e.iterrows():
                H = r["field_T"]
                if H <= 0:
                    continue
                lh = np.log10(H)
                if lh < x.min() or lh > x.max():
                    continue
                fig = np.interp(lh, x, y)
                ext = np.log10(r["Jc"])
                d = ext - fig
                diffs.append(d)
                if len(diffs) <= 200:
                    print("  %6.1f %8.3f %12.3e %12.3e %+10.3f"
                          % (T, H, r["Jc"], 10 ** fig, d))
        if diffs:
            a = np.array(diffs)
            print("  ---")
            print("  points compared            : %d" % len(a))
            print("  median offset              : %+.3f dex" % np.median(a))
            print("  scatter about that offset  : %.3f dex" % np.std(a - np.median(a)))
            print("  points within 0.05 dex     : %d" % int((np.abs(a) < 0.05).sum()))
            print("  points within 0.10 dex     : %d" % int((np.abs(a) < 0.10).sum()))


if __name__ == "__main__":
    pass
