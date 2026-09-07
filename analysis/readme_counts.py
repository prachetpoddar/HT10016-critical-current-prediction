#!/usr/bin/env python3
"""
readme_counts.py

Prints the count tables README.md carries, computed from the deposit.

Why this exists. The README shipped through several revisions quoting counts
from a cohort that no longer existed: 107 anchor rows against 96, 71 physical
samples against 60, 2151 dispatch rows against 2097, 239 candidate records
against 233, two withdrawn records against eleven papers, and variance ratios
of 0.73, 0.60 and 0.12 that reproduce from no cohort in the deposit. It also
named two figure generators that are not in the repository. A reader following
it would have concluded the deposit was broken.

Nothing in the README is now typed by hand. Run this and paste, or diff it
against the file:

    python3 analysis/readme_counts.py
    python3 analysis/readme_counts.py --check README.md

--check exits non-zero if any line this prints is absent from the README, which
is what stops it going stale again.

Run from the repository root.
"""
import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figure_4_source import aggregate_per_physical_sample  # noqa: E402

DATA = "data"


def rows(name):
    return len(pd.read_csv(os.path.join(DATA, name)))


def lines():
    dep = pd.read_csv(os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv"))
    rep = pd.read_csv(os.path.join(
        DATA, "phase_3_p31_jc_anchor_per_paper_repaired.csv"))
    kept = rep[rep.withdrawn.isna()]
    bt = pd.read_csv(os.path.join(
        DATA, "phase_3_p44_post_UCLA_beta_T_fits_repaired.csv"))
    import numpy as np
    bt_ok = bt[bt.reproduced & np.isfinite(bt.beta_T_repaired)]
    prot = pd.read_csv(os.path.join("audit", "fit_protocol_applied.csv"))
    prov = pd.read_csv(os.path.join(DATA, "provenance_table_fitcohort_full.csv"))
    live = prov[prov.contributes != "none, withdrawn"]
    dn = pd.read_csv(os.path.join(
        DATA, "phase_3_p57_de_novo_predictions.csv"))
    emitted = dn[dn.refusal_flag.isna()]

    out = ["| quantity | value |", "|---|---:|"]

    def row(label, value):
        out.append("| %s | %s |" % (label, value))

    row("source papers contributing fitted curves", len(
        live[~live.second_identifier_for_the_same_paper.astype(bool)]))
    row("distinct compound labels", live.compound.nunique())
    row("extracted critical-current points",
        int(pd.to_numeric(live.n_Jc_points, errors="coerce").sum()))
    row("temperature-axis fits", len(bt_ok))
    row("field-axis fits passing physicality", int(prot.admitted.sum()))
    row("field-axis source papers", int(prot[prot.admitted].paper.nunique()))
    row("per-paper anchor rows, as deposited", len(dep))
    row("per-paper anchor rows, after repair", len(kept))
    row("physical samples behind Fig. 3, after repair",
        len(aggregate_per_physical_sample(kept)))
    row("source papers behind Fig. 3, after repair",
        aggregate_per_physical_sample(kept).paper_id.nunique())
    row("candidate records evaluated", len(dn) // 9)
    row("distinct candidate compounds", dn.compound_formula.nunique())
    row("compounds receiving a dispatched target",
        emitted.compound_formula.nunique())
    row("prediction targets emitted", len(emitted))
    row("prediction targets refused", len(dn) - len(emitted))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", metavar="README")
    args = ap.parse_args()
    body = lines()
    if not args.check:
        print("\n".join(body))
        return 0
    text = open(args.check, encoding="utf-8").read()
    missing = [ln for ln in body if ln not in text]
    for ln in body:
        print("   %-3s %s" % ("ok" if ln in text else "MISS", ln))
    if missing:
        print("\n%d line(s) in %s do not match the deposit"
              % (len(missing), args.check))
        return 1
    print("\nevery count in %s matches the deposit" % args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
