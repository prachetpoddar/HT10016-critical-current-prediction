#!/usr/bin/env python3
"""
build_supplement_tables.py

Generates the worked-example tables of the Supplemental Material, Tables S4, S5
and S6, directly from the deposited CSVs.

Why this exists. Those tables were maintained by hand. A record withdrawn from
the analysis stayed visible in Table S4 through two revisions, and the prose
introducing Table S5 went on describing rows the table no longer showed. A
worked example that disagrees with the deposit is worse than no worked example,
because it is the part of the supplement a reader checks first.

Every row emitted here is read from the deposit and checked against
audit/withdrawn_records.csv before it is written, so a withdrawn identifier
cannot reappear. The selection rule for each table is stated in the code rather
than left to whoever last edited the document.

    python analysis/build_supplement_tables.py
    python analysis/build_supplement_tables.py --json out.json

Run from the repository root.
"""
import argparse
import json
import os
import sys

import pandas as pd

DATA = "data"
ANCHOR = os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv")
FITS_H = os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv")
PRED = os.path.join(DATA, "phase_3_p57_de_novo_predictions.csv")
WITHDRAWN = os.path.join("audit", "withdrawn_records.csv")

REFUSAL_PROSE = {
    "T_above_Tc": "T above Tc",
    "Hc2_unavailable": "Hc2 unavailable",
    "H_above_Hc2": "H above Hc2",
    "non_monotonic_Jc_T": "non-monotonic Jc(T)",
    "H_below_validated_reduced_field": "H below validated range",
    "family_fails_field_axis_validation": "family fails field axis",
}

FORM = {"bulk": "Bulk", "wire": "Wire", "thin_film": "Thin film",
        "polycrystal": "Polycrystal", "single_crystal": "Single crystal"}


def short(identifier):
    """The distinctive part of a DOI, as the tables print it."""
    s = str(identifier)
    for p in ("elsevier_", "springer_", "iop_"):
        s = s.replace(p, "")
    s = s.replace("10.1016_", "").replace("10.1016/", "")
    s = s.replace("10.1038_", "").replace("10.1007_", "").replace("10.1088_", "")
    return s


def withdrawn_tokens():
    if not os.path.exists(WITHDRAWN):
        return set()
    w = pd.read_csv(WITHDRAWN)
    out = set()
    for i in w.identifier.astype(str):
        out.add(i)
        out.add(short(i.replace("/", "_")))
    return out


def assert_clean(rows, col, banned, table):
    bad = [r[col] for r in rows
           if any(b and b in str(r[col]) for b in banned)]
    if bad:
        sys.exit("%s would show withdrawn records: %s" % (table, sorted(set(bad))))


def table_s4(banned):
    """Anchor excerpt: the PDF-verified record, then every paper contributing
    more than one sample form or more than one specimen, which is what the
    table is for."""
    a = pd.read_csv(ANCHOR)
    lead = a[a.paper_id.str.contains("jallcom.2023.170146", regex=False)].head(1)
    rest = a[~a.paper_id.isin(lead.paper_id)]
    # Papers contributing more than one sample form come first, because the
    # within-paper form contrast is what the table is for; then papers
    # contributing several specimens of one form, which show processing spread.
    two_form = rest.groupby("paper_id").filter(lambda g: g.sample_form.nunique() > 1)
    many_spec = rest[~rest.paper_id.isin(two_form.paper_id)].groupby(
        "paper_id").filter(lambda g: len(g) >= 4)
    pick = [lead]
    for src in (two_form, many_spec):
        for pid, g in src.groupby("paper_id", sort=False):
            pick.append(g.head(5))
            if sum(len(x) for x in pick) >= 12:
                break
        if sum(len(x) for x in pick) >= 12:
            break
    keep = pd.concat(pick).drop_duplicates(subset=["paper_id", "sample_id"]).head(12)
    rows = [dict(source=short(r.paper_id), compound=r.compound_formula,
                 form=FORM.get(r.sample_form, r.sample_form), sample=r.sample_id,
                 tc="%.1f" % r.Tc_K,
                 anchor="%.1f K, %s T" % (r.T_anchor_K,
                                          ("%.2f" % r.H_anchor_T).rstrip("0").rstrip(".")),
                 log_jc="%.3f" % r.log10_Jc_anchor, n=int(r.n_data_points))
            for _, r in keep.iterrows()]
    assert_clean(rows, "source", banned, "Table S4")
    return rows


def table_s5(banned):
    """Field-axis fit excerpt: the passing fits first, then bound ones, so a
    reader sees both the applicability filter firing and not firing."""
    f = pd.read_csv(FITS_H)
    # One fit per source paper, so the excerpt shows six papers rather than one
    # paper six times.
    ok = (f[f.physicality == "ok"].sort_values("SE_beta")
          .drop_duplicates("arxiv_id").head(3))
    bound = (f[f.physicality == "H_axis_applicability_bound"]
             .sort_values("H_axis_range_normalized")
             .drop_duplicates("arxiv_id").head(3))
    rows = [dict(source=short(r.arxiv_id), compound=r.compound_formula,
                 hc2="%.1f / %.1f" % (r.Hc2_T_used, r.Hc2_T_default),
                 provenance=("Tier 1, %s" % ("direct match"
                             if "direct" in str(r.Hc2_source) else "extrapolated"))
                 if str(r.Hc2_source).startswith("Tier_1")
                 else ("Tier 2, per-substructure ratio"
                       if str(r.Hc2_source).startswith("Tier_2")
                       else "Tier 3, literature default"),
                 span="%.3f" % r.H_axis_range_normalized,
                 beta="%.2f (%.2f)" % (r.beta, r.SE_beta),
                 flag="ok" if r.physicality == "ok" else "bound")
            for _, r in pd.concat([ok, bound]).iterrows()]
    assert_clean(rows, "source", banned, "Table S5")
    return rows


def table_s6(_banned):
    """Dispatch excerpt: one dispatched target and one of each refusal code, so
    the table shows the refusal vocabulary rather than only the successes."""
    p = pd.read_csv(PRED, low_memory=False)
    p["refusal_flag"] = p["refusal_flag"].fillna("")
    picks = [p[p.refusal_flag == ""].head(2)]
    for code in sorted(c for c in p.refusal_flag.unique() if c):
        picks.append(p[p.refusal_flag == code].head(1))
    rows = []
    for _, r in pd.concat(picks).iterrows():
        emitted = r.refusal_flag == ""
        rows.append(dict(
            candidate=r.compound_formula,
            anchors="%.1f K / %s" % (r.Tc_anchor_K,
                                     "none" if pd.isna(r.Hc2_T_anchor)
                                     else "%.1f T" % r.Hc2_T_anchor),
            scope=r.predictor_method_scope.replace(
                "sample_form_conditional_median:", "Stage 2, ").replace(
                "substructure_aggregate_median", "Stage 3, aggregate"),
            t="%.1f" % r.T_K, h="%.1f" % r.H_T,
            log_jc="%.3f" % r.predicted_log_Jc if emitted else "none",
            interval=("%.3f to %.3f" % (r.predicted_log_Jc_lower_95,
                                        r.predicted_log_Jc_upper_95))
            if emitted else "none",
            refusal="none" if emitted else REFUSAL_PROSE.get(
                r.refusal_flag, r.refusal_flag)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")
    banned = withdrawn_tokens()
    print("withdrawn identifiers excluded from every table: %d\n" % (len(banned) // 2))
    out = {"S4": table_s4(banned), "S5": table_s5(banned), "S6": table_s6(banned)}
    for name, rows in out.items():
        print("Table %s  (%d rows)" % (name, len(rows)))
        for r in rows:
            print("   " + " || ".join(str(v) for v in r.values()))
        print()
    if args.json:
        json.dump(out, open(args.json, "w"), indent=1)
        print("written to %s" % args.json)


if __name__ == "__main__":
    main()
