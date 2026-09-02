#!/usr/bin/env python3
"""
regenerate_regime_tables.py

Rebuilds the two Stage 2 tables from the frozen anchor cohort, and renames two
columns that counted something other than what they were called.

Why. phase_3_p39_stage2_regime_classification.csv carried a chalcogenide
variance ratio of 0.7610 over 12 records against the regenerated 0.7687 over 10,
because it is built from phase_3_p31_jc_anchor_substructure_sampleform.csv,
which no withdrawal or correction ever propagated into. That file still listed
cuprate_HBCCO and conventional_A15, both withdrawn; a sample_form of "unknown",
which the corrections of 2026-09-01 eliminated; a chalcogenide wire cell at
-0.42 in log10 Jc, which is the FST mis-classification since re-labelled
thin_film; and iron_pnictide_1111 split across thin_film and unknown rather than
across the three forms it actually has. Every derived quantity in the regime
table inherited all of that.

The renames. Neither column counted papers.

  n_papers in the sample-form table is len(log_jc) over the rows of one
  (substructure, sample_form) cell, so it counts anchor records, and a record is
  one specimen at one isotherm. It becomes n_anchor_records.

  n_papers_total in the regime table is the sum of that over a substructure's
  cells, so it counts anchor records too. It becomes n_anchor_records.

  n_papers in the regime table comes from the variance decomposition, which runs
  on records aggregated to one per physical sample, so it counts samples rather
  than papers or records. It becomes n_physical_samples.

The three quantities differ: iron chalcogenide 11-type has 21 anchor records
from 10 physical samples across 7 source papers. Reporting any of them under the
name of another is what let a stale count sit unnoticed beside a fresh one.

Standard deviations use the population convention, ddof = 0, which is what the
deposited file used and what the variance decomposition uses.

    python analysis/regenerate_regime_tables.py --dry-run
    python analysis/regenerate_regime_tables.py

Run from the repository root.
"""
import argparse
import os
import shutil
import sys

import numpy as np
import pandas as pd

ANCHORS = os.path.join("data", "phase_3_p31_jc_anchor_per_paper.csv")
FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
P18 = os.path.join("data", "phase_3_p18_substructure_descriptor_means.csv")
DECOMP = os.path.join("data", "phase_3_p31_variance_decomposition.csv")
SF_OUT = os.path.join("data", "phase_3_p31_jc_anchor_substructure_sampleform.csv")
REGIME_OUT = os.path.join("data", "phase_3_p39_stage2_regime_classification.csv")
LOW_CONFIDENCE = 3          # cells below this many records are flagged
IQR_FROM_STD = 1.35         # the deposited estimator, kept so the column means the same thing


def sample_form_table(a):
    rows = []
    for (sub, sf), g in a.groupby(["substructure", "sample_form"]):
        v = g.log10_Jc_anchor.dropna().values
        sd = float(np.std(v, ddof=0))
        se = sd / np.sqrt(len(v)) if len(v) else np.nan
        rows.append(dict(substructure=sub, sample_form=sf,
                         n_anchor_records=len(v),
                         log10_Jc_anchor_mean=float(np.mean(v)),
                         log10_Jc_anchor_median=float(np.median(v)),
                         log10_Jc_anchor_std=sd,
                         log10_Jc_anchor_ci_lo_95=(float(np.mean(v) - 1.96 * se)
                                                   if len(v) > 1 else np.nan),
                         log10_Jc_anchor_ci_hi_95=(float(np.mean(v) + 1.96 * se)
                                                   if len(v) > 1 else np.nan),
                         low_confidence_flag=len(v) < LOW_CONFIDENCE))
    return pd.DataFrame(rows).sort_values(["substructure", "sample_form"])


def regime(ratio):
    if pd.isna(ratio):
        return "Regime_unknown"
    if ratio > 0.7:
        return "Regime_A_sample_form_dominant"
    if ratio >= 0.3:
        return "Regime_B_sample_form_moderate"
    return "Regime_C_sample_form_minor"


def regime_table(sf, decomp):
    per = decomp[decomp.scope == "per_substructure"].copy()
    per = per.rename(columns={"n_papers": "n_physical_samples"})
    per["regime"] = per.ratio_between_total.apply(regime)
    g = sf.groupby("substructure")
    stats = pd.DataFrame(dict(
        n_anchor_records=g.n_anchor_records.sum(),
        log_jc_anchor_iqr_substructure_only=g.log10_Jc_anchor_median.apply(
            lambda v: float(np.percentile(v, 75) - np.percentile(v, 25))),
        log_jc_anchor_iqr_sample_form_conditional_avg=g.log10_Jc_anchor_std.apply(
            lambda v: float(np.mean(v * IQR_FROM_STD))),
    )).reset_index()
    out = per.merge(stats, on="substructure", how="left")
    out["precision_improvement_factor"] = (
        out.log_jc_anchor_iqr_substructure_only
        / out.log_jc_anchor_iqr_sample_form_conditional_avg)
    return out


def descriptor_means(a):
    """Rebuild the H_irr_or_empirical rows of the descriptor table.

    That framing still carried conventional_A15 and cuprate_HBCCO, both
    withdrawn, and an iron_chalcogenide_11 row on the 56-fit pre-withdrawal
    cohort. The other two framings are left untouched: nothing in the deposit
    states how their rows were assembled, and rewriting them on a guess is the
    error this revision keeps correcting.

    The rule is recovered rather than assumed, and reproduces the deposited row
    exactly for every family whose cohort did not move: n_papers is the fit
    count, beta_H_median and beta_H_mean are over all fits, and each descriptor
    mean is the mean over fits of the compound's value.
    """
    import sys as _s
    _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from multi_stage_loso import classify
    f = pd.read_csv(FITS)
    f["substructure"] = f.compound_formula.apply(classify)
    d = a.drop_duplicates("compound_formula").set_index("compound_formula")
    for c in ("mean_chi", "max_chi", "var_chi", "ionic_fraction"):
        f[c] = f.compound_formula.map(d[c])
    g = f.groupby("substructure")
    out = pd.DataFrame(dict(
        framing="H_irr_or_empirical",
        n_papers=g.beta.size(),
        beta_H_mean=g.beta.mean(), beta_H_median=g.beta.median(),
        mean_chi_mean=g.mean_chi.mean(), max_chi_mean=g.max_chi.mean(),
        var_chi_mean=g.var_chi.mean(),
        ionic_fraction_mean=g.ionic_fraction.mean(),
        beta_T_mean=np.nan, beta_T_median=np.nan)).reset_index()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    a = pd.read_csv(ANCHORS)
    sf = sample_form_table(a)
    out = regime_table(sf, pd.read_csv(DECOMP))

    old = pd.read_csv(REGIME_OUT) if os.path.exists(REGIME_OUT) else None
    print("Stage 2 regime table, regenerated from %d anchor records\n" % len(a))
    print("   %-22s %6s %6s %6s %8s   %s"
          % ("substructure", "smpl", "recs", "forms", "ratio", "regime"))
    for _i, r in out.iterrows():
        print("   %-22s %6d %6d %6d %8s   %s"
              % (r.substructure, r.n_physical_samples, r.n_anchor_records,
                 r.n_sample_forms,
                 "n/a" if pd.isna(r.ratio_between_total)
                 else "%.4f" % r.ratio_between_total, r.regime))
    if old is not None:
        gone = set(old.substructure) - set(out.substructure)
        if gone:
            print("\n   families dropped as withdrawn: %s" % ", ".join(sorted(gone)))
        same = out.set_index("substructure").regime.reindex(
            old.set_index("substructure").regime.index)
        moved = [s for s in old.substructure
                 if s in set(out.substructure)
                 and old.set_index("substructure").regime[s] != same[s]]
        print("   regime labels changed: %s" % (", ".join(moved) if moved else "none"))
    print("\n   forms now present: %s" % ", ".join(sorted(sf.sample_form.unique())))

    if args.dry_run:
        print("\nnothing was written.")
        return 0
    backup = os.path.join("audit", "pre_regime_regeneration_20260902")
    os.makedirs(backup, exist_ok=True)
    for p in (SF_OUT, REGIME_OUT):
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(backup, os.path.basename(p)))
    sf.to_csv(SF_OUT, index=False)
    out.to_csv(REGIME_OUT, index=False)
    if os.path.exists(P18):
        p18 = pd.read_csv(P18)
        shutil.copy2(P18, os.path.join(backup, os.path.basename(P18)))
        keep = p18[p18.framing != "H_irr_or_empirical"]
        new = descriptor_means(a)[list(p18.columns)]
        pd.concat([new, keep], ignore_index=True).to_csv(P18, index=False)
        print("   descriptor table: H_irr_or_empirical rebuilt, %d rows -> %d; "
              "other framings untouched"
              % ((p18.framing == "H_irr_or_empirical").sum(), len(new)))
    print("\nwritten %s and %s\nbackups: %s" % (SF_OUT, REGIME_OUT, backup))
    return 0


if __name__ == "__main__":
    sys.exit(main())
