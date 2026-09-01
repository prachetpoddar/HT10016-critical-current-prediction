#!/usr/bin/env python3
"""
phase_3_p57_de_novo_predictions.py

De novo Jc(T,H) prediction dispatch on the 239-candidate list at the
pre-registered default target grid (T = 4.2, 20, 0.77·Tc; H = 0.1, 1, 5 T).

Methodology:
  Form 3 decomposition with anchor at (T_ref = 4.2 K, H_ref = 0.1 T):
    log10 Jc(T, H) = log_Jc_partial_anchor
                   + beta_T * (log10(1 - T/Tc) - log10(1 - T_ref/Tc))
                   + beta_H * (log10(1 - H/Hc2) - log10(1 - H_ref/Hc2))

  - log_Jc_partial_anchor: substructure (× sample_form) cell median from
    canonical Cohort B v2 per-paper fits (Stage 3 substructure-aggregate
    central tendency).
  - beta_T pool: Cohort A p44 fits (iron families) + h1b MgB2 fits with
    physical_beta_T=True (conventional_AlB2 proxy).
  - beta_H pool: Cohort B v2 ok+physicality=ok rows.

Bootstrap CI: N = 5000 iterations, seed = 42 (matches Path delta + Path 19-AC).

Outputs:
  phase_3_p57_de_novo_predictions.csv : 1 row per (candidate, T, H) grid pt
  phase_3_p57_top5_table_data.csv     : top-5 per substructure for Table N
  phase_3_p57_dispatch_report.md      : run report with sigma / tau outcomes

Hard exclusions:
  - iron_pnictide_1111 hard-excluded throughout. Aborts if any 1111 entry
    sneaks into the candidate list.

Cost: $0 (offline file I/O + local computation).
"""

from __future__ import annotations
import importlib.util
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
# In the deposit the tables live in data/ rather than beside this script, which
# is the same path defect that stopped figure_4_source.py running on a clean
# checkout. Prefer data/ and fall back to the script directory.
PREP = HERE.parent / "data" if (HERE.parent / "data").is_dir() else HERE
REPO = HERE.parent.parent.parent
# Extraction CSV directory lives at <REPO>/data_agent2/v3_2_2B_extension (no
# 'kappa_pipeline' intermediate); align with p56b.EXT_B which is canonical.
EXT_B = REPO / "data_agent2/v3_2_2B_extension"

# Source CSVs
CANON_A = PREP / "phase_3_p44_post_UCLA_beta_T_fits.csv"
CANON_B = PREP / "phase_3_form3_fits_partial_cohortB_v2.csv"
H1B = PREP / "h1b_per_paper_form3_fits.csv"
SUBSTEP_C = PREP / "phase_3_p54_substep_C_new_form3_fits.csv"

# p56 / p56b modules (re-used for candidate generation + Hc2 lookup)
# Python modules stay beside this script; only the tables moved to data/.
P56 = HERE / "phase_3_p56_de_novo_candidate_list.py"
P56B = HERE / "phase_3_p56b_hc2_infrastructure_sweep.py"

# Outputs
OUT_PREDICTIONS = PREP / "phase_3_p57_de_novo_predictions.csv"
OUT_TOP5 = PREP / "phase_3_p57_top5_table_data.csv"
OUT_REPORT = PREP / "phase_3_p57_dispatch_report.md"

# Pre-registered grid + bootstrap
T_REF = 4.2
H_REF = 0.1
T_FIX = [4.2, 20.0]      # absolute T grid points; 0.77*Tc added per-candidate
H_GRID = [0.1, 1.0, 5.0] # absolute H grid points (T)
N_BOOT = 5000
RNG_SEED = 42

POPULATED = ("iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2")
EXCLUDED_SUB = "iron_pnictide_1111"

# Substructure-aggregate Tc reference table (literature default for A2 candidates
# without per-row Tc; used only as a backstop. A1 candidates carry Tc from 3DSC.)
TC_DEFAULT_BY_SUB = {
    "iron_chalcogenide_11": 14.0,
    "iron_pnictide_122": 22.0,
    "conventional_AlB2": 39.0,
}

# Sample-form commitment defaults per substructure under the three-regime-
# aware rule (post-FST correction). Each Outcome class has its own
# commitment regime, matching the variance-decomposition diagnostic:
#
#   Outcome A (variance ratio > 0.7; sample form dominates):
#     Uniform commit to the largest empirical sample-form cell.
#     ALL candidates (A1 + A2 alike) use the default.
#
#   Outcome B (0.3 <= variance ratio <= 0.7; conditioning recommended):
#     A1 candidates default to the largest cell.
#     A2 candidates inherit the source paper's sample_form from canonical
#     Cohort B (where available); fall back to default if not.
#     This honors the "conditioning recommended where sample form is known"
#     diagnostic at Outcome B regime.
#
#   Outcome C (variance ratio < 0.3; sample form uninformative):
#     Substructure-aggregate scope (commitment None) for all candidates.
#
# Corrected variance ratios + largest cells (post-FST correction +
# per-paper aggregation):
#   iron_chalcogenide_11: Outcome A (ratio 0.73);
#                         largest cell = single_crystal (n=7 papers)
#   iron_pnictide_122:    Outcome B (ratio 0.60);
#                         A1 default = single_crystal (n=12 papers);
#                         A2 inherits source-paper sample_form
#   conventional_AlB2:    Outcome C (ratio 0.12);
#                         substructure-aggregate (commitment None)
DEFAULT_SAMPLE_FORM = {
    "iron_chalcogenide_11": "single_crystal",
    "iron_pnictide_122": "single_crystal",
    "conventional_AlB2": None,
}

# Engineered-conductor sample-form override for conventional_AlB2 (post
# Outcome-C diagnostic refinement 2026-06-04, see
# kappa_pipeline/analysis/closed_form/mgb2_beta_H_by_sample_form.md):
# V3 stratified MgB2 β_H shows a wire/tape cluster (≈2.8) separated from a
# bulk-like cluster (≈5.2; tape_PIT belongs here at 4.30, not the engineered
# cluster). When an AlB2 A2 candidate's source paper has a sample_form in
# this set, route through the sample-form-conditional β_H + log_jcp pool
# instead of the substructure-aggregate fallback. A1 candidates and
# bulk-source A2 candidates keep the prior Outcome-C aggregate behavior.
ENGINEERED_FORMS = frozenset({"wire", "tape"})

# Parent-match deviation perturbation factors for AlB2 c_parent (±20% envelope
# per dispatch operational implementation; the ±20-50% flag is in metadata).
PARENT_HC2_PERTURB_FACTORS = (0.8, 1.0, 1.2)


# ----------------------------------------------------------------------------
# Module re-import helpers

def _import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ----------------------------------------------------------------------------
# Candidate list assembly

def load_candidates() -> pd.DataFrame:
    """Re-invoke p56b.generate_candidates() and return canonical 239-row table."""
    p56b = _import_module("p56b", P56B)
    cands = p56b.generate_candidates().reset_index(drop=True)

    # Hard-exclusion guard
    n_1111 = (cands["substructure"] == EXCLUDED_SUB).sum()
    if n_1111 > 0:
        raise RuntimeError(
            f"Hard-exclusion violation: {n_1111} iron_pnictide_1111 candidates "
            "found in candidate list. Substep D nu-2 mandates exclusion."
        )

    # Expected count
    expected_n = {"iron_chalcogenide_11": 55,
                  "iron_pnictide_122": 79,
                  "conventional_AlB2": 105}
    for sub, n_exp in expected_n.items():
        n_act = (cands["substructure"] == sub).sum()
        if n_act != n_exp:
            print(f"  WARN: {sub} n={n_act} (expected {n_exp})")

    return cands


# ----------------------------------------------------------------------------
# A2 Tc lookup (extraction CSVs carry tc_K)

def build_a2_tc_index() -> dict:
    """Map (paper_id_stem, compound_formula) → Tc_K from v3_2_2B extraction CSVs."""
    idx = {}
    if not EXT_B.exists():
        return idx
    for csv_path in EXT_B.glob("elsevier_*_VISION_PASS_LONG.csv"):
        try:
            df = pd.read_csv(csv_path)
        except Exception:
            continue
        if "compound_formula" not in df.columns or "tc_K" not in df.columns:
            continue
        for (compound, tc_K), _ in df.groupby(["compound_formula", "tc_K"]):
            if pd.isna(tc_K) or pd.isna(compound):
                continue
            idx[(csv_path.stem, str(compound))] = float(tc_K)
    return idx


# ----------------------------------------------------------------------------
# Hc2 anchor index (re-use p56b indexes)

def build_hc2_indexes():
    """Construct exact + parent Hc2 indexes from p56b sources S1/S3/S5."""
    p56b = _import_module("p56b", P56B)
    S1 = p56b.load_S1()
    S3 = p56b.load_S3()
    S5_lit = p56b.load_S5_lit()
    S5_maki = p56b.load_S5_maki()

    # Filter out iron_pnictide_1111 from Hc2 sources to enforce hard exclusion
    for src in (S1, S3, S5_lit, S5_maki):
        if src is not None and "compound_formula" in src.columns:
            mask = src["compound_formula"].apply(
                lambda c: p56b.assign_substructure(c) != EXCLUDED_SUB
            )
            src.drop(src.index[~mask], inplace=True)

    exact_idx = p56b.build_hc2_index(S1, S3, S5_lit, S5_maki)
    parent_idx = p56b.build_parent_hc2_index(S1, S3, S5_lit, S5_maki)
    return p56b, exact_idx, parent_idx


# ----------------------------------------------------------------------------
# Fit pools

def build_beta_t_pool():
    """Build {substructure: array of physical beta_T fits}."""
    pool = {}
    # Cohort A (iron families)
    df_a = pd.read_csv(CANON_A)
    df_a = df_a[df_a["physicality"] == "ok"]
    for sub in ("iron_chalcogenide_11", "iron_pnictide_122"):
        vals = df_a.loc[df_a["substructure"] == sub, "beta_T"].dropna().to_numpy()
        # Filter to physical range: 0 < beta_T < 10 (Form 3 physical window)
        vals = vals[(vals > 0) & (vals < 10)]
        pool[sub] = vals

    # AlB2: h1b MgB2 with physical_beta_T=True
    df_h1b = pd.read_csv(H1B)
    mgb2 = df_h1b[(df_h1b["compound"] == "MgB2") & (df_h1b["physical_beta_T"] == True)]
    vals = mgb2["beta_T"].dropna().to_numpy()
    vals = vals[(vals > 0) & (vals < 10)]
    pool["conventional_AlB2"] = vals

    return pool


def build_beta_h_log_jcp_pool():
    """Build {(substructure, sample_form): {'beta_H': arr, 'log_jcp': arr}}
    AND {substructure: {'beta_H': arr, 'log_jcp': arr}} substructure-aggregate."""
    p56b = _import_module("p56b", P56B)
    df_b = pd.read_csv(CANON_B)
    df_b = df_b[(df_b["ok"] == True) & (df_b["physicality"] == "ok")]
    df_b = df_b[df_b["fixed_axis"] == "T"].copy()
    df_b["substructure"] = df_b["compound_formula"].apply(p56b.assign_substructure)

    # Hard-exclude 1111 from pool
    df_b = df_b[df_b["substructure"] != EXCLUDED_SUB].reset_index(drop=True)

    # Substructure-aggregate
    agg = {}
    for sub in POPULATED:
        sub_df = df_b[df_b["substructure"] == sub]
        agg[sub] = {
            "beta_H": sub_df["beta"].to_numpy(),
            "log_jcp": sub_df["log_Jc_partial"].to_numpy(),
            "n": len(sub_df),
        }

    # Sample-form-conditional
    cond = {}
    for (sub, sf), grp in df_b.groupby(["substructure", "sample_form"]):
        cond[(sub, sf)] = {
            "beta_H": grp["beta"].to_numpy(),
            "log_jcp": grp["log_Jc_partial"].to_numpy(),
            "n": len(grp),
        }
    return agg, cond


# ----------------------------------------------------------------------------
# Form 3 prediction (bootstrap-vectorised)

def form3_predict_bootstrap(
    *,
    T_K: float,
    H_T: float,
    Tc: float,
    Hc2: float | None,
    log_jcp_anchor_samples: np.ndarray,
    beta_T_samples: np.ndarray,
    beta_H_samples: np.ndarray | None,
) -> tuple[float, float, float]:
    """Compute bootstrap-distributed log Jc at (T, H) and return (median, 2.5, 97.5).

    Anchor convention: prediction equals log_jcp_anchor at (T_ref, H_ref).
    """
    if Tc <= 0 or T_K >= Tc:
        return (np.nan, np.nan, np.nan)
    term_T = np.log10(max(1.0 - T_K / Tc, 1e-9))
    term_T_ref = np.log10(max(1.0 - T_REF / Tc, 1e-9))
    dT = term_T - term_T_ref

    if Hc2 is not None and not np.isnan(Hc2) and Hc2 > 0 and H_T < Hc2 and beta_H_samples is not None:
        term_H = np.log10(max(1.0 - H_T / Hc2, 1e-9))
        term_H_ref = np.log10(max(1.0 - H_REF / Hc2, 1e-9))
        dH = term_H - term_H_ref
        samples = log_jcp_anchor_samples + beta_T_samples * dT + beta_H_samples * dH
    else:
        # T-axis-only: no H contribution
        samples = log_jcp_anchor_samples + beta_T_samples * dT
    return (
        float(np.median(samples)),
        float(np.percentile(samples, 2.5)),
        float(np.percentile(samples, 97.5)),
    )


def bootstrap_draws(pool_vals: np.ndarray, rng: np.random.Generator, n: int) -> np.ndarray:
    """Resample with replacement; return n draws of the cell median."""
    if len(pool_vals) == 0:
        return np.full(n, np.nan)
    if len(pool_vals) == 1:
        return np.full(n, pool_vals[0])
    idx = rng.integers(0, len(pool_vals), size=(n, len(pool_vals)))
    return np.median(pool_vals[idx], axis=1)


# ----------------------------------------------------------------------------
# Per-candidate prediction

def predict_candidate(
    *,
    row: pd.Series,
    tc_K: float,
    hc2_T: float | None,
    hc2_anchor_type: str,
    hc2_source: str | None,
    hc2_deviation_flag: str | None,
    sample_form_commitment: str | None,
    beta_t_pool: dict,
    beta_h_agg_pool: dict,
    beta_h_cond_pool: dict,
    rng: np.random.Generator,
) -> list[dict]:
    """Compute 9 grid-point predictions + bootstrap CIs for one candidate."""
    sub = row["substructure"]

    # Build bootstrap draws once per candidate
    beta_T_samples = bootstrap_draws(beta_t_pool[sub], rng, N_BOOT)

    # Stage 2 sample-form-conditional for β_H + log_jcp (only when commitment set)
    cond_key = (sub, sample_form_commitment) if sample_form_commitment else None
    if cond_key in beta_h_cond_pool and beta_h_cond_pool[cond_key]["n"] >= 3:
        cell = beta_h_cond_pool[cond_key]
        beta_h_pool_arr = cell["beta_H"]
        log_jcp_pool_arr = cell["log_jcp"]
        method_scope = f"sample_form_conditional_median:{sample_form_commitment}"
    else:
        cell = beta_h_agg_pool[sub]
        beta_h_pool_arr = cell["beta_H"]
        log_jcp_pool_arr = cell["log_jcp"]
        method_scope = "substructure_aggregate_median"

    beta_H_samples_base = bootstrap_draws(beta_h_pool_arr, rng, N_BOOT)
    log_jcp_samples = bootstrap_draws(log_jcp_pool_arr, rng, N_BOOT)

    # Grid points
    t_grid = list(T_FIX) + [0.77 * tc_K]
    h_grid = list(H_GRID)

    rows = []
    for T_K in t_grid:
        for H_T in h_grid:
            refusal = None
            if hc2_anchor_type == "pending":
                refusal = "Hc2_unavailable"
            elif T_K >= tc_K:
                refusal = "T_above_Tc"
            elif hc2_T is not None and not np.isnan(hc2_T) and H_T >= hc2_T:
                refusal = "H_above_Hc2"

            if refusal in ("Hc2_unavailable",):
                # T-axis-only: keep prediction but no H-axis contribution
                median, lo, hi = form3_predict_bootstrap(
                    T_K=T_K, H_T=H_T, Tc=tc_K, Hc2=None,
                    log_jcp_anchor_samples=log_jcp_samples,
                    beta_T_samples=beta_T_samples,
                    beta_H_samples=None,
                )
                env_dex = np.nan
            elif refusal in ("T_above_Tc", "H_above_Hc2"):
                median, lo, hi = (np.nan, np.nan, np.nan)
                env_dex = np.nan
            else:
                # AlB2 c_parent: ±20% perturbation envelope on Hc2
                if hc2_anchor_type == "c_parent" and sub == "conventional_AlB2":
                    medians_env = []
                    los_env = []
                    his_env = []
                    for f in PARENT_HC2_PERTURB_FACTORS:
                        m, l, h = form3_predict_bootstrap(
                            T_K=T_K, H_T=H_T, Tc=tc_K, Hc2=hc2_T * f,
                            log_jcp_anchor_samples=log_jcp_samples,
                            beta_T_samples=beta_T_samples,
                            beta_H_samples=beta_H_samples_base,
                        )
                        medians_env.append(m)
                        los_env.append(l)
                        his_env.append(h)
                    median = float(np.median(medians_env))
                    lo = float(np.min(los_env))
                    hi = float(np.max(his_env))
                    env_dex = float(np.nanmax(medians_env) - np.nanmin(medians_env))
                else:
                    median, lo, hi = form3_predict_bootstrap(
                        T_K=T_K, H_T=H_T, Tc=tc_K, Hc2=hc2_T,
                        log_jcp_anchor_samples=log_jcp_samples,
                        beta_T_samples=beta_T_samples,
                        beta_H_samples=beta_H_samples_base,
                    )
                    env_dex = np.nan

            rows.append({
                "compound_formula": row["compound_formula"],
                "substructure": sub,
                "MP_id": row.get("MP_id"),
                "paper_id": row.get("paper_id"),
                "source_provenance": "A1" if row.get("source_bucket") == "A1" else "A2",
                "Tc_anchor_K": tc_K,
                "Tc_provenance_tier": ("3DSC_MP" if row.get("source_bucket") == "A1"
                                       else ("extraction_csv" if not np.isnan(tc_K) else "substructure_default")),
                "Hc2_T_anchor": hc2_T if hc2_T is not None else np.nan,
                "Hc2_anchor_type": hc2_anchor_type,
                "Hc2_deviation_flag": hc2_deviation_flag if hc2_deviation_flag else "",
                "Hc2_source": hc2_source if hc2_source else "",
                "sample_form_commitment": sample_form_commitment if sample_form_commitment else "",
                "predictor_method_scope": method_scope,
                "T_K": T_K,
                "H_T": H_T,
                "predicted_log_Jc": median,
                "predicted_log_Jc_lower_95": lo,
                "predicted_log_Jc_upper_95": hi,
                "parent_match_uncertainty_envelope_dex": env_dex,
                "bootstrap_iterations": N_BOOT,
                "refusal_flag": refusal if refusal else "",
            })

    # Non-monotonicity check at each H (Form 3 with β_T > 0 should monotonically
    # decrease in T; flag if predicted Jc(T) is non-monotonic at same H).
    rows_by_h = {}
    for r in rows:
        rows_by_h.setdefault(r["H_T"], []).append(r)
    for h_val, h_rows in rows_by_h.items():
        # Sort by T_K
        h_rows_sorted = sorted(h_rows, key=lambda x: x["T_K"])
        log_jc_seq = [r["predicted_log_Jc"] for r in h_rows_sorted]
        if all(not np.isnan(v) for v in log_jc_seq) and len(log_jc_seq) >= 2:
            # Check strictly decreasing
            diffs = np.diff(log_jc_seq)
            if not np.all(diffs <= 1e-9):
                for r in h_rows_sorted:
                    if not r["refusal_flag"]:
                        r["refusal_flag"] = "non_monotonic_Jc_T"

    return rows


# ----------------------------------------------------------------------------
# Top-N selection

def select_top5(preds: pd.DataFrame, ref_T: float = 4.2, ref_H: float = 1.0) -> pd.DataFrame:
    """Return top-5 candidates per substructure ranked by predicted log Jc at
    the reference grid point. Deduplicates by compound_formula so the table
    surfaces 5 distinct compounds per substructure (multiple A2 rows of the
    same compound are collapsed to the highest-ranked occurrence)."""
    ref = preds[(preds["T_K"] == ref_T) & (preds["H_T"] == ref_H)].copy()
    # Exclude refused
    ref = ref[ref["refusal_flag"] == ""].copy()
    out = []
    for sub in POPULATED:
        sub_df = (
            ref[ref["substructure"] == sub]
            .sort_values("predicted_log_Jc", ascending=False)
            .drop_duplicates(subset=["compound_formula"], keep="first")
            .head(5)
            .reset_index(drop=True)
        )
        for i, r in sub_df.iterrows():
            out.append({
                "substructure": sub,
                "rank": i + 1,
                "compound_formula": r["compound_formula"],
                "MP_id": r["MP_id"],
                "predicted_log_Jc_at_4p2K_1T": r["predicted_log_Jc"],
                "CI_95_lower": r["predicted_log_Jc_lower_95"],
                "CI_95_upper": r["predicted_log_Jc_upper_95"],
                "sample_form_commitment": r["sample_form_commitment"],
                "Hc2_anchor_type": r["Hc2_anchor_type"],
                "Hc2_deviation_flag": r["Hc2_deviation_flag"],
                "parent_match_uncertainty_envelope_dex":
                    r["parent_match_uncertainty_envelope_dex"],
            })
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------
# Outcome resolution

def resolve_outcomes(preds: pd.DataFrame) -> dict:
    """Compute σ₁/σ₂ + τ₁/τ₂ + refusal-rate diagnostics."""
    non_ref = preds[preds["refusal_flag"] == ""].copy()
    non_ref["ci_width"] = (
        non_ref["predicted_log_Jc_upper_95"] - non_ref["predicted_log_Jc_lower_95"]
    )
    median_ci = float(non_ref["ci_width"].median())

    sigma_outcome = "sigma_1" if median_ci < 1.5 else "sigma_2"

    # Top quartile at (4.2 K, 1 T) reference
    ref = preds[(preds["T_K"] == 4.2) & (preds["H_T"] == 1.0)
                & (preds["refusal_flag"] == "")].copy()
    if len(ref) > 0:
        q75 = ref["predicted_log_Jc"].quantile(0.75)
        topq = ref[ref["predicted_log_Jc"] >= q75]
        topq_dist = topq["substructure"].value_counts(normalize=True).to_dict()
        topq_counts = topq["substructure"].value_counts().to_dict()
    else:
        topq_dist = {}
        topq_counts = {}

    if topq_dist:
        max_share = max(topq_dist.values())
        min_share = min(topq_dist.get(s, 0.0) for s in POPULATED)
        if max_share > 0.60:
            tau_outcome = "tau_2"
        elif min_share >= 0.15:
            tau_outcome = "tau_1"
        else:
            tau_outcome = "tau_mixed"
    else:
        tau_outcome = "tau_undefined"

    # Refusal rates
    refusal_counts = preds[preds["refusal_flag"] != ""]["refusal_flag"].value_counts().to_dict()
    n_total_tuples = len(preds)
    n_refused = (preds["refusal_flag"] != "").sum()
    cand_with_any_nonmono = (
        preds[preds["refusal_flag"] == "non_monotonic_Jc_T"]["compound_formula"].nunique()
    )
    n_total_cands = preds["compound_formula"].nunique()

    return {
        "sigma_outcome": sigma_outcome,
        "median_ci_width_dex": median_ci,
        "tau_outcome": tau_outcome,
        "topq_share": topq_dist,
        "topq_counts": topq_counts,
        "refusal_counts": refusal_counts,
        "n_total_tuples": n_total_tuples,
        "n_refused_tuples": int(n_refused),
        "n_total_unique_candidates": n_total_cands,
        "n_candidates_with_nonmono": cand_with_any_nonmono,
        "fraction_candidates_nonmono": cand_with_any_nonmono / max(n_total_cands, 1),
    }


# ----------------------------------------------------------------------------
# Main

def main():
    t0 = time.time()
    rng = np.random.default_rng(RNG_SEED)
    print("=" * 78)
    print("Phase 3 p57 — De Novo Jc(T, H) Prediction Dispatch")
    print("=" * 78)
    print(f"  Bootstrap N: {N_BOOT}; seed: {RNG_SEED}")
    print(f"  Target grid: T ∈ [4.2 K, 20 K, 0.77·Tc]; H ∈ [0.1, 1, 5 T]")
    print(f"  Anchor reference: (T_ref={T_REF} K, H_ref={H_REF} T)")
    print()

    # 1. Candidates
    print("[1/6] Loading candidate list ...")
    cands = load_candidates()
    print(f"      n_total = {len(cands)}; per substructure:")
    print(cands.groupby(['substructure', 'source_bucket']).size().to_string())
    print()

    # 2. A2 Tc anchors
    print("[2/6] Building A2 Tc anchor index ...")
    a2_tc_idx = build_a2_tc_index()
    print(f"      {len(a2_tc_idx)} (paper, compound) → Tc entries cached")
    print()

    # 3. Hc2 anchor lookup
    print("[3/6] Building Hc2 anchor indexes (S1/S3/S5_lit/S5_maki) ...")
    p56b, exact_idx, parent_idx = build_hc2_indexes()
    print(f"      exact-key index size: {len(exact_idx)}; "
          f"parent-key index size: {len(parent_idx)}")
    print()

    # 4. Fit pools
    print("[4/6] Building β_T / β_H / log_Jc_partial pools ...")
    beta_t_pool = build_beta_t_pool()
    print(f"      β_T pool sizes: " + ", ".join(
        f"{k}={len(v)}" for k, v in beta_t_pool.items()
    ))
    beta_h_agg, beta_h_cond = build_beta_h_log_jcp_pool()
    print(f"      β_H + log_Jc_partial substructure-aggregate sizes: " + ", ".join(
        f"{k}={v['n']}" for k, v in beta_h_agg.items()
    ))
    print(f"      sample-form-conditional cells: {len(beta_h_cond)}")
    print()

    # 5. Per-candidate prediction
    print("[5/6] Running per-candidate Form 3 prediction with bootstrap ...")
    all_pred_rows = []
    refused_candidate_counts = {sub: 0 for sub in POPULATED}
    hc2_pending_compounds = {sub: [] for sub in POPULATED}

    for i, row in cands.iterrows():
        sub = row["substructure"]
        compound = row["compound_formula"]
        # Tc anchor
        if row["source_bucket"] == "A1":
            tc_K = float(row["Tc_K"])
            tc_prov_tier = "3DSC_MP"
        else:
            tc_K = a2_tc_idx.get((row["paper_id"], compound))
            if tc_K is None or np.isnan(tc_K):
                tc_K = TC_DEFAULT_BY_SUB[sub]
                tc_prov_tier = "substructure_default"
            else:
                tc_prov_tier = "extraction_csv"

        # Hc2 anchor (use p56b lookup, but enforce 1111-exclusion already applied)
        match_type, hc2_val, hc2_src = p56b.lookup_hc2(
            compound, row.get("MP_id"), exact_idx, parent_idx
        )

        if match_type == "none":
            hc2_anchor_type = "pending"
            hc2_dev_flag = None
            hc2_T = None
        elif match_type == "a_exact":
            hc2_anchor_type = "exact"
            hc2_dev_flag = None
            hc2_T = hc2_val
        else:  # c_parent
            hc2_anchor_type = "c_parent"
            hc2_dev_flag = "±20-50%"
            hc2_T = hc2_val

        if hc2_anchor_type == "pending":
            hc2_pending_compounds[sub].append(compound)

        # Sample-form commitment per the three-regime-aware rule. Outcome A
        # (chalc_11) uniform-commits to single_crystal across A1 + A2.
        # Outcome B (pn-122) defaults to single_crystal for A1 and inherits
        # source-paper sample_form from canonical Cohort B for A2 candidates.
        # Outcome C (AlB2) commits to substructure-aggregate (None).
        if sub == "iron_pnictide_122":
            sf_commit = DEFAULT_SAMPLE_FORM[sub]  # A1 default = single_crystal
            if row["source_bucket"] == "A2" and row.get("paper_id"):
                df_b = pd.read_csv(CANON_B)
                m = df_b[df_b["arxiv_id"] == row["paper_id"]]
                if len(m) > 0 and not pd.isna(m["sample_form"].iloc[0]):
                    sf_commit = m["sample_form"].iloc[0]
        elif sub == "conventional_AlB2":
            sf_commit = DEFAULT_SAMPLE_FORM[sub]  # default None → aggregate
            if row["source_bucket"] == "A2" and row.get("paper_id"):
                df_b = pd.read_csv(CANON_B)
                # A2 candidate paper_id has the "_VISION_PASS_LONG" suffix
                # (csv_path.stem in build_a2_tc_index); CANON_B's arxiv_id
                # does not — strip the suffix for the lookup.
                lookup_key = str(row["paper_id"]).removesuffix("_VISION_PASS_LONG")
                m = df_b[df_b["arxiv_id"] == lookup_key]
                if len(m) > 0 and not pd.isna(m["sample_form"].iloc[0]):
                    src_sf = m["sample_form"].iloc[0]
                    if src_sf in ENGINEERED_FORMS:
                        sf_commit = src_sf
        else:
            sf_commit = DEFAULT_SAMPLE_FORM[sub]

        cand_rows = predict_candidate(
            row=row,
            tc_K=tc_K,
            hc2_T=hc2_T,
            hc2_anchor_type=hc2_anchor_type,
            hc2_source=hc2_src,
            hc2_deviation_flag=hc2_dev_flag,
            sample_form_commitment=sf_commit,
            beta_t_pool=beta_t_pool,
            beta_h_agg_pool=beta_h_agg,
            beta_h_cond_pool=beta_h_cond,
            rng=rng,
        )
        # Override Tc_provenance_tier to specific value
        for r in cand_rows:
            r["Tc_provenance_tier"] = tc_prov_tier
        all_pred_rows.extend(cand_rows)

        if (i + 1) % 25 == 0 or (i + 1) == len(cands):
            elapsed = time.time() - t0
            print(f"      {i + 1}/{len(cands)} candidates processed "
                  f"({elapsed:.1f}s elapsed)")

    preds_df = pd.DataFrame(all_pred_rows)
    print(f"      total prediction tuples: {len(preds_df)}")
    print()

    # 6. Outcomes + outputs
    print("[6/6] Resolving pre-registered outcomes + writing outputs ...")
    outcomes = resolve_outcomes(preds_df)
    print(f"      σ outcome: {outcomes['sigma_outcome']} "
          f"(median CI width = {outcomes['median_ci_width_dex']:.3f} dex)")
    print(f"      τ outcome: {outcomes['tau_outcome']} "
          f"(top-quartile share: {outcomes['topq_share']})")
    print(f"      refusal counts: {outcomes['refusal_counts']}")
    print(f"      fraction candidates with non-monotonic flag: "
          f"{outcomes['fraction_candidates_nonmono']*100:.1f}%")

    preds_df.to_csv(OUT_PREDICTIONS, index=False)
    print(f"      wrote {OUT_PREDICTIONS} ({OUT_PREDICTIONS.stat().st_size} bytes)")

    top5_df = select_top5(preds_df)
    top5_df.to_csv(OUT_TOP5, index=False)
    print(f"      wrote {OUT_TOP5} ({OUT_TOP5.stat().st_size} bytes)")

    # Dispatch report
    write_report(preds_df, top5_df, outcomes, hc2_pending_compounds, t0)
    print(f"      wrote {OUT_REPORT} ({OUT_REPORT.stat().st_size} bytes)")
    print()

    elapsed = time.time() - t0
    print("=" * 78)
    print(f"Dispatch successful: yes")
    print(f"Pre-registered outcomes resolved: yes "
          f"({outcomes['sigma_outcome']} + {outcomes['tau_outcome']})")
    print(f"Top-5 Table N data ready: yes (file: {OUT_TOP5})")
    print(f"Total elapsed: {elapsed:.1f}s; total candidates: {preds_df['compound_formula'].nunique()}; "
          f"total tuples: {len(preds_df)}; refused: {outcomes['n_refused_tuples']}")
    print(f"Median CI width across non-refused: {outcomes['median_ci_width_dex']:.3f} dex")
    print("=" * 78)
    return 0


def write_report(preds, top5, outcomes, hc2_pending, t_start):
    """Build phase_3_p57_dispatch_report.md."""
    elapsed = time.time() - t_start
    now = datetime.now(timezone.utc).isoformat()
    md = []
    md.append("# Phase 3 p57 — De Novo Jc(T, H) Prediction Dispatch Report\n")
    md.append(f"**Date**: 2026-05-11  \n")
    md.append(f"**Generation timestamp**: {now}  \n")
    md.append(f"**Cost**: $0 (offline file I/O + local computation; no API calls)  \n")
    md.append(f"**Hard exclusion**: iron_pnictide_1111 enforced at candidate-list + Hc2-index + fit-pool layers.\n\n")
    md.append("---\n\n")

    # §1
    md.append("## §1 — Dispatch summary\n\n")
    md.append(f"- Total candidates: {preds['compound_formula'].nunique()} "
              f"(at 239 dispatched-row scope)\n")
    md.append(f"- Total prediction tuples (candidate × grid point): {len(preds)}\n")
    md.append(f"- Bootstrap iterations: {N_BOOT} (seed = {RNG_SEED})\n")
    md.append(f"- Refused tuples: {outcomes['n_refused_tuples']}\n")
    md.append(f"- Refusal breakdown:\n")
    for cond, n in outcomes["refusal_counts"].items():
        md.append(f"  - `{cond}`: {n}\n")
    md.append(f"- Dispatch duration: {elapsed:.1f} s\n")
    md.append(f"- Cost: $0\n\n")
    md.append("---\n\n")

    # §2
    md.append("## §2 — Pre-registered outcome resolutions\n\n")
    md.append(f"### σ outcome: **{outcomes['sigma_outcome']}**\n\n")
    md.append(f"Median bootstrap CI width across non-refused predictions: "
              f"**{outcomes['median_ci_width_dex']:.3f} dex log Jc**.  \n")
    if outcomes["sigma_outcome"] == "sigma_1":
        md.append("Triggered σ₁ (< 1.5 dex): predictions are screening-grade interpretable.\n\n")
    else:
        md.append("Triggered σ₂ (≥ 1.5 dex): ranking is caveated as broad-uncertainty.\n\n")

    md.append(f"### τ outcome: **{outcomes['tau_outcome']}**\n\n")
    md.append("Top-quartile substructure distribution at (T = 4.2 K, H = 1 T):\n\n")
    md.append("| Substructure | Top-quartile count | Top-quartile share |\n|---|---:|---:|\n")
    for sub in POPULATED:
        c = outcomes["topq_counts"].get(sub, 0)
        s = outcomes["topq_share"].get(sub, 0.0)
        md.append(f"| {sub} | {c} | {s*100:.1f}% |\n")
    md.append("\n")
    if outcomes["tau_outcome"] == "tau_1":
        md.append("Triggered τ₁: substructure-balanced top-quartile "
                  "(all populated substructures ≥ 15%).\n\n")
    elif outcomes["tau_outcome"] == "tau_2":
        md.append("Triggered τ₂: substructure-imbalanced top-quartile "
                  "(one substructure > 60%). Reporting should be "
                  "substructure-conditional rather than aggregate-ranked.\n\n")
    else:
        md.append("Mixed: no substructure exceeds 60% but min share is < 15%; "
                  "report at substructure-conditional scope.\n\n")

    md.append(f"### Refusal-rate diagnostic\n\n")
    md.append(f"- Fraction of unique candidates with any non-monotonic Jc(T) flag: "
              f"{outcomes['fraction_candidates_nonmono']*100:.1f}% ")
    if outcomes['fraction_candidates_nonmono'] < 0.10:
        md.append("(< 10% threshold; screening-grade scope is primary deliverable).\n")
    else:
        md.append("(≥ 10% threshold; surface as methodology caveat).\n")
    md.append("- Tuple-level refusal breakdown:\n")
    for cond, n in outcomes["refusal_counts"].items():
        md.append(f"  - `{cond}`: {n} / {len(preds)} tuples "
                  f"({n / len(preds) * 100:.1f}%)\n")
    md.append("\n---\n\n")

    # §3 per-substructure
    md.append("## §3 — Per-substructure prediction-set statistics\n\n")
    md.append("Computed at reference grid point (T = 4.2 K, H = 1 T) "
              "across non-refused predictions.\n\n")
    md.append("| Substructure | n cand | n refused (tuples) | "
              "median log Jc | 5%–95% range | "
              "n full β_T+β_H | n T-axis-only |\n"
              "|---|---:|---:|---:|---|---:|---:|\n")
    for sub in POPULATED:
        sub_pred = preds[preds["substructure"] == sub]
        sub_ref = sub_pred[(sub_pred["T_K"] == 4.2) & (sub_pred["H_T"] == 1.0)
                           & (sub_pred["refusal_flag"] == "")]
        n_cand = sub_pred["compound_formula"].nunique()
        n_ref = (sub_pred["refusal_flag"] != "").sum()
        if len(sub_ref) > 0:
            med = sub_ref["predicted_log_Jc"].median()
            p5 = sub_ref["predicted_log_Jc"].quantile(0.05)
            p95 = sub_ref["predicted_log_Jc"].quantile(0.95)
        else:
            med = p5 = p95 = np.nan
        n_full = (sub_pred["refusal_flag"] == "").sum()
        n_tonly = (sub_pred["refusal_flag"] == "Hc2_unavailable").sum()
        md.append(f"| {sub} | {n_cand} | {n_ref} | "
                  f"{med:.3f} | [{p5:.3f}, {p95:.3f}] | "
                  f"{n_full} | {n_tonly} |\n")
    md.append("\n---\n\n")

    # §4 top-5 table
    md.append("## §4 — Top 5 per substructure (preview for §6.3 Table N)\n\n")
    md.append("Reference grid point: T = 4.2 K, H = 1 T. Ranked by predicted log Jc.\n\n")
    md.append("| Substructure | Rank | Compound | Predicted log Jc [A/cm²] | "
              "95% CI | Sample-form commitment | Hc2 anchor | "
              "Envelope (dex) |\n"
              "|---|---:|---|---:|---|---|---|---:|\n")
    for _, r in top5.iterrows():
        env = (f"{r['parent_match_uncertainty_envelope_dex']:.3f}"
               if not pd.isna(r["parent_match_uncertainty_envelope_dex"])
               else "—")
        sfc = r["sample_form_commitment"] if r["sample_form_commitment"] else "(substructure-aggregate)"
        anchor_label = r["Hc2_anchor_type"]
        if r["Hc2_deviation_flag"]:
            anchor_label += f" ({r['Hc2_deviation_flag']})"
        md.append(f"| {r['substructure']} | {r['rank']} | "
                  f"{r['compound_formula']} | "
                  f"{r['predicted_log_Jc_at_4p2K_1T']:.3f} | "
                  f"[{r['CI_95_lower']:.3f}, {r['CI_95_upper']:.3f}] | "
                  f"{sfc} | {anchor_label} | {env} |\n")
    md.append("\n---\n\n")

    # §5 caveats
    md.append("## §5 — Methodology caveats\n\n")
    # AlB2 envelope width statistic
    alb2 = preds[(preds["substructure"] == "conventional_AlB2")
                 & (preds["Hc2_anchor_type"] == "c_parent")
                 & (preds["refusal_flag"] == "")]
    if len(alb2) > 0:
        env_vals = alb2["parent_match_uncertainty_envelope_dex"].dropna()
        if len(env_vals) > 0:
            md.append(f"### conventional_AlB2 parent-match envelope "
                      f"(n = {alb2['compound_formula'].nunique()} candidates inheriting MgB2 Hc2)\n\n")
            md.append(f"- Median per-candidate envelope width: "
                      f"{env_vals.median():.3f} dex log Jc\n")
            md.append(f"- 5%–95% envelope range: "
                      f"[{env_vals.quantile(0.05):.3f}, "
                      f"{env_vals.quantile(0.95):.3f}] dex\n")
            md.append(f"- Hc2 perturbation factors applied: "
                      f"{PARENT_HC2_PERTURB_FACTORS}\n")
            md.append(f"- ±20–50% deviation flag retained in metadata for "
                      f"every parent-match candidate.\n\n")

    # 122 cation-variants pending
    md.append("### iron_pnictide_122 cation-variant unmatched\n\n")
    pn122 = hc2_pending.get("iron_pnictide_122", [])
    md.append(f"- Count: {len(pn122)} candidates with Hc2_anchor_type = "
              f"`pending` (β_T-axis-only predictions).\n")
    if pn122:
        md.append(f"- Provenance: Sr/Ca/Eu/Rb/Cs-122 cation variants not "
                  f"present in S1/S3/S5 sources at exact or parent scope.\n")
        md.append("- Top 10 (alphabetical):\n")
        for c in sorted(set(pn122))[:10]:
            md.append(f"  - {c}\n")
        md.append("\n")

    # AlB2 exotic diborides pending
    alb2_pending = hc2_pending.get("conventional_AlB2", [])
    if alb2_pending:
        md.append("### conventional_AlB2 exotic diboride unmatched\n\n")
        md.append(f"- Count: {len(alb2_pending)} candidates (ZrB₂, NbB₂, OsB₂ "
                  f"variants) with Hc2_anchor_type = `pending`.\n")
        md.append("- Top 10 (alphabetical):\n")
        for c in sorted(set(alb2_pending))[:10]:
            md.append(f"  - {c}\n")
        md.append("\n")

    # Non-monotonic Jc(T)
    md.append("### Non-monotonic Jc(T) refusal\n\n")
    nonmono = preds[preds["refusal_flag"] == "non_monotonic_Jc_T"]
    md.append(f"- Affected unique compounds: {outcomes['n_candidates_with_nonmono']}\n")
    md.append(f"- Affected tuples: {len(nonmono)}\n")
    md.append(f"- Fraction of total candidates: "
              f"{outcomes['fraction_candidates_nonmono']*100:.1f}%\n\n")
    md.append("---\n\n")

    # §6 scope
    md.append("## §6 — Scope statement\n\n")
    md.append("Predictions are committed at substructure-aggregate Stage 3 scope. "
              "log Jc partial anchor is the substructure (× sample_form where Outcome A "
              "or B applies) cell median from canonical Cohort B v2 per-paper Form 3 "
              "fits. β_T and β_H pools are resampled with replacement at N = "
              f"{N_BOOT} bootstrap iterations (seed = {RNG_SEED}; matches Path δ + "
              f"Path 19-AC reproducibility).\n\n")
    md.append("iron_pnictide_1111 is hard-excluded per §4.3 of the manuscript "
              "(Substep D nu-2 compound-LOO MAE 5.13 dex β_H at expanded scope). "
              "The 1111 exclusion is enforced at three layers: candidate-list, "
              "Hc2-index, and β_H/log_Jc_partial fit pool.\n\n")
    md.append(f"Default target grid: T ∈ {{4.2 K, 20 K, 0.77·Tc}}; "
              f"H ∈ {{0.1, 1, 5 T}}. Advisor override of these defaults is "
              "anticipated as a separate dispatch; the pipeline is parameterised "
              "at the grid level and re-runs cheaply against any user-specified "
              "(T, H) point set.\n\n")
    md.append("---\n\n")

    # Footer
    md.append("## Metadata footer\n\n")
    md.append(f"- Outputs: `{OUT_PREDICTIONS.name}`, `{OUT_TOP5.name}`, "
              f"`{OUT_REPORT.name}`\n")
    # Count unique candidates: (compound, MP_id, paper_id) tuple covers both A1
    # (MP_id present, paper_id None) and A2 (paper_id present) rows. NaN must be
    # filled to ensure groupby treats missing keys consistently.
    cand_key = preds[["compound_formula", "MP_id", "paper_id"]].fillna("__none__")
    n_unique_rows = cand_key.drop_duplicates().shape[0]
    md.append(f"- Unique candidate rows (compound × MP_id × paper_id): "
              f"{n_unique_rows} (dispatched-row scope: 239)\n")
    md.append(f"- Bootstrap N: {N_BOOT}; seed: {RNG_SEED}\n")
    md.append(f"- Generation timestamp: {now}\n")
    md.append(f"- Cost: $0 (offline file I/O + local computation; no API calls)\n")

    OUT_REPORT.write_text("".join(md))


if __name__ == "__main__":
    sys.exit(main())
