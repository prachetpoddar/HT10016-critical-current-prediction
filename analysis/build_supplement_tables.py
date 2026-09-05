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

Every row emitted here is read from the deposit and checked against every
withdrawal ledger in the repository before it is written, so a withdrawn
identifier cannot reappear. The selection rule for each table is stated in the
code rather than left to whoever last edited the document.

Three ledgers, not one. audit/withdrawn_records.csv holds the seven records
withdrawn before 2026-09-04. audit/jc_anchor_repairs.csv holds the anchor rows
withdrawn on 2026-09-05, 26 of 96, and the papers whose values were rescaled.
data/phase_3_form3_fits_partial_cohortB_v2_repaired.csv holds the field-axis
fits withdrawn in the same pass. An earlier version of this file consulted only
the first, and Table S4 went on printing six rows and Table S5 five rows drawn
from records the later two removed. Referee A was invited to check those tables
against the source figures, which is the check they fail.

The repaired tables are read where they exist, so the values printed are the
repaired ones. Table S4's four rows from jallcom.2013.04.183 move up a decade,
which is the correction that paper needed and never received.

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
ANCHOR_REP = ANCHOR.replace(".csv", "_repaired.csv")
FITS_H = os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_H_REP = FITS_H.replace(".csv", "_repaired.csv")
ANCHOR_LEDGER = os.path.join("audit", "jc_anchor_repairs.csv")
PROV = os.path.join(DATA, "provenance_table_fitcohort_full.csv")
PRED = os.path.join(DATA, "phase_3_p57_de_novo_predictions.csv")
WITHDRAWN = os.path.join("audit", "withdrawn_records.csv")

REFUSAL_PROSE = {
    "T_above_Tc": "T above Tc",
    "Hc2_unavailable": "Hc2 unavailable",
    "H_above_Hc2": "H above Hc2",
    "non_monotonic_Jc_T": "non-monotonic Jc(T)",
    "H_below_validated_reduced_field": "H below validated range",
    "family_fails_field_axis_validation": "family fails field axis",
    "T_above_validated_reduced_temperature": "T above validated range",
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


def add(out, i):
    out.add(str(i))
    out.add(short(str(i).replace("/", "_")))


def withdrawn_tokens():
    """Every identifier any ledger in the repository has withdrawn."""
    out = set()
    if os.path.exists(WITHDRAWN):
        for i in pd.read_csv(WITHDRAWN).identifier.astype(str):
            add(out, i)
    if os.path.exists(ANCHOR_LEDGER):
        led = pd.read_csv(ANCHOR_LEDGER)
        for i in led.loc[led.action == "withdrawn", "paper"].astype(str):
            # A row-level withdrawal names the paper and the sample form in
            # brackets. It removes one record, not a paper, so it is not a ban
            # token; the row is dropped by reading the repaired table. Banning
            # the paper here would have removed mtphys.2022.100783 from both
            # tables when only its polycrystal anchor was withdrawn.
            if " (" not in i:
                add(out, i)
    if os.path.exists(FITS_H_REP):
        fb = pd.read_csv(FITS_H_REP)
        for i in fb.loc[fb.withdrawn.fillna("") != "", "withdrawn"].astype(str):
            add(out, i)
    return out


# The rule these tables follow, stated once. A paper withdrawn by any ledger is
# excluded from every worked-example table, not only from the table whose
# quantity the withdrawal names. The ledgers are not interchangeable in what
# they remove: jpcs.2026.113652 lost its anchors because its recorded currents
# are not the printed ones in any unit, and physc.2009.05.098 kept its anchors
# under a unit correction while losing its field-axis fits because its critical
# scale does not follow the axis. But a worked example exists so that a referee
# can open the source and check it, and a paper under any withdrawal is not a
# record that check can be asked of. The conservative rule is the honest one
# here, and it costs five rows.


def drop_banned(df, col, banned):
    """Remove every row whose source identifier any ledger has withdrawn.

    The selection rules pick rows, and asserting afterwards that none is banned
    only turns a bad pick into an abort. Filtering first lets the rule choose
    the next eligible record instead, which is what a worked-example table
    needs. assert_clean stays as the backstop.
    """
    ids = df[col].astype(str)
    keep = ~ids.apply(lambda x: any(b and b in x for b in banned))
    return df[keep].copy()


def anchors(banned=()):
    """The repaired anchor table with withdrawn rows dropped, if it exists."""
    if os.path.exists(ANCHOR_REP):
        a = pd.read_csv(ANCHOR_REP)
        a = a[a.withdrawn.fillna("") == ""].copy()
    else:
        a = pd.read_csv(ANCHOR)
    return drop_banned(a, "paper_id", banned)


def field_fits(banned=()):
    """The repaired field-axis fits with withdrawn papers dropped."""
    if os.path.exists(FITS_H_REP):
        f = pd.read_csv(FITS_H_REP)
        f = f[f.withdrawn.fillna("") == ""].copy()
        for src, dst in [("beta_repaired", "beta"),
                         ("Hc2_repaired", "Hc2_T_used"),
                         ("range_repaired", "H_axis_range_normalized")]:
            if src in f.columns:
                f[dst] = f[src].where(f[src].notna(), f[dst])
    else:
        f = pd.read_csv(FITS_H)
    return drop_banned(f, "arxiv_id", banned)


def assert_clean(rows, col, banned, table):
    bad = [r[col] for r in rows
           if any(b and b in str(r[col]) for b in banned)]
    if bad:
        sys.exit("%s would show withdrawn records: %s" % (table, sorted(set(bad))))


def table_s4(banned):
    """Anchor excerpt: the PDF-verified record, then every paper contributing
    more than one sample form or more than one specimen, which is what the
    table is for."""
    a = anchors(banned)
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
    f = field_fits(banned)
    # One fit per source paper, so the excerpt shows six papers rather than one
    # paper six times.
    ok = (f[f.physicality == "ok"].sort_values("SE_beta")
          .drop_duplicates("arxiv_id").head(3))
    b = f[f.physicality == "H_axis_applicability_bound"].copy()
    # Three narrowest spans, which are the ceiling cases, plus the one fit whose
    # resolved scale sits furthest below its literature value. That last row is
    # the scale-resolution failure Sec. III.F quantifies, and picking on span
    # alone drops it: the three narrowest are all cuprates sitting at the
    # regression ceiling, which shows the filter firing but not why a resolved
    # scale can be wrong. Selecting it by rule rather than by hand is the point
    # of this file.
    b["scale_shortfall"] = b.Hc2_T_default / b.Hc2_T_used
    worst = b.sort_values("scale_shortfall", ascending=False).head(1)
    bound = (b.sort_values("H_axis_range_normalized")
             .drop_duplicates("arxiv_id").head(3))
    bound = pd.concat([bound, worst]).drop_duplicates(subset=["arxiv_id",
                                                              "sample_identifier"])
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


def table_s1(_banned):
    """Provenance summary by substructure family, generated from the deposit.

    Hand-maintained until now, and it showed: it still carried an "Iron other"
    row for the two compounds since reclassified into their families, and stale
    counts for the two families that received them, while its TOTAL row summed
    correctly and so hid the fact.

    The critical-field column is also renamed. It read "Paper-reported Hc2" and
    counted every paper whose provenance string is not the substructure
    literature catalog, which sweeps 13 Tier-3 literature defaults and 9 Tier-2
    per-substructure ratios in under a heading that claims the paper reported
    the value. Only 12 of the 65 papers carry a Tier-1 anchor read from the
    source, and that is what the column now counts.
    """
    p = pd.read_csv(PROV)
    # The provenance table keeps every row it ever had, including the eleven
    # papers withdrawn on 2026-09-03 and one duplicate identifier, and carries
    # the disposition in a column instead of deleting them. Summing without
    # reading that column reproduces the pre-withdrawal census, which is what
    # this table did: 62 papers, 38 compounds and 4146 points against Table I's
    # corrected 50, 35 and 3303. The two tables are in the same document.
    if "contributes" in p.columns:
        before = (p.identifier.nunique(), p.compound.nunique(),
                  int(pd.to_numeric(p.n_Jc_points, errors="coerce").sum()))
        p = p[~p.contributes.astype(str).str.startswith("none, withdrawn")]
        # The duplicate row is a second identifier for a paper already counted,
        # so it is excluded from the paper count and kept in the compound and
        # point counts, which is the rule apply_provenance_status.py states and
        # the rule Table I's 35 compounds and 3303 points follow. Dropping it
        # outright gave 34 and 2947 and would have put Table S1 at odds with
        # Table I by one compound and 356 points.
        dup = p.contributes.astype(str).str.startswith("the same paper as")
        after = (int(p.loc[~dup, "identifier"].nunique()),
                 int(p.compound.nunique()),
                 int(pd.to_numeric(p.n_Jc_points, errors="coerce").sum()))
        print("   Table S1 cohort: %d papers, %d compounds, %d points; before "
              "the withdrawals %d, %d, %d" % (after + before))
        p = p.copy()
        p["counts_as_paper"] = ~dup
    rows, order = [], sorted(p.substructure_family.unique())
    for fam in order:
        g = p[p.substructure_family == fam]
        rows.append(dict(
            family=fam.replace("_", " ").replace("conventional AlB2", "MgB2-class"),
            papers=int(g.loc[g.get("counts_as_paper", True), "identifier"]
                       .nunique()) if "counts_as_paper" in g
            else g.identifier.nunique(),
            fully_fittable=int((g.contribution_flag == "fully fittable").sum()),
            cohort_a_only=int(g.contribution_flag.str.startswith("Cohort A only").sum()),
            cohort_b_only=int(g.contribution_flag.str.startswith("Cohort B only").sum()),
            cohort_ab_nonfittable=int(g.contribution_flag.str.startswith("Cohort A and B").sum()),
            compounds=g.compound.nunique(),
            tier1_hc2=int(g.Hc2_provenance.str.startswith("Tier_1").sum()),
            points=int(pd.to_numeric(g.n_Jc_points, errors="coerce").sum())))
    rows.append(dict(family="TOTAL",
                     papers=int(p.loc[p.get("counts_as_paper", True),
                                      "identifier"].nunique())
                     if "counts_as_paper" in p else p.identifier.nunique(),
                     fully_fittable=int((p.contribution_flag == "fully fittable").sum()),
                     cohort_a_only=int(p.contribution_flag.str.startswith("Cohort A only").sum()),
                     cohort_b_only=int(p.contribution_flag.str.startswith("Cohort B only").sum()),
                     cohort_ab_nonfittable=int(p.contribution_flag.str.startswith("Cohort A and B").sum()),
                     compounds=p.compound.nunique(),
                     tier1_hc2=int(p.Hc2_provenance.str.startswith("Tier_1").sum()),
                     points=int(pd.to_numeric(p.n_Jc_points, errors="coerce").sum())))
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
        # A refusal acts on a prediction target, not on a candidate, so a row
        # can carry a reason code for the field axis and still carry the
        # temperature-axis value the remaining gates allow: 321 of the 540
        # Hc2-unavailable rows do. An earlier version of this generator printed
        # "none" for every refused row, so the worked example contradicted both
        # the file it excerpts and the paragraph introducing it. The value is
        # now shown whenever the file carries one.
        has = pd.notna(r.predicted_log_Jc)
        has_ci = pd.notna(r.predicted_log_Jc_lower_95) and pd.notna(
            r.predicted_log_Jc_upper_95)
        rows.append(dict(
            candidate=r.compound_formula,
            anchors="%.1f K / %s" % (r.Tc_anchor_K,
                                     "none" if pd.isna(r.Hc2_T_anchor)
                                     else "%.1f T" % r.Hc2_T_anchor),
            scope=r.predictor_method_scope.replace(
                "sample_form_conditional_median:", "Stage 2, ").replace(
                "substructure_aggregate_median", "Stage 3, aggregate")
            .replace("_", " "),
            t="%.1f" % r.T_K, h="%.1f" % r.H_T,
            log_jc="%.3f" % r.predicted_log_Jc if has else "none",
            interval=("%.3f to %.3f" % (r.predicted_log_Jc_lower_95,
                                        r.predicted_log_Jc_upper_95))
            if has_ci else "none",
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
    out = {"S1": table_s1(banned), "S4": table_s4(banned),
           "S5": table_s5(banned), "S6": table_s6(banned)}
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
