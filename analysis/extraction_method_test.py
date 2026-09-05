#!/usr/bin/env python3
"""
extraction_method_test.py

Does how an extraction was made predict whether it reproduces its figure?

The census found the four papers' agreement ordering matched their extraction
route, hand digitisation being much the best. That was four papers, so it needed
testing on everything else that can be tested. The finer ordering the census
suggested, vision_pass ahead of vision_pass_round3, is NOT reproduced here: over
more papers the two are the other way round (0.949 against 0.662) and the
difference between them is not the finding. The difference between hand and
machine is.

This scores every paper that has both a pixel trace of its own figure and an
extraction file, on one statistic: the median of |log10(extracted Jc / figure
Jc)| over the extraction's own points, interpolated on the traced curve. It is
the extracted values that are being judged, not the fitted exponent, because the
question is about the extraction step.

What this can and cannot show, stated before the numbers because an independent
review found the first version overstated all three.

  It measures REPRODUCIBILITY, not correctness. Comparing a hand digitisation
  with a pixel trace compares two readings of one curve. The sharpest case is
  jallcom.2023.170384, whose text states jc = 2e6 A/cm2 at 2 K in self field.
  The hand extraction gives 3.34e6 and the trace 3.89e6: they agree with each
  other four times better than either agrees with the paper. A score of 0.009
  says two careful readings converge, not that they are right.

  One of the three hand papers is the digitiser's own calibration target.
  jallcom.2023.170384 is the figure the tool was validated against before it was
  trusted (audit/recovery_begins_20260904.md), and one of the fixes made in that
  same commit was decided by comparison with these very values. It is reported
  separately below and excluded from the headline.

  The vision arm is selected. Five of its nine papers were graded FAIL in
  audit/extraction_integrity.csv before they were traced. Its median is
  therefore not a rate, and the comparison is run again with them removed.

  A poor score for a vision pass is the one direction that is not weakened: if a
  vision pass disagrees with a pixel trace of the same figure by more than a
  decade, one of them is wrong, and on the two figures with an in-text anchor
  the trace is the one that matches.

    python3 analysis/extraction_method_test.py

Run from the repository root. Changes nothing.
"""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd

EXT = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
       "v3_2_2B_extension/")
RE = os.path.join("data", "reextraction")

# paper -> (extraction file stem, trace stem(s), field factor to reach tesla,
#           how the extraction's sample column maps onto the trace's series)
CASES = [
    dict(paper="physc.2013.04.060", method="hand",
         ext=["10.1016_j.physc.2013.04.060_MgB2_C_doping_series_transport_4_2K",
              "10.1016_j.physc.2013.04.060_MgB2_dopant_series_transport_10K"],
         traces=["physc_2013_04_060_fig2", "physc_2013_04_060_fig3"], scale=1.0,
         smap={"MgB2_4_2K": "MgB2-00", "MgB(2-x)Cx_x_0_0386_4_2K": "MgB2-01",
               "MgB(2-x)Cx_x_0_1202_4_2K": "MgB2-04"},
         drop=set()),   # MgB2-00 was dropped in the first version because the
                        # black trace also matches the other curves' connecting
                        # lines. Dropping it changed the median by 0.0001 and
                        # turned 59 of 62 inside 0.1 dex into 59 of 59, so it is
                        # restored: the contamination is a defect of the trace,
                        # not a reason to hide the paper's three worst points.
    dict(paper="physc.2011.02.004 (1002.0208v2)", method="hand",
         ext=["10.1016_j.physc.2011.02.004_PrFeAsO_magnetization_5-35K"],
         traces=["1002_0208v2_fig5a"], scale=1.0, smap={}, drop=set()),
    dict(paper="jallcom.2023.170384", method="hand",
         ext=["10.1016_j.jallcom.2023.170384_LaFeAsO_magnetization_2-10K"],
         traces=["jallcom_2023_170384_fig6c"], scale=1.0, smap={}, drop=set(),
         calibration_target=True),
    dict(paper="matchemphys.2023.128348", method="vision_pass",
         ext=["10.1016_j.matchemphys.2023.128348_VISION_PASS"],
         traces=["matchemphys_2023_128348_fig5"], scale=1.0, smap={}, drop=set()),
    dict(paper="matpr.2019.05.078", method="vision_pass",
         ext=["10.1016_j.matpr.2019.05.078_VISION_PASS"],
         traces=["matpr_2019_05_078_fig2a"], scale=1.0, smap={}, drop=set()),
    dict(paper="phpro.2015.06.160", method="vision_pass",
         ext=["10.1016_j.phpro.2015.06.160_VISION_PASS"],
         traces=["phpro_2015_06_160_fig3L"], scale=1.0, smap={}, drop=set()),
    dict(paper="mtphys.2022.100783", method="vision_pass",
         ext=["10.1016_j.mtphys.2022.100783_VISION_PASS"],
         traces=["mtphys_2022_100783_fig6a", "mtphys_2022_100783_fig6b"],
         scale=1.0, smap={}, drop=set(), flagged=True,
         panelled="two traced panels are different specimens about 1.0 dex "
                  "apart and both name their only series 4.2K, while the "
                  "extraction spans 4.2 to 21 K"),
    dict(paper="s10854-026-16566-9", method="vision_pass",
         ext=["springer_10.1007_s10854-026-16566-9_VISION_PASS"],
         traces=["s10854_fig9a", "s10854_fig9b", "s10854_fig9c", "s10854_fig9d"],
         scale=1.0, smap={}, drop=set(), flagged=True,
         panelled="four traced panels are four MWCNT levels 0.86 to 1.93 dex "
                  "apart and all name their series 5K, 7K, 10K"),
    dict(paper="physc.2009.11.051", method="vision_pass_round3",
         ext=["10.1016_j.physc.2009.11.051_VISION_PASS"],
         traces=["physc_2009_11_051_fig3"], scale=0.1, smap={}, drop=set(),
         flagged=True),
    dict(paper="physc.2010.05.048", method="vision_pass_round3",
         ext=["10.1016_j.physc.2010.05.048_VISION_PASS"],
         traces=["physc_2010_05_048_fig3"], scale=0.1, smap={}, drop=set()),
    dict(paper="ceramint.2024.10.058", method="vision_pass_round3",
         ext=["10.1016_j.ceramint.2024.10.058_VISION_PASS"],
         traces=["ceramint_2024_10_058_fig4"], scale=1.0, smap={}, drop=set(),
         flagged=True),
    dict(paper="jallcom.2013.04.183", method="vision_pass_round3",
         ext=["10.1016_j.jallcom.2013.04.183_VISION_PASS"],
         traces=["jallcom_2013_04_183_fig8"], scale=1.0, smap={}, drop=set(),
         flagged=True, jc_scale=10.0),
]


def load_ext(stems):
    out = []
    for s in stems:
        for f in glob.glob(EXT + "elsevier_" + s + "_LONG.csv") + \
                 glob.glob(EXT + s + "_LONG.csv"):
            out.append(pd.read_csv(f))
    return pd.concat(out, ignore_index=True) if out else None


def sample_of_row(r):
    for c in ("doping_or_composition", "sample_identifier", "notes"):
        v = str(r.get(c, ""))
        if c == "notes" and "sample=" in v:
            return v.split("sample=")[1].split(";")[0].strip()
        if c != "notes" and v and v != "nan":
            return v
    return ""


def curve(t, series, T, strict=False):
    g = t
    if series is not None and "series" in t.columns:
        g = t[t.series == series]
    if "temperature_K" in g.columns and T is not None:
        near = g[np.isclose(g.temperature_K, T, atol=0.35)]
        if len(near) >= 3:
            g = near
        elif strict:
            # no traced isotherm at this temperature: refuse rather than fall
            # back to every temperature pooled
            return None, None
    g = g[g.Jc_A_per_cm2 > 0].sort_values("field_T")
    g = g[g.field_T > 0]
    if len(g) < 3:
        return None, None
    x = np.log10(g.field_T.values.astype(float))
    y = np.log10(g.Jc_A_per_cm2.values.astype(float))
    keep = np.concatenate([[True], np.diff(x) > 0])
    return x[keep], y[keep]


def score(case):
    e = load_ext(case["ext"])
    if e is None or e.empty:
        return None
    ts = [pd.read_csv(os.path.join(RE, n + "_points.csv")) for n in case["traces"]
          if os.path.exists(os.path.join(RE, n + "_points.csv"))]
    if not ts:
        return None
    t = pd.concat(ts, ignore_index=True)
    if "series" in t.columns and len(case["traces"]) > 1 and case.get("panelled"):
        # several panels whose series names collide: the samples cannot be told
        # apart, so nothing here is comparable
        return dict(unscorable=case.get("panelled"))
    allser = sorted(t.series.astype(str).unique()) if "series" in t.columns else []
    # A panel holds one specimen when every series name is just a temperature.
    single_sample = bool(allser) and all(
        re.fullmatch(r"[0-9]+(\.[0-9]+)?\s*K", q) for q in allser)
    d, unmatched = [], []
    for _, r in e.iterrows():
        H = float(r.get("field_T", np.nan)) * case["scale"]
        J = float(r.get("Jc_A_per_cm2", np.nan)) * case.get("jc_scale", 1.0)
        T = float(r.get("temperature_K", np.nan))
        if not (H > 0 and J > 0):
            continue
        samp = case["smap"].get(sample_of_row(r), sample_of_row(r))
        # Unique matching only. The first version fell back to pooling every
        # series when a label did not match, which silently compared s10854's
        # four MWCNT panels against each other (0.86 to 1.93 dex apart) and
        # mtphys's two specimens (about 1.0 dex apart). Both are now unscorable,
        # which is the honest outcome.
        if single_sample:
            # the traced panel holds one specimen and its series are temperature
            # labels, so the isotherm alone identifies the curve
            ser = None
        else:
            exact = [q for q in allser if q == samp]
            if not exact and samp:
                exact = [q for q in allser if q.lower().startswith(samp.lower())]
            if allser and not exact:
                unmatched.append(samp)
                continue
            ser = exact[0] if exact else None
        if ser in case["drop"]:
            continue
        x, y = curve(t, ser, T if np.isfinite(T) else None, strict=True)
        if x is None:
            continue
        lh = np.log10(H)
        if lh < x.min() or lh > x.max():
            continue
        d.append(np.log10(J) - float(np.interp(lh, x, y)))
    if len(d) < 3:
        return dict(unscorable="only %d comparable points after unique matching"
                    % len(d))
    a = np.array(d)
    return dict(n=len(a), med=float(np.median(np.abs(a))),
                ratio=float(10 ** np.median(a)),
                w01=int((np.abs(a) < 0.1).sum()))


def main():
    rows, notes = [], []
    print("=" * 92)
    print("HOW THE EXTRACTION WAS MADE AGAINST HOW WELL IT REPRODUCES THE FIGURE")
    print("=" * 92)
    print("Unique matching only: a point is scored against its own sample's own")
    print("isotherm or it is not scored. Two on-file unit repairs are applied to")
    print("both arms alike, the kilo-oersted field error in two vision extractions")
    print("and the tenfold Jc error in a third.")
    print()
    print("%-30s %-19s %5s %8s %8s %6s %s"
          % ("paper", "route", "pts", "|log10|", "ratio", "in0.1", "note"))
    for c in CASES:
        s_ = score(c)
        tag = ("CALIBRATION TARGET" if c.get("calibration_target")
               else ("pre-graded FAIL" if c.get("flagged") else ""))
        if not s_ or s_.get("unscorable"):
            why = (s_ or {}).get("unscorable", "no comparable points")
            print("%-30s %-19s %5s %8s %8s %6s %s"
                  % (c["paper"][:30], c["method"], "-", "unscorable", "-", "-", tag))
            notes.append((c["paper"], why))
            continue
        rows.append(dict(paper=c["paper"], method=c["method"],
                         flagged=bool(c.get("flagged")),
                         target=bool(c.get("calibration_target")), **s_))
        print("%-30s %-19s %5d %8.3f %8.2f %6d %s"
              % (c["paper"][:30], c["method"], s_["n"], s_["med"], s_["ratio"],
                 s_["w01"], tag))
    for p_, w in notes:
        print("\n  %s not scored: %s" % (p_, w))

    r = pd.DataFrame(rows)
    if r.empty:
        return
    hand = r[r.method == "hand"]
    vis = r[r.method != "hand"]

    print()
    print("=" * 92)
    print("THE COMPARISON, UNDER EVERY EXCLUSION THAT MATTERS")
    print("=" * 92)
    print("%-46s %6s %9s %s" % ("set", "papers", "median", "range"))

    def line(lab, g):
        if len(g) == 0:
            return
        print("%-46s %6d %9.3f   %.3f to %.3f"
              % (lab, len(g), g.med.median(), g.med.min(), g.med.max()))

    line("hand, all", hand)
    line("hand, excluding the calibration target", hand[~hand.target])
    line("vision, all scorable", vis)
    line("vision, excluding those pre-graded FAIL", vis[~vis.flagged])
    print()
    h2 = hand[~hand.target]
    v2 = vis[~vis.flagged]
    print("  The separation is complete at the paper level in every version:")
    print("      worst hand %.3f against best vision %.3f"
          % (hand.med.max(), vis.med.min()))
    if len(h2) and len(v2):
        print("      excluding both the target and the pre-graded: %.3f against %.3f"
              % (h2.med.max(), v2.med.min()))
    print()
    print("  It is not complete at the isotherm level. Three of about forty-five")
    print("  vision curves score inside the hand range, all of them in")
    print("  matchemphys.2023.128348. Collapsing each paper to one median is what")
    print("  makes the separation look total.")
    print()
    print("  No significance test is quoted. With %d against %d the smallest"
          % (len(hand), len(vis)))
    print("  achievable Mann-Whitney p is 1/C(%d,%d) = %.4f, and any complete"
          % (len(hand) + len(vis), len(hand),
             1.0 / np.math.comb(len(hand) + len(vis), len(hand))
             if hasattr(np, "math") else 0.0045))
    print("  separation returns exactly that, so the p value would restate")
    print("  'no overlap' and add nothing.")

    print()
    print("=" * 92)
    print("WHAT THIS DOES NOT LICENSE")
    print("=" * 92)
    print("  Hand digitisation has failed twice in this corpus, and neither")
    print("  failure is the kind this test can see:")
    print("      physc.2009.05.098   a kilo-oersted axis written into a tesla")
    print("                          column, 234 hand-read points, the reading")
    print("                          itself faithful")
    print("      jallcom.2023.170146 210 hand-read points filed under a DOI whose")
    print("                          PDF is a different paper entirely")
    print("  Both are unit and provenance errors, not reading errors. Reading the")
    print("  figure by hand fixes the values; it does not fix the label on the")
    print("  axis or the name on the file, and those are what removed sixteen")
    print("  passing fits elsewhere in this work.")
    print()
    print("  The three hand papers were also digitised by the author on figures he")
    print("  chose. audit/reextraction_input_triage.md shows what the rest look")
    print("  like: panels with fifteen unlabelled colour curves, figures with no")
    print("  temperature printed anywhere, and one isotherm carrying a single")
    print("  plotted marker against a nineteen-value extraction grid.")


if __name__ == "__main__":
    main()
