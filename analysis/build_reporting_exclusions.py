#!/usr/bin/env python3
"""
build_reporting_exclusions.py

Encodes the two reporting-layer screens that the dispatch routine does not
write back into phase_3_p57_de_novo_predictions.csv, so that every count in
the manuscript can be reproduced from the deposit alone.

Screen 1, record level: a candidate record whose transition-temperature anchor
lies below 4.2 K, the lowest absolute temperature on the evaluation grid,
cannot be evaluated at the reference point and is refused.

Screen 2, prediction level: emitted tuples whose predicted value is an
extrapolation far outside the family's calibration cohort are removed. These
are identified in the deposited within-substructure outlier audit.

Output: audit/reporting_layer_exclusions.csv, one row per affected tuple.
"""
import csv, json

SRC = "data/phase_3_p57_de_novo_predictions.csv"
OUT = "audit/reporting_layer_exclusions.csv"
T_FLOOR = 4.2
OUTLIER_COMPOUNDS = {"Fe1Te1", "Fe1Se0.05Te0.95"}

rows = list(csv.DictReader(open(SRC)))
out = []
for r in rows:
    try:
        tc = float(r["Tc_anchor_K"])
    except (ValueError, KeyError):
        continue
    emitted = not r["refusal_flag"].strip()
    tags = []
    if tc < T_FLOOR:
        tags.append(("record_below_grid_floor",
                     f"Tc anchor {tc} K < {T_FLOOR} K grid floor"))
    if (emitted and r["compound_formula"] in OUTLIER_COMPOUNDS
            and abs(float(r["T_K"]) - 0.77 * tc) < 1e-6):
        tags.append(("calibration_outlier",
                     "0.77*Tc extrapolation far below family calibration cohort"))
    for tag, crit in tags:
        out.append({**{k: r[k] for k in ("compound_formula", "substructure", "Tc_anchor_K",
                                         "T_K", "H_T", "predicted_log_Jc", "refusal_flag")},
                    "emitted_by_dispatch": emitted,
                    "exclusion": tag, "criterion": crit})

with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

# a compound is reported only if it retains at least one emitted, non-excluded tuple
excluded_keys = {(r["compound_formula"], r["T_K"], r["H_T"]) for r in out}
emitted_all, retained = set(), set()
for r in rows:
    if r["refusal_flag"].strip():
        continue
    emitted_all.add(r["compound_formula"])
    if (r["compound_formula"], r["T_K"], r["H_T"]) not in excluded_keys:
        retained.add(r["compound_formula"])

summary = dict(
    total_tuples=len(rows),
    emitted_by_dispatch=sum(1 for r in rows if not r["refusal_flag"].strip()),
    compounds_dispatched=len(emitted_all),
    tuples_flagged_record_below_grid_floor=sum(1 for r in out if r["exclusion"] == "record_below_grid_floor"),
    tuples_flagged_calibration_outlier=sum(1 for r in out if r["exclusion"] == "calibration_outlier"),
    emitted_tuples_removed=len({(r["compound_formula"], r["T_K"], r["H_T"])
                                for r in out if r["emitted_by_dispatch"]}),
    compounds_reported=len(retained),
    compounds_removed=sorted(emitted_all - retained),
)
print(json.dumps(summary, indent=1))
json.dump(summary, open("audit/reporting_layer_summary.json", "w"), indent=1)
