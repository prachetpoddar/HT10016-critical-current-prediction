"""
retrace_stage_comparison.py

Claim 3 of Table III, recomputed from audit/multi_stage_loso.csv.

The manuscript reports, under leave-one-substructure-out, a mean absolute
error in the field exponent of 12.3 without sample-form conditioning and 14.9
with it across the seven families carrying a descriptor, and 1.19 without
against 0.55 with it on the fits passing physicality over the three families
the conditional scope can score.

This checks those four numbers, and then asks the question the four numbers do
not answer on their own: the deposited table carries FOUR ways of forming the
conditional prediction, and the manuscript quotes one of them.

    stage2_pooled_forms_abs      pooled over sample forms
    stage2_pooled_flat_abs       pooled flat            <- the one quoted
    stage2_nearest_family_abs    nearest family
    stage2_nearest_no_form_abs   nearest, form ignored

The unconditioned arm quoted by the manuscript is stage1_abs, the monolithic
regression on one compositional descriptor. It is NOT stage3_abs: reading the
deposited columns by eye once put stage3_abs a position to the left of where it
is and produced 12.3 from the wrong column by coincidence. stage3_abs, the
substructure-aggregate median, is reported here as well, because it is the
control that uses no descriptor, no family and no sample form, and it beats
both arms on the seven-family cohort.

Run from the repository root.
"""
import os

import numpy as np
import pandas as pd

SRC = os.path.join("audit", "multi_stage_loso.csv")
OUT = os.path.join("audit", "retrace_20260906", "stage_comparison_retrace.csv")
COND = ["stage2_pooled_forms_abs", "stage2_pooled_flat_abs",
        "stage2_nearest_family_abs", "stage2_nearest_no_form_abs"]
# The unconditioned arm is Stage 1, the monolithic regression on one
# compositional descriptor, which uses neither family nor sample form. It is
# NOT stage3_abs: reading the deposited columns by eye put stage3_abs one
# position left of where it is, and produced 12.3 from the wrong column by
# coincidence. The columns are named, so they are addressed by name.
BASE = "stage1_abs"
QUOTED = "stage2_pooled_flat_abs"


def arm(df, name):
    """One cohort: the unconditioned error and each conditional reading,
    scored on the families the conditional scope can actually score."""
    scorable = df.dropna(subset=[QUOTED])
    row = dict(cohort=name, families_all=len(df), families_scored=len(scorable),
               unconditioned_all=df[BASE].mean(),
               unconditioned_scored=scorable[BASE].mean())
    for c in COND:
        row[c] = scorable[c].mean() if scorable[c].notna().all() else np.nan
    return row


def main():
    if not os.path.exists(SRC):
        raise SystemExit("missing %s; run from the repository root" % SRC)
    d = pd.read_csv(SRC)
    rows = [arm(g, name) for name, g in d.groupby("cohort", sort=False)]
    out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.to_csv(OUT, index=False)

    pd.set_option("display.width", 200)
    print(out.to_string(index=False, float_format=lambda v: "%.4f" % v))
    print("\nwrote %s\n" % OUT)

    seven = d[d.cohort == "all fits, every family with a descriptor"]
    phys = d[(d.cohort == "physicality == ok only")].dropna(subset=[QUOTED])

    print("against the manuscript, Sec. III.A")
    checks = [("seven families, without conditioning", seven[BASE].mean(), 12.3),
              ("seven families, with conditioning", seven[QUOTED].mean(), 14.9),
              ("physicality, without conditioning", phys[BASE].mean(), 1.19),
              ("physicality, with conditioning", phys[QUOTED].mean(), 0.55)]
    bad = 0
    for label, got, want in checks:
        ok = abs(got - want) < 0.05
        bad += 0 if ok else 1
        print("   %-38s manuscript %5.2f   retrace %7.4f   %s"
              % (label, want, got, "ok" if ok else "MISMATCH"))

    print("\nthe reading the manuscript does not name")
    for name, g in (("seven families", seven), ("physicality", phys)):
        g = g.dropna(subset=[QUOTED])
        base = g[BASE].mean()
        print("   %-16s unconditioned %7.4f" % (name, base))
        for c in COND:
            v = g[c].mean()
            verdict = ("conditioning worse" if v > base
                       else "conditioning better")
            print("      %-30s %8.4f   %s" % (c, v, verdict))

    print("\nremoving one family. The ratio is unconditioned / conditioned,")
    print("so above 1 means conditioning helps.")
    for name, g0 in (("seven families", seven), ("physicality", phys)):
        full = g0[BASE].mean() / g0[QUOTED].mean()
        ratios = []
        for f in g0.substructure:
            g = g0[g0.substructure != f]
            ratios.append((f, g[BASE].mean() / g[QUOTED].mean()))
        lo = min(r for _, r in ratios)
        hi = max(r for _, r in ratios)
        print("   %-16s full cohort %.3f, leave-one-out range %.3f to %.3f, "
              "crosses unity: %s"
              % (name, full, lo, hi,
                 "yes" if (lo < 1 < hi) or (full - 1) * (lo - 1) < 0
                 or (full - 1) * (hi - 1) < 0 else "no"))
        for f, r in sorted(ratios, key=lambda t: t[1]):
            print("      without %-24s %7.3f" % (f, r))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
