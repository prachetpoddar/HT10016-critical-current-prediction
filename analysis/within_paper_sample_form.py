#!/usr/bin/env python3
"""
within_paper_sample_form.py

Within-paper robustness check on the sample-form claim, generating Tables S8
and S9 of the Supplemental Material.

Why this exists. The variance decomposition of Sec. III.A attributes 77%, 60%
and 12% of within-family anchor variance to sample form, but sample form is
nearly collinear with source paper: 34 of the 35 papers contributing anchor rows
report a single form. The decomposition therefore cannot separate the form from
the practice of the paper that used it. The one comparison that can, holding the
paper fixed, is reported here.

It is a small check and its size is the finding. Exactly one paper in the cohort
measures two sample forms of the same compound at the same temperature and
field. Six papers measure three or more specimens of one compound in one form at
one condition, differing only in doping or processing. Both are reported, so the
within-paper form contrast can be read against the within-paper processing
spread of the same corpus rather than against nothing.

This is a robustness check, not a model. Nothing here is fitted and nothing
downstream consumes it.

    python analysis/within_paper_sample_form.py
    python analysis/within_paper_sample_form.py --json out.json

Run from the repository root.
"""
import argparse
import json
import os
import sys

import pandas as pd

ANCHORS = os.path.join("data", "phase_3_p31_jc_anchor_per_paper.csv")
MIN_SERIES = 3          # specimens needed before a processing series is reported
KEY = ["paper_id", "compound_formula", "substructure", "T_anchor_K", "H_anchor_T"]


def short(paper_id):
    """The distinctive part of the identifier, matching Tables S4 to S6."""
    return str(paper_id).split("_10.1016_")[-1].split("_10.1007_")[-1]


def matched_forms(a):
    """Papers measuring two sample forms of one compound at one condition."""
    rows = []
    for k, s in a.groupby(KEY):
        if s.sample_form.nunique() < 2:
            continue
        for _i, r in s.iterrows():
            rows.append(dict(paper=short(k[0]), compound=k[1], family=k[2],
                             condition="%.1f K, %.2f T" % (k[3], k[4]),
                             form=r.sample_form, sample=r.sample_id,
                             log_jc="%.3f" % r.log10_Jc_anchor))
        rows.append(dict(paper="", compound="", family="", condition="",
                         form="difference", sample="",
                         log_jc="%.3f" % (s.log10_Jc_anchor.max()
                                          - s.log10_Jc_anchor.min())))
    return rows


def matched_processing(a):
    """Papers measuring several specimens of one compound in one form."""
    rows = []
    for k, s in a.groupby(KEY + ["sample_form"]):
        if len(s) < MIN_SERIES:
            continue
        rows.append(dict(paper=short(k[0]), compound=k[1], family=k[2],
                         form=k[5], condition="%.1f K, %.2f T" % (k[3], k[4]),
                         n=len(s),
                         span="%.3f" % (s.log10_Jc_anchor.max()
                                        - s.log10_Jc_anchor.min()),
                         specimens="; ".join(sorted(s.sample_id.astype(str)))))
    return sorted(rows, key=lambda r: -float(r["span"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    a = pd.read_csv(ANCHORS)

    forms = matched_forms(a)
    proc = matched_processing(a)

    print("Table S8  within-paper sample-form contrast\n")
    if not forms:
        print("   no paper measures two sample forms at one condition")
    for r in forms:
        print("   " + " || ".join(str(v) for v in r.values()))

    print("\nTable S9  within-paper processing series, one form each\n")
    for r in proc:
        print("   " + " || ".join(str(r[k]) for k in
                                  ("paper", "compound", "form", "condition",
                                   "n", "span")))
    spans = sorted(float(r["span"]) for r in proc)
    if spans:
        med = spans[len(spans) // 2] if len(spans) % 2 else \
            0.5 * (spans[len(spans) // 2 - 1] + spans[len(spans) // 2])
        print("\n   %d series, span %.3f to %.3f dex, median %.3f"
              % (len(spans), spans[0], spans[-1], med))
    diffs = [float(r["log_jc"]) for r in forms if r["form"] == "difference"]
    if diffs and spans:
        print("   the %d within-paper form contrast%s: %s dex"
              % (len(diffs), "" if len(diffs) == 1 else "s",
                 ", ".join("%.3f" % d for d in diffs)))
        print("   every processing series in the same corpus is larger than "
              "that contrast" if min(spans) > max(diffs) else
              "   some processing series are smaller than that contrast")

    if args.json:
        with open(args.json, "w") as f:
            json.dump({"S8": forms, "S9": proc}, f, indent=1)
        print("\nwritten to %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
