"""Path 3-p56: De novo candidate list at 3 testable substructures.

Hard exclusion: iron_pnictide_1111 per Substep D nu-2 (compound-LOO MAE 5.13 dex β_H
at expanded scope; substructure-conditional methodology applicability fails).

A1 source: 3DSC_MP.csv (5,773 superconductors with Tc + MP_id + spacegroup; offline
file at /Users/prachetpoddar/Documents/SuperconductorWorkflow/3DSC_MP.csv;
generated 2022-06-20 by 3DSC project; combines SuperCon + Materials Project records).
A2 source: data_agent2/v3_2_2B_extension/ vision-pass extraction CSVs cross-referenced
against canonical fits (phase_3_form3_fits_partial_cohortB_v2.csv).

NOTE: Materials Project does NOT store Tc or Hc2 (DFT-only properties). Hc2 lookup is
NOT directly available via existing infrastructure — flagged at every entry as
"literature lookup required."

Output: phase_3_p56_de_novo_candidate_list.md
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

import pandas as pd
import numpy as np

REPO = Path("/Users/prachetpoddar/Documents/SuperconductorWorkflow")
HERE = Path(__file__).resolve().parent
PREP = (HERE.parent / "data") if (HERE.parent / "data").is_dir() else REPO / "kappa_pipeline/analysis/v3_2_9_path_2_prep"
EXT_B_DIR = REPO / "data_agent2" / "v3_2_2B_extension"

DSC = REPO / "3DSC_MP.csv"
CANONICAL_B = PREP / "phase_3_form3_fits_partial_cohortB_v2.csv"
CANONICAL_A = PREP / "phase_3_p44_post_UCLA_beta_T_fits.csv"
H1B = PREP / "h1b_per_paper_form3_fits.csv"
NEW_FITS_AC = PREP / "phase_3_p54_substep_C_new_form3_fits.csv"

OUT_MD = PREP / "phase_3_p56_de_novo_candidate_list.md"


def load_3dsc():
    df = pd.read_csv(DSC, skiprows=1, low_memory=False)
    return df


def filter_substructure(df, sub):
    """Apply substructure-specific filter on 3DSC."""
    f = df["formula_sc"].astype(str)
    sg = df["spacegroup_2"].astype(str)
    if sub == "iron_chalcogenide_11":
        # P4/nmm tetragonal; FeX with X = Se/Te/S; no As, no O (excludes pnictides + 1111)
        return df[
            f.str.contains("Fe", na=False)
            & f.str.contains("Se|Te", na=False, regex=True)
            & ~f.str.contains("As", na=False)
            & ~f.str.contains("O", na=False)
            & sg.str.contains("P 4/n m m", na=False)
        ].copy()
    elif sub == "iron_pnictide_122":
        # I4/mmm tetragonal; AFe2As2 family
        # Exclude 1111 (which has FeAsO patterns) and chalcogenides
        return df[
            f.str.contains("Fe", na=False)
            & f.str.contains("As", na=False)
            & ~f.str.contains("O", na=False)  # excludes 1111 family
            & sg.str.contains("I 4/m m m", na=False)
        ].copy()
    elif sub == "conventional_AlB2":
        # P6/mmm hexagonal; B2 stoichiometry (AlB2-type diborides)
        return df[
            f.str.contains("B2", na=False)
            & sg.str.contains("P 6/m m m", na=False)
        ].copy()
    return df.iloc[0:0].copy()


def canonical_compound_key(c):
    """Canonical key for cross-cohort matching."""
    if c is None or pd.isna(c):
        return None
    return str(c).replace(" ", "").replace("_", "").lower()


def load_canonical_fit_compounds():
    """Load all compounds present in canonical Cohort A + Cohort B fits."""
    canon_B = pd.read_csv(CANONICAL_B)
    canon_A = pd.read_csv(CANONICAL_A)
    h1b = pd.read_csv(H1B)
    new_AC = pd.read_csv(NEW_FITS_AC)

    keys = set()
    for c in canon_B["compound_formula"].dropna().unique():
        keys.add(canonical_compound_key(c))
    for c in canon_A["compound_formula"].dropna().unique():
        keys.add(canonical_compound_key(c))
    for c in h1b["compound"].dropna().unique():
        keys.add(canonical_compound_key(c))
    for c in new_AC["compound_formula"].dropna().unique():
        keys.add(canonical_compound_key(c))
    return keys


def find_A2_candidates(canonical_keys):
    """Scan v3_2_2B_extension/ for compounds with extracted data but not in canonical fits.

    A2a: extracted but Form 3 fit failed (physicality != 'ok' OR ok != True)
    A2b: extracted but n_distinct H below MIN_N_H = 4 threshold
    """
    canon_B = pd.read_csv(CANONICAL_B)
    # Compute n_distinct per (paper × compound × T_fixed) directly from extraction CSVs
    A2_records = []
    for csv_path in EXT_B_DIR.glob("elsevier_*_VISION_PASS_LONG.csv"):
        try:
            df = pd.read_csv(csv_path)
        except Exception:
            continue
        if "primary_scan_direction" in df.columns:
            df = df[df["primary_scan_direction"] == "H"]
        for compound, grp in df.groupby("compound_formula", dropna=False):
            if not isinstance(compound, str) or pd.isna(compound):
                continue
            comp_key = canonical_compound_key(compound)
            # Inferred substructure for this compound
            sub = assign_substructure(compound)
            if sub not in {"iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"}:
                continue
            # Already in canonical fits?
            in_canon = comp_key in canonical_keys
            # Distinct T_fixed values
            T_vals = grp.get("temperature_K", pd.Series()).dropna().unique()
            for T in T_vals:
                sub_T = grp[grp["temperature_K"] == T]
                n_pts = len(sub_T)
                n_distinct_H = sub_T["field_T"].nunique() if "field_T" in sub_T.columns else 0
                if n_distinct_H < 4:
                    fail_reason = f"insufficient n_distinct_H={n_distinct_H} (< MIN_N_H=4)"
                    bucket = "A2b"
                else:
                    # Check if this paper × compound × T is in canonical fits
                    paper_id = sub_T["paper_id"].iloc[0] if "paper_id" in sub_T.columns else csv_path.stem
                    canon_match = canon_B[(canon_B["arxiv_id"] == paper_id)
                                          & (canon_B["compound_formula"] == compound)
                                          & (canon_B["fixed_axis_value"] == T)]
                    if len(canon_match) == 0:
                        fail_reason = "extracted but not in canonical fits (likely physicality-failed at fit)"
                        bucket = "A2a"
                    elif (canon_match["physicality"] != "ok").any():
                        fail_reason = f"physicality={canon_match['physicality'].iloc[0]}"
                        bucket = "A2a"
                    else:
                        # In canonical fits as ok — skip (already covered)
                        continue

                sample_form_val = (sub_T["sample_form"].iloc[0]
                                    if "sample_form" in sub_T.columns else "unknown")
                A2_records.append({
                    "paper_id": csv_path.stem,
                    "compound_formula": compound,
                    "substructure": sub,
                    "sample_form": sample_form_val,
                    "T_fixed_K": T,
                    "fail_reason": fail_reason,
                    "n_data_points_available": n_pts,
                    "n_distinct_H": n_distinct_H,
                    "bucket": bucket,
                    "in_canonical_compound_keys": in_canon,
                    "threshold_relaxation_would_yield_fit":
                        (n_pts >= 3 and n_distinct_H >= 3 and bucket == "A2b"),
                })
    return pd.DataFrame(A2_records)


def assign_substructure(c):
    c = (c or "")
    if "MgB2" in c or ("B2" in c and "Mg" in c):
        return "conventional_AlB2"
    if ("FeTe" in c or "FeSe" in c) and "FeAs" not in c and "O" not in c:
        return "iron_chalcogenide_11"
    if "FeAsO" in c or "Fe2As2O" in c:
        return "iron_pnictide_1111"
    if "Fe2As2" in c or "BaFe" in c or "(Fe" in c:
        return "iron_pnictide_122"
    return "other"


def main():
    print("Path 3-p56: de novo candidate list build")
    print()

    # ===== Load 3DSC =====
    dsc = load_3dsc()
    print(f"3DSC loaded: {len(dsc)} superconductor records")
    print()

    # ===== Load canonical fit compounds for filter =====
    canonical_keys = load_canonical_fit_compounds()
    print(f"Canonical fit compounds (keys): {len(canonical_keys)}")
    print()

    # ===== A1 per substructure =====
    A1_results = {}
    print("=== A1 — Materials Project / 3DSC query ===")
    for sub in ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]:
        raw = filter_substructure(dsc, sub)
        n_total = len(raw)
        # Filter known superconductor (Tc > 0)
        sc = raw[raw["tc"] > 0].copy()
        n_known_sc = len(sc)
        # Hc2 estimate: NOT available in 3DSC
        sc["literature_Hc2_T"] = None
        sc["literature_Hc2_reference"] = "literature lookup required"
        n_has_hc2 = 0  # no Hc2 in source
        # Not in canonical fits?
        sc["compound_canonical_key"] = sc["formula_sc"].apply(canonical_compound_key)
        sc["in_canonical_fits_already"] = sc["compound_canonical_key"].isin(canonical_keys)
        not_canon = sc[~sc["in_canonical_fits_already"]].copy()
        n_not_canon = len(not_canon)
        # In-scope = passes all filters above (Hc2 is flagged-required, not filtered)
        not_canon["in_scope_flag"] = True
        n_in_scope = len(not_canon)
        # Add literature Tc reference (DOI from 3DSC)
        not_canon["literature_Tc_reference"] = not_canon["doi_2"].fillna("").apply(
            lambda d: f"DOI:{d}" if d and not pd.isna(d) else "via 3DSC SuperCon dataset (Stanev 2018)")

        A1_results[sub] = {
            "n_total": n_total, "n_known_sc": n_known_sc, "n_has_hc2": n_has_hc2,
            "n_not_canon": n_not_canon, "n_in_scope": n_in_scope,
            "candidates": not_canon,
        }
        print(f"\n  {sub}:")
        print(f"    n_total (raw 3DSC hits at substructure filter): {n_total}")
        print(f"    n_known_superconductor (Tc > 0): {n_known_sc}")
        print(f"    n_has_Hc2_estimate (in 3DSC): {n_has_hc2} (3DSC does not store Hc2)")
        print(f"    n_not_in_canonical_fits: {n_not_canon}")
        print(f"    n_in_scope: {n_in_scope}")
    print()

    # ===== A2 candidates =====
    print("=== A2 — Cohort B extraction CSVs but not in canonical fits ===")
    A2 = find_A2_candidates(canonical_keys)
    print(f"  Total A2 records across 3 substructures: {len(A2)}")
    if len(A2) > 0:
        print(A2.groupby(["substructure", "bucket"]).size().to_string())
    print()

    # ===== Combined per substructure =====
    print("=== Combined in-scope per substructure ===")
    combined_counts = {}
    for sub in ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]:
        n_a1 = A1_results[sub]["n_in_scope"]
        n_a2 = len(A2[A2["substructure"] == sub]) if len(A2) > 0 else 0
        combined = n_a1 + n_a2
        combined_counts[sub] = {"A1": n_a1, "A2": n_a2, "combined": combined}
        print(f"  {sub}: A1={n_a1} + A2={n_a2} = {combined}")
    total_combined = sum(c["combined"] for c in combined_counts.values())
    print(f"\n  TOTAL combined in-scope: {total_combined}")
    rho = "rho-1 (n ≥ 30 sufficient)" if total_combined >= 30 else "rho-2 (n < 30 sparse)"
    print(f"  Pre-registered outcome: {rho}")
    print()

    # ===== Write MD =====
    write_markdown(A1_results, A2, combined_counts, total_combined, rho)
    print(f"Wrote {OUT_MD.name}")


def write_markdown(A1_results, A2, combined_counts, total_combined, rho_outcome):
    md = []
    timestamp = datetime.now(timezone.utc).isoformat()

    md.append("# Path 3-p56: De Novo Jc(T,H) Prediction Candidate List\n\n")
    md.append("**Date**: 2026-05-10\n")
    md.append(f"**Generation timestamp**: {timestamp}\n")
    md.append("**Cost**: $0 (offline 3DSC_MP.csv scan + local CSV cross-reference; no API calls)\n")
    md.append("**Hard exclusion**: iron_pnictide_1111 per Substep D nu-2 (compound-LOO MAE 5.129 dex β_H "
              "at expanded scope; substructure-conditional methodology applicability fails per Path 19-AC).\n\n")
    md.append("---\n\n")

    # ===== Methodology =====
    md.append("## §1 — Methodology\n\n")
    md.append("### A1 source: 3DSC_MP.csv (offline file)\n\n")
    md.append("3DSC_MP.csv at repository root (5,773 superconductor records; generated 2022-06-20 by the "
              "3DSC project from SuperCon + Materials Project cross-reference) is the canonical Tc + spacegroup "
              "+ MP_id source. Materials Project itself does NOT store experimental Tc or Hc2 (DFT-computed "
              "properties only); the existing `compound_extractor_mp.py` infrastructure fetches DFT properties "
              "(formation_energy, band_gap, density, magnetization) but NOT Tc/Hc2. Per dispatch hard constraint, "
              "Hc2 values are flagged at every entry as `literature lookup required` — not invented.\n\n")
    md.append("### A1 substructure filters\n\n")
    md.append("- **iron_chalcogenide_11**: spacegroup `P 4/n m m` (tetragonal) AND formula contains Fe AND "
              "(Se OR Te) AND NOT As AND NOT O. The NOT-As + NOT-O filter excludes pnictides + 1111 oxypnictides.\n")
    md.append("- **iron_pnictide_122**: spacegroup `I 4/m m m` (tetragonal) AND formula contains Fe AND As "
              "AND NOT O. The NOT-O filter excludes the 1111 oxypnictide family.\n")
    md.append("- **conventional_AlB2**: spacegroup `P 6/m m m` (hexagonal) AND formula contains B2 stoichiometry. "
              "Captures MgB2 + isostructural diborides.\n\n")

    md.append("### A1 filter pipeline\n\n")
    md.append("1. n_total per substructure (raw 3DSC hits at substructure filter)\n")
    md.append("2. n_known_superconductor (Tc > 0)\n")
    md.append("3. n_has_Hc2_estimate (Hc2 in 3DSC) — **N/A; 3DSC does not store Hc2 → 0 across all substructures**\n")
    md.append("4. n_not_in_canonical_fits (canonical key not in `phase_3_p44_post_UCLA_beta_T_fits.csv` ∪ "
              "`phase_3_form3_fits_partial_cohortB_v2.csv` ∪ `h1b_per_paper_form3_fits.csv` ∪ "
              "`phase_3_p54_substep_C_new_form3_fits.csv`)\n")
    md.append("5. n_in_scope (intersection — these are the A1 candidate list; Hc2 lookup deferred to gap analysis)\n\n")

    md.append("### A2 source: v3_2_2B_extension extraction CSVs not in canonical fits\n\n")
    md.append("Scan all `data_agent2/v3_2_2B_extension/elsevier_*_VISION_PASS_LONG.csv` for compound-formula × "
              "T_fixed groups; cross-reference against canonical fits CSV to identify extracted-but-not-fit candidates.\n\n")
    md.append("- **A2a**: extracted but Form 3 fit failed (physicality != 'ok' OR not present in canonical fits)\n")
    md.append("- **A2b**: extracted but n_distinct_H < MIN_N_H = 4 (insufficient distinct H-points for Form 3 fitting)\n\n")

    md.append("### Pre-registered exclusion\n\n")
    md.append("**iron_pnictide_1111 hard-excluded** at every layer of this dispatch. Per Substep D nu-2 outcome "
              "(2026-05-10): iron_pnictide_1111 compound-LOO MAE 5.129 dex β_H at expanded scope (vs Path 19-prime "
              "3.066 baseline; WORSE). 4 of 6 new 1111 papers added at Substep C fail H-axis applicability filter "
              "(Hc2 ~60-70T vs typical experimental Jc(H) span 0-7T → H_range/Hc2 < 0.12). Substructure-conditional "
              "methodology applicability per Substep D nu-2 fails at populated scope; predictions at 1111 substructure "
              "would carry uninterpretable wide CIs from compound-LOO 95% CI [2.49, 6.24]. Surfacing 1111 candidates "
              "anywhere undermines the nu-2 commitment for paper 3 framing.\n\n")

    md.append("### MP query reproducibility note\n\n")
    md.append("3DSC_MP.csv is an offline snapshot file. To re-run with current Materials Project state: install "
              "`mp_api` package + obtain MP_API_KEY + run `compound_extractor_mp.py` infrastructure (currently fetches "
              "DFT properties only, not Tc). For current dispatch, no online MP call was made; 3DSC_MP.csv is the "
              "data source (timestamp of file creation: 2022-06-20 per 3DSC project).\n\n")

    md.append("---\n\n")

    # ===== A1 per substructure =====
    md.append("## §2 — A1 candidate list per substructure (3DSC source)\n\n")

    for sub in ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]:
        r = A1_results[sub]
        md.append(f"### §2.{['iron_chalcogenide_11', 'iron_pnictide_122', 'conventional_AlB2'].index(sub)+1} {sub}\n\n")

        md.append("Filter pipeline counts:\n\n")
        md.append(f"| stage | n |\n|---|---:|\n")
        md.append(f"| n_total (raw 3DSC hits) | {r['n_total']} |\n")
        md.append(f"| n_known_superconductor (Tc > 0) | {r['n_known_sc']} |\n")
        md.append(f"| n_has_Hc2_estimate (in 3DSC) | {r['n_has_hc2']} |\n")
        md.append(f"| n_not_in_canonical_fits | {r['n_not_canon']} |\n")
        md.append(f"| **n_in_scope** | **{r['n_in_scope']}** |\n\n")

        cands = r["candidates"]
        if len(cands) == 0:
            md.append("(no in-scope candidates at this substructure)\n\n")
            continue

        # Sort by Tc desc; show top + tail if very long
        cands_sorted = cands.sort_values("tc", ascending=False)
        max_show = 30
        show = cands_sorted.head(max_show)

        md.append(f"Top {min(max_show, len(cands_sorted))} candidates by Tc (descending):\n\n")
        md.append("| pretty_formula | MP_id | spacegroup | Tc (K) | Tc reference | Hc2 (T) | "
                  "Hc2 reference | in_canonical_fits | in_scope_flag |\n")
        md.append("|---|---|---|---:|---|---:|---|---|---|\n")
        for _, row in show.iterrows():
            tc_ref = row.get("literature_Tc_reference", "via 3DSC")
            tc_ref_short = tc_ref[:60] + "..." if len(str(tc_ref)) > 60 else tc_ref
            md.append(f"| {row['formula_sc']} | {row['material_id_2']} | {row['spacegroup_2']} | "
                      f"{row['tc']:.2f} | {tc_ref_short} | — | "
                      f"literature lookup required | False | True |\n")
        if len(cands_sorted) > max_show:
            md.append(f"\n*({len(cands_sorted) - max_show} additional candidates not shown; full list in CSV)*\n")
        md.append("\n")

    md.append("---\n\n")

    # ===== A2 per substructure =====
    md.append("## §3 — A2 candidate list per substructure (extraction-CSV-but-not-fit)\n\n")
    if len(A2) == 0:
        md.append("No A2 candidates surfaced at the 3 testable substructures.\n\n")
    else:
        for sub in ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]:
            sub_A2 = A2[A2["substructure"] == sub]
            md.append(f"### §3.{['iron_chalcogenide_11', 'iron_pnictide_122', 'conventional_AlB2'].index(sub)+1} {sub}\n\n")
            md.append(f"n A2 records: {len(sub_A2)}\n\n")
            if len(sub_A2) == 0:
                md.append("(no A2 candidates at this substructure)\n\n")
                continue
            md.append("| paper_id | compound_formula | sample_form | T_fixed (K) | fail_reason | "
                      "n_data_points | n_distinct_H | bucket | threshold_relaxation_yields_fit |\n")
            md.append("|---|---|---|---:|---|---:|---:|---|---|\n")
            for _, row in sub_A2.head(30).iterrows():
                md.append(f"| {row['paper_id']} | {row['compound_formula']} | {row['sample_form']} | "
                          f"{row['T_fixed_K']} | {row['fail_reason']} | {row['n_data_points_available']} | "
                          f"{row['n_distinct_H']} | {row['bucket']} | {row['threshold_relaxation_would_yield_fit']} |\n")
            if len(sub_A2) > 30:
                md.append(f"\n*({len(sub_A2) - 30} additional A2 records not shown)*\n")
            md.append("\n")

    md.append("---\n\n")

    # ===== Combined =====
    md.append("## §4 — Combined in-scope candidate count per substructure\n\n")
    md.append("| substructure | A1 in_scope | A2 records | combined |\n|---|---:|---:|---:|\n")
    for sub, c in combined_counts.items():
        md.append(f"| {sub} | {c['A1']} | {c['A2']} | {c['combined']} |\n")
    md.append(f"| **TOTAL** | — | — | **{total_combined}** |\n\n")
    md.append(f"**Pre-registered outcome triggered**: **{rho_outcome}**\n\n")

    md.append("---\n\n")

    # ===== Gap analysis =====
    md.append("## §5 — Required-inputs gap analysis\n\n")
    md.append("Per dispatch hard constraint: Hc2 values are NOT in 3DSC and the existing infrastructure does NOT "
              "fetch Hc2 from any external source. **All A1 candidates require literature lookup of Hc2(0) before "
              "prediction dispatch.** Tc values are populated from 3DSC for all A1 candidates (see Tc + Tc reference "
              "columns in §2 tables).\n\n")
    md.append("**Hc2 lookup priority order** (to be done by user / advisor / RA before prediction dispatch):\n\n")
    md.append("1. Direct measurement (M-H loop intersection at Jc → 0; transport ρ vs H at fixed T near Tc with "
              "WHH extrapolation Hc2(0) = −0.69 × Tc × dHc2/dT|Tc).\n")
    md.append("2. Compound-aggregate literature value (review papers; SuperCon database for individual compounds).\n")
    md.append("3. Substructure-aggregate fallback (Tier 3 default per `phase_3_p18_form3_fits_partial_v2.py` Tier "
              "framework — for chalc_11 Hc2≈47T; for pnictide_122 Hc2≈50T; for AlB2 Hc2≈16T).\n\n")

    md.append("**A2 candidates already have Tc + Hc2 in their extraction CSVs** (carried from `tc_K` and `hc2_T` "
              "columns of v3_2_2B_extension). No literature lookup required for A2 — only Form 3 fit threshold "
              "relaxation OR vision-pass re-extraction at higher resolution.\n\n")

    md.append("---\n\n")

    # ===== Sample-form distribution =====
    md.append("## §6 — Sample-form distribution per substructure\n\n")
    md.append("Per Path 3 contribution (§S8.5b.7 sample-form variance decomposition), sample form is a load-bearing "
              "stratification dimension for predictor scope assignment. 3DSC source does NOT carry sample-form metadata "
              "(it's a structural/compositional database). Sample form for A1 candidates would be **user-specified at "
              "design scope** — i.e., the prediction dispatch must commit a target sample form per candidate.\n\n")
    md.append("A2 candidates DO carry sample form from extraction CSVs:\n\n")
    if len(A2) > 0:
        for sub in ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]:
            sub_A2 = A2[A2["substructure"] == sub]
            if len(sub_A2) == 0:
                continue
            sf_counts = sub_A2["sample_form"].value_counts()
            md.append(f"**{sub}** (A2 only):\n\n")
            for sf, n in sf_counts.items():
                md.append(f"- {sf}: {n}\n")
            md.append("\n")
    else:
        md.append("(no A2 records to characterize)\n\n")

    md.append("---\n\n")

    # ===== Pre-registered prediction methodology =====
    md.append("## §7 — Pre-registered prediction methodology (locks scope before dispatch)\n\n")
    md.append("**Pointwise target grid** (default; subject to advisor override per findings inventory §9 question (i)):\n")
    md.append("- T = 4.2 K, 20 K, 0.77·Tc\n")
    md.append("- H = 0.1 T, 1 T, 5 T\n")
    md.append("- Per-candidate output: 9 (T, H) grid points × 1 Jc value each\n\n")

    md.append("**Per-candidate output**:\n")
    md.append("- Predicted Jc at each grid point (A/cm²)\n")
    md.append("- β_T estimate with bootstrap CI (N=5000 iterations, seed=42, matches Path δ + Path 19-AC)\n")
    md.append("- β_H estimate with bootstrap CI (N=5000, seed=42)\n")
    md.append("- log_Jc_partial estimate with bootstrap CI\n\n")

    md.append("**Mandatory scope qualifier at every prediction**:\n\n")
    md.append("> \"Within-substructure populated cohort scope; substructure-conditional methodology applicability "
              "per Path 12 (substructure-aggregate LOSO MAE 0.43 dex β_H Stage 2) + Path 19-AC (per-paper LOO MAE "
              "0.994 dex β_H at post-AC scope, cohort-stable verdict). Cross-axis cascade evidence at substructure-aggregate "
              "scope (Tier a + b per §S8.6); within-substructure compound-aggregate scope partially testable at "
              "iron_chalcogenide_11 (n=3 overlap) per Substep D mu-2.\"\n\n")

    md.append("**Hard exclusion at all dispatch layers**: iron_pnictide_1111 per Substep D nu-2 (substructure-conditional "
              "methodology applicability fails; compound-LOO MAE 5.129 dex β_H).\n\n")

    md.append("**Pre-registered binary outcomes** (resolved at prediction dispatch close-out):\n\n")
    md.append("- **rho-1 / rho-2**: combined in-scope candidate list size — this dispatch's outcome documented in §4 above.\n")
    md.append("- **sigma-1 / sigma-2**: predicted Jc bootstrap CIs at target grid have median width < 1.5 dex (sigma-1, "
              "ranking interpretable) or ≥ 1.5 dex (sigma-2, ranking caveated as broad-uncertainty). RESOLVED at "
              "prediction-dispatch close-out — NOT this dispatch.\n")
    md.append("- **tau-1 / tau-2**: top-ranked candidates' substructure distribution balanced across the 3 testable "
              "substructures (tau-1) or concentrated in one (tau-2; calls for substructure-conditional reporting). "
              "RESOLVED at prediction-dispatch close-out.\n\n")

    md.append("**Hold**: prediction dispatch held until advisor signs off on (a) findings inventory + (b) this candidate "
              "list + (c) target grid choice + (d) discovery list destination (paper 3 §6 main text vs §S8 supplementary).\n\n")

    md.append("---\n\n")

    # ===== Metadata footer =====
    md.append("## Metadata footer\n\n")
    md.append(f"- Total n_in_scope per substructure:\n")
    for sub, c in combined_counts.items():
        md.append(f"  - {sub}: A1={c['A1']} + A2={c['A2']} = **{c['combined']}**\n")
    md.append(f"- **Combined total in-scope: {total_combined}**\n")
    md.append(f"- **Pre-registered outcome triggered at candidate-list scope: {rho_outcome}**\n")
    md.append(f"- iron_pnictide_1111 hard-excluded (NOT counted, NOT listed) per Substep D nu-2.\n")
    md.append(f"- Generation timestamp: {timestamp}\n")
    md.append(f"- Cost: $0 (offline 3DSC scan + local CSV cross-reference)\n")
    md.append(f"- Cumulative Phase 3 cost remains $66.95 / $100 (~33.0% headroom)\n")

    OUT_MD.write_text("".join(md))


if __name__ == "__main__":
    main()
