"""
apply_figure_caption_edits.py

Bring the Figure 1 caption and Table IV into line with the corrected figures.

Correcting Figure 1 to the deposit created a contradiction inside the
manuscript: the panel now draws 85 of 183 candidate compounds dispatched while
the caption beside it read 185 and 125, and Table IV read 239 / 185 / 125. All
of those are pre-withdrawal values from the same era as the figure.

Every replacement here is a number the deposit computes, and each is asserted
against analysis/figure_counts.py before it is written, so the script cannot
put a typo into the document. It refuses to write if any edit misses.

What this script deliberately does NOT touch, because these need a decision
about the claim and not a number swap:

  * "For iron chalcogenide 11-type, sample-form conditioning is mandatory, so
    the dispatch uses the single-crystal ..." describes a dispatch that no
    longer happens. All 441 of that family's grid points are refused: 248 by
    the reduced-field gate, 153 for target temperature above Tc, 40 by the
    family field-axis gate.
  * "We report family medians at 4.2 K and the lowest evaluated field of 0.1 T"
    reports values at a field where nothing is dispatched. The emitted grid
    now carries one field, 5 T; the reduced-field gate removed every low-field
    point.
  * "The median full width of the 95% bootstrap confidence interval across
    non-refused predictions is 0.39 dex, a factor of about 2.5" is 0.825 dex
    over the 256 emitted records, a factor of about 6.7. The tight intervals
    were the low-field ones the gate removed.
  * The aside comparing 1 T against a 50 T upper critical field, which is also
    outside the dispatched grid.

Usage:
    python3 analysis/apply_figure_caption_edits.py --ms IN.docx --out OUT.docx
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import docx  # noqa: E402

from apply_manuscript_edits import apply  # noqa: E402
from figure_counts import from_deposit  # noqa: E402


def build(C):
    cand = C["candidate_compounds"]
    disp = C["dispatched_compounds"]
    by = {f["key"]: f for f in C["families"]}
    ch, pn = by["iron_chalcogenide_11"], by["iron_pnictide_122"]
    # Candidate records per family come from the tier table, which is the
    # column Table IV's first slot has always held.
    import pandas as pd
    t = pd.read_csv(os.path.join("data",
                                 "phase_3_p56_candidate_tier_assignment.csv"))
    rec = {k: int((t.substructure_family == k).sum())
           for k in t.substructure_family.unique()}
    p57 = pd.read_csv(os.path.join("data",
                                   "phase_3_p57_de_novo_predictions.csv"),
                      low_memory=False)
    flags = p57.refusal_flag.fillna("")
    share = {k: 100.0 * (flags == k).sum() / len(p57)
             for k in set(flags) if k}
    return [
        # Figure 1 caption
        ("and how many are refused for want of a critical-field anchor",
         "and how many are refused, with the gate that refused them",
         "four refusal codes now fire, not one", None),
        ("The calibrated model evaluates 185 distinct candidate compounds",
         "The calibrated model evaluates %d distinct candidate compounds" % cand,
         "candidate compounds from the deposit", None),
        ("Of the 185 candidates, 125 are dispatched with at least one "
         "non-refused prediction target and 123 survive the calibration "
         "screen of Sec. III.E",
         "Of the %d candidates, %d are dispatched with at least one "
         "non-refused prediction target and 123 lie inside the calibration "
         "domain of Sec. III.E" % (cand, disp),
         "dispatched compounds from the deposit; the 123 are the compounds "
         "inside the calibration domain, a strict superset of the %d, and the "
         "difference is refused by the reduced-field and above-Tc gates rather "
         "than by the calibration screen" % disp, None),
        # Table IV
        ("55 / 31 / 31",
         "%d / %d / %d" % (rec["iron_chalcogenide_11"], ch["total"],
                           ch["dispatched"]),
         "iron chalcogenide 11-type, recomputed", None),
        ("79 / 51 / 9",
         "%d / %d / %d" % (rec["iron_pnictide_122"], pn["total"],
                           pn["dispatched"]),
         "iron pnictide 122-type, recomputed", None),
        ("239 / 185 / 125",
         "%d / %d / %d" % (len(t), cand, disp),
         "combined row, recomputed", None),
        # The refusal shares beside Table IV. The reduced-field code is the
        # largest of the four and the sentence did not mention it at all,
        # which is the same omission 176d750 found in Figure 2's box.
        ("125 compounds receive at least one non-refused prediction target; "
         "25.1% of candidate-grid-point predictions are refused for a missing "
         "field anchor and 10.5% for target temperature above Tc.",
         "%d compounds receive at least one non-refused prediction target; "
         "%.1f%% of candidate-grid-point predictions are refused for lying "
         "below the validated reduced field, %.1f%% for a missing field anchor "
         "and %.1f%% for target temperature above Tc."
         % (disp, share["H_below_validated_reduced_field"],
            share["Hc2_unavailable"], share["T_above_Tc"]),
         "four codes fire; the reduced-field code is the largest and was "
         "unmentioned", None),
        ("Missing upper-critical-field anchors produce refusals for 25.1% of "
         "candidate-grid-point predictions, and target temperatures above the "
         "transition temperature produce refusals for 10.5%.",
         "Predictions below the validated reduced field produce refusals for "
         "%.1f%% of candidate-grid-point predictions, missing "
         "upper-critical-field anchors for %.1f%%, and target temperatures "
         "above the transition temperature for %.1f%%."
         % (share["H_below_validated_reduced_field"],
            share["Hc2_unavailable"], share["T_above_Tc"]),
         "same three shares, recomputed", None),
        ("Candidate dispatch across 185 distinct compounds in three "
         "validated substructure families.",
         "Candidate dispatch across %d distinct compounds in three validated "
         "substructure families, of which one emits at the current gate "
         "settings." % cand,
         "183 candidates, and only the MgB2 class still emits", None),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")

    C = from_deposit()
    edits = build(C)
    doc = docx.Document(a.ms)
    report = []
    misses = apply(doc, edits, "manuscript", report)
    for _, done, find, repl, why in report:
        print("   %-4s %s\n        -> %s\n        %s"
              % ("ok" if done else "MISS", find, repl, why))
    print()
    if misses:
        print("%d edit(s) missed; nothing written" % len(misses))
        return 1
    if a.dry_run:
        print("dry run, nothing written")
        return 0
    doc.save(a.out)
    print("wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
