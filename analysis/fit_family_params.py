"""
fit_family_params.py

Regenerates data/family_params.json, the per-family Form 3 parameters that
analysis/manuscript_figure_5.py draws.

What was wrong with the previous version. It fitted the parameters to the
dispatch table's own predictions, that is, it read the predictor's output back
and recovered the exponents the predictor had used. That is circular, and it
stopped working: under the refusal gates of this revision only the MgB2 class
has a non-refused row, so the two other families have nothing to fit and the
module died with "expected non-empty vector for x". data/family_params.json was
therefore a frozen artifact from a cohort state that is not in the deposit, and
the old docstring's claim that reading the parameters from the dispatch table
is what let Figure 5 be checked against the withdrawals described a check that
could not be run.

What this version does instead. It builds each family's parameters from the
fitted cohorts directly, which is what the paper says the predictor does at
substructure-aggregate scope: the family median exponent on each axis, and the
family median partial anchor as the prefactor.

  beta_H, prefactor   the field-axis fits of that family that the protocol
                      admits, which is the 52-fit cohort of Sec. III.C. The
                      prefactor is log10 Jc,partial, the fitted intercept at
                      zero reduced field, which is the quantity the figure's
                      field panel plots against.
  beta_T              the repaired temperature exponent over that family's
                      fits in the 257-fit cohort. The MgB2 class carries none
                      of those, which Sec. III.C states, so its temperature
                      exponent comes from the separate per-paper cohort of 15
                      MgB2 fits that the same section describes.

The critical scales are each family's modal anchor pair, which is what the Fig.
5 caption says the grid uses, and which an independent check confirmed is the
mode of the candidate cohort rather than a hard-coded convenience.

The parameters this produces are not identical to the frozen ones, and the
differences are printed rather than smoothed over.

Run from the repository root.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

T_FITS = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits_repaired.csv")
MGB2_T = os.path.join("data", "h1b_per_paper_form3_fits.csv")
H_FITS = os.path.join("data",
                      "phase_3_form3_fits_partial_cohortB_v2_repaired.csv")
PROT = os.path.join("audit", "fit_protocol_applied.csv")
PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
OUT = os.path.join("data", "family_params.json")
FROZEN = OUT

# Each family's modal (Tc, Hc2) anchor pair, which the Fig. 5 caption names.
MODAL = {"conventional_AlB2": (38.0, 15.5),
         "iron_chalcogenide_11": (14.0, 47.0),
         "iron_pnictide_122": (22.0, 50.0)}
H0 = 0.1          # the field the temperature curve is drawn at
N_ADMITTED = 52   # the cohort Sec. III.C reports


def family_of(name, fallback):
    s = str(name)
    if s in fallback:
        return fallback[s]
    return "conventional_AlB2" if s.upper().startswith("MGB") else None


def load():
    h = pd.read_csv(H_FITS)
    prov = pd.read_csv(PROV)
    fb = dict(zip(prov.compound.astype(str),
                  prov.substructure_family.astype(str)))
    h["family"] = [family_of(c, fb) for c in h.compound_formula]
    # The admitted cohort, rebuilt from the deposited columns rather than
    # joined to audit/fit_protocol_applied.csv, whose paper and sample columns
    # carry specimen identifiers that do not key against this file. The
    # definition is the one Sec. III.C states plus the temperature clause the
    # response letter discloses, and it is asserted against the printed count.
    ttc = h.fixed_axis_value / h.Tc_repaired
    h["admitted"] = h.passing_repaired.fillna(False).astype(bool) & (ttc < 0.7)
    if int(h.admitted.sum()) != N_ADMITTED:
        raise SystemExit("the admitted cohort is %d fits, not the %d Sec. "
                         "III.C reports; the field cohort moved and these "
                         "parameters should be rebuilt deliberately"
                         % (int(h.admitted.sum()), N_ADMITTED))
    t = pd.read_csv(T_FITS)
    t = t[t.reproduced & np.isfinite(t.beta_T_repaired)]
    mg = pd.read_csv(MGB2_T)
    mg = mg[mg.compound.astype(str).str.contains("MgB2")
            & (mg.physical_beta_T == True)]
    return h, t, mg


def main():
    for p in (T_FITS, MGB2_T, H_FITS, PROT, PROV):
        if not os.path.exists(p):
            sys.exit("missing input: %s" % p)
    frozen = {}
    if os.path.exists(FROZEN):
        frozen = json.load(open(FROZEN))
    h, t, mg = load()
    print("family parameters, rebuilt from the fitted cohorts\n")
    out = {}
    for fam, (tc, hc) in MODAL.items():
        fh = h[(h.family == fam) & h.admitted]
        if len(fh) < 2:
            raise SystemExit("%s has %d admitted field fits; the family "
                             "median is not defined on fewer than two"
                             % (fam, len(fh)))
        beta_H = float(fh.beta.median())
        pref = float(fh.log_Jc_partial.median())
        ft = t[t.substructure.astype(str) == fam]
        if fam == "conventional_AlB2":
            if len(ft):
                raise SystemExit("the 257-fit cohort now carries %d MgB2 "
                                 "rows; this module takes the MgB2 "
                                 "temperature exponent from the separate "
                                 "per-paper cohort because it carried none"
                                 % len(ft))
            beta_T, n_T = float(mg.beta_T.median()), len(mg)
        else:
            beta_T, n_T = float(ft.beta_T_repaired.median()), len(ft)
        out[fam] = dict(Tc=tc, Hc2=hc, beta_H=beta_H, logJc_H=pref,
                        beta_T=beta_T,
                        logJc_T=pref + beta_H * float(np.log10(1 - H0 / hc)),
                        n_H=len(fh), n_T=n_T, H0=H0,
                        source=("family median over the admitted field fits "
                                "and the repaired temperature exponents"))
        f = frozen.get(fam, {})
        print("   %-22s Tc=%5.1f Hc2=%5.1f" % (fam, tc, hc))
        for k in ("beta_H", "logJc_H", "beta_T"):
            was = f.get(k)
            print("      %-9s %8.4f   frozen %s" %
                  (k, out[fam][k],
                   "%8.4f  (moves %+.4f)" % (was, out[fam][k] - was)
                   if isinstance(was, float) else "absent"))
        print("      %-9s %8d field fits, %d temperature fits"
              % ("cohort", len(fh), n_T))
    json.dump(out, open(OUT, "w"), indent=1)
    print("\n   wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
