#!/usr/bin/env python3
"""
verify_deposit.py

Checks that this deposit is internally consistent and reproduces its own
headline numbers, and prints the counts a reader needs to size the cohort.

Referee A asked four separate times to see the data, and asked specifically for
"the number of papers actually contributing Jc curves, the number of physical
samples, the number of compounds". Those are printed below, computed rather than
quoted, so no count in the manuscript rests on a number that exists only in
prose.

The consistency checks exist because this deposit has twice shipped in a state
that disagreed with itself. A withdrawal was applied to the source tables and
not to the derived decomposition, so the deposited decomposition described a
cohort that no longer existed. A unit correction reached two fields out of four,
leaving one table's two Jc columns a factor of a million apart and one sample
labelled a thin film in one table and a wire in two others. Both are the kind of
defect a reader finds in minutes and an author never sees, so they are asserted
here rather than trusted.

    python analysis/verify_deposit.py

Exit status is non-zero if any check fails.

Run from the repository root.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figure_4_source import (aggregate_per_physical_sample,      # noqa: E402
                             compute_variance_decomposition)

DATA = "data"
ANCHOR = os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv")
DERIVED = os.path.join(DATA, "phase_3_p31_variance_decomposition.csv")
BANDS = "A > 0.7 | B 0.3-0.7 | C < 0.3"

# What the manuscript prints, pinned here so that a cohort change which is not
# carried into the text fails loudly rather than sitting in a table nobody
# recomputes. Every earlier version of this deposit disagreed with its own
# manuscript on at least one of these.
MANUSCRIPT = dict(
    papers_contributing_anchor_rows=35,
    physical_samples=69,
    anchor_rows=105,
    fitted_curve_papers=65,          # Table I, "Papers contributing fitted curves"
    fitted_curve_compounds=40,       # Table I, "Distinct compounds with fitted curves"
    extracted_points=4247,           # Table I, "Critical-current data points extracted"
    temperature_axis_fits=414,       # Table I, "Temperature-axis partial fits"
    field_axis_fits_ok=88,           # Table I, "Field-axis partial fits passing physicality"
    field_axis_ok_papers=15,
    candidate_compounds=183,         # Table I, "Candidate compounds evaluated"
    dispatched_compounds=85,         # Table IV, combined "dispatched"
    dispatch_tuples=2097,
    emitted_targets=256,
    candidate_records=233,           # Supplement Sec. 12, record-level counts
    calibration_retained=212,
    calibration_refused=21,
    calibration_high_confidence=82,
    calibration_graded_confidence=130,
)

failures = []


def check(label, ok, detail=""):
    print("   %-58s %s%s" % (label, "ok" if ok else "FAILED",
                             ("   " + detail) if detail else ""))
    if not ok:
        failures.append(label)


def band(v):
    return "A" if v > 0.7 else ("B" if v >= 0.3 else "C")


def main():
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")
    a = pd.read_csv(ANCHOR)
    agg = aggregate_per_physical_sample(a)

    print("cohort size, computed from %s\n" % ANCHOR)
    print("   papers contributing Jc anchor rows   %4d" % a.paper_id.nunique())
    print("   physical samples after aggregation   %4d" % len(agg))
    print("   anchor rows                          %4d" % len(a))
    print("   distinct compounds                   %4d" % a.compound_formula.nunique())
    print("   substructure families                %4d" % a.substructure.nunique())
    print("   sample forms                         %4d   %s"
          % (a.sample_form.nunique(), ", ".join(sorted(a.sample_form.unique()))))

    print("\ndeposited table sizes\n")
    for f in sorted(glob.glob(os.path.join(DATA, "*.csv"))):
        print("   %-52s %6d" % (os.path.basename(f), sum(1 for _ in open(f)) - 1))

    print("\npre-registered classification, %s\n" % BANDS)
    vd = compute_variance_decomposition(agg)
    for _, r in vd[vd.scope == "per_substructure"].iterrows():
        if pd.isna(r.ratio_between_total):
            print("   %-24s %4d  single sample form, no decomposition"
                  % (r.substructure, r.n_papers))
        else:
            print("   %-24s %4d  ratio %.4f   outcome %s"
                  % (r.substructure, r.n_papers, r.ratio_between_total,
                     band(r.ratio_between_total)))
    ax = vd[vd.scope == "aggregate_all"].iloc[0]
    print("   %-24s %4d  ratio %.4f   pooled across families"
          % ("aggregate", ax.n_papers, ax.ratio_between_total))

    print("\nconsistency checks\n")

    dep = pd.read_csv(DERIVED)
    dx = dep[dep.scope == "aggregate_all"].iloc[0]
    check("derived decomposition reproduces from its own source",
          int(dx.n_papers) == int(ax.n_papers)
          and abs(dx.ratio_between_total - ax.ratio_between_total) < 1e-12,
          "file %d/%.6f vs recomputed %d/%.6f"
          % (dx.n_papers, dx.ratio_between_total, ax.n_papers, ax.ratio_between_total))

    dep_fams = set(dep[dep.scope == "per_substructure"].substructure)
    check("derived families match the source table's families",
          dep_fams == set(a.substructure.unique()),
          "only in derived: %s" % (dep_fams - set(a.substructure.unique()) or "none"))

    ok = np.allclose(a.Jc_anchor_A_per_cm2, 10 ** a.log10_Jc_anchor)
    check("Jc_anchor_A_per_cm2 equals 10^log10_Jc_anchor", ok)

    # A paper may legitimately contribute several samples of different forms, so
    # the conflict test is per (record, sample), not per record. Only one paper
    # in this cohort contributes two forms, and collapsing to the paper level
    # flagged it as a defect when it is the intended structure.
    seen = {}
    for f in glob.glob(os.path.join(DATA, "*.csv")):
        d = pd.read_csv(f, low_memory=False)
        if "sample_form" not in d.columns:
            continue
        key = next((c for c in ("paper_id", "arxiv_id", "identifier")
                    if c in d.columns), None)
        sid = next((c for c in ("sample_id", "sample_identifier")
                    if c in d.columns), None)
        if key is None:
            continue
        for _, r in d.iterrows():
            pid = str(r[key]).replace("elsevier_", "").replace("springer_", "")
            pid = pid.replace("_", "").replace("/", "").replace(".", "").lower()
            sample = str(r[sid]).strip().lower() if sid else ""
            seen.setdefault((pid, sample), set()).add(str(r.sample_form))
    conflicting = {k: v for k, v in seen.items()
                   if len({x for x in v if x != "nan"}) > 1}
    check("each sample carries one form across all tables",
          not conflicting, "conflicts: %s" % (list(conflicting)[:3] or "none"))

    placeholders = set()
    for f in glob.glob(os.path.join(DATA, "*.csv")):
        d = pd.read_csv(f, low_memory=False)
        if "sample_form" not in d.columns:
            continue
        for v in set(d.sample_form.dropna().astype(str)):
            if v.lower() in ("unknown", "not recorded", "unspecified", "n/a", "none"):
                # A placeholder is only a defect where the record actually feeds
                # the fitted cohort. Provenance rows for papers that contribute
                # no anchor is a legitimate "we never determined this".
                ids = d.loc[d.sample_form == v]
                key = next((c for c in ("paper_id", "arxiv_id", "identifier")
                            if c in d.columns), None)
                if key and any(a.paper_id.str.contains(str(i).split("/")[-1],
                                                       regex=False).any()
                               for i in ids[key]):
                    placeholders.add((os.path.basename(f), v))
    check("no placeholder sample_form on a record in the fitted cohort",
          not placeholders, "%s" % (sorted(placeholders) or "none"))

    check("no sample_form is the placeholder 'unknown'",
          "unknown" not in set(a.sample_form),
          "a form label must name a form, not the absence of one")

    prov = pd.read_csv(os.path.join(DATA, "provenance_table_fitcohort_full.csv"))
    bt = pd.read_csv(os.path.join(DATA, "phase_3_p44_post_UCLA_beta_T_fits.csv"))
    fh = pd.read_csv(os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv"))
    fh_ok = fh[fh.physicality == "ok"]
    p57 = pd.read_csv(os.path.join(DATA, "phase_3_p57_de_novo_predictions.csv"),
                      low_memory=False)
    tiers = pd.read_csv(os.path.join(
        DATA, "phase_3_p56_candidate_tier_assignment.csv"))
    computed = dict(
        papers_contributing_anchor_rows=a.paper_id.nunique(),
        physical_samples=len(agg),
        anchor_rows=len(a),
        fitted_curve_papers=prov.identifier.nunique(),
        fitted_curve_compounds=prov.compound.nunique(),
        extracted_points=int(pd.to_numeric(prov.n_Jc_points, errors="coerce").sum()),
        temperature_axis_fits=len(bt),
        field_axis_fits_ok=len(fh_ok),
        field_axis_ok_papers=fh_ok.arxiv_id.nunique(),
        candidate_compounds=p57.compound_formula.nunique(),
        dispatched_compounds=p57[p57.refusal_flag.fillna("") == ""].compound_formula.nunique(),
        dispatch_tuples=len(p57),
        emitted_targets=int((p57.refusal_flag.fillna("") == "").sum()),
        candidate_records=len(tiers),
        calibration_retained=int((tiers.tier != "refused_calibration_domain").sum()),
        calibration_refused=int((tiers.tier == "refused_calibration_domain").sum()),
        calibration_high_confidence=int((tiers.tier == "high_confidence").sum()),
        calibration_graded_confidence=int((tiers.tier == "graded_confidence").sum()),
    )
    for k, want in MANUSCRIPT.items():
        got = computed[k]
        check("manuscript %s" % k.replace("_", " "), got == want,
              "deposit %d, manuscript %d" % (got, want))

    withdrawn = os.path.join("audit", "withdrawn_records.csv")
    if os.path.exists(withdrawn):
        w = pd.read_csv(withdrawn)
        ids = set(w.identifier)
        present = [i for i in ids
                   if a.paper_id.str.contains(i.split("/")[-1], regex=False).any()]
        check("no withdrawn record survives in the anchor table",
              not present, "withdrawn: %s" % ", ".join(sorted(ids)))

    print()
    if failures:
        print("%d check(s) FAILED: %s" % (len(failures), "; ".join(failures)))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
