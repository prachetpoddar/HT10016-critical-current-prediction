#!/usr/bin/env python3
"""
rebuild_temperature_axis.py

Recompute beta_T from the figures rather than audit the deposited values.

analysis/adjudicate_temperature_axis.py answered whether the deposited
temperature exponents reproduce the published figures. They do not. That
settles what has to be withdrawn but produces no replacement. Everything needed
for a replacement now exists: a pixel trace of seventeen of the eighteen Cohort
A figures, and each paper's own reported Tc with the sentence it was read from
(analysis/tc_anchor_audit.py). This script builds the temperature axis from
those two inputs and nothing else.

What it does differently from the deposit, and why.

  Tc.  The paper's own value for the sample whose figure was measured, not a
  constant keyed to an idealised parent-compound string. Six of the deposited
  values were wrong by 5 K or more, all overestimates, and the three largest
  deposited exponents belonged to the three worst.

  Jc.  Read off the figure by the digitiser, not taken from the extraction
  tables, which are 1.0 to 2.3 dex outside the printed panel in six papers and
  carry field axes wrong by two to four orders of magnitude in four.

  Field grid.  A geometric grid across the span every contributing isotherm
  actually covers, chosen from the trace rather than inherited from the
  deposit, so no fit is evaluated at a field the figure does not reach.

  The applicability window.  Eq. (1)'s temperature clause, T/Tc < 0.7, applied
  per point rather than per fit. The deposit never bound on it because its
  inflated Tc values made every window look comfortable: the largest deposited
  coverage was T_max/Tc = 0.694. Under each paper's real Tc the same windows are
  much hotter, and a fit that now runs past 0.7 is refused rather than reported.

The output is a table with the same columns as the deposited one so the two can
be compared directly, plus the columns the deposit lacked: how many points the
fit rests on after the window is applied, the reduced temperature it reaches,
and where its Tc came from.

    python3 analysis/rebuild_temperature_axis.py            # writes the table
    python3 analysis/rebuild_temperature_axis.py --dry-run  # prints only

Run from the repository root.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "analysis")
from tc_anchor_audit import TC_READ
from adjudicate_temperature_axis import TRACE, trace

DEP = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
OUT = os.path.join("data", "temperature_axis_rebuilt_from_figures.csv")

T_MAX_REDUCED = 0.7     # Eq. (1)'s temperature clause, as the manuscript states it
N_FIELDS = 10           # fields per paper, geometric across the common span
MIN_T_PTS = 3           # temperatures needed for a slope
MIN_T_SPAN = 0.15       # dex of log10(1 - T/Tc) needed before a slope means anything
WELL_DETERMINED = 0.25  # SE/|beta| below this counts as well determined


def sample_of(series_name):
    """
    The sample a traced series belongs to, where the trace records one.

    Fig. 5(b) of 1611.08455v1 plots two crystals, A and B, at overlapping
    temperatures, and its trace names them A_7K, B_7K and so on. A fit that
    mixes them is fitting a temperature dependence across two different samples.
    Series named only by temperature return None and are treated as one sample.
    """
    if "_" not in str(series_name):
        return None
    head = str(series_name).split("_")[0]
    return head if head and not head[0].isdigit() else None


def pick_sample(t):
    """The sample contributing the most distinct temperatures, or None."""
    if "series" not in t.columns:
        return None
    labs = {sample_of(s) for s in t.series.unique()}
    labs.discard(None)
    if len(labs) < 2:
        return None
    best, n = None, -1
    for lab in sorted(labs):
        k = t[t.series.map(lambda s: sample_of(s) == lab)].temperature_K.nunique()
        if k > n:
            best, n = lab, k
    return best


def isotherm_exact(t, T, sample=None):
    """
    One traced isotherm, matched on the exact temperature and on one sample.

    Two things this does that the adjudicator's version does not, both forced by
    a defect an independent review found.

    Exact matching. The adjudicator matches within 0.6 K, which is right when an
    extraction's temperature has to be paired with a figure's. Here both sides
    are the figure, so a tolerance only aliases: on 1108.0407v1 it collapsed the
    1.8, 2.0, 2.5 and 3.0 K isotherms onto one another, and the same forty points
    then entered one regression three times under three different x.

    No field clipping. The adjudicator clips a traced field to 1e-4 T so a
    log axis stays defined. Points at or below zero are digitiser noise near
    H = 0; moving them four decades below the panel invents a long interpolation
    segment where the figure has none, and makes the isotherm look as though it
    reaches a field it never plots. They are dropped instead.
    """
    s_ = t[t.temperature_K == T]
    if sample is not None:
        s_ = s_[s_.series.map(lambda v: sample_of(v) == sample)]
    s_ = s_[s_.field_T > 0].sort_values("field_T")
    if len(s_) < MIN_T_PTS:
        return None, None
    x = np.log10(s_.field_T.values.astype(float))
    y = np.log10(s_.Jc_A_per_cm2.values.astype(float))
    if len(y) >= 3:
        y = y.copy()
        y[1:-1] = np.median(np.stack([y[:-2], y[1:-1], y[2:]]), axis=0)
    keep = np.concatenate([[True], np.diff(x) > 0])
    return x[keep], y[keep]


def fit_beta(T, J, Tc):
    """
    Slope of log10 Jc against log10(1 - T/Tc), with its standard error and the
    residual rms. Returns None when the regressor is degenerate.
    """
    T = np.asarray(T, float)
    J = np.asarray(J, float)
    if np.any(T >= Tc) or len(T) < MIN_T_PTS:
        return None
    x = np.log10(1.0 - T / Tc)
    y = np.log10(J)
    if np.ptp(x) < MIN_T_SPAN:
        return None
    n = len(x)
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    rms = float(np.sqrt(np.mean(resid ** 2)))
    if n > 2:
        s2 = float(np.sum(resid ** 2) / (n - 2))
        sxx = float(np.sum((x - x.mean()) ** 2))
        se = float(np.sqrt(s2 / sxx)) if sxx > 0 else np.nan
    else:
        se = np.nan
    return dict(beta_T=float(b), logJc0=float(a), SE_beta_T=se, rms=rms,
                n_T_pts=n, T_min=float(T.min()), T_max=float(T.max()),
                t_reduced_max=float(T.max() / Tc), x_span=float(np.ptp(x)))


def common_field_span(t, temps, sample=None):
    """
    The field range every listed isotherm covers. A fit at a field outside it
    would be interpolating a curve that stops short, which is how a figure with
    three plotted markers turns into a nineteen-point grid.
    """
    lo, hi = -np.inf, np.inf
    for T in temps:
        x, _y = isotherm_exact(t, T, sample)
        if x is None:
            return None
        lo = max(lo, x.min())
        hi = min(hi, x.max())
    return (lo, hi) if hi > lo else None


def figure_jc(t, T, logH, sample=None):
    x, y = isotherm_exact(t, T, sample)
    if x is None or logH < x.min() or logH > x.max():
        return np.nan
    return 10.0 ** float(np.interp(logH, x, y))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    dep = pd.read_csv(DEP)
    meta = dep.groupby("paper_id").agg(
        compound_formula=("compound_formula", "first"),
        substructure=("substructure", "first")).to_dict("index")

    rows, skipped = [], []
    for p, name in sorted(TRACE.items()):
        if not name:
            skipped.append((p, "no trace: recorded fields match no axis on the page"))
            continue
        e = TC_READ.get(p)
        if not e or e["read"] is None:
            skipped.append((p, "the paper states no Tc for this sample"))
            continue
        Tc = float(e["read"])
        t = trace(name)
        sample = pick_sample(t)
        temps = [T for T in sorted(t.temperature_K.unique())
                 if isotherm_exact(t, T, sample)[0] is not None]
        # Eq. (1)'s temperature clause, applied to the points before the fit
        temps_in = [T for T in temps if T / Tc < T_MAX_REDUCED]
        if len(temps_in) < MIN_T_PTS:
            skipped.append((p, "only %d of %d isotherms sit below T/Tc = %.1f "
                               "with Tc = %.1f K"
                            % (len(temps_in), len(temps), T_MAX_REDUCED, Tc)))
            continue
        span = common_field_span(t, temps_in, sample)
        if span is None:
            skipped.append((p, "the contributing isotherms share no field range"))
            continue
        lo, hi = span
        grid = np.linspace(lo, hi, N_FIELDS)
        m = meta.get(p, {})
        for lh in grid:
            T_, J_ = [], []
            for T in temps_in:
                v = figure_jc(t, T, lh, sample)
                if np.isfinite(v) and v > 0:
                    T_.append(T)
                    J_.append(v)
            f = fit_beta(T_, J_, Tc)
            if f is None:
                continue
            rows.append(dict(
                paper_id=p,
                compound_formula=m.get("compound_formula", ""),
                substructure=m.get("substructure", ""),
                field_T=round(float(10.0 ** lh), 4),
                Tc_K=Tc,
                Tc_source="paper-reported: %s" % e["quote"][:90],
                sample=e["compound"] + ("" if sample is None
                                        else " (figure sample %s)" % sample),
                n_T_pts=f["n_T_pts"],
                T_min=f["T_min"], T_max=f["T_max"],
                t_reduced_max=round(f["t_reduced_max"], 4),
                beta_T=f["beta_T"], logJc0=f["logJc0"],
                SE_beta_T=f["SE_beta_T"], rms=f["rms"],
                x_span_dex=round(f["x_span"], 4),
                beta_lo=f["beta_T"] - 1.96 * f["SE_beta_T"],
                beta_hi=f["beta_T"] + 1.96 * f["SE_beta_T"],
                well_determined=bool(np.isfinite(f["SE_beta_T"])
                                     and abs(f["beta_T"]) > 0
                                     and f["SE_beta_T"] / abs(f["beta_T"])
                                     < WELL_DETERMINED),
                ok=bool(f["t_reduced_max"] < T_MAX_REDUCED
                        and f["n_T_pts"] >= MIN_T_PTS),
                source="rebuilt from figure trace %s" % name))

    out = pd.DataFrame(rows)

    print("=" * 88)
    print("REBUILT TEMPERATURE AXIS")
    print("=" * 88)
    print("  papers rebuilt      : %d   (the independent unit is the paper, not"
          % out.paper_id.nunique())
    print("                         the fit: the 10 fits per paper are the same")
    print("                         curve family re-evaluated at 10 fields)")
    print("  fits                : %d" % len(out))
    print("  papers not rebuilt  : %d" % len(skipped))
    for p, why in skipped:
        print("      %-18s %s" % (p[:18], why))

    # docstring claims, asserted rather than stated
    six = [q for q, e in TC_READ.items()
           if e["read"] is not None
           and len(dep[dep.paper_id == q])
           and abs(float(dep[dep.paper_id == q].Tc_K.iloc[0]) - e["read"]) >= 5.0]
    over = all(float(dep[dep.paper_id == q].Tc_K.iloc[0]) > TC_READ[q]["read"]
               for q in six)
    print("\n  docstring checks")
    print("      deposited Tc wrong by 5 K or more   : %d papers, all overestimates: %s"
          % (len(six), over))
    print("      largest deposited T_max/Tc          : %.4f"
          % (dep.T_max / dep.Tc_K).max())

    print()
    print("=" * 88)
    print("PER PAPER")
    print("=" * 88)
    print("lever  = span of log10(1 - T/Tc) the fit rests on, in dex")
    print("Hspan  = span of the field grid, in dex; a narrow one means the ten")
    print("         fits are one field")
    print("bySE   = median 95%% interval half-width from the fit's own residuals")
    print("byH    = standard deviation of beta_T across the ten fields")
    print("The second is the honest uncertainty. Where it exceeds the first, the")
    print("single-exponent model is not supported inside that paper.")
    print()
    print("%-18s %3s %6s %6s %6s %6s %7s %7s %7s %6s"
          % ("paper", "nT", "Tc(K)", "T/Tc", "lever", "Hspan", "beta_T",
             "bySE", "byH", "ratio"))
    rowsum = []
    for p, g in out.groupby("paper_id"):
        hs = np.log10(g.field_T.max()) - np.log10(g.field_T.min())
        bySE = float(np.median(1.96 * g.SE_beta_T))
        byH = float(g.beta_T.std())
        rowsum.append(dict(paper=p, beta=float(g.beta_T.median()), byH=byH,
                           bySE=bySE, lever=float(g.x_span_dex.median()),
                           hspan=hs, nT=int(g.n_T_pts.median()),
                           sub=g.substructure.iloc[0]))
        print("%-18s %3d %6.1f %6.3f %6.3f %6.3f %7.3f %7.3f %7.3f %6.1f"
              % (p[:18], int(g.n_T_pts.median()), g.Tc_K.iloc[0],
                 g.t_reduced_max.max(), g.x_span_dex.median(), hs,
                 g.beta_T.median(), bySE, byH, byH / bySE if bySE else np.nan))

    print()
    print("=" * 88)
    print("beta_T IS NOT CONSTANT WITHIN A PAPER")
    print("=" * 88)
    print("beta_T across the ten fields, low field first. A single exponent per")
    print("paper is the model the manuscript fits; these are what the figures give.")
    for p, g in out.groupby("paper_id"):
        v = g.sort_values("field_T").beta_T.values
        print("  %-18s %s" % (p[:18], " ".join("%6.2f" % x for x in v)))
    rising = sum(1 for p, g in out.groupby("paper_id")
                 if g.sort_values("field_T").beta_T.values[-1]
                 > g.sort_values("field_T").beta_T.values[0])
    signch = [p for p, g in out.groupby("paper_id") if (g.beta_T < 0).any()]
    print("\n  papers whose exponent rises from the lowest field to the highest : %d of %d"
          % (rising, out.paper_id.nunique()))
    print("  papers whose exponent changes sign inside the paper             : %d %s"
          % (len(signch), ", ".join(x[:12] for x in signch)))
    print("  median within-paper sd of beta_T                                : %.2f"
          % np.median([r["byH"] for r in rowsum]))
    print("  median of the fits' own 95%% half-widths                         : %.2f"
          % np.median([r["bySE"] for r in rowsum]))

    print()
    print("=" * 88)
    print("AGAINST THE DEPOSIT, LIKE FOR LIKE")
    print("=" * 88)
    papers = sorted(out.paper_id.unique())
    dsub = dep[dep.paper_id.isin(papers)]
    pm_new = out.groupby("paper_id").beta_T.median()
    pm_old = dsub.groupby("paper_id").beta_T.median()

    def sep(per_paper, subof):
        m = {}
        for q, v in per_paper.items():
            m.setdefault(subof[q], []).append(v)
        med = {k: float(np.median(v)) for k, v in m.items()}
        return max(med.values()) / min(med.values()), med

    subof = out.groupby("paper_id").substructure.first().to_dict()
    sep_new, med_new = sep(pm_new, subof)
    sep_old, med_old = sep(pm_old, subof)
    print("Both sides restricted to the same %d papers and weighted one paper" % len(papers))
    print("per paper, because a paper contributing 21 deposited fits and 8 is")
    print("otherwise counted twice as heavily as one contributing 8.")
    print()
    print("%-24s %10s %10s" % ("substructure", "deposited", "rebuilt"))
    for k in sorted(med_new):
        print("%-24s %10.3f %10.3f" % (k, med_old.get(k, np.nan), med_new[k]))
    print("\n  separation across substructures : deposited %.2f, rebuilt %.2f"
          % (sep_old, sep_new))
    print("  spread across papers            : deposited %.1f, rebuilt %.1f"
          % (pm_old.max() / pm_old.min(), pm_new.max() / pm_new.min()))
    print("\n  For reference, the separation over ALL %d deposited papers is %.2f;"
          % (dep.paper_id.nunique(),
             dep.groupby("substructure").beta_T.median().max()
             / dep.groupby("substructure").beta_T.median().min()))
    print("  quoting that against the rebuilt %.2f would compare two different"
          % sep_new)
    print("  cohorts, so it is not the comparison made here.")

    rng = np.random.default_rng(0)
    bs_sep, bs_spr = [], []
    pl = list(pm_new.index)
    for _ in range(2000):
        pick = rng.choice(pl, size=len(pl), replace=True)
        s_ = pm_new[pick]
        try:
            bs_sep.append(sep(pd.Series(s_.values, index=pick), subof)[0])
            bs_spr.append(s_.max() / s_.min())
        except (ValueError, ZeroDivisionError):
            pass
    print("\n  Bootstrap over the %d papers, 2000 draws:" % len(pl))
    print("      separation %.2f, 95%% interval [%.2f, %.2f]"
          % (sep_new, np.percentile(bs_sep, 2.5), np.percentile(bs_sep, 97.5)))
    print("      spread     %.1f, 95%% interval [%.1f, %.1f]"
          % (pm_new.max() / pm_new.min(), np.percentile(bs_spr, 2.5),
             np.percentile(bs_spr, 97.5)))

    print("\n  Leave one paper out, effect on the separation:")
    for q in pl:
        s2 = pm_new.drop(q)
        v, _ = sep(s2, subof)
        if abs(v - sep_new) / sep_new > 0.1:
            print("      without %-18s %.2f  (%+.0f%%)"
                  % (q[:18], v, 100 * (v - sep_new) / sep_new))

    if not args.dry_run:
        out.to_csv(OUT, index=False)
        print("\nwritten to %s" % OUT)


if __name__ == "__main__":
    main()
