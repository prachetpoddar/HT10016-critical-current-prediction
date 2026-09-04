"""
apply_traced_value_edits.py

Carry the corrections in audit/superseded_values_traced_20260904.md into the
three artifacts.

Only the edits the deposit settles are here. Each replacement value is either
recomputed at run time from a deposited table or is a wording change that
removes a statement the deposit contradicts. Four clusters are deliberately NOT
in this script because the deposit does not decide them on its own, and are
listed at the end of the ledger instead: the printed Tables S4, S5 and S6, the
unreproducible 0.751/0.929/1.094/2.622, the field-scale audit numbers that the
three documents give three different ways, and the calibration screen's effect,
which cannot be restated until phase_3_p56_candidate_tier_assignment.csv is
regenerated.

The script refuses to write if any find misses, and treats an already-applied
edit as done.

Usage:
    python3 analysis/apply_traced_value_edits.py --ms MS.docx --supp S.docx \
        --letter L.docx --out-dir DIR [--dry-run]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import docx  # noqa: E402
import pandas as pd  # noqa: E402

from apply_manuscript_edits import apply  # noqa: E402

DATA = "data"


def deposit():
    """Every number this script writes, recomputed rather than quoted."""
    d = {}
    a = pd.read_csv(os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv"))
    sys.path.insert(0, "analysis")
    from figure_4_source import aggregate_per_physical_sample
    d["families"] = a.substructure.nunique()
    d["anchor_rows"] = len(a)
    d["samples"] = len(aggregate_per_physical_sample(a))

    p = pd.read_csv(os.path.join(DATA, "phase_3_p57_de_novo_predictions.csv"))
    d["grid_rows"] = len(p)
    d["emitted"] = int(p.refusal_flag.isna().sum())
    d["dispatched_compounds"] = int(p.loc[p.refusal_flag.isna(),
                                         "compound_formula"].nunique())
    d["refusals"] = p.refusal_flag.value_counts().to_dict()

    f = pd.read_csv(os.path.join(DATA,
                                 "phase_3_form3_fits_partial_cohortB_v2.csv"))
    ex = f[f.Hc2_source.astype(str).str.contains("extrapolated_to_low_T_anchor")]
    d["endpoint_fits"] = len(ex)
    d["endpoint_factor"] = float((ex.Hc2_T_default / ex.Hc2_T_used).median())

    pr = pd.read_csv(os.path.join(DATA, "provenance_table_fitcohort_full.csv"))
    d["cuprate_papers"] = int(pr.substructure_family.astype(str)
                              .str.startswith("cuprate").sum())

    # The anchor-count validation. The manuscript pairs a three-compound K = 1
    # error with a four-compound K = 3 one, which is the mismatch the same
    # section says it is correcting.
    import external_anchor_count as eac
    r = eac.results() if hasattr(eac, "results") else None
    if r is None:
        # fall back to the deposited audit table the script writes
        t = pd.read_csv(os.path.join("audit", "external_anchor_count.csv"))
        t = t.set_index("cohort")
        d["k1_three"] = float(t.loc["K=1, three monotonic", "mae"])
        d["k3_three"] = float(t.loc["K=3, three monotonic", "mae"])
        d["k1_four"] = float(t.loc["K=1, all four", "mae"])
        d["k3_four"] = float(t.loc["K=3, all four", "mae"])
    d["reduction"] = 100.0 * (d["k1_three"] - d["k3_three"]) / d["k1_three"]

    from phase_3_p39_multi_stage_predictor import stage1_loso_rank_order
    s1 = stage1_loso_rank_order()
    d["rank_mae"] = float(s1.rank_position_error.mean())
    d["rank_within_1"] = int((s1.rank_position_error <= 1).sum())
    d["rank_n"] = len(s1)
    return d


def edits(d):
    red = "%.1f%%" % d["reduction"]
    k1t, k3t = "%.3f" % d["k1_three"], "%.3f" % d["k3_three"]
    fam = {7: "seven", 8: "eight", 9: "nine"}[d["families"]]
    words = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
    cup = words.get(d["cuprate_papers"], str(d["cuprate_papers"]))
    fac = "%.1f" % d["endpoint_factor"]

    ms = [
        # 1. the populated-family count, wrong three ways in one sentence
        ("It uses nine populated families: iron chalcogenide 11-type, iron "
         "pnictide 122-type, MgB2-class, iron pnictide 1111-type, and four "
         "cuprate substructures, plus one conventional family.",
         "It uses %s populated families: iron chalcogenide 11-type, iron "
         "pnictide 122-type, iron pnictide 1111-type, three cuprate "
         "substructures, and the MgB2-class conventional family." % fam,
         "the deposit has %d populated families; the sentence named four "
         "cuprates where there are three and counted the MgB2 class twice"
         % d["families"], None),

        ("on the mean maximum Pauling electronegativity across nine "
         "substructure families, with leave-one-substructure-out validation",
         "on the mean maximum Pauling electronegativity across %s "
         "substructure families, with leave-one-substructure-out validation"
         % fam,
         "the same paragraph already says seven four sentences later", None),

        ("The Stage 1 error was computed across nine substructure families",
         "The Stage 1 error was computed across the nine substructure "
         "families of an earlier version of this analysis",
         "true of the earlier cohort, and now says so", None),

        # 2. the rank-position error
        ("The rank-position error remains 1.11,",
         "The rank-position error remains %.2f," % d["rank_mae"],
         "stage1_loso_rank_order gives %.2f over %d held-outs"
         % (d["rank_mae"], d["rank_n"]), None),

        # 3. the anchor-count reduction
        ("The pooled error decreases to 0.927.",
         "The pooled error on those three decreases to %s." % k3t,
         "0.927 is the four-compound K = 3 value; the three monotonic "
         "cuprates give %s" % k3t, None),

        ("Comparing this against the four-compound one-anchor value of 1.592 "
         "gives a 41.8% reduction, but that ratio compares different cohorts,",
         "Comparing the four-compound one-anchor value of 1.592 against the "
         "four-compound three-anchor value of 0.927 gives a 41.8%% reduction, and "
         "the matched three-compound reduction is %s, so the two ratios rest "
         "on different cohorts," % red,
         "41.8% is a four-against-four ratio; the mismatched one was the "
         "26.8%", None),

        ("the one-anchor error is 1.267 and the reduction is 26.8%, and that "
         "is the figure we carry.",
         "the one-anchor error is %s, the three-anchor error is %s, and the "
         "reduction is %s, and that is the figure we carry." % (k1t, k3t, red),
         "the matched pair is %s to %s" % (k1t, k3t), None),

        ("reducing the error by 26.8% on the matched three-compound cohort",
         "reducing the error by %s on the matched three-compound cohort" % red,
         "matched three-compound reduction", None),

        ("three anchors reduce error to 0.927 on the monotonic subset, a "
         "26.8% reduction on the matched cohort.",
         "on the matched three monotonic cuprates three anchors reduce the "
         "error from %s to %s, a %s reduction." % (k1t, k3t, red),
         "0.927 is not the monotonic-subset value", None),

        # 4. K counts measured points, not compounds. 8d43b4c settled this on
        #    the implementation and said it had corrected the manuscript. It
        #    had not.
        ("Check that at least K = 3 anchor compounds are available within the "
         "family.",
         "Check that at least K = 3 anchor measurements are available for the "
         "candidate.",
         "K_MIN and K_MAX bound len(anchors), and an Anchor is one measured "
         "triple; Fig. 4 varies K at fixed cohort size", None),

        ("The requirement of at least three anchor compounds is therefore an "
         "empirical boundary",
         "The requirement of at least three anchor measurements is therefore "
         "an empirical boundary",
         "same rule, same wording", None),

        ("Requiring three anchor compounds restores predictive performance",
         "Requiring three anchor measurements restores predictive performance",
         "same rule, same wording", None),

        # 5. the endpoint-resolution factor
        ("a median factor of 5.1 across the 41 fits it affects",
         "a median factor of %s across the %d fits it affects"
         % (fac, d["endpoint_fits"]),
         "the extrapolated-to-low-T subset is %d fits at a median "
         "default/used of %.4f" % (d["endpoint_fits"], d["endpoint_factor"]),
         None),

        # 6. the cuprates are in the fitted cohort
        ("and the cuprate results reported here appear only as an external "
         "validation set exhibiting measurement-window saturation.",
         "and the cuprates enter this work two ways: %s cuprate papers sit in "
         "the fitted cohort, and four out-of-corpus cuprates serve as the "
         "external validation set, where they exhibit measurement-window "
         "saturation." % cup,
         "provenance_table_fitcohort_full.csv holds %d cuprate papers"
         % d["cuprate_papers"], None),

        # 7. Table IV's caption against Table IV's body
        ("The third figure in that column is the dispatch-routine count and "
         "reconciles with the deposited prediction file; the calibration "
         "screen of Sec. III.E then removes two iron chalcogenide candidates, "
         "leaving 123 compounds reported.",
         "The third figure in that column is the dispatch-routine count and "
         "reconciles with the deposited prediction file, which emits at least "
         "one prediction for %d compounds."
         % d["dispatched_compounds"],
         "the prediction file emits %d compounds, all MgB2-class, so no iron "
         "chalcogenide candidate reaches the calibration screen; the 123 came "
         "from a tier table that predates both window gates"
         % d["dispatched_compounds"], None),
    ]

    supp = [
        ("The rank-position mean absolute error remains 1.11, with 5 of 9 "
         "substructures predicted within one rank position.",
         "The rank-position mean absolute error remains %.2f, with %d of %d "
         "substructures predicted within one rank position."
         % (d["rank_mae"], d["rank_within_1"], d["rank_n"]),
         "recomputed from stage1_loso_rank_order", None),

        ("Against the four-compound K = 1 value of 1.592 this is a 41.8% "
         "reduction, but that ratio compares different cohorts.",
         "Against the four-compound K = 1 value of 1.592 the four-compound "
         "K = 3 value of 0.927 is a 41.8%% reduction; the matched three give %s, "
         "from %s to %s." % (red, k1t, k3t),
         "41.8% is four against four", None),

        ("the K = 1 error is 1.267 and the reduction is 26.8%, which is the "
         "figure the main text carries.",
         "the K = 1 error is %s, the K = 3 error is %s, and the reduction is "
         "%s, which is the figure the main text carries." % (k1t, k3t, red),
         "matched pair", None),

        ("this underestimates the scale by a median factor of 5.1 across the "
         "41 fits it affects.",
         "this underestimates the scale by a median factor of %s across the "
         "%d fits it affects." % (fac, d["endpoint_fits"]),
         "extrapolated-to-low-T subset", None),

        ("One row is one physical sample from one paper.",
         "One row is one isotherm record, a single sample from one paper at "
         "one measurement temperature, so the %d rows cover %d physical "
         "samples." % (d["anchor_rows"], d["samples"]),
         "aggregate_per_physical_sample collapses %d rows to %d samples by "
         "stripping the isotherm suffix" % (d["anchor_rows"], d["samples"]),
         None),

        ("the 2151-row candidate prediction file",
         "the %d-row candidate prediction file" % d["grid_rows"],
         "deposited row count", None),

        ("The file contains 1386 emitted predictions, 540 refusals for a "
         "missing upper-critical-field anchor, and 225 refusals for a target "
         "temperature above the transition temperature.",
         "The file contains %d emitted predictions and %d refusals: %d for a "
         "field below the validated reduced-field range, %d for a missing "
         "upper-critical-field anchor, %d for a target temperature above the "
         "transition temperature, %d for a temperature above the validated "
         "reduced-temperature range, and %d for a family that fails "
         "field-axis validation."
         % (d["emitted"], sum(d["refusals"].values()),
            d["refusals"]["H_below_validated_reduced_field"],
            d["refusals"]["Hc2_unavailable"],
            d["refusals"]["T_above_Tc"],
            d["refusals"]["T_above_validated_reduced_temperature"],
            d["refusals"]["family_fails_field_axis_validation"]),
         "three of the five refusal codes were missing and two of the three "
         "printed counts were stale", None),
    ]

    letter = [
        ("the larger error is computed across nine substructure families",
         "the larger error is computed across the nine substructure families "
         "of an earlier version of this analysis",
         "true of the earlier cohort, and now says so", None),

        ("the 41.8% anchor-count reduction quoted in Section III.B compared a "
         "four-compound value against a three-compound one.",
         "the 26.8%% anchor-count reduction quoted in Section III.B compared a "
         "three-compound one-anchor value against a four-compound three-anchor "
         "one; the matched pair gives %s." % red,
         "41.8% is four against four; the mismatched ratio was the 26.8%",
         None),

        ("On the matched three it is 26.8%, and that is the figure we now "
         "carry.",
         "That matched pair, %s to %s, is the figure we now carry." % (k1t, k3t),
         "matched pair", None),

        ("that the cuprates appearing in this paper do so only as an external "
         "validation set exhibiting measurement-window saturation.",
         "that the cuprates enter the work two ways, %s cuprate papers in the "
         "fitted cohort and four out-of-corpus cuprates as the external "
         "validation set, where they exhibit measurement-window saturation."
         % cup,
         "provenance_table_fitcohort_full.csv holds %d cuprate papers"
         % d["cuprate_papers"], None),

        ("check that at least three anchor compounds are available within the "
         "family;",
         "check that at least three anchor measurements are available for the "
         "candidate;",
         "K counts measured points supplied with a query", None),

        ("evaluated across nine substructure families with "
         "leave-one-substructure-out validation.",
         "evaluated across %s substructure families with "
         "leave-one-substructure-out validation." % fam,
         "the deposit has %d" % d["families"], None),

        ("which underestimates the scale by a median factor of 5.1 across the "
         "41 fits it affects.",
         "which underestimates the scale by a median factor of %s across the "
         "%d fits it affects." % (fac, d["endpoint_fits"]),
         "extrapolated-to-low-T subset", None),
    ]
    return ms, supp, letter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms", required=True)
    ap.add_argument("--supp", required=True)
    ap.add_argument("--letter", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")

    d = deposit()
    print("recomputed from the deposit")
    for k in sorted(d):
        if k != "refusals":
            print("   %-24s %s" % (k, d[k]))
    print()

    ms_e, supp_e, letter_e = edits(d)
    report, misses = [], []
    docs = [(args.ms, ms_e, "manuscript"),
            (args.supp, supp_e, "supplement"),
            (args.letter, letter_e, "letter")]
    objs = []
    for path, es, label in docs:
        o = docx.Document(path)
        misses += apply(o, es, label, report)
        objs.append((o, path))

    for label, done, find, repl, why in report:
        print("   %-11s %-4s %s" % (label, "ok" if done else "MISS", find))
        if not done:
            print("                    %s" % why)
    print()
    if misses:
        sys.exit("%d edit(s) did not match; nothing written" % len(misses))
    if args.dry_run:
        print("%d edit(s) all matched; --dry-run, nothing written"
              % len(report))
        return 0
    os.makedirs(args.out_dir, exist_ok=True)
    for o, path in objs:
        out = os.path.join(args.out_dir, os.path.basename(path))
        o.save(out)
        print("written %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
