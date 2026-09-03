#!/usr/bin/env python3
"""Rebuild supplement Table S1 from the deposited provenance table.

The table was static, so it still described a 69-paper cohort. Every column is
recomputed here from provenance_table_fitcohort_full.csv, and the row labels and
column order are kept exactly as the supplement prints them so the replacement
drops straight in.

    python analysis/rebuild_supplement_table_s1.py
"""
import collections
import csv
import os

SRC = os.path.join("data", "provenance_table_fitcohort_full.csv")
LABEL = {
    "iron_chalcogenide_11": "Iron chalcogenide 11",
    "iron_pnictide_111": "Iron pnictide 111",
    "iron_pnictide_1111": "Iron pnictide 1111",
    "iron_pnictide_122": "Iron pnictide 122",
    "iron_other": "Iron other",
    "conventional_AlB2": "Conventional AlB2",
    "conventional_A15": "Conventional A15",
    "cuprate_BSCCO": "Cuprate BSCCO",
    "cuprate_HBCCO": "Cuprate HBCCO",
    "cuprate_LSCO": "Cuprate LSCO",
    "cuprate_RBCO": "Cuprate RBCO",
}
ORDER = list(LABEL)


def main():
    rows = list(csv.DictReader(open(SRC)))
    by = collections.defaultdict(list)
    for r in rows:
        by[r["substructure_family"]].append(r)

    out, tot = [], collections.Counter()
    compounds_all, points_all = set(), 0
    for fam in ORDER:
        g = by.get(fam)
        if not g:
            continue
        n = len(g)
        full = sum(1 for r in g if r["contribution_flag"] == "fully fittable")
        a_only = sum(1 for r in g if r["contribution_flag"].startswith("Cohort A only"))
        b_only = sum(1 for r in g if r["contribution_flag"].startswith("Cohort B only"))
        neither = n - full - a_only - b_only
        cmpds = {r["compound"] for r in g}
        reported = sum(1 for r in g
                       if r["Hc2_provenance"].startswith("Tier_1")
                       or r["Hc2_provenance"].startswith("Tier_2"))
        pts = sum(int(float(r["n_Jc_points"])) for r in g if r["n_Jc_points"].strip())
        out.append([LABEL[fam], n, full, a_only, b_only, neither,
                    len(cmpds), reported, pts])
        tot["n"] += n; tot["full"] += full; tot["a"] += a_only
        tot["b"] += b_only; tot["neither"] += neither; tot["rep"] += reported
        compounds_all |= cmpds; points_all += pts

    out.append(["TOTAL", tot["n"], tot["full"], tot["a"], tot["b"],
                tot["neither"], len(compounds_all), tot["rep"], points_all])

    head = ["Substructure family", "n papers", "Fully fittable", "Cohort A only",
            "Cohort B only", "Cohort A+B (non-fittable)", "Distinct compounds",
            "Paper-reported Hc2", "Jc points"]
    w = [max(len(str(r[i])) for r in [head] + out) for i in range(len(head))]
    for r in [head] + out:
        print(" | ".join(str(v).ljust(w[i]) for i, v in enumerate(r)))

    print("\nNote: 'Distinct compounds' in the TOTAL row is the count over the "
          "whole cohort, not the sum of the family column, because a compound "
          "can appear in more than one family scope.")


if __name__ == "__main__":
    main()
