#!/usr/bin/env python3
"""
external_anchor_count.py

Recomputes the out-of-corpus anchor-count validation behind Fig. 4, including
the confidence intervals, which previously had no generator anywhere.

Two things this fixes.

The K = 3 value was not computed on the cohort the caption names. Fig. 4 and
Sec. III.B described 0.927 as the pooled error "across the three monotonic
cuprates after the non-monotonic compound is refused". It is the pooled error
across all four held-out cuprates, the refused one included, whose own error is
1.623. Pairing it with the three-compound K = 1 value of 1.267 gave a 26.8%
reduction that compares different cohorts, which is the error Sec. III.B
corrects two sentences earlier. On the three monotonic cuprates throughout, the
reduction is 1.267 to 0.694, or 45.2%.

The error bars had no source. manuscript_figure_4.py hardcodes 1.192-2.234 and
0.765-1.094 with the comment that they were "recovered from the pipeline's own
artwork and cross-checked against the text". No script in the workflow computes
them and no deposited table contains them. They are recomputed here as a
percentile bootstrap over held-out measurement points, 5000 iterations at a
fixed seed, and the prediction files they are computed from are deposited
alongside so the interval can be checked rather than trusted.

The statistic is the mean absolute error in log10 Jc over held-out points,
pooled by compound first so that a compound with more points does not dominate,
which is what reproduces the deposited 1.592 and 1.267.

    python analysis/external_anchor_count.py
    python analysis/external_anchor_count.py --json out.json

Run from the repository root.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

DIR = os.path.join("data", "external_validation")
NON_MONOTONIC = "Tl-1223_pure"
ITERS, SEED = 5000, 20260902


def load(name):
    d = pd.read_csv(os.path.join(DIR, name))
    d["abs_err"] = (d.predicted_log_Jc - d.actual_log_Jc).abs()
    return d


def mae(d):
    """Mean over compounds of each compound's mean absolute error."""
    return float(d.groupby("compound").abs_err.mean().mean())


def boot(d, iters=ITERS, seed=SEED):
    """Percentile interval, resampling compounds and then points within them."""
    rng = np.random.default_rng(seed)
    comps = sorted(d.compound.unique())
    by = {c: d[d.compound == c].abs_err.values for c in comps}
    draws = np.empty(iters)
    for i in range(iters):
        pick = rng.choice(comps, size=len(comps), replace=True)
        draws[i] = np.mean([by[c][rng.integers(0, len(by[c]), len(by[c]))].mean()
                            for c in pick])
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    k1, k3 = load("predictions_all.csv"), load("predictions_k3.csv")
    mono = lambda d: d[d.compound != NON_MONOTONIC]

    rows = []
    for label, d in [("K=1, all four", k1), ("K=1, three monotonic", mono(k1)),
                     ("K=3, all four", k3), ("K=3, three monotonic", mono(k3))]:
        lo, hi = boot(d)
        rows.append(dict(cohort=label, n_compounds=d.compound.nunique(),
                         n_points=len(d), mae=mae(d), ci_lo=lo, ci_hi=hi))
    out = pd.DataFrame(rows)

    print("out-of-corpus anchor-count validation\n")
    print("   %-24s %5s %7s %8s   %s" % ("cohort", "cmpd", "points", "MAE", "95% interval"))
    for _i, r in out.iterrows():
        print("   %-24s %5d %7d %8.4f   [%.3f, %.3f]"
              % (r.cohort, r.n_compounds, r.n_points, r.mae, r.ci_lo, r.ci_hi))
    m = {r.cohort: r.mae for _i, r in out.iterrows()}
    print("\n   per compound at K=3:")
    for c, v in k3.groupby("compound").abs_err.mean().sort_values().items():
        print("      %-24s %.4f%s" % (c, v, "   refused, non-monotonic"
                                      if c == NON_MONOTONIC else ""))
    a, b = m["K=1, three monotonic"], m["K=3, three monotonic"]
    print("\n   matched three-compound reduction   %.3f to %.3f, %.1f%%"
          % (a, b, 100 * (a - b) / a))
    a4, b4 = m["K=1, all four"], m["K=3, all four"]
    print("   unmatched four-compound pair       %.3f to %.3f, %.1f%%   (not carried)"
          % (a4, b4, 100 * (a4 - b4) / a4))
    print("\n   deposited caption values 1.592 and 1.267 reproduce: %s"
          % ("yes" if abs(a4 - 1.592) < 5e-4 and abs(a - 1.267) < 5e-4 else "NO"))

    os.makedirs("audit", exist_ok=True)
    out.to_csv(os.path.join("audit", "external_anchor_count.csv"), index=False)
    print("written to audit/external_anchor_count.csv")
    if args.json:
        json.dump(out.to_dict("records"), open(args.json, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
