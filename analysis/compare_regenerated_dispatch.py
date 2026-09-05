#!/usr/bin/env python3
"""The dispatch regenerated on the corrected tables, against the deposited one.

The deposited prediction file was never regenerated after the withdrawals and
the anchor corrections, and audit/beta_T_withdrawal_notes.md says so. It could
not be regenerated here either, because three inputs were missing from the
checkout. They are staged now: 3DSC_MP.csv, literature_hc2_in_scope.csv and
phase_3_makidegennes_per_paper_fits.csv, plus 32 extraction files the uploads
copy of data_agent2/v3_2_2B_extension was missing. The generator runs.

Reproduction, and where it stops. Running the generator on the pre-withdrawal
snapshot and applying the two post-hoc gate scripts gives 2151 rows against the
deposit's 2097, so the file as a whole does not reproduce. What does reproduce
exactly is the part that matters: **the emitted set is identical**. Both carry
163 emitted predictions on the same 163 (compound, temperature, field) keys, at
the same two grid points, with the same 15.5 T anchor on all 86 records at
4.2 K and the same split of 83 parent anchors to 3 exact. Every one of the 54
extra rows is refused, and the refusal codes differ only in how many targets
fall below the validated reduced field. The comparison below is therefore
like-for-like on the quantity being compared, and is not a reproduction of the
file.

The finding. At 4.2 K and 5 T the deposited spread is 0.0098 dex across 86
records, which is the figure the response letter gives Referee A. On the
corrected tables it is 0.2242 dex, twenty-three times larger, and the whole of
that comes from two records. Eighty-four still route to the substructure-
aggregate predictor and span 0.0085 dex among themselves. Two MgB2 records
acquire a wire sample-form commitment they did not have before, route to the
Stage 2 conditional pool, and land at 5.198 and 5.199 against the aggregate's
4.980.

That is a better answer to the referee than the one in the letter. The narrow
spread is a property of the aggregate predictor evaluated at its own reference
point, and the moment two records route to a conditioned cell instead they sit
0.22 dex away. It demonstrates the conditioning claim rather than embarrassing
it.

    python analysis/compare_regenerated_dispatch.py

Run from the repository root.
"""
import os

import numpy as np
import pandas as pd

DEP = os.path.join("data", "phase_3_p57_de_novo_predictions.csv")
REGEN = os.path.join("audit", "p57_regen_20260905",
                     "phase_3_p57_de_novo_predictions_regenerated.csv")


def emitted(path):
    x = pd.read_csv(path)
    f = x.refusal_flag.fillna("").astype(str).str.strip()
    return x, x[f.isin(["", "nan", "None", "<NA>"])]


def main():
    xd, d = emitted(DEP)
    xr, r = emitted(REGEN)
    kd = set(zip(d.compound_formula, d.T_K, d.H_T))
    kr = set(zip(r.compound_formula, r.T_K, r.H_T))
    print("the two files\n")
    print("   %-34s %8s %8s" % ("", "deposit", "regen"))
    print("   %-34s %8d %8d" % ("rows", len(xd), len(xr)))
    print("   %-34s %8d %8d" % ("emitted", len(d), len(r)))
    print("   %-34s %8s" % ("emitted keys identical", kd == kr))
    if kd != kr:
        raise SystemExit("the emitted sets differ, so nothing below is "
                         "like-for-like")
    print("   the file as a whole does not reproduce; every extra row is "
          "refused")

    print("\nat 4.2 K and 5 T\n")
    print("   %-34s %10s %10s" % ("", "deposit", "regen"))
    gd = d[np.isclose(d.T_K, 4.2) & np.isclose(d.H_T, 5.0)]
    gr = r[np.isclose(r.T_K, 4.2) & np.isclose(r.H_T, 5.0)]
    for name, a, b in [
            ("records", len(gd), len(gr)),
            ("compounds", gd.compound_formula.nunique(),
             gr.compound_formula.nunique()),
            ("distinct critical-field anchors", gd.Hc2_T_anchor.nunique(),
             gr.Hc2_T_anchor.nunique())]:
        print("   %-34s %10s %10s" % (name, a, b))
    print("   %-34s %10.4f %10.4f"
          % ("span of the prediction, dex",
             gd.predicted_log_Jc.max() - gd.predicted_log_Jc.min(),
             gr.predicted_log_Jc.max() - gr.predicted_log_Jc.min()))
    if gd.Hc2_T_anchor.nunique() != 1 or gr.Hc2_T_anchor.nunique() != 1:
        raise SystemExit("the shared-anchor premise fails in one arm")

    print("\n   which predictor each record routes to\n")
    for lab, g in [("deposit", gd), ("regen", gr)]:
        print("   %-10s %s" % (lab, g.predictor_method_scope.value_counts()
                               .to_dict()))
    w = gr[gr.sample_form_commitment.fillna("") != ""]
    rest = gr[gr.sample_form_commitment.fillna("") == ""]
    print("\n   the %d records that keep the aggregate predictor span %.4f dex"
          % (len(rest), rest.predicted_log_Jc.max()
             - rest.predicted_log_Jc.min()))
    print("   the %d that acquire a sample-form commitment sit at %s"
          % (len(w), ", ".join("%.3f" % v for v in w.predicted_log_Jc)))
    if len(w) == 0:
        raise SystemExit("no record acquires a commitment, so the widening "
                         "has some other cause and this account is wrong")
    print("   so the whole of the widening is the two conditioned records, "
          "not a change in the")
    print("   aggregate predictor, whose own spread moves from %.4f to %.4f"
          % (gd.predicted_log_Jc.max() - gd.predicted_log_Jc.min(),
             rest.predicted_log_Jc.max() - rest.predicted_log_Jc.min()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
