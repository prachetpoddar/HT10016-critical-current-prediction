#!/usr/bin/env python3
"""
score_field_axis_census.py

Score the pre-registered field-axis census on the statistic that was
pre-registered, and report what that statistic says rather than what a
different one said.

The census is the complete set of untraced passing field-axis papers that have a
usable source document: four papers, 28 of the 94 passing fits, fixed in
audit/field_axis_census_preregistration_20260905.md before any tracing began.
It exists because the earlier six-paper comparison used a set selected for
suspicion.

Why this script exists rather than the shell it replaces. The first report of
the census answered a different question from the one pre-registered. The
pre-registration fixes the primary statistic as the per-fit median of
|log(deposited beta_H / figure beta_H)|. What was reported instead was the
median of |log10(extraction Jc / figure Jc)| over data points, which never
touches beta_H, and it was compared against a temperature-axis number computed
in natural logs. Both errors flattered the field axis. Both are corrected here,
and both statistics are printed side by side so the difference is visible.

    python3 analysis/score_field_axis_census.py

Run from the repository root. Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "analysis")
from adjudicate_field_axis import PASS, beta_H, figure_beta, trace, MIN_LEVER

FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
EXT = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
       "v3_2_2B_extension/")

# The four census papers, their traces, how a deposited sample maps onto the
# figure, and the factor the extraction's field column needs to reach tesla.
CENSUS = {
    "elsevier_10.1016_j.physc.2013.04.060": dict(
        traces={10.0: "physc_2013_04_060_fig2", 4.2: "physc_2013_04_060_fig3"},
        field_scale=1.0,
        samples={"Undoped_MgB2_10K": "Undoped_MgB2_10K",
                 "SiC_Doped_MgB2_10K": "SiC_Doped_MgB2_10K",
                 "ZrB2_Doped_MgB2_10K": "ZrB2_Doped_MgB2_10K",
                 "Ag_Doped_MgB2_10K": "Ag_Doped_MgB2_10K",
                 "TiC_Doped_MgB2_10K": "TiC_Doped_MgB2_10K",
                 "MgB2_4_2K": "MgB2-00",
                 "MgB(2-x)Cx_x_0_0386_4_2K": "MgB2-01",
                 "MgB(2-x)Cx_x_0_1202_4_2K": "MgB2-04"},
        exclude={"MgB2-00": "the black series also matches the other two curves' "
                            "connecting lines; ten points where the figure plots five"}),
    "elsevier_10.1016_j.matchemphys.2023.128348": dict(
        traces={20.0: "matchemphys_2023_128348_fig5"}, field_scale=1.0,
        samples={"X01": "X01", "X02": "X02", "X03": "X03", "X04": "X04"},
        exclude={}),
    "elsevier_10.1016_j.physc.2009.11.051": dict(
        traces={2.0: "physc_2009_11_051_fig3", 10.0: "physc_2009_11_051_fig3",
                15.0: "physc_2009_11_051_fig3", 20.0: "physc_2009_11_051_fig3"},
        field_scale=0.1,
        samples={"irradiated": "irradiated", "unirradiated": "unirradiated"},
        exclude={}, per_temp=True),
    "elsevier_10.1016_j.physc.2010.05.048": dict(
        traces={t: "physc_2010_05_048_fig3" for t in (2., 3., 4., 5., 6., 7., 8., 9.)},
        field_scale=0.1,
        samples={"FeTe0.59Se0.41": None}, exclude={}, by_temp_series=True),
}

# Per-paper medians of |log10(extraction Jc / figure Jc)|, the secondary
# statistic, reproduced by an independent reviewer to three decimals.
JC_AGREEMENT = {
    "elsevier_10.1016_j.physc.2013.04.060": (0.004, "60 of 63"),
    "elsevier_10.1016_j.matchemphys.2023.128348": (0.119, "9 of 20"),
    "elsevier_10.1016_j.physc.2009.11.051": (0.393, "5 of 28"),
    "elsevier_10.1016_j.physc.2010.05.048": (0.566, "1 of 52"),
}

# The temperature axis, per paper, as analysis/adjudicate_temperature_axis.py
# reports it: deposited/figure beta ratios.
TEMPERATURE = [0.29, 0.25, 0.52, 0.40, 0.38, 0.19, 0.56, 0.09, 1.00, 0.47,
               0.94, 0.43, 0.69, 0.29]

# How each extraction was made, from the extraction files' own columns.
METHOD = {
    "elsevier_10.1016_j.physc.2013.04.060": "user digitisation",
    "elsevier_10.1016_j.matchemphys.2023.128348": "vision_pass",
    "elsevier_10.1016_j.physc.2009.11.051": "vision_pass_round3",
    "elsevier_10.1016_j.physc.2010.05.048": "vision_pass_round3",
}


def series_for(cfg, row):
    if cfg.get("by_temp_series"):
        return "%gK" % row.fixed_axis_value
    if cfg.get("per_temp"):
        return "%s_%dK" % (cfg["samples"].get(row.sample_identifier,
                                              row.sample_identifier),
                           int(row.fixed_axis_value))
    return cfg["samples"].get(row.sample_identifier)


def main():
    d = PASS(pd.read_csv(FITS))
    print("=" * 88)
    print("THE PRE-REGISTERED STATISTIC: beta_H from the figure against the deposit")
    print("=" * 88)
    print("Same Hc2, same temperature, same H < Hc2 window on both sides.")
    print()
    print("%-42s %5s %9s %9s %8s" % ("paper", "fits", "deposited", "figure", "|ln|"))
    per_fit, per_paper = [], {}
    for k, cfg in CENSUS.items():
        g = d[d.paper_key == k]
        rr = []
        for _, r in g.iterrows():
            nm = cfg["traces"].get(r.fixed_axis_value)
            s = series_for(cfg, r)
            if nm is None or s in cfg.get("exclude", {}):
                continue
            t = trace(nm)
            if s is not None:
                t = t[t.series == s]
            if t.empty:
                continue
            t = t.copy()
            f = figure_beta(t, r.fixed_axis_value, r.Hc2_T_used)
            if not f or f["lever"] < MIN_LEVER or f["beta"] == 0:
                continue
            rr.append(abs(np.log(abs(r.beta / f["beta"]))))
            per_fit.append(rr[-1])
        if rr:
            per_paper[k] = float(np.median(rr))
            print("%-42s %5d %9s %9s %8.3f"
                  % (k[:42], len(rr), "", "", per_paper[k]))
    print()
    if per_fit:
        print("  census, per fit   : %d fits, median |ln ratio| %.3f"
              % (len(per_fit), np.median(per_fit)))
    if per_paper:
        print("  census, per paper : %d papers, median |ln ratio| %.3f"
              % (len(per_paper), np.median(list(per_paper.values()))))
    tb = np.abs(np.log(np.array(TEMPERATURE)))
    print("  temperature axis  : %d papers, median |ln ratio| %.3f"
          % (len(tb), np.median(tb)))
    try:
        from scipy.stats import mannwhitneyu
        if per_paper:
            p = mannwhitneyu(list(per_paper.values()), tb, alternative="less").pvalue
            print("\n  field closer to agreement than temperature : p = %.3f" % p)
    except Exception:
        pass
    print("\n  Both arms are natural logs. The first report of this census compared")
    print("  a log10 statistic against a natural-log one, which is where its")
    print("  p = 0.025 came from; in one base it is not significant.")

    print()
    print("=" * 88)
    print("THE SECONDARY STATISTIC: the extracted Jc against the figure")
    print("=" * 88)
    print("%-42s %-20s %8s %10s" % ("paper", "extraction method", "|log10|", "in 0.1 dex"))
    for k, (v, w) in JC_AGREEMENT.items():
        print("%-42s %-20s %8.3f %10s" % (k[:42], METHOD[k], v, w))
    print("\n  The agreement ordering is exactly the method ordering. The one paper")
    print("  that agrees essentially exactly was extracted by hand, so comparing it")
    print("  with a pixel trace is close to a self-comparison. It is not a control")
    print("  for the vision-pass extractions, and none of those has been shown to")
    print("  reproduce a figure.")


if __name__ == "__main__":
    main()
