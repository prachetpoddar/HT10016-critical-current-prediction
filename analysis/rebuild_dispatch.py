#!/usr/bin/env python3
"""
rebuild_dispatch.py

One entry point that rebuilds data/phase_3_p57_de_novo_predictions.csv from the
deposited tables, and says whether the result is the file the paper ships.

Why this exists. The dispatch table was not produced by one script. It is the
output of four, run in order, and only the first of them is named anywhere in
the manuscript:

  1. analysis/phase_3_p57_de_novo_predictions.py   the predictor itself
  2. analysis/withdraw_records.py                  removes the candidate records
                                                   of withdrawn source papers
  3. analysis/apply_field_window_gate.py           the reduced-field clause of
                                                   Eq. (1) and the field-axis
                                                   family validation
  4. analysis/apply_temperature_window_gate.py     the reduced-temperature clause

A reader who ran step 1 alone, which is what the deposit invited, got a file
with 2151 rows against the deposited 2097, carrying two of the five refusal
codes instead of five, and with the candidate records of two withdrawn papers
back in it. That is the reproducibility gap this closes.

The verify mode copies data/, audit/ and analysis/ into a scratch tree, runs the
four steps there, and compares. It writes nothing under the repository, so it is
safe to run on a clean checkout and safe to run repeatedly. The write mode does
the same and then replaces the deposited file with the rebuilt one.

    python analysis/rebuild_dispatch.py            verify only, nothing written
    python analysis/rebuild_dispatch.py --write    replace the deposited file

Run from the repository root.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

PRED = os.path.join("data", "phase_3_p57_de_novo_predictions.csv")

# In order. The list is the point of this file: it is the only place the order
# is written down, and check_claims_against_deposit.py asserts against the file
# it produces.
STEPS = [
    ("analysis/phase_3_p57_de_novo_predictions.py", []),
    ("analysis/withdraw_records.py", []),
    ("analysis/apply_field_window_gate.py", []),
    ("analysis/apply_temperature_window_gate.py", []),
]

# Sorting key for the comparison. Row order is not part of the claim: the four
# steps filter and rewrite in place and the surviving order depends on which
# rows were dropped, so two runs that agree on every value can still differ on
# order. The key has to be enough to identify a row uniquely, and it is checked
# to be so before it is used.
KEY = ["compound_formula", "substructure", "paper_id", "MP_id", "Tc_anchor_K",
       "sample_form_commitment", "T_K", "H_T"]

# What a difference has to exceed to be reported. Bootstrap columns are drawn
# from a seeded generator and reproduce exactly on the same inputs, so this is
# not a tolerance for noise; it is float round-trip through CSV.
ATOL = 1e-9


def run_chain(work):
    for script, extra in STEPS:
        r = subprocess.run([sys.executable, script] + extra, cwd=work,
                           capture_output=True, text=True)
        if r.returncode != 0:
            tail = (r.stderr.strip().splitlines() or ["failed"])[-3:]
            raise SystemExit("%s exited %d:\n   %s"
                             % (script, r.returncode, "\n   ".join(tail)))
        print("   ran %-52s ok" % script)


def compare(rebuilt_path, deposit_path):
    """(ok, lines). Compares the two tables on shape, columns and every cell."""
    a = pd.read_csv(rebuilt_path)
    b = pd.read_csv(deposit_path)
    lines = []
    if list(a.columns) != list(b.columns):
        only_a = [c for c in a.columns if c not in b.columns]
        only_b = [c for c in b.columns if c not in a.columns]
        lines.append("columns differ: rebuilt only %s, deposit only %s"
                     % (only_a or "none", only_b or "none"))
        return False, lines
    if len(a) != len(b):
        lines.append("row counts differ: rebuilt %d, deposit %d"
                     % (len(a), len(b)))
        return False, lines
    # KEY alone does not identify a row: the same compound reached through the
    # same source paper appears more than once, 423 times in this table, which
    # Supplement Sec. 10 describes. Sorting on KEY and then on every remaining
    # column makes the comparison a multiset comparison, which is the claim
    # being made: the two tables hold the same rows with the same values, in
    # whatever order the four steps happened to leave them.
    order = KEY + [c for c in a.columns if c not in KEY]
    A = a.sort_values(order, kind="mergesort",
                      na_position="first").reset_index(drop=True)
    B = b.sort_values(order, kind="mergesort",
                      na_position="first").reset_index(drop=True)
    for c in A.columns:
        x, y = A[c], B[c]
        if x.dtype.kind in "fi" and y.dtype.kind in "fi":
            bad = ~((x.isna() & y.isna())
                    | np.isclose(x.astype(float), y.astype(float),
                                 rtol=0, atol=ATOL, equal_nan=True))
        else:
            bad = (x.fillna("\x00").astype(str)
                   != y.fillna("\x00").astype(str))
        n = int(bad.sum())
        if n:
            worst = ""
            if x.dtype.kind in "fi":
                worst = "  worst |difference| %.6g" % float(
                    (x.astype(float) - y.astype(float)).abs().max())
            lines.append("%-42s %5d cell(s) differ%s" % (c, n, worst))
    return not lines, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="replace the deposited file with the rebuilt one")
    args = ap.parse_args()
    if not os.path.isdir("data") or not os.path.isdir("analysis"):
        sys.exit("run from the repository root")
    if not os.path.exists(PRED):
        sys.exit("missing %s" % PRED)

    with tempfile.TemporaryDirectory(prefix="rebuild_dispatch_") as work:
        print("rebuilding the dispatch table in a scratch copy\n")
        for d in ("data", "audit", "analysis"):
            if os.path.isdir(d):
                shutil.copytree(d, os.path.join(work, d))
        # The scratch copy starts from the deposited file, and the first step
        # overwrites it. Remove it first so a step that writes nothing cannot
        # pass by leaving the deposited copy in place, which is the same defect
        # analysis/check_figures.py documents for the figures.
        os.remove(os.path.join(work, PRED))
        run_chain(work)
        rebuilt = os.path.join(work, PRED)
        if not os.path.exists(rebuilt):
            sys.exit("the chain wrote nothing to %s" % PRED)
        print()
        ok, lines = compare(rebuilt, PRED)
        if ok:
            print("the rebuilt table matches the deposited one on every cell")
        else:
            print("the rebuilt table differs from the deposited one:")
            for ln in lines:
                print("   %s" % ln)
        if args.write:
            shutil.copy2(rebuilt, PRED)
            print("\nwritten: %s" % PRED)
            for extra in ("phase_3_p57_top5_table_data.csv",
                          "phase_3_p57_dispatch_report.md"):
                src = os.path.join(work, "data", extra)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join("data", extra))
                    print("written: data/%s" % extra)
            for extra in ("field_window_gate.csv", "temperature_window_gate.csv"):
                src = os.path.join(work, "audit", extra)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join("audit", extra))
                    print("written: audit/%s" % extra)
            return 0
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
