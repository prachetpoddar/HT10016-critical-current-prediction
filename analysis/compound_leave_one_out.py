#!/usr/bin/env python3
"""
compound_leave_one_out.py

Regenerates the compound-level leave-one-out validation on both axes: the
field-axis table phase_3_p47_compound_leave_out_MAE.csv reported in Table III,
and the temperature-axis figures reported in Sec. III.C, including the
paper-level bootstrap.

Why this exists. Neither result had a generator in the deposit. Both were
static numbers, so when records were withdrawn they kept describing the cohort
that produced them. That is the propagation defect this deposit has already
documented twice, and it is worse here than in a count, because a stale
validation number is indistinguishable from a current one.

Protocols, recovered by reproducing the deposited values.

  Temperature axis. Each compound in a family is held out in turn and its fits
  are predicted by the median beta_T of the remaining fits in that family.
  Statistic: mean absolute error over fits. Confidence: 2000 resamples of the
  contributing papers with replacement, reporting the fraction of resamples
  whose leave-one-out error falls below the screening threshold of 1 in the
  exponent. Resamples that leave fewer than two compounds cannot support a
  leave-one-out and are counted separately rather than scored.

  Field axis. Same held-out compound, but the predictor is the median beta of
  the remaining fits sharing the held-out fit's sample form, falling back to the
  family median where that form is unrepresented. Cohort: fits whose physicality
  flag is "ok".

Reproduction status against the deposited numbers, on the pre-withdrawal data:

  temperature axis   0.2609 / 1.0922 / 1.7211   against 0.261 / 1.092 / 1.721
  bootstrap          91% / 38% / 9%             against 92% / 38% / 8%
  field axis         AlB2 0.7532, chalcogenide 0.6412, 122 0.9729   exact
  field axis 1111    3.1289 against the deposited 3.0656

The 1111 field-axis row is the one protocol not reproduced. That family has
three compounds and eleven fits and the manuscript evaluates it at two scopes,
so the deposited value was probably produced under the second. The difference
is reported rather than tuned away, and the 1111 field-axis figure should not
be described as reproducible from this deposit until it is resolved.

    python analysis/compound_leave_one_out.py --dry-run
    python analysis/compound_leave_one_out.py

Run from the repository root.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

FITS_H = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_T = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
ANCHOR = os.path.join("data", "phase_3_p31_jc_anchor_per_paper.csv")
OUT_H = os.path.join("data", "phase_3_p47_compound_leave_out_MAE.csv")
OUT_T = os.path.join("audit", "temperature_axis_leave_one_out.csv")

FAMILIES_H = ["conventional_AlB2", "iron_chalcogenide_11",
              "iron_pnictide_1111", "iron_pnictide_122"]
FAMILIES_T = ["iron_chalcogenide_11", "iron_pnictide_122", "iron_pnictide_1111"]

THRESHOLD = 1.0
UNRESOLVED_H = {"iron_pnictide_1111"}


def loo(s, col, form_conditioned):
    res = []
    for c in s.compound_formula.unique():
        train = s[s.compound_formula != c]
        test = s[s.compound_formula == c]
        if train.empty:
            continue
        for _, row in test.iterrows():
            if form_conditioned:
                same = train[train.sample_form == row.sample_form]
                pool = same[col] if len(same) else train[col]
            else:
                pool = train[col]
            res.append(abs(row[col] - pool.median()))
    if not res:
        return np.nan, np.nan
    return float(np.mean(res)), float(np.median(res))


def bootstrap(s, col, iters, seed):
    """Fraction of paper-level resamples whose leave-one-out error clears the
    screening threshold, and how many resamples were too degenerate to score."""
    papers = s.paper_id.unique()
    rng = np.random.default_rng(seed)
    by_paper = {p: s[s.paper_id == p] for p in papers}
    hits = valid = degenerate = 0
    for _ in range(iters):
        d = pd.concat([by_paper[p] for p in rng.choice(papers, len(papers),
                                                       replace=True)])
        if d.compound_formula.nunique() < 2:
            degenerate += 1
            continue
        valid += 1
        m, _md = loo(d, col, form_conditioned=False)
        hits += m < THRESHOLD
    return (hits / valid if valid else np.nan), valid, degenerate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260901)
    args = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")

    a = pd.read_csv(ANCHOR)
    fam = a.drop_duplicates("paper_id").set_index("paper_id").substructure.to_dict()

    # Temperature axis.
    bt = pd.read_csv(FITS_T)
    trows = []
    print("temperature axis, substructure-median predictor\n")
    print("%-22s %5s %5s %8s %10s %s"
          % ("substructure", "cmpd", "fits", "MAE", "below thr", "papers"))
    for name in FAMILIES_T:
        s = bt[bt.substructure == name]
        if s.empty:
            continue
        mae, med = loo(s, "beta_T", form_conditioned=False)
        frac, valid, degen = bootstrap(s, "beta_T", args.iters, args.seed)
        trows.append(dict(axis="temperature", substructure=name,
                          n_compounds=s.compound_formula.nunique(),
                          n_fits=len(s), n_papers=s.paper_id.nunique(),
                          loo_mae=mae, loo_median_residual=med,
                          frac_bootstrap_below_threshold=frac,
                          bootstrap_valid=valid, bootstrap_degenerate=degen))
        print("%-22s %5d %5d %8.4f %9.0f%% %6d"
              % (name, s.compound_formula.nunique(), len(s), mae,
                 100 * frac, s.paper_id.nunique()))

    # Field axis.
    f = pd.read_csv(FITS_H)
    f["substructure"] = f.arxiv_id.map(fam)
    f = f[f.physicality == "ok"]
    old = pd.read_csv(OUT_H) if os.path.exists(OUT_H) else None
    hrows = []
    print("\nfield axis, sample-form-conditioned predictor\n")
    print("%-22s %5s %5s %8s %10s   %s"
          % ("substructure", "cmpd", "fits", "MAE", "median", "deposited"))
    for name in FAMILIES_H:
        s = f[f.substructure == name]
        if s.empty:
            continue
        mae, med = loo(s, "beta", form_conditioned=True)
        hrows.append(dict(substructure=name,
                          n_compounds=s.compound_formula.nunique(),
                          n_fits=len(s), compound_loo_mae=mae,
                          compound_loo_median_residual=med))
        prev = ""
        if old is not None:
            m = old[old.substructure == name]
            if len(m):
                prev = "%.4f" % m.iloc[0].compound_loo_mae
        note = "   protocol not reproduced" if name in UNRESOLVED_H else ""
        print("%-22s %5d %5d %8.4f %10.4f   %9s%s"
              % (name, s.compound_formula.nunique(), len(s), mae, med,
                 prev or "none", note))

    if args.dry_run:
        print("\nnothing was written.")
        return
    pd.DataFrame(hrows).to_csv(OUT_H, index=False)
    os.makedirs("audit", exist_ok=True)
    pd.DataFrame(trows).to_csv(OUT_T, index=False)
    print("\nwritten to %s and %s" % (OUT_H, OUT_T))


if __name__ == "__main__":
    main()
