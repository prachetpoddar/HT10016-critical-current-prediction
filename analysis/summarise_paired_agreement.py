#!/usr/bin/env python3
"""
summarise_paired_agreement.py

Turns audit/paired_extraction_agreement.csv into the numbers the response letter
needs, and lists the cases a person has to adjudicate rather than averaging them
away.
"""
import csv, json, os, statistics, collections, importlib.util

# Recompute the compound comparison from the stored replies rather than trusting
# the flag written at run time, so a fix to the folding rules can be applied
# without paying for the run again.
_spec = importlib.util.spec_from_file_location(
    "_paired", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "paired_extraction_agreement.py"))
_paired = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_paired)

SRC = "audit/paired_extraction_agreement.csv"
OUT = "audit/paired_extraction_agreement_summary.json"
FIELDS = ["jc_h_sweep_present", "jc_t_sweep_present", "primary_scan_direction",
          "primary_compound", "T_min_K", "T_max_K", "H_min_T", "H_max_T"]
GATING = FIELDS[:3]
NUMERIC = ["T_min_K", "T_max_K", "H_min_T", "H_max_T"]

allrows = list(csv.DictReader(open(SRC)))
tv = lambda s: str(s).strip().lower() == "true"
rows = [r for r in allrows if not r["error"]]
for r in rows:
    rel = _paired.compound_relation(r["a__primary_compound"], r["b__primary_compound"])
    r["compound_relation"] = rel
    r["agree__primary_compound"] = str(rel == "exact")
    n_ok = sum(1 for f in FIELDS if str(r["agree__%s" % f]).strip().lower() == "true")
    r["n_fields_agree"] = n_ok
    r["agreement_fraction"] = round(n_ok / len(FIELDS), 4)
oos = [r for r in allrows if r["error"].startswith("out_of_scope")]
unavail = [r for r in allrows if r["error"] and not r["error"].startswith("out_of_scope")]

per_field = {f: round(sum(tv(r["agree__%s" % f]) for r in rows) / len(rows), 4)
             for f in FIELDS} if rows else {}
frac = [float(r["agreement_fraction"]) for r in rows]
gate = [tv(r["gating_all_agree"]) for r in rows]

# The numeric window only means anything where both readers found a sweep at all.
both_h = [r for r in rows if tv(r["a__jc_h_sweep_present"]) and tv(r["b__jc_h_sweep_present"])]
win = {f: round(sum(tv(r["agree__%s" % f]) for r in both_h) / len(both_h), 4)
       for f in NUMERIC} if both_h else {}

rel = collections.Counter(r["compound_relation"] for r in rows)

summary = {
    "readers": [rows[0]["model_a"], rows[0]["model_b"]] if rows else None,
    "papers_compared": len(rows),
    "out_of_scope_not_papers": len(oos),
    "pdf_unavailable_or_error": len(unavail),
    "mean_field_agreement": round(statistics.mean(frac), 4) if frac else None,
    "median_field_agreement": round(statistics.median(frac), 4) if frac else None,
    "papers_in_full_agreement": sum(1 for f in frac if f == 1.0),
    "gating_all_agree": sum(gate),
    "gating_agreement_rate": round(sum(gate) / len(gate), 4) if gate else None,
    "manual_adjudication_fraction": round(1 - sum(gate) / len(gate), 4) if gate else None,
    "per_field_agreement": per_field,
    "window_agreement_where_both_found_a_sweep": {"n_papers": len(both_h), **win},
    "compound_relation_counts": dict(rel),
    "total_cost_usd": round(sum(float(r["cost_usd"] or 0) for r in rows), 4),
}
json.dump(summary, open(OUT, "w"), indent=1)
print(json.dumps(summary, indent=1))

adj = [r for r in rows if r["compound_relation"] in
       ("same_elements_diff_coefficients", "subset_extra_elements", "disjoint")]
if adj:
    print("\ncompound pairs to adjudicate by hand (%d):" % len(adj))
    print("  %-34s %-30s %-30s %s" % ("identifier", "reader A", "reader B", "relation"))
    for r in adj:
        print("  %-34s %-30s %-30s %s" % (r["identifier"][:34],
              str(r["a__primary_compound"])[:30], str(r["b__primary_compound"])[:30],
              r["compound_relation"]))

dis = [r for r in rows if not tv(r["gating_all_agree"])]
if dis:
    print("\ngating disagreements (%d):" % len(dis))
    for r in dis:
        print("  %-34s A: h=%s t=%s dir=%-7s   B: h=%s t=%s dir=%s" % (
            r["identifier"][:34], r["a__jc_h_sweep_present"], r["a__jc_t_sweep_present"],
            r["a__primary_scan_direction"], r["b__jc_h_sweep_present"],
            r["b__jc_t_sweep_present"], r["b__primary_scan_direction"]))
