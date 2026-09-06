#!/usr/bin/env python3
"""
anchor_form_permutation.py

Exact permutation floors for the sample-form variance-decomposition diagnostic
of Sec. III.A, on both anchor cohorts.

Why this exists. Sec. III.A states that the diagnostic cannot establish its
regime labels to any standard of significance, because sample form is very
nearly a relabelling of source paper. It gave the number of distinct labellings
each family admits under that clustered null as three, four and ten. The four
and the ten are the counts under a null that preserves the observed cell sizes.
The three is not: it is the number of ways to split the three MgB2-class source
papers into two non-empty groups, which does not hold the wire and bulk counts
at 8 and 5. Under the size-preserving null the MgB2-class family admits exactly
one labelling, so its floor is p = 1 rather than p = 0.33. The same null is now
applied to all three families here and the counts are deposited.

Two nulls are reported for each family because they answer different questions.

  unclustered   every assignment of the observed sample-form labels to the
                physical samples of the family. This is the test that would be
                right if sample form varied within a source paper.

  clustered     every assignment of sample forms to SOURCE PAPERS, with each
                paper's samples all taking that paper's form, restricted to
                assignments that reproduce the observed per-form sample counts.
                This is the only null that respects the corpus structure, since
                no source paper in either cohort contributes more than one
                sample form to any of the three families drawn.

Both are enumerated exhaustively rather than sampled, so the reported p is
exact and the floor is the reciprocal of the number of labellings.

Run: python3 analysis/anchor_form_permutation.py
"""

from __future__ import annotations
import itertools
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from figure_4_source import (  # noqa: E402
    PANEL_SUBSTRUCTURES,
    SUB_COLORS,
    aggregate_per_physical_sample,
    compute_variance_decomposition,
)

DEPOSITED = ROOT / "data" / "phase_3_p31_jc_anchor_per_paper.csv"
REPAIRED = ROOT / "data" / "phase_3_p31_jc_anchor_per_paper_repaired.csv"
OUT = ROOT / "data" / "anchor_form_permutation.csv"

# What each cohort must return before anything else is reported. These are the
# ratios the two committed renders of Figure 3 have displayed: the deposited
# triple is what the pre-2026-09-06 PNG showed, the repaired triple is what the
# current one shows and what figures/manuscript_figure_3.stamp.json records.
REFERENCE = {
    "deposited": {"conventional_AlB2": 0.115886,
                  "iron_chalcogenide_11": 0.373664,
                  "iron_pnictide_122": 0.487678},
    "repaired": {"conventional_AlB2": 0.044159,
                 "iron_chalcogenide_11": 0.809011,
                 "iron_pnictide_122": 0.374292},
}


def eta_squared(values, labels) -> float:
    """Between-group share of total variance, the quantity Eq. (8) defines.

    Population convention, matching compute_variance_decomposition: sums of
    squares divided by n, so the n cancels and this is the ratio of the
    between-group sum of squares to the total.
    """
    values = np.asarray(values, dtype=float)
    labels = np.asarray(labels)
    grand = values.mean()
    total = ((values - grand) ** 2).sum()
    if total <= 0:
        return float("nan")
    between = sum(
        (labels == u).sum() * (values[labels == u].mean() - grand) ** 2
        for u in np.unique(labels)
    )
    return float(between / total)


def load(cohort: str) -> pd.DataFrame:
    """Physical-sample table for one cohort, restricted to the drawn families."""
    if cohort == "deposited":
        df = pd.read_csv(DEPOSITED)
    elif cohort == "repaired":
        df = pd.read_csv(REPAIRED)
        if "withdrawn" not in df.columns:
            raise SystemExit("the repaired anchor table has no withdrawn "
                             "column, so the repaired cohort cannot be formed")
        df = df[df["withdrawn"].isna()]
    else:
        raise SystemExit("unknown cohort %r" % cohort)
    df = df[df["substructure"].isin(SUB_COLORS)].copy()
    return aggregate_per_physical_sample(df)


def check_primitive(panel: pd.DataFrame, sub: str, cohort: str) -> float:
    """eta_squared must agree with the deposited decomposition, not merely look
    plausible. This is the primitive both nulls are built on, so it is checked
    against an independently written implementation before either runs."""
    obs = eta_squared(panel["log10_Jc_anchor"].values,
                      panel["sample_form"].values)
    dec = compute_variance_decomposition(panel)
    ref = float(dec.loc[dec["scope"] == "per_substructure",
                        "ratio_between_total"].iloc[0])
    if abs(obs - ref) > 1e-9:
        raise SystemExit(
            "eta_squared gives %.9f for %s on the %s cohort and "
            "compute_variance_decomposition gives %.9f; the two disagree, so "
            "neither null means anything" % (obs, sub, cohort, ref))
    return obs


def _distinct_arrangements(sizes: Counter):
    """Every distinct arrangement of a label multiset, without duplicates.

    itertools.permutations over the label list would emit n! sequences and
    count each distinct arrangement once per within-form reordering, which
    inflates the denominator of the permutation p by the same factor for every
    arrangement. The p is unchanged by that but the reported labelling count
    and the floor are not, and the floor is what Sec. III.A quotes. This
    enumerates arrangements, so len() of the result is the number the text can
    use.
    """
    forms = sorted(sizes)
    n = sum(sizes.values())

    def place(remaining, slots):
        if not remaining:
            yield []
            return
        form = remaining[0]
        rest = remaining[1:]
        k = sizes[form]
        for combo in itertools.combinations(slots, k):
            left = [s for s in slots if s not in combo]
            for tail in place(rest, left):
                yield [(form, combo)] + tail

    for placement in place(forms, tuple(range(n))):
        lab = [None] * n
        for form, combo in placement:
            for i in combo:
                lab[i] = form
        yield lab


def unclustered(panel: pd.DataFrame, obs: float):
    """Exhaustive permutation of the form labels over physical samples."""
    values = panel["log10_Jc_anchor"].values
    sizes = Counter(panel["sample_form"].values)
    stats = [eta_squared(values, np.asarray(lab))
             for lab in _distinct_arrangements(sizes)]
    stats = np.asarray(stats)
    return len(stats), float((stats >= obs - 1e-12).mean())


def clustered(panel: pd.DataFrame, obs: float):
    """Exhaustive assignment of forms to source papers, sizes preserved.

    Each paper carries one form for all of its samples, which is not an
    assumption but a property of both cohorts: no paper contributes two sample
    forms to any drawn family. That is asserted here rather than trusted.
    """
    per_paper = panel.groupby("paper_id")["sample_form"].nunique()
    if (per_paper > 1).any():
        # A paper spanning two forms has no place in a null that gives each
        # paper one label: the observed configuration is not reachable, so no
        # p is defined. This happens in exactly one family of the deposited
        # cohort and in none of the repaired one. It is reported as undefined
        # rather than forced, because the alternative is to invent a splitting
        # convention and then quote a floor derived from it.
        return None, None
    papers = list(dict.fromkeys(panel["paper_id"]))
    values = panel["log10_Jc_anchor"].values
    target = Counter(panel["sample_form"].values)
    forms = sorted(target)
    stats = []
    for assign in itertools.product(forms, repeat=len(papers)):
        table = dict(zip(papers, assign))
        lab = np.array([table[p] for p in panel["paper_id"]])
        if Counter(lab) != target:
            continue
        stats.append(eta_squared(values, lab))
    stats = np.asarray(stats)
    return len(stats), float((stats >= obs - 1e-12).mean())


def main():
    rows = []
    for cohort in ("deposited", "repaired"):
        table = load(cohort)
        for sub in PANEL_SUBSTRUCTURES:
            panel = table[table["substructure"] == sub]
            obs = check_primitive(panel, sub, cohort)
            want = REFERENCE[cohort][sub]
            if abs(obs - want) > 5e-6:
                raise SystemExit(
                    "the %s cohort gives %.6f for %s, not the %.6f the "
                    "committed figure displayed" % (cohort, obs, sub, want))
            n_unc, p_unc = unclustered(panel, obs)
            n_clu, p_clu = clustered(panel, obs)
            rows.append(dict(
                cohort=cohort, substructure=sub,
                n_samples=len(panel), n_papers=panel["paper_id"].nunique(),
                sample_forms="; ".join(
                    "%s %d" % kv for kv in
                    sorted(Counter(panel["sample_form"]).items())),
                eta_squared=round(obs, 6),
                unclustered_labellings=n_unc,
                unclustered_p=None if p_unc is None else round(p_unc, 4),
                unclustered_floor=None if n_unc is None else round(1 / n_unc, 4),
                clustered_labellings=n_clu,
                clustered_p=None if p_clu is None else round(p_clu, 4),
                clustered_floor=None if n_clu is None else round(1 / n_clu, 4),
            ))
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))
    print("\nwrote %s" % OUT)


if __name__ == "__main__":
    main()
