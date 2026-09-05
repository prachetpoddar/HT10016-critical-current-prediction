#!/usr/bin/env python3
"""
manuscript_numbers_repaired.py

Table I as published, Table I repaired, and the mapping between them.

The decision this serves. The repaired cohort is reported as primary and the
deposited one is kept in the supplement, with a row-by-row mapping, so that the
cohort shrinking from 94 field-axis fits to 52 is something a reader can follow
rather than something they have to accept.

Every repaired number below traces to a script in this repository, named in the
`from` column. Nothing here is a new measurement.

    python3 analysis/manuscript_numbers_repaired.py

Run from the repository root. Writes audit/manuscript_numbers_repaired.csv and
audit/supplement_fit_disposition.csv.
"""
import os
import re
import sys

import numpy as np
import pandas as pd

DATA = "data"
PROV = os.path.join(DATA, "provenance_table_fitcohort_full.csv")
ANCHOR = os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv")
FITS_B = os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_B_REP = FITS_B.replace(".csv", "_repaired.csv")
FITS_A_REP = os.path.join(DATA, "phase_3_p44_post_UCLA_beta_T_fits_repaired.csv")
PRED = os.path.join(DATA, "phase_3_p57_de_novo_predictions.csv")
APPLIED = os.path.join("audit", "fit_protocol_applied.csv")
PRINTED = os.path.join("audit", "manuscript_printed_counts.csv")
OUT = os.path.join("audit", "manuscript_numbers_repaired.csv")
OUT_MAP = os.path.join("audit", "supplement_fit_disposition.csv")


def main():
    printed = pd.read_csv(PRINTED).set_index("quantity")
    prov = pd.read_csv(PROV)
    con = prov[prov.status == "contributing"] if "status" in prov.columns else prov
    dupn = int(con.get("second_identifier_for_the_same_paper",
                       pd.Series(dtype=bool)).sum())
    anchor = pd.read_csv(ANCHOR)
    fa = pd.read_csv(FITS_A_REP)
    ap = pd.read_csv(APPLIED)
    adm = ap[ap.admitted & ap.was_passing]
    pred = pd.read_csv(PRED, low_memory=False)

    rows = [
        dict(quantity="fitted curve papers", published=62,
             repaired=len(con) - dupn,
             frm="provenance table, status == contributing, one paper counted "
                 "once where two identifiers name it"),
        dict(quantity="fitted curve compounds", published=38,
             repaired=con.compound.nunique(),
             frm="the same rows"),
        dict(quantity="extracted points", published=4146,
             repaired=int(pd.to_numeric(con.n_Jc_points, errors="coerce").sum()),
             frm="the same rows; both extractions of the duplicated paper count"),
        dict(quantity="temperature-axis partial fits", published=260,
             repaired=int((fa.reproduced & np.isfinite(fa.beta_T_repaired)).sum()),
             frm="apply_anchor_repairs.py; three of the 260 are not refitted, "
                 "two whose paper has no rows in the extraction and one whose "
                 "deposited rule was never reproduced"),
        dict(quantity="field-axis partial fits passing", published=94,
             repaired=len(adm),
             frm="fit_protocol.py --report, on the cohort apply_anchor_repairs.py "
                 "leaves"),
        dict(quantity="field-axis source papers", published=16,
             repaired=adm.paper.nunique(), frm="the same"),
        dict(quantity="per-paper anchors behind Fig. 3", published=96,
             repaired=len(anchor),
             frm="unchanged: no withdrawn paper appears in the anchor table"),
        dict(quantity="candidate compounds evaluated", published=183,
             repaired=pred.compound_formula.nunique(),
             frm="unchanged: the prediction side is untouched by the anchor repair"),
    ]
    t = pd.DataFrame(rows)
    t["moves"] = t.published != t.repaired
    os.makedirs("audit", exist_ok=True)
    t.to_csv(OUT, index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 78)
    print("=" * 78)
    print("TABLE I, AS PUBLISHED AND REPAIRED")
    print("=" * 78)
    print(t[["quantity", "published", "repaired", "moves"]].to_string(index=False))
    print()
    print("where each repaired number comes from")
    for _, r in t.iterrows():
        print(f"  {r.quantity:32s} {r.frm}")
    print()
    print(f"  {int(t.moves.sum())} of the {len(t)} printed quantities move; "
          f"{len(t) - int(t.moves.sum())} do not")
    print()

    # ---- the supplement's mapping table
    fb = pd.read_csv(FITS_B)
    rep = pd.read_csv(FITS_B_REP)
    passing = fb[(fb.ok == True) & (fb.physicality == "ok")].copy()
    key = ["paper_key", "fixed_axis_value", "sample_identifier"]
    withdrawn = rep.set_index(rep.index)["withdrawn"].fillna("")
    passing["withdrawn"] = withdrawn.reindex(passing.index).fillna("")
    ap_key = ap.set_index(["paper", "T"]) if "T" in ap.columns else None

    disp = []
    for i, r in passing.iterrows():
        if str(r.withdrawn) not in ("", "nan"):
            d, why = ("dropped", f"paper withdrawn: {r.withdrawn}")
        else:
            # match on the sample too: physc.2013.04.060 carries eight
            # samples across two temperatures, and matching on (paper,
            # temperature) alone took the first of three and reported eight
            # kept where seven survive
            m = ap[(ap.paper == r.paper_key)
                   & np.isclose(ap["T"], r.fixed_axis_value)
                   & (ap["sample"].astype(str) == str(r.sample_identifier))]
            if not len(m):
                d, why = ("dropped", "the deposited fit rule was not reproduced")
            elif bool(m.admitted.iloc[0]):
                d, why = ("kept", "clears the field clause and the temperature window")
            elif not bool(m.clears_field_clause.iloc[0]):
                d, why = ("dropped", "fails the field clause under the repaired anchor")
            elif not bool(m.in_temperature_window.iloc[0]):
                d, why = ("dropped", "T/Tc above 0.7 under the repaired Tc")
            else:
                d, why = ("dropped", "too few points after the retention floor")
        disp.append(dict(paper=r.paper_key, sample=r.sample_identifier,
                         temperature_K=r.fixed_axis_value,
                         deposited_beta_H=r.beta, disposition=d, reason=why))
    dd = pd.DataFrame(disp)
    dd.to_csv(OUT_MAP, index=False)
    print("=" * 78)
    print("SUPPLEMENT: what became of each of the 94 deposited passing fits")
    print("=" * 78)
    print(dd.groupby(["disposition", "reason"]).size().to_string())
    print()
    print("by paper")
    piv = dd.pivot_table(index="paper", columns="disposition", aggfunc="size",
                         fill_value=0)
    print(piv.to_string())
    print()
    print(f"written: {OUT}")
    print(f"written: {OUT_MAP}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
