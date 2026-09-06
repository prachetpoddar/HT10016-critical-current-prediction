"""
retrace_variance_decomposition.py

Claim 2 of Table III, recomputed from the anchor tables without importing any
of the code that produced the published figures.

The published route is analysis/apply_jc_anchor_repairs.py and the deposited
audit/variance_decomposition_repaired.csv. This script reads only
data/phase_3_p31_jc_anchor_per_paper.csv and its _repaired sibling and
recomputes, from scratch:

    eta squared   the fraction of within-family variance in the anchor that
                  differences between sample forms account for
    omega squared the bias-corrected version of the same quantity
    p             a permutation probability under the null that respects the
                  clustering, shuffling the sample-form label between PAPERS
                  rather than between records
    the p floor   the smallest probability the clustered null can return,
                  which is one over the number of distinct paper labellings

Run from the repository root.
"""
import itertools
import os
import re

import numpy as np
import pandas as pd

DEP = os.path.join("data", "phase_3_p31_jc_anchor_per_paper.csv")
REP = os.path.join("data", "phase_3_p31_jc_anchor_per_paper_repaired.csv")
OUT = os.path.join("audit", "retrace_20260906",
                   "variance_decomposition_retrace.csv")
VALUE, GROUP, CLUSTER = "log10_Jc_anchor", "sample_form", "paper_key"
ISO = re.compile(r"[_\-]\d+(?:\.\d+|_\d+)?\s*K$", re.IGNORECASE)

# The MAGLAB identifiers put the isotherm in the paper_id, and no regex parses
# them reliably: the specimen token is itself numeric, so "MAGLAB_11_6K" is
# specimen 11 at 6 K and not specimen "MAGLAB" at 11.6 K. A general pattern
# reads it the second way, which is how this retrace first produced 13 and 11
# samples for the chalcogenide and 122 families instead of 12 and 10. The set
# is closed at ten records, so it is enumerated. Every key is asserted to
# exist in the table below.
MAGLAB_SPECIMEN = {
    "MAGLAB_11_4_2K": "MAGLAB_11",
    "MAGLAB_11_6K": "MAGLAB_11",
    "MAGLAB_Co122_4_2K": "MAGLAB_Co122",
    "MAGLAB_Co122_4_2K_zero": "MAGLAB_Co122",
    "MAGLAB_La1111_4_2K": "MAGLAB_La1111",
    "MAGLAB_Nd1111_10K": "MAGLAB_Nd1111",
    "MAGLAB_Nd1111_4_2K": "MAGLAB_Nd1111",
    "MAGLAB_Ni122_4_2K": "MAGLAB_Ni122",
    "MAGLAB_P122_4_2K": "MAGLAB_P122",
    "MAGLAB_Sm1111_4_2K": "MAGLAB_Sm1111",
}


def specimen(pid):
    return MAGLAB_SPECIMEN.get(pid, pid)


def strip_isotherm(v):
    """Drop an isotherm-temperature suffix from an identifier.

    The suffix appears on sample_id for most papers and on paper_id for the
    MAGLAB records, which carry sample_id='unspecified'. Stripping only
    sample_id leaves the MAGLAB isotherms of one physical sample counted as
    separate samples, which is the difference between the two deposited
    decompositions: data/phase_3_p31_variance_decomposition.csv strips both
    and gives 12 and 10 samples for the chalcogenide and 122 families, while
    data/phase_3_p58_variance_stability.csv strips one and gives 13 and 11.
    """
    return ISO.sub("", str(v)).strip()


def collapse(df):
    """One record per physical sample, as analysis/figure_4_source.py does."""
    df = df.copy()
    # The guard has to run table -> map, not map -> table. Asserting that every
    # key exists in the table fires spuriously when a withdrawal removes a
    # mapped row, and passes silently on the case that matters: a MAGLAB
    # identifier the map does not know, which is then treated as its own
    # specimen. An unmapped MAGLAB_11_9K row moves the chalcogenide cohort
    # from 12 samples to 13 and its eta squared from 0.374 to 0.408.
    unmapped = sorted({p for p in df.paper_id.astype(str)
                       if p.startswith("MAGLAB") and p not in MAGLAB_SPECIMEN})
    if unmapped:
        raise SystemExit("MAGLAB identifier(s) with no specimen mapping, which "
                         "would each be counted as a separate physical "
                         "sample: %s" % ", ".join(unmapped))
    df["paper_key"] = df.paper_id.map(specimen)
    df["sample_key"] = df.sample_id.map(strip_isotherm)
    g = (df.groupby(["substructure", "paper_key", "sample_key", GROUP],
                    as_index=False)
           .agg(**{VALUE: (VALUE, "mean"),
                   "n_isotherms": (VALUE, "count")}))
    return g


def sums_of_squares(y, g):
    """Between-group and within-group sums of squares, one way."""
    y = np.asarray(y, float)
    grand = y.mean()
    ssb = 0.0
    for lab in pd.unique(g):
        v = y[np.asarray(g) == lab]
        ssb += len(v) * (v.mean() - grand) ** 2
    sst = ((y - grand) ** 2).sum()
    return ssb, sst - ssb


def eta2(y, g):
    ssb, ssw = sums_of_squares(y, g)
    return np.nan if (ssb + ssw) == 0 else ssb / (ssb + ssw)


def omega2(y, g):
    """Bias-corrected effect size. Negative when between-group mean squares
    fall below the within-group mean square, which is a real outcome and is
    not clipped to zero here."""
    ssb, ssw = sums_of_squares(y, g)
    n, k = len(y), pd.unique(g).size
    if n - k <= 0 or (ssb + ssw) == 0:
        return np.nan
    ms_w = ssw / (n - k)
    return (ssb - (k - 1) * ms_w) / (ssb + ssw + ms_w)


def multiset_arrangements(labels):
    """Distinct arrangements of a multiset, without enumerating n! of them.

    itertools.permutations over the per-paper labels generates n! tuples and
    then dedups to a support of a few hundred. At seven papers that is 5040
    and harmless; at twelve it is 479 million.
    """
    labels = sorted(labels)
    out = []

    def rec(remaining, acc):
        if not remaining:
            out.append(tuple(acc))
            return
        prev = None
        for i, v in enumerate(remaining):
            if v == prev:
                continue
            prev = v
            rec(remaining[:i] + remaining[i + 1:], acc + [v])

    rec(labels, [])
    return out


def clustered_labellings(df):
    """Every distinct assignment of the observed form labels to papers.

    Sample form is a property of the paper in this corpus, so a null that
    shuffles the label between records would break the clustering and return
    a probability the design cannot support. The support of the clustered
    null is the set of permutations of the per-paper labels.
    """
    per_paper = df.groupby(CLUSTER)[GROUP].agg(lambda s: s.iloc[0])
    papers = list(per_paper.index)
    labels = list(per_paper.values)
    return papers, labels, multiset_arrangements(labels)


def clustered_p(df):
    """Exact p over the clustered null, plus the floor that null imposes."""
    papers, labels, support = clustered_labellings(df)
    assign = {p: i for i, p in enumerate(papers)}
    idx = df[CLUSTER].map(assign).to_numpy()
    y = df[VALUE].to_numpy(float)
    # The observed statistic has to be a member of the null's support, or the
    # p is a tail probability for a value the null cannot produce. Where a
    # paper carries two sample forms, the per-record labelling is not one of
    # the clustered null's arrangements: for the deposited 122 family the
    # per-record eta squared is 0.4877 while the null's identity arrangement
    # gives 0.5092, and no arrangement equals 0.4877. Both are reported.
    ident = np.asarray(list(df.groupby(CLUSTER)[GROUP]
                            .agg(lambda s: s.iloc[0]).values),
                       dtype=object)[idx]
    obs_record = eta2(y, df[GROUP].to_numpy())
    obs_null = eta2(y, ident)
    if not np.isfinite(obs_null):
        return np.nan, np.nan, np.nan, len(support)
    vals = np.array([eta2(y, np.asarray(a, dtype=object)[idx])
                     for a in support], float)
    p_record = float(np.mean(vals >= obs_record - 1e-12))
    p_null = float(np.mean(vals >= obs_null - 1e-12))
    return p_record, p_null, 1.0 / len(support), len(support)


def one_paper_one_form(df):
    """How many papers carry more than one sample form."""
    return int((df.groupby(CLUSTER)[GROUP].nunique() > 1).sum())


def run(path, cohort, live_only):
    df = pd.read_csv(path)
    if live_only and "withdrawn" not in df.columns:
        raise SystemExit("%s has no withdrawn column, so the repaired cohort "
                         "cannot be selected" % path)
    if live_only:
        # withdrawn holds the reason as a string, empty when the row is kept.
        # An astype(bool) here marks every row True, including the NaNs, and
        # empties the cohort silently.
        before = len(df)
        df = df[df.withdrawn.isna()]
        if before - len(df) != 26:
            raise SystemExit("the repair withdraws 26 of the 96 anchor rows "
                             "per Sec. III.F; this file drops %d"
                             % (before - len(df)))
    df = df[df[VALUE].notna()]
    df = collapse(df)
    rows = []
    for fam, grp in df.groupby("substructure"):
        if grp[GROUP].nunique() < 2:
            rows.append(dict(cohort=cohort, substructure=fam, n=len(grp),
                             papers=grp[CLUSTER].nunique(),
                             forms=grp[GROUP].nunique(), eta2=np.nan,
                             omega2=np.nan, p_clustered=np.nan,
                             p_floor=np.nan, support=0,
                             multiform_papers=one_paper_one_form(grp)))
            continue
        p, p_null, floor, sup = clustered_p(grp)
        rows.append(dict(
            cohort=cohort, substructure=fam, n=len(grp),
            papers=grp[CLUSTER].nunique(), forms=grp[GROUP].nunique(),
            eta2=eta2(grp[VALUE], grp[GROUP]),
            omega2=omega2(grp[VALUE].to_numpy(float), grp[GROUP].to_numpy()),
            p_clustered=p, p_clustered_null_consistent=p_null,
            p_floor=floor, support=sup,
            multiform_papers=one_paper_one_form(grp)))
    return pd.DataFrame(rows)


def main():
    if not os.path.isdir("data"):
        raise SystemExit("run from the repository root")
    out = pd.concat([run(DEP, "deposited", False),
                     run(REP, "repaired", True)], ignore_index=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.to_csv(OUT, index=False)

    show = ["cohort", "substructure", "n", "papers", "forms", "eta2",
            "omega2", "p_clustered", "p_clustered_null_consistent", "p_floor",
            "support", "multiform_papers"]
    print(out[show].to_string(index=False,
                              float_format=lambda v: "%.4f" % v))
    print("\nwrote %s" % OUT)

    print("\nagainst the manuscript, Sec. III.A")
    want = {("deposited", "iron_chalcogenide_11"): 0.37,
            ("deposited", "iron_pnictide_122"): 0.49,
            ("deposited", "conventional_AlB2"): 0.12,
            ("repaired", "iron_chalcogenide_11"): 0.81,
            ("repaired", "iron_pnictide_122"): 0.37,
            ("repaired", "conventional_AlB2"): 0.04}
    bad = 0
    for (coh, fam), target in sorted(want.items()):
        row = out[(out.cohort == coh) & (out.substructure == fam)]
        got = float(row.eta2.iat[0]) if len(row) else float("nan")
        ok = abs(got - target) < 0.005
        bad += 0 if ok else 1
        print("   %-10s %-22s manuscript %.2f   retrace %.4f   %s"
              % (coh, fam, target, got, "ok" if ok else "MISMATCH"))
    n_rep = out[(out.cohort == "repaired")
                & (out.substructure == "iron_pnictide_122")].n
    got_n = int(n_rep.iat[0]) if len(n_rep) else -1
    if got_n != 5:
        bad += 1
    print("\n   the sample count beside 0.37: manuscript says 5 after the "
          "2026-09-06 repair; retrace says %s   %s"
          % (got_n if got_n >= 0 else "n/a", "ok" if got_n == 5 else "MISMATCH"))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
