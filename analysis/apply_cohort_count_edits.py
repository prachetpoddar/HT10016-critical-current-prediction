"""
apply_cohort_count_edits.py

Two supplement counts that the deposit contradicts, both recomputed here.

  * "the cuprate substructures contribute 7 distinct compounds to the fitted
    cohort". provenance_table_fitcohort_full.csv holds five cuprate papers and
    five distinct cuprate compounds, and the supplement's own Table S1 sums to
    the same five.
  * "4 of 46 iron chalcogenide 11-type fits ... reach it". The denominator is
    the whole field-axis fit table by family, which is the cohort the adjacent
    "1 of 22 iron pnictide 1111-type fits" uses. That family holds 51 fits, not
    46. The numerators are right: 28 fits sit at the imposed ceiling, and they
    split BSCCO 20, RBCO 3, iron chalcogenide 11 four and iron pnictide 1111
    one.

Usage:
    python3 analysis/apply_cohort_count_edits.py --supp S.docx --out-dir DIR
        [--dry-run]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import docx  # noqa: E402
import pandas as pd  # noqa: E402

from apply_manuscript_edits import apply  # noqa: E402
from phase_3_p39_multi_stage_predictor import assign_substructure  # noqa: E402

DATA = "data"
CEILING = 29.99


def deposit():
    pr = pd.read_csv(os.path.join(DATA, "provenance_table_fitcohort_full.csv"))
    cup = pr[pr.substructure_family.astype(str).str.startswith("cuprate")]
    f = pd.read_csv(os.path.join(
        DATA, "phase_3_form3_fits_partial_cohortB_v2.csv")).copy()
    f["fam"] = f.compound_formula.map(assign_substructure)
    tot = f.fam.value_counts()
    ceil = f[f.beta >= CEILING].fam.value_counts()
    return {"cuprate_compounds": int(cup.compound.nunique()),
            "chalcogenide_fits": int(tot.get("iron_chalcogenide_11", 0)),
            "chalcogenide_ceiling": int(ceil.get("iron_chalcogenide_11", 0)),
            "p1111_fits": int(tot.get("iron_pnictide_1111", 0)),
            "p1111_ceiling": int(ceil.get("iron_pnictide_1111", 0))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--supp", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")

    d = deposit()
    for k, v in d.items():
        print("   %-24s %s" % (k, v))
    print()

    edits = [
        ("and the cuprate substructures contribute 7 distinct compounds to the "
         "fitted cohort",
         "and the cuprate substructures contribute %d distinct compounds to "
         "the fitted cohort" % d["cuprate_compounds"],
         "provenance_table_fitcohort_full.csv and Table S1 both give %d"
         % d["cuprate_compounds"], None),

        ("%d of 46 iron chalcogenide 11-type fits and %d of %d iron pnictide "
         "1111-type fits also reach it."
         % (d["chalcogenide_ceiling"], d["p1111_ceiling"], d["p1111_fits"]),
         "%d of %d iron chalcogenide 11-type fits and %d of %d iron pnictide "
         "1111-type fits also reach it."
         % (d["chalcogenide_ceiling"], d["chalcogenide_fits"],
            d["p1111_ceiling"], d["p1111_fits"]),
         "that family holds %d fits; the adjacent 1111 denominator already "
         "uses this cohort" % d["chalcogenide_fits"], None),
    ]

    doc = docx.Document(args.supp)
    report = []
    misses = apply(doc, edits, "supplement", report)
    for label, done, find, _r, why in report:
        print("   %-11s %-4s %s" % (label, "ok" if done else "MISS", find[:70]))
        if not done:
            print("                    %s" % why)
    print()
    if misses:
        sys.exit("%d edit(s) did not match; nothing written" % len(misses))
    if args.dry_run:
        print("all matched; --dry-run, nothing written")
        return 0
    os.makedirs(args.out_dir, exist_ok=True)
    out = os.path.join(args.out_dir, os.path.basename(args.supp))
    doc.save(out)
    print("written %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
