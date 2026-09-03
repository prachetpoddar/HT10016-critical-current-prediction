#!/usr/bin/env python3
"""
apply_temperature_window_gate.py

Enforces the temperature half of the applicability window on the dispatch
table, which nothing enforced.

Why this exists. This revision added analysis/apply_field_window_gate.py, which
reads Eq. (1)'s field clause per evaluation point and refuses any target below
H/Hc2 = 0.3. No matching gate was added for the temperature clause, so the two
halves of one window were enforced by two different conventions in the same
table. The consequence was not theoretical: 93 of the 256 surviving predictions
sat at reduced temperature 0.7 or above, reaching 0.9333.

Eighty-seven of those come from the target grid itself. analysis/phase_3_p57_de
_novo_predictions.py builds t_grid as [4.2, 20.0] + [0.77 * Tc], so every
candidate carries a point at reduced temperature 0.77 by construction, ten
percent past the bound the manuscript states. The remaining six come from the
absolute 4.2 K and 20 K points landing high on low-Tc candidates; the extreme
case is a Tc of 4.5 K evaluated at 4.2 K, a reduced temperature of 0.9333.

Nothing in the deposit supports those points. Across all 260 deposited
temperature-axis fits the largest measured coverage is T_max/Tc = 0.6944, and
not one fit reaches 0.77. The exponent being evaluated there was never
validated there.

It also reaches a reported number. The median 95% interval over the emitted set
is 0.8248 dex; over the targets inside the window it is 0.6117 and over those
outside it 1.2061. The width quoted to the referees was inflated by about a
third by targets that Fig. 5 shades as out-of-window in the same document.

The gate. A prediction is refused when its reduced temperature is at or above
T_MAX_REDUCED. Per target, not per compound, which is the convention every
other refusal code here uses. As with the field gate the refused value is moved
into a withheld_ column rather than deleted, so the dispatch emits nothing
while what the model would have produced stays auditable.

    python analysis/apply_temperature_window_gate.py --dry-run
    python analysis/apply_temperature_window_gate.py

Run from the repository root.
"""
import argparse
import os
import shutil
import sys

import pandas as pd

DATA = "data"
PRED = os.path.join(DATA, "phase_3_p57_de_novo_predictions.csv")
AUDIT = os.path.join("audit", "temperature_window_gate.csv")
BETA_T = os.path.join(DATA, "phase_3_p44_post_UCLA_beta_T_fits.csv")

T_MAX_REDUCED = 0.7
CODE = "T_above_validated_reduced_temperature"

VALUE_COLS = ["predicted_log_Jc", "predicted_log_Jc_lower_95",
              "predicted_log_Jc_upper_95"]
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
    t_red = d.T_K / d.Tc_anchor_K

    # The bound is only meaningful if the denominator is. A missing, zero or
    # below-measurement Tc would make t_red silently wrong rather than absent,
    # so it is checked before anything is refused on it.
    bad = d.Tc_anchor_K.isna() | (d.Tc_anchor_K <= 0)
    if bad.any():
        sys.exit("%d row(s) carry no usable Tc anchor; refusing to gate on a "
                 "reduced temperature that cannot be formed" % int(bad.sum()))

    fires = (d.refusal_flag == "") & t_red.notna() & (t_red >= T_MAX_REDUCED)
    already = (d.refusal_flag == CODE).sum()
    before = d[d.refusal_flag == ""]

    print("temperature-axis applicability gate, T/Tc < %.2f%s\n"
          % (T_MAX_REDUCED, "   (DRY RUN)" if args.dry_run else ""))
    print("   tuples in the dispatch table            %5d" % len(d))
    print("   non-refused before the gate             %5d" % len(before))
    print("   refused, reduced temperature >= %.2f    %5d"
          % (T_MAX_REDUCED, fires.sum()))
    print("   already carried the window code         %5d" % already)
    print("   non-refused after the gate              %5d"
          % (len(before) - fires.sum()))

    # What the deposit can actually support, printed rather than asserted in a
    # comment, because it is the reason the gate is at 0.7 and not higher.
    bt = pd.read_csv(BETA_T)
    cover = (bt.T_max / bt.Tc_K)
    print("\n   deposited temperature-axis fits         %5d" % len(bt))
    print("   largest measured T_max/Tc               %.4f" % cover.max())
    print("   fits reaching the 0.77 grid point       %5d"
          % int((cover >= 0.77).sum()))

    surv = d[(d.refusal_flag == "") & ~fires]
    print("\n   compounds keeping a target              %5d"
          % surv.compound_formula.nunique())
    for fam, s in surv.groupby("substructure"):
        print("      %-24s %3d compounds, %d targets, T %s"
              % (fam, s.compound_formula.nunique(), len(s),
                 "%.3f-%.3f K" % (s.T_K.min(), s.T_K.max())))

    def med(sel):
        w = (d.loc[sel, "predicted_log_Jc_upper_95"]
             - d.loc[sel, "predicted_log_Jc_lower_95"]).dropna()
        return w.median() if len(w) else float("nan")

    print("\n   median 95%% interval, before the gate    %.4f dex"
          % med(d.refusal_flag == ""))
    print("   median 95%% interval, refused here       %.4f dex" % med(fires))
    print("   median 95%% interval, after the gate     %.4f dex"
          % med((d.refusal_flag == "") & ~fires))

    if args.dry_run:
        print("\nnothing was written.")
        return

    if not os.path.exists(PRED + ".pre_temperature_gate"):
        shutil.copy2(PRED, PRED + ".pre_temperature_gate")
    for src, dst in WITHHELD_COLS.items():
        if dst not in d.columns:
            d[dst] = pd.NA
        d.loc[fires, dst] = d.loc[fires, src]
    if "withheld_reduced_temperature" not in d.columns:
        d["withheld_reduced_temperature"] = pd.NA
    d.loc[fires, "withheld_reduced_temperature"] = t_red[fires]
    d["withheld_reduced_temperature"] = pd.to_numeric(
        d["withheld_reduced_temperature"], errors="coerce")
    d.loc[fires, VALUE_COLS] = pd.NA
    d.loc[fires, "refusal_flag"] = CODE
    d.to_csv(PRED, index=False)

    os.makedirs("audit", exist_ok=True)
    rep = d[d.refusal_flag == CODE][
        ["compound_formula", "substructure", "Tc_anchor_K", "Hc2_T_anchor",
         "T_K", "H_T", "withheld_reduced_temperature", "refusal_flag",
         "withheld_log_Jc", "withheld_log_Jc_lower_95",
         "withheld_log_Jc_upper_95"]]
    # Same idempotence trap the field gate hit: a second run fires on nothing
    # and would replace a full record with an empty file. Selecting on the code
    # rather than on `fires` keeps the record complete on a rerun, and the size
    # guard is kept as a second line of defence.
    if len(rep) == 0 and os.path.exists(AUDIT) and os.path.getsize(AUDIT) > 200:
        print("\nwritten: %s  (backup at %s.pre_temperature_gate)"
              % (PRED, PRED))
        print("audit  : %s left unchanged; this run fired on nothing" % AUDIT)
    else:
        rep.to_csv(AUDIT, index=False)
        print("\nwritten: %s  (backup at %s.pre_temperature_gate)"
              % (PRED, PRED))
        print("audit  : %s  (%d refused targets)" % (AUDIT, len(rep)))


if __name__ == "__main__":
    main()
