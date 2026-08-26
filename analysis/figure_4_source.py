#!/usr/bin/env python3
"""
figure_4_source.py

Figure 4 - Variance-decomposition diagnostic across populated substructures.
Three side-by-side panels (one per populated substructure), two-column width
(178 mm), shared y-axis range.

Data source: phase_3_p31_jc_anchor_per_paper.csv (Path 3 per-paper
log_Jc_anchor table). Per-paper aggregation applied: multi-isotherm
measurements of one physical sample (sample_id with _<num>K suffix encoding
isotherm temperature) are collapsed to a single record via mean of
log_Jc_anchor within (paper_id, stripped_sample_id, sample_form) groups.

Per-panel sample-form distribution (post-aggregation, post-FST correction):
  iron_chalcogenide_11: n=13 (single_crystal 7, thin_film 4, polycrystal 2)
                        FST records previously mis-classified as wire have
                        been re-classified as thin_film per source-paper
                        verification (Piperno et al., Sci Rep 13:574, 2023).
  iron_pnictide_122:    n=16 (single_crystal 12, thin_film 2, polycrystal 1, wire 1)
                        of which polycrystal and wire are singletons (n=1)
  conventional_AlB2:    n=15 (wire 10, bulk 5)

Combined-correction variance-decomposition ratios (between-sample-form /
total at log_Jc_anchor scope; Outcome A/B/C thresholds preserved):
  iron_chalcogenide_11 = 0.73 (Outcome A; threshold >0.7; narrow pass)
  iron_pnictide_122    = 0.60 (Outcome B; threshold 0.3-0.7)
  conventional_AlB2    = 0.12 (Outcome C; threshold <0.3)

Singleton cells (n=1) display only the per-paper marker with explicit "n=1"
annotation; no median line or IQR box is drawn for cells with one record.

Output: figure_4_variance_decomposition.png at 300 DPI.
"""

from __future__ import annotations
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
PREP = HERE.parent
JC_ANCHOR_CSV = PREP / "phase_3_p31_jc_anchor_per_paper.csv"
OUT = HERE / "figure_4_variance_decomposition.png"

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
SUB_OUTCOMES = {
    "iron_chalcogenide_11": "A",
    "iron_pnictide_122": "B",
    "conventional_AlB2": "C",
}

# Sample-form marker shapes (redundant with color for grayscale safety)
SAMPLE_FORM_MARKERS = {
    "polycrystal": "o",
    "single_crystal": "s",
    "thin_film": "^",
    "wire": "D",
    "tape": "v",
    "bulk": "P",
}

SAMPLE_FORM_ORDER = ["polycrystal", "single_crystal", "thin_film",
                     "wire", "tape", "bulk"]
SAMPLE_FORM_DISPLAY = {
    "polycrystal": "Poly-\ncrystal",
    "single_crystal": "Single\ncrystal",
    "thin_film": "Thin\nfilm",
    "wire": "Wire",
    "tape": "Tape",
    "bulk": "Bulk",
}


def _strip_isotherm_suffix(sid: str) -> str:
    """Remove isotherm-K suffix from sample_id so multi-isotherm measurements
    of one physical sample collapse to a single grouping key. Pattern
    matches '_4K', '_4.2K', '_4_2K', '-5K', etc. (case-insensitive on K).
    """
    if not isinstance(sid, str):
        return str(sid)
    return re.sub(r'[_\-]\d+(?:\.\d+|_\d+)?\s*K$', '', sid,
                  flags=re.IGNORECASE).strip()


def aggregate_per_physical_sample(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse multi-isotherm same-sample records to one row per physical sample.

    The Path 3 per-paper anchor table contains one row per
    (paper, sample, isotherm-T) measurement. Many rows are multi-isotherm
    measurements of the same physical sample, with sample_id encoding the
    isotherm temperature as a `_<num>K` suffix. This collapses such rows to
    one record per physical sample by averaging log10_Jc_anchor within
    (substructure, paper_id, stripped_sample_id, sample_form) groups.

    Substructure filtering is NOT applied here — callers filter downstream.
    """
    df = df.copy()
    df["sample_id_stripped"] = df["sample_id"].apply(_strip_isotherm_suffix)
    agg = df.groupby(
        ["substructure", "paper_id", "sample_id_stripped", "sample_form"],
        as_index=False,
    ).agg(
        log10_Jc_anchor=("log10_Jc_anchor", "mean"),
        n_isotherms=("log10_Jc_anchor", "count"),
    )
    agg.rename(columns={"sample_id_stripped": "sample_id"}, inplace=True)
    return agg


def compute_variance_decomposition(
    cohort_df: pd.DataFrame,
    substructures=None,
) -> pd.DataFrame:
    """Between- vs within-sample-form variance decomposition on log10_Jc_anchor.

    Input: per-physical-sample DataFrame (e.g. output of
    aggregate_per_physical_sample) with columns substructure, sample_form,
    log10_Jc_anchor.

    Output: DataFrame with schema
    (scope, substructure, n_papers, n_sample_forms, total_var, between_sf_var,
    within_sf_var, ratio_between_total, note) matching
    phase_3_p31_variance_decomposition.csv. The aggregate_all row pools
    across all substructures; per-substructure rows decompose within each
    substructure separately. Single-form substructures are reported with
    only total_var populated and a "single sample_form" note.

    Variance convention: population-weighted (sum-of-squares / n), matching
    the prior production CSV. Between-form var is the n-weighted sum of
    squared form-mean deviations from the grand mean.
    """

    def _decomp(sub_df: pd.DataFrame):
        n = len(sub_df)
        if n == 0:
            return None
        n_forms = int(sub_df["sample_form"].nunique())
        grand = sub_df["log10_Jc_anchor"].mean()
        total_var = float(((sub_df["log10_Jc_anchor"] - grand) ** 2).sum() / n)
        gp = sub_df.groupby("sample_form")["log10_Jc_anchor"].agg(["mean", "count"])
        between_var = float((gp["count"] * (gp["mean"] - grand) ** 2).sum() / n)
        within_var = float(total_var - between_var)
        ratio = float(between_var / total_var) if total_var > 0 else float("nan")
        return dict(
            n_papers=int(n), n_sample_forms=n_forms,
            total_var=total_var, between_sf_var=between_var,
            within_sf_var=within_var, ratio_between_total=ratio,
        )

    rows = []
    agg = _decomp(cohort_df)
    if agg is not None:
        rows.append(dict(scope="aggregate_all", substructure="ALL", **agg, note=""))

    if substructures is None:
        substructures = sorted(cohort_df["substructure"].dropna().unique())
    for sub in substructures:
        sub_df = cohort_df[cohort_df["substructure"] == sub]
        r = _decomp(sub_df)
        if r is None:
            continue
        if r["n_sample_forms"] <= 1:
            rows.append(dict(
                scope="per_substructure", substructure=sub,
                n_papers=r["n_papers"], n_sample_forms=r["n_sample_forms"],
                total_var=r["total_var"], between_sf_var=None,
                within_sf_var=None, ratio_between_total=None,
                note="single sample_form; no decomposition",
            ))
        else:
            rows.append(dict(scope="per_substructure", substructure=sub, **r, note=""))
    return pd.DataFrame(rows)


def load_cohort() -> pd.DataFrame:
    """Load Path 3 per-paper log_Jc_anchor table; filter to the three
    populated substructures used in Figure 4; collapse multi-isotherm
    same-sample records via aggregate_per_physical_sample."""
    df = pd.read_csv(JC_ANCHOR_CSV)
    df = df[df["substructure"].isin(SUB_COLORS.keys())].copy()
    return aggregate_per_physical_sample(df)


def panel_one_substructure(ax, sub_df: pd.DataFrame, sub: str,
                            y_min: float, y_max: float, is_leftmost: bool):
    color = SUB_COLORS[sub]
    # Identify present sample forms in order
    present_forms = [sf for sf in SAMPLE_FORM_ORDER
                      if sf in sub_df["sample_form"].unique()]
    x_positions = {sf: i for i, sf in enumerate(present_forms)}

    # Per-cell median + IQR overlay first (so scatter sits on top). Skip
    # singleton cells (n=1): we do not draw a median bar or IQR box for
    # cells with a single record, since a single point has no within-cell
    # spread to characterize.
    singleton_cells = {}
    for sf, x in x_positions.items():
        cell = sub_df[sub_df["sample_form"] == sf]["log10_Jc_anchor"].dropna()
        n = len(cell)
        if n == 0:
            continue
        if n == 1:
            singleton_cells[sf] = float(cell.iloc[0])
            continue
        med = cell.median()
        q25 = cell.quantile(0.25)
        q75 = cell.quantile(0.75)
        # IQR box at 20% alpha
        ax.fill_between([x - 0.30, x + 0.30], q25, q75,
                          color=color, alpha=0.20, zorder=2,
                          linewidth=0)
        # Median bar
        ax.plot([x - 0.30, x + 0.30], [med, med],
                  color=color, lw=2.2, zorder=4)

    # Scatter individual per-paper estimates with sample-form markers
    rng = np.random.default_rng(42)
    for sf, x in x_positions.items():
        cell = sub_df[sub_df["sample_form"] == sf]
        marker = SAMPLE_FORM_MARKERS.get(sf, "o")
        n = len(cell)
        if n == 0:
            continue
        jitter = rng.uniform(-0.13, 0.13, size=n)
        ax.scatter(np.full(n, x) + jitter, cell["log10_Jc_anchor"].values,
                     c=color, marker=marker, s=28, alpha=0.65,
                     edgecolors="black", linewidths=0.4, zorder=3)
        # "n=1" annotation for singleton cells
        if sf in singleton_cells:
            ax.text(x + 0.18, singleton_cells[sf],
                      "n=1", fontsize=8, color=color, style="italic",
                      va="center", ha="left", zorder=5,
                      bbox=dict(facecolor="white", edgecolor="none",
                                  pad=0.5, alpha=0.75))

    # Cosmetics
    ax.set_xticks(list(x_positions.values()))
    ax.set_xticklabels([SAMPLE_FORM_DISPLAY[sf] for sf in present_forms],
                       rotation=0, fontsize=10)
    ax.set_xlim(-0.6, len(present_forms) - 0.4)
    ax.set_ylim(y_min, y_max)
    ax.set_title(SUB_LABELS[sub])
    if is_leftmost:
        ax.set_ylabel(r"log$_{10}$ J$_c$ anchor (A/cm$^2$)")
    # Major-tick spacing for log_Jc_anchor range (typical span ~7-8 dex)
    from matplotlib.ticker import MultipleLocator
    ax.yaxis.set_major_locator(MultipleLocator(2.0))
    ax.yaxis.set_minor_locator(MultipleLocator(0.5))
    if not is_leftmost:
        # Leave tick marks visible but suppress label duplication
        ax.tick_params(axis="y", labelleft=False)
    ax.grid(axis="y", linestyle=":", alpha=0.4, lw=0.5)

    # Annotation box (top-LEFT). Per Hossain review: previous top-right
    # position at y_frac 0.96/0.90 overlapped the highest thin_film triangle
    # markers in the chalc_11 and pn-122 panels. The upper-left region is
    # clear in all three panels (polycrystal/wire data sits at low y; left
    # column tops are empty above ~ log Jc 5.0).
    outcome = SUB_OUTCOMES[sub]
    decomp_row = compute_variance_decomposition(sub_df, substructures=[sub])
    ratio = float(decomp_row.loc[
        decomp_row["scope"] == "per_substructure", "ratio_between_total"
    ].iloc[0])
    ax.text(0.03, 0.96,
              f"Outcome {outcome}\nratio {ratio:.2f}",
              transform=ax.transAxes, ha="left", va="top",
              fontsize=10,
              bbox=dict(boxstyle="round,pad=0.35",
                         facecolor="white",
                         edgecolor=color, lw=0.8, alpha=0.95))


def main():
    df = load_cohort()

    # Compute shared y-range across all log_Jc_anchor values
    log_jc_vals = df["log10_Jc_anchor"].dropna().values
    y_min = float(np.floor(log_jc_vals.min())) - 0.5
    y_max = float(np.ceil(log_jc_vals.max())) + 0.5

    fig, axes = plt.subplots(1, 3, figsize=(7.01, 3.3), sharey=True)
    subs_ordered = ["iron_chalcogenide_11", "iron_pnictide_122",
                    "conventional_AlB2"]

    for i, (ax, sub) in enumerate(zip(axes, subs_ordered)):
        sub_df = df[df["substructure"] == sub].copy()
        print(f"{sub}: n_fits = {len(sub_df)}; "
              f"sample_forms = {sub_df['sample_form'].value_counts().to_dict()}")
        panel_one_substructure(ax, sub_df, sub, y_min, y_max,
                                is_leftmost=(i == 0))

    # Shared x-axis label centered below all three panels
    fig.text(0.5, 0.005, "Sample form", ha="center", va="bottom", fontsize=10)

    # Sample-form marker legend at top of figure
    handles = []
    labels = []
    forms_used = set()
    for sub in subs_ordered:
        for sf in df[df["substructure"] == sub]["sample_form"].unique():
            forms_used.add(sf)
    for sf in SAMPLE_FORM_ORDER:
        if sf in forms_used:
            handles.append(plt.Line2D([0], [0], marker=SAMPLE_FORM_MARKERS[sf],
                                         color="black", lw=0, ms=6,
                                         mec="black", mfc="lightgray"))
            # Capitalize first letter for marker legend; "_" -> space
            labels.append(sf.replace("_", " ").capitalize())
    fig.legend(handles, labels, loc="upper center", ncol=len(handles),
                  bbox_to_anchor=(0.5, 1.02), frameon=False, fontsize=10)

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
