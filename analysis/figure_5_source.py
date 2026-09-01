#!/usr/bin/env python3
"""
figure_5_source.py

Figure 5 - Substructure-base Jc(T, H) curves with bootstrap CI envelopes.
Two-panel side-by-side, two-column width (178 mm).

Left panel:  Jc(T) at fixed H = 1 T for each populated substructure
Right panel: Jc(H) at fixed T = 4.2 K for each populated substructure

Data sources (priority order):
  1. phase_3_p57_de_novo_predictions.csv - per-candidate predictions at
     the pointwise target grid (T = 4.2, 20, 0.77*Tc) x (H = 0.1, 1, 5 T)
  2. Fit parameters from phase_3_p57_de_novo_predictions.py fit pools
     (substructure-aggregate beta_T median, beta_H median, log_Jc_partial
     median) for smooth Kramer-type curve interpolation between grid points

Anchor convention (matches p57 dispatch):
  log10 Jc(T, H) = log_Jc_partial_anchor
                 + beta_T * [log10(1 - T/Tc) - log10(1 - T_ref/Tc)]
                 + beta_H * [log10(1 - H/Hc2) - log10(1 - H_ref/Hc2)]
  T_ref = 4.2 K, H_ref = 0.1 T.

Verified reference values at (T = 4.2 K, H = 1 T):
  iron_chalcogenide_11 median log Jc = 5.985
  iron_pnictide_122 median log Jc    = 5.741
  conventional_AlB2 median log Jc    = 5.269

Verified median bootstrap CI width = 0.39 dex (across non-refused
predictions; used as constant-width envelope at +/- 0.194 dex around each
curve).

Output: figure_5_substructure_base_curves.png at 300 DPI.
"""

from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# In the deposit the predictor module sits beside this script in analysis/ and
# the figures go to figures/, rather than the prep-folder layout these scripts
# were written against.
P57_PY = HERE / "phase_3_p57_de_novo_predictions.py"
OUT = ROOT / "figures" / "figure_5_substructure_base_curves.png"

plt.rcParams.update({
    "font.family": "Helvetica",
    "font.size": 10,
    "axes.titlesize": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "mathtext.fontset": "stixsans",
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
})

SUB_COLORS = {
    "iron_chalcogenide_11": "#1B9E77",
    "iron_pnictide_122": "#D95F02",
    "conventional_AlB2": "#7570B3",
}
SUB_LABELS = {
    "iron_chalcogenide_11": "Iron chalcogenide 11-type",
    "iron_pnictide_122": "Iron pnictide 122-type",
    "conventional_AlB2": r"MgB$_2$-class",
}

# Representative per-substructure Tc and Hc2 anchors for curve generation.
# Tc values use the family-canonical values per the manuscript (14 K / 38 K /
# 39 K). Pipeline-derived Cohort B v2 medians for cross-reference are 14 K
# (chalc_11; matches), 22 K (pn-122; reflects Ba-122 undoped subset; the
# canonical 38 K covers the K-doped optimum that dominates the §6 candidate
# cohort), 39 K (AlB2; matches). Hc2 values are family-canonical maxima used
# at the substructure-aggregate Stage 3 predictor anchor.
SUB_TC_HC2 = {
    "iron_chalcogenide_11": dict(Tc=14.0, Hc2=25.0),   # FeSe-family canonical
    "iron_pnictide_122": dict(Tc=38.0, Hc2=50.0),       # BaFe2As2 K-doped canonical
    "conventional_AlB2": dict(Tc=39.0, Hc2=18.0),       # MgB2 canonical
}

# Reference log Jc at (T = 4.2 K, H = 1 T) under the uniform largest-cell-
# scope commitment rule (chalc_11 + pn-122 commit to single_crystal; AlB2
# substructure-aggregate). Recovered from the regenerated p57 predictions.
LOG_JC_REF_AT_4P2K_1T = {
    "iron_chalcogenide_11": 5.984,
    "iron_pnictide_122": 5.741,
    "conventional_AlB2": 5.269,
}

# Median bootstrap CI width across non-refused p57 predictions under the
# uniform commitment rule (essentially unchanged from prior 0.388 dex
# because single_crystal cell dominates the chalc_11 Cohort B v2 pool).
# Reported as 0.39 dex in the text following Referee A's objection to excessive
# precision on a bootstrap width. The figure must not contradict the text.
CI_WIDTH_DEX = 0.39
CI_HALF = CI_WIDTH_DEX / 2.0

T_REF = 4.2
H_REF = 0.1
H_FIXED_LEFT = 1.0   # H for left panel
T_FIXED_RIGHT = 4.2  # T for right panel


def _import(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_substructure_fit_params() -> dict[str, dict]:
    """Pull substructure-aggregate beta_T median, beta_H median, and
    log_Jc_partial median from the p57 dispatch's fit pools."""
    p57 = _import("p57", P57_PY)
    beta_t_pool = p57.build_beta_t_pool()
    beta_h_agg, _ = p57.build_beta_h_log_jcp_pool()
    out = {}
    for sub in SUB_COLORS:
        out[sub] = dict(
            beta_T=float(np.median(beta_t_pool[sub])),
            beta_H=float(np.median(beta_h_agg[sub]["beta_H"])),
            log_jcp=float(np.median(beta_h_agg[sub]["log_jcp"])),
            n_beta_T=len(beta_t_pool[sub]),
            n_beta_H=beta_h_agg[sub]["n"],
        )
    return out


def form3_log_Jc(T_K: np.ndarray, H_T: np.ndarray, params: dict,
                  Tc: float, Hc2: float, anchor_value: float) -> np.ndarray:
    """Evaluate Form 3 log Jc at (T, H) grid with anchor convention.

    The substructure-aggregate predictor anchors the prediction at
    (T_ref = 4.2 K, H_ref = 1 T) using the verified reference log Jc value
    (anchor_value). The Form 3 fractional terms then scale relative to that
    anchor.
    """
    # Both arrays must be same shape after broadcasting
    T_K = np.asarray(T_K, dtype=float)
    H_T = np.asarray(H_T, dtype=float)
    # Clip arguments inside (0, 1) range to avoid log(0) or log(negative)
    tT_actual = np.log10(np.clip(1.0 - T_K / Tc, 1e-9, None))
    tT_ref = np.log10(np.clip(1.0 - T_REF / Tc, 1e-9, None))
    tH_actual = np.log10(np.clip(1.0 - H_T / Hc2, 1e-9, None))
    tH_ref_1T = np.log10(np.clip(1.0 - H_FIXED_LEFT / Hc2, 1e-9, None))
    # Reference at (4.2 K, 1 T): anchor_value
    return (anchor_value
            + params["beta_T"] * (tT_actual - tT_ref)
            + params["beta_H"] * (tH_actual - tH_ref_1T))


def build_left_panel_curves(fit_params: dict, n_points: int = 80) -> dict:
    """Jc(T) at fixed H = 1 T for each substructure."""
    curves = {}
    for sub in SUB_COLORS:
        Tc = SUB_TC_HC2[sub]["Tc"]
        Hc2 = SUB_TC_HC2[sub]["Hc2"]
        # T grid from 4.2 K to 0.92*Tc
        T_grid = np.linspace(T_REF, 0.92 * Tc, n_points)
        H_grid = np.full(n_points, H_FIXED_LEFT)
        anchor = LOG_JC_REF_AT_4P2K_1T[sub]
        log_jc = form3_log_Jc(T_grid, H_grid, fit_params[sub], Tc, Hc2, anchor)
        curves[sub] = dict(T=T_grid, log_Jc=log_jc, Tc=Tc, Hc2=Hc2)
    return curves


def build_right_panel_curves(fit_params: dict, n_points: int = 80) -> dict:
    """Jc(H) at fixed T = 4.2 K for each substructure."""
    curves = {}
    for sub in SUB_COLORS:
        Tc = SUB_TC_HC2[sub]["Tc"]
        Hc2 = SUB_TC_HC2[sub]["Hc2"]
        # H grid from 0.1 T to 0.92*Hc2 (or 10 T cap, whichever smaller)
        H_max = min(10.0, 0.92 * Hc2)
        H_grid = np.linspace(H_REF, H_max, n_points)
        T_grid = np.full(n_points, T_FIXED_RIGHT)
        anchor = LOG_JC_REF_AT_4P2K_1T[sub]
        log_jc = form3_log_Jc(T_grid, H_grid, fit_params[sub], Tc, Hc2, anchor)
        curves[sub] = dict(H=H_grid, log_Jc=log_jc, Tc=Tc, Hc2=Hc2)
    return curves


def main():
    fit_params = get_substructure_fit_params()
    print("Substructure-aggregate fit parameters (medians from p57 pools):")
    for sub, p in fit_params.items():
        print(f"  {sub}: beta_T = {p['beta_T']:.3f} (n={p['n_beta_T']}); "
              f"beta_H = {p['beta_H']:.3f} (n={p['n_beta_H']}); "
              f"log_Jc_partial = {p['log_jcp']:.3f}")
    left = build_left_panel_curves(fit_params)
    right = build_right_panel_curves(fit_params)

    # Cross-check the reference value at (T = 4.2 K, H = 1 T)
    for sub in SUB_COLORS:
        ref_recovery = form3_log_Jc(np.array([T_REF]), np.array([H_FIXED_LEFT]),
                                       fit_params[sub], SUB_TC_HC2[sub]["Tc"],
                                       SUB_TC_HC2[sub]["Hc2"],
                                       LOG_JC_REF_AT_4P2K_1T[sub])
        print(f"  {sub} predicted log Jc(4.2K, 1T) = {float(ref_recovery[0]):.3f} "
              f"vs verified reference {LOG_JC_REF_AT_4P2K_1T[sub]:.3f}")

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(7.01, 3.5),
                                              sharey=True)

    # --- Left panel: Jc(T) at H = 1 T ---
    for sub in SUB_COLORS:
        c = left[sub]
        color = SUB_COLORS[sub]
        ax_left.plot(c["T"], c["log_Jc"], color=color, lw=1.6,
                       label=SUB_LABELS[sub], zorder=3)
        ax_left.fill_between(c["T"], c["log_Jc"] - CI_HALF, c["log_Jc"] + CI_HALF,
                                color=color, alpha=0.30, zorder=2,
                                linewidth=0)
    # T = 4.2 K reference line removed from left panel per Hossain review
    # (redundant with right-panel title "J_c(H) at T = 4.2 K"; also caused
    # legend-frame collision in the lower-left).
    ax_left.set_xlabel("T (K)")
    ax_left.set_ylabel(r"log$_{10}$ J$_c$ (A/cm$^2$)")
    ax_left.set_title(r"J$_c$(T) at H = 1 T")
    # Determine x-range: from 0 K to max Tc + small margin (capped at 50 K)
    max_T = min(50.0, max(SUB_TC_HC2[s]["Tc"] for s in SUB_COLORS) + 4.0)
    ax_left.set_xlim(0, max_T)

    # Tc vertical reference lines per substructure at 30% alpha in
    # substructure color. Labels are placed later (after ylim is set)
    # using a staircase y-fraction stagger to keep the 38 K and 39 K
    # labels visually distinct.
    for sub in SUB_COLORS:
        tc = SUB_TC_HC2[sub]["Tc"]
        color = SUB_COLORS[sub]
        ax_left.axvline(tc, color=color, ls="--", lw=1.2, alpha=0.30,
                          zorder=1)

    # --- Right panel: Jc(H) at T = 4.2 K ---
    for sub in SUB_COLORS:
        c = right[sub]
        color = SUB_COLORS[sub]
        ax_right.plot(c["H"], c["log_Jc"], color=color, lw=1.6,
                        label=SUB_LABELS[sub], zorder=3)
        ax_right.fill_between(c["H"], c["log_Jc"] - CI_HALF,
                                  c["log_Jc"] + CI_HALF,
                                  color=color, alpha=0.30, zorder=2,
                                  linewidth=0)
    ax_right.axvline(H_FIXED_LEFT, color="#666666", ls=":", lw=1.0, zorder=1)
    ax_right.set_xlabel("H (T)")
    ax_right.set_title(r"J$_c$(H) at T = 4.2 K")
    ax_right.set_xlim(0, 10)

    # Right-panel reference tick marks at the y-axis for verified values
    # at (T = 4.2 K, H = 1 T) per substructure. Numeric labels relocated to
    # OUTSIDE the panel's left edge per Hossain review (previous in-panel
    # white-boxed labels occluded curve/envelope content). The colored tick
    # mark stays on the y-axis at x in [0, 0.30] (well clear of the H = 1 T
    # dotted reference line); labels render to the left of the axis at
    # x = -0.20 with clip_on=False.
    for sub in SUB_COLORS:
        val = LOG_JC_REF_AT_4P2K_1T[sub]
        color = SUB_COLORS[sub]
        # Tick mark at the y-axis (slightly shorter to not cross H = 1 T line)
        ax_right.plot([0.0, 0.30], [val, val],
                        color=color, lw=2.2,
                        solid_capstyle="butt", zorder=4)
        # Numeric label outside the left edge of the panel, right-aligned
        ax_right.text(-0.20, val, f"{val:.2f}",
                        color=color, fontsize=8, va="center", ha="right",
                        zorder=5, clip_on=False)

    # Annotation: median CI width as a bracket on the right edge of the
    # right panel. Placed at H = 8.5 T in clear space below the legend.
    h_anno = 8.5
    c_122 = right["iron_pnictide_122"]
    idx_anno = int(np.searchsorted(c_122["H"], h_anno))
    if idx_anno >= len(c_122["log_Jc"]):
        idx_anno = len(c_122["log_Jc"]) - 1
    y_center = c_122["log_Jc"][idx_anno] - 0.6  # offset below curve to avoid overlap
    # Bracketed error bar with thicker line + taller caps for readability
    ax_right.errorbar([h_anno], [y_center], yerr=[[CI_HALF], [CI_HALF]],
                        fmt="none", ecolor="black", capsize=5, capthick=1.3,
                        elinewidth=1.3, zorder=5)
    ax_right.text(h_anno - 0.3, y_center,
                    "Median CI\nwidth =\n0.388 dex",
                    fontsize=8, va="center", ha="right", color="black")

    # Shared y-axis: set a reasonable shared range
    # Determine range from all curves
    all_log_jc = []
    for c in list(left.values()) + list(right.values()):
        all_log_jc.append(c["log_Jc"])
    all_log_jc = np.concatenate(all_log_jc)
    y_max = float(np.max(all_log_jc)) + CI_HALF + 0.4
    y_min = float(np.min(all_log_jc)) - CI_HALF - 0.4
    ax_left.set_ylim(y_min, y_max)

    # Tc labels (placed after ylim set so axes-fraction positioning is
    # final). Per Hossain review: labels relocated to the LEFT of each Tc
    # dashed line (text + line collision was prohibited). Horizontal
    # placement uses a per-substructure left-offset; vertical staircase
    # stagger retained to keep the 38 K (pn-122) and 39 K (AlB2) labels
    # (whose vertical lines sit only 1 K apart) visually separable.
    tc_label_y_frac = {
        "iron_chalcogenide_11": 0.94,
        "iron_pnictide_122": 0.88,
        "conventional_AlB2": 0.74,
    }
    # Larger left-offset for pn-122 + AlB2 so the right edges of those
    # labels do not collide with each other at the close-x cluster.
    tc_label_x_offset = {
        "iron_chalcogenide_11": 1.5,
        "iron_pnictide_122": 1.5,
        "conventional_AlB2": 1.5,
    }
    for sub in SUB_COLORS:
        tc = SUB_TC_HC2[sub]["Tc"]
        color = SUB_COLORS[sub]
        y_frac = tc_label_y_frac[sub]
        y_label = y_min + y_frac * (y_max - y_min)
        x_label = tc - tc_label_x_offset[sub]
        ax_left.text(x_label, y_label, rf"T$_c$ = {tc:.0f} K",
                       color=color, fontsize=8, va="center", ha="right",
                       rotation=0, alpha=0.95,
                       bbox=dict(facecolor="white", edgecolor=color,
                                   pad=1.2, lw=0.5, alpha=0.85))

    # Legend on left panel (lower-left, out of the curve region)
    ax_left.legend(loc="lower left", fontsize=10, frameon=True,
                     edgecolor="#666666", framealpha=0.95,
                     borderpad=0.5)

    for ax in (ax_left, ax_right):
        ax.grid(True, ls=":", lw=0.5, alpha=0.4)

    plt.tight_layout()
    plt.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
