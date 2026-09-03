#!/usr/bin/env python3
"""
isotherm_head_test.py

Tests whether the lowest-field value of each isotherm in a record is a round
number, and whether those values across isotherms form an exact arithmetic or
geometric sequence.

Why this test and not the others. The screen in audit_extraction_integrity.py
looks inside a series: equal steps along the field axis, one series a constant
offset from another, values on a coarse grid. It does not look across the
isotherms of a record at the single quantity a person fabricating a plausible
family of curves has to choose first, which is where each curve starts. Two
signatures live there and neither survives a reading of a figure:

  round heads      the zero-field or lowest-field value of every isotherm is a
                   one- or two-significant-figure number. A digitiser reading a
                   log axis returns 5.072e5, 4.366e5, 3.795e5; a generated family
                   returns 1e6, 9e5, 8e5.

  head ladder      those values form an exact arithmetic or geometric sequence.
                   Real isotherm spacing is set by the temperature dependence of
                   the pinning, which is neither linear nor a fixed ratio in the
                   isotherm index.

This test is cheap, needs no source PDF, and separates the two extraction routes
in this corpus completely, which none of the other signatures do.

Result on this corpus, recorded in audit/isotherm_head_test.csv:

  beta_T source (agent2_dataset_v3_2_1.csv, iron rows)
      40 testable papers, 40 with round heads or a ladder, 0 irregular
      25 of those are exact ladders: 23 arithmetic, 2 geometric

  Cohort B, vision route
      19 testable files, 15 with round heads or a ladder, 4 irregular

  Cohort B, named route
      7 testable files, 7 irregular, none with round heads

The separation is total between the beta_T source and the named route, and no
other signature in the deposit's screen separates them at all.

The direct confirmation is 2012.13723, the one figure re-extracted by
measurement. Its deposited 4 K isotherm is 1e6, 8e5, 6e5, 5e5, 4e5, 3e5, 2e5,
1.5e5 and its isotherm heads step by exactly 1e5. The figure starts at
2.2e6, which the paper also states in its text, and falls to about 5e5.

    python analysis/isotherm_head_test.py --dir <folder of long-format CSVs>
    python analysis/isotherm_head_test.py --wide <agent2_dataset_v3_2_1.csv>
"""
import argparse
import csv
import glob
import math
import os
from collections import defaultdict


def sig_figs(v):
    if v <= 0:
        return 9
    e = math.floor(math.log10(v))
    m = v / 10 ** e
    for k in range(1, 7):
        if abs(m - round(m, k - 1)) < 1e-9:
            return k
    return 9


def heads_of(points_by_T):
    """Lowest-field Jc of each isotherm, highest first."""
    out = []
    for t in sorted(points_by_T):
        v = sorted(points_by_T[t])
        if v:
            out.append(v[0][1])
    return sorted(out, reverse=True)


def classify(heads):
    """Round heads, an arithmetic ladder, or a geometric one.

    The geometric case was added after the arithmetic test alone graded
    1502.05345 as irregular on heads of 1e6, 5e5, 2.5e5, 1.25e5, 6.25e4, which
    is an exact halving. A generated family is as likely to be built by
    repeated scaling as by repeated subtraction, and only the second leaves
    equal differences.
    """
    if len(heads) < 2:
        return dict(n_isotherms=len(heads), round_heads=None, ladder=None,
                    ladder_kind="", verdict="too few isotherms")
    rnd = all(sig_figs(h) <= 2 for h in heads)
    lad, kind = False, ""
    if len(heads) >= 3:
        d = [round(heads[i] - heads[i + 1], 6) for i in range(len(heads) - 1)]
        if len(set(d)) == 1 and d[0] != 0:
            lad, kind = True, "arithmetic"
        else:
            q = [round(heads[i + 1] / heads[i], 6) for i in range(len(heads) - 1)
                 if heads[i] > 0]
            if len(q) == len(heads) - 1 and len(set(q)) == 1 and q[0] not in (0, 1):
                lad, kind = True, "geometric"
    verdict = ("LADDER (%s)" % kind) if lad else ("round heads" if rnd else "irregular")
    return dict(n_isotherms=len(heads), round_heads=rnd, ladder=lad,
                ladder_kind=kind, verdict=verdict)


def group_long(rows):
    g = defaultdict(list)
    for r in rows:
        try:
            j = float(r["Jc_A_per_cm2"]); t = float(r["temperature_K"]); h = float(r["field_T"])
        except (TypeError, ValueError, KeyError):
            continue
        if j > 0:
            g[t].append((h, j))
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", help="folder of long-format per-paper CSVs")
    ap.add_argument("--wide", help="a single CSV with pdf_name/temperature_K/field_T/Jc columns")
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    results = []
    if args.dir:
        for p in sorted(glob.glob(os.path.join(args.dir, "*.csv"))):
            rows = list(csv.DictReader(open(p, newline="")))
            if not rows or "Jc_A_per_cm2" not in rows[0]:
                continue
            h = heads_of(group_long(rows))
            r = classify(h)
            r["record"] = os.path.basename(p)
            r["heads"] = " ".join("%.4g" % x for x in h[:8])
            results.append(r)
    if args.wide:
        rows = list(csv.DictReader(open(args.wide, newline="")))
        jc = "Jc" if rows and "Jc" in rows[0] else "Jc_A_per_cm2"
        by = defaultdict(list)
        for r in rows:
            try:
                if float(r.get("stoich_Fe", 1)) <= 0:
                    continue
                by[r["pdf_name"]].append(r)
            except (TypeError, ValueError):
                continue
        for name, rs in sorted(by.items()):
            g = defaultdict(list)
            for r in rs:
                try:
                    j = float(r[jc]); t = float(r["temperature_K"]); h = float(r["field_T"])
                except (TypeError, ValueError):
                    continue
                if j > 0:
                    g[t].append((h, j))
            h = heads_of(g)
            res = classify(h)
            res["record"] = name
            res["heads"] = " ".join("%.4g" % x for x in h[:8])
            results.append(res)

    cols = ["record", "n_isotherms", "round_heads", "ladder", "ladder_kind", "verdict", "heads"]
    print("%-46s %4s %-14s %s" % ("record", "iso", "verdict", "heads"))
    for r in results:
        print("%-46s %4s %-14s %s" % (r["record"][:46], r["n_isotherms"], r["verdict"], r["heads"][:52]))
    n = len(results)
    lad = sum(1 for r in results if r["ladder"])
    rnd = sum(1 for r in results if r["round_heads"])
    print("\n%d records: %d with round heads, %d forming an exact ladder" % (n, rnd, lad))

    if args.csv:
        os.makedirs(os.path.dirname(args.csv) or ".", exist_ok=True)
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows([{k: r.get(k) for k in cols} for r in results])
        print("written to %s" % args.csv)


if __name__ == "__main__":
    main()
