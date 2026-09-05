#!/usr/bin/env python3
"""
apply_provenance_status.py

Bring the provenance table into line with the withdrawals, without deleting a
row.

The problem. `data/provenance_table_fitcohort_full.csv` is the cohort
definition: 62 rows, one per paper the deposit says contributes. Eleven of those
papers were withdrawn on 2026-09-03, each with a citation, the figure checked
and a reason, in `audit/withdrawn_beta_T_papers.csv`. The provenance table was
never updated, so it still lists them, and it still flags them "fully fittable".

That is not only bookkeeping. `analysis/verify_deposit.py` computes the
manuscript's printed counts from this table:

    fitted curve papers    = prov.identifier.nunique()
    fitted curve compounds = prov.compound.nunique()
    extracted points       = sum of prov.n_Jc_points

so the manuscript's 62 papers, 38 compounds and 4146 extracted points are
pre-withdrawal counts.

What this does. It adds three columns and corrects one, and deletes nothing:

    status                 contributing, withdrawn, or duplicate_identifier
    withdrawn_on           the date, for a withdrawn row
    withdrawn_reason_ref   where the reason is written down
    contributes            what the row ACTUALLY produces, replacing the
                           aspirational "fully fittable"

The original flag is preserved as `contribution_flag_original`, because it is
what the manuscript was written against and a reader has to be able to see it.

    python3 analysis/apply_provenance_status.py --check
    python3 analysis/apply_provenance_status.py --apply

Run from the repository root. --apply snapshots the table into
audit/pre_provenance_status_20260905/ first, and refuses to overwrite an
existing snapshot.
"""
import os
import re
import shutil
import sys

import numpy as np
import pandas as pd

PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
FITS_B = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_A = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
WITHDRAWN_A = os.path.join("audit", "withdrawn_beta_T_papers.csv")
DUPES = os.path.join("audit", "duplicate_papers.csv")
SNAP = os.path.join("audit", "pre_provenance_status_20260905")


def squash(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def main():
    mode = "--apply" if "--apply" in sys.argv else "--check"
    prov = pd.read_csv(PROV)
    wa = pd.read_csv(WITHDRAWN_A)
    dup = pd.read_csv(DUPES)
    fb = pd.read_csv(FITS_B)
    fa = pd.read_csv(FITS_A)

    wmap = {squash(r.paper_id).replace("pdf", ""): r for _, r in wa.iterrows()}
    dup_ids = set()
    for c in ("field_axis_id", "temperature_axis_id"):
        if c in dup.columns:
            dup_ids |= {squash(v) for v in dup[c].astype(str)}
    dup_primary = {squash(v) for v in dup.paper_key.astype(str)}

    def match(ident, keys):
        q = squash(ident)
        return [k for k in keys if q == squash(k) or q in squash(k)]

    kb = fb.paper_key.astype(str).unique()
    ka = fa.paper_key.astype(str).unique()
    # a paper's field fits may be filed under its other identifier
    kb_ax = fb.arxiv_id.astype(str).unique() if "arxiv_id" in fb.columns else []

    rows = []
    for _, r in prov.iterrows():
        i = str(r.identifier)
        q = squash(i)
        hit = None
        for k, w in wmap.items():
            if k and (q == k or q in k or k in q):
                hit = w
                break
        nb = len(fb[fb.paper_key.isin(match(i, kb))])
        if not nb and "arxiv_id" in fb.columns:
            nb = len(fb[fb.arxiv_id.astype(str).isin(match(i, kb_ax))])
        na = len(fa[fa.paper_key.isin(match(i, ka))])
        second = False
        if hit is not None:
            status = "withdrawn"
            contributes = "none, withdrawn"
        # substring, not exact: the duplicate ledger spells the field-axis id
        # with its 'elsevier_' prefix and the provenance table does not, so an
        # equality test never fired and the row was counted as contributing
        # alongside the paper it duplicates
        elif (any(q and q in x for x in dup_ids)
              and not any(q and q in x for x in dup_primary)):
            # still contributing: this row is a real extraction of a real
            # paper. It is a SECOND identifier for a paper another row also
            # names, so it counts for points and not for papers.
            status = "contributing"
            second = True
            m = dup[dup.field_axis_id.astype(str).map(squash).str.contains(q)]
            contributes = ("the same paper as " + str(m.paper_key.iloc[0])
                           if len(m) else "duplicate identifier")
        else:
            status = "contributing"
            second = False
            contributes = ("both axes" if nb and na else
                           "field axis only" if nb else
                           "temperature axis only" if na else
                           "no fit in either table")
        rows.append(dict(
            status=status,
            withdrawn_on=(hit.withdrawn if hit is not None else ""),
            withdrawn_reason_ref=("audit/withdrawn_beta_T_papers.csv"
                                  if hit is not None else ""),
            contributes=contributes,
            second_identifier_for_the_same_paper=second,
            field_fits=nb, temperature_fits=na))
    add = pd.DataFrame(rows, index=prov.index)
    out = prov.copy()
    out["contribution_flag_original"] = out.contribution_flag
    for c in add.columns:
        out[c] = add[c]

    n = out.status.value_counts()
    con = out[out.status == "contributing"]
    pts = pd.to_numeric(out.n_Jc_points, errors="coerce")
    print("status of the 62 provenance rows")
    print(n.to_string())
    print()
    print("what the rows actually contribute")
    print(out.contributes.value_counts().to_string())
    print()
    print("the counts the manuscript prints, computed both ways")
    print(f"{'quantity':26s} {'as printed':>12} {'contributing only':>19}")
    print(f"{'fitted curve papers':26s} {out.identifier.nunique():12d} "
          f"{con.identifier.nunique():19d}")
    print(f"{'fitted curve compounds':26s} {out.compound.nunique():12d} "
          f"{con.compound.nunique():19d}")
    print(f"{'extracted points':26s} {int(pts.sum()):12d} "
          f"{int(pd.to_numeric(con.n_Jc_points, errors='coerce').sum()):19d}")
    print()
    dupn = int(con.second_identifier_for_the_same_paper.sum())
    print(f"  the {len(con)} contributing rows describe "
          f"{len(con) - dupn} distinct papers: {dupn} of them is a second "
          f"identifier for a paper another row already names, one row per axis. "
          f"Its points are real and counted; its paper is not counted twice.")
    print()
    print("rows whose original flag was 'fully fittable' and which contribute:")
    ff = out[out.contribution_flag_original == "fully fittable"]
    print(ff.contributes.value_counts().to_string())
    print()

    if mode == "--check":
        print("--check: nothing written. Re-run with --apply.")
        return 0
    if os.path.isdir(SNAP):
        print(f"{SNAP} already exists; the pre-status copy is kept and this "
              f"run will not overwrite it")
    else:
        os.makedirs(SNAP)
        shutil.copy2(PROV, os.path.join(SNAP, os.path.basename(PROV)))
    out.to_csv(PROV, index=False)
    print(f"snapshot: {SNAP}")
    print(f"written:  {PROV}  ({len(out)} rows, none deleted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
