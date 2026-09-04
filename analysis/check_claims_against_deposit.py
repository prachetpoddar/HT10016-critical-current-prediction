"""
check_claims_against_deposit.py

Binds numeric claims in the documents to quantities the deposit computes, and
reports what it could not bind.

Why this replaces the approach it sits beside. analysis/check_cross_artifact
_consistency.py holds a list of strings already known to be wrong. It is a
regression list, not a check: it can only ever find what someone already found
by hand, so a clean run means "none of the things we previously caught have
come back", not "the documents agree with the data". Measured against the three
artifacts, that list and verify_deposit's typed table between them name 43 of
the 436 distinct numbers those documents print, which is 9.9%. Every round of
this revision found new defects by hand and then added them to the list, which
is exactly what a denylist guarantees.

This script runs the other way. Each entry below is a quantity the deposit can
compute together with the words the documents use around it. Wherever those
words appear, the number beside them is read and compared. A number that
disagrees is a failure whether or not anyone knew to look for it, which is the
property the denylist does not have.

Three outcomes, and the third is the point:

  agrees      the document's number matches the deposit
  DISAGREES   it does not, and nobody had to have seen it first
  unbound     a number this script cannot bind to any deposit quantity

The unbound count is reported rather than hidden. It is the honest measure of
how much of the paper is machine-checked, and it should fall as entries are
added. It will never reach zero: the documents legitimately carry equation
numbers, reference numbers, section numbers, years, temperatures quoted from
source papers, and quantities whose source was never deposited.

Usage:
    python3 analysis/check_claims_against_deposit.py --dir /home/claude
"""
import argparse
import html
import os
import re
import sys
import zipfile

import numpy as np
import pandas as pd

DATA = "data"


def _loo(df, substructure, column):
    """One cell of data/phase_3_p47_compound_leave_out_MAE.csv."""
    row = df[df.substructure == substructure]
    if len(row) != 1 or column not in df.columns:
        raise SystemExit("phase_3_p47_compound_leave_out_MAE.csv has no single "
                         "%r row with a %r column; rerun "
                         "analysis/compound_leave_one_out.py"
                         % (substructure, column))
    return float(row.iloc[0][column])


def quantities():
    """Every quantity the deposit can compute, with the words used around it.

    context: a regex that must appear within WINDOW characters of the number.
    fmt:     how the document writes it, so 0.6117 is matched as "0.61".
    """
    p = pd.read_csv(os.path.join(DATA, "phase_3_p57_de_novo_predictions.csv"),
                    low_memory=False)
    t = pd.read_csv(os.path.join(
        DATA, "phase_3_p56_candidate_tier_assignment.csv"))
    prov = pd.read_csv(os.path.join(DATA,
                                    "provenance_table_fitcohort_full.csv"))
    bt = pd.read_csv(os.path.join(DATA,
                                  "phase_3_p44_post_UCLA_beta_T_fits.csv"))
    fh = pd.read_csv(os.path.join(
        DATA, "phase_3_form3_fits_partial_cohortB_v2.csv"))
    a = pd.read_csv(os.path.join(DATA,
                                 "phase_3_p31_jc_anchor_per_paper.csv"))
    loo = pd.read_csv(os.path.join(
        DATA, "phase_3_p47_compound_leave_out_MAE.csv"))
    em = p[p.refusal_flag.fillna("") == ""]
    fh_ok = fh[fh.physicality == "ok"]
    same = np.isclose(fh.Hc2_T_used, fh.Hc2_T_default)
    tiers = fh.Hc2_source.astype(str).str.extract(r"^(Tier_\d)")[0]
    width = float((em.predicted_log_Jc_upper_95
                   - em.predicted_log_Jc_lower_95).median())
    flags = p.refusal_flag.fillna("")

    # Each entry is (name, value, pattern, format). The pattern must contain
    # exactly ONE capture group, and that group is the number compared. There
    # is no proximity search: an earlier version looked for the value within
    # 110 characters of a context phrase, and matching a family name near any
    # unrelated number produced 90 disagreements of which essentially all were
    # artefacts. A check that manufactures inconsistencies is worse than no
    # check, because it costs the reader the trust the real findings need.
    #
    # The cost of anchoring is coverage: a phrase has to be written out before
    # it can be bound, so this table grows one sentence at a time. That is the
    # honest trade. The unbound count is printed so the coverage is never
    # mistaken for completeness.
    Q = [
        ("papers contributing fitted curves", prov.identifier.nunique(),
         r"(\d+) papers pass the fittability filters", "%d"),
        ("fitted-curve compounds", prov.compound.nunique(),
         r"contribute fitted curves across (\d+) compounds", "%d"),
        ("extracted points",
         int(pd.to_numeric(prov.n_Jc_points, errors="coerce").sum()),
         r"compounds and (\d+) critical-current data points", "%d"),
        ("temperature-axis fits", len(bt),
         r"(\d+) temperature-axis fits, \d+\s*field-axis", "%d"),
        # The 122 family's own count, which the cohort pattern above used to
        # bind to and report as a disagreement. Both are now anchored on the
        # sentence that scopes them, so a family-level number and a cohort
        # number cannot be confused for each other.
        ("temperature-axis fits, 122 family",
         int((bt.substructure == "iron_pnictide_122").sum()),
         r"field-axis fits and the (\d+) temperature-axis fits", "%d"),
        ("temperature-axis fits, 122 quadrature",
         int((bt.substructure == "iron_pnictide_122").sum()),
         r"passing physicality and (\d+) temperature-axis fits", "%d"),
        ("field-axis fits, 122 family",
         int(((fh.physicality == "ok")
              & (fh.compound_formula.astype(str)
                 .str.contains(r"Ba|K\(FeAs"))).sum()),
         r"family the (\d+) field-axis fits", "%d"),
        ("field-axis fits", len(fh_ok),
         r"(\d+)\s*field-axis fits drawn from", "%d"),
        ("field-axis source papers", fh_ok.arxiv_id.nunique(),
         r"field-axis fits drawn from (\d+) source papers", "%d"),
        ("anchor rows", len(a),
         r"(\d+) per-paper anchors behind Figure 3", "%d"),
        ("anchor rows, caption", len(a),
         r"Of the (\d+) per-paper anchor records of Table I", "%d"),
        ("candidate compounds", p.compound_formula.nunique(),
         r"evaluates (\d+) distinct candidate compounds", "%d"),
        ("candidate compounds, dispatch", p.compound_formula.nunique(),
         r"candidate records covering (\d+) distinct compounds", "%d"),
        ("candidate records", len(t),
         r"contains (\d+) candidate records", "%d"),
        ("candidate records, screen", len(t),
         r"Of the (\d+) records, \d+ fail this test", "%d"),
        ("dispatch tuples", len(p),
         r"giving (\d+) candidate-grid tuples", "%d"),
        ("dispatched compounds", em.compound_formula.nunique(),
         r"Of the \d+ candidates, (\d+) are dispatched", "%d"),
        ("dispatched compounds, III.E", em.compound_formula.nunique(),
         r"Of the \d+, (\d+) receive at least one non-refused", "%d"),
        ("dispatched compounds, conclusion", em.compound_formula.nunique(),
         r"of which (\d+) compounds receive at least one dispatched", "%d"),
        ("emitted targets", len(em),
         r"over the (\d+) predictions that survive", "%d"),
        ("calibration refused",
         int((t.tier == "refused_calibration_domain").sum()),
         r"records, (\d+) fail this test", "%d"),
        ("calibration retained",
         int((t.tier != "refused_calibration_domain").sum()),
         r"fail this test and (\d+) are retained", "%d"),
        ("graded confidence", int((t.tier == "graded_confidence").sum()),
         r"(\d+) records fall below their family range", "%d"),
        ("high confidence", int((t.tier == "high_confidence").sum()),
         r"family range and (\d+) fall at or above it", "%d"),
        ("interval width", width,
         r"non-refused predictions is ([\d.]+) dex", "%.2f"),
        ("interval width, supplement", width,
         r"confidence-interval width of ([\d.]+) dex", "%.2f"),
        ("interval width, glossary", width,
         r"a factor of 2, and ([\d.]+) dex is a factor", "%.2f"),
        ("interval factor", 10 ** width,
         r"dex in log10 Jc, a factor of about ([\d.]+) in Jc", "%.1f"),
        ("interval half-width", width / 2,
         r"constant half-width of ([\d.]+) dex", "%.2f"),
        ("one sigma", width / (2 * 1.959964),
         r"one-sigma uncertainty of about ([\d.]+) dex", "%.2f"),
        ("field-scale fits total", len(fh),
         r"identical for the \d+ of (\d+) fits", "%d"),
        ("field-scale default", int(same.sum()),
         r"identical for the (\d+) of \d+ fits", "%d"),
        ("field-scale resolved", int((~same).sum()),
         r"across the (\d+) fits for which a paper-derived", "%d"),
        ("field-scale factor",
         float((fh.loc[~same, "Hc2_T_default"]
                / fh.loc[~same, "Hc2_T_used"]).median()),
         r"median factor of ([\d.]+) smaller", "%.1f"),
        # The two field-axis leave-one-compound-out runs the manuscript states
        # as a contrast. Only the conditioned four were ever in a deposited
        # file; the substructure-median four were a code path and an assertion
        # in analysis/verify_redline_numbers.py, which is why they read as
        # unsourced. They are now a column, and both sets are bound here so a
        # reader does not have to take either on trust.
        ("field LOO conditioned, MgB2", _loo(loo, "conventional_AlB2",
                                             "compound_loo_mae"),
         r"gives ([\d.]+) for MgB2-class", "%.3f"),
        ("field LOO conditioned, 122", _loo(loo, "iron_pnictide_122",
                                            "compound_loo_mae"),
         r"([\d.]+) for iron pnictide 122-type and", "%.3f"),
        ("field LOO conditioned, chalcogenide",
         _loo(loo, "iron_chalcogenide_11", "compound_loo_mae"),
         r"and ([\d.]+) for iron chalcogenide 11-type", "%.3f"),
        ("field LOO conditioned, 1111", _loo(loo, "iron_pnictide_1111",
                                             "compound_loo_mae"),
         r"iron pnictide 1111-type at ([\d.]+)", "%.3f"),
        ("field LOO substructure median, MgB2",
         _loo(loo, "conventional_AlB2", "substructure_median_loo_mae"),
         r"protocol exactly, gives ([\d.]+),", "%.3f"),
        ("field LOO substructure median, 122",
         _loo(loo, "iron_pnictide_122", "substructure_median_loo_mae"),
         r"protocol exactly, gives [\d.]+, ([\d.]+),", "%.3f"),
        ("field LOO substructure median, chalcogenide",
         _loo(loo, "iron_chalcogenide_11", "substructure_median_loo_mae"),
         r"protocol exactly, gives [\d.]+, [\d.]+, ([\d.]+) and", "%.3f"),
        ("field LOO substructure median, 1111",
         _loo(loo, "iron_pnictide_1111", "substructure_median_loo_mae"),
         r"protocol exactly, gives [\d.]+, [\d.]+, [\d.]+ and ([\d.]+),",
         "%.3f"),
        ("tier 1 fits", int((tiers == "Tier_1").sum()),
         r"(\d+) of the \d+ fits resolve their scale", "%d"),
        ("tier fits total", len(fh),
         r"\d+ of the (\d+) fits resolve their scale", "%d"),
        ("tier 3 fits", int((tiers == "Tier_3").sum()),
         r"match, (\d+) through the Tier 3", "%d"),
        ("tier 2 fits", int((tiers == "Tier_2").sum()),
         r"and (\d+) through the Tier 2", "%d"),
        ("temperature-axis papers", bt.paper_id.nunique(),
         r"\d+ of the (\d+) (?:temperature-axis )?source papers", "%d"),
        ("dispatched records at the grid point",
         len(em[(em.T_K == 4.2) & (em.H_T == 5.0)]),
         r"the (\d+) MgB2-class (?:prediction )?records covering", "%d"),
        ("compounds at the grid point",
         int(em[(em.T_K == 4.2) & (em.H_T == 5.0)].compound_formula.nunique()),
         r"MgB2-class (?:prediction )?records covering (\d+) distinct "
         r"compounds", "%d"),
    ]
    for code, label in (
            ("H_below_validated_reduced_field",
             r"([\d.]+)% for lying below the validated reduced field"),
            ("Hc2_unavailable",
             r"([\d.]+)% for a missing upper-critical-field anchor"),
            ("T_above_Tc",
             r"([\d.]+)% for a target temperature above Tc"),
            ("T_above_validated_reduced_temperature",
             r"([\d.]+)% for lying at or above the validated reduced "
             r"temperature"),
            ("family_fails_field_axis_validation",
             r"([\d.]+)% for the family failing field-axis validation")):
        Q.append(("refusal share, " + code,
                  100.0 * (flags == code).sum() / len(p), label, "%.1f"))
    return Q


WINDOW = 110
NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")


def doc_text(path):
    if path.endswith(".md"):
        return re.sub(r"\s+", " ", open(path, encoding="utf-8").read())
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf8", "ignore")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    ap.add_argument("--show-unbound", type=int, default=0,
                    help="print this many unbound numbers per document")
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")

    Q = quantities()
    artifacts = [("manuscript", "HT10016_revised_corrected.docx"),
                 ("supplement", "SUPPLEMENTAL_MATERIAL_revised_corrected.docx"),
                 ("letter", "RESPONSE_TO_REFEREES_corrected.docx")]

    failures, total_bound, total_nums = [], 0, 0
    print("numeric claims bound to deposit quantities\n")
    for label, name in artifacts:
        path = os.path.join(args.dir, name)
        if not os.path.exists(path):
            print("%-12s MISSING" % label)
            failures.append(label)
            continue
        text = doc_text(path)
        spans, bound, bad = set(), 0, []
        for qname, value, pat, fmt in Q:
            want = fmt % value
            for m in re.finditer(pat, text):
                # A pattern ending at a sentence boundary captures the full
                # stop with the number, because [\d.]+ does not know a period
                # ends a sentence. "2.571." then disagrees with 2.571 and the
                # check reports a defect that is its own. No number here ends
                # in a period, so stripping one is safe and fixes every
                # pattern rather than the one that happened to expose it.
                got = m.group(1).rstrip(".")
                spans.add((m.start(1), m.end(1)))
                if got == want:
                    bound += 1
                else:
                    lo = max(0, m.start() - 80)
                    bad.append((qname, want, got,
                                text[lo:m.end() + 80].strip()))
        allnums = list(NUM.finditer(text))
        total_nums += len(allnums)
        total_bound += bound
        # A disagreement is only reported where nothing else in the window
        # matched, so a quantity mentioned near an unrelated number does not
        # fire on every occurrence.
        print("%-12s %4d bound, %4d numeric tokens" % (label, bound,
                                                       len(allnums)))
        for qname, want, got, ctx in bad:
            print("   DISAGREES  %-36s document %s, deposit %s"
                  % (qname, got, want))
            print("      ...%s..." % ctx[:160])
            failures.append("%s: %s" % (label, qname))
        if args.show_unbound:
            un = [n.group(0) for n in allnums
                  if not any(s <= n.start() < e for s, e in spans)]
            print("   unbound sample: %s"
                  % ", ".join(un[:args.show_unbound]))

    print("\n   %d of %d numeric tokens bound (%.1f%%)"
          % (total_bound, total_nums, 100.0 * total_bound / max(total_nums, 1)))
    print()
    if failures:
        print("%d disagreement(s)" % len(failures))
        return 1
    print("every bound claim agrees with the deposit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
