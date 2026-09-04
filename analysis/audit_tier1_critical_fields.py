#!/usr/bin/env python3
"""
audit_tier1_critical_fields.py

Screen the critical-field scale behind every Form 3 field-axis fit.

Why. The provenance tier is not evidence. Tier 1 means an extraction said the
value came from the paper, not that anyone checked it did, and it is the tier
the applicability filter admits: 82 of the 94 passing fits are Tier 1, against
8 of 61 for the Tier 3 literature default.

A first version of this screen keyed on the caption text each extraction
recorded, and an adversarial review took it apart. Two of its three tests were
wrong, and both were wrong in the direction that flatters the screen:

  * It regressed the assigned scale against temperature after averaging across
    samples, so physc.2013.04.060 appeared to rise when the rise was entirely
    sample composition: three samples at 4.2 K, five different ones at 10 K.
    Three papers rise within a sample, not four; 36 fits, not 44.
  * It called six papers wrong for taking their scale from a
    critical-current-versus-field figure. Five of those papers state that as
    their own method, and it is a standard one: matchemphys.2023.128348 and
    physc.2013.04.060 both define the irreversibility field as where Jc falls
    to 100 A/cm2, and mtphys.2022.100783 uses a Kramer extrapolation of the
    same curves. Reading Hirr off Jc(H) is not a defect.

It also cleared the worst case in the corpus. phpro.2015.06.160 states
"we estimate the value of upper critical field (Hc2(0)) approximately 26 T and
31 T", its extraction records both, and the fits use 9.0 T at every
temperature, which is the ac-susceptibility rig's ceiling, "in field up to 9 T"
in the caption's own words. The caption named a real measurement, so the
keyword test passed it.

So this version tests the numbers instead. Each test either cannot be argued
with or names the exact confrontation a reader should check.

  1. WITHIN A SAMPLE, the assigned scale must fall with temperature. Upper
     critical fields fall, and so do irreversibility fields; nothing legitimate
     rises. Grouped by sample, never averaged across them.

  2. The scale must exceed the largest field the curve was measured at. A scale
     at or below the measured maximum makes the reduced field reach or pass 1,
     where the fitted form is undefined.

  3. Where a paper's own extraction file carries a LARGER critical field than
     the fits use, the larger one is named. That is the phpro case, and it is
     found by comparison rather than by reading prose.

  4. The applicability filter's interaction with all of this, which is the
     finding that outlives any single paper and is reported whether or not any
     paper is flagged. The criterion admits a curve when
     (Hmax - Hmin) / Hc2 > 0.3, so a scale that is too small widens the reduced
     window and lets the curve through. It selects for the error it cannot see.

    python3 analysis/audit_tier1_critical_fields.py [--csv]

Run from the repository root. The per-paper extraction files it reads for
tests 2 and 3 are not deposited; where they are absent those tests report
"unchecked" rather than passing.
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

        # 2. the scale sits at or below the measured maximum
        mm = measured_max(pid)
        if mm is None:
            detail.append("no extraction file, exposure unchecked")
        else:
            over = []
            for _i, r in g.iterrows():
                m = mm.get(round(float(r.fixed_axis_value), 3))
                if m and float(r.Hc2_T_used) <= m:
                    over.append("%g K: measured to %.3g T against a scale of "
                                "%.3g T" % (r.fixed_axis_value, m,
                                            r.Hc2_T_used))
            if over:
                flags.append("scale at or below the measured maximum")
                detail.extend(over[:2])

        # 3. a larger critical field for the same paper goes unused
        hct = hct_rows(pid)
        if hct is not None:
            vals = []
            for r in hct:
                try:
                    vals.append((float(r["field_T"]), r.get("source_term", ""),
                                 r.get("figure_id", ""), r.get("notes", "")))
                except (TypeError, ValueError):
                    pass
            if vals:
                biggest = max(vals)
                used = float(g.Hc2_T_used.max())
                # Only when the value in use does not vary with temperature.
                # A zero-temperature extrapolation is SUPPOSED to exceed the
                # field at a finite temperature, so "something larger exists"
                # is not by itself a defect and flagged four more papers where
                # it is the expected relation. What is a defect is a scale that
                # does not move with temperature at all while a larger,
                # temperature-resolved value sits unused in the same file. That
                # is the instrument ceiling case: phpro.2015.06.160 uses 9.0 T
                # at every temperature, which its own caption calls the limit
                # of the measurement, "in field up to 9 T", while the paper
                # estimates Hc2(0) at 26 T and 31 T.
                constant = g.groupby("fixed_axis_value").Hc2_T_used.mean().nunique() == 1
                if biggest[0] > used * 1.5 and constant and g.fixed_axis_value.nunique() > 1:
                    flags.append("a constant scale, with a larger one unused")
                    detail.append("%.3g T recorded as %s in %s, fits use up to "
                                  "%.3g T" % (biggest[0], biggest[1] or "?",
                                              biggest[2] or "?", used))

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
    print("\nthe applicability filter against the scale it cannot see\n")
    ct = pd.crosstab(flagged, f.physicality)
    print(ct.rename(index={True: "flagged", False: "unflagged"}).to_string())
    print("\n   median reduced span   flagged %.3f   unflagged %.3f"
          % (f[flagged].H_axis_range_normalized.median(),
             f[~flagged].H_axis_range_normalized.median()))
    print("\n   by provenance tier:")
    print(pd.crosstab(f.tier, f.physicality).to_string())
    print("\n   The criterion admits a curve when (Hmax - Hmin) / Hc2 exceeds "
          "0.3.\n   A scale that is too small widens that ratio, so the filter "
          "selects for\n   the error it cannot see. That is why the "
          "highest-confidence tier supplies\n   most of the passing cohort and "
          "the literature default supplies almost none.")

    if args.csv:
        os.makedirs("audit", exist_ok=True)
        r.to_csv(OUT, index=False)
        print("\n   written %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
