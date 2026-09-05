#!/usr/bin/env python3
"""
fit_protocol.py

One statement of the fitting protocol, and one implementation of it.

Why this exists. Three things about the protocol were undocumented or
inconsistent, and new data pushed through the old code would inherit all three:

  1. the retention rule was not stated anywhere
  2. the temperature clause of the applicability window was applied to one
     cohort and not the other
  3. the field clause contains nothing independent of the anchor, so it cannot
     say what it is meant to say

This module fixes each as a decision, states it, implements it once, and
measures what the decision costs. Everything downstream should call these
functions rather than re-deriving the rule.

    python3 analysis/fit_protocol.py --selftest
    python3 analysis/fit_protocol.py --report      what each decision costs

DECISION 1: RETENTION.

    keep a point when  1 - H/Hc2 >= H_FLOOR,  H_FLOOR = 0.05

What was there before was `H < Hc2` with no floor. Its defect is real: a point
arbitrarily close to the anchor has an abscissa of log10(1 - H/Hc2) going to
minus infinity and so takes unbounded leverage over the slope. 1002.0208v2
retains a point at 1 - H/Hc2 = 0.0011, whose abscissa is -2.96 while the rest of
that isotherm sits near -0.3.

The floor is a CHOICE, not a measurement, and the first version of this docstring
argued for it twice over from the same fact. It said that four fits of
jallcom.2023.170146 "behave as though a floor near 0.05 was already applied",
and separately that every paper's closest retained point sits at 0.057 or above.
Both come from the reconstruction factor 0.95 in
analysis/apply_anchor_repairs.py, which is 1 - 0.05. Under the old rule as
stated, jallcom.2023.170146's closest retained point is at 0.015, not 0.057, and
a fine sweep of that factor bounds the implied floor only to 0.0475 to 0.055,
from those same four fits.

What the floor costs, measured against the old rule as stated: it drops 20
points across 15 fits in 4 papers and moves the exponent by up to 0.835. What it
does not do is cure the case it was written for. 1002.0208v2's exponents run
0.068 to 1.015 with the floor and 0.099 to 1.015 without it, and all six are
admitted either way. The floor bounds the leverage; it does not make that paper's
fits good.

DECISION 2: THE TEMPERATURE CLAUSE APPLIES TO BOTH COHORTS.

    a fit is inside the window when  T/Tc < 0.7

The manuscript states this clause as part of the applicability window. It is
imposed on the temperature axis, by cutting the fit window against the anchor,
and it is not imposed on the field axis at all. Either it is part of the window
or it is not; it cannot be both. It is applied here to both.

DECISION 3: THE FIELD CLAUSE STAYS, AND IS STATED FOR WHAT IT IS.

    the clause          (Hmax - Hmin)/Hc2 > 0.3, on the retained points
    reported beside it  the lever, the span of log10(1 - H/Hc2), which is what
                        the slope is actually estimated over

The first version of this module replaced the clause with a minimum lever, on
the argument that the lever "cannot be satisfied by shrinking the anchor alone".
That argument is wrong and an independent review broke it. The floor pins the
smallest retained 1 - H/Hc2 at 0.05, so shrinking the anchor until a data point
lands just inside the floor maximises the lever, and it is the same move that
maximises the old ratio. On this cohort every one of the ten fits that fail the
lever clears it on unchanged data at a smaller anchor, phpro.2015.06.160 among
them. The two criteria are gamed identically.

There is no anchor-independent criterion to be had here. The abscissa of the fit
is log(1 - H/Hc2), so every property of the fit is a property of the anchor. The
only repair is to make the anchor trustworthy, which is what
analysis/apply_anchor_repairs.py does, and then to say plainly what the clause
is: a statement that the measured field span is a large fraction of the recorded
critical field, which is informative exactly to the extent that the recorded
critical field is right.

So the clause is kept, the lever is reported next to it as a diagnostic, and
neither is presented as a test of the data alone.
"""
import sys

import numpy as np

H_FLOOR = 0.05          # minimum 1 - H/Hc2 for a point to be retained
TEMP_CLAUSE = 0.7       # T/Tc must be below this
FIELD_CLAUSE = 0.3      # the old (Hmax - Hmin)/Hc2 bound, kept for comparison
# log10(2): the reduced field 1 - H/Hc2 must vary by at least a factor of two
# across the retained points. That is the smallest span over which a power law
# in it can be said to have been measured rather than assumed.
# reported, not gated: the span the slope is estimated over. A factor of two in
# the reduced field is the smallest span over which a power law in it can be
# said to have been measured. It is NOT anchor-independent; see Decision 3.
MIN_LEVER_DEX = 0.301
MIN_PTS = 3


def retain(H, Hc2, floor=None):
    """Boolean mask of the points a fit may use. Decision 1.

    floor is read at call time, not bound at def time: a caller doing a
    sensitivity sweep by setting fit_protocol.H_FLOOR was silently getting the
    shipped value back.
    """
    floor = H_FLOOR if floor is None else floor
    H = np.asarray(H, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        h = 1.0 - H / Hc2
    return np.isfinite(h) & (h >= floor)


def lever(H, Hc2):
    """Span of the abscissa over the retained points, in dex. Decision 3."""
    H = np.asarray(H, float)[retain(H, Hc2)]
    if len(H) < 2:
        return 0.0
    x = np.log10(1.0 - H / Hc2)
    return float(x.max() - x.min())


def old_field_clause(H, Hc2):
    """(Hmax - Hmin)/Hc2 over the retained points. Reported, not used."""
    H = np.asarray(H, float)[retain(H, Hc2)]
    if len(H) < 2:
        return np.nan
    return float((H.max() - H.min()) / Hc2)


def inside_window(T, Tc):
    """Decision 2, applied to both cohorts."""
    return bool(T / Tc < TEMP_CLAUSE)


def fit(x_num, J, scale):
    """log10 Jc on log10(1 - x/scale). Returns slope, n, lever."""
    x_num = np.asarray(x_num, float)
    J = np.asarray(J, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        x = np.log10(1.0 - x_num / scale)
        y = np.log10(J)
    m = np.isfinite(x) & np.isfinite(y) & (J > 0)
    if m.sum() < MIN_PTS:
        return np.nan, int(m.sum()), 0.0
    return (float(np.polyfit(x[m], y[m], 1)[0]), int(m.sum()),
            float(x[m].max() - x[m].min()))


def admits(H, J, Hc2, T, Tc):
    """The whole protocol on one fit. Returns a dict, never a bare boolean."""
    keep = retain(H, Hc2)
    Hk = np.asarray(H, float)[keep]
    Jk = np.asarray(J, float)[keep]
    b, n, lev = fit(Hk, Jk, Hc2)
    ratio = old_field_clause(H, Hc2)
    return dict(n_kept=int(keep.sum()), beta=b, n_used=n, lever_dex=lev,
                field_ratio=ratio,
                in_temperature_window=inside_window(T, Tc),
                enough_points=n >= MIN_PTS,
                has_lever=bool(lev >= MIN_LEVER_DEX),
                clears_field_clause=bool(ratio > FIELD_CLAUSE),
                admitted=bool(n >= MIN_PTS and ratio > FIELD_CLAUSE
                              and inside_window(T, Tc)))


def selftest():
    bad = 0
    # 9.5 sits exactly on the floor and is kept; 9.6 and 9.99 are inside it
    H = np.array([0., 1., 2., 4., 8., 9.5, 9.6, 9.99])
    Hc2 = 10.0

    k = retain(H, Hc2)
    ok = list(k) == [True] * 6 + [False, False]
    print(f"  [{'PASS' if ok else 'FAIL'}] retention is inclusive at the "
          f"floor and drops what is inside it: kept {H[k]}, dropped {H[~k]}")
    bad += not ok

    # a point at the anchor must not be able to carry the fit
    lev_floor = lever(H, Hc2)
    lev_nofloor = np.log10(1 - H[0] / Hc2) - np.log10(1 - H[-1] / Hc2)
    ok = lev_floor < 2.0 < lev_nofloor
    print(f"  [{'PASS' if ok else 'FAIL'}] the floor bounds the lever: "
          f"{lev_floor:.3f} dex with it, {lev_nofloor:.3f} without")
    bad += not ok

    # the old clause can be passed by shrinking the anchor; the lever cannot be
    # passed by shrinking it alone, because points fall out at the floor
    Hd = np.array([0., 0.1, 0.2, 0.3])
    r_big, r_small = old_field_clause(Hd, 10.0), old_field_clause(Hd, 0.35)
    l_big, l_small = lever(Hd, 10.0), lever(Hd, 0.35)
    ok = (r_big < FIELD_CLAUSE < r_small) and (l_small > l_big)
    print(f"  [{'PASS' if ok else 'FAIL'}] shrinking the anchor from 10 to "
          f"0.35 T takes the old ratio {r_big:.3f} -> {r_small:.3f}, past its "
          f"{FIELD_CLAUSE} bound, on unchanged data")
    bad += not ok

    # decision 2 must be symmetric: same function, both cohorts
    ok = inside_window(10.0, 20.0) and not inside_window(15.0, 20.0)
    print(f"  [{'PASS' if ok else 'FAIL'}] the temperature clause is one "
          f"function: 10/20 inside, 15/20 outside")
    bad += not ok

    # fit must recover a planted exponent through the protocol
    Hs = np.linspace(0, 8, 12)
    Js = 1e6 * (1 - Hs / 10.0) ** 1.7
    got = admits(Hs, Js, 10.0, 4.0, 20.0)
    ok = abs(got["beta"] - 1.7) < 1e-9 and got["admitted"]
    print(f"  [{'PASS' if ok else 'FAIL'}] a planted exponent of 1.7 comes "
          f"back as {got['beta']:.6f} and the fit is admitted")
    bad += not ok

    # the claim Decision 3 now rests on: the lever is gamed by the same anchor
    # shrink as the ratio, so it is no more independent of the anchor
    l_big2, l_small2 = lever(Hd, 10.0), lever(Hd, 0.35)
    ok = l_small2 > l_big2 and l_small2 > MIN_LEVER_DEX > l_big2
    print(f"  [{'PASS' if ok else 'FAIL'}] the same shrink takes the lever "
          f"{l_big2:.3f} -> {l_small2:.3f}, past its {MIN_LEVER_DEX} bound "
          f"too: the lever is not the anchor-free criterion the first version "
          f"claimed")
    bad += not ok

    # and the lever does not imply the ratio, so their nesting on this cohort
    # is a fact about the cohort and not about the criteria
    Hn = np.array([9.0, 9.2, 9.4, 9.5])
    a2 = admits(Hn, 1e5 * (1 - Hn / 10.0) ** 1.5, 10.0, 4.0, 20.0)
    ok = a2["has_lever"] and not a2["clears_field_clause"]
    print(f"  [{'PASS' if ok else 'FAIL'}] a fit spanning 0.5 T on a 10 T "
          f"anchor has the lever ({a2['lever_dex']:.3f}) and fails the clause "
          f"({a2['field_ratio']:.3f}): neither criterion contains the other")
    bad += not ok

    # MIN_PTS is enforced, and was pinned by nothing
    Ht = np.array([0., 1.])
    a3 = admits(Ht, np.array([1e6, 5e5]), 10.0, 4.0, 20.0)
    ok = not a3["enough_points"] and not a3["admitted"]
    print(f"  [{'PASS' if ok else 'FAIL'}] a two-point fit is refused at "
          f"MIN_PTS = {MIN_PTS}")
    bad += not ok

    print("  selftest:", "all guards fire" if not bad
          else f"{bad} GUARD(S) DID NOT FIRE")
    return bad


def report():
    """What each decision costs, on the repaired cohort."""
    import os
    import pandas as pd
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ar", os.path.join("analysis", "apply_anchor_repairs.py"))
    ar = importlib.util.module_from_spec(spec)
    sys.modules["ar"] = ar
    spec.loader.exec_module(ar)

    mb = pd.read_csv(ar.MASTER_B)
    rep_path = ar.FITS_B.replace(".csv", "_repaired.csv")
    fb = pd.read_csv(rep_path if os.path.exists(rep_path) else ar.FITS_B)
    found = ar.reproduce_B(mb, pd.read_csv(ar.FITS_B))

    rows = []
    for i, r in fb.iterrows():
        hit = found.get(i)
        if not hit or str(r.get("withdrawn", "")) not in ("", "nan"):
            continue
        name, _ = hit
        key = (r.arxiv_id if r.arxiv_id in set(mb.arxiv_id) else r.paper_key)
        g = None
        for nm, gg in ar.slice_for(mb, "arxiv_id", key, "temperature_K",
                                   r.fixed_axis_value,
                                   ("doping_or_composition", "sample_form",
                                    "figure_id", "notes")):
            if nm == name:
                g = gg
                break
        if g is None or not len(g):
            continue
        hc2 = r.get("Hc2_repaired", r.Hc2_T_used)
        tc = r.get("Tc_repaired", r.Tc_K_anchor)
        H = g.field_T.to_numpy(float)
        J = g.Jc_A_per_cm2.to_numpy(float)
        # the DEPOSITED retention set, cut at the deposited anchor. Re-cutting
        # at a larger repaired anchor admits points the deposited fit never had
        # and inflates the span, which is the move apply_anchor_repairs.py
        # refuses; doing it here credited four phpro.2015.06.160 fits with
        # clearing a bound the repair records them as failing.
        dep = H < hit[1] * r.Hc2_T_used
        a = admits(H[dep], J[dep], hc2, r.fixed_axis_value, tc)
        b0, _, _ = fit(H[dep], J[dep], hc2)   # same retained set, no floor
        # and against the OLD RULE AS STATED, H < Hc2 with no floor at all.
        # Comparing against the 0.95 reconstruction instead would build the
        # answer in, because 0.95 is 1 - H_FLOOR.
        raw = H < hc2
        b_raw, n_raw, _ = fit(H[raw], J[raw], hc2)
        a.update(beta_nofloor=b0, beta_old_rule=b_raw, n_old_rule=n_raw,
                 paper=r.paper_key, T=r.fixed_axis_value,
                 was_passing=bool(r.ok) and r.physicality == "ok")
        rows.append(a)
    d = pd.DataFrame(rows)
    was = d[d.was_passing]
    print(f"{len(d)} reproduced field-axis fits survive the anchor repair, "
          f"{len(was)} of them from the deposit's passing set")
    print()
    print("what each decision costs, applied to those "
          f"{len(was)} fits, one at a time")
    moved = int((was.beta_nofloor - was.beta).abs().gt(1e-9).sum())
    dmax = float((was.beta_nofloor - was.beta).abs().max())
    print(f"  retention floor of {H_FLOOR} on 1 - H/Hc2 : "
          f"{int((~was.enough_points).sum())} lose too many points, but it "
          f"MOVES the exponent on {moved} fits over "
          f"{was[(was.beta_nofloor - was.beta).abs().gt(1e-9)].paper.nunique()} "
          f"papers, by up to {dmax:.3f}")
    dr = (was.beta_old_rule - was.beta).abs()
    nr = int(dr.gt(1e-9).sum())
    print(f"    measured instead against the old rule AS STATED, H < Hc2 with "
          f"no floor, it moves {nr} fits over "
          f"{was[dr.gt(1e-9)].paper.nunique()} papers by up to {dr.max():.3f}, "
          f"and drops {int((was.n_old_rule - was.n_used).sum())} points in all")
    print(f"    it does NOT cure what it was written for: 1002.0208v2's "
          f"exponents run "
          f"{was[was.paper == '1002.0208v2.pdf'].beta.min():.3f} to "
          f"{was[was.paper == '1002.0208v2.pdf'].beta.max():.3f} with the "
          f"floor against "
          f"{was[was.paper == '1002.0208v2.pdf'].beta_old_rule.min():.3f} to "
          f"{was[was.paper == '1002.0208v2.pdf'].beta_old_rule.max():.3f} "
          f"without it, and all six are still admitted")
    print(f"  temperature clause T/Tc < {TEMP_CLAUSE}      : "
          f"{int((~was.in_temperature_window).sum())} fall outside the window")
    print(f"  field clause      ratio > {FIELD_CLAUSE}      : "
          f"{int((~was.clears_field_clause).sum())} fail it")
    print(f"  (reported, not gated) lever >= {MIN_LEVER_DEX} : "
          f"{int((~was.has_lever).sum())} fall short of a factor of two")
    print()
    print("the clause and the lever against each other")
    tab = pd.crosstab(was.clears_field_clause, was.has_lever)
    tab.index.name = "clears the clause"
    tab.columns.name = "has the lever"
    print(tab.to_string())
    print("  neither is independent of the anchor: shrinking Hc2 until a data "
          "point lands just inside the retention floor maximises BOTH.")
    print()
    print("the cohort under the stated protocol")
    print(f"  admitted: {int(was.admitted.sum())} fits over "
          f"{was[was.admitted].paper.nunique()} papers")
    print(was[was.admitted].groupby("paper").size().to_string())
    print()
    ex = was[~was.admitted]
    print(f"  refused: {len(ex)} fits, by first reason")
    for name, mask in (("too few points", ~ex.enough_points),
                       ("fails the field clause",
                        ex.enough_points & ~ex.clears_field_clause),
                       ("outside the temperature window",
                        ex.enough_points & ex.clears_field_clause
                        & ~ex.in_temperature_window)):
        print(f"    {name:34s} {int(mask.sum())}")
    print(f"    (of the {len(ex)} refused, {int((~ex.has_lever).sum())} also "
          f"fall short of the lever, and {int((was.admitted & ~was.has_lever).sum())} "
          f"ADMITTED fits do too)")
    print()
    print(f"  exponents admitted: median {was[was.admitted].beta.median():.3f}, "
          f"range {was[was.admitted].beta.min():.3f} to "
          f"{was[was.admitted].beta.max():.3f}")
    d.to_csv(os.path.join("audit", "fit_protocol_applied.csv"), index=False)
    print()
    print("written: audit/fit_protocol_applied.csv")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--report" in sys.argv:
        if selftest():
            print("THE PROTOCOL DOES NOT BEHAVE. Nothing below is trustworthy.")
            sys.exit(1)
        print()
        sys.exit(report())
    print(__doc__)
