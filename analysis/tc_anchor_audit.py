#!/usr/bin/env python3
"""
tc_anchor_audit.py

The Tc used by every Cohort A temperature-axis fit, checked against the paper it
is attributed to, and the consequence of correcting it.

Why this exists. provenance_table_fitcohort_full.csv records Tc_provenance as
"paper-reported (v3.2.1 / Cohort A vision pass)" for all 31 Cohort A rows. Within
Cohort A it is not paper-reported: Tc_anchor_K is a strict function of the
idealised parent-compound string, and check_compound_keyed() below asserts that
rather than asserting it in prose. Every row reading Ba(FeAs)2 carries 38.0 K,
every Fe2TeSe 14.5 K, every Sm2FeAs2O 55.0 K, every Pr2FeAs2O 51.0 K. Those ten
Ba(FeAs)2 rows are Rb-substituted, Co-doped, P-doped, Ni-doped and K-doped
samples whose measured Tc runs from 19 K to 40 K. Across all 62 rows there is one
counterexample (FeSeTe at 14.5 in Cohort A and 14.0 in Cohort B), so the claim is
stated for Cohort A only.

Scope. The fit table covers 20 papers. Two are Elsevier extension rows with no
PDF in the corpus and nothing is asserted about them. Of the remaining eighteen,
one paper's own Tc could not be located, so the readings below cover seventeen.

TC_READ records what each paper says about the sample whose figure was
extracted, with the sentence it was read from, so a reading can be checked
without reopening the PDF. Where a paper gives several conventions for that same
sample (onset, midpoint, zero resistance) they are recorded in `alts` and the
conclusion is recomputed across every combination, because beta_T is sensitive
to the choice and a difference of convention is not an error.

Three things the earlier version of this script got wrong and an independent
review caught:

  - 2012.13723v3 was read as 38.3 K. That number appears once in the paper and
    refers to previously reported films on oxide substrates, not to the CaF2
    film measured here, which is 36.4 K.
  - 1111.3923v1 was marked unresolved. The paper has one film and states its Tc
    twice; 13.6 K is the bulk PLD target, not the film.
  - 1108.0407v1 and 1611.08455v1 were counted as errors. Both papers report a
    zero-resistance Tc within a kelvin of the deposited anchor, so those are
    differences of convention and are marked as such.

The effect on the fitted exponent is computed by refitting from the same
extraction rows under the corrected Tc. Section C reports what that refit is and
is not: because each paper's isotherms are near-parallel translations of one
another, the shift is close to a Tc-only rescaling and the papers, not the fits,
are the independent units.

Section D runs the null the conclusion needs. A collapse in spread is only
evidence about Tc if a wrong Tc does not produce it, so the same statistic is
recomputed under random Tc drawn from each family's plausible range.

    python3 analysis/tc_anchor_audit.py

Run from the repository root. Changes nothing.
"""
import os
import sys

import numpy as np
import pandas as pd

DEP = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
WIDE = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
        "agent2_dataset_v3_2_1.csv")

GROSS_K = 5.0        # a Tc error at or above this is reported separately
CONVENTION_K = 1.0   # deposited within this of any Tc the paper states for the
                     # same sample counts as a difference of convention

# paper -> dict(read, alts, compound, quote, note)
#   read     the paper's Tc for the sample whose figure was extracted
#   alts     other conventions the paper gives FOR THE SAME SAMPLE
#   quote    the sentence `read` came from
TC_READ = {
    "0806.2839v1.pdf": dict(
        read=54.6, alts=[], compound="SmO(1-x)F(x)FeAs",
        quote="critical temperatures Tc = 54.6 K"),
    "0903.0004v2.pdf": dict(
        read=22.6, alts=[], compound="Rb-substituted BaFe2As2",
        quote="an onset to superconductivity at 22.6 K, for the plate-like "
              "crystal from the same batch used for the DC magnetization"),
    "0906.0444v1.pdf": dict(
        read=24.0, alts=[], compound="Ba(Fe0.93Co0.07)2As2",
        quote="Tc of the irradiated Ba(Fe0.93Co0.07)2As2 sample is 24 K and is "
              "not affected by the introduction of the columnar damage"),
    "0907.0147v2.pdf": dict(
        read=15.3, alts=[], compound="FeTe0.60Se0.40",
        quote="superconducts with a Tc onset of 15.3K"),
    "1002.0208v2.pdf": dict(
        read=48.0, alts=[], compound="PrFeAsO0.60F0.12",
        quote="the M(T) curve exhibits a usual superconducting behavior with "
              "the diamagnetic onset temperature ~ 48 K"),
    "1009.4896v1.pdf": dict(
        read=None, alts=[], compound="LiFeAs",
        quote="no statement of this sample's own Tc appears in the text; the "
              "only temperatures given are measurement temperatures"),
    "1104.0477v2.pdf": dict(
        read=15.2, alts=[16.1], compound="FeSe0.5Te0.5 film C1",
        quote="the midpoint Tc and zero-resistivity Tc are 16.1 and 15.2 K for "
              "C1; Jc is measured on C1"),
    "1108.0407v1.pdf": dict(
        read=9.8, alts=[11.4, 8.1], compound="beta-FeSe",
        quote="the midpoint of resistive transition with Tc = 9.8 K; the paper "
              "also gives Tc,onset 11.4 K and Tc,0 8.1 K"),
    "1111.3923v1.pdf": dict(
        read=17.7, alts=[], compound="FeSe(1-x)Te(x) film",
        quote="the Fe/FeSe1-xTex bilayer with a high Tc of 17.7 K showed strong "
              "intrinsic pinning; 13.6 K is the bulk PLD target, not the film"),
    "1502.05345v1.pdf": dict(
        read=30.7, alts=[], compound="P-doped BaFe2As2 film",
        quote="phase purity with a high Tc of 30.7 K"),
    "1611.08455v1.pdf": dict(
        read=13.7, alts=[16.0], compound="FeTe0.65Se0.35",
        quote="both samples A and B exhibit almost the same onset of Tc "
              "(T_onset_c ~ 13.7 K +/- 0.2 K), as determined from the real part "
              "of the AC susceptibility. The paper also reports a resistive "
              "onset near 16 K; 13.7 K is the one that matches Fig. 5(b), whose "
              "jc is taken from the width of the magnetisation loop"),
    "1903.00866v2.pdf": dict(
        read=36.0, alts=[], compound="CaKFe4As4",
        quote="Tc defined by the onset of diamagnetism is 36.0 K"),
    "2012.13723v3.pdf": dict(
        read=36.4, alts=[36.0], compound="K-doped BaFe2As2 film on CaF2",
        quote="with Tc_on of 36.4 K; abstract gives an onset Tc of 36 K. The "
              "38.3 K in this paper is previously reported films on oxide "
              "substrates, not this one"),
    "2207.06629v1.pdf": dict(
        read=39.8, alts=[], compound="K-doped Ba122 film",
        quote="the film exhibited a high critical temperature of 39.8 K"),
    "2305.10034v1.pdf": dict(
        read=13.3, alts=[], compound="La0.87Sm0.13FeAs0.91P0.09O",
        quote="the appearance of superconductivity at 13.3 K in "
              "La0.87Sm0.13FeAs0.91P0.09O"),
    "2308.10492v1.pdf": dict(
        read=19.3, alts=[], compound="BaFe1.908Ni0.092As2",
        quote="above the superconducting transition Tc (~ 19.3 K); the sentence "
              "carries a citation, so this reading is the weakest of the six"),
    "2510.10264v1.pdf": dict(
        read=25.1, alts=[], compound="underdoped PrFeAs(O,F)",
        quote="the critical temperature is determined to be approximately "
              "Tc_zero = 25.1 K"),
    "2511.19058v1.pdf": dict(
        read=9.0, alts=[], compound="FeSe (strained)",
        quote="the superconducting transition temperature Tc of FeSe-strain "
              "remains essentially unchanged at 9 K"),
}

# plausible Tc range per family, for the null in section D
FAMILY_RANGE = {
    "iron_chalcogenide_11": (8.0, 18.0),
    "iron_pnictide_122": (19.0, 40.0),
    "iron_pnictide_1111": (13.0, 56.0),
    "iron_pnictide_111": (15.0, 20.0),
}


def beta_T(temps, jcs, Tc):
    """
    Slope of log10 Jc against log10(1 - T/Tc), the form the deposited fits use.
    NaN when any temperature reaches Tc, because the regressor is undefined
    there; that is a result, not an error.
    """
    T = np.asarray(temps, float)
    if Tc is None or not np.isfinite(Tc) or np.any(T >= Tc):
        return np.nan
    x = np.log10(1.0 - T / Tc)
    y = np.log10(np.asarray(jcs, float))
    if len(x) < 3 or np.ptp(x) == 0:
        return np.nan
    return float(np.polyfit(x, y, 1)[0])


def refit(wide, paper, H, Tmin, Tmax, Tc):
    T, J = points(wide, paper, H, Tmin, Tmax)
    if len(T) < 3:
        return np.nan, 0
    return beta_T(T, J, Tc), len(T)


_CACHE = {}


def points(wide, paper, H, Tmin, Tmax):
    """(T, Jc) for one deposited row, cached, so the null can resample cheaply."""
    k = (paper, H, Tmin, Tmax)
    if k not in _CACHE:
        s = wide[(wide.pdf_name == paper) & (wide.Jc > 0) & (wide.field_T == H)]
        s = s[(s.temperature_K >= Tmin) & (s.temperature_K <= Tmax)]
        s = s.sort_values("temperature_K")
        _CACHE[k] = (s.temperature_K.values.astype(float),
                     s.Jc.values.astype(float))
    return _CACHE[k]


def check_compound_keyed():
    """Assert in code what the docstring claims about the provenance table."""
    pr = pd.read_csv(PROV)
    a = pr[pr.Tc_provenance.str.contains("Cohort A", na=False)]
    bad = a.groupby("compound").Tc_anchor_K.nunique()
    bad = bad[bad > 1]
    ok = len(bad) == 0
    print("  Cohort A rows                         : %d" % len(a))
    print("  distinct compound strings             : %d" % a.compound.nunique())
    print("  compounds carrying one Tc only        : %s"
          % ("all of them" if ok else "NO: %s" % list(bad.index)))
    print("  all declared paper-reported           : %s"
          % bool(a.Tc_provenance.str.contains("paper-reported").all()))
    for c in ("Ba(FeAs)2", "Fe2TeSe", "Sm2FeAs2O", "Pr2FeAs2O"):
        g = a[a.compound == c]
        if len(g):
            print("    %-12s %2d rows  Tc = %s"
                  % (c, len(g), sorted(g.Tc_anchor_K.unique())))
    return ok


def reproduction_check(dep, wide):
    """
    Every row whose deposited beta_T is not reproduced from the wide file under
    its own deposited Tc, to a relative tolerance of 1e-4 (loose enough to
    ignore the last-digit rounding in the deposited table, tight enough that a
    genuinely different fit cannot pass). Those rows cannot support a "changing only Tc"
    comparison and are excluded from section B by name.
    """
    bad = []
    for _, r in dep.iterrows():
        if r.paper_id not in TC_READ:
            continue
        b, n = refit(wide, r.paper_id, r.field_T, r.T_min, r.T_max, r.Tc_K)
        if not np.isfinite(b) or abs(b - r.beta_T) > max(1e-4, 1e-4 * abs(r.beta_T)):
            bad.append((r.paper_id, r.field_T, r.beta_T, b))
    return bad


def spread_table(per_paper_dep, per_paper_cor, per_fit_dep, per_fit_cor):
    def mm(x):
        x = np.asarray(x, float)
        x = x[np.isfinite(x) & (x > 0)]
        return x.max() / x.min() if len(x) else np.nan

    def iqr(x):
        x = np.asarray(x, float)
        x = x[np.isfinite(x) & (x > 0)]
        return np.percentile(x, 75) / np.percentile(x, 25) if len(x) else np.nan

    def sdlog(x):
        x = np.asarray(x, float)
        x = x[np.isfinite(x) & (x > 0)]
        return np.std(np.log10(x)) if len(x) else np.nan

    rows = [
        ("max/min, per-paper medians", mm(per_paper_dep), mm(per_paper_cor)),
        ("max/min, per-fit values", mm(per_fit_dep), mm(per_fit_cor)),
        ("Q3/Q1, per-fit values", iqr(per_fit_dep), iqr(per_fit_cor)),
        ("Q3/Q1, per-paper medians", iqr(per_paper_dep), iqr(per_paper_cor)),
        ("sd of log10, per-paper medians", sdlog(per_paper_dep), sdlog(per_paper_cor)),
    ]
    return rows


def main():
    for f in (DEP, PROV):
        if not os.path.exists(f):
            sys.exit("missing: %s" % f)
    if not os.path.exists(WIDE):
        sys.exit("wide file not found: %s" % WIDE)
    dep = pd.read_csv(DEP)
    wide = pd.read_csv(WIDE)

    print("=" * 92)
    print("A. IS THE ANCHOR COMPOUND-KEYED RATHER THAN PAPER-REPORTED?")
    print("=" * 92)
    check_compound_keyed()

    print()
    print("=" * 92)
    print("B. THE ANCHOR AGAINST EACH PAPER")
    print("=" * 92)
    print("%-18s %9s %9s %8s  %-12s %s"
          % ("paper", "deposited", "paper", "error", "verdict", "sample"))
    gross, small, conv, unres = [], [], [], []
    for p in sorted(TC_READ):
        e = TC_READ[p]
        d = dep[dep.paper_id == p]
        if d.empty:
            continue
        used = float(d.Tc_K.iloc[0])
        if e["read"] is None:
            unres.append(p)
            print("%-18s %9.1f %9s %8s  %-12s %s"
                  % (p[:18], used, "-", "-", "unresolved", e["compound"]))
            continue
        err = used - e["read"]
        near = min([abs(used - v) for v in ([e["read"]] + e["alts"])])
        if near <= CONVENTION_K:
            v = "convention"
            conv.append(p)
        elif abs(err) >= GROSS_K:
            v = "GROSS"
            gross.append(p)
        else:
            v = "off"
            small.append(p)
        print("%-18s %9.1f %9.1f %+8.1f  %-12s %s"
              % (p[:18], used, e["read"], err, v, e["compound"]))

    print("\n  wrong by %.0f K or more     : %d  %s"
          % (GROSS_K, len(gross), ", ".join(x[:12] for x in gross)))
    print("  wrong by less             : %d  %s"
          % (len(small), ", ".join(x[:12] for x in small)))
    print("  difference of convention  : %d  %s"
          % (len(conv), ", ".join(x[:12] for x in conv)))
    print("  not established           : %d  %s"
          % (len(unres), ", ".join(x[:12] for x in unres)))

    print()
    print("=" * 92)
    print("C. WHAT CORRECTING THE ANCHOR DOES TO beta_T")
    print("=" * 92)
    bad = reproduction_check(dep, wide)
    if bad:
        print("  rows excluded because the deposited beta_T is not reproduced")
        print("  from the wide file under its own Tc (so 'changing only Tc'")
        print("  would be false for them):")
        for pid, H, dv, rv in bad:
            print("    %-18s H=%-6.2f deposited %.6f  refit %.6f"
                  % (pid[:18], H, dv, rv))
    else:
        print("  every row reproduces under its own Tc")
    excl = {(b[0], b[1]) for b in bad}

    rows = []
    for _, r in dep.iterrows():
        e = TC_READ.get(r.paper_id)
        if not e or e["read"] is None:
            continue
        if (r.paper_id, r.field_T) in excl:
            continue
        b_old, _ = refit(wide, r.paper_id, r.field_T, r.T_min, r.T_max, r.Tc_K)
        b_new, _ = refit(wide, r.paper_id, r.field_T, r.T_min, r.T_max, e["read"])
        if not np.isfinite(b_old) or not np.isfinite(b_new):
            continue
        rows.append(dict(paper=r.paper_id, sub=r.substructure,
                         old=b_old, new=b_new))
    t = pd.DataFrame(rows)
    print("\n  fits compared : %d, over %d papers"
          % (len(t), t.paper.nunique()))
    print("\n%-18s %5s %10s %10s %8s"
          % ("paper", "fits", "deposited", "corrected", "shift"))
    pm = t.groupby("paper").agg(old=("old", "median"), new=("new", "median"),
                                n=("old", "size")).sort_values("old",
                                                               ascending=False)
    for p, r in pm.iterrows():
        print("%-18s %5d %10.3f %10.3f %8.2f"
              % (p[:18], r.n, r.old, r.new, r.new / r.old))

    print("\n  How much of this is a refit? Each paper's isotherms are")
    print("  near-parallel translations, so the shift is close to a Tc-only")
    print("  rescaling of the deposited slope. Correlation between the actual")
    print("  shift and the geometric factor computed from the temperatures and")
    print("  the two Tc values alone, using no Jc value:")
    g = []
    for _, r in dep.iterrows():
        e = TC_READ.get(r.paper_id)
        if not e or e["read"] is None or (r.paper_id, r.field_T) in excl:
            continue
        s = wide[(wide.pdf_name == r.paper_id) & (wide.Jc > 0)
                 & (wide.field_T == r.field_T)]
        s = s[(s.temperature_K >= r.T_min) & (s.temperature_K <= r.T_max)]
        T = s.temperature_K.values
        if len(T) < 3 or np.any(T >= e["read"]) or np.any(T >= r.Tc_K):
            continue
        num = np.ptp(np.log10(1 - T / r.Tc_K))
        den = np.ptp(np.log10(1 - T / e["read"]))
        if den > 0:
            g.append(num / den)
    if len(g) == len(t):
        ratio = (t.new / t.old).values
        print("    corr = %.5f over %d fits" % (np.corrcoef(g, ratio)[0, 1], len(g)))
    print("  So the independent units are the %d papers, not the %d fits."
          % (t.paper.nunique(), len(t)))

    print()
    print("=" * 92)
    print("D. HOW BIG IS THE COLLAPSE, AND DOES A WRONG Tc PRODUCE IT TOO?")
    print("=" * 92)
    print("%-34s %10s %10s %8s" % ("statistic", "deposited", "corrected", "factor"))
    for name, a, b in spread_table(pm.old.values, pm.new.values,
                                   t.old.values, t.new.values):
        print("%-34s %10.2f %10.2f %8.2f" % (name, a, b, a / b))

    sub = t.groupby("sub").agg(old=("old", "median"), new=("new", "median"))
    print("\n  by substructure (median over fits)")
    for s_, r in sub.iterrows():
        print("    %-24s %8.3f -> %8.3f  x%.2f" % (s_, r.old, r.new, r.new / r.old))
    print("    spread across substructures %.2f -> %.2f"
          % (sub.old.max() / sub.old.min(), sub.new.max() / sub.new.min()))

    print("\n  Null: random Tc from each family's plausible range, floored above")
    print("  the paper's own T_max. 400 draws, same statistic.")
    rng = np.random.default_rng(0)
    fam = dep.groupby("paper_id").substructure.first().to_dict()
    tmax = dep.groupby("paper_id").T_max.max().to_dict()
    papers = list(pm.index)
    rowsets = {p: [(r.field_T, r.T_min, r.T_max)
                   for _, r in dep[dep.paper_id == p].iterrows()]
               for p in papers}
    for p in papers:                       # warm the cache once
        for H, a, b in rowsets[p]:
            points(wide, p, H, a, b)
    null_mm, null_sd = [], []
    for _ in range(400):
        med = []
        for p in papers:
            lo, hi = FAMILY_RANGE.get(fam[p], (10.0, 50.0))
            lo = max(lo, tmax[p] + 0.5)
            if hi <= lo:
                hi = lo + 1.0
            tc = rng.uniform(lo, hi)
            v = [beta_T(*points(wide, p, H, a, b), tc)
                 for H, a, b in rowsets[p]]
            v = [x for x in v if np.isfinite(x) and x > 0]
            if v:
                med.append(np.median(v))
        med = np.array(med)
        if len(med) > 2:
            null_mm.append(med.max() / med.min())
            null_sd.append(np.std(np.log10(med)))
    null_mm = np.array(null_mm)
    null_sd = np.array(null_sd)
    obs_mm = pm.new.max() / pm.new.min()
    obs_sd = np.std(np.log10(pm.new.values))
    print("    max/min   observed %.2f   null median %.2f  [%.2f, %.2f]  p = %.3f"
          % (obs_mm, np.median(null_mm), np.percentile(null_mm, 5),
             np.percentile(null_mm, 95), (null_mm <= obs_mm).mean()))
    print("    sd(log10) observed %.3f  null median %.3f [%.3f, %.3f]  p = %.3f"
          % (obs_sd, np.median(null_sd), np.percentile(null_sd, 5),
             np.percentile(null_sd, 95), (null_sd <= obs_sd).mean()))

    print("\n  This section says nothing about whether the Jc series are")
    print("  readings of the published figures. See")
    print("  audit/anchored_vs_generated_20260905.md, which stands.")


if __name__ == "__main__":
    main()
