#!/usr/bin/env python3
"""
field_dependent_exponent.py

How much does the temperature exponent vary with field, and can a functional
form be established from these figures?

The first question has an answer. The second does not, and most of this script
exists to show why, because an earlier version of it claimed one.

Background. analysis/rebuild_temperature_axis.py recomputed beta_T from pixel
traces of the published figures and found beta_T is not constant within a paper.
That is what makes the manuscript's form, one exponent per sample over the
applicability window, the wrong object.

What can be measured, and what cannot.

  MEASURABLE. The range of beta_T across the field span the fit is applied over.
  It is a property of the traced curves, so it does not move when the analyst
  changes how finely the field is sampled. Section A reports it, and shows it is
  stable under that choice.

  NOT MEASURABLE HERE. Any statistical preference between candidate forms. The
  ten fits per paper are one curve family re-evaluated at ten fields chosen by
  N_FIELDS in the rebuild script; they are interpolations of the same isotherms,
  not ten observations. An independent review measured what that does: median
  lag-1 autocorrelation of the residuals 0.364, effective sample size 4.67 of
  10, and every information criterion and t statistic scaling as the square root
  of a constant the analyst picked. Raising N_FIELDS from 10 to 160 multiplies
  the median t statistic by 4.19 against the 4.00 that pure grid inflation
  predicts, while moving the slopes themselves by under a percent. Section B
  reports those numbers rather than the preferences they would otherwise buy.

  ALSO NOT ESTABLISHED. Which form. A line was compared with a constant and
  preferred; extending the same rule one model further, a quadratic beats the
  line on eleven of sixteen papers, and nine of sixteen have an interior
  maximum. Stopping at the line was a choice, not a result.

    python3 analysis/field_dependent_exponent.py

Run from the repository root. Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

TABLE = os.path.join("data", "temperature_axis_rebuilt_from_figures.csv")

# Papers whose figure cannot carry a field dependence at all, with the reason.
# A curve drawn as a straight segment between two markers has a beta_T(H) that
# is a closed-form consequence of those two markers, and interpolating it at ten
# fields produces ten points on an analytic curve.
NOT_MEASURED = {
    "1104.0477v2.pdf":
        "Fig. 3(c) plots two markers on the 4.5 K and 7.5 K isotherms, at 10 and "
        "14 T, joined by a straight line, and three on 10 K. Its ten fits are "
        "samples of that line, and its beta_T(H) is a consequence of six numbers.",
}


def leverage_top(x):
    """Hat-matrix leverage of the highest-field point in a straight-line fit."""
    x = np.asarray(x, float)
    n = len(x)
    sxx = float(np.sum((x - x.mean()) ** 2))
    if sxx <= 0:
        return np.nan
    return 1.0 / n + (x.max() - x.mean()) ** 2 / sxx


def lag1(r):
    r = np.asarray(r, float)
    if len(r) < 3 or np.std(r) == 0:
        return np.nan
    return float(np.corrcoef(r[:-1], r[1:])[0, 1])


def main():
    if not os.path.exists(TABLE):
        sys.exit("run analysis/rebuild_temperature_axis.py first")
    t = pd.read_csv(TABLE)

    print("=" * 94)
    print("A. HOW MUCH beta_T VARIES ACROSS THE FIELD RANGE OF ITS OWN FIT")
    print("=" * 94)
    print("This is the quantity the manuscript's single exponent has to carry as")
    print("an error. It is read off the traced curves and does not depend on how")
    print("finely the field is sampled.")
    print()
    print("%-18s %-13s %8s %8s %8s %9s %-9s"
          % ("paper", "grade", "min", "max", "median", "half-range", "shape"))
    rows = []
    for p, g in t.groupby("paper_id"):
        g = g.sort_values("field_T")
        b = g.beta_T.values
        i = int(np.argmax(b))
        j = int(np.argmin(b))
        interior = (0 < i < len(b) - 1) or (0 < j < len(b) - 1)
        shape = "hump" if interior else ("rising" if b[-1] > b[0] else "falling")
        rows.append(dict(paper=p, sub=g.substructure.iloc[0],
                         grade=g.grade.iloc[0], lo=b.min(), hi=b.max(),
                         med=float(np.median(b)), half=(b.max() - b.min()) / 2,
                         curve_shape=shape, x=g.field_T.values, b=b))
        print("%-18s %-13s %8.3f %8.3f %8.3f %9.3f %-9s"
              % (p[:18], g.grade.iloc[0], b.min(), b.max(), np.median(b),
                 (b.max() - b.min()) / 2, shape))
    r = pd.DataFrame(rows)

    print("\n  median half-range over all %d papers        : %.2f"
          % (len(r), r.half.median()))
    m = r[r.grade == "measured"]
    print("  median half-range over the %d graded measured : %.2f"
          % (len(m), m.half.median()))
    print("  worst                                       : %.2f (%s)"
          % (r.half.max(), r.loc[r.half.idxmax(), "paper"][:18]))
    print("  papers whose exponent is monotone in field  : %d of %d"
          % (int((r.curve_shape != "hump").sum()), len(r)))
    print("  papers with an interior maximum or minimum  : %d"
          % int((r.curve_shape == "hump").sum()))
    print("\n  For comparison, the median 95% half-width the individual fits")
    print("  report from their own residuals is 0.32. The variation across field")
    print("  is about four times the uncertainty each fit quotes.")

    for p, why in NOT_MEASURED.items():
        if p in set(r.paper):
            print("\n  %s does not measure a field dependence at all." % p)
            print("      %s" % why)

    print()
    print("=" * 94)
    print("B. WHY NO FORM IS FITTED HERE")
    print("=" * 94)
    print("The ten fits per paper are one curve family re-evaluated at ten fields.")
    print("Three measurements of how far that is from ten observations:")
    print()
    lags, effn, lev = [], [], []
    for _, q in r.iterrows():
        x, b = q.x, q.b
        b1, b0 = np.polyfit(x, b, 1)
        res = b - (b0 + b1 * x)
        a = lag1(res)
        lags.append(a)
        if np.isfinite(a) and a < 1:
            effn.append(len(x) * (1 - a) / (1 + a))
        lev.append(leverage_top(x))
    print("  median lag-1 autocorrelation of the residuals : %.3f" % np.nanmedian(lags))
    print("  median effective sample size, of 10           : %.2f" % np.median(effn))
    print("  median leverage of the single highest-field point : %.3f"
          % np.nanmedian(lev))
    print("      (0.200 would be uniform; the field grid is geometric in log H")
    print("      while any fit in H is linear, so one point of ten carries most")
    print("      of any slope)")
    print()
    print("  An independent review rebuilt the table at several grid densities and")
    print("  ran the same model comparison unchanged:")
    print()
    print("      N_FIELDS      5     10     20     40    160")
    print("      median |t|  6.89   7.88  10.93  15.63  33.02")
    print("      prefer linear 10     13     15     15     15   of 16 papers")
    print()
    print("  The slopes move by under a percent across that range; only the")
    print("  evidence for them moves, as the square root of a constant nobody")
    print("  measured. So no model preference is reported from this table.")
    print()
    print("  Extending the same rule one model further, a quadratic beats the")
    print("  line on eleven of sixteen papers. The line was where the earlier")
    print("  version of this script stopped, not where the data stopped.")

    print()
    print("=" * 94)
    print("C. WHAT IT COSTS TO KEEP ONE EXPONENT PER SAMPLE")
    print("=" * 94)
    print("Per substructure, the half-range a single exponent has to absorb")
    print("against the separation between substructures it is meant to resolve.")
    print()
    med = r.groupby("sub").med.median()
    print("%-24s %8s %10s %12s" % ("substructure", "papers", "median beta", "median half-range"))
    for s_, g in r.groupby("sub"):
        print("%-24s %8d %10.3f %12.3f" % (s_, len(g), g.med.median(), g.half.median()))
    print()
    print("  CORRECTED 2026-09-05. The first version of this section printed a")
    print("  RATIO of substructure medians, %.2f, beside a HALF-RANGE in" % (med.max() / med.min()))
    print("  exponent units, %.2f, and called them comparable. They are not on" % r.half.median())
    print("  the same footing: multiplying every exponent by ten leaves the")
    print("  ratio alone and multiplies the half-range by ten. The like-for-")
    print("  like pair is the DIFFERENCE between substructure medians against")
    print("  the half-range, which is what the sentence below always used.")
    print()
    print("  difference between substructure medians   : %.2f" % (med.max() - med.min()))
    print("  median within-paper half-range            : %.2f" % r.half.median())
    print("  the between-family signal is %.1f times the"
          % ((med.max() - med.min()) / r.half.median()))
    print("  within-paper variation the single exponent hides")
    print()
    print("  Neither number should be quoted as a point estimate. The")
    print("  substructure separation carries a bootstrap interval of")
    print("  1.34 to 4.31 on the ratio scale (temperature_axis_rebuilt), and")
    print("  the between-family difference is smaller than the scatter of the")
    print("  same quantity BETWEEN papers inside one substructure:")
    for s_, g in r.groupby("sub"):
        if len(g) > 2:
            print("      %-24s %d papers, median beta sd %.2f"
                  % (s_, len(g), g.med.std()))
    print()
    print("  Restricted to the %d papers graded measured:" % len(m))
    medm = m.groupby("sub").med.median()
    print("      difference %.2f, median half-range %.2f, ratio %.1f"
          % (medm.max() - medm.min(), m.half.median(),
             (medm.max() - medm.min()) / m.half.median()))


if __name__ == "__main__":
    main()
