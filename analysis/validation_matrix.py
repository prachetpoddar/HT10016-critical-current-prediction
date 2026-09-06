"""
validation_matrix.py

One family-by-axis validation status, computed from the final cohorts.

Why. The documents carry incompatible validation statements. The manuscript
says "three validated substructure families" in three places and "not validated
at family level" in three others; Table IV labels the 11-type family
"Temperature and field" while Sec. III.C reports no family-level field verdict;
and the response letter says the framework declines to predict outside its
validated scope while the emitted outputs use the field term. This module
computes the status once, per family and per axis, so the documents can be made
to agree with one thing rather than with each other.

It also settles which cohort each printed number came from, which turned out to
be the harder half. analysis/compound_leave_one_out.py, the script both
documents name, reads the UNREPAIRED fit tables and the 94-fit field cohort. It
therefore reproduces the "cohort as published" values, 0.588, 1.314 and 3.120
on the temperature axis, and not the repaired values the manuscript prints.
This module runs the same estimator on the final cohorts and reports whether
the printed repaired values reproduce.

The estimator is imported from compound_leave_one_out rather than rewritten, so
the matrix is the paper's own statistic on the paper's own final data.

  temperature axis  the 257-fit repaired cohort, substructure-median predictor
  field axis        the 52 fits the protocol admits, sample-form-conditioned,
                    which is the predictor Sec. III.C describes
  separation        eta squared with source papers as the unit and the family
                    label permuted between them, per axis

Run from the repository root.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import headline_on_repaired_cohort as H                            # noqa: E402
from compound_leave_one_out import loo                             # noqa: E402

T_FITS = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits_repaired.csv")
H_FITS = os.path.join("data",
                      "phase_3_form3_fits_partial_cohortB_v2_repaired.csv")
PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
OUT = os.path.join("audit", "retrace_20260906", "validation_matrix.csv")

THRESHOLD = 1.0
N_ADMITTED = 52
N_TEMPERATURE = 257
# What the documents print for each axis, so a disagreement is named here.
PRINTED_T = {"iron_chalcogenide_11": 0.546, "iron_pnictide_122": 0.580,
             "iron_pnictide_1111": 0.513}
# The field-axis values are computed on beta_repaired, not beta. Three of the
# four printed values reproduce on that column and only one does on the
# other, which is how the column was identified: on beta the MgB2-class error
# is 0.704 and clears the threshold, on beta_repaired it is 1.230 and does
# not, and that is the verdict for the only family the framework dispatches.
H_COL = "beta_repaired"
PRINTED_H = {"conventional_AlB2": 1.230, "iron_pnictide_122": 1.957,
             "iron_chalcogenide_11": 0.707, "iron_pnictide_1111": 3.327}


def family_of(name, fallback):
    s = str(name)
    return fallback.get(s) or ("conventional_AlB2"
                               if s.upper().startswith("MGB") else None)


def cohorts():
    prov = pd.read_csv(PROV)
    fb = dict(zip(prov.compound.astype(str),
                  prov.substructure_family.astype(str)))

    t = pd.read_csv(T_FITS)
    t = t[t.reproduced & np.isfinite(t.beta_T_repaired)].copy()
    if len(t) != N_TEMPERATURE:
        raise SystemExit("the temperature cohort is %d fits, not the %d "
                         "Table I prints" % (len(t), N_TEMPERATURE))
    t = t.rename(columns={"beta_T_repaired": "beta",
                          "substructure": "family"})

    h = pd.read_csv(H_FITS).copy()
    h["family"] = [family_of(c, fb) for c in h.compound_formula]
    adm = (h.passing_repaired.fillna(False).astype(bool)
           & ((h.fixed_axis_value / h.Tc_repaired) < 0.7))
    h = h[adm]
    if len(h) != N_ADMITTED:
        raise SystemExit("the admitted field cohort is %d fits, not the %d "
                         "Sec. III.C prints" % (len(h), N_ADMITTED))
    if h.family.isna().any():
        raise SystemExit("field fits with no family: %s"
                         % sorted(set(h.compound_formula[h.family.isna()])))
    return t, h


def separation(s, col):
    tab = s.groupby(["paper", "family"])[col].median().reset_index()
    tab = tab.rename(columns={col: "beta"})
    counts = tab.groupby("family").paper.nunique()
    tab = tab[tab.family.isin(counts[counts >= H.MIN_PAPERS_PER_FAMILY].index)]
    if tab.family.nunique() < 2:
        return None, None
    p, eta = H.permutation_p(tab)
    return eta, p


def main():
    t, h = cohorts()
    t = t.assign(paper=t.paper_key.astype(str))
    # The repaired field file carries its own sample_form. An earlier version
    # of this module overwrote it with a constant, which turns the
    # form-conditioned predictor into the plain family median and moved the
    # MgB2-class error from 1.230 to 0.699, reversing that family's verdict.
    if "sample_form" not in h.columns:
        raise SystemExit("the field cohort has no sample_form column; the "
                         "form-conditioned predictor Sec. III.C describes "
                         "cannot be reproduced without it")
    h = h.assign(paper=h.paper_key.astype(str))
    print("one validation status per family and axis, from the final "
          "cohorts\n")

    eta_t, p_t = separation(t, "beta")
    eta_h, p_h = separation(h, "beta")
    print("   separation, source papers as the unit")
    print("      temperature axis  eta squared %.3f, permutation p %.4f"
          % (eta_t, p_t))
    print("      field axis        eta squared %.3f, permutation p %.4f"
          % (eta_h, p_h))
    print()

    rows = []
    print("   %-24s %-12s %5s %5s %9s %9s  %s"
          % ("family", "axis", "cmpd", "fits", "error", "printed", "status"))
    fams = sorted(set(t.family) | set(h.family))
    for fam in fams:
        for axis, frame, col, cond, printed in (
                ("temperature", t, "beta", False, PRINTED_T),
                ("field", h, H_COL, True, PRINTED_H)):
            g = frame[(frame.family == fam) & np.isfinite(frame[col])]
            if g.empty:
                print("   %-24s %-12s %5s %5s %9s %9s  not assessable, no "
                      "fits in this cohort" % (fam, axis, "-", "-", "-", "-"))
                rows.append(dict(family=fam, axis=axis, compounds=0, fits=0,
                                 error=np.nan, printed=printed.get(fam),
                                 status="not assessable"))
                continue
            n_c = g.compound_formula.nunique() if "compound_formula" in g \
                else g.compound.nunique()
            if "compound_formula" not in g:
                g = g.assign(compound_formula=g.compound)
            if n_c < 2:
                status = "not assessable, one compound"
                mae = np.nan
            else:
                mae, _med, _f, _r = loo(g, col, form_conditioned=cond)
                status = ("clears the threshold" if mae < THRESHOLD
                          else "does not clear the threshold")
            want = printed.get(fam)
            print("   %-24s %-12s %5d %5d %9s %9s  %s"
                  % (fam, axis, n_c, len(g),
                     "%.3f" % mae if np.isfinite(mae) else "-",
                     "%.3f" % want if want else "-", status))
            rows.append(dict(family=fam, axis=axis, compounds=n_c, fits=len(g),
                             error=mae, printed=want, status=status))

    bad = [r for r in rows if r["printed"] is not None
           and np.isfinite(r.get("error", np.nan))
           and abs(r["error"] - r["printed"]) > 5e-4]
    print()
    quoted = [r for r in rows if r["printed"] is not None]
    if bad:
        print("   the printed value does not reproduce for %d of the %d cells "
              "the documents quote:" % (len(bad), len(quoted)))
        for r in bad:
            print("      %-24s %-12s computed %.3f, printed %.3f"
                  % (r["family"], r["axis"], r["error"], r["printed"]))
    else:
        print("   every printed value reproduces")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("\n   wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
