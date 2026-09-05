#!/usr/bin/env python3
"""
headline_on_repaired_cohort.py

Does the exponent separate substructure families, and does repairing the
anchors change the answer?

WHAT THE FIRST VERSION OF THIS GOT WRONG. It compared a between-family
DIFFERENCE of medians against the largest between-paper STANDARD DEVIATION
inside one family, and reported that repairing the Tc anchors made the
temperature axis clear that bar for the first time. An independent review broke
it three ways:

  1. the two cohorts being compared were not the same cohort. The repaired table
     drops two papers whose fit rule was never reproduced, for reasons that have
     nothing to do with Tc, and both are single-fit chalcogenide papers carrying
     a full paper's weight. On the matched intersection the DEPOSITED axis
     already clears the bar, so the flip was cohort composition.
  2. a range over k group medians and the standard deviation of one group are
     not comparable statistics. They differ in units of dispersion, in how they
     grow with k, and in sample size.
  3. the bootstrap was upward biased, by an amount that differed between the
     cohorts being compared, so most of the apparent tightening of the interval
     was differential bias rather than precision.

WHAT IS REPORTED NOW. One statistic, on per-paper medians, with papers as the
unit of analysis:

    eta squared   the fraction of between-paper variance in the exponent that
                  the family label accounts for
    permutation p the same statistic under 20000 shuffles of the family label
                  across papers

Both are scale free, both use papers as the unit, and the permutation test needs
no distributional assumption. Every cohort comparison is run on the matched
intersection of papers and fits, and the script refuses to compare two cohorts
that do not cover the same papers.

    python3 analysis/headline_on_repaired_cohort.py
    python3 analysis/headline_on_repaired_cohort.py --selftest

Run from the repository root. Writes audit/headline_on_repaired_cohort.csv.
"""
import os
import re
import sys

import numpy as np
import pandas as pd

FITS_B = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_A = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
FITS_A_REP = FITS_A.replace(".csv", "_repaired.csv")
PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
APPLIED = os.path.join("audit", "fit_protocol_applied.csv")
OUT = os.path.join("audit", "headline_on_repaired_cohort.csv")
N_PERM = 20000
MIN_PAPERS_PER_FAMILY = 2


def norm_key(k):
    """Fits-table paper_key to the provenance table's identifier."""
    k = re.sub(r"^(elsevier|springer|iop)_", "", str(k))
    k = re.sub(r"\.pdf$", "", k)
    if k.startswith("10."):
        parts = k.split("_")
        if len(parts) > 1:
            k = parts[0] + "/" + "_".join(parts[1:])
    return k


def attach_family(fits, prov, check_col=None):
    """Family per fit, with every mapping required to resolve uniquely."""
    m = {}
    for _, r in prov.iterrows():
        ident = str(r.identifier)
        if ident in m and m[ident] != r.substructure_family:
            raise SystemExit(f"provenance carries two families for {ident}")
        m[ident] = r.substructure_family
    fam = []
    for k in fits.paper_key.astype(str):
        hit = m.get(norm_key(k))
        if hit is None:
            cands = [i for i in m if i and i in k]
            if len(cands) != 1:
                raise SystemExit(
                    f"{k!r} maps to {len(cands)} provenance identifiers; the "
                    f"family cannot be assigned without guessing")
            hit = m[cands[0]]
        fam.append(hit)
    out = fits.copy()
    out["family"] = fam
    if out.family.isna().any():
        raise SystemExit("some fits have no family; the join is incomplete")
    if check_col and check_col in out.columns:
        bad = out[out[check_col].notna() & (out[check_col] != out.family)]
        if len(bad):
            raise SystemExit(f"the regex join disagrees with the deposit's own "
                             f"{check_col} on {len(bad)} rows")
    return out


def per_paper(fits, beta_col):
    t = (fits.groupby(["paper_key", "family"])[beta_col].median().reset_index()
         .rename(columns={"paper_key": "paper", beta_col: "beta"}))
    counts = t.groupby("family").paper.nunique()
    keep = counts[counts >= MIN_PAPERS_PER_FAMILY].index
    return t[t.family.isin(keep)], sorted(set(counts.index) - set(keep))


def eta_squared(t):
    """Fraction of between-paper variance in beta explained by the family."""
    y = t.beta.to_numpy(float)
    if len(y) < 3 or t.family.nunique() < 2:
        return np.nan
    grand = y.mean()
    ss_tot = ((y - grand) ** 2).sum()
    if ss_tot <= 0:
        return np.nan
    ss_between = sum(len(g) * (g.beta.mean() - grand) ** 2
                     for _, g in t.groupby("family"))
    return float(ss_between / ss_tot)


def _eta_fast(y, codes, k, ss_tot, grand):
    """eta squared from integer group codes. Same quantity as eta_squared."""
    cnt = np.bincount(codes, minlength=k)
    tot = np.bincount(codes, weights=y, minlength=k)
    with np.errstate(invalid="ignore", divide="ignore"):
        means = np.where(cnt > 0, tot / np.maximum(cnt, 1), grand)
    return float((cnt * (means - grand) ** 2).sum() / ss_tot)


def permutation_p(t, n=N_PERM, seed=0):
    """Shuffle the family label ACROSS PAPERS, which is the unit of analysis."""
    obs = eta_squared(t)
    if not np.isfinite(obs):
        return np.nan, obs
    y = t.beta.to_numpy(float)
    codes, uniq = pd.factorize(t.family)
    k = len(uniq)
    grand = y.mean()
    ss_tot = ((y - grand) ** 2).sum()
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n):
        hits += _eta_fast(y, rng.permutation(codes), k, ss_tot, grand) >= obs - 1e-12
    return (hits + 1) / (n + 1), obs


def summarise(name, fits, beta_col, prov, check_col=None):
    f = attach_family(fits, prov, check_col)
    f = f[np.isfinite(f[beta_col])]
    t, thin = per_paper(f, beta_col)
    used = f[f.family.isin(t.family.unique())]
    p, eta = permutation_p(t)
    print("=" * 76)
    print(f"{name}")
    print(f"  analysed: {len(used)} fits over {t.paper.nunique()} papers in "
          f"{t.family.nunique()} families"
          + (f"; excluded, fewer than {MIN_PAPERS_PER_FAMILY} papers: "
             f"{', '.join(thin)}" if thin else ""))
    tab = t.groupby("family").agg(papers=("paper", "nunique"),
                                  median_beta=("beta", "median"))
    print(tab.round(3).to_string())
    print(f"  eta squared {eta:.3f}   permutation p {p:.4f} over {N_PERM} "
          f"shuffles of the family label across papers")
    print(f"  exponents on the analysed set: median "
          f"{used[beta_col].median():.3f}, range {used[beta_col].min():.3f} to "
          f"{used[beta_col].max():.3f}")
    print()
    return dict(cohort=name, fits=len(used), papers=t.paper.nunique(),
                families=t.family.nunique(), eta_sq=eta, perm_p=p,
                median_beta=used[beta_col].median()), t


def matched(a, b):
    """Restrict two per-paper tables to the papers they share."""
    common = sorted(set(a.paper) & set(b.paper))
    return a[a.paper.isin(common)], b[b.paper.isin(common)], common


def selftest():
    bad = 0
    rng = np.random.default_rng(0)
    # a table with a real family effect and one without
    strong = pd.DataFrame(dict(
        paper=[f"p{i}" for i in range(12)],
        family=["A"] * 6 + ["B"] * 6,
        beta=list(rng.normal(1, .1, 6)) + list(rng.normal(3, .1, 6))))
    ps, _ = permutation_p(strong, 2000)
    # the null arm is the MEDIAN over many draws, not one draw: with six papers
    # a side, a single random table reaches eta squared near 0.5 often enough
    # that testing one of them measures the draw and not the statistic
    pn = float(np.median([
        permutation_p(strong.assign(beta=rng.normal(2, 1, 12)), 500, seed=i)[0]
        for i in range(20)]))
    ok = ps < 0.01 and pn > 0.2
    print(f"  [{'PASS' if ok else 'FAIL'}] permutation p separates a planted "
          f"effect from noise: {ps:.4f} against a median {pn:.3f} over 20 "
          f"null draws")
    bad += not ok

    e = eta_squared(strong)
    null = strong.assign(beta=rng.normal(2, 1, 12))
    ok = 0.9 < e <= 1.0 and eta_squared(null) < 0.9
    print(f"  [{'PASS' if ok else 'FAIL'}] eta squared {e:.3f} on the planted "
          f"effect, {eta_squared(null):.3f} on noise")
    bad += not ok

    # scale invariance: multiplying every exponent by ten must not move either
    ten = strong.assign(beta=strong.beta * 10)
    ok = (abs(eta_squared(ten) - e) < 1e-12
          and abs(permutation_p(ten, 2000)[0] - ps) < 1e-12)
    print(f"  [{'PASS' if ok else 'FAIL'}] both statistics are scale free: "
          f"eta {eta_squared(ten):.3f} after a tenfold rescale")
    bad += not ok

    # the matching guard must actually restrict
    a = pd.DataFrame(dict(paper=["x", "y", "z"], family=list("AAB"),
                          beta=[1., 2., 3.]))
    b = a[a.paper != "z"]
    ma, mb, common = matched(a, b)
    ok = common == ["x", "y"] and len(ma) == len(mb) == 2
    print(f"  [{'PASS' if ok else 'FAIL'}] matching restricts to the shared "
          f"papers: {common}")
    bad += not ok

    print("  selftest:", "all guards fire" if not bad
          else f"{bad} GUARD(S) DID NOT FIRE")
    return bad


def main():
    if "--selftest" in sys.argv:
        return selftest()
    print("selftest first")
    if selftest():
        print("THE STATISTIC DOES NOT BEHAVE. Nothing below is trustworthy.")
        return 1
    print()
    prov = pd.read_csv(PROV)
    rows, tables = [], {}

    fb = pd.read_csv(FITS_B)
    r, t = summarise("FIELD AXIS, deposited passing",
                     fb[(fb.ok == True) & (fb.physicality == "ok")],
                     "beta", prov)
    rows.append(r)
    tables["field_dep"] = t

    if os.path.exists(APPLIED):
        ap = pd.read_csv(APPLIED)
        adm = ap[ap.admitted & ap.was_passing].rename(columns={"paper": "paper_key"})
        r, t = summarise("FIELD AXIS, admitted under the stated protocol",
                         adm, "beta", prov)
        rows.append(r)
        tables["field_adm"] = t

    fa = pd.read_csv(FITS_A)
    r, t = summarise("TEMPERATURE AXIS, deposited", fa, "beta_T", prov,
                     check_col="substructure")
    rows.append(r)
    tables["temp_dep"] = t

    if os.path.exists(FITS_A_REP):
        fr = pd.read_csv(FITS_A_REP)
        fr = fr[fr.reproduced & np.isfinite(fr.beta_T_repaired)]
        r, t = summarise("TEMPERATURE AXIS, repaired Tc", fr,
                         "beta_T_repaired", prov, check_col="substructure")
        rows.append(r)
        tables["temp_rep"] = t

    print("=" * 76)
    print("MATCHED COMPARISONS, on the papers each pair shares")
    print("=" * 76)
    for a, b, label in (("temp_dep", "temp_rep", "temperature axis, Tc repair"),
                        ("field_dep", "field_adm", "field axis, repair and protocol")):
        if a not in tables or b not in tables:
            continue
        ta, tb, common = matched(tables[a], tables[b])
        pa, ea = permutation_p(ta)
        pb, eb = permutation_p(tb)
        dropped = sorted(set(tables[a].paper) - set(common))
        print(f"{label}: {len(common)} shared papers"
              + (f"; dropped from the first: {', '.join(dropped)}"
                 if dropped else ""))
        print(f"    before  eta squared {ea:.3f}  p {pa:.4f}")
        print(f"    after   eta squared {eb:.3f}  p {pb:.4f}")
        rows.append(dict(cohort=f"MATCHED {label} (before)", papers=len(common),
                         eta_sq=ea, perm_p=pa))
        rows.append(dict(cohort=f"MATCHED {label} (after)", papers=len(common),
                         eta_sq=eb, perm_p=pb))
        print()

    t = pd.DataFrame(rows)
    os.makedirs("audit", exist_ok=True)
    t.to_csv(OUT, index=False)
    print("SIDE BY SIDE")
    print(t[["cohort", "papers", "eta_sq", "perm_p", "median_beta"]]
          .round(4).to_string(index=False))
    print()
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
