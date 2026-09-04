"""
repair_tier_table_emission.py

Bring the prediction-derived columns of
data/phase_3_p56_candidate_tier_assignment.csv back into agreement with
data/phase_3_p57_de_novo_predictions.csv.

Why. The tier table was last written before the field-window gate (fbba543,
8d43b4c) and the temperature-window gate (cea6c85) were applied to the
prediction file. It marks 123 compounds as emitting, across three families,
where the prediction file emits 84, all of them MgB2-class, and the 84 are a
strict subset of the 123. Not one of those 84 carries the right count either:
0 of 84 have n_viable_predictions equal to the number of unrefused rows the
prediction file holds for them. Table IV of the manuscript carried the tier
table's number in its caption and the prediction file's in its body.

What this touches and what it does not. Six columns are recomputed, and they
are the six that are a function of the prediction file:

    n_viable_predictions, emits_predictions,
    predicted_log_Jc_min, predicted_log_Jc_median, predicted_log_Jc_max,
    median_CI_width_dex

Everything else is left alone. In particular `tier` and `refusal_detail` come
from the calibration-domain screen, which is a transition-temperature rule
against an empirical floor and does not read the prediction file, so the two
window gates cannot have moved them.

The candidate set itself is not regenerated. That would need 3DSC_MP.csv, which
is not in this deposit, and it does not need regenerating: the prediction file
still covers the same 183 compounds through the same 233 records. This script
refuses to write if that stops being true.

Usage:
    python3 analysis/repair_tier_table_emission.py [--dry-run]
"""
import argparse
import os
import sys

import pandas as pd

TIERS = os.path.join("data", "phase_3_p56_candidate_tier_assignment.csv")
PRED = os.path.join("data", "phase_3_p57_de_novo_predictions.csv")
DERIVED = ["n_viable_predictions", "emits_predictions",
           "predicted_log_Jc_min", "predicted_log_Jc_median",
           "predicted_log_Jc_max", "median_CI_width_dex"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")

    t = pd.read_csv(TIERS)
    p = pd.read_csv(PRED, low_memory=False)
    missing = [c for c in DERIVED if c not in t.columns]
    if missing:
        sys.exit("the tier table has no %s column(s)" % ", ".join(missing))

    # The two files must still be describing the same candidate set. If they
    # are not, the candidate list itself has moved and this script is the wrong
    # tool: that needs 3DSC_MP.csv and a rerun of
    # analysis/phase_3_p56_de_novo_candidate_list.py.
    if set(t.compound) != set(p.compound_formula):
        only_t = sorted(set(t.compound) - set(p.compound_formula))[:5]
        only_p = sorted(set(p.compound_formula) - set(t.compound))[:5]
        sys.exit("the two files describe different candidate sets; tier table "
                 "only: %s; prediction file only: %s" % (only_t, only_p))

    em = p[p.refusal_flag.isna()]
    n = em.groupby("compound_formula").size()
    lo = em.groupby("compound_formula").predicted_log_Jc.min()
    md = em.groupby("compound_formula").predicted_log_Jc.median()
    hi = em.groupby("compound_formula").predicted_log_Jc.max()
    width = (em.predicted_log_Jc_upper_95 - em.predicted_log_Jc_lower_95)
    ci = width.groupby(em.compound_formula).median()

    before = {"emitting_compounds": int((t.emits_predictions == "yes")
                                        .groupby(t.compound).any().sum()),
              "emitting_records": int((t.emits_predictions == "yes").sum()),
              "viable_total": int(t.n_viable_predictions.fillna(0).sum())}

    t["n_viable_predictions"] = t.compound.map(n).fillna(0).astype(int)
    t["emits_predictions"] = t.n_viable_predictions.gt(0).map(
        {True: "yes", False: "no"})
    t["predicted_log_Jc_min"] = t.compound.map(lo)
    t["predicted_log_Jc_median"] = t.compound.map(md)
    t["predicted_log_Jc_max"] = t.compound.map(hi)
    t["median_CI_width_dex"] = t.compound.map(ci)

    after = {"emitting_compounds": int(t.loc[t.emits_predictions == "yes",
                                             "compound"].nunique()),
             "emitting_records": int((t.emits_predictions == "yes").sum()),
             "viable_total": int(t.n_viable_predictions.sum())}

    print("tier table, prediction-derived columns\n")
    for k in before:
        print("   %-20s %6d  ->  %6d" % (k, before[k], after[k]))
    print()
    fam = t[t.emits_predictions == "yes"].groupby(
        "substructure_family").compound.nunique()
    print("   emitting compounds by family after the repair:")
    for k, v in fam.items():
        print("      %-24s %d" % (k, v))
    print()

    # A calibration-refused candidate must not emit. The screen is a separate
    # rule, so this is a real cross-check rather than a tautology.
    bad = t[(t.tier == "refused_calibration_domain")
            & (t.emits_predictions == "yes")]
    print("   calibration-refused records still marked emitting: %d"
          % len(bad))
    if after["emitting_compounds"] != em.compound_formula.nunique():
        sys.exit("recomputed %d emitting compounds against %d in the "
                 "prediction file" % (after["emitting_compounds"],
                                      em.compound_formula.nunique()))
    if args.dry_run:
        print("\n--dry-run, nothing written")
        return 0
    t.to_csv(TIERS, index=False)
    print("\nwritten %s" % TIERS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
