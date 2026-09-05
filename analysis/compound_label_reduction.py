"""
compound_label_reduction.py

How many distinct composition keys are behind the 35 distinct compound labels
of Table I, and which labels denote the same material.

Why this exists. Table I counts labels, not materials, and the labels come
from two naming systems. Cohort A rows carry the formula the structure
registry returns; Cohort B rows carry the stoichiometry the paper prints. So
one material can appear twice, and one label can cover two dopings:

    Pr2FeAs2O and PrFeAsO0.6F0.12   the same specimen set, the same paper
    Ba(FeAs)2 at 38 K and BaFe2As2 at 20 K   different dopings, one label

Section II.D of the manuscript already gives the mapping table. What it did
not say, until an independent review of the figures raised it, is that the
count of 35 in Table I is a count of labels and is not the number of distinct
materials.

The reduction rule, stated rather than eyeballed. Two labels share a key when
they reduce to the same (substructure family, element set, dopant marker),
where the reduction strips stoichiometric coefficients and parenthesis
grouping and lifts the _X_doped suffix into the dopant field. Doping variants
of one parent keep separate keys; naming variants of one composition merge.

The rule is mechanical, and its output is neither an upper nor a lower bound
on the number of materials. It merges Fe9Se8 with FeSe, which are different
compounds, and it leaves PrFeAsO0.6F0.12 apart from Pr2FeAs2O, which are the
same one, because only the first carries fluorine. It is reported as what it
is: the number of distinct composition keys under a stated rule.

What depends on the labels. Nothing in the aggregation, which groups by
substructure family and sample form. The one analysis that groups by label is
the compound leave-one-out, and this script reports its two cohorts
separately, because a material appearing under two labels inside one cohort is
not fully held out.

Run from the repository root.
"""
import re
from collections import defaultdict

import pandas as pd

ELEM = re.compile(r"[A-Z][a-z]?")

# Where the mechanical rule is known to be wrong, in both directions. These are
# read off the labels by hand and are reported beside the rule's output rather
# than folded into it, so the count stays reproducible and its errors stay
# visible.
RULE_MERGES_WRONGLY = [("Fe9Se8", "FeSe")]
RULE_SEPARATES_WRONGLY = [("Pr2FeAs2O", "PrFeAsO0.6F0.12"),
                          ("Sm2FeAs2O", "SmFeAsO0.8F0.2"),
                          ("Sm2FeAs2O", "SmFeAsO_F_doped"),
                          ("La2FeAs2O", "LaFeAsO_F_doped"),
                          ("FeSe_Te_doped", "FeTe0.5Se0.5")]


def key(label):
    """(element set, dopant) for one compound label, under the stated rule."""
    s, dop = label, ""
    m = re.search(r"_([A-Za-z]+)_doped$", s)
    if m:
        dop = m.group(1)
        s = s[:m.start()]
    s = re.sub(r"_x_[\d_]+$", "", s)      # MgB(2-x)Cx_x_0_0386
    s = s.replace("-x", "")
    body = re.sub(r"[\d.(),]", "", s)     # coefficients and grouping go
    return tuple(sorted(set(ELEM.findall(body)))), dop


def reduce_labels(rows):
    """label -> key groups, for an iterable of (family, label) pairs."""
    groups = defaultdict(set)
    for fam, lab in rows:
        groups[(fam,) + key(lab)].add(lab)
    return groups


def main():
    prov = pd.read_csv("data/provenance_table_fitcohort_full.csv")
    live = prov[prov.contributes != "none, withdrawn"]
    groups = reduce_labels(zip(live.substructure_family, live.compound))

    print("the fit cohort")
    print("   distinct compound labels        %3d" % live.compound.nunique())
    print("   distinct composition keys       %3d" % len(groups))
    print()
    print("   labels that share a key")
    for k in sorted(groups):
        labs = sorted(groups[k])
        if len(labs) > 1:
            print("      %-22s %s" % (k[0], ", ".join(labs)))
    print()

    bt = pd.read_csv("data/phase_3_p44_post_UCLA_beta_T_fits_repaired.csv")
    keep = bt[bt.reproduced & bt.beta_T_repaired.notna()]
    tg = reduce_labels(zip(keep.substructure, keep.compound_formula))
    print("the compound leave-one-out cohorts, which are the only place a "
          "label is a unit")
    print("   temperature axis   %d labels, %d keys"
          % (keep.compound_formula.nunique(), len(tg)))
    for k in sorted(tg):
        labs = sorted(tg[k])
        if len(labs) > 1:
            print("      shares a key: %s" % ", ".join(labs))

    # The field-axis cohort is named by paper in audit/fit_protocol_applied.csv
    # and its compound labels come from the provenance table, so it is resolved
    # through the paper identifier rather than read from a compound column.
    prot = pd.read_csv("audit/fit_protocol_applied.csv")
    adm = prot[prot.admitted]
    ids = live.set_index(live.identifier.astype(str).str.replace("/", "_",
                                                                regex=False))
    pairs = []
    for paper in sorted(adm.paper.unique()):
        base = str(paper).replace(".pdf", "")
        for pre in ("elsevier_", "springer_"):
            if base.startswith(pre):
                base = base[len(pre):]
        hit = ids[ids.index.str.contains(base.replace("/", "_"), regex=False)]
        if len(hit) == 0:
            raise SystemExit("no provenance row for admitted paper %r" % paper)
        for _, r in hit.iterrows():
            pairs.append((r.substructure_family, r.compound))
    fg = reduce_labels(pairs)
    labs = {lab for _, lab in pairs}
    print("   field axis         %d labels, %d keys" % (len(labs), len(fg)))
    for k in sorted(fg):
        got = sorted(fg[k])
        if len(got) > 1:
            print("      shares a key: %s" % ", ".join(got))

    print()
    print("where the rule is wrong")
    seen = set(live.compound)
    for a, b in RULE_MERGES_WRONGLY:
        if {a, b} <= seen:
            print("      merges but should not:   %s, %s" % (a, b))
    for a, b in RULE_SEPARATES_WRONGLY:
        if {a, b} <= seen:
            print("      separates but should not: %s, %s" % (a, b))
    tlabs = set(keep.compound_formula)
    hit = [(a, b) for a, b in RULE_SEPARATES_WRONGLY if {a, b} <= tlabs]
    print()
    print("      inside the temperature-axis cohort, the rule's only shared "
          "key is a pair")
    print("      of different compounds, and no pair it separates should be "
          "merged: %s" % ("none" if not hit else hit))
    flabs = labs
    hitf = [(a, b) for a, b in RULE_SEPARATES_WRONGLY if {a, b} <= flabs]
    print("      inside the field-axis cohort, the pairs the rule wrongly "
          "separates are: %s" % ("none" if not hitf else hitf))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
