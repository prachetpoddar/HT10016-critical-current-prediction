#!/usr/bin/env python3
"""Assert every number written into the manuscript redline against the deposit.

A redline is a list of assertions about files. Writing it from a previous
write-up rather than from the files is how a correction round propagates its own
errors, which has happened in this deposit before. Each number below is
recomputed here from the deposited CSVs and compared with what the redline says.

    python analysis/verify_redline_numbers.py

Exit status is non-zero if any number disagrees.
"""
import collections
import io
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figure_4_source import aggregate_per_physical_sample          # noqa: E402
import compound_leave_one_out as clo                               # noqa: E402

DATA = "data"
THREE = ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]
fails = []


REDLINE = os.path.join("audit", "manuscript_redline_20260903.md")
_redline_rows = None
drift = []

# The four Table I rows this script also reads out of the redline itself, by
# row name, so the two cannot disagree. Everything else here is asserted
# against the deposit only.
#
# A weaker version of this check was tried first and thrown away: it asked
# whether the expected value appeared ANYWHERE in the document. That passes on
# almost any small integer in a file this long, and it did pass when the value
# in Table I was changed back to its superseded one, because the number still
# appeared in a sentence explaining the change. A check that cannot fail is
# worse than no check, so this one reads the specific table cell.
TABLE_I = {
    "papers contributing fitted curves": "Papers contributing fitted curves",
    "distinct compounds with fitted curves": "Distinct compounds with fitted curves",
    "critical-current data points extracted": "Critical-current data points extracted",
    "temperature-axis partial fits": "Temperature-axis partial fits",
    "field-axis partial fits passing physicality":
        "Field-axis partial fits passing physicality",
    "per-paper anchors behind Fig. 3": "Per-paper anchors behind Fig. 3",
    "candidate compounds evaluated": "Candidate compounds evaluated",
}


def _table_i():
    """The 'to' column of the redline's Table I, by row name.

    Rows look like: | Papers contributing fitted curves | 69 | **62** | src |
    """
    global _redline_rows
    if _redline_rows is None:
        _redline_rows = {}
        if os.path.exists(REDLINE):
            for line in io.open(REDLINE, encoding="utf-8"):
                m = re.match(r"\|\s*([^|]+?)\s*\|\s*[\d.]+\s*\|\s*\*\*([\d.]+)\*\*\s*\|",
                             line)
                if m:
                    _redline_rows[m.group(1)] = m.group(2)
    return _redline_rows


def check(label, got, want):
    """Assert the deposit against the value the redline states.

    `want` is a copy of what the redline says, and a copy drifts: six of these
    were correct when written and were superseded by a withdrawal and a
    classifier fix while the redline still carried the old ones. For the rows
    the redline states in a table, the table is read and compared, so the two
    have to move together.
    """
    ok = got == want
    print("   %-52s %-10s %s" % (label, got, "ok" if ok else "REDLINE SAYS %s" % (want,)))
    if not ok:
        fails.append(label)
    name = TABLE_I.get(label)
    if name:
        stated = _table_i().get(name)
        if stated is None:
            drift.append("%s: no such row in the redline's Table I" % name)
        elif stated != str(want):
            drift.append("%s: this script expects %s, the redline's Table I "
                         "says %s" % (name, want, stated))


def main():
    prov = pd.read_csv(os.path.join(DATA, "provenance_table_fitcohort_full.csv"))
    bt = pd.read_csv(os.path.join(DATA, "phase_3_p44_post_UCLA_beta_T_fits.csv"))
    fh = pd.read_csv(os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv"))
    a = pd.read_csv(os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv"))
    tiers = pd.read_csv(os.path.join(DATA, "phase_3_p56_candidate_tier_assignment.csv"))
    h1b = pd.read_csv(os.path.join(DATA, "h1b_per_paper_form3_fits.csv"))

    print("Table I")
    check("papers contributing fitted curves", len(prov), 62)
    check("distinct compounds with fitted curves", prov.compound.nunique(), 38)
    check("critical-current data points extracted",
          int(pd.to_numeric(prov.n_Jc_points, errors="coerce").sum()), 4146)
    check("temperature-axis partial fits", len(bt), 260)
    ok = fh[(fh.ok.astype(str) == "True") & (fh.physicality == "ok")]
    check("field-axis partial fits passing physicality", len(ok), 94)
    check("field-axis source papers", ok.arxiv_id.nunique(), 16)
    check("per-paper anchors behind Fig. 3", len(a), 96)
    check("candidate compounds evaluated", tiers.compound_formula.nunique()
          if "compound_formula" in tiers else tiers.iloc[:, 0].nunique(), 183)

    print("\nSec. II.A source composition")
    papers = sorted(bt.paper_id.unique())
    arxiv = [p for p in papers if not p.startswith(("elsevier_", "springer_", "iop_"))]
    check("temperature-axis source papers", len(papers), 20)
    check("of which arXiv preprints", len(arxiv), 18)

    print("\nFig. 3 caption")
    sel = a[a.substructure.isin(THREE)]
    check("anchor records in the three plotted families", len(sel), 56)
    agg = aggregate_per_physical_sample(a)
    check("markers drawn (physical samples in those families)",
          int(agg.substructure.isin(THREE).sum()), 37)

    print("\nSec. III.C, temperature axis")
    for fam, want_c, want_n in (("iron_chalcogenide_11", 5, 89),
                                ("iron_pnictide_122", 2, 106),
                                ("iron_pnictide_1111", 3, 54)):
        s = bt[bt.substructure == fam]
        check("%s compounds" % fam, s.compound_formula.nunique(), want_c)
        check("%s fits" % fam, len(s), want_n)
    c122 = bt[bt.substructure == "iron_pnictide_122"].compound_formula.value_counts()
    check("Ba(FeAs)2 fits", int(c122.get("Ba(FeAs)2", 0)), 85)
    check("K(FeAs)2 fits", int(c122.get("K(FeAs)2", 0)), 21)

    print("\nSec. III.C, the MgB2 temperature cohort")
    mg = h1b[h1b.compound == "MgB2"]
    phys = mg[mg.physical_beta_T.astype(str).str.lower().isin(("true", "1", "yes"))]
    check("physical MgB2 fits", len(phys), 15)
    check("median beta_T, to two decimals", round(float(phys.beta_T.median()), 2), 1.14)
    check("distinct source labels in the deposit", mg.source.nunique(), 2)

    print("\nSec. III.C, field axis, leave-one-compound-out")
    _bt, f = clo.load(DATA)
    for fam, want_cond, want_med in (("conventional_AlB2", 0.753, 0.751),
                                     ("iron_pnictide_122", 0.973, 0.929),
                                     ("iron_chalcogenide_11", 1.093, 1.094),
                                     ("iron_pnictide_1111", 2.571, 2.622)):
        s = f[f.substructure == fam]
        cond = round(clo.loo(s, "beta", True)[0], 3)
        med = round(clo.loo(s, "beta", False)[0], 3)
        check("%s, sample-form conditioned" % fam, cond, want_cond)
        check("%s, substructure median" % fam, med, want_med)

    print()
    if drift:
        print("%d row(s) where this script and %s disagree:"
              % (len(drift), REDLINE))
        for u in drift:
            print("   " + u)
        print()
    if fails or drift:
        if fails:
            print("%d number(s) in the redline do not match the deposit:"
                  % len(fails))
            for f_ in fails:
                print("   " + f_)
        return 1
    print("every number in the redline reproduces from the deposit, and its "
          "Table I agrees with this script row by row")
    return 0


if __name__ == "__main__":
    sys.exit(main())
