#!/usr/bin/env python3
"""
phase_3_p58_variance_stability.py

Stability of the sample-form variance-decomposition ratios (eta^2) reported in
the manuscript as 0.73 / 0.60 / 0.12.

Method follows figures/figure_4_source.py exactly: multi-isotherm records of one
physical sample are collapsed by mean within
(substructure, paper_id, stripped_sample_id, sample_form); eta^2 is the
n-weighted between-sample-form variance divided by the total variance, both on
the population (1/n) convention.

Three stability probes, all clustered on the source paper because records from
one paper are not independent:
  1. paper-cluster bootstrap, percentile 95% interval
  2. leave-one-paper-out
  3. label permutation test (null: sample form carries no information)

Output: phase_3_p58_variance_stability.csv + stdout summary.
"""
import re, json, random, csv
import pandas as pd, numpy as np

HERE = "."
SRC = f"{HERE}/phase_3_p31_jc_anchor_per_paper.csv"
OUT = f"{HERE}/phase_3_p58_variance_stability.csv"
FAMILIES = ["iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"]
N_BOOT, N_PERM, SEED = 5000, 10000, 42


def strip_isotherm(sid):
    if not isinstance(sid, str):
        return str(sid)
    return re.sub(r'[_\-]\d+(?:\.\d+|_\d+)?\s*K$', '', sid, flags=re.IGNORECASE).strip()


def load():
    df = pd.read_csv(SRC)
    df = df[df["substructure"].isin(FAMILIES)].copy()
    df["sample_id_stripped"] = df["sample_id"].apply(strip_isotherm)
    agg = df.groupby(["substructure", "paper_id", "sample_id_stripped", "sample_form"],
                     as_index=False).agg(log10_Jc_anchor=("log10_Jc_anchor", "mean"))
    return agg


def eta2(sub):
    """n-weighted between-form variance / total variance, population convention."""
    n = len(sub)
    if n == 0:
        return np.nan
    if sub["sample_form"].nunique() < 2:
        return np.nan
    grand = sub["log10_Jc_anchor"].mean()
    total = ((sub["log10_Jc_anchor"] - grand) ** 2).sum() / n
    gp = sub.groupby("sample_form")["log10_Jc_anchor"].agg(["mean", "count"])
    between = (gp["count"] * (gp["mean"] - grand) ** 2).sum() / n
    return float(between / total) if total > 0 else np.nan


def ordering_test(coh, n_boot=N_BOOT, seed=SEED):
    """Paper-clustered joint bootstrap: does the three-regime ordering survive?

    Resamples papers within each family independently and records how often the
    published ordering and the published regime bands are reproduced.
    """
    rng = random.Random(seed)
    papers = {f: sorted(coh[coh.substructure == f].paper_id.unique()) for f in FAMILIES}
    by = {f: {p: coh[(coh.substructure == f) & (coh.paper_id == p)] for p in papers[f]}
          for f in FAMILIES}
    draws = {f: [] for f in FAMILIES}
    for _ in range(n_boot):
        for f in FAMILIES:
            d = pd.concat([by[f][rng.choice(papers[f])] for _ in papers[f]], ignore_index=True)
            draws[f].append(eta2(d))
    D = {f: np.array(draws[f]) for f in FAMILIES}
    ok = ~np.isnan(D[FAMILIES[0]]) & ~np.isnan(D[FAMILIES[1]]) & ~np.isnan(D[FAMILIES[2]])
    a, b, c = (D[f][ok] for f in FAMILIES)
    return dict(
        usable_resamples=int(ok.sum()), n_boot=n_boot,
        p_chal_gt_mgb2=round(float((a > c).mean()), 4),
        p_122_gt_mgb2=round(float((b > c).mean()), 4),
        p_chal_gt_122=round(float((a > b).mean()), 4),
        p_full_ordering=round(float(((a > b) & (b > c)).mean()), 4),
        p_chal_strong_gt_0p7=round(float((a > 0.7).mean()), 4),
        p_122_intermediate_0p3_0p7=round(float(((b >= 0.3) & (b <= 0.7)).mean()), 4),
        p_mgb2_weak_lt_0p3=round(float((c < 0.3).mean()), 4),
    )


def main():
    rng = random.Random(SEED)
    npr = np.random.default_rng(SEED)
    coh = load()
    rows = []
    for fam in FAMILIES:
        sub = coh[coh["substructure"] == fam].reset_index(drop=True)
        point = eta2(sub)
        papers = sorted(sub["paper_id"].unique())
        by = {p: sub[sub["paper_id"] == p] for p in papers}

        boots, degenerate = [], 0
        for _ in range(N_BOOT):
            draw = pd.concat([by[rng.choice(papers)] for _ in papers], ignore_index=True)
            v = eta2(draw)
            if np.isnan(v):
                degenerate += 1
            else:
                boots.append(v)
        boots = np.sort(np.array(boots))
        lo, hi = (np.percentile(boots, 2.5), np.percentile(boots, 97.5)) if len(boots) else (np.nan, np.nan)

        lopo = []
        for p in papers:
            v = eta2(sub[sub["paper_id"] != p].reset_index(drop=True))
            lopo.append((p, v))
        lv = [v for _, v in lopo if not np.isnan(v)]
        worst = min(lopo, key=lambda t: (np.inf if np.isnan(t[1]) else t[1]))

        perm = []
        labels = sub["sample_form"].to_numpy()
        for _ in range(N_PERM):
            s2 = sub.copy()
            s2["sample_form"] = npr.permutation(labels)
            v = eta2(s2)
            if not np.isnan(v):
                perm.append(v)
        perm = np.array(perm)
        pval = float((perm >= point).mean()) if len(perm) else np.nan

        rows.append(dict(substructure=fam, n_samples=len(sub), n_papers=len(papers),
                         n_sample_forms=int(sub["sample_form"].nunique()),
                         eta2_point=round(point, 4),
                         boot_lo95=round(float(lo), 4), boot_hi95=round(float(hi), 4),
                         boot_median=round(float(np.median(boots)), 4) if len(boots) else np.nan,
                         boot_degenerate_draws=degenerate,
                         lopo_min=round(float(min(lv)), 4), lopo_max=round(float(max(lv)), 4),
                         lopo_worst_paper=worst[0],
                         perm_p=round(pval, 4), perm_median=round(float(np.median(perm)), 4)))

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ordering = ordering_test(coh)
    with open(OUT.replace(".csv", "_ordering.json"), "w") as fh:
        json.dump(ordering, fh, indent=1)
    pd.set_option("display.width", 200)
    print(out.to_string(index=False))
    print("\nPaper-clustered ordering test (%d of %d resamples usable):"
          % (ordering["usable_resamples"], ordering["n_boot"]))
    for k, v in ordering.items():
        if k.startswith("p_"):
            print("   %-32s %.3f" % (k, v))
    return out, ordering


if __name__ == "__main__":
    main()
