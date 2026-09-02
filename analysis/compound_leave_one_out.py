#!/usr/bin/env python3
"""
compound_leave_one_out.py

Regenerates the compound-level leave-one-out validation on both axes: the
field-axis table phase_3_p47_compound_leave_out_MAE.csv behind Table III, and
the temperature-axis figures of Sec. III.C with their paper-level bootstrap.

Why this exists. Neither result had a generator. Both were static numbers, so
they never propagated through any correction, and a stale validation figure is
indistinguishable from a current one.

Protocols, recovered by reproducing the deposited values, and asserted below
against the pre-withdrawal snapshot rather than described in prose.

  Temperature axis. Hold out each compound in turn; predict its fits by the
  median beta_T of the remaining fits in the family. Statistic: mean absolute
  error over fits.

  Field axis. Same held-out compound; predict each held-out fit by the median
  beta of the remaining fits sharing its sample form, falling back to the family
  median where that form is unrepresented. Cohort: physicality == "ok".

Three things this script deliberately does NOT do, each because doing them
produced a wrong number here first.

  It does not compare against the file it writes. DEPOSITED below pins the
  values as they stood before any regeneration. An earlier version read the
  comparison column out of phase_3_p47_compound_leave_out_MAE.csv and then
  overwrote that file, so a second run reported the unreproduced 1111 row as
  matching the deposit exactly.

  It no longer preserves a row it cannot reproduce. An earlier version carried
  the deposited iron_pnictide_1111 field-axis value of 3.0656 through unchanged
  because this protocol returns 3.1289. Keeping a number the deposited code
  does not produce is exactly the defect a provenance paper cannot ship, so the
  generator's value is now written and the deposited one is recorded below as
  history. The same applies to the per-paper Stage 2 validation, whose original
  97-fit cohort cannot be rebuilt from the deposited fit file: it is recomputed
  on the cohort that does exist rather than quoted from one that does not.

  It does not report a single bootstrap fraction. Resamples are stratified by
  how many distinct compounds survive, because the strata are not equivalent: a
  two-compound resample predicts a held-out compound from one other compound.
  For iron_pnictide_1111 that stratum supplies most of the resamples that clear
  the threshold, so a pooled fraction is carried by its weakest stratum.

The anchor-count gate. Sec. II.D says "at least K = 3 anchor compounds are
available within the family". At dispatch the candidate is outside the fitted
family so the sentence is unambiguous, and no dispatched family is near the
bound, which is why no implementation of it exists to consult. In a
leave-one-out the held-out compound is inside the family and the sentence is
ambiguous: gating on the family (n >= 3) and gating on the anchors actually
available to that prediction (n - 1 >= 3) differ, and they differ on three of
the seven family-axis pairs. Both are reported. The manuscript has to say which
it means; this script will not choose.

    python analysis/compound_leave_one_out.py --dry-run
    python analysis/compound_leave_one_out.py --reproduce   # assert on the snapshot
    python analysis/compound_leave_one_out.py

Run from the repository root.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

DATA = "data"
SNAPSHOT = os.path.join("audit", "pre_withdrawal_20260901")
OUT_H = os.path.join(DATA, "phase_3_p47_compound_leave_out_MAE.csv")
OUT_T = os.path.join("audit", "temperature_axis_leave_one_out.csv")
OUT_G = os.path.join("audit", "leave_one_out_anchor_gate.csv")
OUT_P = os.path.join("audit", "per_paper_field_validation.csv")

FAMILIES_H = ["conventional_AlB2", "iron_chalcogenide_11",
              "iron_pnictide_1111", "iron_pnictide_122"]
FAMILIES_T = ["iron_chalcogenide_11", "iron_pnictide_122", "iron_pnictide_1111"]

THRESHOLD = 1.0

# The deposited values, pinned. Never read back from a file this script writes.
DEPOSITED_H = {
    "conventional_AlB2": (0.7531793918356584, 0.5560610162687745),
    "iron_chalcogenide_11": (0.641180745621664, 0.665794874844566),
    "iron_pnictide_1111": (3.065635459082229, 1.0623191444845497),
    "iron_pnictide_122": (0.9728593350331054, 0.8665239049136337),
}
DEPOSITED_T = {"iron_chalcogenide_11": 0.261, "iron_pnictide_122": 1.092,
               "iron_pnictide_1111": 1.721}

# Values the deposit carried before this generator existed, kept only so the
# printout can show what changed. Nothing is written from them.
SUPERSEDED_H = {"iron_pnictide_1111": 3.065635459082229}


def load(base):
    bt = pd.read_csv(os.path.join(base, "phase_3_p44_post_UCLA_beta_T_fits.csv"))
    f = pd.read_csv(os.path.join(base, "phase_3_form3_fits_partial_cohortB_v2.csv"))
    a = pd.read_csv(os.path.join(base, "phase_3_p31_jc_anchor_per_paper.csv"))
    fmap = a.drop_duplicates("paper_id").set_index("paper_id").substructure.to_dict()
    f = f.copy()
    f["substructure"] = f.arxiv_id.map(fmap)
    ok = f[f.physicality == "ok"]
    unmapped = ok.substructure.isna().sum()
    if unmapped:
        # An "ok" fit whose paper is absent from the anchor table would drop out
        # of every family silently, so it is surfaced rather than filtered.
        print("   warning: %d field-axis 'ok' fits have no family label" % unmapped)
    return bt, ok


def per_paper_validation(f, iters, seed):
    """Leave-one-paper-out on the field exponent, with a percentile bootstrap.

    The supplement previously quoted 0.994 with a 95% interval of [0.495, 1.661]
    on a cohort described as 97 fits. The deposited fit file yields 88 fits that
    pass physicality, and no filter over it reconstructs 97, so that figure is
    not quoted any more. This recomputes the same quantity on the cohort the
    deposit actually contains.
    """
    res = []
    for p in f.arxiv_id.unique():
        train = f[f.arxiv_id != p]
        test = f[f.arxiv_id == p]
        if train.empty:
            continue
        res.extend((test.beta - train.beta.median()).abs().values)
    res = np.asarray(res, dtype=float)
    rng = np.random.default_rng(seed)
    draws = res[rng.integers(0, len(res), size=(iters, len(res)))].mean(axis=1)
    return (float(res.mean()), float(np.percentile(draws, 2.5)),
            float(np.percentile(draws, 97.5)), len(f), f.arxiv_id.nunique())


def loo(s, col, form_conditioned, min_train_compounds=0):
    """Mean and median absolute error, each compound held out in turn.

    min_train_compounds implements the anchor-count gate on the pool actually
    available to each prediction. 0 disables it. Folds below the bound are
    refused, not scored.
    """
    res, folds, refused = [], 0, 0
    for c in s.compound_formula.unique():
        train = s[s.compound_formula != c]
        test = s[s.compound_formula == c]
        if train.empty or train.compound_formula.nunique() < min_train_compounds:
            refused += 1
            continue
        folds += 1
        for _, row in test.iterrows():
            if form_conditioned:
                same = train[train.sample_form == row.sample_form]
                pool = same[col] if len(same) else train[col]
            else:
                pool = train[col]
            res.append(abs(row[col] - pool.median()))
    if not res:
        return np.nan, np.nan, folds, refused
    return float(np.mean(res)), float(np.median(res)), folds, refused


def bootstrap(s, col, iters, seed):
    """Paper-level resampling, stratified by how many compounds survive.

    A pooled fraction hides that the strata are not comparable, so the strata
    are returned and the caller reports them. Degenerate strata are named: a
    stratum whose resamples are all the same multiset carries one observation
    however many times it is drawn.
    """
    papers = s.paper_id.unique()
    rng = np.random.default_rng(seed)
    by = {p: s[s.paper_id == p] for p in papers}
    strata = {}
    for _ in range(iters):
        pick = tuple(sorted(rng.choice(papers, len(papers), replace=True)))
        d = pd.concat([by[p] for p in pick])
        k = d.compound_formula.nunique()
        st = strata.setdefault(k, dict(n=0, hits=0, multisets=set()))
        st["n"] += 1
        st["multisets"].add(pick)
        if k < 2:
            continue
        m, _md, folds, _r = loo(d, col, False)
        if folds:
            st["hits"] += m < THRESHOLD
    return strata


def report_bootstrap(name, strata, total):
    parts = []
    for k in sorted(strata):
        st = strata[k]
        if k < 2:
            parts.append("%d cmpd: %d unscorable" % (k, st["n"]))
            continue
        tag = ""
        if len(st["multisets"]) == 1:
            tag = " degenerate, one distinct resample"
        parts.append("%d cmpd: %d/%d (%.0f%%)%s"
                     % (k, st["hits"], st["n"], 100 * st["hits"] / st["n"], tag))
    scor = sum(st["n"] for k, st in strata.items() if k >= 2)
    hits = sum(st["hits"] for k, st in strata.items() if k >= 2)
    print("      %-22s pooled %.0f%% of %d scorable   [%s]"
          % (name, 100 * hits / scor if scor else float("nan"), scor,
             "; ".join(parts)))
    return hits / scor if scor else np.nan


def run(base, iters, seed, verbose=True):
    bt, f = load(base)
    out = dict(temperature={}, field={}, gate=[])
    if verbose:
        print("temperature axis, substructure-median predictor\n")
    for name in FAMILIES_T:
        s = bt[bt.substructure == name]
        if s.empty:
            continue
        mae, med, _fo, _r = loo(s, "beta_T", False)
        strata = bootstrap(s, "beta_T", iters, seed)
        if verbose:
            print("   %-22s %d compounds, %d papers, %d fits   MAE %.4f"
                  % (name, s.compound_formula.nunique(), s.paper_id.nunique(),
                     len(s), mae))
        frac = report_bootstrap("bootstrap", strata, iters) if verbose else np.nan
        out["temperature"][name] = (mae, med, frac, strata)
    if verbose:
        print("\nfield axis, sample-form-conditioned predictor\n")
        print("   %-22s %5s %5s %9s %10s   %s"
              % ("substructure", "cmpd", "fits", "MAE", "median", "deposited"))
    for name in FAMILIES_H:
        s = f[f.substructure == name]
        if s.empty:
            continue
        mae, med, _fo, _r = loo(s, "beta", True)
        out["field"][name] = (mae, med, s.compound_formula.nunique(), len(s))
        if verbose:
            dep = DEPOSITED_H.get(name, (float("nan"),))[0]
            note = "   supersedes the deposited %.4f" % SUPERSEDED_H[name] \
                if name in SUPERSEDED_H else ""
            print("   %-22s %5d %5d %9.4f %10.4f   %9.4f%s"
                  % (name, s.compound_formula.nunique(), len(s), mae, med,
                     dep, note))

    mae_p, lo_p, hi_p, nfit, npap = per_paper_validation(f, 5000, seed)
    out["per_paper"] = (mae_p, lo_p, hi_p, nfit, npap)
    if verbose:
        print("\nper-paper leave-one-out on the field exponent\n")
        print("   %d fits from %d papers   MAE %.3f   95%% interval [%.3f, %.3f]"
              % (nfit, npap, mae_p, lo_p, hi_p))

    # Both readings of the anchor-count gate.
    if verbose:
        print("\nanchor-count gate, both readings of Sec. II.D\n")
        print("   %-22s %-4s %-4s %14s %16s"
              % ("substructure", "axis", "n", "gate on family", "gate on anchors"))
    for axis, d, col, fc in [("T", bt, "beta_T", False), ("H", f, "beta", True)]:
        for name in sorted(set(d.substructure.dropna())):
            s = d[d.substructure == name]
            n = s.compound_formula.nunique()
            if n < 2:
                continue
            a_fam, _m, fo_fam, _r = loo(s, col, fc, min_train_compounds=2)
            a_anc, _m, fo_anc, _r = loo(s, col, fc, min_train_compounds=3)
            out["gate"].append(dict(
                axis=axis, substructure=name, n_compounds=n,
                gate_on_family=a_fam if fo_fam else np.nan,
                gate_on_available_anchors=a_anc if fo_anc else np.nan,
                refused_on_family=fo_fam == 0,
                refused_on_available_anchors=fo_anc == 0))
            if verbose:
                print("   %-22s %-4s %-4d %14s %16s"
                      % (name, axis, n,
                         "%.4f" % a_fam if fo_fam else "refused",
                         "%.4f" % a_anc if fo_anc else "refused"))
    return out


def reproduce():
    """Assert the documented protocol against the pre-withdrawal snapshot."""
    if not os.path.isdir(SNAPSHOT):
        sys.exit("snapshot %s not present" % SNAPSHOT)
    print("asserting the protocol against %s\n" % SNAPSHOT)
    r = run(SNAPSHOT, iters=2000, seed=20260901, verbose=False)
    bad = []
    for name, (dep, dep_med) in DEPOSITED_H.items():
        got, got_med = r["field"][name][0], r["field"][name][1]
        exact = abs(got - dep) < 1e-9 and abs(got_med - dep_med) < 1e-9
        expected = name not in SUPERSEDED_H
        print("   field  %-22s %.10f vs %.10f   %s"
              % (name, got, dep, "exact" if exact else "DIFFERS"))
        if exact != expected:
            bad.append("field %s" % name)
    for name, dep in DEPOSITED_T.items():
        got = r["temperature"][name][0]
        ok = abs(got - dep) < 5e-4
        print("   temp   %-22s %.4f vs %.3f   %s"
              % (name, got, dep, "matches" if ok else "DIFFERS"))
        if not ok:
            bad.append("temperature %s" % name)
    if bad:
        print("\nreproduction FAILED for: %s" % ", ".join(bad))
        return 1
    print("\nevery documented reproduction claim holds on the pre-withdrawal "
          "snapshot; the one superseded row still differs, which is why the "
          "generator's value is what ships.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reproduce", action="store_true")
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260901)
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")
    if args.reproduce:
        return reproduce()

    r = run(DATA, args.iters, args.seed)
    if args.dry_run:
        print("\nnothing was written.")
        return 0

    hrows = []
    for name in FAMILIES_H:
        if name not in r["field"]:
            continue
        mae, med, nc, nf = r["field"][name]
        hrows.append(dict(substructure=name, n_compounds=nc, n_fits=nf,
                          compound_loo_mae=mae, compound_loo_median_residual=med))
    pd.DataFrame(hrows).to_csv(OUT_H, index=False)

    trows = []
    for name, (mae, med, frac, strata) in r["temperature"].items():
        for k in sorted(strata):
            st = strata[k]
            trows.append(dict(
                substructure=name, resample_n_compounds=k, n_resamples=st["n"],
                n_below_threshold=st["hits"], distinct_resamples=len(st["multisets"]),
                degenerate=len(st["multisets"]) == 1, loo_mae_point_estimate=mae,
                loo_median_residual=med))
    pd.DataFrame(trows).to_csv(OUT_T, index=False)
    pd.DataFrame(r["gate"]).to_csv(OUT_G, index=False)
    m, lo, hi, nf, np_ = r["per_paper"]
    pd.DataFrame([dict(statistic="per_paper_leave_one_out_beta_H", n_fits=nf,
                       n_papers=np_, mae=m, ci_lower_95=lo, ci_upper_95=hi,
                       bootstrap_iterations=5000, seed=args.seed)]).to_csv(OUT_P, index=False)
    print("\nwritten to %s, %s, %s and %s" % (OUT_H, OUT_T, OUT_G, OUT_P))
    return 0


if __name__ == "__main__":
    sys.exit(main())
