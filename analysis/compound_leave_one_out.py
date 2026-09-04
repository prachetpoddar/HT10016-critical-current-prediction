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

  It writes the value this cohort supports, and says what the superseded one
  was computed on. The deposited iron_pnictide_1111 field-axis value of 3.0656
  is not unreproducible, and an earlier version of this docstring said it was.
  It is in phase_3_p50_compound_loo_bootstrap.csv, and it reproduces to every
  digit from the fit table as that table stood before 2026-09-01. What moved it
  to 3.1289 is the three sample_form corrections of that date, two of which land
  in this family: jallcom.2023.170384 from unknown to single_crystal and
  physc.2009.05.098 from thin_film to polycrystal, each read off the source
  paper's own description of its samples. The field-axis predictor conditions on
  sample form, so relabelling two of the family's three compounds changes which
  fits pool together. Both readings exceed the screening threshold, so the
  family's status does not turn on which is quoted; only the number does.

  The same holds for the per-paper Stage 2 validation. Its cohort is 99 fits,
  not the 97 the supplement quoted, and it rebuilds exactly: the 95 physicality-
  ok fits of the pre-correction Cohort B v2 table plus the four FeSe-pure
  field-axis fits added post-AC from jallcom.2024.173999, giving 5 substructures
  and 18 papers. Rebuilt that way it returns 0.9944, which is the deposited
  0.994. It is superseded here because the Nb3Sn withdrawal removed its fifth
  substructure and the sample-form corrections moved the rest, not because it
  could not be found.

  It does not report a single bootstrap fraction. Resamples are stratified by
  how many distinct compounds survive, because the strata are not equivalent: a
  two-compound resample predicts a held-out compound from one other compound.
  For iron_pnictide_1111 that stratum supplies most of the resamples that clear
  the threshold, so a pooled fraction is carried by its weakest stratum.

The anchor-count gate is not a bound on family size, and this script no longer
applies one. Sec. II.D of the manuscript reads "at least K = 3 anchor compounds
are available within the family", and an earlier version of this script took
that literally and refused any family-axis pair with fewer than four compounds.
The implementation says otherwise. kappa_pipeline/predictor/constants.py sets
K_MIN = 1, K_MAX = 5, K_RECOMMENDED = 3, and validators.py enforces those
against len(anchors), where monotonic.py defines an Anchor as a single measured
(temperature_K, field_T, log_Jc) triple for the compound being predicted. K is
therefore the number of measured points supplied with a query, not a count of
compounds in a family, and it places no bound on family size at all. Fig. 4
says the same thing independently: it evaluates K = 3 across three held-out
cuprates, which a family-size reading would forbid. The manuscript sentence is
the error, and it is corrected there. Families are reported against the
screening threshold alone, which is the rule the paper pre-registered.

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
# The fit table as it stood before the three sample_form corrections of
# 2026-09-01. Every deposited field-axis value reproduces from it exactly,
# including the superseded iron_pnictide_1111 3.0656 that reproduces from no
# later snapshot. Keeping it is what turns "that number does not reproduce" into
# "that number was computed on these labels, and here they are".
SNAPSHOT_PRE_FORM = os.path.join("audit", "pre_sample_form_correction_20260901")
# The fit table before the Nb3Sn withdrawal, which is the only snapshot in which
# the Stage 2 per-paper cohort still has its fifth substructure. Together with
# data/phase_3_p54_substep_C_new_form3_fits.csv it rebuilds that cohort exactly.
SNAPSHOT_PRE_NB3SN = os.path.join("audit", "pre_nb3sn_withdrawal_20260901")
STAGE2_COHORT = (99, 18, 5, 86, 0.994)   # fits, papers, substructures, scored, MAE
OUT_H = os.path.join(DATA, "phase_3_p47_compound_leave_out_MAE.csv")
OUT_T = os.path.join("audit", "temperature_axis_leave_one_out.csv")
OUT_G = os.path.join("audit", "leave_one_out_family_size_sensitivity.csv")
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


def per_paper_validation(f, iters, seed, conditioned=True):
    """Leave-one-paper-out on the field exponent, with a percentile bootstrap.

    Two predictors, because they are not the same quantity and an earlier
    revision reported one as the successor of the other.

      conditioned=True   Stage 2 as the paper defines it: predict each held-out
                         fit by the median exponent of the fits from other
                         papers that share its substructure AND its sample form.
                         A fit with no such pool is unscorable and is dropped,
                         which is what the original run did.
      conditioned=False  the pooled predictor: one median over every fit from
                         every other paper, ignoring family and form. Every fit
                         is scorable, so this scores more fits on a weaker rule.

    This matters because the supplement previously replaced a conditioned 0.994
    with a pooled 1.141 and described the second as the first recomputed on a
    new cohort. It is a different predictor as well as a different cohort, and
    comparing the two is the cohort-mismatch error the main text corrects
    elsewhere. On the deposited 88-fit cohort the conditioned predictor gives
    1.053 over the 68 fits it can score and the pooled one gives 1.141 over 88.
    Both are deposited, each labelled with its predictor.
    """
    res = []
    for p in f.arxiv_id.unique():
        train = f[f.arxiv_id != p]
        test = f[f.arxiv_id == p]
        if train.empty:
            continue
        if not conditioned:
            res.extend((test.beta - train.beta.median()).abs().values)
            continue
        for _i, row in test.iterrows():
            pool = train[(train.substructure == row.substructure)
                         & (train.sample_form == row.sample_form)]
            if pool.empty:
                continue
            res.append(abs(row.beta - pool.beta.median()))
    res = np.asarray(res, dtype=float)
    rng = np.random.default_rng(seed)
    draws = res[rng.integers(0, len(res), size=(iters, len(res)))].mean(axis=1)
    return (float(res.mean()), float(np.percentile(draws, 2.5)),
            float(np.percentile(draws, 97.5)), len(res), f.arxiv_id.nunique())


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
        # The same predictor with sample-form conditioning switched off. The
        # manuscript states both, as a contrast, and only the conditioned half
        # was ever written to a file: the unconditioned run existed as a code
        # path and an assertion in analysis/verify_redline_numbers.py and
        # nowhere else, which is why its four values read as unsourced. They
        # are not; they are just undeposited.
        med_mae, med_med, _fo2, _r2 = loo(s, "beta", False)
        out["field"][name] = (mae, med, s.compound_formula.nunique(), len(s),
                              med_mae, med_med)
        if verbose:
            dep = DEPOSITED_H.get(name, (float("nan"),))[0]
            note = "   supersedes the deposited %.4f" % SUPERSEDED_H[name] \
                if name in SUPERSEDED_H else ""
            print("   %-22s %5d %5d %9.4f %10.4f   %9.4f%s"
                  % (name, s.compound_formula.nunique(), len(s), mae, med,
                     dep, note))
    if verbose:
        print("\nfield axis, substructure-median predictor, the contrast the "
              "manuscript states\n")
        print("   %-22s %9s %10s" % ("substructure", "MAE", "median"))
        for name in FAMILIES_H:
            if name in out["field"]:
                print("   %-22s %9.4f %10.4f"
                      % (name, out["field"][name][4], out["field"][name][5]))

    cond = per_paper_validation(f, 5000, seed, conditioned=True)
    pool = per_paper_validation(f, 5000, seed, conditioned=False)
    out["per_paper"] = cond
    out["per_paper_pooled"] = pool
    if verbose:
        print("\nper-paper leave-one-out on the field exponent, %d papers\n"
              % cond[4])
        print("   %-34s %5s %8s   %s" % ("predictor", "fits", "MAE", "95% interval"))
        for label, r in [("Stage 2, substructure and form", cond),
                         ("pooled median, no conditioning", pool)]:
            print("   %-34s %5d %8.4f   [%.3f, %.3f]"
                  % (label, r[3], r[0], r[1], r[2]))
        print("   the two are different predictors; the Stage 2 row is the one "
              "that succeeds the deposited 0.994")

    # Family-size sensitivity. This is NOT the anchor-count rule of Sec. II.D,
    # which counts measured points supplied with a query and bounds nothing
    # here. It answers a different and still fair question: would any family's
    # reported error survive a requirement that its training pool retain two or
    # three distinct compounds? Reported so a reader can see the size of the
    # restriction the paper does not impose.
    if verbose:
        print("\nfamily-size sensitivity, not a rule the paper applies\n")
        print("   %-22s %-4s %-4s %14s %16s"
              % ("substructure", "axis", "n", "train n>=2", "train n>=3"))
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
                mae_train_at_least_2=a_fam if fo_fam else np.nan,
                mae_train_at_least_3=a_anc if fo_anc else np.nan,
                no_fold_at_least_2=fo_fam == 0,
                no_fold_at_least_3=fo_anc == 0))
            if verbose:
                print("   %-22s %-4s %-4d %14s %16s"
                      % (name, axis, n,
                         "%.4f" % a_fam if fo_fam else "refused",
                         "%.4f" % a_anc if fo_anc else "refused"))
    return out


def substructure_from_formula(c):
    """The formula-to-family map the original Path delta run used.

    Kept separate from the paper-id map used elsewhere in this script because it
    is what the superseded Stage 2 cohort was built with, and reconstructing a
    superseded value means using the rule that produced it rather than the rule
    that replaced it.
    """
    c = c or ""
    if "Nb3Sn" in c or "V3Si" in c or "V3Ga" in c:
        return "conventional_A15"
    if "MgB2" in c or "MgB(2-x)Cx" in c:
        return "conventional_AlB2"
    if ("FeTe" in c or "FeSe" in c) and "FeAs" not in c:
        return "iron_chalcogenide_11"
    if "FeAsO" in c:
        return "iron_pnictide_1111"
    if "Fe2As2" in c or "BaFe" in c or "(Fe" in c:
        return "iron_pnictide_122"
    return "other_unclassified"


def reconstruct_stage2():
    """Rebuild the per-paper Stage 2 cohort the supplement previously reported.

    The supplement described that cohort as 97 fits and said no filter over the
    deposited fit file reproduces it. Both statements were wrong. It is 99 fits,
    and it does not come from one file: it is the 95 physicality-passing fits of
    the fit table as it stood before the Nb3Sn withdrawal, plus the four FeSe
    field-axis fits added afterwards, which live in a separate deposited table.
    Looking for it inside the current fit file alone could not have found it.

    Rebuilt this way it gives 5 substructures, 18 papers, 86 scored fits and a
    mean absolute error of 0.9944, which is the reported 0.994. That makes the
    figure superseded rather than untraceable, and it locates what superseded
    it: the withdrawal removed the fifth substructure and the sample-form
    corrections moved the conditioning.
    """
    src = os.path.join(SNAPSHOT_PRE_NB3SN,
                       "phase_3_form3_fits_partial_cohortB_v2.csv")
    new = os.path.join(DATA, "phase_3_p54_substep_C_new_form3_fits.csv")
    if not (os.path.exists(src) and os.path.exists(new)):
        print("\n   Stage 2 cohort cannot be rebuilt; a snapshot is missing")
        return ["stage2 cohort snapshot"]
    a = pd.read_csv(src)
    a = a[a.physicality == "ok"]
    b = pd.read_csv(new)
    b = b[(b.physicality == "ok") & (b.fixed_axis == "T")]
    c = pd.concat([a, b], ignore_index=True)
    c["substructure"] = c.compound_formula.map(substructure_from_formula)
    res = []
    for _i, row in c.iterrows():
        pool = c[(c.arxiv_id != row.arxiv_id)
                 & (c.substructure == row.substructure)
                 & (c.sample_form == row.sample_form)]
        if pool.empty:
            continue
        res.append(abs(row.beta - pool.beta.median()))
    got = (len(c), c.arxiv_id.nunique(), c.substructure.nunique(),
           len(res), round(float(np.mean(res)), 3))
    print("\nrebuilding the superseded per-paper Stage 2 cohort\n")
    print("   %-34s %s" % ("fits, papers, substructures", got[:3]))
    print("   %-34s %d scored, MAE %.4f" % ("Stage 2 conditioned predictor",
                                            got[3], float(np.mean(res))))
    if got != STAGE2_COHORT:
        print("   expected %s, got %s" % (STAGE2_COHORT, got))
        return ["stage2 cohort"]
    print("   matches the reported cohort and value exactly")
    return []


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

    # The superseded row, sourced. It does not reproduce from the snapshot above
    # because that snapshot postdates the sample-form corrections, and the
    # field-axis predictor conditions on sample form. It reproduces exactly from
    # the snapshot that precedes them, along with every other deposited value,
    # which locates the change precisely rather than leaving the row unexplained.
    if os.path.isdir(SNAPSHOT_PRE_FORM):
        print("\nasserting the superseded row against %s\n" % SNAPSHOT_PRE_FORM)
        r0 = run(SNAPSHOT_PRE_FORM, iters=1, seed=20260901, verbose=False)
        for name, (dep, _med) in DEPOSITED_H.items():
            got = r0["field"][name][0]
            ok = abs(got - dep) < 1e-9
            print("   field  %-22s %.10f vs %.10f   %s"
                  % (name, got, dep, "exact" if ok else "DIFFERS"))
            if not ok:
                bad.append("pre-sample-form %s" % name)
    else:
        print("\n   %s not present; the superseded row cannot be sourced"
              % SNAPSHOT_PRE_FORM)


    bad += reconstruct_stage2()

    if bad:
        print("\nreproduction FAILED for: %s" % ", ".join(bad))
        return 1
    print("\nEvery documented reproduction claim holds. On the pre-withdrawal "
          "snapshot the iron_pnictide_1111 field-axis row differs, and on the "
          "snapshot taken before the sample-form corrections every deposited "
          "value including that one reproduces exactly. The corrections are "
          "therefore what moved it, and the generator's value is what ships.")
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
        mae, med, nc, nf, med_mae, med_med = r["field"][name]
        hrows.append(dict(substructure=name, n_compounds=nc, n_fits=nf,
                          compound_loo_mae=mae, compound_loo_median_residual=med,
                          substructure_median_loo_mae=med_mae,
                          substructure_median_loo_median_residual=med_med))
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
    prows = []
    for stat, key in [("per_paper_leave_one_out_beta_H_stage2_conditioned",
                       "per_paper"),
                      ("per_paper_leave_one_out_beta_H_pooled_median",
                       "per_paper_pooled")]:
        m, lo, hi, nf, np_ = r[key]
        prows.append(dict(statistic=stat, n_fits_scored=nf, n_papers=np_, mae=m,
                          ci_lower_95=lo, ci_upper_95=hi,
                          bootstrap_iterations=5000, seed=args.seed))
    pd.DataFrame(prows).to_csv(OUT_P, index=False)
    print("\nwritten to %s, %s, %s and %s" % (OUT_H, OUT_T, OUT_G, OUT_P))
    return 0


if __name__ == "__main__":
    sys.exit(main())
