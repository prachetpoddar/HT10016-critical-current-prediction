#!/usr/bin/env python3
"""The exponent-drift figures behind A3, recomputed, with a replacement example.

Referee A's central objection is that Eq. (1) is an expansion near the critical
scale and is used far from it. The response concedes it and quantifies the cost:

  "Across the 18 series in which one scale was held over three or more
  measurement temperatures, the median absolute rank correlation between
  exponent and temperature is 0.70, rising to 0.80 in the nine series sampled
  at four or more temperatures. In the clearest case, SmFeAsO0.8F0.2 with a
  scale held at 86 T, the fitted exponent runs from 1.25 to 12.14 as the
  temperature rises from 2 to 35 K."

**Those four numbers were right when they were written.** A first version of
this file reported that they do not reproduce on any state of the fit table, and
adversarial review refuted it. The error was in the grouping: `sample_identifier`
encodes the measurement temperature for eight papers, so keying on it splits one
temperature sweep into singletons that then fail the three-temperature test and
vanish. That dropped 44 of 159 rows, including every row of the letter's own
worked example, which is why a first run could not find it.

Grouped correctly, on the release table the figures come out exactly: 18 series
at three or more temperatures with a median absolute rank correlation of 0.700,
and 9 at four or more with 0.800. They are stale, not unreproducible, and the
difference matters: telling a referee that a number cannot be reproduced when it
was correct at deposit invites doubt about every other number in the letter.

The definition, stated so it can be checked. A series is one source paper, one
sample, and one held critical scale; the statistic is the absolute Spearman
correlation between the fixed measurement temperature and the fitted field
exponent. Keying on the scale is what makes "one scale was held" true by
construction, which is the letter's own wording, and it splits a sample that was
fitted against several scales into its per-scale runs rather than discarding it.
Two readings of that rule are computed and they agree everywhere: keying on the
raw sample identifier and the scale, and stripping the temperature suffix from
the identifier and then requiring one scale within the sample.

The worked example has to go, for two independent reasons. `physc.2009.05.098`'s
printed field axis is kilo-oersted recorded as tesla; corrected, its spans fall
from 0.53 to 0.053 of the assigned scale, all eight fits fail the 0.3
applicability bound, and its field-axis fits were withdrawn on 2026-09-05. And
separately, the exponent is not monotone over the quoted window: it falls from
1.252 at 2 K to 0.819 at 10 K before rising to 12.145 at 35 K, so "runs from
1.25 to 12.14 as the temperature rises" describes a rise that does not happen
for the first third of the range. The rank correlation over that window is
0.786, not 1. The 40 K point, which sits at the fitter's 30.0 ceiling, is
outside the quoted window and stays out of any replacement.

    python analysis/exponent_drift_series.py

Run from the repository root.
"""
import io
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
RELEASE_REV = "8ad8d43"
CEILING = 30.0
QUOTED = dict(n3=18, med3=0.700, n4=9, med4=0.800)
OUT = os.path.join("audit", "exponent_drift_series.csv")


def strip_temperature(s):
    return re.sub(r"[_\-]\d+(?:\.\d+)?\s*K$", "", str(s), flags=re.I).strip()


def series(f, need=3, reading="scale_key"):
    """One row per (paper, sample, held scale) with at least `need` temperatures.

    Two readings of the same rule, kept because agreement between them is what
    says the rule is not an artefact of one spelling.

      scale_key   group on the raw sample identifier and the scale used
      strip_first collapse the temperature suffix on the identifier, then
                  require a single scale within the sample
    """
    f = f.copy()
    f["sid"] = f.sample_identifier.map(strip_temperature)
    if reading == "scale_key":
        keys, require_one = ["arxiv_id", "sample_identifier", "Hc2_T_used"], False
    else:
        keys, require_one = ["arxiv_id", "sid"], True
    rows = []
    for _k, g in f.groupby(keys):
        g = g.dropna(subset=["beta", "fixed_axis_value"])
        if require_one and g.Hc2_T_used.nunique() != 1:
            continue
        if g.fixed_axis_value.nunique() < need:
            continue
        r = spearmanr(g.fixed_axis_value, g.beta).correlation
        if not np.isfinite(r):
            continue
        rows.append(dict(
            paper=g.arxiv_id.iloc[0], sample=g.sid.iloc[0],
            compound=g.compound_formula.iloc[0],
            scale=float(g.Hc2_T_used.iloc[0]),
            n_temps=int(g.fixed_axis_value.nunique()),
            rho=float(r), abs_rho=abs(float(r)),
            beta_lo=float(g.beta.min()), beta_hi=float(g.beta.max()),
            t_lo=float(g.fixed_axis_value.min()),
            t_hi=float(g.fixed_axis_value.max()),
            at_ceiling=bool(g.beta.max() >= CEILING - 0.01),
            has_bound=bool((g.physicality != "ok").any())))
    return pd.DataFrame(rows)


def summarise(f, reading="scale_key"):
    a, b = series(f, 3, reading), series(f, 4, reading)
    return (len(a), float(a.abs_rho.median()) if len(a) else np.nan,
            len(b), float(b.abs_rho.median()) if len(b) else np.nan)


def states():
    out = [("current deposit", pd.read_csv(FITS))]
    for d in sorted(os.listdir("audit")):
        p = os.path.join("audit", d, os.path.basename(FITS))
        if os.path.isfile(p):
            out.append((d, pd.read_csv(p)))
    r = subprocess.run(["git", "show", "%s:%s" % (RELEASE_REV, FITS)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        # Reporting "no state of the table reproduces this" while silently
        # skipping the state that does is the failure this guards against.
        raise SystemExit("the release table at %s could not be read, so the "
                         "comparison would be missing the one state that "
                         "matters" % RELEASE_REV)
    out.append(("release %s" % RELEASE_REV, pd.read_csv(io.StringIO(r.stdout))))
    return out


def main():
    print("the letter's figures against every state of the fit table\n")
    print("   %-38s %5s %8s %5s %8s"
          % ("table", "n>=3", "median", "n>=4", "median"))
    hit = []
    for lab, f in states():
        n3, m3, n4, m4 = summarise(f)
        exact = (n3 == QUOTED["n3"] and abs(m3 - QUOTED["med3"]) < 5e-3
                 and n4 == QUOTED["n4"] and abs(m4 - QUOTED["med4"]) < 5e-3)
        if exact:
            hit.append(lab)
        print("   %-38s %5d %8.3f %5d %8.3f%s"
              % (lab, n3, m3, n4, m4, "   the letter exactly" if exact else ""))
    print("   %-38s %5d %8.2f %5d %8.2f"
          % ("the letter", QUOTED["n3"], QUOTED["med3"], QUOTED["n4"],
             QUOTED["med4"]))
    if not hit:
        raise SystemExit("no state reproduces the letter, so the definition is "
                         "wrong and nothing here is reportable")
    print("\n   reproduced on: %s" % ", ".join(hit))

    cur = pd.read_csv(FITS)
    a, b = summarise(cur, "scale_key"), summarise(cur, "strip_first")
    if a != b:
        raise SystemExit("the two readings of the rule disagree on the current "
                         "table: %s against %s" % (a, b))
    print("   both readings of the rule agree: %d series at three or more "
          "temperatures," % a[0])
    print("   median %.3f, and %d at four or more, median %.3f, on the current "
          "table" % (a[1], a[2], a[3]))

    print("\nthe worked example\n")
    g = cur[cur.arxiv_id.astype(str).str.contains("physc.2009.05.098",
                                                  regex=False)]
    g = g.dropna(subset=["beta"]).sort_values("fixed_axis_value")
    if g.empty:
        raise SystemExit("the letter's example is not in the table, which the "
                         "account does not explain")
    w = g[(g.fixed_axis_value >= 2) & (g.fixed_axis_value <= 35)]
    mono = bool((np.diff(w.beta.values) > 0).all())
    print("   %s, scale %.1f T, %d temperatures"
          % (g.compound_formula.iloc[0], g.Hc2_T_used.iloc[0], len(g)))
    print("   over the quoted 2 to 35 K window: exponent %.3f to %.3f, "
          "rank correlation %.3f"
          % (w.beta.min(), w.beta.max(),
             spearmanr(w.fixed_axis_value, w.beta).correlation))
    print("   monotone across that window: %s" % ("yes" if mono else "no"))
    if mono:
        raise SystemExit("the example is monotone, so the second reason for "
                         "replacing it does not hold")
    print("   it falls from %.3f at %.0f K to %.3f at %.0f K before rising, so "
          "the letter's" % (g.beta.iloc[0], g.fixed_axis_value.iloc[0],
                            g.beta.min(),
                            float(g.loc[g.beta.idxmin(), "fixed_axis_value"])))
    print("   'runs from 1.25 to 12.14 as the temperature rises' describes a "
          "rise that does not")
    print("   happen over the first third of the range")

    sys.path.insert(0, os.path.abspath("analysis"))
    import build_supplement_tables as bst          # noqa: E402
    banned = {x for x in bst.withdrawn_tokens() if x}
    s = series(cur, 3)
    s["banned"] = s.paper.apply(lambda p: any(x in str(p) for x in banned))
    live = s[~s.banned & ~s.at_ceiling & ~s.has_bound].sort_values(
        "abs_rho", ascending=False)
    print("\n   candidates for a replacement: no ledger withdrawal, no fit at "
          "the %.0f ceiling,\n   no bound fit in the series\n" % CEILING)
    print("      %-34s %-16s %6s %4s %6s %s"
          % ("paper", "compound", "scale", "n", "rho", "exponent range"))
    for _i, r in live.iterrows():
        print("      %-34s %-16s %6.1f %4d %6.2f  %.3f to %.3f over "
              "%.1f to %.1f K"
              % (str(r.paper)[-34:], str(r.compound)[:16], r.scale, r.n_temps,
                 r.rho, r.beta_lo, r.beta_hi, r.t_lo, r.t_hi))
    print("\n   Both come from one paper. The polycrystal record of that paper "
          "is the copy of its")
    print("   own single crystal that audit/defect_backtrack_20260904.md "
          "identifies, and its anchor")
    print("   row is withdrawn, so only the single crystal is usable. That "
          "record is graded weak,")
    print("   1.3 to 1.7 times high with a wrong tail, and the letter has to "
          "say so if it uses it.")
    s.to_csv(OUT, index=False)
    print("\n   written to %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
