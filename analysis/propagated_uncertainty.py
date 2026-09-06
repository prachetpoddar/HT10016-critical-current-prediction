"""
propagated_uncertainty.py

The substructure-aggregate quadrature, recomputed from the deposit.

Three things were wrong with it.

**The temperature-exponent scatter does not reproduce, and it is the pre-repair
one.** Sec. III.E gives the three inputs as 0.265 in log10 Jc,partial, 1.158 in
beta_T and 0.920 in beta_H "within the iron pnictide 122-type scope", and the
supplement names the cohorts: 36 field-axis fits passing physicality and 106
temperature-axis fits. Two of the three reproduce to four digits. The third
does not: over those 106 fits the deposit gives 1.1712 on the exponent as
deposited and 0.5629 on the repaired exponent, which is the one the rest of the
paper uses. No mask, estimator or cohort variant returns 1.158. That value does
appear in the deposit, two paragraphs later in the same supplement section, as
the pooled unconditioned per-paper field-axis validation error over 94 fits.
The collision is worth stating; the attribution is inference and is not
asserted here.

**The correlation caveat points the wrong way.** Both documents say that where
the terms are positively correlated the independent quadrature understates the
aggregate, so 0.29 dex should be read as a lower bound. That is true for one of
the three pairs and false for the other two, and the two dominate. Writing
log10 Jc = A + beta_T * dT + beta_H * dH with dT = log10(1 - T/Tc) and
dH = log10(1 - H/Hc2), the partial derivative with respect to the anchor is +1
while both dT and dH are negative. So the anchor-to-exponent cross terms carry
a negative coefficient and the exponent-to-exponent cross term a positive one.
The script evaluates all three rather than arguing about them, and a uniform
positive correlation lowers the propagated uncertainty at every grid point,
which makes the quoted figure an upper bound on the structural component under
that assumption rather than a lower one.

**The scope is the family that dispatches nothing.** The 122-type scope emits
no prediction under the refusal gates of this revision, which the paper states
three times, so the quadrature is reported for a scope that never uses it. The
same propagation on the MgB2 class, the only family that dispatches, is
computed here beside it.

Run from the repository root.
"""
import os
import sys

import numpy as np
import pandas as pd

T_FITS = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits_repaired.csv")
H_FITS = os.path.join("data",
                      "phase_3_form3_fits_partial_cohortB_v2_repaired.csv")
PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
# The 257-fit temperature cohort carries no MgB2-class row, which Sec. III.C
# states. The MgB2 temperature exponents are the separate per-paper Form 3
# cohort of fifteen fits that Sec. III.C also describes, so the MgB2
# propagation is built across two cohorts and is reported as such.
MGB2_T_FITS = os.path.join("data", "h1b_per_paper_form3_fits.csv")
OUT = os.path.join("audit", "retrace_20260906", "propagated_uncertainty.csv")

# What Sec. III.E prints, and the supplement's own evaluation point.
PRINTED = dict(sd_anchor=0.265, sd_beta_T=1.158, sd_beta_H=0.920)
PRINTED_QUAD = {0.1: 0.285, 1.0: 0.286, 5.0: 0.289}
ANCHOR = {"iron_pnictide_122": (22.0, 50.0), "conventional_AlB2": (38.0, 15.5)}
T_EVAL = {"iron_pnictide_122": (4.2,), "conventional_AlB2": (4.2, 20.0)}
GRID = (0.1, 1.0, 5.0)


def family_of(name, fallback):
    """Map a compound label onto a substructure family.

    The provenance table misses the doped MgB2 variants, which are written as
    MgB2_SiC_doped and similar and are the bulk of the AlB2 field cohort. An
    earlier count of 15 rather than 20 was that gap, not a cohort choice.
    """
    s = str(name)
    if s in fallback:
        return fallback[s]
    if s.upper().startswith("MGB"):
        return "conventional_AlB2"
    return None


def inputs():
    t = pd.read_csv(T_FITS)
    h = pd.read_csv(H_FITS)
    prov = pd.read_csv(PROV)
    fb = dict(zip(prov.compound.astype(str),
                  prov.substructure_family.astype(str)))
    h["family"] = [family_of(c, fb) for c in h.compound_formula]
    unmapped = sorted(set(h.compound_formula[h.family.isna()].astype(str)))
    ok = h[h.physicality == "ok"]
    out = {}
    mg = pd.read_csv(MGB2_T_FITS)
    mg = mg[mg.compound.astype(str).str.contains("MgB2")
            & (mg.physical_beta_T == True)]
    for fam in ANCHOR:
        ft = t[t.substructure.astype(str) == fam]
        if fam == "conventional_AlB2":
            if len(ft):
                raise SystemExit("the 257-fit cohort now carries %d MgB2 rows;"
                                 " this module takes the MgB2 temperature "
                                 "exponents from a separate file because it "
                                 "carried none" % len(ft))
            ft = mg.rename(columns={"beta_T": "beta_T",
                                    "beta_T": "beta_T"}).assign(
                beta_T_repaired=np.nan)
        fh = ok[ok.family == fam]
        out[fam] = dict(
            n_T=len(ft), n_H=len(fh),
            sd_anchor=float(fh.log_Jc_partial.std(ddof=1)),
            sd_beta_H=float(fh.beta.std(ddof=1)),
            sd_beta_T_deposited=float(ft.beta_T.std(ddof=1)),
            sd_beta_T_repaired=float(
                ft.beta_T_repaired.replace([np.inf, -np.inf],
                                           np.nan).dropna().std(ddof=1)))
    return out, unmapped


def quad(sd_a, sd_t, sd_h, Tc, Hc2, T, H, rho=0.0):
    """One-sigma propagated uncertainty in log10 Jc.

    rho is applied uniformly to all three pairs. The three cross-term
    coefficients are returned so the sign argument is arithmetic rather than
    prose: the two anchor-to-exponent products are negative and the
    exponent-to-exponent product is positive.
    """
    dT = np.log10(max(1.0 - T / Tc, 1e-12))
    dH = np.log10(max(1.0 - H / Hc2, 1e-12))
    b, c = dT * sd_t, dH * sd_h
    var = sd_a ** 2 + b ** 2 + c ** 2
    cross = 2.0 * (sd_a * b + sd_a * c + b * c)
    return float(np.sqrt(max(var + rho * cross, 0.0))), \
        dict(anchor_T=2 * sd_a * b, anchor_H=2 * sd_a * c, T_H=2 * b * c,
             total=cross)


def main():
    for p in (T_FITS, H_FITS, PROV):
        if not os.path.exists(p):
            sys.exit("missing input: %s" % p)
    v, unmapped = inputs()
    print("the substructure-aggregate quadrature, recomputed\n")
    if unmapped:
        print("   compounds with no family after the fallback: %s"
              % ", ".join(unmapped))

    p122 = v["iron_pnictide_122"]
    print("\n   the three inputs Sec. III.E prints, against the deposit")
    print("   %-26s %8s %10s" % ("", "printed", "deposit"))
    print("   %-26s %8.3f %10.4f   (%d field fits)"
          % ("sd log10 Jc,partial", PRINTED["sd_anchor"], p122["sd_anchor"],
             p122["n_H"]))
    print("   %-26s %8.3f %10.4f   (%d field fits)"
          % ("sd beta_H", PRINTED["sd_beta_H"], p122["sd_beta_H"],
             p122["n_H"]))
    print("   %-26s %8.3f %10.4f   (%d temperature fits, exponent as "
          "deposited)" % ("sd beta_T", PRINTED["sd_beta_T"],
                          p122["sd_beta_T_deposited"], p122["n_T"]))
    print("   %-26s %8s %10.4f   (the repaired exponent, which the rest of "
          "the paper uses)" % ("", "", p122["sd_beta_T_repaired"]))

    for name, got in (("sd log10 Jc,partial", p122["sd_anchor"]),
                      ("sd beta_H", p122["sd_beta_H"])):
        want = PRINTED["sd_anchor"] if "partial" in name \
            else PRINTED["sd_beta_H"]
        if abs(got - want) > 5e-4:
            raise SystemExit("%s does not reproduce: %.4f against the printed "
                             "%.3f. Two of the three inputs reproducing is "
                             "what identifies the intended cohort, so this "
                             "check has to pass before the third means "
                             "anything." % (name, got, want))
    if abs(p122["sd_beta_T_deposited"] - PRINTED["sd_beta_T"]) < 5e-4:
        raise SystemExit("sd beta_T now reproduces at %.4f; this module was "
                         "written because it did not, and its conclusion "
                         "should be revisited"
                         % p122["sd_beta_T_deposited"])

    Tc, Hc2 = ANCHOR["iron_pnictide_122"]
    print("\n   the quadrature on the 122-type scope at 4.2 K, which "
          "dispatches nothing")
    print("   %-34s %8s %8s %8s" % ("inputs", "0.1 T", "1 T", "5 T"))
    rows = []
    for label, sdt in (("as printed (sd beta_T 1.158)", PRINTED["sd_beta_T"]),
                       ("deposit, exponent as deposited",
                        p122["sd_beta_T_deposited"]),
                       ("deposit, repaired exponent",
                        p122["sd_beta_T_repaired"])):
        sd_a = PRINTED["sd_anchor"] if label.startswith("as printed") \
            else p122["sd_anchor"]
        sd_h = PRINTED["sd_beta_H"] if label.startswith("as printed") \
            else p122["sd_beta_H"]
        vals = [quad(sd_a, sdt, sd_h, Tc, Hc2, 4.2, H)[0] for H in GRID]
        print("   %-34s %8.4f %8.4f %8.4f" % ((label,) + tuple(vals)))
        rows.append(dict(scope="iron_pnictide_122", inputs=label, T=4.2,
                         **{"H_%g" % H: x for H, x in zip(GRID, vals)}))
    # The supplement prints three decimals, so the bar is one unit in its
    # last digit. The achieved worst case is printed rather than hidden
    # behind the bar: at 0.1 T the recomputation gives 0.2856, which rounds
    # to 0.286 and is printed as 0.285. That is the supplement rounding down,
    # and it is inside a digit the paper's own rounding rule says is not
    # supported by a cohort of this size.
    printed_now = rows[0]
    worst = max(abs(printed_now["H_%g" % H] - PRINTED_QUAD[H]) for H in GRID)
    if worst > 1e-3:
        raise SystemExit("the printed inputs no longer give the printed "
                         "quadrature; worst disagreement %.4f over %s"
                         % (worst, ", ".join("%g T" % H for H in GRID)))
    print("   the printed inputs reproduce the printed 0.285 / 0.286 / 0.289, "
          "worst disagreement %.4f" % worst)

    pmg = v["conventional_AlB2"]
    Tc, Hc2 = ANCHOR["conventional_AlB2"]
    print("\n   the same propagation on the MgB2 class, which is the only "
          "family that dispatches")
    print("   inputs from the deposit: sd anchor %.4f, sd beta_H %.4f over %d "
          "field fits; sd beta_T %.4f over %d temperature fits"
          % (pmg["sd_anchor"], pmg["sd_beta_H"], pmg["n_H"],
             pmg["sd_beta_T_deposited"], pmg["n_T"]))
    for T in T_EVAL["conventional_AlB2"]:
        vals = [quad(pmg["sd_anchor"], pmg["sd_beta_T_deposited"],
                     pmg["sd_beta_H"], Tc, Hc2, T, H)[0] for H in GRID]
        print("   at %4.1f K %25s %8.4f %8.4f %8.4f" % ((T, "") + tuple(vals)))
        rows.append(dict(scope="conventional_AlB2", inputs="deposit", T=T,
                         **{"H_%g" % H: x for H, x in zip(GRID, vals)}))

    print("\n   the sign of the correlation correction, on the printed inputs "
          "at 5 T")
    _, k = quad(PRINTED["sd_anchor"], PRINTED["sd_beta_T"],
                PRINTED["sd_beta_H"], *ANCHOR["iron_pnictide_122"], 4.2, 5.0)
    print("   %-38s %+.6f" % ("anchor with beta_T", k["anchor_T"]))
    print("   %-38s %+.6f" % ("anchor with beta_H", k["anchor_H"]))
    print("   %-38s %+.6f" % ("beta_T with beta_H", k["T_H"]))
    print("   %-38s %+.6f" % ("sum", k["total"]))
    if k["total"] >= 0:
        raise SystemExit("the cross terms now sum positive, so a uniform "
                         "positive correlation would raise the propagated "
                         "uncertainty and the documents' caveat would be "
                         "right as written")
    print("   the sum is negative, so a uniform positive correlation lowers "
          "the propagated uncertainty:")
    for rho in (0.0, 0.2, 0.4, 0.8):
        s, _ = quad(PRINTED["sd_anchor"], PRINTED["sd_beta_T"],
                    PRINTED["sd_beta_H"], *ANCHOR["iron_pnictide_122"],
                    4.2, 5.0, rho)
        print("      rho %.1f  %.4f dex" % (rho, s))
        rows.append(dict(scope="iron_pnictide_122", inputs="printed, rho %.1f"
                         % rho, T=4.2, H_5=s))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("\n   wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
