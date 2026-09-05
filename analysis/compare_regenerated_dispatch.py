#!/usr/bin/env python3
"""The dispatch regenerated, against the deposited one, and what it shows.

Two adversarial reviews stand behind this file. The first version claimed the
widening of the 4.2 K dispatch spread was an effect of the withdrawals and the
anchor repair. It is not, and the claim is retracted here rather than softened.

What the run shows, in one table. Every arm below is the unmodified generator
followed by the two post-hoc gate scripts.

  deposited file                      2097 rows, 86 records at 4.2 K, span
                                      0.0098 dex, no record on a conditional
                                      predictor
  generator on the release tables     2151 rows, 86 records, span 0.2255 dex,
  (git 8ad8d43, before any            two records on a wire-conditional
  withdrawal or anchor repair)        predictor
  generator on the current tables     2151 rows, 86 records, span 0.2242 dex,
                                      the same two records

So the withdrawals and the anchor repair move the spread by 0.0013 dex, which
is 0.6 percent of it. The rest is present on the tables as released.

**The finding is therefore about the deposit, not about the corrections.** The
deposited prediction file does not reproduce from the deposited generator run
on the deposited tables. The generator, on the release tables, routes two MgB2
records from `matpr.2019.05.078` to the (conventional_AlB2, wire) conditional
cell, because their source paper's fits carry sample_form "wire" and wire is in
the generator's ENGINEERED_FORMS. The deposited file shows those records on the
substructure-aggregate predictor instead. Something between the generator and
the deposit removed the commitment, and nothing in the repository records it.

A caution that has to travel with any use of the wire cell. It holds 8 fits
from 2 papers, 6 of them from one, and the two records it predicts come from a
paper whose own 2 fits are in the pool, so a quarter of the pool is the thing
being predicted. That is the case the A4 concession describes as sample form
being very nearly a relabelling of source paper. It should not be offered to a
referee as a demonstration of conditioning.

And the 0.0098 itself carries no information. The 84 records that stay on the
aggregate predictor have identical model inputs at 4.2 K: the temperature term
is zero because 4.2 K is the reference temperature, and all 86 share a 15.5 T
anchor. They differ only in their draw from one shared bootstrap stream, and
0.0098 against 0.0085 is inside that noise, as audit/dispatch_spread_20260905.md
already established.

An environment note that invalidated a first regeneration. The generator sets
REPO to the grandparent of the repository directory and reads the extraction
index from REPO/data_agent2/v3_2_2B_extension, while the module it imports for
candidate generation hardcodes a different REPO. In a checkout where only the
second resolves, build_a2_tc_index returns an empty dict without raising, and
every extraction-derived transition temperature falls silently to a
substructure default: 612 rows on defaults where the deposit has 558 on
extraction values. The 4.2 K figure survives that, because the temperature term
is zero there, but nothing else in the file does. audit/p57_regen_20260905/
carries a manifest naming the resolved path and hashing every input.

    python analysis/compare_regenerated_dispatch.py

Run from the repository root.
"""
import os

import numpy as np
import pandas as pd

DEP = os.path.join("data", "phase_3_p57_de_novo_predictions.csv")
REGEN_DIR = os.path.join("audit", "p57_regen_20260905")
REGEN = os.path.join(REGEN_DIR, "phase_3_p57_de_novo_predictions_regenerated.csv")
RELEASE = os.path.join(REGEN_DIR,
                       "phase_3_p57_de_novo_predictions_from_release_tables.csv")
KEY = ["compound_formula", "paper_id", "T_K", "H_T"]


def emitted(path):
    x = pd.read_csv(path)
    return x, x[x.refusal_flag.fillna("") == ""]


def keyed(d):
    """Multiplicity-aware key counts.

    A set of (compound, T, H) triples collapses four duplicate rows and can
    therefore report two different emitted sets as identical. The source paper
    is added to the key and the counts are compared, not the sets.
    """
    return d.groupby(KEY).size()


def at_ref(d):
    return d[np.isclose(d.T_K, 4.2) & np.isclose(d.H_T, 5.0)]


def split(g):
    """By the predictor actually used, not by the commitment requested.

    A record can carry a sample-form commitment and still fall back to the
    aggregate pool when its cell holds fewer than three fits, so splitting on
    the commitment names a different set from the one the prediction came from.
    """
    cond = g.predictor_method_scope.astype(str).str.startswith(
        "sample_form_conditional")
    return g[~cond], g[cond]


def line(lab, x, e):
    g = at_ref(e)
    agg, cond = split(g)
    print("   %-30s %5d %6d %8.4f %9.4f %6d"
          % (lab, len(x), len(g),
             g.predicted_log_Jc.max() - g.predicted_log_Jc.min(),
             agg.predicted_log_Jc.max() - agg.predicted_log_Jc.min(),
             len(cond)))
    return g, agg, cond


def main():
    fails = []
    xd, d = emitted(DEP)
    xr, r = emitted(REGEN)
    have_rel = os.path.exists(RELEASE)
    if have_rel:
        xl, l = emitted(RELEASE)

    print("the arms\n")
    print("   %-30s %5s %6s %8s %9s %6s"
          % ("", "rows", "at ref", "span", "aggregate", "cond"))
    gd, ad, cd = line("deposited file", xd, d)
    if have_rel:
        gl, al, cl = line("generator, release tables", xl, l)
    gr, ar, cr = line("generator, current tables", xr, r)

    # Every extra row must be refused, and the emitted multiset must match.
    if len(d) != len(r):
        fails.append("emitted rows %d against %d" % (len(d), len(r)))
    kd, kr = keyed(d), keyed(r)
    if not kd.equals(kr):
        fails.append("the emitted key multisets differ on %d keys"
                     % int((kd.reindex(kr.index.union(kd.index)).fillna(0)
                            != kr.reindex(kr.index.union(kd.index)).fillna(0))
                           .sum()))

    # The premise the whole account rests on.
    for lab, g in [("deposit", gd), ("regen", gr)]:
        if g.Hc2_T_anchor.nunique() != 1:
            fails.append("%s: the records at the reference point do not share "
                         "one critical-field anchor" % lab)
        if np.abs(np.log10(np.maximum(1 - 4.2 / g.Tc_anchor_K, 1e-9))
                  - np.log10(np.maximum(1 - 4.2 / g.Tc_anchor_K, 1e-9))).max():
            pass

    # The Tc index has to have resolved. This is the silent failure that
    # invalidated a first regeneration.
    tiers = xr.Tc_provenance_tier.value_counts().to_dict()
    print("\n   Tc provenance, deposit  %s" % xd.Tc_provenance_tier
          .value_counts().to_dict())
    print("   Tc provenance, regen    %s" % tiers)
    if tiers.get("substructure_default", 0) > 0 and \
            xd.Tc_provenance_tier.value_counts().get("substructure_default",
                                                     0) == 0:
        fails.append("the regenerated file falls back to substructure default "
                     "transition temperatures where the deposit uses "
                     "extraction values, so the extraction index did not "
                     "resolve")

    # The causal question. If the release tables already show the widening, the
    # corrections are not what produced it.
    if have_rel:
        wl = gl.predicted_log_Jc.max() - gl.predicted_log_Jc.min()
        wr = gr.predicted_log_Jc.max() - gr.predicted_log_Jc.min()
        wd = gd.predicted_log_Jc.max() - gd.predicted_log_Jc.min()
        print("\n   the widening attributable to the corrections   %.4f dex, "
              "%.1f%% of %.4f" % (abs(wr - wl), 100 * abs(wr - wl) /
                                  abs(wr - wd), abs(wr - wd)))
        print("   the rest is present on the tables as released, so this is "
              "not a corrections result")

    # Values, not just keys. Nothing in a first version compared a single
    # prediction, so a regeneration that shifted every emitted value by five
    # decades would have passed.
    m = pd.merge(d, r, on=KEY, suffixes=("_d", "_r"))
    agg_shared = m[~m.predictor_method_scope_r.astype(str)
                   .str.startswith("sample_form_conditional")]
    dv = (agg_shared.predicted_log_Jc_d - agg_shared.predicted_log_Jc_r).abs()
    print("\n   on the %d emitted rows that stay on the aggregate predictor in "
          "both arms," % len(agg_shared))
    print("   the largest change in a prediction is %.4f dex" % dv.max())
    if dv.max() > 0.05:
        fails.append("an aggregate-predictor prediction moved by %.4f dex, "
                     "which the account does not explain" % dv.max())

    if cr.empty:
        fails.append("no record routes to a conditional predictor, so the "
                     "account of the widening is wrong")
    else:
        print("\n   the %d conditional records" % len(cr))
        for _i, row in cr.iterrows():
            print("      %-10s %-46s %.4f"
                  % (row.compound_formula, row.paper_id,
                     row.predicted_log_Jc))
        print("   the aggregate records sit at %.4f"
              % np.median(ar.predicted_log_Jc))

    print("\nselftest")
    for f in fails:
        print("   FAIL %s" % f)
    if fails:
        raise SystemExit("nothing here is reportable")
    print("   all checks pass")
    print("\n   Not to be published as a corrections result, and not to be "
          "offered as evidence")
    print("   for conditioning: the wire cell is 8 fits from 2 papers and the "
          "two records it")
    print("   predicts come from a paper whose own fits are a quarter of it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
