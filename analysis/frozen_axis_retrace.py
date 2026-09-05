#!/usr/bin/env python3
"""
frozen_axis_retrace.py

The whole cohort, retraced through the protocol that built it: freeze one of the
two factors of Eq. (1), mobilise the other, and fit the curve that comes out.

The mechanism. Eq. (1) is a product of a temperature factor and a field factor.
To fit either exponent you hold one variable fixed and sweep the other. On the
field axis you fix a temperature and sweep H against (1 - H/Hc2). On the
temperature axis you fix a field and sweep T against (1 - T/Tc). In both cases
the frozen factor's own scale, Hc2 or Tc, is the anchor, and the anchor does
three jobs at once:

  1. it selects which points are kept, because the fitter drops points near and
     above Hc2
  2. it forms the abscissa, log(1 - H/Hc2)
  3. it forms the denominator of the applicability clause, (Hmax - Hmin)/Hc2

So the clause is not a test of whether a measurement covers a physically large
fraction of the upper critical field. It is a comparison of the anchor with the
extraction's own field range.

WHAT IS AND IS NOT A FINDING HERE. An independent review made the distinction
and it has to be kept:

  - that the clause reduces to "the anchor is at most 1/0.3 times the span" is
    ALGEBRA, not a measurement. Reporting a high reproduction rate for it is
    reporting that arithmetic works. It is stated below as an identity.
  - what is empirical is the consequence: which fits that identity admits, and
    the fact that the retention rule is NOT the stated one. `H < Hc2` reproduces
    the deposited statistic for 134 of 153 fits and `H < 0.95 Hc2` for 141, so
    points are dropped below the anchor by a rule the deposit does not state.
  - also empirical: the temperature clause is imposed by truncating the fit
    window against the anchor, and it is imposed on one cohort and not the
    other.

    python3 analysis/frozen_axis_retrace.py
    python3 analysis/frozen_axis_retrace.py --selftest

Run from the repository root. Writes audit/frozen_axis_retrace.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

MASTER = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
          "agent2_dataset_v3_2_2B.csv")
WIDE = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
        "agent2_dataset_v3_2_1.csv")
FITS_H = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_T = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
RE = os.path.join("data", "reextraction")
OUT = os.path.join("audit", "frozen_axis_retrace.csv")
FIELD_CLAUSE = 0.3
TEMP_CLAUSE = 0.7

TRACE = {
    "0806.2839v1.pdf": "0806_2839v1_fig3",
    "0903.0004v2.pdf": "0903_0004v2_fig6b",
    "0906.0444v1.pdf": "0906_0444v1_fig3a",
    "1002.0208v2.pdf": "1002_0208v2_fig5a",
    "1009.4896v1.pdf": "1009_4896v1_fig2b",
    "1104.0477v2.pdf": "1104_0477v2_fig3c",
    "1108.0407v1.pdf": "1108_0407v1_fig5d",
    "1111.3923v1.pdf": "1111_3923v1_fig4a",
    "1502.05345v1.pdf": "1502_05345v1_fig4b_Hc",
    "1611.08455v1.pdf": "1611_08455v1_fig5b_bothsamples",
    "1903.00866v2.pdf": "1903_00866v2_fig4",
    "2012.13723v3.pdf": "2012.13723_fig4",
    "2207.06629v1.pdf": "2207.06629_fig4",
    "2305.10034v1.pdf": "jallcom_2023_170384_fig6c",
    "2308.10492v1.pdf": "2308_10492v1_fig2b",
    "2510.10264v1.pdf": "2510_10264v1_fig4a",
    "2511.19058v1.pdf": "2511_19058v1_fig2b",
}


def grid_of(master, paper, T):
    g = master[(master.arxiv_id == paper) & (np.isclose(master.temperature_K, T))]
    if not len(g):
        return None
    return np.unique(g.field_T.to_numpy(float))


def normalised_range(grid, hc2):
    """The deposited statistic, recomputed from the grid and the anchor alone."""
    kept = grid[grid < hc2]
    if len(kept) < 2:
        return np.nan
    return (kept.max() - kept.min()) / hc2


def gate_floor(grid):
    """The smallest applicability ratio any anchor INSIDE the data can produce.

    For an anchor in (g_k, g_{k+1}] the kept points run g_0 to g_k, so the ratio
    is (g_k - g_0)/Hc2 and is smallest at Hc2 = g_{k+1}. Taking the minimum over
    k gives the floor. If the floor is above the clause, no anchor lying inside
    the paper's own field range can fail the clause, whatever its value.

    The floor is set by the largest RATIO between neighbouring grid points near
    the bottom of the grid, not by how many points there are. A grid starting at
    zero with uniform steps has a floor of one half, because the worst anchor
    sits just above the second point. Only a grid whose steps grow faster than
    1/0.3 between neighbours, a decade-spaced log grid for instance, can be
    failed by an anchor inside its own range. The first version of this
    docstring said "coarse", which is not what the arithmetic depends on, and
    the self-test caught it.
    """
    if len(grid) < 3:
        return np.nan
    g0 = grid.min()
    return min((grid[k] - g0) / grid[k + 1] for k in range(1, len(grid) - 1))


def retention_sweep(master, fits, factors=(1.00, 0.98, 0.95, 0.90)):
    """Which retention rule actually reproduces the deposited statistic.

    The deposit says points at or above Hc2 are dropped. If that were the rule,
    kept = grid < Hc2 would reproduce the deposited normalised range everywhere
    it can be reconstructed. It does not, and a stricter cut does better, so
    there is a second retention criterion the deposit does not state.
    """
    out = {}
    for fac in factors:
        n = 0
        for _, r in fits.iterrows():
            grid = grid_of(master, r.paper_key, r.fixed_axis_value)
            if grid is None:
                continue
            kept = grid[grid < fac * r.Hc2_T_used]
            if len(kept) < 2:
                continue
            if abs((kept.max() - kept.min()) / r.Hc2_T_used
                   - r.H_axis_range_normalized) < 1e-4:
                n += 1
        out[fac] = n
    return out


def field_axis(master, fits):
    rows = []
    for _, r in fits.iterrows():
        grid = grid_of(master, r.paper_key, r.fixed_axis_value)
        if grid is None:
            continue
        rows.append(dict(
            paper=r.paper_key, T=r.fixed_axis_value,
            passing=bool(r.ok) and r.physicality == "ok",
            # the FIELD CLAUSE specifically. `passing` also fails for
            # beta_extreme, which is a different gate, and mixing the two
            # understated the reproduction rate by five fits.
            clears_field_clause=r.physicality != "H_axis_applicability_bound",
            hc2=r.Hc2_T_used, top=grid.max(), span=grid.max() - grid.min(),
            hc2_over_top=r.Hc2_T_used / grid.max(),
            deposited_ratio=r.H_axis_range_normalized,
            recomputed_ratio=normalised_range(grid, r.Hc2_T_used),
            gate_floor=gate_floor(grid),
        ))
    d = pd.DataFrame(rows)
    d["reproduced"] = (d.recomputed_ratio - d.deposited_ratio).abs() < 1e-4
    return d


def best_threshold(x, label):
    """The single cut on x that best reproduces the boolean label.

    Candidate cuts are the observed values themselves, not rounded copies of
    them: rounding the candidate down excludes the point sitting exactly on its
    own optimal cut, which cost one fit here and would cost a whole tie block
    elsewhere.

    Returned with the majority-class baseline, because a lopsided label is
    reproduced to its own base rate by a cut at either extreme and the raw
    accuracy alone says nothing.
    """
    x = np.asarray(x, float)
    label = np.asarray(label, bool)
    base = max(label.mean(), 1 - label.mean())
    best = (np.nan, 0.0)
    for thr in np.unique(x):
        acc = float(((x <= thr) == label).mean())
        if acc > best[1]:
            best = (float(thr), acc)
    return best[0], best[1], float(base)


def selftest():
    bad = 0
    # 1. The reconstruction must be sensitive to the anchor.
    grid = np.array([0., 1., 2., 5., 10., 15., 20., 30., 40., 50.])
    a, b = normalised_range(grid, 3.5), normalised_range(grid, 12.5)
    ok = abs(a - 2 / 3.5) < 1e-12 and abs(b - 10 / 12.5) < 1e-12 and a != b
    print(f"  [{'PASS' if ok else 'FAIL'}] normalised range from grid and anchor: "
          f"{a:.4f} at 3.5 T, {b:.4f} at 12.5 T")
    bad += not ok
    # 2. The gate floor must know a coarse grid from a dense one.
    linear = gate_floor(grid)
    dense = gate_floor(np.linspace(0, 50, 200))
    log = gate_floor(np.array([0., 0.01, 0.1, 1., 10., 100.]))
    ok = linear > FIELD_CLAUSE and dense > FIELD_CLAUSE and log < FIELD_CLAUSE
    print(f"  [{'PASS' if ok else 'FAIL'}] gate floor: linear grid {linear:.3f}, "
          f"200-point grid {dense:.3f} (both > {FIELD_CLAUSE}, cannot fail), "
          f"decade log grid {log:.3f} (can fail)")
    bad += not ok
    # 3. A threshold rule must not reproduce a shuffled label.
    rng = np.random.default_rng(0)
    x = rng.lognormal(0, 1.5, 400)
    lab = x <= 3.0
    _, real, base = best_threshold(x, lab)
    shuf = np.median([best_threshold(x, rng.permutation(lab))[1]
                      for _ in range(40)])
    ok = (real - base) > 0.2 and (shuf - base) < 0.05
    print(f"  [{'PASS' if ok else 'FAIL'}] threshold reproduction over the "
          f"{base:.3f} majority baseline: {real:.3f} on a real cut, "
          f"{shuf:.3f} on shuffled labels")
    bad += not ok
    print("  selftest:", "all guards fire" if not bad
          else f"{bad} GUARD(S) DID NOT FIRE")
    return bad


def main():
    if "--selftest" in sys.argv:
        return selftest()
    print("selftest first")
    if selftest():
        print("THE STATISTICS DO NOT BEHAVE. Nothing below is trustworthy.")
        return 1
    print()

    master = pd.read_csv(MASTER)
    fits = pd.read_csv(FITS_H)
    d = field_axis(master, fits)
    os.makedirs("audit", exist_ok=True)
    d.to_csv(OUT, index=False)

    print("=" * 72)
    print("THE FIELD AXIS: freeze T, mobilise H")
    print("=" * 72)
    missing = sorted(set(fits.paper_key) - set(master.arxiv_id))
    print(f"{len(d)} of {len(fits)} fits have a field grid in this extraction "
          f"file. The {len(fits) - len(d)} that do not all belong to "
          f"{', '.join(missing)}, which is keyed in the OTHER extraction file "
          f"and is a key-format mismatch, not a property of the data.")
    print()
    print("IDENTITY, not a measurement. The clause is (Hmax - Hmin)/Hc2 > 0.3 "
          "where Hmax and Hmin are the retained points, so it says exactly")
    print(f"    Hc2 < span / {FIELD_CLAUSE} = {1/FIELD_CLAUSE:.2f} x span")
    print("and where the grid starts at zero and nothing is retained out, "
          "span is the top of the extracted field range. Nothing about the "
          "sample enters. A high reproduction rate for this is arithmetic "
          "working, and is reported only to show the reconstruction is right.")
    thr, acc, base = best_threshold(d.hc2_over_top.to_numpy(),
                                    d.clears_field_clause.to_numpy())
    print(f"    reproduction of the field clause by "
          f"'anchor <= {thr:.2f} x top': {acc*100:.2f}% of {len(d)}, "
          f"baseline {base*100:.1f}%")
    print()
    print("EMPIRICAL. The retention rule is not the one the deposit states.")
    sweep = retention_sweep(master, fits)
    for fac, n in sweep.items():
        mark = "  <- the stated rule" if fac == 1.0 else ""
        print(f"    kept = grid < {fac:.2f} x Hc2 reproduces the deposited "
              f"normalised range for {n} of {len(d)}{mark}")
    print("    so points below the anchor are dropped by a criterion that is "
          "not recorded anywhere. Two checked by hand: s41598-022-24044-5 at "
          "10 K drops its 17.91 T point against an 18 T anchor, and "
          "jallcom.2023.170146 at 10 K drops 4.83 and 4.91 T against 5.0 T.")
    print()
    print("EMPIRICAL. Which anchors the identity admits.")
    print("the anchor divided by the top of the extraction's own field range")
    print(d.groupby("clears_field_clause").hc2_over_top
          .describe(percentiles=[.05, .5, .95]).round(3).to_string())
    print(f"    {int(d.clears_field_clause.sum())} fits over "
          f"{d[d.clears_field_clause].paper.nunique()} papers clear it; "
          f"{int((~d.clears_field_clause).sum())} over "
          f"{d[~d.clears_field_clause].paper.nunique()} papers do not")
    print()
    below = d[d.clears_field_clause & (d.hc2_over_top < 1)]
    print(f"fits clearing the clause whose anchor lies BELOW the top of their "
          f"own extracted data: {len(below)} over {below.paper.nunique()} papers")
    print("    this is NOT by itself a wrong anchor. Data running past the "
          "irreversibility field into the tail is ordinary. What separates the "
          "two cases is how much current sits above the anchor:")
    for p_, g in below.groupby("paper"):
        sub = master[master.arxiv_id == p_]
        frac = []
        for _, rr in g.iterrows():
            gg = sub[np.isclose(sub.temperature_K, rr["T"])]
            if not len(gg):
                continue
            above = gg[gg.field_T >= rr.hc2].Jc_A_per_cm2
            if len(above) and gg.Jc_A_per_cm2.max() > 0:
                frac.append(above.max() / gg.Jc_A_per_cm2.max())
        if frac:
            print(f"      {p_:44s} up to {max(frac)*100:7.2f}% of peak Jc "
                  f"above its own anchor")
    print("    the two at the top of that list are the papers whose EXTRACTION "
          "field axis is wrong: their traced figures end at 4.93 and 4.92 T "
          "against extractions running to 50 and 20. There the anchor is not "
          "the defective quantity.")
    print()
    can = d[d.gate_floor > FIELD_CLAUSE]
    print(f"fits whose field grid has no jump larger than {1/FIELD_CLAUSE:.2f} "
          f"times between neighbours, so no anchor inside the paper's own "
          f"field range can fail the clause: {len(can)} of "
          f"{int(d.gate_floor.notna().sum())} scorable")
    print(f"    of those, {int(can.clears_field_clause.sum())} clear the clause "
          f"and {int((~can.clears_field_clause).sum())} do not; every one that "
          f"does not has an anchor above its own data: "
          f"{'confirmed' if (can[~can.clears_field_clause].hc2_over_top > 1).all() else 'NOT TRUE ON THIS DATA'}")
    print()

    print("=" * 72)
    print("THE TEMPERATURE AXIS: freeze H, mobilise T")
    print("=" * 72)
    t = pd.read_csv(FITS_T)
    t["tmax_over_tc"] = t.T_max / t.Tc_K
    print(f"{len(t)} fits over {t.paper_key.nunique()} papers. Every row has "
          f"ok = True and physicality = ok: this file records no failures at "
          f"all, unlike the field-axis file, so 'all of them pass' is a "
          f"property of the deposit rather than of the fits.")
    print(f"the largest T_max/Tc anywhere is {t.tmax_over_tc.max():.3f}, "
          f"against a clause at {TEMP_CLAUSE}")
    print()
    wide = pd.read_csv(WIDE)
    trunc = kept_full = nodata = 0
    for _, r in t.iterrows():
        e = wide[wide.pdf_name == r.paper_key]
        if not len(e):
            nodata += 1
            continue
        eT = e.temperature_K.to_numpy(float)
        if (eT > r.T_max + 1e-9).any():
            trunc += 1
        else:
            kept_full += 1
    print(f"fits whose extraction carries temperatures ABOVE the fit's own "
          f"T_max, so the window was cut: {trunc} of {trunc + kept_full}")
    print(f"    the remaining {kept_full} were never truncated, so the clause "
          f"was not binding on them")
    rows = []
    for pk, tr in TRACE.items():
        Tc = t.groupby("paper_key").Tc_K.first().get(pk, np.nan)
        e = wide[wide.pdf_name == pk]
        eT = np.unique(np.round(e.temperature_K.to_numpy(float), 2)) if len(e) else np.array([])
        p_ = os.path.join(RE, tr + "_points.csv")
        fT = (np.unique(np.round(pd.read_csv(p_).temperature_K.to_numpy(float), 2))
              if os.path.exists(p_) else np.array([]))
        if not len(eT) or not len(fT) or Tc != Tc:
            continue
        rows.append(dict(paper=pk, ext_above=int((eT / Tc > TEMP_CLAUSE).sum()),
                         fig_above=int((fT / Tc > TEMP_CLAUSE).sum())))
    tt = pd.DataFrame(rows)
    agree = int((tt.ext_above == tt.fig_above).sum())
    print(f"and the extraction itself is not truncated: across the {len(tt)} "
          f"papers with both an extraction and a pixel trace, the number of "
          f"isotherms above {TEMP_CLAUSE} Tc agrees paper by paper in "
          f"{agree} of {len(tt)}, {int(tt.fig_above.sum())} in each total")
    print("    so the clause is imposed at the fit, by cutting the window "
          "against the anchor. The anchor sets the window AND the abscissa of "
          "the same fit.")
    print()
    fh = pd.read_csv(FITS_H)
    ph = fh[(fh.ok == True) & (fh.physicality == "ok")]
    tr_h = ph.fixed_axis_value / ph.Tc_K_anchor
    print(f"the temperature clause is imposed on the temperature axis only: "
          f"{int((tr_h > TEMP_CLAUSE).sum())} of the {len(ph)} passing "
          f"field-axis fits, over "
          f"{ph[tr_h > TEMP_CLAUSE].paper_key.nunique()} papers, sit above it, "
          f"the worst at {tr_h.max():.3f}")
    print()
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
