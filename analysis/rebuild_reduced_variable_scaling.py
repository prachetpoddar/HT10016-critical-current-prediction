"""
rebuild_reduced_variable_scaling.py

Rebuild the reduced-variable scaling test from point-level data.

Why. data/reduced_variable_scaling.csv is the deepest artifact behind Sec.
III.D: it is aggregated to 66 cells, git carries it only in the release commit,
no script in the repository generates it, and no point-level table sits behind
it. Its arithmetic reproduces exactly, and nothing earlier than its arithmetic
can be checked. Its 5422 records also exceed every deposited census: the whole
pre-withdrawal corpus is 4146 extracted points and the rows flagged fully
fittable carry 2383.

This does not reproduce that table, which is not possible, and it does not
settle the claim either. What it establishes is narrower and more useful: the
13.0 percent figure depends on a convention the manuscript never states, and
plausible alternatives span 9 to 46 percent, crossing the 30 percent adoption
threshold.

The cohort is NOT the manuscript's. It is 27 papers of digitised points from
data/reextraction/, joined to the critical scales in the provenance table, and
the script prints its coverage rather than implying equivalence.

An earlier version of this script reported that the refutation was confirmed
and strengthened, at 8.66 percent. That was withdrawn. Its record key grouped
by (paper, measurement temperature), which merges distinct samples measured at
the same temperature in one paper: 19 of 133 such groups swallow two to five
real curves, and they are exactly the papers whose within-paper spread is the
physics, irradiated against unirradiated, five dopants, four samples. On the
real curve key the figure is 15.97 percent, above the manuscript rather than
below it.

The protocol is the manuscript's, from Sec. III.D: nine equal-width bins of
0.1 in T/Tc and nine in H/Hc2,0 spanning 0 to 0.9, cells retained at five
records or more, the statistic the median within-cell standard deviation of
log10 Jc against the global standard deviation over the same records. Both
reduction scales are reported, and so is the pooled within-cell alternative,
because the two differ by about a factor of two.

The 400-draw critical-field perturbation of Sec. III.D has no script and no
deposited output either, so it is rebuilt here on the same input.

Run from the repository root.
"""
import glob
import os
import re

import numpy as np
import pandas as pd

OUT_DIR = os.path.join("audit", "retrace_20260906")
GRID, WIDTH, MIN_N = 9, 0.1, 5
PERTURB_DRAWS, PERTURB_SIGMA, THRESHOLD = 400, 0.35, 30.0
SEED = 20260906
# The tier that Sec. III.D perturbs: critical fields that are not read from
# the paper itself.
ESTIMATED = ("literature catalog", "Tier_3", "Tier_4")


def norm(s):
    s = re.sub(r"\.pdf$", "", str(s))
    s = re.sub(r"^(elsevier|springer|iop)_", "", s)
    return s.replace("/", "_").replace(".", "_").lower()


def load_points():
    """Every digitised point that carries a temperature, a field and a Jc."""
    frames = []
    for f in sorted(set(glob.glob(os.path.join("data", "reextraction",
                                               "*.csv")))):
        d = pd.read_csv(f)
        if {"paper_id", "series", "temperature_K", "field_T",
                "Jc_A_per_cm2"} <= set(d.columns):
            d = d[["paper_id", "series", "temperature_K", "field_T",
                   "Jc_A_per_cm2"]]
            frames.append(d.assign(source_file=os.path.basename(f)))
    if not frames:
        raise SystemExit("no point files under data/reextraction")
    p = pd.concat(frames, ignore_index=True)
    p = p.dropna(subset=["temperature_K", "field_T", "Jc_A_per_cm2"])
    p = p[p.Jc_A_per_cm2 > 0]
    p["key"] = p.paper_id.map(norm)
    return p


def join_scales(p):
    prov = pd.read_csv(os.path.join("data",
                                    "provenance_table_fitcohort_full.csv"))
    prov["key"] = prov.identifier.map(norm)
    cols = ["key", "identifier", "compound", "substructure_family",
            "Tc_anchor_K", "Hc2_anchor_T", "Hc2_provenance", "contributes"]
    m = p.merge(prov[cols], on="key", how="left")
    missing = sorted(set(p.key) - set(prov.key))
    if missing:
        raise SystemExit("no provenance row for: %s" % ", ".join(missing))
    bad = m[m.Tc_anchor_K.isna() | m.Hc2_anchor_T.isna()]
    if len(bad):
        raise SystemExit("%d points have no critical scale: %s"
                         % (len(bad), sorted(bad.identifier.unique())))
    return m


def binned(m, hc2, unit="curve"):
    """The 9 by 9 grid, filtered as Sec. III.D filters it.

    unit fixes what one record in a cell is, and it decides the answer.

      "raw"    every digitised point. A densely digitised curve puts dozens of
               points into one cell, so the within-cell standard deviation
               then measures how smooth that one curve is and not how well
               different papers agree. On this input that returns a 46 percent
               reduction, which is an artifact of digitisation density and not
               a result.
      "curve"  one record per (paper, source file, series) and cell, which
               is one digitised curve's contribution to that cell. The series
               column is the curve identity; grouping by measurement
               temperature instead merges different samples measured at the
               same temperature.
      "paper"  one record per source paper and cell, which is stricter still.
    """
    t = m.temperature_K.to_numpy(float) / m.Tc_anchor_K.to_numpy(float)
    h = m.field_T.to_numpy(float) / np.asarray(hc2, float)
    keep = (t >= 0) & (t < GRID * WIDTH) & (h >= 0) & (h < GRID * WIDTH)
    d = pd.DataFrame(dict(
        pid=m.identifier.to_numpy()[keep],
        src=m.source_file.to_numpy()[keep],
        series=m.series.to_numpy()[keep],
        y=np.log10(m.Jc_A_per_cm2.to_numpy(float)[keep]),
        ti=np.floor(t[keep] / WIDTH).astype(int),
        hi=np.floor(h[keep] / WIDTH).astype(int)))
    if unit == "curve":
        d = d.groupby(["pid", "src", "series", "ti", "hi"],
                      as_index=False).y.mean()
    elif unit == "paper":
        d = d.groupby(["pid", "ti", "hi"], as_index=False).y.mean()
    elif unit != "raw":
        raise SystemExit("unit must be raw, curve or paper")
    cells = d.groupby(["ti", "hi"]).y.agg(["size", "mean", "std"])
    cells = cells[cells["size"] >= MIN_N]
    return d, cells


def statistic(d, cells):
    """Median within-cell SD, global SD over the same records, and both
    reduction scales. The pooled alternative is returned beside it."""
    if cells.empty:
        return None
    used = d.merge(cells.reset_index()[["ti", "hi"]], on=["ti", "hi"])
    med = float(cells["std"].median())
    glob = float(used.y.std(ddof=1))
    n = cells["size"].to_numpy(float)
    s = cells["std"].to_numpy(float)
    pooled = float(np.sqrt(((n - 1) * s ** 2).sum() / (n.sum() - len(n))))
    return dict(cells=len(cells), records=int(used.shape[0]),
                sizes=cells["size"].to_numpy(float),
                median_within=med, global_sd=glob, pooled_within=pooled,
                sd_reduction=100 * (1 - med / glob),
                var_reduction=100 * (1 - (med / glob) ** 2),
                sd_reduction_pooled=100 * (1 - pooled / glob),
                var_reduction_pooled=100 * (1 - (pooled / glob) ** 2))


def ks_two_sample(a, b):
    """Two-sample Kolmogorov-Smirnov, without a scipy dependency."""
    a = np.sort(np.asarray(a, float))
    b = np.sort(np.asarray(b, float))
    grid = np.concatenate([a, b])
    ca = np.searchsorted(a, grid, "right") / a.size
    cb = np.searchsorted(b, grid, "right") / b.size
    d = float(np.max(np.abs(ca - cb)))
    en = np.sqrt(a.size * b.size / float(a.size + b.size))
    lam = (en + 0.12 + 0.11 / en) * d
    p = 2.0 * sum((-1) ** (k - 1) * np.exp(-2.0 * k * k * lam * lam)
                  for k in range(1, 101))
    return d, float(min(max(p, 0.0), 1.0))


def shared_scale(m):
    """Points in papers that share an identical critical-scale pair."""
    pair = m.drop_duplicates("identifier")[["identifier", "Tc_anchor_K",
                                            "Hc2_anchor_T"]]
    dup = pair.groupby(["Tc_anchor_K", "Hc2_anchor_T"]).identifier.transform(
        "size") > 1
    return m.identifier.isin(pair[dup].identifier).sum()


def main():
    if not os.path.isdir("data"):
        raise SystemExit("run from the repository root")
    os.makedirs(OUT_DIR, exist_ok=True)
    m = join_scales(load_points())

    print("cohort actually available, which is NOT the manuscript's\n")
    print("   digitised points with T, H and Jc      %6d" % len(m))
    print("   source papers                          %6d"
          % m.identifier.nunique())
    print("   compound labels                        %6d" % m.compound.nunique())
    print("   substructure families                  %6d"
          % m.substructure_family.nunique())
    live = m[m.contributes != "none, withdrawn"]
    print("   points from papers not withdrawn       %6d" % len(live))
    print("   the manuscript's cohort is 23 fully fittable compounds and a")
    print("   binning table of 5422 records, neither of which this is. The")
    print("   compound labels above overstate diversity: Ba(FeAs)2 and")
    print("   BaFe2As2 are one stoichiometry, as are Fe2TeSe, FeTeSe and")
    print("   FeTe0.5Se0.5, so the materials number about a dozen.")
    print("   Sixteen of the 27 papers take their critical field from a")
    print("   shared substructure constant, so for %d of the %d points the"
          % (int(shared_scale(m)), len(m)))
    print("   reduced transformation is a common affine rescale.\n")

    print("what one record in a cell is, and why it decides the answer\n")
    dep = pd.read_csv(os.path.join("data", "reduced_variable_scaling.csv"))
    print("   %-7s %6s %7s %8s %8s %8s %8s   %s"
          % ("unit", "cells", "records", "median", "global", "SD red",
             "var red", "cell sizes vs the deposited table"))
    for unit in ("raw", "curve", "paper"):
        st = statistic(*binned(m, m.Hc2_anchor_T, unit))
        ks = ks_two_sample(st["sizes"], dep.n.to_numpy(float))
        print("   %-7s %6d %7d %8.4f %8.4f %7.2f%% %7.2f%%   D=%.3f p=%.3g"
              % (unit, st["cells"], st["records"], st["median_within"],
                 st["global_sd"], st["sd_reduction"], st["var_reduction"],
                 ks[0], ks[1]))
    print()
    print("   The deposited table holds 66 cells of mean size 82 and maximum")
    print("   594. That distribution is indistinguishable from the raw")
    print("   point-level binning above and is incompatible with either")
    print("   collapsed unit, so the deposited records are points and the")
    print("   like-for-like comparison is the raw row. That row does not")
    print("   confirm the manuscript: it gives a far larger reduction.")
    print("   The collapsed rows are what the test is about physically, and")
    print("   they bracket the manuscript's 13.0 from both sides.\n")

    print("two choices the manuscript does not state, and what they cost\n")
    for drop, label in ((None, "both digitisations kept"),
                        ("1611_08455v1_fig5b_points.csv",
                         "the sparser duplicate dropped"),
                        ("1611_08455v1_fig5b_bothsamples_points.csv",
                         "the denser duplicate dropped")):
        mm = m if drop is None else m[m.source_file != drop]
        st = statistic(*binned(mm, mm.Hc2_anchor_T, "curve"))
        print("   %-32s SD %6.2f%%  variance %6.2f%%"
              % (label, st["sd_reduction"], st["var_reduction"]))
    print("   1611_08455v1 fig 5b is digitised twice, into a 270-row file and")
    print("   a 553-row file that share identical values. Nothing in the")
    print("   deposit says which is canonical, and the choice moves the")
    print("   answer by 6.9 points against a 4.3-point gap to 13.0.\n")

    los = []
    for pid in sorted(m.identifier.unique()):
        st = statistic(*binned(m[m.identifier != pid],
                               m[m.identifier != pid].Hc2_anchor_T, "curve"))
        if st:
            los.append((pid, st["sd_reduction"], st["var_reduction"]))
    sd_lo = [v for _, v, _ in los]
    print("   leave one paper out, on the curve unit: SD reduction ranges")
    print("   %.2f%% to %.2f%%, and exceeds the manuscript's 13.0 in %d of %d"
          % (min(sd_lo), max(sd_lo), sum(v > 13.0 for v in sd_lo), len(sd_lo)))
    print("   refits. Thirty-nine to sixty cells cannot discriminate a")
    print("   four-point difference.\n")

    base = statistic(*binned(m, m.Hc2_anchor_T, "curve"))
    if base is None:
        raise SystemExit("no cell reached the five-record threshold")
    print("the curve unit in full, for the record")
    print("   populated cells                        %6d" % base["cells"])
    print("   records inside them                    %6d" % base["records"])
    print("   median within-cell SD                  %9.4f dex"
          % base["median_within"])
    print("   global SD over the same records        %9.4f dex"
          % base["global_sd"])
    print("   reduction, standard-deviation scale    %8.2f%%   "
          "manuscript 13.0" % base["sd_reduction"])
    print("   reduction, variance scale              %8.2f%%   "
          "manuscript 24.3" % base["var_reduction"])
    print("   pooled within-cell SD                  %9.4f dex"
          % base["pooled_within"])
    print("   reduction from the pooled SD           %8.2f%% and %.2f%%\n"
          % (base["sd_reduction_pooled"], base["var_reduction_pooled"]))
    est = m.Hc2_provenance.astype(str).str.startswith(ESTIMATED)
    papers_est = m[est].identifier.nunique()
    print("perturbing the critical fields that are not paper-reported")
    print("   points on an estimated critical field  %6d of %d"
          % (int(est.sum()), len(m)))
    print("   papers affected                        %6d of %d"
          % (papers_est, m.identifier.nunique()))
    rng = np.random.default_rng(SEED)
    per_paper = sorted(m[est].identifier.unique())
    sd_draws, var_draws = [], []
    for _ in range(PERTURB_DRAWS):
        factor = dict(zip(per_paper,
                          rng.lognormal(0.0, PERTURB_SIGMA, len(per_paper))))
        hc2 = m.Hc2_anchor_T.to_numpy(float) * np.array(
            [factor.get(i, 1.0) if e else 1.0
             for i, e in zip(m.identifier, est)])
        st = statistic(*binned(m, hc2, "curve"))
        if st is not None:
            sd_draws.append(st["sd_reduction"])
            var_draws.append(st["var_reduction"])
    sd_draws = np.array(sd_draws)
    var_draws = np.array(var_draws)
    print("   draws completed                        %6d of %d"
          % (len(sd_draws), PERTURB_DRAWS))
    for label, arr in (("standard-deviation scale", sd_draws),
                       ("variance scale", var_draws)):
        print("   %-38s median %6.2f%%  range %6.2f to %6.2f  "
              "reaching %g%%: %d"
              % (label, np.median(arr), arr.min(), arr.max(), THRESHOLD,
                 int((arr >= THRESHOLD).sum())))
    print("\n   the manuscript reports zero of 400 draws reaching the "
          "threshold on\n   the standard-deviation scale and 9 of 400 on the "
          "variance scale.\n")
    print("what this rebuild does and does not establish\n")
    print("   It does not confirm the 13.0 and 24.3 figures and it does not")
    print("   contradict them. On a different cohort the answer runs from")
    print("   8.9 to 46.2 percent depending on what one record is, swings")
    print("   6.9 points on an undocumented duplicate file, and ranges over")
    print("   24 points under leave-one-paper-out.")
    print("   What it does establish is that the statistic is not robust to")
    print("   a convention the manuscript never states. A referee who asks")
    print("   what a record is can move the reduction across the 30 percent")
    print("   adoption threshold without leaving the deposit.")

    pd.DataFrame([base]).to_csv(
        os.path.join(OUT_DIR, "reduced_variable_rebuild.csv"), index=False)
    pd.DataFrame(dict(sd_reduction=sd_draws,
                      var_reduction=var_draws)).to_csv(
        os.path.join(OUT_DIR, "reduced_variable_perturbation.csv"),
        index=False)
    print("\nwrote %s and the perturbation draws beside it" % OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
