#!/usr/bin/env python3
"""
figure_4_source.py

Generator for Figure 3 of the manuscript, and the library that every other
script uses for per-physical-sample aggregation and the variance decomposition.
The name predates the figure numbering and is kept because verify_deposit.py,
withdraw_records.py and permutation_test.py import from it.

Figure-to-script mapping for this deposit:

    Fig. 1  analysis/manuscript_figure_1.py
    Fig. 2  analysis/manuscript_figure_2.py
    Fig. 3  this file
    Fig. 4  analysis/manuscript_figure_4.py
    Fig. 5  analysis/manuscript_figure_5.py

Variance-decomposition diagnostic across populated substructures.
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

matplotlib is imported only when something is drawn. verify_deposit.py imports
this module for aggregate_per_physical_sample and compute_variance_decomposition
alone, and a reviewer checking the deposited numbers should not need a plotting
stack to do it.

Note on regenerating the figure: it renders in Helvetica or Arial with several
fallbacks. On a machine that has neither, matplotlib substitutes silently and
the deposited figure comes back with a different typeface while reporting
success.

Do not read the findfont warnings as the test. matplotlib walks the family list
in order and warns once per family it cannot resolve, so on macOS it warns about
Nimbus Sans and Liberation Sans, which are Linux fallbacks, while having found
Helvetica first and used it. A warning naming a fallback is expected; a warning
naming Helvetica AND Arial is the one that matters. The run reports the family
it actually resolved, which is the check to read.
"""

from __future__ import annotations
import re
import os
from pathlib import Path
import numpy as np
import pandas as pd

# matplotlib is imported lazily. verify_deposit.py imports this module only for
# aggregate_per_physical_sample and compute_variance_decomposition, neither of
# which draws anything, and a reviewer checking the deposit should not need a
# plotting stack to do it. A hard import here made verify_deposit.py fail with
# ModuleNotFoundError on a clean environment, which reads as a broken deposit
# rather than as a missing optional dependency.
plt = None


def _report_font():
    """Say which font family was actually used, so nobody has to interpret the
    findfont warnings to know whether the deposited typeface changed.

    Returns the family name, or None if nothing from the list resolved.
    """
    from matplotlib import font_manager
    for want in RC_PARAMS["font.family"]:
        try:
            path = font_manager.findfont(font_manager.FontProperties(family=want),
                                         fallback_to_default=False)
        except Exception:
            continue
        print("font resolved: %s  (%s)" % (want, os.path.basename(path)))
        if want not in ("Helvetica", "Arial"):
            print("WARNING: the deposited figure was drawn in %s, not Helvetica "
                  "or Arial. Do not commit this render." % want)
        return want
    print("WARNING: no family from the list resolved; matplotlib fell back to "
          "its default. Do not commit this render.")
    return None


def _write_stamp(df, family):
    """Record the ratios this render displays, but only for a valid render.

    analysis/check_figures.py compares this stamp against the deposit and fails
    when they differ, which is how a stale Figure 3 is caught. Writing it by
    hand is how it silently stops matching the PNG beside it, so the renderer
    writes it, and only when the typeface is the deposited one. A substituted
    font leaves the stamp alone, so a render that must not be committed cannot
    also certify itself.
    """
    import json
    if family not in ("Helvetica", "Arial"):
        print("stamp not written: %s is not the deposited typeface, so this "
              "render should not be committed" % (family or "the fallback"))
        return
    dec = compute_variance_decomposition(df)
    per = dec[dec["scope"] == "per_substructure"]
    drawn = {r.substructure: round(float(r.ratio_between_total), 4)
             for _, r in per.iterrows()
             if r.substructure in PANEL_SUBSTRUCTURES
             and r.ratio_between_total == r.ratio_between_total}
    STAMP.write_text(json.dumps(
        {"drawn_from": drawn,
         "font": family,
         "note": ("Ratios the committed figures/manuscript_figure_3.png "
                  "displays. Written by analysis/figure_4_source.py on a "
                  "render in the deposited typeface, and checked against the "
                  "deposit by analysis/check_figures.py. Do not edit by "
                  "hand.")}, indent=1) + "\n")
    print("stamp written: %s" % ", ".join(
        "%s %.4f" % (k, v) for k, v in sorted(drawn.items())))


def _quiet_findfont():
    """Silence matplotlib's per-fallback findfont warnings.

    font.family is a list with fallbacks for other machines, so matplotlib logs
    a warning for every family it cannot find even when the first one resolves.
    On macOS that is Nimbus Sans and Liberation Sans, twice per text element,
    which buries a successful render under several hundred lines that look like
    failures. _report_font() states which family was actually used, so the
    warnings carry nothing the run does not already say.
    """
    import logging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)


def _need_plt():
    global plt
    if plt is None:
        _quiet_findfont()
        import matplotlib.pyplot as _plt
        _plt.rcParams.update(RC_PARAMS)
        plt = _plt
    return plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# The anchor table and the figure live in data/ and figures/, not beside this
# script. The previous PREP = HERE.parent form resolved to the repository root
# and made load_cohort() and main() raise FileNotFoundError on a clean checkout,
# so the deposited figure could not be regenerated from the deposited data.
JC_ANCHOR_CSV = ROOT / "data" / "phase_3_p31_jc_anchor_per_paper.csv"
OUT = ROOT / "figures" / "manuscript_figure_3.png"
STAMP = ROOT / "figures" / "manuscript_figure_3.stamp.json"

RC_PARAMS = {
    "font.family": ["Helvetica", "Nimbus Sans", "Arial", "Liberation Sans", "DejaVu Sans"],
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
}

# The three families Figure 3 draws, in panel order. Hoisted to module scope
# so _write_stamp records exactly what was plotted rather than a second
# list that could drift from it.
PANEL_SUBSTRUCTURES = ["iron_chalcogenide_11", "iron_pnictide_122",
                    "conventional_AlB2"]

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
# The outcome letter is DERIVED from the ratio the panel computes, not stored.
# It was a dict frozen at A / B / C, so a band change left the figure printing
# the old letter while the panel's own number said otherwise, and any claim of
# label stability read off this figure was true by construction.
BANDS = ((0.7, "A"), (0.3, "B"))


def outcome_letter(ratio):
    if ratio is None or ratio != ratio:
        return "-"
    for lo, letter in BANDS:
        if ratio > lo or (letter == "B" and ratio >= lo):
            return letter
    return "C"

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


# The MAGLAB identifiers put the isotherm in the paper_id and cannot be parsed
# reliably by pattern, because the specimen token is itself sometimes numeric:
# MAGLAB_11_6K is specimen "11" at 6 K, while MAGLAB_11_4_2K is specimen "11" at
# 4.2 K, and no regex distinguishes "11 at 6 K" from "11.6 K" without knowing
# which tokens name a material. A first attempt at a general pattern read
# MAGLAB_11_6K as 11.6 K and produced a bare "MAGLAB" group. The set is ten
# records and closed, so it is enumerated rather than guessed.
#
# MAGLAB_Co122_4_2K and MAGLAB_Co122_4_2K_zero are the same film at the same
# temperature under different anchor fields, 1 T and self-field, so they are one
# specimen here.
MAGLAB_SPECIMEN = {
    "MAGLAB_11_4_2K": "MAGLAB_11",
    "MAGLAB_11_6K": "MAGLAB_11",
    "MAGLAB_Co122_4_2K": "MAGLAB_Co122",
    "MAGLAB_Co122_4_2K_zero": "MAGLAB_Co122",
    "MAGLAB_La1111_4_2K": "MAGLAB_La1111",
    "MAGLAB_Nd1111_10K": "MAGLAB_Nd1111",
    "MAGLAB_Nd1111_4_2K": "MAGLAB_Nd1111",
    "MAGLAB_Ni122_4_2K": "MAGLAB_Ni122",
    "MAGLAB_P122_4_2K": "MAGLAB_P122",
    "MAGLAB_Sm1111_4_2K": "MAGLAB_Sm1111",
}


def _specimen_key(pid: str) -> str:
    """Map an identifier to the physical specimen it measured.

    For DOI-style identifiers this is the identifier itself. For the MAGLAB
    records, which encode the isotherm in the identifier and carry
    sample_id='unspecified', it is the enumerated specimen above. Stripping only
    sample_id left all ten counted as independent physical samples, which is the
    opposite of what aggregate_per_physical_sample documents.
    """
    if not isinstance(pid, str):
        return str(pid)
    return MAGLAB_SPECIMEN.get(pid, pid)


def aggregate_per_physical_sample(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse multi-isotherm same-sample records to one row per physical sample.

    The Path 3 per-paper anchor table contains one row per
    (paper, sample, isotherm-T) measurement. Many rows are multi-isotherm
    measurements of the same physical sample, with the isotherm temperature
    encoded as a `_<num>K` suffix on either sample_id or, for the MAGLAB
    records, on paper_id. Both are stripped before grouping, and rows are
    collapsed by averaging log10_Jc_anchor within
    (substructure, stripped_paper_id, stripped_sample_id, sample_form) groups.

    Note on what the average means: where a sample was measured across a wide
    temperature range the mean of log10_Jc_anchor is not a physical anchor, it
    is the mean of values spanning that range. One record here collapses
    isotherms from 2 K to 40 K, a span of 2.4 dex. That is a property of the
    anchor definition rather than of this function, but a caller treating the
    result as a single-temperature quantity would be wrong to.

    Substructure filtering is NOT applied here — callers filter downstream.
    """
    df = df.copy()
    df["sample_id_stripped"] = df["sample_id"].apply(_strip_isotherm_suffix)
    df["paper_id_stripped"] = df["paper_id"].apply(_specimen_key)
    agg = df.groupby(
        ["substructure", "paper_id_stripped", "sample_id_stripped", "sample_form"],
        as_index=False,
    ).agg(
        log10_Jc_anchor=("log10_Jc_anchor", "mean"),
        n_isotherms=("log10_Jc_anchor", "count"),
    )
    agg.rename(columns={"sample_id_stripped": "sample_id",
                        "paper_id_stripped": "paper_id"}, inplace=True)
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
    # SAMPLE_FORM_DISPLAY already carries the line breaks. The 122 panel packs
    # four forms into the same width the others use for two or three, and at a
    # fixed 10 pt the second lines of "Poly-/crystal" and "Single/crystal" ran
    # into each other and rendered as "crystalcrystal". Scale the tick font with
    # the number of forms rather than wrapping, which would only add a third
    # line to labels that are already two.
    tick_fs = 10 if len(present_forms) <= 3 else 8.5
    ax.set_xticklabels([SAMPLE_FORM_DISPLAY[sf] for sf in present_forms],
                       rotation=0, fontsize=tick_fs, linespacing=1.2)
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
    decomp_row = compute_variance_decomposition(sub_df, substructures=[sub])
    ratio = float(decomp_row.loc[
        decomp_row["scope"] == "per_substructure", "ratio_between_total"
    ].iloc[0])
    outcome = outcome_letter(ratio)
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

    plt = _need_plt()
    fig, axes = plt.subplots(1, 3, figsize=(7.01, 3.3), sharey=True)
    subs_ordered = PANEL_SUBSTRUCTURES

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
            handles.append(_need_plt().Line2D([0], [0], marker=SAMPLE_FORM_MARKERS[sf],
                                         color="black", lw=0, ms=6,
                                         mec="black", mfc="lightgray"))
            # Capitalize first letter for marker legend; "_" -> space
            labels.append(sf.replace("_", " ").capitalize())
    fig.legend(handles, labels, loc="upper center", ncol=len(handles),
                  bbox_to_anchor=(0.5, 1.02), frameon=False, fontsize=10)

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(OUT, dpi=300, bbox_inches="tight")
    family = _report_font()
    _write_stamp(df, family)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
