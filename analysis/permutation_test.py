#!/usr/bin/env python3
"""
permutation_test.py

Significance of the sample-form variance decomposition against two nulls.

Why two. The statistic is eta2, the fraction of variance in log10_Jc_anchor
explained by sample_form, computed on the per-physical-sample aggregate. The
obvious null shuffles sample_form across records, which asks: given these
records, could this much separation arise by chance? That question is the wrong
one for this cohort, because sample_form is very nearly collinear with the
source paper. Almost every paper contributes exactly one form, so a record-level
shuffle breaks the paper structure as well as the form structure, and any
between-paper variance whatsoever inflates the statistic against it.

The paper-clustered null shuffles the form label between papers, keeping every
record of a paper on one label. It asks the question a reader actually has:
given that forms arrive one paper at a time, is the separation between forms
larger than the separation between papers? That is a much harder test and it is
the honest one.

Both are reported. The naive p-values are kept in the output so that a reader
can see the size of the difference rather than take the choice of null on trust.

    python analysis/permutation_test.py
    python analysis/permutation_test.py --iters 200000 --seed 20260901

Writes audit/permutation_paper_clustered.csv. Run from the repository root.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figure_4_source import aggregate_per_physical_sample  # noqa: E402

ANCHOR = os.path.join("data", "phase_3_p31_jc_anchor_per_paper.csv")
OUT = os.path.join("audit", "permutation_paper_clustered.csv")


def eta2(y, g):
    """Between-group sum of squares over total, population convention."""
    y = np.asarray(y, dtype=float)
    total = ((y - y.mean()) ** 2).sum()
    if total <= 0:
        return np.nan
    between = 0.0
    for lab in np.unique(g):
        m = g == lab
        between += m.sum() * (y[m].mean() - y.mean()) ** 2
    return between / total


def permute(y, forms, papers, iters, rng, clustered):
    """Fraction of shuffles reaching the observed eta2.

    Under the clustered null the unit of exchange is the paper: the multiset of
    per-paper form labels is permuted among papers and every record inherits its
    paper's label. Under the naive null the unit is the record.
    """
    obs = eta2(y, forms)
    if not np.isfinite(obs):
        return np.nan, np.nan
    if clustered:
        uniq, inv = np.unique(papers, return_inverse=True)
        # One label per paper. Where a paper carries several forms its modal
        # label is used, so the permuted labelling stays a paper-level object.
        lab = np.array([pd.Series(forms[inv == i]).mode().iloc[0]
                        for i in range(len(uniq))])
        hits = 0
        for _ in range(iters):
            hits += eta2(y, rng.permutation(lab)[inv]) >= obs - 1e-12
    else:
        f = np.asarray(forms)
        hits = 0
        for _ in range(iters):
            hits += eta2(y, rng.permutation(f)) >= obs - 1e-12
    return obs, hits / iters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260901)
    args = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")

    agg = aggregate_per_physical_sample(pd.read_csv(ANCHOR))
    rng = np.random.default_rng(args.seed)

    rows = []
    scopes = [("aggregate", agg)] + [
        (s, agg[agg.substructure == s]) for s in sorted(agg.substructure.unique())]
    for name, d in scopes:
        if d.sample_form.nunique() < 2:
            rows.append(dict(scope=name, n=len(d), eta2=np.nan,
                             perm_p_naive=np.nan, perm_p_paper_clustered=np.nan))
            continue
        y = d.log10_Jc_anchor.values
        f = d.sample_form.values
        p = d.paper_id.values
        e, p_naive = permute(y, f, p, args.iters, rng, clustered=False)
        _e, p_clu = permute(y, f, p, args.iters, rng, clustered=True)
        rows.append(dict(scope=name, n=len(d), eta2=e,
                         perm_p_naive=p_naive, perm_p_paper_clustered=p_clu))

    out = pd.DataFrame(rows)
    print("%-24s %4s %8s %10s %12s"
          % ("scope", "n", "eta2", "p naive", "p clustered"))
    for _, r in out.iterrows():
        if pd.isna(r.eta2):
            print("%-24s %4d   single sample form" % (r.scope, r.n))
        else:
            print("%-24s %4d %8.4f %10.4f %12.4f"
                  % (r.scope, r.n, r.eta2, r.perm_p_naive,
                     r.perm_p_paper_clustered))
    os.makedirs("audit", exist_ok=True)
    out.to_csv(OUT, index=False)
    print("\nwritten to %s   (%d shuffles, seed %d)" % (OUT, args.iters, args.seed))


if __name__ == "__main__":
    main()
