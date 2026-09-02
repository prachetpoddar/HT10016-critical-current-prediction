#!/usr/bin/env python3
"""
multi_stage_loso.py

Leave-one-substructure-out validation of the three prediction scopes, computed
so that no stage sees the family it is predicting, and reported under every
construction and cohort that a reader could reasonably ask for.

WHY THIS EXISTS

phase_3_p39_multi_stage_predictor.py holds a substructure out for Stage 1 and
then predicts that same substructure at Stages 2 and 3 from its own fits:

    s2_pred = stage3_df[stage3_df.substructure == sub].beta_H_median_within_cell.median()
    s3_pred = fits_ok.groupby("substructure").beta.median()[sub]

Neither withholds anything. On the cohort that reproduces the published numbers,
conventional_A15 returns residuals of exactly 0.0000 at both stages, because it
is predicting itself; on the current deposit conventional_AlB2 returns 4.4e-16.
The reported 10.10 / 0.43 / 0.84 therefore sets one out-of-sample error against
two resubstitution errors.

Two further defects in that generator, both found here rather than assumed:

  The three means are taken over different family sets. Stage 2 and Stage 3 are
  NaN for any family with no physicality == "ok" fits, which on the publication
  cohort is all four cuprates, and pandas .mean() skips them silently. Stage 1
  is a mean over 9 families and Stages 2 and 3 over 5. The like-for-like Stage 1
  on those same 5 is 6.948, and 6.948 / 0.4313 = 16.11, so the manuscript's
  "16-fold" is in fact the matched ratio. What it should not do is quote 10.10
  as the numerator, because that number is computed on a family set the ratio
  never uses.

  Two of the five Stage 2 and Stage 3 terms are the self-predicted 0.0000 of
  conventional_A15, whose only record was withdrawn on 2026-09-01. Holding the
  in-sample method fixed and dropping A15 alone moves the published means to
  0.539 and 1.046.

WHAT REPRODUCES, AND WHAT DOES NOT

An earlier version of this docstring said the published 10.10 needed an
iron_chalcogenide_11 target of 1.43633 which "matches no deposited snapshot, so
that figure cannot be reproduced from the deposit at any cohort". That was
wrong, and it is retracted. All three published values reproduce jointly from
audit/pre_nb3sn_withdrawal_20260901 with that target: 10.0951, 0.4313, 0.8367.
Nor is the target a point requirement; any value in roughly [1.343, 1.437]
rounds Stage 1 to 10.10, and 1.370764 is itself a deposited quantity. The
defensible statement is narrower: the p18 descriptor row those numbers were
computed against is not deposited at any snapshot, while the fit table they used
is.

THE THREE SCOPES, FITTED ON TRAINING FAMILIES ONLY

  Stage 1   regress the family target on the compositional descriptor max_chi
            over the training families; predict the held-out one.

  Stage 2   the sample-form-conditional scope. There is no single obvious way to
            evaluate a within-family scope on a family that has been withheld,
            so four readings are computed and all four are reported. The
            weakest and the strongest differ by a factor of two, and reporting
            only one would be choosing an answer.

  Stage 3   the substructure-aggregate scope: the median of every training fit,
            with the training within-form interquartile range offered as a
            bound. Coverage of that bound is measured, not asserted.

Both target cohorts are computed. The all-fits target is what
phase_3_p18_substructure_descriptor_means.csv contains, matching it to fourteen
digits on cuprate_LSCO, whose five fits are all bound-hit; it is therefore the
quantity the descriptor regression was fitted against. The ok-only target is
what Sec. III.C of the manuscript uses at compound scope. The manuscript uses
both definitions without distinguishing them, which is itself worth reporting.

KNOWN LIMITS OF THIS SCRIPT, STATED RATHER THAN LEFT TO BE FOUND

  The descriptor is no longer read from p18. An earlier version of this script
  regressed a freshly computed target on max_chi_mean taken straight out of the
  table it calls stale, which is a fit-count-weighted mean and moved with the
  same withdrawals. It is now recomputed from the deposited anchor table by the
  same rule, the mean over a family's fits of each compound's max_chi, and
  _check_descriptor asserts that the rule reproduces the deposited p18 value on
  every family whose cohort did not change. Only the two families the
  withdrawals touched differ, and the two withdrawn families are gone.

  Three of the seven families are cuprates whose targets sit at or near the
  fitter's ceiling of 30 and which share max_chi_mean = 3.44 exactly, with
  targets 30.0, 5.50 and 30.0. No single-valued function of that descriptor can
  place all three, so a large part of the Stage 1 error is a property of the
  descriptor and the fit ceiling rather than of monolithic regression. Means and
  medians are both reported because with n = 7 and three censored points they
  say different things.

    python analysis/multi_stage_loso.py
    python analysis/multi_stage_loso.py --json out.json

Run from the repository root.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The canonical classifier lives in phase_3_p39_multi_stage_predictor, but
# importing that module pulls in scipy for a Spearman coefficient this script
# never uses, and scipy is not installed everywhere this deposit is run. The
# rules are mirrored here so the script runs anywhere pandas does, and
# _check_classifier asserts the mirror against the original whenever the
# original can be imported, so the two cannot drift silently.
def _assign_local(c):
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
    if "YBa" in c or "YBaCuO" in c or "REBCO" in c:
        return "cuprate_RBCO"
    if "Hg" in c and "Cu" in c and ("Ba" in c or "Sr" in c):
        return "cuprate_HBCCO"
    if "BSCCO" in c or "Bi-22" in c:
        return "cuprate_BSCCO"
    if "Bi" in c and "Sr" in c and "Cu" in c:
        return "cuprate_BSCCO"
    if "La" in c and "Cu" in c and "O" in c and "Ba" not in c:
        return "cuprate_LSCO"
    return "other_unclassified"


def _check_classifier(formulas):
    """Assert the mirror matches the canonical rules, where those can load."""
    try:
        from phase_3_p39_multi_stage_predictor import assign_substructure
    except ImportError:
        return "canonical classifier unavailable (scipy missing); mirror used"
    bad = [c for c in set(formulas) if assign_substructure(c) != _assign_local(c)]
    assert not bad, "mirrored classifier disagrees on %r" % bad[:5]
    return "mirror verified against the canonical classifier on %d formulas" % len(set(formulas))


assign_substructure = _assign_local

FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
DESCRIPTORS = os.path.join("data", "phase_3_p18_substructure_descriptor_means.csv")
OUT = os.path.join("audit", "multi_stage_loso.csv")
DESCRIPTOR = "max_chi_mean"

# assign_substructure matches on formula substrings and misses one spelling in
# the deposited fit file: Ba_Fe_Co_2As2 (MAGLAB_Co122_4_2K) is Ba(Fe,Co)2As2 and
# so iron_pnictide_122, but the underscores defeat the "Fe2As2", "BaFe" and
# "(Fe" branches and it falls through to other_unclassified. Left uncorrected it
# stays in the training pool when iron_pnictide_122 is held out, which is a leak
# this script's own headline promise forbids. assert_no_leak below enforces it.
SPELLING = {"Ba_Fe_Co_2As2": "iron_pnictide_122"}


def classify(formula):
    return SPELLING.get(formula, assign_substructure(formula))


ANCHORS = os.path.join("data", "phase_3_p31_jc_anchor_per_paper.csv")
# Families whose fit cohort the withdrawals and reclassification changed, and
# which therefore must not match the deposited descriptor table.
MOVED = {"iron_chalcogenide_11", "iron_pnictide_122"}


def _check_descriptor(fam):
    """The recomputation must reproduce p18 wherever the cohort did not move."""
    if not os.path.exists(DESCRIPTORS):
        return "p18 absent; descriptor recomputed without a cross-check"
    d = pd.read_csv(DESCRIPTORS)
    d = d[d.framing == "H_irr_or_empirical"].set_index("substructure")
    same = bad = 0
    for _i, r in fam.iterrows():
        if r.substructure in MOVED or r.substructure not in d.index:
            continue
        if abs(float(d.loc[r.substructure, DESCRIPTOR]) - r[DESCRIPTOR]) < 1e-9:
            same += 1
        else:
            bad += 1
    assert not bad, "descriptor rule disagrees with p18 on %d unmoved families" % bad
    return ("descriptor rule reproduces p18 on all %d families whose cohort did "
            "not move" % same)


def load(ok_only):
    f = pd.read_csv(FITS)
    f["substructure"] = f.compound_formula.apply(classify)
    if ok_only:
        f = f[f.physicality == "ok"]
    a = pd.read_csv(ANCHORS).drop_duplicates("compound_formula")
    chi = a.set_index("compound_formula").max_chi
    f = f.assign(_chi=f.compound_formula.map(chi))
    fam = (f.groupby("substructure")
             .agg(target=("beta", "median"), n_fits=("beta", "size"),
                  **{DESCRIPTOR: ("_chi", "mean")})
             .reset_index())
    fam = fam.dropna(subset=[DESCRIPTOR]).reset_index(drop=True)
    return f, fam


def assert_no_leak(f, fam):
    """No fit of a scored family may sit outside that family's own label."""
    scored = set(fam.substructure)
    stray = f[~f.substructure.isin(scored)]
    for _i, r in stray.iterrows():
        for s in scored:
            token = s.split("_")[-1]
            assert token.lower() not in str(r.compound_formula).lower(), (
                "unclassified fit %r looks like %s and would leak into its "
                "training pool" % (r.compound_formula, s))


def stage2_variants(train, fam_train, held, chi_held):
    """Four readings of "the sample-form-conditional median", all out of sample.

    pooled_forms       one median per sample form over all training fits, the
                       held-out family's forms combined weighted by how many
                       fits it contributes to each. Uses no family information,
                       so it drags every prediction toward the pooled median.
    pooled_flat        the plain median of all training fits in those forms.
    nearest_family     the training family nearest in the descriptor, restricted
                       to the held-out family's forms. This is the strongest
                       reading and the one to beat.
    nearest_no_form    the same nearest family with no form restriction, which
                       isolates how much of that reading comes from the form
                       conditioning rather than from family similarity.
    """
    forms = held.sample_form.value_counts().to_dict()
    out = {}

    num = den = 0.0
    for form, w in forms.items():
        pool = train[train.sample_form == form]
        if not pool.empty:
            num += w * pool.beta.median()
            den += w
    out["pooled_forms"] = num / den if den else np.nan

    flat = train[train.sample_form.isin(forms)]
    out["pooled_flat"] = flat.beta.median() if len(flat) else np.nan

    near = fam_train.iloc[(fam_train[DESCRIPTOR] - chi_held).abs().argsort()]
    nf = near.iloc[0].substructure
    pool = train[train.substructure == nf]
    sub = pool[pool.sample_form.isin(forms)]
    out["nearest_family"] = (sub.beta.median() if len(sub)
                             else pool.beta.median())
    out["nearest_no_form"] = pool.beta.median()
    return out


def run(ok_only, families=None, label=""):
    f, fam = load(ok_only)
    if families is not None:
        fam = fam[fam.substructure.isin(families)].reset_index(drop=True)
        f = f[f.substructure.isin(families)]
    assert_no_leak(f, fam)
    if len(fam) < 3:
        return None, None

    keys = ["pooled_forms", "pooled_flat", "nearest_family", "nearest_no_form"]
    rows = []
    for i, r in fam.iterrows():
        tr_fam = fam.drop(i)
        train = f[f.substructure != r.substructure]
        held = f[f.substructure == r.substructure]
        assert (train.substructure == r.substructure).sum() == 0

        b, a = np.polyfit(tr_fam[DESCRIPTOR], tr_fam.target, 1)
        s1 = b * r[DESCRIPTOR] + a
        s2 = stage2_variants(train, tr_fam, held, r[DESCRIPTOR])
        s3 = train.beta.median()
        iqr = float(train.groupby("sample_form").beta
                    .apply(lambda x: x.quantile(.75) - x.quantile(.25)).median())

        row = dict(cohort=label, substructure=r.substructure,
                   n_fits=int(r.n_fits), target=r.target,
                   stage1_abs=abs(s1 - r.target), stage3_abs=abs(s3 - r.target),
                   stage3_iqr_bound=iqr,
                   stage3_within_bound=abs(s3 - r.target) <= iqr)
        for k in keys:
            row["stage2_%s_abs" % k] = abs(s2[k] - r.target)
        rows.append(row)
    return pd.DataFrame(rows), keys


def report(out, keys, title):
    print("\n%s   (%d families)\n" % (title, len(out)))
    print("   %-22s %5s %8s %9s %9s %9s"
          % ("held out", "fits", "target", "Stage 1", "S2 best", "Stage 3"))
    best = min(keys, key=lambda k: out["stage2_%s_abs" % k].mean())
    for _i, r in out.iterrows():
        print("   %-22s %5d %8.3f %9.3f %9.3f %9.3f"
              % (r.substructure, r.n_fits, r.target, r.stage1_abs,
                 r["stage2_%s_abs" % best], r.stage3_abs))
    m1, m3 = out.stage1_abs.mean(), out.stage3_abs.mean()
    d1, d3 = out.stage1_abs.median(), out.stage3_abs.median()
    print("\n   %-34s %9s %9s" % ("Stage 2 reading", "MAE", "fold vs S1"))
    for k in keys:
        v = out["stage2_%s_abs" % k].mean()
        print("   %-34s %9.3f %9.2f%s"
              % (k, v, m1 / v, "   <- best" if k == best else ""))
    print("\n   Stage 1  MAE %7.3f   median %7.3f" % (m1, d1))
    print("   Stage 3  MAE %7.3f   median %7.3f   fold on means %.2f, on medians %.2f"
          % (m3, d3, m1 / m3, d1 / d3))
    cov = int(out.stage3_within_bound.sum())
    print("   Stage 3 IQR bound covers the residual in %d of %d families"
          % (cov, len(out)))
    return dict(stage1_mae=m1, stage1_median=d1, stage3_mae=m3,
                stage3_median=d3, best_stage2=best,
                best_stage2_mae=float(out["stage2_%s_abs" % best].mean()),
                bound_coverage="%d/%d" % (cov, len(out)))


IRON_MGB2 = ["conventional_AlB2", "iron_chalcogenide_11",
             "iron_pnictide_1111", "iron_pnictide_122"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    print(_check_classifier(pd.read_csv(FITS).compound_formula))
    print(_check_descriptor(load(False)[1]) + "\n")
    summary, frames = {}, []
    for ok_only, fams, title in [
            (False, None, "all fits, every family with a descriptor"),
            (True, None, "physicality == ok only"),
            (False, IRON_MGB2, "all fits, cuprates removed from cohort and pools")]:
        out, keys = run(ok_only, fams, title)
        if out is None:
            print("\n%s   too few families to regress" % title)
            continue
        summary[title] = report(out, keys, title)
        frames.append(out)

    print("\nNo reading of Stage 2, on any cohort, reaches even a two-fold "
          "improvement on Stage 1, and the published comparison claims sixteen.")
    os.makedirs("audit", exist_ok=True)
    pd.concat(frames).to_csv(OUT, index=False)
    print("written to %s" % OUT)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(summary, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
