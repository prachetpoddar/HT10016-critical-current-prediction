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
import io
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
# What the manuscript actually prints, read out of the manuscript by
# analysis/read_manuscript_counts.py and deposited with its provenance in
# audit/manuscript_printed_counts.csv.
#
# This replaces a hand-written dictionary that described itself as the
# manuscript's counts and was not. Every value in it equalled what the deposit
# held on the day it was written, so the check compared the deposit with a
# snapshot of the deposit. Table I of HT10016_revised.docx prints 69, 43, 4387,
# 419, 95, 110 and 185 where that dictionary held 65, 40, 4247, 414, 88, 105
# and 183, so nine mismatches were being reported at the wrong sizes and one
# quantity, candidate compounds, was reported as agreeing when it does not.
#
# Counts still typed here are ones not yet located in the manuscript text. They
# are marked, and locating them is outstanding work rather than a passing check.
MANUSCRIPT_CSV = os.path.join("audit", "manuscript_printed_counts.csv")
# These are not printed anywhere in the manuscript or the supplement. Both were
# searched for the phrases that would carry them and neither appears, so there
# is nothing in the text to agree or disagree with. They are checked against the
# deposit's own current values so that a future cohort change still moves them
# visibly, and they are labelled as not printed rather than as verified.
MANUSCRIPT_NOT_PRINTED = dict(
    papers_contributing_anchor_rows=32,
    physical_samples=60,
)
MANUSCRIPT_NOT_YET_LOCATED = dict(
    # Moved by analysis/apply_temperature_window_gate.py, which refused the
    # 93 targets sitting at reduced temperature 0.7 or above.
    dispatched_compounds=84,
    dispatch_tuples=2097,
    emitted_targets=163,
    candidate_records=233,
    calibration_retained=212,
    calibration_refused=21,
    calibration_high_confidence=82,
    calibration_graded_confidence=130,
)


def _load_manuscript_counts():
    """Read the manuscript's printed counts, and refuse to run without them.

    A missing file is not a reason to fall back on typed values: that is how the
    previous version came to assert numbers nobody had read out of the paper.
    """
    if not os.path.exists(MANUSCRIPT_CSV):
        raise SystemExit(
            "%s is missing. Run analysis/read_manuscript_counts.py against the "
            "manuscript before verifying the deposit against it." % MANUSCRIPT_CSV)
    import csv as _csv
    out, where = {}, {}
    with open(MANUSCRIPT_CSV, newline="") as fh:
        for r in _csv.DictReader(fh):
            out[r["quantity"]] = int(r["value"])
            where[r["quantity"]] = "%s, %s" % (r["document"], r["located_in"])
    for k, v in MANUSCRIPT_NOT_YET_LOCATED.items():
        out.setdefault(k, v)
        where.setdefault(k, "NOT YET LOCATED in the manuscript")
    for k, v in MANUSCRIPT_NOT_PRINTED.items():
        out.setdefault(k, v)
        where.setdefault(k, "NOT PRINTED in the manuscript; pinned to the deposit")
    return out, where


MANUSCRIPT, MANUSCRIPT_SOURCE = _load_manuscript_counts()


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

    # The manuscript's fitted-curve counts are computed from this table, and
    # the table still holds the eleven papers withdrawn on 2026-09-03, because
    # withdrawing a paper never removed its provenance row. The counts below
    # are therefore pre-withdrawal, and the manuscript needs editing. This is
    # reported on every run rather than left for someone to notice.
    if "status" in prov.columns:
        con = prov[prov.status == "contributing"]
        dupn = int(con.get("second_identifier_for_the_same_paper",
                           pd.Series(dtype=bool)).sum())
        pts = int(pd.to_numeric(con.n_Jc_points, errors="coerce").sum())
        print()
        print("   OUTSTANDING MANUSCRIPT EDITS, from the withdrawals")
        print("   %-28s %10s %10s" % ("quantity", "printed", "correct"))
        print("   %-28s %10d %10d" % ("fitted curve papers",
                                      prov.identifier.nunique(),
                                      len(con) - dupn))
        print("   %-28s %10d %10d" % ("fitted curve compounds",
                                      prov.compound.nunique(),
                                      con.compound.nunique()))
        print("   %-28s %10d %10d" % ("extracted points",
                                      int(pd.to_numeric(prov.n_Jc_points,
                                                        errors="coerce").sum()),
                                      pts))
        print("   the checks below still compare the deposit as published "
              "against the manuscript as written, so they pass; the table "
              "above is what has to change in both.")
        print()
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
        src = MANUSCRIPT_SOURCE.get(k, "")
        # A count nobody has found in the manuscript is not verified by matching
        # it, so say so on the line rather than printing a bare ok.
        if src.startswith("HT10016"):
            note = ""
        elif src.startswith("NOT PRINTED"):
            note = "  [not printed in the manuscript]"
        else:
            note = "  [value not located in the manuscript]"
        check("manuscript %s" % k.replace("_", " "), got == want,
              "deposit %d, manuscript %d%s" % (got, want, note))

    # The upper critical field is the other quantity carried in more than one
    # deposited table, and nothing here checked it until
    # analysis/audit_hc2_tables.py was written. It is run as a single line so
    # that a cross-table inconsistency in Hc2 or Tc cannot pass unnoticed
    # simply because this script never looked.
    import subprocess
    r = subprocess.run([sys.executable,
                        os.path.join("analysis", "audit_hc2_tables.py")],
                       capture_output=True, text=True)
    bad = [ln.strip() for ln in r.stdout.splitlines() if "FAILED" in ln
           and "check(s)" not in ln]
    check("Hc2 and Tc are consistent across the deposited tables",
          r.returncode == 0,
          "run analysis/audit_hc2_tables.py: " + "; ".join(
              b.split("FAILED")[0].strip() for b in bad) if bad else "")

    # The paper-clustered permutation table is a derived artifact of the anchor
    # cohort, and nothing read it. It was still describing the pre-withdrawal
    # cohort, 69 samples against 60, with the 122 family at n=16 and eta^2
    # 0.5988 against 9 and 0.3452. That is the exact failure this script exists
    # to catch, a withdrawal applied to the source and not to what derives from
    # it, so the sample counts are now checked against the live cohort.
    perm = os.path.join("audit", "permutation_paper_clustered.csv")
    if os.path.exists(perm):
        pt = pd.read_csv(perm).set_index("scope")
        live = {"aggregate": len(agg)}
        for sub, g in agg.groupby("substructure"):
            live[sub] = len(g)
        drift = {k: (int(pt.loc[k, "n"]), v) for k, v in live.items()
                 if k in pt.index and int(pt.loc[k, "n"]) != v}
        check("the permutation table describes the current cohort",
              not drift,
              "; ".join("%s table %d vs cohort %d" % (k, a_, b)
                        for k, (a_, b) in drift.items())
              or "run analysis/permutation_test.py")

    withdrawn = os.path.join("audit", "withdrawn_records.csv")
    if os.path.exists(withdrawn):
        w = pd.read_csv(withdrawn)
        ids = set(w.identifier)
        present = [i for i in ids
                   if a.paper_id.str.contains(i.split("/")[-1], regex=False).any()]
        check("no withdrawn record survives in the anchor table",
              not present, "withdrawn: %s" % ", ".join(sorted(ids)))

    # The tier table and the prediction file must agree on which candidates
    # emit. They are the same question asked of two files, and only one of them
    # was regenerated when the field-window and temperature-window gates were
    # applied: the tier table still marks 123 compounds as emitting across three
    # families, while the prediction file emits 84, all of them MgB2-class, and
    # the 84 are a strict subset of the 123. Table IV's caption in the
    # manuscript carries the tier table's number while its body carries the
    # prediction file's, so the two disagree inside one table. This is the
    # failure this script was written for, a gate applied to one derived table
    # and not to the other, and nothing here was asking the question.
    tier_p = os.path.join("data", "phase_3_p56_candidate_tier_assignment.csv")
    pred_p = os.path.join("data", "phase_3_p57_de_novo_predictions.csv")
    if os.path.exists(tier_p) and os.path.exists(pred_p):
        tt = pd.read_csv(tier_p)
        pp = pd.read_csv(pred_p)
        t_em = set(tt.loc[tt.emits_predictions.astype(str).str.lower()
                          .isin(["yes", "true", "1"]), "compound"])
        p_em = set(pp.loc[pp.refusal_flag.isna(), "compound_formula"])
        check("the tier table and the prediction file agree on who emits",
              t_em == p_em,
              "tier table %d compounds, prediction file %d, %d marked emitting "
              "that emit nothing, %d emitting that the tier table does not mark"
              % (len(t_em), len(p_em), len(t_em - p_em), len(p_em - t_em))
              + ("; regenerate analysis/phase_3_p56_de_novo_candidate_list.py"
                 if t_em != p_em else ""))

    # Every deposited script must at least parse. This is the cheapest check in
    # the file and it went missing until analysis/phase_3_p39_multi_stage_predictor.py
    # shipped with a string replacement that had cut into a literal at both
    # ends, leaving DESCRIPTOR = "max_ch on one side and sified" on the other.
    # It was pushed and sat on the remote, because a script nobody ran that
    # revision is a script nobody found out was broken, and none of the four
    # check_* scripts import it. A SyntaxError is not a subtle defect and it
    # should not need a reader to hit it.
    import ast
    import glob as _glob
    broken = []
    for f in sorted(_glob.glob(os.path.join("analysis", "*.py"))):
        try:
            ast.parse(io.open(f, encoding="utf-8").read(), filename=f)
        except SyntaxError as e:
            broken.append("%s line %s: %s" % (os.path.basename(f), e.lineno, e.msg))
    check("every deposited script parses", not broken,
          "; ".join(broken) or "%d file(s)"
          % len(_glob.glob(os.path.join("analysis", "*.py"))))

    print()
    if failures:
        print("%d check(s) FAILED: %s" % (len(failures), "; ".join(failures)))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
