#!/usr/bin/env python3
"""
withheld_shells.py

Summarises the predictions the dispatch gates withhold, for Sec. 16 of the
Supplemental Material.

Why this exists, and what it is not. Two gates in Sec. III.E refuse a large
majority of the evaluation grid: a field target below the validated reduced
field of 0.3, and membership of a family that fails the field-axis screening
threshold. Those refusals are the correct behaviour and the manuscript reports
no value for them. But the model still computed something, and deleting it
would leave a reader unable to see how far the framework reaches or what it
would take to extend it. The withheld values are therefore retained in the
dispatch table under withheld_ columns and summarised here.

Nothing in this file is a prediction. Every row is a projection outside the
interval over which the exponent was fitted, or inside a family whose
leave-one-out error exceeds the screening threshold, or both. The distinction
matters most where the numbers look most reasonable, because a withheld value
carries no validation at all and reads exactly like one that does.

    python analysis/withheld_shells.py

Run from the repository root.
"""
import os
import sys

import numpy as np
import pandas as pd

PRED = os.path.join("data", "phase_3_p57_de_novo_predictions.csv")
OUT = os.path.join("audit", "withheld_shells_summary.csv")

LABEL = {"iron_chalcogenide_11": "Iron chalcogenide 11-type",
         "iron_pnictide_122": "Iron pnictide 122-type",
         "conventional_AlB2": "MgB2-class"}
REASON = {"H_below_validated_reduced_field": "reduced field below 0.3",
          "family_fails_field_axis_validation": "family fails the field axis"}


def main():
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    d = pd.read_csv(PRED, low_memory=False)
    d["refusal_flag"] = d["refusal_flag"].fillna("")
    if "withheld_log_Jc" not in d.columns:
        sys.exit("no withheld columns; run analysis/apply_field_window_gate.py first")

    w = d[d.withheld_log_Jc.notna()]
    e = d[d.refusal_flag == ""]

    print("dispatched and withheld, by family\n")
    print("%-26s %9s %9s %11s %11s %s"
          % ("family", "emitted", "withheld", "h_red min", "h_red max", "withheld log Jc"))
    rows = []
    for fam in ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]:
        we = w[w.substructure == fam]
        ee = e[e.substructure == fam]
        if we.empty and ee.empty:
            continue
        print("%-26s %9d %9d %11.4f %11.4f  %.2f to %.2f"
              % (LABEL[fam], len(ee), len(we), we.withheld_reduced_field.min(),
                 we.withheld_reduced_field.max(), we.withheld_log_Jc.min(),
                 we.withheld_log_Jc.max()))
        for code, sub in we.groupby("refusal_flag"):
            rows.append(dict(
                family=LABEL[fam], reason=REASON.get(code, code),
                n_targets=len(sub), n_compounds=sub.compound_formula.nunique(),
                reduced_field_min=round(float(sub.withheld_reduced_field.min()), 4),
                reduced_field_max=round(float(sub.withheld_reduced_field.max()), 4),
                withheld_log_Jc_median=round(float(sub.withheld_log_Jc.median()), 3),
                withheld_log_Jc_min=round(float(sub.withheld_log_Jc.min()), 3),
                withheld_log_Jc_max=round(float(sub.withheld_log_Jc.max()), 3),
                median_interval_width_dex=round(float(
                    (sub.withheld_log_Jc_upper_95 - sub.withheld_log_Jc_lower_95).median()), 3)))

    print("\nwithheld set by reason\n")
    print("%-26s %-30s %8s %10s %14s"
          % ("family", "reason", "targets", "compounds", "median log Jc"))
    for r in rows:
        print("%-26s %-30s %8d %10d %14.3f"
              % (r["family"], r["reason"], r["n_targets"], r["n_compounds"],
                 r["withheld_log_Jc_median"]))

    print("\nwhat the withheld set would restore\n")
    restored = w.compound_formula.nunique()
    both = set(e.compound_formula) | set(w.compound_formula)
    print("   compounds with an emitted target                 %4d" % e.compound_formula.nunique())
    print("   compounds appearing only in the withheld set     %4d"
          % len(set(w.compound_formula) - set(e.compound_formula)))
    print("   compounds covered if the window were validated   %4d" % len(both))
    print("   families with an emitted target                  %4d" % e.substructure.nunique())
    print("   families in the withheld set                     %4d" % w.substructure.nunique())

    print("\nhow far outside the window the withheld set sits\n")
    q = w.withheld_reduced_field.quantile([0.5, 0.9, 1.0])
    print("   median reduced field %.3f, 90th percentile %.3f, maximum %.3f"
          % (q.loc[0.5], q.loc[0.9], q.loc[1.0]))
    print("   fraction below one tenth of the bound: %.0f%%"
          % (100 * (w.withheld_reduced_field < 0.03).mean()))

    os.makedirs("audit", exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("\nwritten to %s" % OUT)


if __name__ == "__main__":
    main()
