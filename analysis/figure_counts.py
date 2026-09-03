"""
figure_counts.py

Every count that Figures 1 and 2 print, computed from the deposited tables
rather than typed into the generator.

This module exists because the figures drifted twice. The version embedded in
the manuscript asserted 69 papers, 43 compounds, 4387 points and 110 anchors;
the generator in analysis/ asserted 65, 40, 4247 and 105; the deposit says 62,
38, 4146 and 96. Nothing caught either gap, because analysis/check_documents.py
reads word/document.xml and can never see inside an embedded image.

Two kinds of quantity appear in these figures and they are kept apart here.

FROM_DEPOSIT is recomputed on every run from data/, so a withdrawal moves the
figure the same turn it moves the tables.

UPSTREAM is fixed by a pipeline stage whose own tables are not deposited: the
size of the retrieval corpus, the v3.2.1 fittable-compound cohort, the
vision-pass cache, and the v3.2.2B partial-fit count. These are unaffected by
the anchor-table withdrawals, which is why they are allowed to be constants,
but they are named here rather than buried in a generator so that the next
person can see exactly which numbers have no deposited source.
"""
import os
import pandas as pd

DATA = "data"

UPSTREAM = dict(
    articles_screened=934,          # retrieval corpus, Elsevier + Springer
    fittable_compounds_v321=23,     # 3DSC canonical cohort, v3.2.1
    partial_fits_v322B=175,         # v3.2.2B partial-fit count
    vision_cache_entries=662,       # vision-pass cache size
)

# The family label each substructure key carries in the figures. MgB2 is set
# in mathtext so the 2 subscripts; the others are plain.
FAMILY_LABEL = {
    "conventional_AlB2": r"MgB$_2$-class",
    "iron_chalcogenide_11": "Iron chalcogenide 11-type",
    "iron_pnictide_122": "Iron pnictide 122-type",
    "iron_pnictide_1111": "Iron pnictide 1111-type",
}


def _p(name):
    return os.path.join(DATA, name)


def from_deposit():
    """Recompute every deposit-derived count the figures print."""
    if not os.path.isdir(DATA):
        raise SystemExit("run from the repository root")
    a = pd.read_csv(_p("phase_3_p31_jc_anchor_per_paper.csv"))
    prov = pd.read_csv(_p("provenance_table_fitcohort_full.csv"))
    bt = pd.read_csv(_p("phase_3_p44_post_UCLA_beta_T_fits.csv"))
    fh = pd.read_csv(_p("phase_3_form3_fits_partial_cohortB_v2.csv"))
    p57 = pd.read_csv(_p("phase_3_p57_de_novo_predictions.csv"), low_memory=False)

    emitted = p57[p57.refusal_flag.fillna("") == ""]
    fams = []
    for key, grp in p57.groupby("substructure"):
        total = grp.compound_formula.nunique()
        disp = emitted[emitted.substructure == key].compound_formula.nunique()
        fams.append(dict(key=key, label=FAMILY_LABEL.get(key, key),
                         total=int(total), dispatched=int(disp),
                         refused=int(total - disp)))
    # Largest family last, which is the order the deposited figure drew them.
    fams.sort(key=lambda f: f["total"])

    return dict(
        fitted_curve_papers=int(prov.identifier.nunique()),
        fitted_curve_compounds=int(prov.compound.nunique()),
        extracted_points=int(pd.to_numeric(prov.n_Jc_points,
                                           errors="coerce").sum()),
        temperature_axis_fits=int(len(bt)),
        field_axis_fits_ok=int(len(fh[fh.physicality == "ok"])),
        field_axis_ok_papers=int(fh[fh.physicality == "ok"].arxiv_id.nunique()),
        anchor_rows=int(len(a)),
        anchor_papers=int(a.paper_id.nunique()),
        candidate_compounds=int(p57.compound_formula.nunique()),
        dispatched_compounds=int(emitted.compound_formula.nunique()),
        families=fams,
    )


if __name__ == "__main__":
    d = from_deposit()
    for k, v in d.items():
        if k != "families":
            print("   %-28s %6d" % (k, v))
    print()
    for f in d["families"]:
        print("   %-26s %4d of %4d dispatched" % (f["label"], f["dispatched"],
                                                  f["total"]))
    print()
    for k, v in UPSTREAM.items():
        print("   %-28s %6d   [upstream, no deposited source]" % (k, v))
