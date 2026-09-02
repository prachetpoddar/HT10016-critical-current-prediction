#!/usr/bin/env python3
"""
apply_field_window_gate.py

Enforces the field-axis applicability window and the field-axis validation
result on the dispatch table.

Why this exists. Sec. II.A states the applicability window for Form 3 on the
field axis as reduced field above 0.3, and Sec. II.D states that the predictor
dispatches only inside validated scope. The deposited dispatch table did not
enforce the first through the second: 1054 of the 1350 non-refused prediction
tuples sat below H/Hc2 = 0.3, some at 0.002, and the manuscript described them
as extrapolations while also claiming that the refusal gates prevent
out-of-scope prediction. Both statements cannot hold at once. This script makes
the second true by adding the refusal the first implies.

The gate. A field-axis prediction is refused when the requested reduced field
lies below H_MIN_REDUCED, with the reason code below. The refusal is per
prediction target, not per compound: a compound refused at 0.1 T keeps whatever
targets fall inside the window, and keeps its temperature-axis output, which is
the same convention the other refusal codes already use.

What survives is worth stating plainly, because the gate is not cosmetic. Only
the 5 T column clears the bound, and only where the critical-field anchor is
small enough: MgB2-class at 15.5 T gives 0.32, iron chalcogenide 11-type at
16 T gives 0.31, and every iron pnictide 122-type anchor of 50 T or more gives
at most 0.10, so that family retains no field-axis target at all.

    python analysis/apply_field_window_gate.py --dry-run
    python analysis/apply_field_window_gate.py

Run from the repository root.
"""
import argparse
import os
import shutil
import sys

import pandas as pd

DATA = "data"
PRED = os.path.join(DATA, "phase_3_p57_de_novo_predictions.csv")
AUDIT = os.path.join("audit", "field_window_gate.csv")

H_MIN_REDUCED = 0.3
CODE = "H_below_validated_reduced_field"

# Second gate. Sec. III.C validates each family on each axis against a
# screening threshold of 1 in the exponent, and Sec. III.E restricts dispatch to
# families that pass. Applying that rule to the field axis on the corrected
# cohort, iron chalcogenide 11-type is at 1.093 and iron pnictide 1111-type at
# 3.13, so neither passes; MgB2-class at 0.753 and iron pnictide 122-type at
# 0.973 do. The manuscript previously reported the chalcogenide value while
# still labelling that family field-validated and dispatching it, which is the
# contradiction this gate removes. The thresholds are read from the deposited
# leave-one-out table rather than hardcoded, so a change in the cohort moves the
# gate with it.
LOO = os.path.join(DATA, "phase_3_p47_compound_leave_out_MAE.csv")
SCREENING_THRESHOLD = 1.0
CODE_FAMILY = "family_fails_field_axis_validation"

# Columns the refusal blanks, matching what the existing refusal codes blank.
VALUE_COLS = ["predicted_log_Jc", "predicted_log_Jc_lower_95",
              "predicted_log_Jc_upper_95"]

# The gate is non-destructive. A refused target's value is moved into a
# withheld_ column rather than deleted, so the dispatch emits nothing while the
# value the model would have produced stays auditable. Sec. 16 of the
# Supplemental Material reports that withheld set, labelled as what it is: a
# projection outside the validated window, not a prediction. Deleting it would
# have made the paper's own scope boundary unfalsifiable, and would have thrown
# away the evidence for what the framework covers if the cohort grows.
WITHHELD_COLS = {c: "withheld_" + c.replace("predicted_", "")
                 for c in VALUE_COLS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")

    d = pd.read_csv(PRED, low_memory=False)
    d["refusal_flag"] = d["refusal_flag"].fillna("")
    h_red = d.H_T / d.Hc2_T_anchor

    loo = pd.read_csv(LOO)
    failing = set(loo.loc[loo.compound_loo_mae > SCREENING_THRESHOLD, "substructure"])
    passing = set(loo.loc[loo.compound_loo_mae <= SCREENING_THRESHOLD, "substructure"])

    fires = (d.refusal_flag == "") & h_red.notna() & (h_red < H_MIN_REDUCED)
    fires_fam = (d.refusal_flag == "") & ~fires & d.substructure.isin(failing)
    already = (d.refusal_flag == CODE).sum()

    print("field-axis applicability gate, H/Hc2 >= %.2f%s\n"
          % (H_MIN_REDUCED, "   (DRY RUN)" if args.dry_run else ""))
    print("   tuples in the dispatch table            %5d" % len(d))
    print("   non-refused before the gate             %5d" % (d.refusal_flag == "").sum())
    print("   refused, reduced field below %.2f       %5d" % (H_MIN_REDUCED, fires.sum()))
    print("   refused, family fails the field axis    %5d" % fires_fam.sum())
    print("   already carried the window code         %5d" % already)
    print("   non-refused after both gates            %5d"
          % ((d.refusal_flag == "").sum() - fires.sum() - fires_fam.sum()))
    print("\n   field-axis validation, threshold %.1f" % SCREENING_THRESHOLD)
    for _, r in loo.sort_values("compound_loo_mae").iterrows():
        print("      %-24s %.4f   %s" % (r.substructure, r.compound_loo_mae,
              "passes" if r.compound_loo_mae <= SCREENING_THRESHOLD else "FAILS, dispatch refused"))

    survivors = d[(d.refusal_flag == "") & ~fires & ~fires_fam]
    print("\n   compounds keeping a field-axis target   %5d"
          % survivors.compound_formula.nunique())
    print("   by family:")
    for fam, s in survivors.groupby("substructure"):
        print("      %-24s %3d compounds, fields %s"
              % (fam, s.compound_formula.nunique(),
                 sorted(s.H_T.unique())))
    lost = d[fires]
    for fam in sorted(set(d.substructure.dropna())):
        keep = survivors[survivors.substructure == fam].compound_formula.nunique()
        if keep == 0 and (lost.substructure == fam).any():
            print("      %-24s retains no field-axis target" % fam)

    if not args.dry_run:
        if not os.path.exists(PRED + ".pre_field_gate"):
            shutil.copy2(PRED, PRED + ".pre_field_gate")
        for src, dst in WITHHELD_COLS.items():
            if dst not in d.columns:
                d[dst] = pd.NA
            d.loc[fires | fires_fam, dst] = d.loc[fires | fires_fam, src]
        # Do not reset this column wholesale. On a second run fires is empty, so
        # a blanket reset would erase the reduced-field values of every target
        # the first run withheld and leave the audit unable to explain them.
        if "withheld_reduced_field" not in d.columns:
            d["withheld_reduced_field"] = pd.NA
        d.loc[fires | fires_fam, "withheld_reduced_field"] = h_red[fires | fires_fam]
        # Object dtype would serialize these through str() and silently drop
        # digits on every rerun, so the column round-trips as float.
        d["withheld_reduced_field"] = pd.to_numeric(d["withheld_reduced_field"],
                                                    errors="coerce")
        d.loc[fires, VALUE_COLS] = pd.NA
        d.loc[fires, "refusal_flag"] = CODE
        d.loc[fires_fam, VALUE_COLS] = pd.NA
        d.loc[fires_fam, "refusal_flag"] = CODE_FAMILY
        d.to_csv(PRED, index=False)
        os.makedirs("audit", exist_ok=True)
        rep = d[fires | fires_fam][
            ["compound_formula", "substructure", "Tc_anchor_K", "Hc2_T_anchor",
             "T_K", "H_T", "withheld_reduced_field", "refusal_flag",
             "withheld_log_Jc", "withheld_log_Jc_lower_95",
             "withheld_log_Jc_upper_95"]]
        # The gate is idempotent on the table but not on its own audit: a
        # second run sees the codes already written, fires on nothing, and would
        # replace a 1094-row record with an empty file. That is the same defect
        # as a generator reading the file it overwrites, so it is refused here.
        if len(rep) == 0 and os.path.exists(AUDIT) and os.path.getsize(AUDIT) > 200:
            print("\nwritten: %s  (backup at %s.pre_field_gate)" % (PRED, PRED))
            print("audit  : %s left unchanged; this run fired on nothing and the "
                  "existing record is not empty" % AUDIT)
        else:
            rep.to_csv(AUDIT, index=False)
            print("\nwritten: %s  (backup at %s.pre_field_gate)" % (PRED, PRED))
            print("audit  : %s  (%d refused targets)" % (AUDIT, len(rep)))
    else:
        print("\nnothing was written.")


if __name__ == "__main__":
    main()
