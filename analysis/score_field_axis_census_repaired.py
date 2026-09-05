#!/usr/bin/env python3
"""
score_field_axis_census_repaired.py

The pre-registered field-axis census, re-scored against the repaired anchors.

Why it has to be re-scored. The census asks whether the field axis reproduces
its own printed figures better than the temperature axis does. Its statistic is
the per-fit |ln(deposited beta_H / figure beta_H)|, with the SAME anchor, the
same temperature and the same window on both sides. The anchor therefore enters
both sides, and analysis/apply_anchor_repairs.py changed it.

Why this is awkward, and the awkwardness is not hidden here. The census set was
fixed in audit/field_axis_census_preregistration_20260905.md before any tracing
began, precisely so the comparison could not be run on a set chosen after the
fact. Two of its four papers, physc.2009.11.051 and physc.2010.05.048, were
withdrawn from the cohort by the anchor repair. Dropping them and re-scoring the
remaining two is exactly the move the pre-registration exists to prevent, so
every arm is reported:

  A  the pre-registered four, deposited anchors        the number on file
  B  the pre-registered four, repaired anchors         same set, new anchors
  C  the two that survive the repair, repaired anchors POST HOC, and labelled so

The comparison arm is also repaired. analysis/adjudicate_temperature_axis.py
already reports the temperature axis's deposited-over-figure ratio under the
deposited Tc and under the paper's own Tc, and both are used, so that a repaired
field arm is never compared against an unrepaired temperature arm.

    python3 analysis/score_field_axis_census_repaired.py

Run from the repository root. Writes audit/field_axis_census_repaired.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "analysis")
from adjudicate_field_axis import PASS, figure_beta, trace, MIN_LEVER
from score_field_axis_census import CENSUS, series_for, METHOD

FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_REP = FITS.replace(".csv", "_repaired.csv")
OUT = os.path.join("audit", "field_axis_census_repaired.csv")

# From analysis/adjudicate_temperature_axis.py, its own printed table: the
# deposited-over-figure beta_T ratio per paper, under the deposited Tc and under
# the Tc the paper prints. A paper with no overlap, or no printed Tc, has no
# entry in the arm that needs it.
TEMPERATURE_DEPOSITED = {
    "0806.2839v1": 0.29, "0903.0004v2": 0.25, "0906.0444v1": 0.52,
    "1009.4896v1": 0.40, "1104.0477v2": 0.38, "1111.3923v1": 0.19,
    "1502.05345v1": 0.56, "1611.08455v1": 0.08, "1903.00866v2": 1.00,
    "2012.13723v3": 0.47, "2207.06629v1": 0.94, "2305.10034v1": 0.43,
    "2308.10492v1": 0.69, "2510.10264v1": 0.29,
}
TEMPERATURE_PAPER_TC = {
    "0806.2839v1": 0.29, "0903.0004v2": 0.25, "0906.0444v1": 0.48,
    "1104.0477v2": 0.38, "1111.3923v1": 0.19, "1502.05345v1": 0.50,
    "1611.08455v1": 0.08, "1903.00866v2": 1.01, "2012.13723v3": 0.47,
    "2207.06629v1": 0.94, "2305.10034v1": 0.42, "2308.10492v1": 0.65,
    "2510.10264v1": 0.22,
}
WITHDRAWN = ("physc.2009.11.051", "physc.2010.05.048")


def score_field(fits, anchor_col):
    """Per-paper median |ln(deposited / figure)| on the census set."""
    out, per_fit = {}, {}
    for k, cfg in CENSUS.items():
        g = fits[fits.paper_key == k]
        rr = []
        for _, r in g.iterrows():
            nm = cfg["traces"].get(r.fixed_axis_value)
            s = series_for(cfg, r)
            if nm is None or s in cfg.get("exclude", {}):
                continue
            t = trace(nm)
            if s is not None:
                t = t[t.series == s]
            if t.empty:
                continue
            hc2 = float(r[anchor_col])
            f = figure_beta(t.copy(), r.fixed_axis_value, hc2)
            if not f or f["lever"] < MIN_LEVER or f["beta"] == 0:
                continue
            # the deposited beta is refit at the repaired anchor on the same
            # window, so both sides move together and the ratio stays a
            # like-for-like comparison
            b = r.beta if anchor_col == "Hc2_T_used" else r.get("beta_repaired",
                                                                np.nan)
            if not np.isfinite(b) or b == 0:
                continue
            rr.append(abs(np.log(abs(b / f["beta"]))))
        if rr:
            out[k] = float(np.median(rr))
            per_fit[k] = rr
    return out, per_fit


def compare(field, temp, label):
    from scipy.stats import mannwhitneyu
    fv = list(field.values())
    tv = list(np.abs(np.log(np.array(list(temp.values())))))
    if len(fv) < 2 or len(tv) < 2:
        return np.nan
    p = mannwhitneyu(fv, tv, alternative="less").pvalue
    print(f"  {label}: field {len(fv)} papers median {np.median(fv):.3f}, "
          f"temperature {len(tv)} papers median {np.median(tv):.3f}, "
          f"p = {p:.3f}")
    return float(p)


def main():
    dep = PASS(pd.read_csv(FITS))
    if not os.path.exists(FITS_REP):
        print(f"{FITS_REP} is missing; run analysis/apply_anchor_repairs.py --apply")
        return 1
    rep = pd.read_csv(FITS_REP)
    rep = rep[(rep.ok == True) & (rep.physicality == "ok")]

    print("=" * 84)
    print("ARM A: the pre-registered four papers, deposited anchors")
    print("=" * 84)
    a, _ = score_field(dep, "Hc2_T_used")
    for k, v in a.items():
        print(f"  {k[:52]:52s} {METHOD.get(k, ''):20s} {v:.3f}")
    pa = compare(a, TEMPERATURE_DEPOSITED, "against the temperature axis at "
                                           "its deposited Tc")
    print()

    print("=" * 84)
    print("ARM B: the same four papers, repaired anchors on both sides")
    print("=" * 84)
    b, _ = score_field(rep, "Hc2_repaired")
    for k, v in b.items():
        moved = "" if k not in a else f"  (was {a[k]:.3f})"
        print(f"  {k[:52]:52s} {METHOD.get(k, ''):20s} {v:.3f}{moved}")
    pb = compare(b, TEMPERATURE_PAPER_TC, "against the temperature axis at the "
                                          "paper's own Tc")
    # count papers whose ANCHOR moved, not whose score moved: the refit carries
    # numerical noise of order 1e-6 even where the anchor is identical, and
    # counting that was reporting three papers where one had changed
    touched = sorted({k for k in CENSUS
                      if (rep[rep.paper_key == k].Hc2_repaired
                          - rep[rep.paper_key == k].Hc2_T_used).abs().gt(1e-9).any()})
    moved_n = len(touched)
    print(f"  only {moved_n} of the {len(b)} census papers has an anchor the "
          f"repair touched. matchemphys.2023.128348's anchors were confirmed "
          f"rather than changed, and the two withdrawn papers keep their "
          f"deposited anchors here because withdrawal is not a correction to "
          f"the value. So arm B is close to arm A by construction.")
    print()

    print("=" * 84)
    print("ARM C: only the two papers that survive the repair. POST HOC.")
    print("=" * 84)
    print("  physc.2009.11.051 and physc.2010.05.048 were withdrawn from the")
    print("  cohort because neither paper prints a critical field of any kind.")
    print("  Scoring the census on what is left is selection after the fact and")
    print("  the pre-registration exists to forbid it. It is reported so that")
    print("  the effect of the selection is visible, not because it is valid.")
    c = {k: v for k, v in b.items() if not any(w in k for w in WITHDRAWN)}
    for k, v in c.items():
        print(f"  {k[:52]:52s} {v:.3f}")
    pc = compare(c, TEMPERATURE_PAPER_TC, "against the temperature axis at the "
                                          "paper's own Tc")
    print()

    print("=" * 84)
    print("WHAT MOVED")
    print("=" * 84)
    print(f"  the pre-registered comparison, deposited throughout : p = {pa:.3f}")
    print(f"  the same set with both anchors repaired             : p = {pb:.3f}")
    print(f"  the surviving two, post hoc                         : p = {pc:.3f}")
    print()
    tdep = np.median(np.abs(np.log(np.array(list(TEMPERATURE_DEPOSITED.values())))))
    tpap = np.median(np.abs(np.log(np.array(list(TEMPERATURE_PAPER_TC.values())))))
    print(f"  the temperature arm itself barely moves under the repair: median "
          f"|ln ratio| {tdep:.3f} at the deposited Tc against {tpap:.3f} at the "
          f"paper's own. Correcting Tc does not make those extractions "
          f"reproduce their figures any better; it changes both sides together.")
    pd.DataFrame([
        dict(arm="A pre-registered, deposited", papers=len(a),
             field_median=np.median(list(a.values())), p=pa),
        dict(arm="B pre-registered, repaired", papers=len(b),
             field_median=np.median(list(b.values())), p=pb),
        dict(arm="C surviving two, post hoc", papers=len(c),
             field_median=np.median(list(c.values())), p=pc),
    ]).to_csv(OUT, index=False)
    print()
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
