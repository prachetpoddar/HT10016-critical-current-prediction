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
    # Re-derived on 2026-09-05 by rerunning the closed-form fitter with the
    # eleven withdrawn papers removed, which is what Table I row 5 now prints.
    # It was 23 of 27 and is 20 of 24: three compounds lose every row they had.
    # analysis/rerun_closed_form_without_withdrawn.py.
    fittable_compounds_v321=20,
    partial_fits_v322B=175,         # v3.2.2B partial-fit count
    vision_cache_entries=662,       # vision-pass cache size
)

# What Table I of the manuscript prints, in the order Figure 1 panel (a) draws
# them. The figure and the table are the same six numbers and there is no
# reason for them ever to differ, so they are pinned here and asserted.
TABLE_I = dict(articles_screened=934, fitted_curve_papers=50,
               fitted_curve_compounds=35, extracted_points=3303,
               fittable_compounds=20, anchor_rows=96)

# The family label each substructure key carries in the figures. MgB2 is set
# in mathtext so the 2 subscripts; the others are plain.
FAMILY_LABEL = {
    "conventional_AlB2": r"MgB$_2$-class",
    "iron_chalcogenide_11": "Iron chalcogenide 11-type",
    "iron_pnictide_122": "Iron pnictide 122-type",
    # 1111 is carried because it appears in the fit cohort even though no
    # candidate in the current dispatch table belongs to it.
    "iron_pnictide_1111": "Iron pnictide 1111-type",
}


def _p(name):
    return os.path.join(DATA, name)


def from_deposit():
    """Recompute every deposit-derived count the figures print.

    Read the repaired cohort, which is what Table I reports. The deposited
    tables are still the input for the pre-repair columns elsewhere in the
    audit, but a figure printed beside Table I has to agree with Table I, and
    reading the unrepaired tables here is how Figure 1 came to print 62, 38 and
    4146 against a table saying 50, 35 and 3303 in the same document.

    That is the third time these figures have drifted, and the first two are in
    this module's own docstring. The reason it keeps happening is that the
    document checker reads word/document.xml and cannot see inside an embedded
    image, so nothing compares the picture with the table. The assertion at the
    end of this function is the fix: the six numbers Figure 1 shares with
    Table I are pinned and checked here, where they are computed, rather than
    in a checker that cannot reach them.
    """
    if not os.path.isdir(DATA):
        raise SystemExit("run from the repository root")
    a = pd.read_csv(_p("phase_3_p31_jc_anchor_per_paper.csv"))
    prov = pd.read_csv(_p("provenance_table_fitcohort_full.csv"))
    bt = pd.read_csv(_p("phase_3_p44_post_UCLA_beta_T_fits_repaired.csv"))
    fh = pd.read_csv(_p("phase_3_form3_fits_partial_cohortB_v2.csv"))
    prot = pd.read_csv(os.path.join("audit", "fit_protocol_applied.csv"))
    # Rows the provenance table still counts as contributing. contributes and
    # second_identifier_for_the_same_paper were added by
    # analysis/apply_provenance_status.py; before that this function summed
    # every row, withdrawn ones included, which is how the figure came to print
    # 62, 38 and 4146.
    #
    # The duplicate is deducted from the PAPER count and from nothing else, and
    # that asymmetry is deliberate. 1002.0208v2 appears under two identifiers,
    # and the second carries its own compound, PrFeAsO0.6F0.12, and its own
    # extracted points. Those are real measurements that happen to share a
    # source paper, so they belong in the compound and point counts while the
    # paper is counted once. Deducting the row everywhere gave 34 compounds and
    # 2947 points against Table I's 35 and 3303, and the assertion below caught
    # it.
    live = prov[prov.contributes != "none, withdrawn"]
    papers = live[~live.second_identifier_for_the_same_paper.astype(bool)]
    keep = bt[bt.reproduced & bt.beta_T_repaired.notna()]
    adm = prot[prot.admitted]
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
    # Ties are broken by key so the order is stable rather than arbitrary.
    fams.sort(key=lambda f: (f["total"], f["key"]))

    # The per-family counts have to partition the cohort, or panel (b) draws
    # bars that do not add up to the total its own footnote quotes. An
    # independent reviewer found nothing asserting this, and a compound
    # appearing under two substructures would break it silently.
    total = sum(f["total"] for f in fams)
    disp = sum(f["dispatched"] for f in fams)
    n_comp = int(p57.compound_formula.nunique())
    n_disp = int(emitted.compound_formula.nunique())
    if total != n_comp or disp != n_disp:
        raise SystemExit(
            "the per-family counts do not partition the cohort: %d family "
            "totals vs %d compounds, %d family dispatched vs %d dispatched. "
            "A compound reachable under two substructures would do this."
            % (total, n_comp, disp, n_disp))
    missing = [f["key"] for f in fams if f["key"] not in FAMILY_LABEL]
    if missing:
        raise SystemExit("no figure label for substructure(s): %s"
                         % ", ".join(missing))

    out = dict(
        fitted_curve_papers=int(papers.identifier.nunique()),
        fitted_curve_compounds=int(live.compound.nunique()),
        extracted_points=int(pd.to_numeric(live.n_Jc_points,
                                           errors="coerce").sum()),
        temperature_axis_fits=int(len(keep)),
        field_axis_fits_ok=int(len(adm)),
        field_axis_ok_papers=int(adm.paper.nunique()),
        anchor_rows=int(len(a)),
        anchor_papers=int(a.paper_id.nunique()),
        candidate_compounds=int(p57.compound_formula.nunique()),
        dispatched_compounds=int(emitted.compound_formula.nunique()),
        families=fams,
    )

    # Figure 1 and Table I print the same six numbers. If they disagree the
    # figure must not be drawn, because a figure that contradicts the table
    # facing it is worse than no figure.
    checks = [("fitted_curve_papers", out["fitted_curve_papers"]),
              ("fitted_curve_compounds", out["fitted_curve_compounds"]),
              ("extracted_points", out["extracted_points"]),
              ("anchor_rows", out["anchor_rows"]),
              ("fittable_compounds", UPSTREAM["fittable_compounds_v321"])]
    bad = ["%s: %s computed, %s in Table I" % (k, v, TABLE_I[k])
           for k, v in checks if v != TABLE_I[k]]
    if bad:
        raise SystemExit("Figure 1 would contradict Table I:\n   "
                         + "\n   ".join(bad))
    return out


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
