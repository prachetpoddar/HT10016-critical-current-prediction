#!/usr/bin/env python3
"""
audit_tier1_critical_fields.py

Screen the critical-field scale behind every Form 3 field-axis fit.

ONE test survives. Two earlier ones were wrong, and both were wrong in the
direction that made the screen look productive. They are described below rather
than deleted, because each looked like a finding and neither was.

The test that survives: WITHIN A SAMPLE, the assigned scale must fall with
temperature. Upper critical fields fall, irreversibility fields fall, and
nothing legitimate rises. Grouped by sample, never averaged across samples: an
earlier version regressed after averaging and physc.2013.04.060 appeared to
rise when the rise was entirely sample composition, three samples at 4.2 K and
five different ones at 10 K.

It flags three papers and 36 of the 159 fits, and all three were independently
read at source before this screen existed. That is the honest strength of the
result: the screen confirms three known cases and finds no new ones.

--------------------------------------------------------------------------
The two tests that were wrong

WRONG: "the scale sits at or below the largest field measured". It compared
Hc2_T_used against the maximum field in the paper's raw extraction file. The
pipeline filters points to those below the scale BEFORE fitting, so the raw
file legitimately extends past it. Checked directly: the recorded
H_axis_range_normalized equals the span of the retained points exactly on every
fit examined, and no fit in the table has a span at or above 1, the maximum
being 0.9987. The test was measuring the extraction file and calling it a
property of the fit. It flagged five papers and 42 fits, two of which
(matchemphys.2023.128348 and matpr.2019.05.078) it flagged on nothing else.

WRONG: "a constant scale with a larger one unused in the same file". In both
cases it fired on, the larger value is a zero-temperature extrapolation.
s10854-026-16566-9's 78.1 T is a WHH row with NO temperature recorded, sitting
beside a proper Hc2(T) curve that falls from 9.2 T at 11 K to 0.0 at 16 K.
phpro.2015.06.160's 26 T and 31 T are Hc2(0) values tagged with each compound's
transition temperature, 18.9 K and 25.5 K, and its 9.0 T at 17.7 K is an
ordinary Hc2(T) point: an ac-susceptibility transition reaching 17.7 K on the
9 T curve is Hc2(17.7 K) = 9 T. Both papers' fits then use the lowest-temperature
Hc2 available as a low-temperature anchor, which is the deposit's documented
extrapolated_to_low_T_anchor convention and is conservative rather than wrong.
It flagged two papers and 18 fits.

Between them those two tests were most of the screen: 60 flagged fits became
36, and the claim that every MgB2-class field-axis fit rested on a bad scale
became none of them.

--------------------------------------------------------------------------
What is reported but no longer claimed as a finding

The screen still prints how the applicability filter divides flagged from
unflagged fits, because the pattern is worth seeing. It is no longer offered as
a mechanism. On three papers it is as consistent with those three papers being
unusual as with the filter selecting for the error, and a claim that needs the
first version's 60 fits to be interesting is a claim that was resting on the
two broken tests.

    python3 analysis/audit_tier1_critical_fields.py [--csv]

Run from the repository root. Changes nothing.
"""
import argparse
import csv
import glob
import os
import sys

import numpy as np
import pandas as pd

DATA = "data"
FITS = os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv")
OUT = os.path.join("audit", "tier1_critical_field_screen.csv")
EXT = "/home/claude/ext"


def hct_rows(paper_id):
    p = os.path.join(EXT, "%s_HcT_supplementary.csv" % paper_id)
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        return list(csv.DictReader(fh))


def measured_max(paper_id):
    """Largest field the paper's own extracted curves reach, per isotherm."""
    p = os.path.join(EXT, "%s_VISION_PASS_LONG.csv" % paper_id)
    if not os.path.exists(p):
        return None
    out = {}
    with open(p) as fh:
        for r in csv.DictReader(fh):
            try:
                t = round(float(r["fixed_axis_value"]), 3)
                h = float(r["field_T"])
            except (TypeError, ValueError, KeyError):
                continue
            out[t] = max(out.get(t, 0.0), h)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")

    f = pd.read_csv(FITS)
    tier = f.Hc2_source.astype(str).str.extract(r"^(Tier_\d)")[0]
    f = f.assign(tier=tier)

    rows = []
    for pid, g in sorted(f.groupby("arxiv_id")):
        flags, detail = [], []

        # 1. rises with temperature, within a sample
        for sid, s in g.groupby("sample_identifier"):
            p = s.groupby("fixed_axis_value").Hc2_T_used.mean().sort_index()
            if len(p) > 1:
                sl = float(np.polyfit(p.index.values, p.values, 1)[0])
                if sl > 0.01:
                    flags.append("rises within a sample")
                    detail.append("%s: %.3g T at %g K to %.3g T at %g K"
                                  % (sid, p.iloc[0], p.index[0],
                                     p.iloc[-1], p.index[-1]))
                    break

        # Tests 2 and 3 lived here and were removed; see the module
        # docstring. What remains needs neither the extraction file nor the
        # supplementary file, so the screen no longer depends on anything
        # outside the deposit.
        rows.append(dict(
            paper_id=pid, fits=len(g),
            tiers=";".join(sorted(set(g.tier.dropna()))),
            passing=int((g.physicality == "ok").sum()),
            hc2_min=round(float(g.Hc2_T_used.min()), 3),
            hc2_max=round(float(g.Hc2_T_used.max()), 3),
            median_span=round(float(g.H_axis_range_normalized.median()), 4),
            verdict=";".join(flags) or "none",
            detail=" | ".join(detail)[:300]))

    r = pd.DataFrame(rows).sort_values(["verdict", "fits"],
                                       ascending=[True, False])
    print("critical-field scale behind %d field-axis fits, %d papers\n"
          % (len(f), f.arxiv_id.nunique()))
    for _, x in r.iterrows():
        print("   %-42s %3d fits %3d pass  %-10s %s"
              % (x.paper_id.replace("elsevier_", "").replace("springer_", ""),
                 x.fits, x.passing, x.tiers.replace("Tier_", "T"), x.verdict))
        if x.detail:
            print("        %s" % x.detail[:150])

    bad = r[r.verdict != "none"]
    print("\n   %d of %d papers flagged, %d of %d fits, %d of %d passing fits"
          % (len(bad), len(r), int(bad.fits.sum()), int(r.fits.sum()),
             int(bad.passing.sum()), int(r.passing.sum())))

    # 4. what the applicability filter does with all of it
    flagged = f.arxiv_id.isin(set(bad.paper_id))
    print("\nhow the applicability filter divides the two groups\n")
    print("   Reported, not claimed. On three papers this is as consistent "
          "with those\n   three being unusual as with the filter selecting "
          "for the error, and the\n   stronger reading rested on two tests "
          "that turned out to be wrong.\n")
    ct = pd.crosstab(flagged, f.physicality)
    print(ct.rename(index={True: "flagged", False: "unflagged"}).to_string())
    print("\n   median reduced span   flagged %.3f   unflagged %.3f"
          % (f[flagged].H_axis_range_normalized.median(),
             f[~flagged].H_axis_range_normalized.median()))
    print("\n   by provenance tier:")
    print(pd.crosstab(f.tier, f.physicality).to_string())
    print("\n   The criterion admits a curve when (Hmax - Hmin) / Hc2 exceeds "
          "0.3, so a\n   scale that is too small widens that ratio. Whether "
          "the filter therefore\n   selects for the error is a hypothesis this "
          "screen cannot test on three\n   papers. The tier split below is "
          "the observation that suggested it.")

    if args.csv:
        os.makedirs("audit", exist_ok=True)
        r.to_csv(OUT, index=False)
        print("\n   written %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
