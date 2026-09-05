#!/usr/bin/env python3
"""
hand_extraction_pattern.py

What the hand extractions in this corpus do that the vision passes do not.

analysis/extraction_method_test.py established that the three hand-digitised
papers reproduce their figures to 0.003 to 0.023 dex while the vision passes sit
at 0.120 to 2.409. This asks what is different about the files themselves, on
properties that need no figure: how many points per isotherm, how they are
spaced, whether the values are rounded, whether the curve is monotone, whether
the extraction covers the figure's field range or a corner of it.

The point is a checklist. If the difference is visible in the file, it can be
required of a new extraction before anyone re-reads a figure to check it.

Two properties separate the routes and they are not equally useful, which an
independent review established after the first version of this script reported
only the weaker one.

  SIGNIFICANT FIGURES separates completely and is nearly worthless. Hand files
  carry two significant figures or fewer on 0.00 to 0.02 of their values; vision
  files on 0.05 to 1.00, median 1.00. But rounding the three good hand files to
  two significant figures on export flips all three into the vision range while
  degrading their agreement with their own figures by 0.002 to 0.004 dex and
  moving beta_H by 0.005 in log, twenty times below the deposit's own quoted
  error. It is a fingerprint of how the file was written, not of how the curve
  was read, and within the vision arm it does not predict agreement at all
  (rank correlation 0.16, p = 0.74).

  NON-MONOTONICITY separates in the direction that matters and cannot be faked
  by an exporter. No vision file in this corpus has a median isotherm that ever
  rises with field: all nineteen are perfectly monotone. Three of the eight hand
  files are not, at 0.97, 0.89 and 0.74. A real Jc(H) has a fishtail; a ladder
  written down as a smooth decline does not. This is the property to require.

    python3 analysis/hand_extraction_pattern.py

Run from the repository root. Changes nothing.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

EXT = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
       "v3_2_2B_extension/")

HAND = ["10.1016_j.physc.2013.04.060_MgB2_C_doping_series_transport_4_2K",
        "10.1016_j.physc.2013.04.060_MgB2_dopant_series_transport_10K",
        "10.1016_j.physc.2011.02.004_PrFeAsO_magnetization_5-35K",
        "10.1016_j.jallcom.2023.170384_LaFeAsO_magnetization_2-10K",
        "10.1016_j.jallcom.2023.170146_MgB2_bulk_magnetization_10-35K",
        "10.1016_j.physc.2009.05.098_SmFeAsO_MO_SHPM_2-40K",
        "springer_10.1038_s41598-022-24044-5_FeSeTe_transport_4-12K",
        "iop_10.1088_0953-2048_29_3_035013_FeSe0.5Te0.5_MO_SHPM_H_sweep"]


def sigfigs(v):
    if not (v > 0):
        return 0
    s = ("%.10g" % v).replace("-", "").replace(".", "").lstrip("0")
    return len(s.rstrip("0")) or 1


def stats(df):
    """Properties of one extraction file that need no figure to compute."""
    col = "Jc_A_per_cm2" if "Jc_A_per_cm2" in df else "Jc"
    d = df[df[col] > 0].copy()
    if len(d) < 4:
        return None
    keys = [c for c in ("temperature_K", "doping_or_composition",
                        "sample_identifier") if c in d.columns]
    groups = list(d.groupby(keys)) if keys else [((), d)]
    npts, spacing, mono, span, rounded = [], [], [], [], []
    for _, g in groups:
        g = g.sort_values("field_T")
        h = g.field_T.values.astype(float)
        j = g[col].values.astype(float)
        if len(h) < 3:
            continue
        npts.append(len(h))
        pos = h[h > 0]
        if len(pos) > 2:
            r = np.diff(np.log10(pos))
            # 0 means perfectly even in log, large means even in linear field
            spacing.append(float(np.std(r) / (abs(np.mean(r)) + 1e-9)))
        mono.append(float(np.mean(np.diff(j) <= 0)))
        if len(pos) > 1:
            span.append(float(np.log10(pos.max() / pos.min())))
    rounded = float(np.mean([sigfigs(v) <= 2 for v in d[col].values]))
    lead = pd.Series([int(("%.10g" % (v / 10 ** np.floor(np.log10(v))))[0])
                      for v in d[col].values if v > 0])
    return dict(rows=len(d), curves=len(npts),
                pts_per_curve=float(np.median(npts)) if npts else np.nan,
                field_decades=float(np.median(span)) if span else np.nan,
                spacing_cv=float(np.median(spacing)) if spacing else np.nan,
                monotone=float(np.median(mono)) if mono else np.nan,
                two_sigfig=rounded,
                distinct_frac=float(d[col].nunique() / len(d)),
                lead_1_2=float(lead.isin([1, 2]).mean()))


def main():
    rows = []
    for f in sorted(glob.glob(EXT + "*_LONG.csv")):
        base = os.path.basename(f)[:-9]
        stem = base.replace("elsevier_", "")
        hand = any(stem == h or base == h for h in HAND)
        df = pd.read_csv(f)
        s = stats(df)
        if not s:
            continue
        rows.append(dict(file=stem, route="hand" if hand else "vision", **s))
    r = pd.DataFrame(rows)

    print("=" * 104)
    print("WHAT THE FILES LOOK LIKE, BEFORE ANY FIGURE IS OPENED")
    print("=" * 104)
    print("pts   median points per isotherm")
    print("dec   median field range covered by one isotherm, in decades")
    print("cv    spacing regularity: 0 is perfectly even in log field, high is even in linear")
    print("mono  fraction of consecutive steps where Jc does not rise")
    print("2sf   fraction of Jc values carrying two significant figures or fewer")
    print("dist  fraction of Jc values that are distinct")
    print("lead  fraction of Jc values whose leading digit is 1 or 2")
    print()
    print("%-52s %-7s %5s %5s %6s %6s %5s %5s %5s"
          % ("file", "route", "pts", "dec", "cv", "mono", "2sf", "dist", "lead"))
    for _, q in r.sort_values(["route", "file"]).iterrows():
        print("%-52s %-7s %5.0f %5.2f %6.2f %6.2f %5.2f %5.2f %5.2f"
              % (q.file[:52], q.route, q.pts_per_curve, q.field_decades,
                 q.spacing_cv, q.monotone, q.two_sigfig, q.distinct_frac,
                 q.lead_1_2))

    print()
    print("=" * 104)
    print("THE DIFFERENCE, BY ROUTE")
    print("=" * 104)
    cols = ["pts_per_curve", "field_decades", "spacing_cv", "monotone",
            "two_sigfig", "distinct_frac", "lead_1_2"]
    print("%-18s %8s %8s %10s" % ("property", "hand", "vision", "separates?"))
    for c in cols:
        h = r[r.route == "hand"][c].dropna()
        v = r[r.route == "vision"][c].dropna()
        if len(h) < 2 or len(v) < 2:
            continue
        clean = (h.min() > v.max()) or (h.max() < v.min())
        print("%-18s %8.2f %8.2f %10s"
              % (c, h.median(), v.median(), "completely" if clean else "overlaps"))
    print("\n  hand files : %d, vision files : %d"
          % (int((r.route == "hand").sum()), int((r.route == "vision").sum())))

    print()
    print("=" * 104)
    print("THE PROPERTY WORTH REQUIRING")
    print("=" * 104)
    h = r[r.route == "hand"]
    v = r[r.route == "vision"]
    print("  vision files whose isotherms are perfectly monotone : %d of %d"
          % (int((v.monotone >= 1.0).sum()), len(v)))
    print("  hand files whose isotherms are not                  : %d of %d  (%s)"
          % (int((h.monotone < 1.0).sum()), len(h),
             ", ".join("%.2f" % x for x in sorted(h[h.monotone < 1.0].monotone))))
    print()
    print("  A measured Jc(H) in these materials shows a second peak, so an")
    print("  isotherm that never once rises with field is a claim about the")
    print("  sample, not a neutral reading. Every vision file in this corpus")
    print("  makes that claim; three of the eight hand files do not.")
    print()
    print("  Significant figures separates the two routes completely and is not")
    print("  worth requiring: rounding a faithful extraction on export flips it")
    print("  while changing beta_H by 0.005 in log. It identifies who wrote the")
    print("  file, which is useful for triage and useless as a quality test.")


if __name__ == "__main__":
    main()
