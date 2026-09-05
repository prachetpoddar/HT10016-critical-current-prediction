#!/usr/bin/env python3
"""
adjudicate_temperature_axis.py

Decide, paper by paper, whether each temperature-axis extraction is a reading of
the figure it names.

Seventeen of the eighteen Cohort A papers now have a pixel trace of their own
figure, so the question can be answered on evidence rather than on structure.
The eighteenth, 0907.0147v2, records fields no axis on its page carries.
Four tests per paper, in increasing order of what they can settle:

  1. ISOTHERM SET.  Does the extraction's list of temperatures exist in the
     figure?  A temperature the figure does not plot cannot have been read from
     it.  This test needs no calibration at all.

  2. RANGE.  Does the extraction's Jc span lie inside the figure's y axis, and
     its field span inside the figure's x axis?  Values off the panel cannot
     have been read from it either.  Reported as the overlap in dex.

  3. beta_T.  Refit the exponent from the traced figure inside each deposited
     row's own temperature window and compare with the deposited value.  The
     comparison uses the SAME Tc on both sides, and the primary version uses the
     DEPOSITED Tc, because the question here is whether the deposited fit is a
     fit to the figure's Jc values, holding the Tc convention fixed.  An earlier
     version of this script used the paper's own Tc for the figure and the
     deposited Tc for the deposited value; that mismatch alone produced three
     apparent recoveries, all of which reject once the two sides agree.  The
     paper's own Tc is reported alongside as a second, coherent variant.

  4. THE PERMUTATION CONTROL.  Test 3 alone proves nothing: an earlier version
     of this comparison found a ratio of 0.97 for one paper, and the same
     deposited exponents scored 0.81 against a figure that paper has never seen,
     because beta_T sits between 1.5 and 2.2 across a whole material class.  So
     every paper's deposited exponents are also scored against every other
     paper's figure, and the self-pairing has to beat the strangers before any
     agreement is called agreement.

Strays. A pixel trace picks up the occasional piece of non-data, so each traced
isotherm is passed through a running median of three in log space before it is
interpolated. Endpoints are left untouched, so an irreversibility collapse
survives; measured displacement stays under 0.1 dex on all but a handful of
isotherms, and where it is larger it is removing a stray.

Shape. A median of ratios hides a disagreement that changes sign: for
1903.00866v2 the deposited exponent rises with field while the figure's falls
through zero, giving a rank correlation of exactly -1 and a median ratio of
1.12. The rank correlation between the two is therefore reported next to the
ratio, and a ratio near 1 with a negative correlation is not agreement.

Panel limits. "Outside the panel" is measured against the axis limits the
calibration recovered from the ticks, not against the trace's own minimum and
maximum. A trace that misses a curve's tail shrinks the apparent panel and
inflates the overhang; on 1104.0477v2, whose figure carries two or three markers
per isotherm, that difference is the whole finding.

    python3 analysis/adjudicate_temperature_axis.py

Run from the repository root. Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "analysis")
from tc_anchor_audit import TC_READ            # the per-paper Tc and its quote

DEP = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
WIDE = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
        "agent2_dataset_v3_2_1.csv")
RE = os.path.join("data", "reextraction")

TRACE = {
    "0806.2839v1.pdf":  "0806_2839v1_fig3",
    "0903.0004v2.pdf":  "0903_0004v2_fig6b",
    "0906.0444v1.pdf":  "0906_0444v1_fig3a",
    "0907.0147v2.pdf":  None,                  # see NOTE below
    "1002.0208v2.pdf":  "1002_0208v2_fig5a",
    "1009.4896v1.pdf":  "1009_4896v1_fig2b",
    "1104.0477v2.pdf":  "1104_0477v2_fig3c",
    "1108.0407v1.pdf":  "1108_0407v1_fig5d",
    "1111.3923v1.pdf":  "1111_3923v1_fig4a",
    "1502.05345v1.pdf": "1502_05345v1_fig4b_Hc",
    "1611.08455v1.pdf": "1611_08455v1_fig5b",
    "1903.00866v2.pdf": "1903_00866v2_fig4",
    "2012.13723v3.pdf": "2012.13723_fig4",
    "2207.06629v1.pdf": "2207.06629_fig4",
    "2305.10034v1.pdf": "jallcom_2023_170384_fig6c",
    "2308.10492v1.pdf": "2308_10492v1_fig2b",
    "2510.10264v1.pdf": "2510_10264v1_fig4a",
    "2511.19058v1.pdf": "2511_19058v1_fig2b",
}

T_TOL = 0.6          # K, matching an extraction temperature to a traced isotherm
MIN_PTS = 3          # traced points needed before an isotherm is interpolated


def running_median3(y):
    if len(y) < 3:
        return y
    out = y.copy()
    out[1:-1] = np.median(np.stack([y[:-2], y[1:-1], y[2:]]), axis=0)
    return out


def panel_limits(name):
    """The y axis limits the calibration recovered from the ticks."""
    import json
    f = os.path.join(RE, name + "_calibration.json")
    if not os.path.exists(f):
        return None
    y = (json.load(open(f)).get("axis_span_from_ticks") or {}).get("y")
    return tuple(y) if y else None


def trace(name):
    t = pd.read_csv(os.path.join(RE, name + "_points.csv"))
    return t[t.Jc_A_per_cm2 > 0].copy()


def isotherm(t, T):
    """
    One traced isotherm at temperature T.

    Grouped by the trace's own `series` column as well as by temperature,
    because Fig. 5(b) of 1611.08455v1 plots two different samples at each
    temperature: taking every point at 7 K interleaves two curves 0.8 dex apart
    and the running median then smooths across the interleave. Where several
    series share a temperature the one with the most points is used and the
    others are left alone.
    """
    s = t[np.isclose(t.temperature_K, T, atol=T_TOL)]
    if "series" in s.columns and s.series.nunique() > 1:
        pick = s.series.value_counts().index[0]
        s = s[s.series == pick]
    s = s.sort_values("field_T")
    if len(s) < MIN_PTS:
        return None, None
    x = np.log10(np.clip(s.field_T.values.astype(float), 1e-4, None))
    y = running_median3(np.log10(s.Jc_A_per_cm2.values.astype(float)))
    keep = np.concatenate([[True], np.diff(x) > 0])
    return x[keep], y[keep]


def figure_value(t, T, H):
    x, y = isotherm(t, T)
    if x is None or H <= 0:
        return np.nan
    lh = np.log10(H)
    if lh < x.min() or lh > x.max():
        return np.nan
    return float(np.interp(lh, x, y))


def beta_T(temps, jcs, Tc):
    T = np.asarray(temps, float)
    if Tc is None or not np.isfinite(Tc) or np.any(T >= Tc):
        return np.nan
    x = np.log10(1.0 - T / Tc)
    y = np.log10(np.asarray(jcs, float))
    if len(x) < 3 or np.ptp(x) == 0:
        return np.nan
    return float(np.polyfit(x, y, 1)[0])


def figure_beta(t, row, Tc):
    """beta_T from a traced figure, inside one deposited row's own window."""
    temps, jcs = [], []
    for T in sorted(t.temperature_K.unique()):
        if not (row.T_min - T_TOL <= T <= row.T_max + T_TOL):
            continue
        v = figure_value(t, T, row.field_T)
        if np.isfinite(v):
            temps.append(T)
            jcs.append(10.0 ** v)
    if len(temps) < 3:
        return np.nan, len(temps)
    return beta_T(temps, jcs, Tc), len(temps)


def main():
    if not os.path.exists(WIDE):
        sys.exit("wide file not found")
    dep = pd.read_csv(DEP)
    wide = pd.read_csv(WIDE)
    traces = {p: trace(n) for p, n in TRACE.items() if n}

    print("=" * 100)
    print("1. ISOTHERM SET  -  does the figure plot the temperatures the extraction records?")
    print("=" * 100)
    print("%-18s %-34s %-34s %s" % ("paper", "extraction", "figure", "missing"))
    missing_any = []
    for p, t in sorted(traces.items()):
        e = sorted(wide[(wide.pdf_name == p) & (wide.Jc > 0)].temperature_K.unique())
        f = sorted(t.temperature_K.unique())
        miss = [x for x in e if not any(abs(x - y) <= T_TOL for y in f)]
        if miss:
            missing_any.append(p)
        print("%-18s %-34s %-34s %s"
              % (p[:18], ",".join("%g" % x for x in e)[:34],
                 ",".join("%g" % x for x in f)[:34],
                 ",".join("%g" % x for x in miss) if miss else "-"))
    print("\n  papers recording an isotherm the figure does not plot : %d  (%s)"
          % (len(missing_any), ", ".join(x[:12] for x in missing_any)))

    print()
    print("=" * 100)
    print("2. RANGE  -  is the extraction inside the panel?")
    print("=" * 100)
    print("Panel limits are the axis span the calibration recovered from the ticks.")
    print("%-18s %24s %24s %10s" % ("paper", "extraction Jc", "panel Jc", "outside"))
    outside = []
    for p, t in sorted(traces.items()):
        e = wide[(wide.pdf_name == p) & (wide.Jc > 0)]
        lo_e, hi_e = e.Jc.min(), e.Jc.max()
        lim = panel_limits(TRACE[p])
        lo_f, hi_f = lim if lim else (t.Jc_A_per_cm2.min(), t.Jc_A_per_cm2.max())
        over = max(0.0, np.log10(hi_e) - np.log10(hi_f)) + \
               max(0.0, np.log10(lo_f) - np.log10(lo_e))
        if over > 0.5:
            outside.append((p, over))
        print("%-18s %11.2e..%-11.2e %11.2e..%-11.2e %10s"
              % (p[:18], lo_e, hi_e, lo_f, hi_f,
                 ("%.2f dex" % over) if over > 0.05 else "-"))
    print("\n  papers whose extraction lies more than 0.5 dex outside the panel : %d"
          % len(outside))
    for p, o in outside:
        print("    %-18s %.2f dex" % (p[:18], o))

    print()
    print("=" * 100)
    print("2b. FIELD AXIS  -  are the recorded fields on the figure's x axis?")
    print("=" * 100)
    print("%-18s %22s %22s %s" % ("paper", "extraction H (T)", "figure H (T)", "verdict"))
    field_bad = []
    for p, t in sorted(traces.items()):
        e = wide[(wide.pdf_name == p) & (wide.Jc > 0)]
        eh = e.field_T[e.field_T > 0]
        if eh.empty:
            continue
        fh = t.field_T[t.field_T > 0]
        ratio = fh.max() / eh.max()
        v = "-"
        if eh.max() < fh.min() or eh.min() > fh.max():
            v = "disjoint, figure/extraction = %.0fx" % ratio
            field_bad.append((p, ratio))
        elif ratio > 3 or ratio < 0.33:
            v = "span off by %.0fx" % (ratio if ratio > 1 else 1 / ratio)
        print("%-18s %10.2e..%-10.2e %10.2e..%-10.2e %s"
              % (p[:18], eh.min(), eh.max(), fh.min(), fh.max(), v))
    print("\n  papers whose recorded fields do not touch the figure's axis at all : %d"
          % len(field_bad))
    for p, r in field_bad:
        print("    %-18s figure spans %.0f times the extraction's range" % (p[:18], r))

    print()
    print("=" * 100)
    print("2c. SPLIT FIELD GRIDS  -  one paper carrying two field blocks a decade apart")
    print("=" * 100)
    for p in sorted(traces):
        e = wide[(wide.pdf_name == p) & (wide.Jc > 0)]
        h = np.sort(e.field_T[e.field_T > 0].unique())
        if len(h) < 4:
            continue
        g = np.diff(np.log10(h))
        i = int(np.argmax(g))
        if g[i] > 2.0:
            print("  %-18s %d values at %.1e..%.1e then %d at %.1e..%.1e  (%.0fx apart)"
                  % (p[:18], i + 1, h[0], h[i], len(h) - i - 1, h[i + 1], h[-1],
                     h[i + 1] / h[i]))

    print()
    print("=" * 100)
    print("3 and 4. beta_T AGAINST THE FIGURE, WITH THE PERMUTATION CONTROL")
    print("=" * 100)
    print("Self = the paper's own figure. Rank = where the self-pairing sits among")
    print("all figures able to score it, 1 being the closest to the deposited value.")
    print("rho = rank correlation between the deposited exponent and the figure's,")
    print("across the fields both are defined at. A ratio near 1 with rho <= 0 is not")
    print("agreement: it is a median taken over a disagreement that changes sign.")
    print()
    print("%-18s %5s %9s %9s %7s %7s %6s %5s %9s"
          % ("paper", "fits", "deposited", "figure", "ratio", "rho", "rank", "of", "paperTc"))
    verdicts = {}
    for p in sorted(traces):
        d = dep[dep.paper_id == p]
        if d.empty:
            continue
        Tc_dep = float(d.Tc_K.iloc[0])
        e = TC_READ.get(p)
        Tc_pap = e["read"] if e else None

        # primary comparison: the deposited Tc on BOTH sides
        scores, pairs = {}, []
        for q, tq in traces.items():
            rr = []
            for _, r in d.iterrows():
                b, _n = figure_beta(tq, r, Tc_dep)
                if np.isfinite(b) and b != 0:
                    rr.append(r.beta_T / b)
                    if q == p:
                        pairs.append((r.beta_T, b))
            if len(rr) >= 3:
                scores[q] = float(np.median(rr))
        if p not in scores:
            print("%-18s %5d %9.3f %9s %7s %7s %6s %5s %9s"
                  % (p[:18], len(d), d.beta_T.median(), "no overlap",
                     "-", "-", "-", "-", "-"))
            verdicts[p] = ("no deposited field lies on the figure's axis, so "
                           "beta_T cannot be scored")
            continue
        own = scores[p]
        order = sorted(scores.items(), key=lambda kv: abs(np.log(abs(kv[1]))))
        rank = [q for q, _ in order].index(p) + 1
        own_b = np.nanmedian([figure_beta(traces[p], r, Tc_dep)[0]
                              for _, r in d.iterrows()])
        a = np.array([x for x, _ in pairs], float)
        b_ = np.array([y for _, y in pairs], float)
        rho = np.nan
        if len(a) >= 4 and np.ptp(a) > 0 and np.ptp(b_) > 0:
            ra = pd.Series(a).rank().values
            rb = pd.Series(b_).rank().values
            if np.std(ra) > 0 and np.std(rb) > 0:
                rho = float(np.corrcoef(ra, rb)[0, 1])

        # second coherent variant: the paper's own Tc on both sides
        alt = np.nan
        if Tc_pap is not None:
            rr2 = []
            for _, r in d.iterrows():
                bf, _n = figure_beta(traces[p], r, Tc_pap)
                s2 = wide[(wide.pdf_name == p) & (wide.Jc > 0)
                          & (wide.field_T == r.field_T)]
                s2 = s2[(s2.temperature_K >= r.T_min) & (s2.temperature_K <= r.T_max)]
                if len(s2) >= 3:
                    bd = beta_T(s2.temperature_K.values, s2.Jc.values, Tc_pap)
                    if np.isfinite(bf) and np.isfinite(bd) and bf != 0:
                        rr2.append(bd / bf)
            if len(rr2) >= 3:
                alt = float(np.median(rr2))

        print("%-18s %5d %9.3f %9.3f %7.2f %7s %6d %5d %9s"
              % (p[:18], len(d), d.beta_T.median(), own_b, own,
                 ("%.2f" % rho) if np.isfinite(rho) else "-",
                 rank, len(scores),
                 ("%.2f" % alt) if np.isfinite(alt) else "-"))

        near = 0.8 <= own <= 1.25
        near_alt = np.isfinite(alt) and 0.8 <= alt <= 1.25
        shape_ok = np.isfinite(rho) and rho > 0
        if near and near_alt and rank == 1 and shape_ok:
            verdicts[p] = "beta_T recovered on both Tc conventions and beats every stranger"
        elif near and not shape_ok:
            verdicts[p] = ("ratio %.2f but the two exponents are anti-ordered "
                           "across field (rho %.2f), so this is not agreement"
                           % (own, rho))
        elif near and not near_alt:
            verdicts[p] = ("ratio %.2f under the deposited Tc but %.2f under the "
                           "paper's own, so the agreement is an artefact of the anchor"
                           % (own, alt))
        elif near:
            verdicts[p] = "beta_T close (ratio %.2f) but %d stranger figures score closer" % (own, rank - 1)
        else:
            verdicts[p] = "beta_T not recovered (ratio %.2f)" % own

    print()
    print("=" * 100)
    print("VERDICT")
    print("=" * 100)
    for p in sorted(traces):
        flags = []
        e = sorted(wide[(wide.pdf_name == p) & (wide.Jc > 0)].temperature_K.unique())
        f = sorted(traces[p].temperature_K.unique())
        if [x for x in e if not any(abs(x - y) <= T_TOL for y in f)]:
            flags.append("isotherm not in the figure")
        for q, o in outside:
            if q == p:
                flags.append("%.1f dex outside the panel" % o)
        v = verdicts.get(p, "not scored")
        print("  %-18s %s" % (p[:18], "; ".join(flags + [v])))
    print()
    print("  0907.0147v2 has no trace: its recorded fields are 1e-5 to 1.2e-3,")
    print("  which no axis on its figure page carries, so there is nothing to")
    print("  compare against until the intended unit is established.")


if __name__ == "__main__":
    main()
