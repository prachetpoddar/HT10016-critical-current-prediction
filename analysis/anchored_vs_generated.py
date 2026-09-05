#!/usr/bin/env python3
"""
anchored_vs_generated.py

Test whether the temperature-axis extractions are better described as
generated from nothing or as low-fidelity readings of the published figures
extended by a smooth model.

The distinction matters because the two carry different remedies.  A generated
series has no recoverable content.  A coarse reading extended by a model has
content wherever the reading was possible, and the fitted quantity may survive
even where the series as a whole does not.

Ground truth is available for three of the eighteen papers, because their
figures were traced pixel by pixel during the field-axis recovery:

    2012.13723v3   Fig. 4    7 isotherms, 4 to 28 K
    2207.06629v1   Fig. 4    8 isotherms, 4 to 32 K
    2305.10034v1   Fig. 6(c) 4 isotherms, 2 to 10 K   (= jallcom.2023.170384)

Four tests, each reported against those traces rather than against intuition.

  A. TEMPERATURE SET.  Does the extraction's list of isotherm temperatures
     match the figure's?  A generator has no way to know it.

  B. CONTACT.  Compared at the extraction's own (T, H) points, how far is the
     extraction from the figure, and is the error structured (a smooth
     function of T or H) or unstructured?

  C. SEPARABILITY.  Is the extracted surface smoother in the rank-1 sense than
     the traced figure it claims to represent?  Reported with the trace as the
     control, since a real Jc(H,T) is not separable either.

  D. THE FITTED QUANTITY.  Refit beta_T from the traced figure inside each fit
     row's own temperature window and compare with the deposited value.  This
     is the only test whose answer bears on the manuscript, because beta_T is
     what the manuscript uses.  An error that is a function of H alone cancels
     in a temperature slope, so beta_T can survive a badly distorted field
     axis.

    python3 analysis/anchored_vs_generated.py

Run from the repository root.  Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

DEP = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
WIDE = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
        "agent2_dataset_v3_2_1.csv")

TRACES = {
    "2012.13723v3.pdf": os.path.join("data", "reextraction", "2012.13723_fig4_points.csv"),
    "2207.06629v1.pdf": os.path.join("data", "reextraction", "2207.06629_fig4_points.csv"),
    "2305.10034v1.pdf": os.path.join("data", "reextraction",
                                     "jallcom_2023_170384_fig6c_points.csv"),
}

T_TOL = 0.6          # K, matching an extraction temperature to a traced series
MIN_TRACE_PTS = 3    # points needed before a traced series is interpolated


def load():
    dep = pd.read_csv(DEP)
    wide = pd.read_csv(WIDE)
    return dep, wide


def traced(path):
    t = pd.read_csv(path)
    return t[t["Jc_A_per_cm2"] > 0].copy()


def figure_value(t, T, H):
    """
    log10 Jc read off the traced isotherm nearest T, at field H, by linear
    interpolation in log-log.  Returns NaN if H lies outside the traced span,
    so the comparison never extrapolates the figure.
    """
    s = t[np.isclose(t["temperature_K"], T, atol=T_TOL)].sort_values("field_T")
    if len(s) < MIN_TRACE_PTS or H <= 0:
        return np.nan
    x = np.log10(np.clip(s["field_T"].values, 1e-4, None))
    y = np.log10(s["Jc_A_per_cm2"].values)
    lh = np.log10(H)
    if lh < x.min() or lh > x.max():
        return np.nan
    return float(np.interp(lh, x, y))


def beta_T(temps, jcs, Tc):
    x = np.log10(1.0 - np.asarray(temps, float) / Tc)
    y = np.log10(np.asarray(jcs, float))
    if len(x) < 3 or np.ptp(x) == 0:
        return np.nan
    return float(np.polyfit(x, y, 1)[0])


def rank1_rms(M):
    """RMS residual of the additive fit M ~ mu + f(T) + g(H), NaN-tolerant."""
    ok = np.isfinite(M)
    if ok.sum() < 6:
        return np.nan
    A = np.where(ok, M, np.nan)
    f = np.zeros(A.shape[0])
    g = np.zeros(A.shape[1])
    mu = np.nanmean(A)
    for _ in range(300):
        f = np.nanmean(A - mu - g[None, :], axis=1)
        g = np.nanmean(A - mu - f[:, None], axis=0)
    R = (A - (mu + f[:, None] + g[None, :]))[ok]
    return float(np.sqrt(np.mean(R ** 2)))


def test_a(dep, wide):
    print("=" * 74)
    print("A. TEMPERATURE SET  -  does the extraction know the figure's isotherms?")
    print("=" * 74)
    for p, path in TRACES.items():
        t = traced(path)
        e = sorted(wide[(wide.pdf_name == p) & (wide.Jc > 0)]["temperature_K"].unique())
        f = sorted(t["temperature_K"].unique())
        shared = [x for x in e if any(abs(x - y) <= T_TOL for y in f)]
        print("  %-18s extraction %s" % (p[:18], e))
        print("  %-18s figure     %s" % ("", f))
        print("  %-18s matched    %d of %d extracted isotherms\n"
              % ("", len(shared), len(e)))


def test_b(dep, wide):
    print("=" * 74)
    print("B. CONTACT  -  extraction against the figure at the extraction's own points")
    print("=" * 74)
    print("  %-18s %6s %8s %9s %9s %9s"
          % ("paper", "pts", "median", "scatter", "|d|<0.1", "|d|<0.2"))
    for p, path in TRACES.items():
        t = traced(path)
        e = wide[(wide.pdf_name == p) & (wide.Jc > 0)]
        d = []
        for _, r in e.iterrows():
            fv = figure_value(t, r["temperature_K"], r["field_T"])
            if np.isfinite(fv):
                d.append(np.log10(r["Jc"]) - fv)
        if not d:
            continue
        a = np.array(d)
        print("  %-18s %6d %+9.3f %9.3f %9d %9d"
              % (p[:18], len(a), np.median(a), np.std(a - np.median(a)),
                 int((np.abs(a) < 0.1).sum()), int((np.abs(a) < 0.2).sum())))
    print()


def test_c(dep, wide):
    print("=" * 74)
    print("C. SEPARABILITY  -  extracted surface against the traced figure")
    print("=" * 74)
    print("  %-18s %12s %12s %8s" % ("paper", "extraction", "figure", "ratio"))
    for p, path in TRACES.items():
        t = traced(path)
        e = wide[(wide.pdf_name == p) & (wide.Jc > 0)]
        temps = sorted(e["temperature_K"].unique())
        fields = sorted(e["field_T"].unique())
        Me = np.full((len(temps), len(fields)), np.nan)
        Mf = np.full((len(temps), len(fields)), np.nan)
        for i, T in enumerate(temps):
            for j, H in enumerate(fields):
                row = e[(e.temperature_K == T) & (e.field_T == H)]
                if len(row):
                    Me[i, j] = np.log10(row["Jc"].iloc[0])
                Mf[i, j] = figure_value(t, T, H)
        # compare on the cells where both exist, so the grids are identical
        both = np.isfinite(Me) & np.isfinite(Mf)
        Me2 = np.where(both, Me, np.nan)
        Mf2 = np.where(both, Mf, np.nan)
        re_, rf = rank1_rms(Me2), rank1_rms(Mf2)
        print("  %-18s %12.4f %12.4f %8.2f"
              % (p[:18], re_, rf, (rf / re_) if re_ else np.nan))
    print()


def test_d(dep, wide):
    print("=" * 74)
    print("D. THE FITTED QUANTITY  -  deposited beta_T against the traced figure")
    print("=" * 74)
    print("  %-18s %6s %10s %10s %7s" % ("paper", "H(T)", "deposited", "figure", "ratio"))
    summary = {}
    for p, path in TRACES.items():
        t = traced(path)
        d = dep[dep.paper_id == p]
        if d.empty:
            continue
        ratios = []
        for _, r in d.iterrows():
            Tc, H = r["Tc_K"], r["field_T"]
            temps, jcs = [], []
            for T in sorted(t["temperature_K"].unique()):
                if not (r["T_min"] - T_TOL <= T <= r["T_max"] + T_TOL):
                    continue
                fv = figure_value(t, T, H)
                if np.isfinite(fv):
                    temps.append(T)
                    jcs.append(10 ** fv)
            if len(temps) < 3:
                continue
            b = beta_T(temps, jcs, Tc)
            if not np.isfinite(b) or b == 0:
                continue
            ratios.append(r["beta_T"] / b)
            print("  %-18s %6.2f %10.3f %10.3f %7.2f"
                  % (p[:18], H, r["beta_T"], b, r["beta_T"] / b))
        if ratios:
            a = np.array(ratios)
            summary[p] = a
            print("  %-18s %6s median ratio %.2f, range %.2f to %.2f, n=%d\n"
                  % ("", "", np.median(a), a.min(), a.max(), len(a)))
    return summary


def main():
    if not os.path.exists(WIDE):
        sys.exit("wide file not found: %s" % WIDE)
    dep, wide = load()
    test_a(dep, wide)
    test_b(dep, wide)
    test_c(dep, wide)
    s = test_d(dep, wide)
    print("=" * 74)
    print("VERDICT PER PAPER (beta_T is the quantity the manuscript uses)")
    print("=" * 74)
    for p, a in s.items():
        m = np.median(a)
        if 0.8 <= m <= 1.25:
            v = "beta_T recovered"
        elif 0.4 <= m < 0.8 or 1.25 < m <= 2.5:
            v = "beta_T biased, coherent"
        else:
            v = "beta_T not recovered"
        print("  %-18s median ratio %5.2f   %s" % (p[:18], m, v))


if __name__ == "__main__":
    main()
