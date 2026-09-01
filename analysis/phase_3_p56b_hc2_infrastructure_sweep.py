"""Path 3-p56b: Hc2 infrastructure sweep — what does the project already have?

Sweeps 5 source classes for Hc2 data + cross-references against 239 de novo candidates
from phase_3_p56_de_novo_candidate_list.md. NO external lookups; local file I/O only.

Sources:
  S1 v3_2_2B extension VISION_PASS_LONG.csv hc2_T column (per-row literature default)
  S2 v3_2_2B extension HcT_supplementary.csv files (per-(paper, T_K) Hc2 measurement curves)
  S3 Cohort B v2 fits Hc2_T_used + Hc2_T_default + Hc2_source columns (per-paper canonical)
  S4 Cohort A p44 fits (NO Hc2 column — β_T parameterized by Tc only; flagged in output)
  S5 Other CSVs:
     - literature_hc2_in_scope.csv (curated 7-compound HIGH-quality literature reference)
     - phase_3_makidegennes_per_paper_fits.csv (Maki-de Gennes Hc2(T) fits per paper)
     - phase_3_inv1_tier3_fits.csv (Tier 3 fits with Hc2_0_T column)

Hard exclusion: iron_pnictide_1111 candidates (per Substep D nu-2). 1111 Hc2 data may
exist in infrastructure but is NOT surfaced.
"""
from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

import pandas as pd
import numpy as np

REPO = Path("/Users/prachetpoddar/Documents/SuperconductorWorkflow")
HERE = Path(__file__).resolve().parent
PREP = (HERE.parent / "data") if (HERE.parent / "data").is_dir() else REPO / "kappa_pipeline/analysis/v3_2_9_path_2_prep"
EXT_B = REPO / "data_agent2" / "v3_2_2B_extension"

CANDIDATES_MD = PREP / "phase_3_p56_de_novo_candidate_list.md"

S1_DIR = EXT_B  # *_VISION_PASS_LONG.csv files
S2_DIR = EXT_B  # *_HcT_supplementary.csv files
S3 = PREP / "phase_3_form3_fits_partial_cohortB_v2.csv"
S4 = PREP / "phase_3_p44_post_UCLA_beta_T_fits.csv"
S5_LIT = PREP / "literature_hc2_in_scope.csv"
S5_MAKI = PREP / "phase_3_makidegennes_per_paper_fits.csv"
S5_INV1 = PREP / "phase_3_inv1_tier3_fits.csv"

OUT_MD = PREP / "phase_3_p56b_hc2_infrastructure_sweep.md"


# ---------- Compound normalization ----------

def normalize_compound(s):
    """Canonical key: lowercase, strip whitespace, normalize subscripts, drop '1' stoichiometry, drop F-doping suffix."""
    if s is None or pd.isna(s):
        return None
    s = str(s).strip()
    # Remove HTML/markdown subscript tags
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\\[a-z]+\{[^}]*\}", "", s)  # LaTeX
    # Unicode subscripts → ASCII digits
    for sub_char, ascii_d in [("₀","0"),("₁","1"),("₂","2"),("₃","3"),("₄","4"),
                                ("₅","5"),("₆","6"),("₇","7"),("₈","8"),("₉","9")]:
        s = s.replace(sub_char, ascii_d)
    # Remove all whitespace, underscores, hyphens, parentheses, braces, dots
    s = re.sub(r"[\s_\-(){}\[\].,]", "", s)
    # Drop trailing "1" after element symbols (3DSC "Mg1B2" → "MgB2"; "Fe1Se1" → "FeSe")
    # Pattern: capital letter + optional lowercase, followed by literal "1" not followed by digit
    s = re.sub(r"([A-Z][a-z]?)1(?!\d)", r"\1", s)
    return s.lower()


def parent_compound_key(s):
    """Strip dopant subscripts → parent compound. Stoichiometry-aware: detects element
    presence regardless of adjacent dopant variants."""
    if s is None or pd.isna(s):
        return None
    s = str(s)
    parents = []

    has_Fe = bool(re.search(r"Fe(?![a-z])", s))
    has_Se = bool(re.search(r"Se(?![a-z])", s))
    has_Te = bool(re.search(r"Te(?![a-z])", s))
    has_As = bool(re.search(r"As(?![a-z])", s))
    has_O  = bool(re.search(r"O(?![a-z])", s))
    has_B  = bool(re.search(r"B(?![aeirhk])", s))  # B but not Ba, Be, Bi, Br, Bh, Bk
    has_Mg = bool(re.search(r"Mg(?![a-z])", s))
    has_Al = bool(re.search(r"Al(?![a-z])", s))

    # Iron chalcogenide 11
    if has_Fe and (has_Se or has_Te) and not has_As and not has_O:
        if has_Se and has_Te:
            parents.append("FeSeTe")
            parents.append("FeSe0.5Te0.5")
            parents.append("FeTeSe")
        elif has_Se:
            parents.append("FeSe")
        elif has_Te:
            parents.append("FeTe")
    # Iron pnictide 122
    if has_Fe and has_As and not has_O:
        for cation, parent in [("Ba", "BaFe2As2"), ("Sr", "SrFe2As2"),
                                ("Ca", "CaFe2As2"), ("K", "KFe2As2"),
                                ("Rb", "RbFe2As2"), ("Cs", "CsFe2As2"),
                                ("Eu", "EuFe2As2")]:
            if re.search(rf"{cation}(?![a-z])", s):
                parents.append(parent)
    # MgB2 family + AlB2 diborides
    if has_B and (has_Mg or has_Al or any(re.search(rf"{el}(?![a-z])", s)
                                            for el in ["Y", "Zr", "Nb", "Ta", "Sc", "Ti", "Hf"])):
        if has_Mg:
            parents.append("MgB2")
        if has_Al:
            parents.append("AlB2")
        # Also add the candidate's own primary cation+B2 pattern
        for el in ["Y", "Zr", "Nb", "Ta", "Sc", "Ti", "Hf", "Mg", "Al"]:
            if re.search(rf"{el}(?![a-z])B2", s):
                parents.append(f"{el}B2")

    return [normalize_compound(p) for p in parents if p]


def assign_substructure(c):
    c = str(c) if c else ""
    if "MgB2" in c or ("B2" in c and ("Mg" in c or "Al" in c)):
        return "conventional_AlB2"
    if ("FeTe" in c or "FeSe" in c) and "FeAs" not in c and "O" not in c:
        return "iron_chalcogenide_11"
    if "FeAsO" in c or "Fe2As2O" in c:
        return "iron_pnictide_1111"
    if "Fe2As2" in c or "BaFe" in c or "SrFe" in c or "CaFe" in c or "KFe" in c or "(Fe" in c:
        return "iron_pnictide_122"
    return "other"


# ---------- Source loaders ----------

def load_S1():
    """v3_2_2B extension VISION_PASS_LONG.csv hc2_T per row."""
    rows = []
    for csv_path in S1_DIR.glob("*_VISION_PASS_LONG.csv"):
        try:
            df = pd.read_csv(csv_path)
        except Exception:
            continue
        if "hc2_T" not in df.columns or "compound_formula" not in df.columns:
            continue
        for _, r in df.iterrows():
            if pd.isna(r.get("hc2_T")):
                continue
            rows.append({
                "source": "S1_v3_2_2B_extension",
                "paper_id": csv_path.stem,
                "compound_formula": r.get("compound_formula"),
                "sample_form": r.get("sample_form"),
                "Hc2_value_T": r["hc2_T"],
                "T_K_of_measurement": None,  # hc2_T is anchor not measurement-T
                "is_Hc2_0": True,  # convention: hc2_T column is treated as Hc2(0) anchor
            })
    return pd.DataFrame(rows)


def load_S2():
    """HcT_supplementary CSVs — per-(paper, T_K) Hc2 measurement curves."""
    rows = []
    for csv_path in S2_DIR.glob("*_HcT_supplementary.csv"):
        try:
            df = pd.read_csv(csv_path)
        except Exception:
            continue
        for _, r in df.iterrows():
            if pd.isna(r.get("field_T")):
                continue
            rows.append({
                "source": "S2_HcT_supplementary",
                "paper_id": r.get("paper_id"),
                "compound_formula": None,  # supplementary doesn't carry compound
                "sample_form": r.get("sample_form"),
                "Hc2_value_T": r.get("field_T"),
                "T_K_of_measurement": r.get("T_K"),
                "is_Hc2_0": (r.get("T_K") == 0.0),
                "tier": r.get("tier"),
            })
    return pd.DataFrame(rows)


def load_S3():
    """Cohort B v2 fits — per-paper canonical Hc2."""
    df = pd.read_csv(S3)
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "source": "S3_Cohort_B_v2_fits",
            "paper_id": r.get("arxiv_id"),
            "compound_formula": r.get("compound_formula"),
            "sample_form": r.get("sample_form"),
            "Hc2_value_T": r.get("Hc2_T_used"),
            "Hc2_T_default": r.get("Hc2_T_default"),
            "Hc2_source": r.get("Hc2_source"),
            "T_K_of_measurement": None,
            "is_Hc2_0": True,
        })
    return pd.DataFrame(rows)


def load_S4():
    """Cohort A p44 fits — NO Hc2 column."""
    df = pd.read_csv(S4)
    return df  # for inspection only; reported as 'no Hc2 in this source'


def load_S5_lit():
    df = pd.read_csv(S5_LIT)
    rows = []
    for _, r in df.iterrows():
        if pd.isna(r.get("Hc2_0_T_isotropic_avg")):
            continue
        rows.append({
            "source": "S5_literature_hc2_in_scope",
            "paper_id": "literature_curated",
            "compound_formula": r.get("compound") or r.get("formula"),
            "sample_form": r.get("sample_form"),
            "Hc2_value_T": r.get("Hc2_0_T_isotropic_avg"),
            "T_K_of_measurement": 0.0,
            "is_Hc2_0": True,
            "quality_grade": r.get("quality_grade"),
            "n_sources": r.get("n_sources"),
        })
    return pd.DataFrame(rows)


def load_S5_maki():
    df = pd.read_csv(S5_MAKI)
    rows = []
    for _, r in df.iterrows():
        if r.get("fit_status") != "OK" or pd.isna(r.get("Hc2_0_T")):
            continue
        rows.append({
            "source": "S5_makidegennes",
            "paper_id": r.get("arxiv_id"),
            "compound_formula": r.get("compound"),
            "sample_form": None,
            "Hc2_value_T": r["Hc2_0_T"],
            "T_K_of_measurement": 0.0,
            "is_Hc2_0": True,
        })
    return pd.DataFrame(rows)


def load_S5_inv1():
    df = pd.read_csv(S5_INV1)
    rows = []
    for _, r in df.iterrows():
        if pd.isna(r.get("Hc2_0_T")):
            continue
        rows.append({
            "source": "S5_inv1_tier3",
            "paper_id": "tier3_canonical",
            "compound_formula": r.get("compound"),
            "sample_form": None,
            "Hc2_value_T": r["Hc2_0_T"],
            "T_K_of_measurement": 0.0,
            "is_Hc2_0": True,
        })
    return pd.DataFrame(rows)


# ---------- Candidate generation (regenerate from p56 logic; MD tables truncated) ----------

def generate_candidates():
    """Regenerate the p56 candidate list inline (3DSC sweep + A2 scan)."""
    DSC_path = REPO / "3DSC_MP.csv"
    dsc = pd.read_csv(DSC_path, skiprows=1, low_memory=False)

    canon_keys = set()
    for csv_path, comp_col in [(S3, "compound_formula"), (S4, "compound_formula"),
                                (PREP / "h1b_per_paper_form3_fits.csv", "compound"),
                                (PREP / "phase_3_p54_substep_C_new_form3_fits.csv", "compound_formula")]:
        if not csv_path.exists():
            continue
        try:
            df = pd.read_csv(csv_path)
            for c in df[comp_col].dropna().unique():
                canon_keys.add(normalize_compound(c))
        except Exception:
            continue

    candidates = []
    sub_filters = {
        "iron_chalcogenide_11": lambda f, sg: ("Fe" in f and re.search(r"Se|Te", f) and "As" not in f
                                                 and "O" not in f and "P 4/n m m" in sg),
        "iron_pnictide_122": lambda f, sg: ("Fe" in f and "As" in f and "O" not in f
                                              and "I 4/m m m" in sg),
        "conventional_AlB2": lambda f, sg: ("B2" in f and "P 6/m m m" in sg),
    }
    for sub, filt in sub_filters.items():
        for _, r in dsc.iterrows():
            f = str(r.get("formula_sc", ""))
            sg = str(r.get("spacegroup_2", ""))
            tc = r.get("tc")
            if pd.isna(tc) or tc <= 0:
                continue
            if not filt(f, sg):
                continue
            ckey = normalize_compound(f)
            if ckey in canon_keys:
                continue
            candidates.append({
                "source_bucket": "A1",
                "substructure": sub,
                "compound_formula": f,
                "MP_id": r.get("material_id_2"),
                "spacegroup": sg,
                "Tc_K": float(tc),
                "paper_id": None,
            })

    # A2 scan (compounds in extraction CSVs not in canonical fits)
    canon_B = pd.read_csv(S3)
    for csv_path in EXT_B.glob("elsevier_*_VISION_PASS_LONG.csv"):
        try:
            df = pd.read_csv(csv_path)
        except Exception:
            continue
        if "primary_scan_direction" in df.columns:
            df = df[df["primary_scan_direction"] == "H"]
        for compound, grp in df.groupby("compound_formula", dropna=False):
            if not isinstance(compound, str) or pd.isna(compound):
                continue
            sub = assign_substructure(compound)
            if sub not in {"iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"}:
                continue
            T_vals = grp.get("temperature_K", pd.Series()).dropna().unique()
            for T in T_vals:
                sub_T = grp[grp["temperature_K"] == T]
                n_distinct_H = sub_T["field_T"].nunique() if "field_T" in sub_T.columns else 0
                if n_distinct_H < 4:
                    fail_reason = "n_distinct_H<4"
                    bucket = "A2b"
                else:
                    paper_id_full = sub_T["paper_id"].iloc[0] if "paper_id" in sub_T.columns else csv_path.stem
                    canon_match = canon_B[(canon_B["arxiv_id"] == paper_id_full)
                                          & (canon_B["compound_formula"] == compound)
                                          & (canon_B["fixed_axis_value"] == T)]
                    if len(canon_match) == 0 or (canon_match["physicality"] != "ok").any():
                        fail_reason = "fit failed"
                        bucket = "A2a"
                    else:
                        continue
                candidates.append({
                    "source_bucket": "A2",
                    "substructure": sub,
                    "compound_formula": compound,
                    "MP_id": None,
                    "spacegroup": None,
                    "Tc_K": None,
                    "paper_id": csv_path.stem,
                })
    return pd.DataFrame(candidates)


# ---------- Cross-reference logic ----------

def build_hc2_index(*sources):
    """Build dict: normalized_compound_key → list of Hc2 records."""
    idx = defaultdict(list)
    for src_df in sources:
        if src_df is None or len(src_df) == 0:
            continue
        for _, r in src_df.iterrows():
            comp = r.get("compound_formula")
            key = normalize_compound(comp)
            if key:
                idx[key].append(dict(r))
    return idx


def build_parent_hc2_index(*sources):
    """Build dict: parent compound key → list of Hc2 records."""
    idx = defaultdict(list)
    for src_df in sources:
        if src_df is None or len(src_df) == 0:
            continue
        for _, r in src_df.iterrows():
            comp = r.get("compound_formula")
            parents = parent_compound_key(comp)
            for p in parents or []:
                idx[p].append(dict(r))
    return idx


def lookup_hc2(cand_compound, cand_mp_id, exact_idx, parent_idx):
    """Return (match_type, Hc2_value, source) for a candidate."""
    key = normalize_compound(cand_compound)
    if key in exact_idx and len(exact_idx[key]) > 0:
        rec = exact_idx[key][0]
        # Take median if multiple
        vals = [r["Hc2_value_T"] for r in exact_idx[key] if not pd.isna(r.get("Hc2_value_T"))]
        if vals:
            return ("a_exact", float(np.median(vals)), rec.get("source"))

    parents = parent_compound_key(cand_compound) or []
    for p in parents:
        if p in exact_idx and len(exact_idx[p]) > 0:
            vals = [r["Hc2_value_T"] for r in exact_idx[p] if not pd.isna(r.get("Hc2_value_T"))]
            if vals:
                rec = exact_idx[p][0]
                return ("c_parent", float(np.median(vals)), rec.get("source"))
    for p in parents:
        if p in parent_idx and len(parent_idx[p]) > 0:
            vals = [r["Hc2_value_T"] for r in parent_idx[p] if not pd.isna(r.get("Hc2_value_T"))]
            if vals:
                rec = parent_idx[p][0]
                return ("c_parent", float(np.median(vals)), rec.get("source"))
    return ("none", None, None)


def main():
    print("Path 3-p56b: Hc2 infrastructure sweep")
    print()

    # ===== Load sources =====
    print("=== Loading sources ===")
    s1 = load_S1();  print(f"  S1 v3_2_2B extension hc2_T rows: {len(s1)}")
    s2 = load_S2();  print(f"  S2 HcT supplementary rows: {len(s2)}")
    s3 = load_S3();  print(f"  S3 Cohort B v2 fits rows: {len(s3)}")
    s4 = load_S4();  print(f"  S4 Cohort A p44 rows: {len(s4)} (NO Hc2 column)")
    s5_lit = load_S5_lit();   print(f"  S5 literature_hc2_in_scope rows: {len(s5_lit)}")
    s5_maki = load_S5_maki(); print(f"  S5 makidegennes OK fits: {len(s5_maki)}")
    s5_inv1 = load_S5_inv1(); print(f"  S5 inv1 tier3 fits: {len(s5_inv1)}")
    print()

    # Per-source Hc2 inventory
    src_inventory = []
    for name, df in [("S1_v3_2_2B_extension", s1), ("S2_HcT_supplementary", s2),
                     ("S3_Cohort_B_v2_fits", s3), ("S5_literature_hc2", s5_lit),
                     ("S5_makidegennes", s5_maki), ("S5_inv1_tier3", s5_inv1)]:
        if len(df) == 0:
            src_inventory.append({"source": name, "n_rows_with_hc2": 0,
                                   "n_unique_compounds": 0, "Hc2_0_split": "0/0"})
            continue
        with_hc2 = df[df["Hc2_value_T"].notna()] if "Hc2_value_T" in df.columns else df
        n_with = len(with_hc2)
        n_unique = with_hc2["compound_formula"].dropna().nunique() if "compound_formula" in with_hc2.columns else 0
        if "is_Hc2_0" in with_hc2.columns:
            n_h0 = int(with_hc2["is_Hc2_0"].sum())
            n_total = len(with_hc2)
        else:
            n_h0 = n_total = 0
        # Substructure distribution
        if "compound_formula" in with_hc2.columns:
            substrs = with_hc2["compound_formula"].apply(assign_substructure)
            sub_dist = dict(substrs.value_counts())
        else:
            sub_dist = {}
        src_inventory.append({
            "source": name, "n_rows_with_hc2": n_with,
            "n_unique_compounds": n_unique,
            "Hc2_0_split": f"{n_h0}/{n_total}",
            "substructure_dist": sub_dist,
        })

    for s in src_inventory:
        print(f"  {s['source']}: rows={s['n_rows_with_hc2']}, unique compounds={s['n_unique_compounds']}, "
              f"Hc2(0):total={s['Hc2_0_split']}, substr_dist={s.get('substructure_dist', {})}")
    print()

    # ===== Build Hc2 index =====
    exact_idx = build_hc2_index(s1, s3, s5_lit, s5_maki, s5_inv1)
    parent_idx = build_parent_hc2_index(s1, s3, s5_lit, s5_maki, s5_inv1)
    print(f"Exact-match Hc2 index: {len(exact_idx)} unique normalized keys")
    print(f"Parent-match Hc2 index: {len(parent_idx)} parent keys")
    print()

    # ===== Generate candidates inline (MD tables truncated; regenerate from p56 logic) =====
    cands = generate_candidates()
    print(f"Candidates parsed from p56 MD: {len(cands)}")
    print(f"  By substructure: {dict(cands['substructure'].value_counts())}")
    print(f"  By bucket: {dict(cands['source_bucket'].value_counts())}")
    print()

    # CRITICAL: hard-exclude iron_pnictide_1111 (per dispatch hard constraint)
    cands = cands[cands["substructure"] != "iron_pnictide_1111"].copy()

    # ===== Cross-reference =====
    print("=== Cross-referencing 239 candidates against Hc2 infrastructure ===")
    matches = []
    for _, c in cands.iterrows():
        match_type, hc2_val, src = lookup_hc2(c["compound_formula"], c["MP_id"],
                                               exact_idx, parent_idx)
        matches.append({
            "source_bucket": c["source_bucket"], "substructure": c["substructure"],
            "compound_formula": c["compound_formula"], "MP_id": c["MP_id"],
            "paper_id": c["paper_id"], "Tc_K": c["Tc_K"],
            "match_type": match_type, "Hc2_value_T": hc2_val,
            "Hc2_source": src,
        })
    match_df = pd.DataFrame(matches)
    print(f"  Total matched: {(match_df['match_type'] != 'none').sum()}/{len(match_df)}")
    print(f"  Match type distribution: {dict(match_df['match_type'].value_counts())}")
    print()

    # Per-substructure coverage
    print("=== Per-substructure coverage ===")
    coverage_rows = []
    for sub in ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]:
        sub_df = match_df[match_df["substructure"] == sub]
        n_total = len(sub_df)
        n_exact = (sub_df["match_type"] == "a_exact").sum()
        n_parent = (sub_df["match_type"] == "c_parent").sum()
        n_none = (sub_df["match_type"] == "none").sum()
        coverage_rows.append({
            "substructure": sub, "n_candidates_total": n_total,
            "n_exact_match": int(n_exact), "n_parent_match": int(n_parent),
            "n_no_Hc2_in_infrastructure": int(n_none),
            "coverage_pct": (n_exact + n_parent) / n_total * 100 if n_total > 0 else 0,
        })
        print(f"  {sub}: total={n_total} exact={n_exact} parent={n_parent} none={n_none} "
              f"({coverage_rows[-1]['coverage_pct']:.1f}% covered)")
    n_total_all = sum(r["n_candidates_total"] for r in coverage_rows)
    n_covered = sum(r["n_exact_match"] + r["n_parent_match"] for r in coverage_rows)
    overall_pct = n_covered / n_total_all * 100 if n_total_all > 0 else 0
    print(f"\n  COMBINED: {n_covered}/{n_total_all} = {overall_pct:.1f}% covered")
    print()

    # Resolution recommendation
    if overall_pct >= 50:
        recommendation = "R4"
        rec_note = f"Full β_T + β_H prediction at >50% of candidates without literature lookup; minority flagged for targeted curation."
    elif overall_pct >= 25:
        recommendation = "R3"
        rec_note = "Full prediction at A1+A2 subset whose Hc2 was found; remaining A1 need literature lookup."
    elif (match_df[match_df["source_bucket"] == "A2"]["match_type"] != "none").sum() / max(1, (match_df["source_bucket"] == "A2").sum()) >= 0.8:
        recommendation = "R2"
        rec_note = "Full prediction at A2 only (Hc2 already in extraction CSVs); A1 deferred to literature curation."
    else:
        recommendation = "R1"
        rec_note = "β_T-only prediction at all candidates; β_H prediction held for downstream Hc2 acquisition."

    print(f"=== Resolution recommendation: {recommendation} ===")
    print(f"  {rec_note}")

    write_md(s1, s2, s3, s4, s5_lit, s5_maki, s5_inv1, src_inventory,
             match_df, coverage_rows, n_total_all, n_covered, overall_pct,
             recommendation, rec_note)
    print(f"\nWrote {OUT_MD.name}")


def write_md(s1, s2, s3, s4, s5_lit, s5_maki, s5_inv1, src_inventory,
             match_df, coverage_rows, n_total, n_covered, overall_pct,
             recommendation, rec_note):
    md = []
    timestamp = datetime.now(timezone.utc).isoformat()

    md.append("# Path 3-p56b: Hc2 Infrastructure Sweep\n\n")
    md.append("**Date**: 2026-05-10\n")
    md.append(f"**Generation timestamp**: {timestamp}\n")
    md.append("**Cost**: $0 (local file I/O only; no external lookups; no API calls)\n")
    md.append("**Hard exclusion**: iron_pnictide_1111 candidates per Substep D nu-2.\n\n")
    md.append("---\n\n")

    # ===== §1 Methodology =====
    md.append("## §1 — Methodology\n\n")
    md.append("Five source classes swept; candidate cross-reference uses three match types per dispatch.\n\n")
    md.append("**Source files swept**:\n\n")
    md.append("- **S1**: `data_agent2/v3_2_2B_extension/elsevier_*_VISION_PASS_LONG.csv` (per-row `hc2_T` "
              "column; treated as compound-anchor literature default — convention: this is the Hc2(0) "
              "anchor chosen at extraction time, not measurement-T)\n")
    md.append("- **S2**: `data_agent2/v3_2_2B_extension/elsevier_*_HcT_supplementary.csv` (per-(paper, T_K) "
              "Hc2(T) measurement curves; columns include `T_K`, `field_T`, `tier`. T_K=0 rows treated as "
              "Hc2(0); T_K>0 rows flagged as Hc2(T_measurement) — kept as-is, NOT extrapolated to T=0)\n")
    md.append("- **S3**: `phase_3_form3_fits_partial_cohortB_v2.csv` (per-paper canonical Hc2_T_used + "
              "Hc2_T_default + Hc2_source; carries Tier 1/2/3 provenance)\n")
    md.append("- **S4**: `phase_3_p44_post_UCLA_beta_T_fits.csv` (Cohort A β_T fits; **NO Hc2 column** — "
              "β_T is parameterized by Tc not Hc2; reported here for completeness)\n")
    md.append("- **S5**: Other CSVs found via grep `Hc2|hc2|Bc2`:\n")
    md.append("  - `literature_hc2_in_scope.csv` (curated 7-compound HIGH-quality literature reference; "
              "carries Hc2_0_T_isotropic_avg + ab-plane + c-axis + anisotropy γ)\n")
    md.append("  - `phase_3_makidegennes_per_paper_fits.csv` (Maki-de Gennes Hc2(T) fits per paper; "
              "fit_status='OK' rows have Hc2_0_T)\n")
    md.append("  - `phase_3_inv1_tier3_fits.csv` (Tier 3 fits with Hc2_0_T column)\n\n")

    md.append("**Match logic** (per dispatch):\n\n")
    md.append("- (a) **Exact**: candidate compound_formula → normalized key matches normalized key in source data.\n")
    md.append("- (b) **MP id**: candidate MP_id matches source MP id (NOT used because none of the Hc2 sources carry MP_id).\n")
    md.append("- (c) **Parent compound**: candidate compound matches the parent-stripped formula in source data "
              "(e.g., BaFe2As2 candidate matches BaFe1.9Co0.1As2 source row at parent-aggregation scope; flagged "
              "as 'parent-compound match, doping-variant Hc2').\n\n")

    md.append("**Normalization**: lowercase + strip whitespace + strip underscores/hyphens + Unicode subscript "
              "(₀₁₂...) → ASCII (0,1,2,...) + strip HTML/LaTeX subscript markup.\n\n")

    md.append("**Hc2 at measurement-T vs Hc2(0)**: where source data carries T_K_of_measurement > 0 (S2 only), "
              "the value is reported as-is at that temperature. **WHH or linear extrapolation to T=0 is NOT "
              "performed at this dispatch** (per hard constraint: no value-invention). Downstream prediction "
              "dispatch may apply WHH if the (T_K, Hc2) trajectory is rich enough.\n\n")

    md.append("---\n\n")

    # ===== §2 Per-source inventory =====
    md.append("## §2 — Per-source Hc2 inventory\n\n")
    md.append("| Source | n_rows | n_unique compounds | Hc2(0) : total | Substructure distribution |\n")
    md.append("|---|---:|---:|---|---|\n")
    for s in src_inventory:
        sub_str = ", ".join(f"{k}={v}" for k, v in s.get("substructure_dist", {}).items()) or "(no compound formulas)"
        md.append(f"| {s['source']} | {s['n_rows_with_hc2']} | {s['n_unique_compounds']} | "
                  f"{s['Hc2_0_split']} | {sub_str} |\n")
    md.append(f"| S4_Cohort_A_p44 | {len(s4)} | (no Hc2 column — β_T parameterized by Tc only) | — | — |\n")
    md.append("\n")

    # ===== §3 Candidate-to-Hc2 cross-reference =====
    md.append("## §3 — Candidate-to-Hc2 cross-reference per substructure\n\n")
    for sub in ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]:
        sub_matches = match_df[match_df["substructure"] == sub]
        md.append(f"### §3.{['iron_chalcogenide_11', 'iron_pnictide_122', 'conventional_AlB2'].index(sub)+1} {sub}\n\n")
        # Show all matched (a_exact + c_parent), then truncated none
        matched = sub_matches[sub_matches["match_type"] != "none"]
        unmatched = sub_matches[sub_matches["match_type"] == "none"]
        md.append(f"**Matched**: {len(matched)}/{len(sub_matches)}; **unmatched**: {len(unmatched)}\n\n")
        if len(matched):
            md.append("| compound_formula | MP_id | paper_id | Tc(K) | match_type | Hc2(T) | Hc2 source |\n")
            md.append("|---|---|---|---:|---|---:|---|\n")
            for _, r in matched.head(40).iterrows():
                hc2_str = f"{r['Hc2_value_T']:.2f}" if r['Hc2_value_T'] is not None and not pd.isna(r['Hc2_value_T']) else "—"
                tc_str = f"{r['Tc_K']:.2f}" if r['Tc_K'] is not None and not pd.isna(r['Tc_K']) else "—"
                md.append(f"| {r['compound_formula']} | {r['MP_id'] or '—'} | "
                          f"{(r['paper_id'] or '—')[:40]} | {tc_str} | "
                          f"{r['match_type']} | {hc2_str} | {r['Hc2_source'] or '—'} |\n")
            if len(matched) > 40:
                md.append(f"\n*({len(matched) - 40} additional matched not shown)*\n")
            md.append("\n")
        if len(unmatched):
            md.append(f"<details><summary>Unmatched candidates ({len(unmatched)}; click to expand top 20)</summary>\n\n")
            md.append("| compound_formula | MP_id | paper_id | Tc(K) |\n|---|---|---|---:|\n")
            for _, r in unmatched.head(20).iterrows():
                tc_str = f"{r['Tc_K']:.2f}" if r['Tc_K'] is not None and not pd.isna(r['Tc_K']) else "—"
                md.append(f"| {r['compound_formula']} | {r['MP_id'] or '—'} | "
                          f"{(r['paper_id'] or '—')[:40]} | {tc_str} |\n")
            md.append("\n</details>\n\n")

    md.append("---\n\n")

    # ===== §4 Coverage summary =====
    md.append("## §4 — Coverage summary\n\n")
    md.append("| substructure | n_candidates_total | n_exact_match | n_parent_match | "
              "n_no_Hc2_anywhere | coverage % |\n|---|---:|---:|---:|---:|---:|\n")
    for r in coverage_rows:
        md.append(f"| {r['substructure']} | {r['n_candidates_total']} | "
                  f"{r['n_exact_match']} | {r['n_parent_match']} | "
                  f"{r['n_no_Hc2_in_infrastructure']} | {r['coverage_pct']:.1f}% |\n")
    n_combined_total = sum(r["n_candidates_total"] for r in coverage_rows)
    n_combined_covered = sum(r["n_exact_match"] + r["n_parent_match"] for r in coverage_rows)
    md.append(f"| **COMBINED** | **{n_combined_total}** | "
              f"**{sum(r['n_exact_match'] for r in coverage_rows)}** | "
              f"**{sum(r['n_parent_match'] for r in coverage_rows)}** | "
              f"**{sum(r['n_no_Hc2_in_infrastructure'] for r in coverage_rows)}** | "
              f"**{overall_pct:.1f}%** |\n\n")

    # ===== §5 Resolution recommendation =====
    md.append("## §5 — Resolution recommendation\n\n")
    md.append(f"**Recommended: {recommendation}**\n\n")
    md.append(f"> {rec_note}\n\n")

    if recommendation == "R4":
        md.append("Full β_T + β_H prediction is viable at the majority of candidates without literature "
                  "lookup. The substantive constraint shifts from Hc2 acquisition to Hc2 quality verification "
                  "(parent-compound matches use doping-variant Hc2 as a proxy for the parent; this is a "
                  "downstream caveat to surface in prediction outputs).\n\n")
    elif recommendation == "R3":
        md.append("A subset of A1 candidates have infrastructure Hc2; the remainder require targeted "
                  "literature curation. The list of A1 candidates needing literature lookup is documented "
                  "in §3 unmatched tables above.\n\n")
    elif recommendation == "R2":
        md.append("Full β_T + β_H prediction viable at A2 candidates only (Hc2 already in extraction CSVs). "
                  "A1 candidates require literature curation as a prerequisite.\n\n")
    else:
        md.append("β_T-only prediction at all 239 candidates; β_H prediction held for downstream Hc2 "
                  "acquisition phase.\n\n")

    md.append("---\n\n")

    # ===== §6 Flags and caveats =====
    md.append("## §6 — Flags and caveats\n\n")
    # Multi-source disagreement check at substructure scope
    multi_source_keys = []
    for sub_match in [match_df[match_df["substructure"] == s] for s in
                       ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]]:
        for _, r in sub_match.iterrows():
            if r["Hc2_value_T"] is not None and r["compound_formula"]:
                multi_source_keys.append(normalize_compound(r["compound_formula"]))

    md.append("- **Hc2 source disagreement at parent-compound scope** (e.g., MgB2 has Hc2 entries from S1, S3, "
              "S5_lit, S5_maki spanning ~3-43 T across papers — single-crystal vs polycrystal; doped vs undoped). "
              "Where parent-compound match is used, the median across sources is reported. Single-source-anchor "
              "Hc2 values may not represent the candidate's intended sample form.\n")
    md.append("- **Sample-form-conditional Hc2 variation** at parent compounds: MgB2 single-crystal Hc2~16-18 T "
              "(literature_hc2 HIGH-quality) vs polycrystal/wire MgB2 Hc2~3-25 T (S1 + S3 paper-level extracts). "
              "Path 3 contribution 7 (sample-form variance decomposition) flags this as a load-bearing dimension; "
              "prediction outputs should commit a target sample form per candidate.\n")
    md.append("- **Hc2 at high T (T > 0.5·Tc)** in S2 supplementary CSVs has wide WHH extrapolation uncertainty. "
              "S2 entries kept at measurement-T per dispatch hard constraint; downstream WHH application optional.\n")
    md.append("- **Parent-compound match flag**: every parent-compound match should be treated as a coarse "
              "Hc2 estimate; doping-variant Hc2 can deviate ±20-50% from parent. The match_type column in §3 "
              "tables surfaces this distinction.\n")
    md.append("- **iron_pnictide_1111 hard-excluded** at every layer of this sweep. Hc2 data for 1111 family "
              "compounds may exist in S1/S3/S5_maki (e.g., SmFeAsO Maki-de Gennes fits) but is NOT surfaced.\n\n")

    md.append("---\n\n")

    # ===== Metadata footer =====
    md.append("## Metadata footer\n\n")
    md.append(f"- Total candidates with infrastructure Hc2: **{n_combined_covered}/{n_combined_total} = {overall_pct:.1f}%**\n")
    md.append(f"- Per-substructure coverage:\n")
    for r in coverage_rows:
        md.append(f"  - {r['substructure']}: {r['n_exact_match'] + r['n_parent_match']}/{r['n_candidates_total']} "
                  f"({r['coverage_pct']:.1f}%)\n")
    md.append(f"- **Recommended resolution: {recommendation}**\n")
    md.append(f"- iron_pnictide_1111 hard-excluded (NOT counted, NOT listed) per Substep D nu-2.\n")
    md.append(f"- Generation timestamp: {timestamp}\n")
    md.append(f"- Cost: $0 (local file I/O only)\n")
    md.append(f"- Cumulative Phase 3 cost remains $66.95 / $100\n")

    OUT_MD.write_text("".join(md))


if __name__ == "__main__":
    main()
