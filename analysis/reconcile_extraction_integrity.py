#!/usr/bin/env python3
"""
reconcile_extraction_integrity.py

Reconcile the deposit's own extraction-integrity screen against the cohort
still in the analysis.

audit/extraction_integrity.csv screens 50 extracted point sets for the
signatures of a fabricated or misread figure: arithmetic ladders, quantisation
onto a grid, a series duplicated from another, a series shifted from another,
fields running past the assigned critical scale, non-monotonic Jc. It reaches
FAIL on 15 files and CHECK on 16.

It was never reconciled against the cohort. That is what this does, and the
answer is that most of what it flags is still in the analysis.

Worth stating plainly, because it cost a day to learn: this screen already
names, precisely and in its own vocabulary, defects that were re-derived here
from the publisher PDFs.

    mtphys.2022.100783   FAIL  duplicate_series shifted_series
    physc.2011.05.018    FAIL  arithmetic duplicate_series field_beyond_hc2
                               grid_quantized
    physc.2009.11.051    FAIL  arithmetic grid_quantized shifted_series
    physc.2010.05.048    CHECK field_beyond_hc2, round_fraction 0.05

The first is the polycrystal record that turns out to be a copy of the single
crystal, shifted by one rung of a ladder. The second is the paper that contains
no critical-current-versus-field figure at all. The third is the paper whose
field axis is in kilo-oersted. The fourth is a competent digitisation of a real
figure whose field unit is wrong, which is exactly what a low round fraction
with field_beyond_hc2 describes.

    python3 analysis/reconcile_extraction_integrity.py [--csv]

Run from the repository root. Changes nothing.
"""
import argparse
import os
import re
import sys

import pandas as pd

DATA = "data"
SCREEN = os.path.join("audit", "extraction_integrity.csv")
OUT = os.path.join("audit", "extraction_integrity_reconciled.csv")


def key(s):
    s = str(s)
    for p in ("elsevier_", "springer_", "iop_"):
        s = s.replace(p, "")
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")

    d = pd.read_csv(SCREEN)
    d["paper"] = (d.file.str.replace("_VISION_PASS_LONG.csv", "", regex=False)
                  .str.replace("_PATH_AC", "", regex=False)
                  .str.replace(r"_[A-Za-z0-9].*_LONG\.csv$", "", regex=True)
                  .str.replace(".csv", "", regex=False).map(key))

    a = pd.read_csv(os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv"))
    a["k"] = a.paper_id.map(key)
    f = pd.read_csv(os.path.join(
        DATA, "phase_3_form3_fits_partial_cohortB_v2.csv"))
    f["k"] = f.arxiv_id.map(key)
    w = pd.read_csv(os.path.join("audit", "withdrawn_records.csv"))
    withdrawn = {key(i.replace("/", "_")) for i in w.identifier}

    rows = []
    for _i, r in d[d.verdict.isin(["FAIL", "CHECK"])].iterrows():
        k = r.paper
        anc = int((a.k == k).sum())
        fits = int((f.k == k).sum())
        pas = int(((f.k == k) & (f.physicality == "ok")).sum())
        status = ("withdrawn" if k in withdrawn
                  else "not in the cohort" if anc == 0 and fits == 0
                  else "LIVE")
        rows.append(dict(verdict=r.verdict, paper=k,
                         signatures=r.signatures, n_points=r.n_points,
                         round_fraction=r.round_fraction, anchor_rows=anc,
                         field_axis_fits=fits, passing_fits=pas,
                         status=status))
    t = pd.DataFrame(rows).sort_values(
        ["status", "verdict", "passing_fits"], ascending=[True, True, False])

    pd.set_option("display.width", 220)
    pd.set_option("display.max_colwidth", 52)
    print("the deposit's extraction-integrity screen, against the live cohort\n")
    print(t.to_string(index=False))

    live = t[t.status == "LIVE"]
    print("\n   flagged files still in the analysis: %d of %d"
          % (len(live), len(t)))
    print("      anchor rows        %3d of %d" % (live.anchor_rows.sum(), len(a)))
    print("      field-axis fits    %3d of %d" % (live.field_axis_fits.sum(), len(f)))
    print("      passing fits       %3d of %d"
          % (live.passing_fits.sum(), int((f.physicality == "ok").sum())))
    print("      of those, FAIL     %3d files carrying %d passing fits"
          % ((live.verdict == "FAIL").sum(),
             live.loc[live.verdict == "FAIL", "passing_fits"].sum()))
    print("\n   withdrawn already:   %d" % (t.status == "withdrawn").sum())
    print("   never in the cohort: %d" % (t.status == "not in the cohort").sum())

    if args.csv:
        t.to_csv(OUT, index=False)
        print("\n   written %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
