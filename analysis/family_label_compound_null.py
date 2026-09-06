"""
family_label_compound_null.py

The substructure separation against an exhaustive compound-level null.

Why. Sec. III.C reports that the family label accounts for 0.524 of the
between-paper variance in the temperature exponent, with a permutation
probability of 0.007 from shuffling the label across the seventeen source
papers. The obvious objection is that family is compound identity wearing
fewer labels: the label is constant within a compound, so a paper-level
shuffle breaks a clustering the design has. That objection is not idle. On the
within-cell scatter of raw log10 Jc, an independent review found the family
label indistinguishable from a random regrouping of the same compounds, at
probabilities of 0.60 and 0.41, which is why no family claim is made there.

Here the objection can be answered exhaustively rather than by sampling. The
seventeen papers carry eight compounds, distributed 3, 3 and 2 across the three
families. Every way of splitting eight compounds into unlabelled groups of
sizes 3, 3 and 2 can be enumerated: there are 280 of them. The null is then not
an estimate. It is the complete set of alternative family definitions with the
same shape, and the observed statistic is compared against all of them.

A second, stricter null is reported beside it. Conditioning additionally on the
number of PAPERS each family carries, 6, 4 and 7, leaves far fewer admissible
partitions, because a regrouping must reproduce the real design in paper count
as well as compound count. That is the hardest null the design admits and the
probability it gives is bounded below by one over the number of partitions.

What this does not do. It does not address the finding, recorded in
audit/retrace_20260906/temperature_axis_separation.md, that there is no
separation at all before the eleven withdrawals and that the withdrawal screen
selects on the exponent. That is a separate objection about which records are
in the cohort, and this test takes the cohort as given.

Run from the repository root.
"""
import itertools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import headline_on_repaired_cohort as H                            # noqa: E402

OUT = os.path.join("audit", "retrace_20260906", "family_compound_null.csv")
PRINTED_ETA = 0.524
# 8 compounds into unlabelled groups of 3, 3 and 2 is 8!/(3!3!2!)/2! = 280,
# of which 30 also match the family paper counts, and 3 non-empty blocks of
# 8 compounds is the Stirling number S(8,3) = 966. All three are asserted.
EXPECTED_PARTITIONS = {"compounds": 280, "papers": 30, "free": 966}


def table():
    prov = pd.read_csv(H.PROV)
    fits = pd.read_csv(H.FITS_A_REP)
    f = H.attach_family(fits, prov)
    f = f[np.isfinite(f.beta_T_repaired)]
    t, thin = H.per_paper(f, "beta_T_repaired")
    if thin:
        print("   families carried by one paper, not scored and not part of "
              "the null: %s" % ", ".join(thin))
    cm = dict(zip(prov.identifier.map(H.norm_key), prov.compound.astype(str)))
    t = t.assign(compound=[cm.get(H.norm_key(p)) for p in t.paper])
    if t.compound.isna().any():
        raise SystemExit("some papers have no compound in the provenance "
                         "table; the null cannot respect a clustering it "
                         "cannot see")
    # One compound must not span two families, or the profile is not a
    # partition of the compounds and the enumeration below is not the null it
    # claims to be.
    multi = t.groupby("compound").family.nunique()
    if (multi > 1).any():
        raise SystemExit("these compounds carry more than one family: %s"
                         % ", ".join(multi[multi > 1].index))
    return t


def unlabelled_partitions(items, sizes):
    """Every distinct way to split items into unlabelled groups of `sizes`.

    Distinct means as a set of groups: two assignments that differ only in
    which family name is attached to which group are the same alternative
    definition, and counting them twice would halve the probability.
    """
    seen = set()

    def rec(pool, remaining):
        if not remaining:
            yield []
            return
        first, rest = remaining[0], remaining[1:]
        for c in itertools.combinations(pool, first):
            left = [x for x in pool if x not in c]
            for tail in rec(left, rest):
                yield [list(c)] + tail

    for p in rec(list(items), list(sizes)):
        key = tuple(sorted(tuple(sorted(g)) for g in p))
        if key not in seen:
            seen.add(key)
            yield p


def eta_for(t, groups):
    lab = {}
    for i, g in enumerate(groups):
        for c in g:
            lab[c] = str(i)
    return H.eta_squared(t.assign(family=t.compound.map(lab)))


def all_three_block_partitions(items):
    """Every way to split the compounds into three non-empty groups.

    This is the most permissive conditioning the design admits: three families,
    the same compounds, each compound kept whole, and no constraint on how many
    compounds a family holds. It is reported first because the size-matched
    null below is floor-limited, and an independent review showed the
    paper-count-matched one cannot return a probability under 0.033 however
    clean the separation is.
    """
    items = list(items)
    first, rest = items[0], items[1:]
    # Pinning the first compound to one block removes one of the three
    # symmetries; the other two blocks can still swap, so the canonical key is
    # still needed. Without it the count comes out at 1932 rather than the
    # Stirling number 966, and every floor is wrong by a factor of two.
    seen = set()
    for assign in itertools.product(range(3), repeat=len(rest)):
        groups = [[first], [], []]
        for x, a in zip(rest, assign):
            groups[a].append(x)
        if not all(groups):
            continue
        key = tuple(sorted(tuple(sorted(g)) for g in groups))
        if key in seen:
            continue
        seen.add(key)
        yield groups


def run_free(t):
    obs = H.eta_squared(t)
    vals, n, real = [], 0, False
    truth = tuple(sorted(tuple(sorted(g.compound.unique()))
                         for _, g in t.groupby("family")))
    for p in all_three_block_partitions(sorted(t.compound.unique())):
        n += 1
        if tuple(sorted(tuple(sorted(g)) for g in p)) == truth:
            real = True
            if abs(eta_for(t, p) - obs) > 1e-9:
                raise SystemExit("relabelling the real partition through the "
                                 "null machinery gives %.6f, not the observed "
                                 "%.6f; the two are not the same statistic"
                                 % (eta_for(t, p), obs))
        vals.append(eta_for(t, p))
    if not real:
        raise SystemExit("the real family partition is not in the "
                         "three-block enumeration")
    vals = np.asarray(vals)
    hits = int((vals >= obs - 1e-12).sum())
    if hits < 1:
        raise SystemExit("the observed value is reached by no partition, not "
                         "even its own; the null and the statistic have come "
                         "apart")
    return dict(partitions=n, observed=obs, null_median=float(np.median(vals)),
                null_p95=float(np.percentile(vals, 95)),
                null_max=float(vals.max()), hits=hits, p=hits / float(n),
                floor=1.0 / n)


def run(t, condition_on_papers):
    per_family = t.drop_duplicates("compound").groupby("family").compound
    sizes = sorted(per_family.nunique().tolist(), reverse=True)
    papers = sorted(t.groupby("family").paper.nunique().tolist(), reverse=True)
    n_by_c = t.groupby("compound").paper.nunique().to_dict()
    obs = H.eta_squared(t)
    vals, kept, real_seen = [], 0, False
    truth = tuple(sorted(tuple(sorted(g.compound.unique()))
                         for _, g in t.groupby("family")))
    for p in unlabelled_partitions(sorted(t.compound.unique()), sizes):
        if condition_on_papers:
            got = sorted(sum(n_by_c[c] for c in g) for g in p)
            if got != sorted(papers):
                continue
        kept += 1
        if tuple(sorted(tuple(sorted(g)) for g in p)) == truth:
            real_seen = True
        vals.append(eta_for(t, p))
    if not real_seen:
        raise SystemExit("the real family partition is not in the enumerated "
                         "set, so the enumeration is not the null it claims "
                         "to be")
    # The count is asserted, not printed and trusted. A dedup key that loses
    # the unlabelled equivalence doubles both numerator and denominator, so
    # the probability is unchanged and only the count and the floor are wrong,
    # which is exactly the failure a printed number does not catch.
    want = EXPECTED_PARTITIONS["papers" if condition_on_papers else "compounds"]
    if kept != want:
        raise SystemExit("the enumeration produced %d partitions, not the %d "
                         "this cohort admits; either the cohort changed or "
                         "the deduplication is wrong" % (kept, want))
    vals = np.asarray(vals)
    hits = int((vals >= obs - 1e-12).sum())
    return dict(partitions=kept, observed=obs, null_median=float(np.median(vals)),
                null_p95=float(np.percentile(vals, 95)), null_max=float(vals.max()),
                hits=hits, p=hits / float(kept), floor=1.0 / kept,
                sizes=sizes, papers=papers)


def main():
    t = table()
    print("the family label against an exhaustive compound-level null\n")
    print("   %d papers, %d compounds, %d families"
          % (t.paper.nunique(), t.compound.nunique(), t.family.nunique()))
    print(t.groupby(["family", "compound"]).paper.nunique().to_string()
          .replace("\n", "\n   "))
    rows = []

    # ---- the primary null: three families, any sizes ---------------------
    fr = run_free(t)
    if fr["partitions"] != EXPECTED_PARTITIONS["free"]:
        raise SystemExit("the three-block enumeration produced %d partitions, "
                         "not the %d this cohort admits"
                         % (fr["partitions"], EXPECTED_PARTITIONS["free"]))
    print("\n   three families of any size, %d partitions, floor %.4f"
          % (fr["partitions"], fr["floor"]))
    print("      observed %.4f;  null median %.4f, 95th percentile %.4f, "
          "largest %.4f" % (fr["observed"], fr["null_median"], fr["null_p95"],
                            fr["null_max"]))
    print("      %d of %d reach the observed value, exact p %.4f"
          % (fr["hits"], fr["partitions"], fr["p"]))
    rows.append(dict(null="three blocks, any sizes",
                     **{k: v for k, v in fr.items()}))

    # ---- the size-matched nulls, reported with their floors ---------------
    for label, cond in (("compound counts only", False),
                        ("compound and paper counts", True)):
        r = run(t, cond)
        if abs(r["observed"] - PRINTED_ETA) > 5e-4:
            raise SystemExit("the observed statistic is %.4f, not the %.3f "
                             "Sec. III.C prints" % (r["observed"], PRINTED_ETA))
        print("\n   conditioning on %s: profile %s%s"
              % (label, r["sizes"],
                 " and %s papers" % r["papers"] if cond else ""))
        print("      %d distinct groupings including the real one, so the "
              "smallest probability attainable is %.4f"
              % (r["partitions"], r["floor"]))
        print("      observed %.4f;  null median %.4f, 95th percentile %.4f, "
              "largest %.4f" % (r["observed"], r["null_median"],
                                r["null_p95"], r["null_max"]))
        print("      %d of %d reach the observed value, exact p %.4f%s"
              % (r["hits"], r["partitions"], r["p"],
                 "  (at the floor, so it reports only that the real grouping "
                 "is the largest)" if abs(r["p"] - r["floor"]) < 1e-12 else ""))
        if r["null_max"] > r["observed"] + 1e-9:
            print("      one alternative grouping separates the exponent "
                  "better than the real one, at %.4f" % r["null_max"])
        rows.append(dict(null=label, **{k: v for k, v in r.items()
                                        if k not in ("sizes", "papers")}))

    # ---- the aggregation unit, which an independent review found moves it --
    tc = (t.groupby(["compound", "family"]).beta.median().reset_index()
          .assign(paper=lambda d: d.compound))
    fc = run_free(tc)
    print("\n   one row per compound instead of per paper, three blocks of "
          "any size: observed %.4f, exact p %.4f over %d partitions"
          % (fc["observed"], fc["p"], fc["partitions"]))
    rows.append(dict(null="three blocks, per compound",
                     **{k: v for k, v in fc.items()}))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("\n   wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
