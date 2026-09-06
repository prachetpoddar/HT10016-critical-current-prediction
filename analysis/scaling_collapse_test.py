"""
scaling_collapse_test.py

Does reduced-variable scaling organize this corpus? A test with a null,
replacing a threshold with no construction.

The problem it replaces. Sec. III.D and the abstract turn on a bar: "Both fall
below the 30% adoption threshold, which marks the level at which a universal
law would substantially exceed the gain observed from family-conditional
aggregation." Nothing in the repository derives 30; it appears only as a
literal in figure code. The quantity the sentence names as its benchmark is the
family-conditional holdout gain, 0.604 dex against 0.613, which is 1.47
percent, so the printed bar is twenty times its own stated benchmark. Worse,
the two are not the same quantity: 13.0 percent is a reduction in within-cell
scatter, 1.47 percent is a reduction in out-of-sample error, and neither
converts into the other.

An attempt to derive the bar by putting family conditioning and reduced-variable
binning on one scale was written and then withdrawn. An independent review
showed that the family grouping is not distinguishable from a random regrouping
of the same compounds into labels with the same profile (excess -2.4 percent on
the curve unit, +0.4 on the raw, probabilities 0.60 and 0.41), so it cannot
define a threshold either. Three of the seven family labels in this cohort are
a single compound from a single paper.

What replaces it. A collapse claim is a claim that particular coordinates carry
structure, so it should be tested against coordinates that do not. Two tests,
both of which the reduced-variable scaling fails.

  Rotation. Standardize the two reduced coordinates and bin on a grid rotated
  by a random angle. The geometry is unchanged, the cloud's local contiguity is
  unchanged, and only the meaning of the axes is destroyed. If reduced
  temperature and reduced field are the right coordinates, the physical grid
  should beat the rotated ones.

  Unreduced variables. Bin the same records on laboratory temperature and
  applied field, without dividing by the critical scales. If dividing through
  is what organizes the data, the reduced grid should win.

Why a rotation null and not the label shuffle used earlier. Shuffling labels
over records destroys contiguity as well as meaning, so any local binning of a
two-dimensional cloud beats it. Random-coordinate binning measures at -0.02
percent under that null, which is true and tells us nothing. The rotation keeps
everything except the claim under test.

The cohort is the point-level rebuild of Sec. III.D from data/reextraction,
described in analysis/rebuild_reduced_variable_scaling.py. It is not the
manuscript's cohort, which cannot be reconstructed.

Run from the repository root.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rebuild_reduced_variable_scaling import (GRID, MIN_N,  # noqa: E402
                                              join_scales, load_points)

OUT = os.path.join("audit", "retrace_20260906", "scaling_collapse_test.csv")
ROTATIONS = 400
BOOTSTRAP = 500
SEED = 20260906
# The duplicate digitisation of one figure that the sibling script reports as
# its largest single sensitivity. Kept in the primary and removed in the sweep.
DUPLICATE = "1611_08455v1_fig5b_bothsamples_points.csv"


def frame():
    m = join_scales(load_points())
    t = m.temperature_K.to_numpy(float) / m.Tc_anchor_K.to_numpy(float)
    h = m.field_T.to_numpy(float) / m.Hc2_anchor_T.to_numpy(float)
    keep = (t >= 0) & (t < 0.9) & (h >= 0) & (h < 0.9)
    d = pd.DataFrame(dict(
        t=t[keep], h=h[keep],
        T=m.temperature_K.to_numpy(float)[keep],
        H=m.field_T.to_numpy(float)[keep],
        y=np.log10(m.Jc_A_per_cm2.to_numpy(float)[keep]),
        paper=m.identifier.to_numpy()[keep],
        compound=m.compound.to_numpy()[keep],
        family=m.substructure_family.to_numpy()[keep],
        src=m.source_file.to_numpy()[keep],
        series=m.series.to_numpy()[keep]))
    d["curve"] = (d.paper.astype(str) + "|" + d.src.astype(str) + "|"
                  + d.series.astype(str))
    dropped = int((~keep).sum())
    return d, dropped


def cell_index(a, b, n=GRID):
    """Equal-width bins over the occupied range of each coordinate.

    The occupied range rather than a fixed 0 to 0.9 window, because the
    unreduced comparison has no fixed window and the two have to be binned the
    same way. On the reduced coordinates the fixed window gives 46.2 percent
    and the occupied range 39.3; both are reported.
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    wa = (a.max() - a.min()) / n or 1.0
    wb = (b.max() - b.min()) / n or 1.0
    ai = np.clip(np.floor((a - a.min()) / wa).astype(int), 0, n - 1)
    bi = np.clip(np.floor((b - b.min()) / wb).astype(int), 0, n - 1)
    return ai * 1000 + bi


def collapse(y, g, stat="median"):
    """Within-cell scatter against the global scatter, over the used records.

    Returns None when no cell reaches MIN_N, which is a real outcome and not
    a zero.
    """
    d = pd.DataFrame(dict(y=np.asarray(y, float), g=np.asarray(g)))
    c = d.groupby("g").y.agg(["size", "std"])
    c = c[(c["size"] >= MIN_N) & c["std"].notna()]
    if c.empty:
        return None
    used = d[d.g.isin(c.index)]
    glob = float(used.y.std(ddof=1))
    if stat == "median":
        w = float(c["std"].median())
    elif stat == "mean":
        w = float(c["std"].mean())
    elif stat == "pooled":
        n = c["size"].to_numpy(float)
        s = c["std"].to_numpy(float)
        w = float(np.sqrt(((n - 1) * s ** 2).sum() / (n.sum() - len(n))))
    else:
        raise SystemExit("stat must be median, mean or pooled")
    return dict(cells=len(c), records=len(used),
                reduction=100 * (1 - w / glob))


def rotation_null(d, rng, stat="median", draws=ROTATIONS):
    """The physical grid against grids rotated on the same standardized axes."""
    u = (d.t.to_numpy() - d.t.mean()) / d.t.std()
    v = (d.h.to_numpy() - d.h.mean()) / d.h.std()
    obs = collapse(d.y, cell_index(u, v), stat)
    vals, cells = [], []
    for _ in range(draws):
        a = rng.uniform(0, 2 * np.pi)
        r = collapse(d.y, cell_index(u * np.cos(a) - v * np.sin(a),
                                     u * np.sin(a) + v * np.cos(a)), stat)
        if r:
            vals.append(r["reduction"])
            cells.append(r["cells"])
    vals = np.asarray(vals)
    return obs, vals, np.asarray(cells)


def compound_purity(d, g):
    """How many compounds a cell holds. A grid that separates compounds is
    not collapsing them, whatever its scatter statistic says."""
    s = pd.DataFrame(dict(g=g, compound=d.compound.to_numpy(),
                          y=d.y.to_numpy()))
    c = s.groupby("g").y.size()
    c = c[c >= MIN_N]
    u = s[s.g.isin(c.index)]
    n = u.groupby("g").compound.nunique()
    return float(n.median()), int((n == 1).sum()), len(n)


def cluster_bootstrap(d, build, rng, draws=BOOTSTRAP):
    """Resample whole curves, because points inside one are not independent."""
    curves = d.curve.unique()
    by = {c: g for c, g in d.groupby("curve")}
    out = []
    for _ in range(draws):
        pick = rng.choice(curves, size=len(curves), replace=True)
        s = pd.concat([by[c] for c in pick], ignore_index=True)
        v = build(s)
        if v is not None:
            out.append(v)
    a = np.asarray(out, float)
    return float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))


def main():
    d, dropped = frame()
    rng = np.random.default_rng(SEED)
    print("does reduced-variable scaling organize this corpus\n")
    print("   %d records from %d papers, %d compounds, %d families, "
          "%d curves; %d points fall outside the 0 to 0.9 window"
          % (len(d), d.paper.nunique(), d.compound.nunique(),
             d.family.nunique(), d.curve.nunique(), dropped))

    rows = []

    # ---- test 1: the physical axes against rotations of themselves --------
    print("\n   1. the reduced axes against random rotations of themselves")
    for stat in ("median", "pooled", "mean"):
        obs, vals, cells = rotation_null(d, rng, stat)
        p = float((vals >= obs["reduction"]).mean())
        print("      %-7s observed %6.2f%% on %d cells;  rotated %6.2f%% "
              "(%d to %d cells);  p(rotated at least as good) %.3f"
              % (stat, obs["reduction"], obs["cells"], vals.mean(),
                 cells.min(), cells.max(), p))
        rows.append(dict(test="rotation", statistic=stat,
                         observed=obs["reduction"], null_mean=float(vals.mean()),
                         p=p, cells=obs["cells"]))

    # ---- test 2: reduced against unreduced coordinates --------------------
    print("\n   2. reduced coordinates against the laboratory coordinates")
    print("      %-28s %6s %9s   %s"
          % ("binned on", "cells", "reduction", "compounds per cell"))
    pairs = (("T/Tc and H/Hc2,0", d.t, d.h),
             ("T/Tc and H", d.t, d["H"]),
             ("T and H/Hc2,0", d["T"], d.h),
             ("T and H", d["T"], d["H"]))
    for name, a, b in pairs:
        g = cell_index(a, b)
        r = collapse(d.y, g)
        med, pure, ncell = compound_purity(d, g)
        print("      %-28s %6d %8.2f%%   median %.1f, %d of %d hold one"
              % (name, r["cells"], r["reduction"], med, pure, ncell))
        rows.append(dict(test="coordinates", statistic=name,
                         observed=r["reduction"], cells=r["cells"],
                         median_compounds=med, single_compound_cells=pure))

    # ---- the interval on the headline, resampling curves ------------------
    print("\n   3. cluster bootstrap over curves, %d draws. The difference is\n"
          "      paired on the same resampled curves, because two marginal\n"
          "      intervals that overlap can still bracket a difference that\n"
          "      never changes sign." % BOOTSTRAP)
    curves = d.curve.unique()
    by = {c: g for c, g in d.groupby("curve")}
    red, raw, dif = [], [], []
    for _ in range(BOOTSTRAP):
        pick = rng.choice(curves, size=len(curves), replace=True)
        s = pd.concat([by[c] for c in pick], ignore_index=True)
        a = collapse(s.y, cell_index(s.t, s.h))
        b = collapse(s.y, cell_index(s["T"], s["H"]))
        if a and b:
            red.append(a["reduction"])
            raw.append(b["reduction"])
            dif.append(b["reduction"] - a["reduction"])
    red, raw, dif = map(np.asarray, (red, raw, dif))
    o_red = collapse(d.y, cell_index(d.t, d.h))["reduction"]
    o_raw = collapse(d.y, cell_index(d["T"], d["H"]))["reduction"]
    print("      reduced          %6.2f%%  [%.2f, %.2f]"
          % (o_red, np.percentile(red, 2.5), np.percentile(red, 97.5)))
    print("      unreduced        %6.2f%%  [%.2f, %.2f]"
          % (o_raw, np.percentile(raw, 2.5), np.percentile(raw, 97.5)))
    print("      the difference   %6.2f%%  [%.2f, %.2f], and the reduced "
          "coordinates win on %.1f%% of draws"
          % (o_raw - o_red, np.percentile(dif, 2.5), np.percentile(dif, 97.5),
             100 * float((dif <= 0).mean())))
    rows.append(dict(test="bootstrap", statistic="reduced", observed=o_red,
                     lo=float(np.percentile(red, 2.5)),
                     hi=float(np.percentile(red, 97.5))))
    rows.append(dict(test="bootstrap", statistic="unreduced", observed=o_raw,
                     lo=float(np.percentile(raw, 2.5)),
                     hi=float(np.percentile(raw, 97.5))))
    rows.append(dict(test="bootstrap", statistic="unreduced minus reduced",
                     observed=o_raw - o_red,
                     lo=float(np.percentile(dif, 2.5)),
                     hi=float(np.percentile(dif, 97.5)),
                     p=float((dif <= 0).mean())))

    # ---- the conventions that were found to move the answer ---------------
    print("\n   4. the conventions an independent review found to move it")
    base = collapse(d.y, cell_index(d.t, d.h))["reduction"]
    print("      %-46s %8s %8s" % ("", "reduced", "raw"))
    print("      %-46s %7.2f%% %7.2f%%"
          % ("as computed above", base,
             collapse(d.y, cell_index(d["T"], d["H"]))["reduction"]))
    dd = d[d.src != DUPLICATE]
    print("      %-46s %7.2f%% %7.2f%%"
          % ("without the duplicate digitisation of one figure",
             collapse(dd.y, cell_index(dd.t, dd.h))["reduction"],
             collapse(dd.y, cell_index(dd["T"], dd["H"]))["reduction"]))
    for fam in sorted(d.family.unique()):
        s = d[d.family != fam]
        if s.compound.nunique() < 3:
            continue
        r1 = collapse(s.y, cell_index(s.t, s.h))
        r2 = collapse(s.y, cell_index(s["T"], s["H"]))
        print("      %-46s %7.2f%% %7.2f%%"
              % ("without " + fam, r1["reduction"], r2["reduction"]))
        rows.append(dict(test="leave one family out", statistic=fam,
                         observed=r1["reduction"], raw=r2["reduction"]))
    for n in (3, 5, 8, 12):
        import rebuild_reduced_variable_scaling as R
        keep = R.MIN_N
        R.MIN_N = n
        globals()["MIN_N"] = n
        r1 = collapse(d.y, cell_index(d.t, d.h))
        r2 = collapse(d.y, cell_index(d["T"], d["H"]))
        print("      %-46s %7.2f%% %7.2f%%"
              % ("minimum cell size %d" % n, r1["reduction"], r2["reduction"]))
        R.MIN_N = keep
        globals()["MIN_N"] = keep

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("\n   wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
