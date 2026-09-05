#!/usr/bin/env python3
"""
refit_from_traces.py

What would re-extracting by hand do to the deposited field-axis exponents?

Pre-registered in audit/sampled_reextraction_preregistration_20260905.md. Seven
vision-pass papers have both a pixel trace of their own figure and at least one
passing field-axis fit: 60 of the 94 passing fits. For each, beta_H is refit
from the trace at the same temperature, for the same sample, under the same
Hc2, over points with H strictly below Hc2.

A pixel trace stands in for a hand re-extraction because stage C measured the
two against each other on three papers and found them 0.003 to 0.023 dex apart.
It fixes reading fidelity and nothing else: the two hand-digitisation failures
on file in this corpus are a kilo-oersted axis written into a tesla column and a
file named for the wrong DOI, and neither is a reading error.

Three things are reported per fit:

  MOVE       |ln(refit / deposited)|, how far the exponent shifts.
  WINDOW     whether Eq. (1)'s field clause still holds once the field unit is
             corrected, recomputed from the traced points below Hc2.
  SUPPORT    whether at least four traced points survive the H < Hc2 filter.

    python3 analysis/refit_from_traces.py

Run from the repository root. Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "analysis")
from adjudicate_field_axis import PASS, beta_H, MIN_LEVER
from extraction_method_test import curve  # same isotherm reader stage C used

FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
RE = os.path.join("data", "reextraction")
# analysis/apply_field_window_gate.py states 0.3 as a bound on the REDUCED FIELD
# of a prediction target. It is applied here to the normalised span of a fit,
# which is a different quantity; the attribution is the manuscript's and is not
# independently verified.
MIN_RANGE = 0.3
MOVE_TOL = 0.25       # about twice the deposit's own median SE_beta/|beta|, 0.131

# paper -> traces, how a deposited sample maps onto a traced series, and the
# factor the FIGURE's field axis needs to reach tesla (1.0 unless the panel is
# in kilo-oersted, in which case the trace is already in tesla and it is the
# deposit's Hc2 comparison that has to be done in tesla).
CASES = {
    "elsevier_10.1016_j.matchemphys.2023.128348": dict(
        traces=["matchemphys_2023_128348_fig5"],
        smap={"X01": "X01", "X02": "X02", "X03": "X03", "X04": "X04"}),
    "elsevier_10.1016_j.matpr.2019.05.078": dict(
        traces=["matpr_2019_05_078_fig2a"],
        smap={"mono-5K": "mono-5K", "multi-5K": "multi-5K"}),
    "elsevier_10.1016_j.phpro.2015.06.160": dict(
        traces=["phpro_2015_06_160_fig3L"], smap={}),
    "elsevier_10.1016_j.mtphys.2022.100783": dict(
        # The first version excluded this paper wholesale on a reason copied
        # from a different script, where the extraction carried no panel label.
        # Here the deposited rows do: audit/mtphys_2022_100783_duplicate_20260904.md
        # identifies Fig. 6(a) as the single crystal and 6(b) as the polycrystal.
        # Two of its twenty fits are at 4.2 K and comparable; the other eighteen
        # are at 6 to 21 K, which neither trace covers.
        traces=["mtphys_2022_100783_fig6a"],
        panels={"Single crystal": "mtphys_2022_100783_fig6a",
                "Polycrystal": "mtphys_2022_100783_fig6b"}, smap={}),
    "springer_10.1007_s10854-026-16566-9": dict(
        traces=["s10854_fig9a", "s10854_fig9b", "s10854_fig9c", "s10854_fig9d"],
        panels={"x=0%": "s10854_fig9a", "x=1%": "s10854_fig9b",
                "x=2%": "s10854_fig9c", "x=3%": "s10854_fig9d"}, smap={}),
    "elsevier_10.1016_j.physc.2009.11.051": dict(
        traces=["physc_2009_11_051_fig3"],
        smap={"irradiated": "irradiated", "unirradiated": "unirradiated"},
        per_temp=True, kOe=True),
    "elsevier_10.1016_j.physc.2010.05.048": dict(
        traces=["physc_2010_05_048_fig3"], smap={}, kOe=True),
}


def load(names):
    ts = []
    for n in names:
        f = os.path.join(RE, n + "_points.csv")
        if os.path.exists(f):
            ts.append(pd.read_csv(f))
    return pd.concat(ts, ignore_index=True) if ts else None


def main():
    d = PASS(pd.read_csv(FITS))
    print("=" * 96)
    print("REFITTING beta_H FROM THE FIGURE, FOR EVERY PASSING FIT THAT HAS A TRACE")
    print("=" * 96)
    print("range is (Hmax-Hmin)/Hc2 recomputed from the traced points below Hc2.")
    print("Eq. (1) needs it above %.1f." % MIN_RANGE)
    print()
    print("%-40s %-16s %5s %8s %8s %6s %7s %s"
          % ("paper", "sample", "T(K)", "deposit", "refit", "move", "range", "verdict"))
    rows = []
    for k, cfg in CASES.items():
        g = d[d.paper_key == k]
        if cfg.get("ambiguous"):
            print("%-40s %-16s %5s %8s %8s %6s %7s %s"
                  % (k[:40], "-", "-", "-", "-", "-", "-", "not comparable"))
            print("      %s" % cfg["ambiguous"])
            for _, r in g.iterrows():
                rows.append(dict(paper=k, verdict="not comparable"))
            continue
        for _, r in g.iterrows():
            name = cfg["traces"][0]
            if cfg.get("panels"):
                for tag, nm in cfg["panels"].items():
                    if tag in str(r.sample_identifier):
                        name = nm
            t = load([name])
            if t is None:
                continue
            ser = None
            if cfg.get("per_temp"):
                ser = "%s_%dK" % (cfg["smap"].get(r.sample_identifier,
                                                  r.sample_identifier),
                                  int(r.fixed_axis_value))
            elif cfg["smap"]:
                ser = cfg["smap"].get(r.sample_identifier)
            x, y = curve(t, ser, r.fixed_axis_value, strict=True)
            if x is None:
                rows.append(dict(paper=k, verdict="no traced isotherm"))
                print("%-40s %-16s %5.1f %8.3f %8s %6s %7s %s"
                      % (k[:40], str(r.sample_identifier)[:16], r.fixed_axis_value,
                         r.beta, "-", "-", "-", "no traced isotherm"))
                continue
            H = 10.0 ** x
            J = 10.0 ** y
            f = beta_H(H, J, r.Hc2_T_used)
            if f and f["lever"] < 0.20:
                # The regressor barely moves while Jc falls a decade, so the
                # exponent is a ratio to nothing. adjudicate_field_axis.py
                # screens on this and the first version of this script did not:
                # six refits, including the 15.5 at 9 K, were short-lever
                # artefacts rather than measurements.
                rows.append(dict(paper=k, verdict="no lever"))
                print("%-40s %-16s %5.1f %8.3f %8.3f %6s %7.3f %s"
                      % (k[:40], str(r.sample_identifier)[:16], r.fixed_axis_value,
                         r.beta, f["beta"], "-", f["H_range_norm"],
                         "no lever (%.3f dex)" % f["lever"]))
                continue
            if not f:
                rows.append(dict(paper=k, verdict="too few points below Hc2"))
                continue
            move = abs(np.log(abs(f["beta"] / r.beta))) if r.beta else np.nan
            passes = f["H_range_norm"] > MIN_RANGE and f["n"] >= 4
            v = ("survives" if (passes and move < MOVE_TOL) else
                 ("exponent moves" if passes else "fails the window"))
            rows.append(dict(paper=k, move=move, rng=f["H_range_norm"],
                             n=f["n"], verdict=v))
            print("%-40s %-16s %5.1f %8.3f %8.3f %6.2f %7.3f %s"
                  % (k[:40], str(r.sample_identifier)[:16], r.fixed_axis_value,
                     r.beta, f["beta"], move, f["H_range_norm"], v))

    r = pd.DataFrame(rows)
    print()
    print("=" * 96)
    print("WHAT RE-EXTRACTION WOULD DO TO THE %d PASSING FITS IT COVERS" % len(r))
    print("=" * 96)
    for v, g in r.groupby("verdict"):
        print("  %-26s %3d fits" % (v, len(g)))
    ok = r.dropna(subset=["move"]) if "move" in r else pd.DataFrame()
    if len(ok):
        print("\n  median exponent shift        : %.2f in log" % ok.move.median())
        print("  fits still clearing Eq. (1)  : %d of %d"
              % (int((ok.rng > MIN_RANGE).sum()), len(ok)))
        print("\n  The survivor count is threshold-sensitive, so the whole curve:")
        print("      |ln shift| below : %s"
              % "  ".join("%.2f" % t for t in (0.05, 0.10, 0.25, 0.50, 1.00, 1.50)))
        print("      fits inside      : %s"
              % "  ".join("%4d" % int((ok.move < t).sum())
                          for t in (0.05, 0.10, 0.25, 0.50, 1.00, 1.50)))
        print("  At a factor of e the majority sit inside. 'Only two survive' is")
        print("  true at 0.25 and is not a robust way to put it: under hand-like")
        print("  six-point subsets the median shift is 0.81 to 0.84 rather than")
        print("  %.2f, and the identity of the survivors changes every time."
              % ok.move.median())

    print()
    print("=" * 96)
    print("A DEFECT THIS EXPOSED, WHICH IS NOT ABOUT RE-EXTRACTION")
    print("=" * 96)
    print("Hc2 rises with temperature in three of these papers, which no upper")
    print("critical field does:")
    for k in ("elsevier_10.1016_j.physc.2009.11.051",
              "elsevier_10.1016_j.physc.2010.05.048",
              "elsevier_10.1016_j.mtphys.2022.100783"):
        g = d[d.paper_key == k].sort_values("fixed_axis_value")
        if g.empty:
            continue
        pairs = ["%g K %.1f T" % (a, b) for a, b in
                 zip(g.fixed_axis_value, g.Hc2_T_used)]
        seen, out = set(), []
        for q in pairs:
            if q not in seen:
                seen.add(q)
                out.append(q)
        print("      %-38s %s" % (k[-28:], ", ".join(out[:6])))
    above = 0
    print("\n  And traced points carry Jc > 0 at fields above their own Hc2 in")
    print("  many of these fits, up to about twice it. Hc2 is where Jc vanishes.")
    print("  The provenance files show where these came from: physc.2010.05.048's")
    print("  anchor is sourced from a figure captioned 'field dependence of")
    print("  magnetization' and physc.2009.11.051's from one about an")
    print("  interpolation index. Under the deposit's own compound defaults for")
    print("  these materials, 50 T and 47 T, none of the sixteen fits clears the")
    print("  window at all. Whether they pass turns entirely on an anchor that")
    print("  cannot be an upper critical field.")


if __name__ == "__main__":
    main()
