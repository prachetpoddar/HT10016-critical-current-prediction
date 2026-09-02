#!/usr/bin/env python3
"""
calibration_domain_screen.py

Recomputes the calibration-domain screen of Sec. III.E from the deposit, and
reports what the screen does and does not pin down.

What the screen is. Before the candidate grid is built, each candidate record is
compared against a per-substructure floor on the transition-temperature anchor.
A record whose Tc falls below its family's floor is refused as outside the
calibration domain and never reaches the grid. Records that pass are graded into
two tiers, which is the 82 / 130 partition the supplement reports.

Where it lives. The screen operates one layer above the dispatch table. Its
output is the record-level table data/phase_3_p56_candidate_tier_assignment.csv,
which carries a tier for every record and, for every refused record, the
comparison that refused it in the form "Tc=1.50K < empirical_floor_5.0K". The
tuple-level table data/phase_3_p57_de_novo_predictions.csv carries the four
dispatch reason codes and no calibration code, which is not an omission: by the
time a record reaches the grid the screen has already run on it.

This is worth stating because an earlier version of the supplement said the
screen had no deposited implementation and that the 212 / 21 split was inferred
rather than recomputed. Both statements were wrong. The split recomputes here,
and it recomputes from the rule the table records rather than from the tier
labels, so the two can disagree and the script says so if they do.

What is genuinely missing, and is reported rather than papered over: the three
floors are recorded but not derived. Nothing in the workflow states how 4.5,
5.0 and 5.1 K were arrived at, and they do not reproduce from any per-family
statistic in the deposited tables. They equal the lowest retained Tc in each
family, which is consistent with the floor having been read off the retained set
rather than computed from the fitted cohort, and that is a circular derivation.
The screen's decisions are checkable; its thresholds are asserted.

    python analysis/calibration_domain_screen.py

Run from the repository root.
"""
import os
import re
import sys

import pandas as pd

TIERS = os.path.join("data", "phase_3_p56_candidate_tier_assignment.csv")
GRID = os.path.join("data", "phase_3_p57_de_novo_predictions.csv")
REFUSED = "refused_calibration_domain"

# The frozen counts the supplement quotes, after the withdrawals of Sec. III.F.
EXPECT = dict(records=233, retained=212, refused=21, high=82, graded=130)


def main():
    if not os.path.exists(TIERS):
        sys.exit("%s not present" % TIERS)
    d = pd.read_csv(TIERS)

    floors = {}
    for _i, r in d[d.tier == REFUSED].iterrows():
        m = re.search(r"empirical_floor_([\d.]+)K", str(r.refusal_detail))
        if m:
            floors.setdefault(r.substructure_family, set()).add(float(m.group(1)))

    print("calibration-domain screen, recomputed from %s\n" % TIERS)
    print("   per-family floor on the transition-temperature anchor\n")
    bad = []
    for fam in sorted(set(d.substructure_family)):
        f = sorted(floors.get(fam, []))
        if len(f) != 1:
            print("      %-24s no single floor recorded: %s" % (fam, f or "none"))
            bad.append("floor for %s" % fam)
            continue
        s = d[d.substructure_family == fam]
        below = s[s.Tc_K < f[0]]
        ref = s[s.tier == REFUSED]
        agree = set(below.index) == set(ref.index)
        print("      %-24s %5.2f K   %3d records, %2d below the floor, %2d refused   %s"
              % (fam, f[0], len(s), len(below), len(ref),
                 "consistent" if agree else "THE RULE AND THE LABELS DISAGREE"))
        if not agree:
            bad.append("rule vs label for %s" % fam)

    got = dict(records=len(d),
               retained=int((d.tier != REFUSED).sum()),
               refused=int((d.tier == REFUSED).sum()),
               high=int((d.tier == "high_confidence").sum()),
               graded=int((d.tier == "graded_confidence").sum()))
    print("\n   record accounting\n")
    for k in ("records", "retained", "refused", "high", "graded"):
        ok = got[k] == EXPECT[k]
        print("      %-10s deposit %3d, manuscript %3d   %s"
              % (k, got[k], EXPECT[k], "ok" if ok else "DIFFERS"))
        if not ok:
            bad.append(k)

    # The refused records still appear in the grid, refused there by whichever
    # dispatch gate fires on them. Saying so keeps a reader from concluding that
    # a missing calibration code in the grid means a missing screen.
    if os.path.exists(GRID):
        g = pd.read_csv(GRID)
        names = set(d[d.tier == REFUSED].compound)
        inn = g[g.compound_formula.isin(names)]
        print("\n   the %d refused records in the dispatch table\n" % len(names))
        print("      %d tuples, none emitted, carrying:" % len(inn))
        for code, n in inn.refusal_flag.fillna("(emitted)").value_counts().items():
            print("         %-34s %4d" % (code, n))
        if (inn.refusal_flag.fillna("") == "").any():
            print("      a refused record emitted a value; the screen did not hold")
            bad.append("refused record emitted")

    if bad:
        print("\nthe screen does not recompute: %s" % ", ".join(bad))
        return 1
    print("\nThe screen recomputes from the rule its own table records, and the "
          "split matches the manuscript. The three floors themselves are "
          "asserted, not derived; see the module docstring.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
