#!/usr/bin/env python3
"""
reclassify_records.py

Corrects substructure labels that the formula matcher assigned wrongly, and
records why, so the change is auditable rather than a hand edit.

The register below is the whole set. Each entry names the pipeline formula, the
family it was given, the family it belongs to, and the evidence, which in both
cases is this paper's own Table S3 mapping the pipeline formula to a conventional
name the manuscript already assigns to that family.

How the labels went wrong. assign_substructure in
phase_3_p39_multi_stage_predictor.py tests formula substrings: a compound is
iron chalcogenide 11-type if it contains "FeTe" or "FeSe", and iron pnictide
122-type if it contains "Fe2As2", "BaFe" or "(Fe". The string "Fe2TeSe" contains
neither "FeTe" nor "FeSe", because of the 2, so it fell through to
other_unclassified even though the same material is spelled FeTeSe, FeSeTe,
FeTe0.5Se0.5 and FeSe0.5Te0.5 elsewhere in the deposit and classified as
chalcogenide every time. KBa(FeAs)4 contains "(Fe" and does classify correctly
under that function, but the temperature-axis table stores a substructure column
written by an earlier classifier that missed it.

Why it matters. The two names carry 87 of the 414 temperature-axis fits, and
both sat in an iron_other bucket that the manuscript never names. With Fe2TeSe
excluded, iron chalcogenide 11-type had 4 compounds and 32 fits and a
leave-one-out error of 0.215, reported as the lowest error of any family on
either axis. With it included the family has 5 compounds and 102 fits, and the
error is 0.962. The claim that it is the lowest does not survive; the claim that
it clears the screening threshold does.

Only two deposited tables carry these names, and both are corrected here.
Neither name appears on the field axis or in the anchor table, so no field-axis
value and no variance-decomposition ratio changes.

    python analysis/reclassify_records.py --dry-run
    python analysis/reclassify_records.py

Run from the repository root.
"""
import argparse
import os
import shutil
import sys

import pandas as pd

REGISTER = [
    dict(formula="Fe2TeSe", was="iron_other", now="iron_chalcogenide_11",
         reason=("Table S3 maps this pipeline formula to FeTe0.5Se0.5, which "
                 "Sec. I names as an iron chalcogenide 11-type material. The "
                 "same compound is spelled FeTeSe, FeSeTe, FeTe0.5Se0.5 and "
                 "FeSe0.5Te0.5 in the field-axis table and is classified as "
                 "chalcogenide under every one of those spellings. The matcher "
                 "tests for the substrings FeTe and FeSe, and Fe2TeSe contains "
                 "neither")),
    dict(formula="KBa(FeAs)4", was="iron_other", now="iron_pnictide_122",
         reason=("Table S3 maps this pipeline formula to (Ba,K)Fe2As2, which "
                 "Sec. II.B names as a cation-variant 122-type compound "
                 "anchored on BaFe2As2")),
]

TARGETS = [("data/phase_3_p44_post_UCLA_beta_T_fits.csv",
            "compound_formula", "substructure"),
           ("data/provenance_table_fitcohort_full.csv",
            "compound", "substructure_family")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("reclassification register%s\n"
          % ("   (DRY RUN)" if args.dry_run else ""))
    for r in REGISTER:
        print("   %-14s %-18s -> %-22s" % (r["formula"], r["was"], r["now"]))
        print("      %s\n" % r["reason"])

    stamp = "20260902"
    backup = os.path.join("audit", "pre_reclassification_%s" % stamp)
    total = 0
    print("%-52s %6s %6s" % ("table", "rows", "changed"))
    for path, ccol, scol in TARGETS:
        if not os.path.exists(path):
            continue
        d = pd.read_csv(path, low_memory=False)
        n = 0
        for r in REGISTER:
            hit = (d[ccol] == r["formula"]) & (d[scol] == r["was"])
            n += int(hit.sum())
            if not args.dry_run:
                d.loc[hit, scol] = r["now"]
        print("%-52s %6d %6d" % (os.path.basename(path)[:52], len(d), n))
        total += n
        if n and not args.dry_run:
            os.makedirs(backup, exist_ok=True)
            shutil.copy2(path, os.path.join(backup, os.path.basename(path)))
            d.to_csv(path, index=False)

    if not total:
        print("\nno row carried a registered mislabel; the deposit is already "
              "corrected")
    elif not args.dry_run:
        print("\nbackups: %s" % backup)

    # State the consequence rather than leaving it to be recomputed by hand.
    t = pd.read_csv(TARGETS[0][0])
    for fam in ("iron_chalcogenide_11", "iron_pnictide_122"):
        s = t[t.substructure == fam]
        print("   %-24s %d compounds, %d papers, %d fits"
              % (fam, s.compound_formula.nunique(), s.paper_id.nunique(), len(s)))
    print("\nRe-run analysis/temperature_axis_summary.py and "
          "analysis/verify_deposit.py after this.")
    if args.dry_run:
        print("nothing was written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
