#!/usr/bin/env python3
"""A10's replacement figures, and why they should not be reported as ratios.

Referee A: "Grouping the data reduces the error in the field-dependence
exponent by a factor of 23. This is an exaggeration." The letter concedes it,
explains that the 23-fold set one out-of-sample error against two
resubstitution errors, and replaces it with three leave-one-substructure-out
figures: 1.07 across the seven families carrying a descriptor, 2.24 on the fits
passing physicality, and 1.83 with the cuprates removed.

All three reproduce exactly. A first version of this file then reported that
they move to 0.98, 4.57 and 2.42 on the repaired cohort. Adversarial review
refuted that, and the refutation is the finding.

**The replacement figures repeat the defect they were introduced to fix.**
multi_stage_loso.py's own docstring says the published 16-fold is invalid
because "Stage 1 is a mean over 9 families and Stages 2 and 3 over 5, and
pandas .mean() skips them silently". The two pooled Stage 2 readings are
undefined for conventional_AlB2 on every cohort here, because no other family
contributes a bulk or wire fit once the cuprates are gated out, so 2.24 and
1.83 divide a four-family Stage 1 mean by a three-family Stage 2 mean. Matched
over the same families they are 2.17 and 2.11. A referee who reads the
generator the letter cites will find it indicting the numbers the letter
quotes.

**The 2.24 to 4.57 movement is a change of estimator, not of conditioning.**
The generator picks whichever of four Stage 2 readings has the lowest error,
and the winner is pooled_flat on the deposited cohort and pooled_forms on the
repaired one. Held at the reading the letter's own figure comes from, 2.24
becomes 2.31. Decomposed further, dropping the three withdrawn papers alone
carries 4.05 of the 4.57 and the repaired exponent adds the rest; the repaired
critical field contributes exactly nothing, because the estimator reads only
compound, family, sample form and exponent and never an anchor. A first version
of this file substituted the repaired anchor anyway, which was dead code that
made the arm look like it accounted for the anchor repairs.

**Four folds cannot support a ratio.** On the 52 fits the protocol admits there
are four families, so four folds, and dropping one family in turn moves the
figure from 0.82 to 391. Stage 1 is a two-parameter fit on three training
points per fold.

So this script no longer reports a best-reading fold improvement. It reports
the Stage 1 and Stage 2 errors under every reading, matched over the families
each reading can actually score, and the jackknife, and leaves the letter to
say that the improvement is not distinguishable from one.

    python analysis/a10_on_repaired_cohort.py

Run from the repository root.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multi_stage_loso as loso                     # noqa: E402

FITS = loso.FITS
FITS_REP = FITS.replace(".csv", "_repaired.csv")
PROTOCOL = os.path.join("audit", "fit_protocol_applied.csv")
SCRATCH = os.path.join("audit", "a10_cohorts")
OUT = os.path.join("audit", "a10_on_repaired_cohort.csv")

# Pre-specified, not chosen after seeing the arms. This is the reading the
# letter's own 2.24 and 1.83 come from, so holding every arm to it is what
# makes the columns comparable.
READING = "stage2_pooled_flat_abs"
COHORTS = [(False, None, "all fits, every family with a descriptor"),
           (True, None, "physicality == ok only"),
           (False, loso.IRON_MGB2, "cuprates removed")]
QUOTED = {"all fits, every family with a descriptor": 1.07,
          "physicality == ok only": 2.24,
          "cuprates removed": 1.83}


def repaired():
    """The repaired field-axis table with withdrawn papers dropped.

    The physicality gate is taken from passing_repaired, not from the deposited
    physicality column. That column was computed from the deposited exponent
    and the deposited anchor, and seven fits carry "ok" there while their own
    repair says they no longer pass. Reading the stale column instead moves the
    middle cohort's figure by a factor of about 1.7, in the flattering
    direction.

    No anchor column is substituted. The estimator never reads one, so doing it
    would only disguise which arm is which.
    """
    r = pd.read_csv(FITS_REP)
    r = r[r.withdrawn.fillna("") == ""].copy()
    r["beta"] = r.beta_repaired.where(r.beta_repaired.notna(), r.beta)
    r["physicality"] = np.where(r.passing_repaired, "ok",
                                "H_axis_applicability_bound")
    return r


def admitted():
    r = repaired()
    p = pd.read_csv(PROTOCOL)
    a = p[p.admitted][["paper", "sample", "T", "beta"]].rename(
        columns={"beta": "beta_protocol"})
    r["T"] = r.fixed_axis_value
    m = r.merge(a, left_on=["paper_key", "sample_identifier", "T"],
                right_on=["paper", "sample", "T"], how="inner")
    if len(m) != int(p.admitted.sum()) or m.duplicated(
            ["paper_key", "sample_identifier", "T"]).any():
        raise SystemExit("the admitted set did not join one to one")
    m["beta"] = m.beta_protocol
    if (m.physicality != "ok").any():
        raise SystemExit("an admitted fit does not pass the repaired gate, so "
                         "the three cohorts are no longer one set here and the "
                         "collapse this script reports is wrong")
    return m.drop(columns=["paper", "sample", "T"])


def block(frame, label, ok_only, fams):
    os.makedirs(SCRATCH, exist_ok=True)
    path = os.path.join(SCRATCH, "%s.csv" % label.replace(" ", "_"))
    frame.to_csv(path, index=False)
    saved = loso.FITS
    loso.FITS = path
    try:
        out, keys = loso.run(ok_only, fams, label)
    finally:
        loso.FITS = saved
    return out, keys


def matched(out, col):
    """Stage 1 and Stage 2 means over the families the reading can score."""
    m = out[col].notna()
    if not m.any():
        return np.nan, np.nan, 0, len(out)
    return (float(out.stage1_abs[m].mean()), float(out[col][m].mean()),
            int(m.sum()), len(out))


def main():
    arms = [("deposited", pd.read_csv(FITS)),
            ("repaired", repaired()),
            ("admitted", admitted())]
    for lab, f in arms:
        print("%-12s %3d fits, %2d papers" % (lab, len(f), f.arxiv_id.nunique()))

    print("\nthe letter's three figures, reproduced and then held to one "
          "reading\n")
    print("   %-42s %7s %9s %9s %9s"
          % ("family cohort", "letter", "as best", READING.split("_")[2],
             "matched"))
    rows, fails = [], []
    for ok_only, fams, title in COHORTS:
        out, keys = block(pd.read_csv(FITS), "dep_" + title, ok_only, fams)
        if out is None:
            continue
        # keys are the reading names; the frame carries them as
        # stage2_<name>_abs columns.
        col = {k: "stage2_%s_abs" % k for k in keys}
        best = min(keys, key=lambda k: out[col[k]].mean())
        as_best = out.stage1_abs.mean() / out[col[best]].mean()
        s1, s2, n, tot = matched(out, READING)
        print("   %-42s %7.2f %9.2f %9.2f %9.2f"
              % (title, QUOTED[title], as_best,
                 out.stage1_abs.mean() / out[READING].mean(), s1 / s2))
        if abs(round(as_best, 2) - QUOTED[title]) > 5e-3:
            fails.append("%s: the deposited arm gives %.4f, the letter prints "
                         "%.2f" % (title, as_best, QUOTED[title]))
        rows.append(dict(arm="deposited", cohort=title, letter=QUOTED[title],
                         best_reading=best, fold_as_best=as_best,
                         fold_fixed_reading=out.stage1_abs.mean()
                         / out[READING].mean(),
                         fold_matched=s1 / s2, families_scored=n,
                         families_total=tot))
    print("\n   'as best' is what the letter reports: the lowest-error of four "
          "Stage 2 readings.")
    print("   The third column holds every arm to %s, which is the reading the "
          "letter's own" % READING.split("_", 1)[1])
    print("   2.24 and 1.83 come from. The fourth divides means taken over the "
          "same families:")
    print("   the pooled readings are undefined for conventional_AlB2, so the "
          "letter's figures")
    print("   divide a four-family numerator by a three-family denominator.")
    if fails:
        for f in fails:
            print("   FAIL %s" % f)
        raise SystemExit("the deposited arm is not the letter, nothing "
                         "reportable")
    print("   the deposited arm reproduces the letter on all three cohorts")

    print("\nevery arm, one reading, matched families\n")
    print("   %-42s %-11s %7s %7s %7s %6s"
          % ("family cohort", "arm", "Stage 1", "Stage 2", "fold", "fams"))
    for ok_only, fams, title in COHORTS:
        for lab, frame in arms:
            out, _keys = block(frame, "%s_%s" % (lab, title), ok_only, fams)
            if out is None:
                print("   %-42s %-11s   too few families" % (title, lab))
                continue
            s1, s2, n, tot = matched(out, READING)
            print("   %-42s %-11s %7.3f %7.3f %7.2f %4d/%d"
                  % (title, lab, s1, s2, s1 / s2 if s2 else np.nan, n, tot))
            rows.append(dict(arm=lab, cohort=title, stage1=s1, stage2=s2,
                             fold_matched=s1 / s2 if s2 else np.nan,
                             families_scored=n, families_total=tot))

    print("\nhow much a single family is worth, on the admitted cohort\n")
    adm = admitted()
    out, keys = block(adm, "admitted_jack_full", True, None)
    fams_present = sorted(out.substructure)
    print("   %-26s %9s %9s" % ("family dropped", "fold", "reading"))
    s1, s2, _n, _t = matched(out, READING)
    print("   %-26s %9.2f %9s" % ("none", s1 / s2, "fixed"))
    swing = [s1 / s2]
    for fam in fams_present:
        sub = adm[adm.compound_formula.apply(loso.classify) != fam]
        o, k = block(sub, "adm_drop_%s" % fam, True, None)
        if o is None:
            print("   %-26s %9s" % (fam, "too few"))
            continue
        a1, a2, _n, _t = matched(o, READING)
        print("   %-26s %9.2f %9s" % (fam, a1 / a2 if a2 else np.nan, "fixed"))
        if a2:
            swing.append(a1 / a2)
    print("\n   four families means four folds, and Stage 1 is a "
          "two-parameter fit on three")
    print("   training points in each. The figure ranges over %.2f to %.2f "
          "when one family is" % (min(swing), max(swing)))
    print("   removed, which is the range a single family is worth.")

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("\n   written to %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
