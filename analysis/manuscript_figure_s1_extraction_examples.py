#!/usr/bin/env python3
"""
manuscript_figure_s1_extraction_examples.py

Generator for Supplemental Figure S1: three worked extraction-to-fit examples.

Referee A asked to see examples from the dataset. Tables S4 to S6 give rows;
this gives the curves those rows came from, so the extraction, the fitting
window and the fit can be audited against each other by eye.

The three panels are chosen to span the outcomes rather than to flatter:

  (a) retained.    FeTeSe at 2 K, physc.2010.05.048. Ten extracted points, a
                   resolved critical field of 3.5 T at the measurement
                   temperature, and a fit over the three points inside it. The
                   span is 0.571 of that scale, which clears the applicability
                   bound, and beta_H is 0.107 with a standard error of 0.018.

  (b) bound-hit.   Bi-2212 at 53 K, s41467-025-55880-4. Six points spanning
                   0.01 to 0.25 T against a literature 100 T scale, a span of
                   0.0024. The fit runs to the numerical ceiling at beta_H = 30
                   with a standard error of 37.6, larger than the estimate
                   itself. This is the failure mode of Sec. III.F, and the row
                   is in Table S5 for the same reason.

  (c) withdrawn.   FeTe0.61Se0.39 at 2 K, physc.2010.03.003. Five points falling
                   by exactly 0.5 dex each across field intervals of 4.5, 10, 10
                   and 25 T. A reading of a curve cannot produce a constant
                   factor between points that is independent of how far the
                   field moved. This record is withdrawn, and the panel is what
                   the log-ladder signature in audit_extraction_integrity.py
                   detects.

Data: the deposited extraction files under data/extraction_examples/, which are
the vision-pass outputs themselves rather than anything derived from them. Fit
parameters are read from the deposited Form 3 fit table, not refitted here, so
the drawn curve is the fit the paper reports.

    python analysis/manuscript_figure_s1_extraction_examples.py

Run from the repository root; writes figures/figure_S1_extraction_examples.png.
"""
import os
import sys

import matplotlib
import logging as _logging
# font.family carries fallbacks for other machines, so matplotlib warns
# once per missing family per text element. Several hundred lines that
# look like failures, on a render that succeeded.
_logging.getLogger("matplotlib.font_manager").setLevel(_logging.ERROR)
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({"font.family": "serif", "font.size": 9,
                     "mathtext.fontset": "dejavuserif"})
INK = "#1A1D23"; OK = "#1B8A7A"; GREY = "#7A828E"; ACC = "#3B4A8C"; BAD = "#B4472F"

EX = os.path.join("data", "extraction_examples")
FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
OUT = os.path.join("figures", "figure_S1_extraction_examples.png")

PANELS = [
    dict(file="physc_2010_05_048_field_axis.csv", T=2.0, sample="FeTe0.59Se0.41",
         doi="j.physc.2010.05.048", key="physc.2010.05.048", fixed=2.0,
         title="(a)  retained", colour=OK),
    dict(file="s41467_025_55880_4_field_axis.csv", T=53.0, sample="s1",
         doi="s41467-025-55880-4", key="s41467-025-55880-4", fixed=53.0,
         title="(b)  applicability bound", colour=ACC),
    dict(file="physc_2010_03_003_withdrawn_field_axis.csv", T=2.0,
         sample="FeTe0.61Se0.39", doi="j.physc.2010.03.003", key=None,
         fixed=None, title="(c)  withdrawn", colour=BAD),
]


def fit_row(key, fixed, sample):
    f = pd.read_csv(FITS)
    s = f[f.arxiv_id.str.contains(key, regex=False)
          & (f.fixed_axis_value == fixed)
          & (f.sample_identifier == sample)]
    if len(s) != 1:
        sys.exit("expected one fit for %s at %s, found %d" % (key, fixed, len(s)))
    return s.iloc[0]


def main():
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.65))
    for ax, p in zip(axes, PANELS):
        d = pd.read_csv(os.path.join(EX, p["file"]))
        d = d[(d.temperature_K == p["T"])
              & (d.doping_or_composition.astype(str).str.startswith(p["sample"]))]
        d = d.sort_values("field_T")
        H = d.field_T.values
        Y = np.log10(d.Jc_A_per_cm2.values)

        ax.plot(H, Y, "o", ms=4.2, mfc="white", mec=GREY, mew=1.0, zorder=3)

        if p["key"]:
            r = fit_row(p["key"], p["fixed"], p["sample"])
            hc2, n = float(r.Hc2_T_used), int(r.n_pts)
            used = slice(0, n)
            ax.plot(H[used], Y[used], "o", ms=4.6, mfc=p["colour"],
                    mec=p["colour"], zorder=4)
            ax.axvspan(H[0], H[n - 1], color=p["colour"], alpha=0.09, zorder=1)
            grid = np.linspace(H[0], H[n - 1], 200)
            grid = grid[grid < hc2]
            ax.plot(grid, r.log_Jc_partial
                    + r.beta * np.log10(1.0 - grid / hc2),
                    "-", lw=1.5, color=p["colour"], zorder=5)
            kind = ("$H_{c2}$ resolved" if abs(hc2 - float(r.Hc2_T_default)) > 1e-9
                    else "$H_{c2}$ literature default")
            ax.text(0.97, 0.90, "%s\n%.3g T" % (kind, hc2),
                    transform=ax.transAxes, fontsize=6.8, color="#5A616C",
                    ha="right", va="top", linespacing=1.3)
            ax.text(0.03, 0.055,
                    "span %.3g of the scale\n$\\beta_H$ = %.3g (%.3g)"
                    % (r.H_axis_range_normalized, r.beta, r.SE_beta),
                    transform=ax.transAxes, fontsize=6.8, color=INK,
                    va="bottom", linespacing=1.35)
        else:
            # The withdrawn record has no retained fit. What the panel shows is
            # the signature that removed it, so the steps are annotated instead.
            ax.plot(H, Y, "-", lw=1.0, color=p["colour"], alpha=0.55, zorder=2)
            ax.plot(H, Y, "o", ms=4.6, mfc=p["colour"], mec=p["colour"], zorder=4)
            for i in range(len(H) - 1):
                ax.annotate("", xy=(H[i + 1], Y[i + 1]), xytext=(H[i + 1], Y[i]),
                            arrowprops=dict(arrowstyle="-|>", lw=0.8, color=BAD,
                                            shrinkA=0, shrinkB=0))
                ax.text(H[i + 1] - 1.5, 0.5 * (Y[i] + Y[i + 1]), "0.500",
                        fontsize=6.4, color=BAD, va="center", ha="right")
            ax.set_xlim(-4.0, H[-1] * 1.16)
            ax.text(0.03, 0.055,
                    "0.500 dex per point,\nacross gaps of 4.5, 10,\n10 and 25 T",
                    transform=ax.transAxes, fontsize=6.8, color=INK,
                    va="bottom", linespacing=1.35)

        ax.set_title(p["title"], fontsize=8.4, color=INK, pad=5, loc="left")
        ax.set_xlabel("$\\mu_0 H$  (T)", fontsize=8)
        ax.text(0.99, 0.99, p["doi"], transform=ax.transAxes, fontsize=6.2,
                color=GREY, ha="right", va="top")
        ax.tick_params(labelsize=7.4)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel("$\\log_{10}\\,J_c$   ($J_c$ in A cm$^{-2}$)", fontsize=8)

    os.makedirs("figures", exist_ok=True)
    fig.tight_layout(w_pad=1.4)
    fig.savefig(OUT, dpi=300)
    print("written %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
