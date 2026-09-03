"""
fix_substructure_classifier.py

Correct two substructure misclassifications in the anchor table, and the
formula label that produced one of them.

The defect. `assign_substructure` in phase_3_p39_multi_stage_predictor.py tests
literal substrings of the formula string, and two spellings defeat it:

  Fe0.975Cu0.025Te0.66Se0.34   Cu-doped FeTe0.66Se0.34. Contains neither "FeTe"
                               nor "FeSe" because the Cu sits between them.
  Ba_Fe_Co_2As2                the underscore-sanitised spelling of
                               Ba(Fe,Co)2As2. Contains neither "BaFe" nor
                               "Fe2As2" nor "(Fe".

Both fall into other_unclassified, and neither is a judgement call. The anchor
table already gives the Cu-doped rows the iron chalcogenide reference field of
47.0 T while calling them unclassified, and provenance_table_fitcohort_full.csv
calls the Ba(Fe,Co) record iron_pnictide_122. The deposit contradicts its own
label in both cases.

The fix is to the matcher, not to the two names. Separators are normalised, so
an underscore or comma spelling matches; the 11-type test is on the element set,
Fe with Te or Se and neither As nor O, so a dopant between the cation and the
chalcogen cannot hide it; and the 1111 test runs before 122 and is also on the
element set, so the Materials Project reduced spellings La2FeAs2O and its
relatives resolve to 1111 rather than being caught by the FeAs2 rule.

SCOPE, which matters. `assign_substructure` reproduces 100% of the labels in
phase_3_p31_jc_anchor_per_paper.csv and only 26.6% of those in the candidate
tables and 48.8% in the temperature-axis fit table. Those were labelled by a
different classifier that is not in the deposit, and it knows spellings this one
does not, Al0.01B2Mg0.99 for the MgB2 class among them. Applying the corrected
matcher to them would relabel 1323 of 2097 dispatch rows into
other_unclassified and destroy the dispatch. So the relabel is applied to the
anchor table only, and the script asserts that scope rather than assuming it.

Effect, through the deposit's own aggregate_per_physical_sample:

    iron_chalcogenide_11   0.7687 A (n=10)  ->  0.3737 B (n=12)
    iron_pnictide_122      0.3452 B (n= 9)  ->  0.4877 B (n=10)
    other_unclassified     0.9880 A (n= 3)  ->  dissolves

The last is a clean removal: that Outcome A was three unrelated samples pooled
because their formulas were spelled unusually.

Idempotent. Run with --dry-run to see the effect without writing.
"""
import argparse
import os
import re
import shutil
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ANCHOR = os.path.join("data", "phase_3_p31_jc_anchor_per_paper.csv")
PREDICTOR = os.path.join("analysis", "phase_3_p39_multi_stage_predictor.py")

# The Cu-free control of the Cu study carries the doped formula. Its sample_id
# is the correct composition; the compound_formula column was copied down from
# the row above, which is part of why the pair was misfiled together.
FORMULA_FIX = [("springer_10.1038_s41598-025-24806-x", "Fe0.99Te0.66Se0.34",
                "Fe0.975Cu0.025Te0.66Se0.34", "Fe0.99Te0.66Se0.34")]

NEW_FUNC = '''def assign_substructure(compound: str) -> str:
    """Refined classifier per P5.7-prime maintenance.

    Authoritative for data/phase_3_p31_jc_anchor_per_paper.csv, whose labels it
    reproduces exactly. It is NOT the classifier that labelled the candidate
    tables or the temperature-axis fit table: it reproduces 26.6% and 48.8% of
    those, which use Materials Project reduced spellings such as
    Al0.01B2Mg0.99 that this function does not know. Do not relabel those tables
    with it.
    """
    c = compound or ""
    # Normalise separators first. Ba_Fe_Co_2As2 is the sanitised spelling of
    # Ba(Fe,Co)2As2 and matched none of the rules below without this.
    n = re.sub(r"[_(),\\s-]", "", c)
    els = set(re.findall(r"[A-Z][a-z]?", n))
    if "Nb3Sn" in n or "V3Si" in n or "V3Ga" in n:
        return "conventional_A15"
    if "MgB2" in n or "MgB2xCx" in n or "MgB(2-x)Cx" in c:
        return "conventional_AlB2"
    # 1111 before 122, and on the element set, so that the Materials Project
    # reduced spelling La2FeAs2O of LaFeAsO is not caught by the FeAs2 rule.
    # No 122 in this corpus carries oxygen.
    if "FeAsO" in n or ("Fe" in els and "As" in els and "O" in els):
        return "iron_pnictide_1111"
    # Element set for the 11-type, so that a dopant sitting between the cation
    # and the chalcogen cannot hide it: Fe0.975Cu0.025Te0.66Se0.34 is
    # FeTe0.66Se0.34 with 2.5% Cu on the Fe site.
    if ("Fe" in els and ("Te" in els or "Se" in els)
            and "As" not in els and "O" not in els):
        return "iron_chalcogenide_11"
    if ("FeTe" in n or "FeSe" in n) and "FeAs" not in n:
        return "iron_chalcogenide_11"
    if "Fe2As2" in n or "BaFe" in n or "(Fe" in c or "FeAs2" in n:
        return "iron_pnictide_122"
    if ("YBa" in n or "REBCO" in n or "SmBa" in n or "GdBa" in n
            or "NdBa" in n or "YBaCuO" in n):
        return "cuprate_RBCO"
    if "Hg" in n and "Cu" in n and ("Ba" in n or "Sr" in n):
        return "cuprate_HBCCO"
    if "BSCCO" in n or "Bi-22" in c or "Bi22" in n:
        return "cuprate_BSCCO"
    if "Bi" in n and "Sr" in n and "Cu" in n:
        return "cuprate_BSCCO"
    if "La" in n and "Cu" in n and "O" in n and "Ba" not in n:
        return "cuprate_LSCO"
    return "other_unclassified"
'''


def patch_predictor(dry):
    src = open(PREDICTOR, encoding="utf-8").read()
    if "Normalise separators first" in src:
        print("   classifier      already patched")
        return True
    start = src.index("def assign_substructure(compound: str) -> str:")
    end = src.index("def regime_from_variance_ratio(")
    if "import re" not in src.split("\n\n")[0] and "\nimport re\n" not in src:
        src = src.replace("\nimport ", "\nimport re\nimport ", 1)
    out = src[:start] + NEW_FUNC + "\n\n" + src[end:]
    if not dry:
        open(PREDICTOR, "w", encoding="utf-8").write(out)
    print("   classifier      %s" % ("would patch" if dry else "patched"))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")

    print("correcting the substructure classifier\n")
    patch_predictor(a.dry_run)

    for m in list(sys.modules):
        if "phase_3_p39" in m:
            del sys.modules[m]
    exec_ns = {}
    exec(compile(NEW_FUNC, "<classifier>", "exec"), {"re": re}, exec_ns)
    classify = exec_ns["assign_substructure"]

    d = pd.read_csv(ANCHOR)
    before = d.substructure.astype(str).copy()

    # The formula copy-down, applied before classifying so the control row is
    # classified from its own composition.
    for paper, sample, wrong, right in FORMULA_FIX:
        sel = (d.paper_id == paper) & (d.sample_id == sample)
        if sel.any() and (d.loc[sel, "compound_formula"] == wrong).all():
            print("   formula label   %s -> %s  (%s)" % (wrong, right, sample))
            if not a.dry_run:
                d.loc[sel, "compound_formula"] = right
            else:
                d.loc[sel, "compound_formula"] = right
        elif sel.any():
            print("   formula label   already corrected")

    after = d.compound_formula.astype(str).map(classify)
    changed = before != after
    print("\n   anchor rows relabelled: %d of %d" % (changed.sum(), len(d)))
    for _, r in d[changed].iterrows():
        print("      %-30s %-28s %-20s -> %s"
              % (str(r.sample_id)[:30], str(r.compound_formula)[:28],
                 before[r.name], after[r.name]))

    # Scope guard. Every row this script does NOT intend to move must be
    # reproduced exactly by the corrected classifier, or the relabel is wider
    # than the defect and must not be written.
    unintended = [(b, w) for b, w in zip(before[~changed], after[~changed])
                  if b != w]
    if unintended:
        sys.exit("the corrected classifier disagrees with %d row(s) it was not "
                 "meant to touch; refusing to write" % len(unintended))
    if changed.sum() > 4:
        sys.exit("expected at most 4 relabelled rows, got %d; refusing to "
                 "write" % changed.sum())

    if a.dry_run:
        print("\ndry run, nothing written")
        return 0
    d["substructure"] = after
    if not os.path.exists(ANCHOR + ".pre_classifier_fix"):
        shutil.copy2(ANCHOR, ANCHOR + ".pre_classifier_fix")
    d.to_csv(ANCHOR, index=False)
    print("\nwritten: %s  (backup at %s.pre_classifier_fix)" % (ANCHOR, ANCHOR))
    print("now regenerate: analysis/regenerate_regime_tables.py, "
          "analysis/permutation_test.py, analysis/figure_4_source.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
