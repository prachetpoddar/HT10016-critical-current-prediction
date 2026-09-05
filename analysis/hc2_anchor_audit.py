#!/usr/bin/env python3
"""
hc2_anchor_audit.py

Every Hc2 anchor in the field-axis cohort, tested the way the Tc anchors were.

Why. analysis/refit_from_traces.py turned up an Hc2 that rises with temperature
in three papers, which no upper critical field does. Whether a fit clears
Eq. (1)'s field clause is (Hmax - Hmin)/Hc2, so the anchor decides membership of
the cohort. analysis/tc_anchor_audit.py found the temperature axis's anchor was a
compound-keyed constant presented as paper-reported; this asks the same question
of the field axis, where the provenance is better but not uniformly so.

Five tests, none of which needs the paper to be read:

  1. MONOTONICITY, within a sample. Hc2(T) falls with temperature and vanishes
     at Tc. A rise across a paper is not by itself wrong, because a paper often
     measures several samples at different temperatures; the test is per sample.

  2. Jc ABOVE THE ANCHOR. The data should carry no current above the field its
     own anchor names. Four screens are applied before a fit is counted, each
     of which an independent review showed the first version of this script
     needed:
       - the trace's series must be the fit's own sample, not every curve at
         that temperature pooled, which had manufactured three of the flags
       - traced points within a few pixels of the frame or sitting on a tick
         are dropped, which had manufactured four more
       - the anchor must have been read at the data's own temperature; an
         anchor extrapolated to 18 K tells you nothing about a 4.2 K curve
       - a source the repository grades as fabricated is not evidence
     And the conclusion is weaker than "impossible" for most of them: an anchor
     recorded as an irreversibility field is a criterion, and matchemphys's
     traced curves reach the paper's own Jc = 100 A/cm2 criterion at 3.14 T
     against a recorded 3.00, which confirms that anchor rather than refuting
     it. Only an anchor the deposit labels term_Hc2 makes current above it
     impossible.

  3. CURRENT AT THE BOUND. At the highest field below Hc2 the current should be
     collapsing. A fit whose last point still carries a third of its maximum is
     nowhere near the irreversibility field.

  4. AGAINST Tc. WITHDRAWN. The first version computed Hc2/(Tc - T) from the
     lowest-temperature row and called it dHc2/dT, which it is not: it is a
     chord, it is monotone in which row is picked (0.125 at 2 K rising to 2.750
     at 20 K for one sample), and the "1 to 5 T per kelvin" it was compared
     against is contradicted by the deposit's own best-provenance anchors at
     0.55 and 0.80. It added one paper the other tests do not already name. The
     section is kept only to record that it was tried and does not work.

  5. AGAINST THE PROVENANCE STRING. The deposit records where each anchor came
     from. Some of those strings name a figure that is not an Hc2 figure.

    python3 analysis/hc2_anchor_audit.py

Run from the repository root. Changes nothing.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "analysis")
from adjudicate_field_axis import PASS

FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
EXT = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
       "v3_2_2B_extension/")
RE = os.path.join("data", "reextraction")

# paper -> its trace, for the papers where the printed curve can be checked
TRACES = {
    "elsevier_10.1016_j.physc.2009.11.051": "physc_2009_11_051_fig3",
    "elsevier_10.1016_j.physc.2010.05.048": "physc_2010_05_048_fig3",
    "elsevier_10.1016_j.physc.2013.04.060": "physc_2013_04_060_fig2",
    "elsevier_10.1016_j.matchemphys.2023.128348": "matchemphys_2023_128348_fig5",
    "elsevier_10.1016_j.mtphys.2022.100783": "mtphys_2022_100783_fig6a",
    "elsevier_10.1016_j.matpr.2019.05.078": "matpr_2019_05_078_fig2a",
    "elsevier_10.1016_j.phpro.2015.06.160": "phpro_2015_06_160_fig3L",
    "springer_10.1007_s10854-026-16566-9": "s10854_fig9a",
    "elsevier_10.1016_j.jallcom.2023.170384": "jallcom_2023_170384_fig6c",
    "1002.0208v2.pdf": "1002_0208v2_fig5a",
}

# the field factor an extraction needs to reach tesla, where a figure is in kOe
KOE = {"elsevier_10.1016_j.physc.2009.11.051",
       "elsevier_10.1016_j.physc.2010.05.048",
       "elsevier_10.1016_j.physc.2009.05.098"}

# Current still flowing at the bound is a signal, not a proof: a sample with a
# strong second peak is genuinely flat up to its irreversibility field, which is
# why 1002.0208v2 shows a high fraction with an anchor that is otherwise sound.
# Only reaching or passing Hc2 is decisive on its own.
CARRY_FRACTION = 1.0 / 3.0

# Extractions the repository grades as inventing high-field points. Using one as
# evidence that a curve passes its anchor would be circular.
FABRICATED = {"elsevier_10.1016_j.mtphys.2022.100783",
              "elsevier_10.1016_j.phpro.2015.06.160",
              "elsevier_10.1016_j.jallcom.2023.170146"}

# The anchor must have been read at the data's own temperature. A provenance
# string naming a different temperature is an extrapolation and says nothing
# about this isotherm.
def anchor_temperature(src):
    import re as _re
    m = _re.search(r"(?:at|anchor_)([0-9]+(?:\.[0-9]+)?)K", str(src))
    return float(m.group(1)) if m else None


def ext_for(paper):
    stem = paper.replace("elsevier_", "").replace(".pdf", "")
    out = []
    for f in glob.glob(EXT + "*" + stem + "*_LONG.csv"):
        out.append(pd.read_csv(f))
    return pd.concat(out, ignore_index=True) if out else None


def main():
    d = pd.read_csv(FITS)
    p = PASS(d)
    prov = pd.read_csv(PROV)

    print("=" * 96)
    print("1. DOES Hc2 RISE WITH TEMPERATURE WITHIN ONE SAMPLE?")
    print("=" * 96)
    bad = []
    for (k, s), g in d.dropna(subset=["Hc2_T_used", "fixed_axis_value"]).groupby(
            ["paper_key", "sample_identifier"]):
        g = g.sort_values("fixed_axis_value")
        if g.fixed_axis_value.nunique() < 3 or g.Hc2_T_used.nunique() < 2:
            continue
        T, H = g.fixed_axis_value.values, g.Hc2_T_used.values
        rho = float(np.corrcoef(T, H)[0, 1])
        if rho > 0.5:
            bad.append((k, s, rho, len(g)))
            print("  %-40s %-16s n=%2d corr(T,Hc2)=%+.2f  %s"
                  % (k[:40], str(s)[:16], len(g), rho,
                     ", ".join("%g K %.1f T" % (a, b) for a, b in zip(T, H))[:70]))
    print("\n  samples whose Hc2 rises with temperature : %d" % len(bad))
    print("  (a rise ACROSS a paper can be several samples; this is within one)")

    print()
    print("=" * 96)
    print("2 and 3. DOES THE DATA CARRY CURRENT AT AND ABOVE ITS OWN Hc2?")
    print("=" * 96)
    print("%-40s %-14s %5s %7s %8s %9s %s"
          % ("paper", "sample", "T", "Hc2", "Hmax/Hc2", "Jc at bnd", "source"))
    over = []
    for k in sorted(p.paper_key.unique()):
        g = p[p.paper_key == k]
        e = ext_for(k)
        t = None
        if k in TRACES:
            f = os.path.join(RE, TRACES[k] + "_points.csv")
            if os.path.exists(f):
                t = pd.read_csv(f)
        scale = 0.1 if k in KOE else 1.0
        for _, r in g.iterrows():
            for src, frame, sc in (("figure", t, 1.0), ("extraction", e, scale)):
                if frame is None or frame.empty:
                    continue
                col = "Jc_A_per_cm2" if "Jc_A_per_cm2" in frame else "Jc"
                fc = frame.copy()
                if "temperature_K" in fc:
                    near = fc[np.isclose(fc.temperature_K, r.fixed_axis_value,
                                         atol=0.35)]
                    if len(near) < 3:
                        # no curve at this temperature: refuse rather than fall
                        # back to every temperature pooled, which had made one
                        # 4.2 K trace answer for twenty fits
                        continue
                    fc = near
                # the fit's own sample, not every curve at that temperature
                if "series" in fc.columns and pd.notna(r.sample_identifier):
                    lab = str(r.sample_identifier)
                    own = fc[fc.series.astype(str).apply(
                        lambda q: q == lab or lab.startswith(q) or q.startswith(lab))]
                    if len(own) >= 3:
                        fc = own
                    elif fc.series.nunique() > 1:
                        continue
                if "doping_or_composition" in fc.columns and pd.notna(r.sample_identifier):
                    own = fc[fc.doping_or_composition.astype(str)
                             == str(r.sample_identifier)]
                    if len(own) >= 3:
                        fc = own
                # points on the frame or on a tick are not data
                if src == "figure" and "n_pixels" in fc.columns and "py" in fc.columns:
                    cal = os.path.join(RE, TRACES[k] + "_calibration.json")
                    if os.path.exists(cal):
                        import json
                        m = json.load(open(cal)).get("frame_px") or {}
                        yb = m.get("y_bottom")
                        if yb:
                            fc = fc[fc.py < yb - 8]
                fc = fc[fc[col] > 0]
                if len(fc) < 3:
                    continue
                H = fc.field_T.values * sc
                J = fc[col].values
                hi = float(H.max() / r.Hc2_T_used)
                below = J[H < r.Hc2_T_used]
                carry = float(below.max() / J.max()) if len(below) else np.nan
                at_bound = (float(below[np.argmax(H[H < r.Hc2_T_used])] / J.max())
                            if len(below) else np.nan)
                at_own_T = anchor_temperature(r.Hc2_source)
                same_T = (at_own_T is None
                          or abs(at_own_T - r.fixed_axis_value) <= 1.0)
                labelled_hc2 = "term_Hc2" in str(r.Hc2_source)
                fabricated = (src == "extraction" and k in FABRICATED)
                if hi > 1.0 or (np.isfinite(at_bound) and at_bound > CARRY_FRACTION):
                    over.append(dict(paper=k, src=src, hi=hi, bound=at_bound,
                                     decisive=hi > 1.0, same_T=same_T,
                                     labelled_hc2=labelled_hc2,
                                     fabricated=fabricated))
                    print("%-40s %-14s %5.1f %7.2f %8.2f %9s %s"
                          % (k[:40], str(r.sample_identifier)[:14],
                             r.fixed_axis_value, r.Hc2_T_used, hi,
                             ("%.2f" % at_bound) if np.isfinite(at_bound) else "-",
                             src))
                break
    ov = pd.DataFrame(over)
    dec = ov[ov.decisive] if len(ov) else ov
    print("\n  fits flagged                                           : %d" % len(ov))
    print("  of those, DECISIVE - the data reaches or passes its Hc2 : %d over %d papers"
          % (len(dec), dec.paper.nunique() if len(dec) else 0))
    if len(dec):
        for k, g in dec.groupby("paper"):
            print("      %-44s %2d fits, worst Hmax/Hc2 %.2f"
                  % (k[:44], len(g), g.hi.max()))
    print()
    print("  Each screen below removes a class the first version counted:")
    a = dec[~dec.fabricated]
    print("      dropping sources the repository grades fabricated : %d over %d papers"
          % (len(a), a.paper.nunique() if len(a) else 0))
    b = a[a.same_T]
    print("      and requiring the anchor be read at this temperature: %d over %d"
          % (len(b), b.paper.nunique() if len(b) else 0))
    c2 = b[b.labelled_hc2]
    print("      and requiring the anchor be labelled term_Hc2       : %d over %d"
          % (len(c2), c2.paper.nunique() if len(c2) else 0))
    if len(c2):
        for k, g in c2.groupby("paper"):
            print("          %-40s %d fits" % (k[:40], len(g)))
    print()
    print("  Only the last line is impossible. An anchor recorded as an")
    print("  irreversibility field is a criterion, and matchemphys's traced curves")
    print("  reach that paper's own Jc = 100 A/cm2 criterion at 3.14 T against a")
    print("  recorded 3.00, which confirms the anchor. The rest are a signal.")
    print("  No passing fit is FITTED on a point at or above its anchor: the")
    print("  fitter filters H < Hc2 and the largest normalised range is 0.999.")
    print("  This is evidence about the anchor, not about fit contamination.")

    print()
    print("=" * 96)
    print("4. THE SLOPE Hc2 AND Tc IMPLY")
    print("=" * 96)
    print("dHc2/dT near Tc, from the anchor and Tc. Iron-based and MgB2 samples")
    print("run about 1 to 5 T per kelvin; a value far below that is a signal.")
    print("%-40s %-14s %6s %7s %8s %s"
          % ("paper", "sample", "Tc", "Hc2", "T/K", ""))
    for k in sorted(p.paper_key.unique()):
        g = p[p.paper_key == k]
        r = g.iloc[0]
        Tc = r.Tc_K_anchor
        if not (Tc and np.isfinite(Tc)):
            continue
        lo = g.loc[g.fixed_axis_value.idxmin()]
        if lo.fixed_axis_value >= Tc:
            continue
        slope = lo.Hc2_T_used / (Tc - lo.fixed_axis_value)
        flag = "LOW" if slope < 0.5 else ("high" if slope > 8 else "")
        print("%-40s %-14s %6.1f %7.2f %8.2f %s"
              % (k[:40], str(lo.sample_identifier)[:14], Tc, lo.Hc2_T_used,
                 slope, flag))

    print()
    print("=" * 96)
    print("5. WHAT THE PROVENANCE STRINGS SAY")
    print("=" * 96)
    c = p.Hc2_source.value_counts()
    print("  distinct provenance strings among the %d passing fits : %d"
          % (len(p), len(c)))
    amb = p[p.Hc2_source.str.contains("ambiguous", na=False)]
    print("  fits whose anchor term the deposit itself records as ambiguous : %d"
          % len(amb))
    for k, g in amb.groupby("paper_key"):
        print("      %-44s %d fits" % (k[:44], len(g)))
    lit = p[p.Hc2_source.str.startswith("Tier_3")]
    print("  fits on a literature default : %d over %d papers"
          % (len(lit), lit.paper_key.nunique()))
    for k, g in lit.groupby("paper_key"):
        print("      %-44s %d fits, Hc2 %.1f T"
              % (k[:44], len(g), g.Hc2_T_used.iloc[0]))


if __name__ == "__main__":
    main()
