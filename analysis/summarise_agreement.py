#!/usr/bin/env python3
"""
summarise_agreement.py

Turns audit/cross_model_agreement.csv into the two numbers the response letter
needs: the cross-model extraction agreement rate for the fitted cohort, and for
the full archive, with the per-field breakdown and the manual-adjudication
fraction (papers where the two readers disagree on any gating field).
"""
import csv, json, statistics, collections

SRC = "audit/cross_model_agreement.csv"
OUT = "audit/cross_model_agreement_summary.json"
GATING = ["jc_h_sweep_present", "jc_t_sweep_present", "primary_scan_direction"]

rows = [r for r in csv.DictReader(open(SRC)) if not r["error"]]
errs = [r for r in csv.DictReader(open(SRC)) if r["error"]]
tv = lambda s: str(s).strip().lower() == "true"


def block(sub, label):
    if not sub:
        return {label: "no rows"}
    frac = [float(r["agreement_fraction"]) for r in sub]
    gate_disagree = [r for r in sub if any(not tv(r[f"agree__{f}"]) for f in GATING)]
    per_field = {}
    for f in [k[7:] for k in sub[0] if k.startswith("agree__")]:
        vals = [tv(r[f"agree__{f}"]) for r in sub]
        per_field[f] = round(sum(vals) / len(vals), 4)
    return {
        "n_papers": len(sub),
        "mean_field_agreement": round(statistics.mean(frac), 4),
        "median_field_agreement": round(statistics.median(frac), 4),
        "papers_in_full_agreement": sum(1 for f in frac if f == 1.0),
        "fraction_in_full_agreement": round(sum(1 for f in frac if f == 1.0) / len(sub), 4),
        "gating_field_disagreement_papers": len(gate_disagree),
        "manual_adjudication_fraction": round(len(gate_disagree) / len(sub), 4),
        "per_field_agreement": per_field,
        "total_cost_usd": round(sum(float(r["cost_usd"] or 0) for r in sub), 4),
    }


# Some PDFs in the archive were completed after the first pass ran, so the two
# readers were not always shown the same document. Those papers are reported
# separately and are not part of the headline rate.
same = [r for r in rows if str(r.get("pdf_changed", "")).strip().lower() != "true"]
moved = [r for r in rows if str(r.get("pdf_changed", "")).strip().lower() == "true"]

summary = {
    "model_second_reader": rows[0]["model"] if rows else None,
    "fitted_cohort": block([r for r in same if tv(r["in_fitted_cohort"])], "fitted_cohort"),
    "full_archive": block(same, "full_archive"),
    "pdf_changed_since_first_pass": block(moved, "pdf_changed"),
    "errors": {"n": len(errs),
               "kinds": dict(collections.Counter(e["error"].split(":")[0] for e in errs))},
}
json.dump(summary, open(OUT, "w"), indent=1)
print(json.dumps(summary, indent=1))
