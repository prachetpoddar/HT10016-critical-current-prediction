# Phase 3 p57 — De Novo Jc(T, H) Prediction Dispatch Report
**Date**: 2026-05-11  
**Generation timestamp**: 2026-09-06T19:28:35.398180+00:00  
**Cost**: $0 (offline file I/O + local computation; no API calls)  
**Hard exclusion**: iron_pnictide_1111 enforced at candidate-list + Hc2-index + fit-pool layers.

---

## §1 — Dispatch summary

- Total candidates: 185 (at 239 dispatched-row scope)
- Total prediction tuples (candidate × grid point): 2151
- Bootstrap iterations: 5000 (seed = 42)
- Refused tuples: 765
- Refusal breakdown:
  - `Hc2_unavailable`: 540
  - `T_above_Tc`: 225
- Dispatch duration: 5.5 s
- Cost: $0

---

## §2 — Pre-registered outcome resolutions

### σ outcome: **sigma_1**

Median bootstrap CI width across non-refused predictions: **0.559 dex log Jc**.  
Triggered σ₁ (< 1.5 dex): predictions are screening-grade interpretable.

### τ outcome: **tau_2**

Top-quartile substructure distribution at (T = 4.2 K, H = 1 T):

| Substructure | Top-quartile count | Top-quartile share |
|---|---:|---:|
| iron_chalcogenide_11 | 45 | 100.0% |
| iron_pnictide_122 | 0 | 0.0% |
| conventional_AlB2 | 0 | 0.0% |

Triggered τ₂: substructure-imbalanced top-quartile (one substructure > 60%). Reporting should be substructure-conditional rather than aggregate-ranked.

### Refusal-rate diagnostic

- Fraction of unique candidates with any non-monotonic Jc(T) flag: 0.0% (< 10% threshold; screening-grade scope is primary deliverable).
- Tuple-level refusal breakdown:
  - `Hc2_unavailable`: 540 / 2151 tuples (25.1%)
  - `T_above_Tc`: 225 / 2151 tuples (10.5%)

---

## §3 — Per-substructure prediction-set statistics

Computed at reference grid point (T = 4.2 K, H = 1 T) across non-refused predictions.

| Substructure | n cand | n refused (tuples) | median log Jc | 5%–95% range | n full β_T+β_H | n T-axis-only |
|---|---:|---:|---:|---|---:|---:|
| iron_chalcogenide_11 | 31 | 171 | 5.986 | [5.965, 5.987] | 324 | 0 |
| iron_pnictide_122 | 51 | 417 | 5.741 | [5.740, 5.742] | 294 | 378 |
| conventional_AlB2 | 103 | 177 | 5.269 | [5.268, 5.272] | 768 | 162 |

---

## §4 — Top 5 per substructure (preview for §6.3 Table N)

Reference grid point: T = 4.2 K, H = 1 T. Ranked by predicted log Jc.

| Substructure | Rank | Compound | Predicted log Jc [A/cm²] | 95% CI | Sample-form commitment | Hc2 anchor | Envelope (dex) |
|---|---:|---|---:|---|---|---|---:|
| iron_chalcogenide_11 | 1 | FeTeSe | 5.987 | [5.954, 6.167] | single_crystal | exact | — |
| iron_chalcogenide_11 | 2 | FeTe0.61Se0.39 | 5.987 | [5.953, 6.165] | single_crystal | exact | — |
| iron_chalcogenide_11 | 3 | Fe1S0.1Te0.9 | 5.987 | [5.953, 6.164] | single_crystal | c_parent (±20-50%) | — |
| iron_chalcogenide_11 | 4 | Fe1S0.12Te0.88 | 5.987 | [5.953, 6.164] | single_crystal | c_parent (±20-50%) | — |
| iron_chalcogenide_11 | 5 | Fe1Se0.13Te0.87 | 5.987 | [5.953, 6.166] | single_crystal | c_parent (±20-50%) | — |
| iron_pnictide_122 | 1 | BaFe2As2 | 5.742 | [5.633, 5.801] | single_crystal | exact | — |
| iron_pnictide_122 | 2 | Ba(Fe,Ru)2As2 | 5.742 | [5.613, 5.798] | single_crystal | exact | — |
| iron_pnictide_122 | 3 | Ba(Fe,Co)2As2 | 5.742 | [5.631, 5.800] | single_crystal | exact | — |
| iron_pnictide_122 | 4 | As2Ba0.3Fe2K0.7 | 5.742 | [5.632, 5.799] | single_crystal | c_parent (±20-50%) | — |
| iron_pnictide_122 | 5 | Ba(Fe1-xCox)2As2 | 5.742 | [5.633, 5.796] | single_crystal | exact | — |
| conventional_AlB2 | 1 | B2Mg0.96Mn0.04 | 5.273 | [5.103, 5.508] | (substructure-aggregate) | c_parent (±20-50%) | 0.025 |
| conventional_AlB2 | 2 | B2Li0.07Mg0.93 | 5.272 | [5.102, 5.504] | (substructure-aggregate) | c_parent (±20-50%) | 0.027 |
| conventional_AlB2 | 3 | Al0.044B2Mg0.956 | 5.272 | [5.107, 5.511] | (substructure-aggregate) | c_parent (±20-50%) | 0.025 |
| conventional_AlB2 | 4 | Al0.185B2Mg0.815 | 5.272 | [5.103, 5.506] | (substructure-aggregate) | c_parent (±20-50%) | 0.027 |
| conventional_AlB2 | 5 | B2Mg0.95Zr0.05 | 5.272 | [5.106, 5.507] | (substructure-aggregate) | c_parent (±20-50%) | 0.027 |

---

## §5 — Methodology caveats

### conventional_AlB2 parent-match envelope (n = 84 candidates inheriting MgB2 Hc2)

- Median per-candidate envelope width: 0.024 dex log Jc
- 5%–95% envelope range: [0.000, 0.194] dex
- Hc2 perturbation factors applied: (0.8, 1.0, 1.2)
- ±20–50% deviation flag retained in metadata for every parent-match candidate.

### iron_pnictide_122 cation-variant unmatched

- Count: 42 candidates with Hc2_anchor_type = `pending` (β_T-axis-only predictions).
- Provenance: Sr/Ca/Eu/Rb/Cs-122 cation variants not present in S1/S3/S5 sources at exact or parent scope.
- Top 10 (alphabetical):
  - As1.7Eu1Fe2P0.3
  - As2Co0.068Fe1.932K1
  - As2Co0.084Fe1.916Sr1
  - As2Co0.112Fe1.888Sr1
  - As2Co0.14Fe1.86Sr1
  - As2Co0.174Fe1.826Sr1
  - As2Co0.184Fe1.816Sr1
  - As2Co0.208Fe1.792Sr1
  - As2Co0.22Eu1Fe1.78
  - As2Co0.234Fe1.766Sr1

### conventional_AlB2 exotic diboride unmatched

- Count: 18 candidates (ZrB₂, NbB₂, OsB₂ variants) with Hc2_anchor_type = `pending`.
- Top 10 (alphabetical):
  - Ag1B2
  - B2Ce0.001La0.999Rh3
  - B2Ce0.002La0.998Rh3
  - B2Ce0.003La0.997Rh3
  - B2Ce1Ru3
  - B2Ir3La1
  - B2Ir3Th1
  - B2Lu1Os3
  - B2Nb0.7
  - B2Nb0.83

### Non-monotonic Jc(T) refusal

- Affected unique compounds: 0
- Affected tuples: 0
- Fraction of total candidates: 0.0%

---

## §6 — Scope statement

Predictions are committed at substructure-aggregate Stage 3 scope. log Jc partial anchor is the substructure (× sample_form where Outcome A or B applies) cell median from canonical Cohort B v2 per-paper Form 3 fits. β_T and β_H pools are resampled with replacement at N = 5000 bootstrap iterations (seed = 42; matches Path δ + Path 19-AC reproducibility).

iron_pnictide_1111 is hard-excluded per §4.3 of the manuscript (Substep D nu-2 compound-LOO MAE 5.13 dex β_H at expanded scope). The 1111 exclusion is enforced at three layers: candidate-list, Hc2-index, and β_H/log_Jc_partial fit pool.

Default target grid: T ∈ {4.2 K, 20 K, 0.77·Tc}; H ∈ {0.1, 1, 5 T}. Advisor override of these defaults is anticipated as a separate dispatch; the pipeline is parameterised at the grid level and re-runs cheaply against any user-specified (T, H) point set.

---

## Metadata footer

- Outputs: `phase_3_p57_de_novo_predictions.csv`, `phase_3_p57_top5_table_data.csv`, `phase_3_p57_dispatch_report.md`
- Unique candidate rows (compound × MP_id × paper_id): 188 (dispatched-row scope: 239)
- Bootstrap N: 5000; seed: 42
- Generation timestamp: 2026-09-06T19:28:35.398180+00:00
- Cost: $0 (offline file I/O + local computation; no API calls)
