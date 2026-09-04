"""
apply_field_scale_edits.py

Bring the manuscript and the response letter into line with the supplement on
the field-scale exposure audit, and correct the eight-paper count in both the
manuscript and the supplement.

Why the three documents disagreed. analysis/recompute_supplement_numbers.py was
written to replace static numbers that had no generator, and its results were
carried into the documents by analysis/apply_manuscript_edits.py. But those two
edits sit in SUPP_EDITS and have no counterpart in MS_EDITS, so the supplement
was corrected and the manuscript and the letter were not. The manuscript still
reads 0.86 and 15 of 77 where the supplement reads 0.80 and 15 of 94, and 31 of
80 where the supplement reads 30 of 77.

Which side is right. The 77 is the number of field-axis fits in the three
dispatched families that pass, and it recomputes from the deposited fit table.
The 80 does not: no deposited fit table has ever produced it, and none of the
six pre-correction snapshots in audit/ does either. The 0.80 and the 15 of 94
come from a documented run of recompute_supplement_numbers.py; the 0.86 and the
15 of 77 come from nothing this deposit contains.

One caveat is recorded rather than hidden. The exposure ratio needs the
per-point extraction dataset, which is not deposited, so the 0.80 and the 15 of
94 cannot be recomputed here. Reconstructing that dataset from the per-paper
extraction files reproduces the median exactly, 0.800, and matches 90 of the 94
curves, giving 14 of 90. The four unmatched curves are the difference. The
count of scales that are an irreversibility field or unlabelled, 30 of 77, does
recompute from deposited tables alone.

The eight-paper count is corrected in both documents and is now recomputable:
audit/dual_model_critical_field_agreement.csv is deposited, and
recompute_supplement_numbers.py joins it to the fit table under a stated rule,
giving 56 of 77 rather than the printed 54 of 80.

Usage:
    python3 analysis/apply_field_scale_edits.py --ms MS.docx --supp S.docx \
        --letter L.docx --out-dir DIR [--dry-run]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import docx  # noqa: E402
import pandas as pd  # noqa: E402

from apply_manuscript_edits import apply  # noqa: E402

DATA = "data"
AGREEMENT = os.path.join("audit", "dual_model_critical_field_agreement.csv")
THREE = {"iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"}

# From the documented run of analysis/recompute_supplement_numbers.py that the
# supplement already carries. Not recomputable here, because the per-point
# extraction dataset is not deposited; see the module docstring.
EXPOSURE_MEDIAN = "0.80"
EXPOSURE_ABOVE = ("15", "94")


def deposit():
    import compound_leave_one_out as clo
    _bt, fr = clo.load(DATA)
    sel = fr[fr.substructure.isin(THREE)].copy()
    lab_irr = sum(1 for s in sel.Hc2_source
                  if "H_irr" in s or "Birr" in s or "ambiguous" in s)
    ag = pd.read_csv(AGREEMENT)
    eight = set(ag.loc[ag.verdict == "AGREE_NO_DATA", "paper"])

    def strip(a):
        t = str(a)
        for pre in ("elsevier_", "springer_", "iop_"):
            t = t.replace(pre, "")
        return t

    sel["key"] = sel.arxiv_id.map(strip)
    return {"three_family": len(sel), "irr_or_unlabelled": lab_irr,
            "eight_paper": int(sel.key.isin(eight).sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms", required=True)
    ap.add_argument("--supp", required=True)
    ap.add_argument("--letter", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")

    d = deposit()
    n3, irr, eight = d["three_family"], d["irr_or_unlabelled"], d["eight_paper"]
    pct = round(100.0 * eight / n3)
    words = {30: "Thirty", 31: "Thirty-one", 54: "Fifty-four",
             55: "Fifty-five", 56: "Fifty-six", 57: "Fifty-seven"}
    print("recomputed from the deposit")
    for k, v in d.items():
        print("   %-20s %s" % (k, v))
    print("   %-20s %s of %s (from the supplement's generator run)"
          % ("exposure > 0.9", EXPOSURE_ABOVE[0], EXPOSURE_ABOVE[1]))
    print()

    ms = [
        ("the median ratio of measured maximum to assigned scale is 0.86, and "
         "for 15 of the 77 curves for which the comparison is defined it "
         "exceeds 0.9.",
         "the median ratio of measured maximum to assigned scale is %s, and "
         "for %s of %s curves it exceeds 0.9."
         % (EXPOSURE_MEDIAN, EXPOSURE_ABOVE[0], EXPOSURE_ABOVE[1]),
         "matches the supplement, which carries the generator's values", None),

        ("and 31 of the 80 assigned scales are either an irreversibility field "
         "or unlabeled rather than a confirmed upper critical field.",
         "and %d of the %d assigned scales are either an irreversibility field "
         "or unlabeled rather than a confirmed upper critical field."
         % (irr, n3),
         "recomputes from the deposited fit table; no fit table has ever "
         "given 80", None),

        ("Fifty-four of the 80 field-axis curves in the three dispatched "
         "families, 68%, take their critical scale from one of those eight "
         "papers.",
         "%s of the %d field-axis curves in the three dispatched families, "
         "%d%%, take their critical scale from one of those eight papers."
         % (words.get(eight, str(eight)), n3, pct),
         "joins the deposited audit table to the fit table", None),
    ]

    supp = [
        ("Fifty-four of the 80 field-axis curves in the three dispatched "
         "families, 68%, take their scale from one of those eight papers.",
         "%s of the %d field-axis curves in the three dispatched families, "
         "%d%%, take their scale from one of those eight papers."
         % (words.get(eight, str(eight)), n3, pct),
         "joins the deposited audit table to the fit table", None),
    ]

    letter = [
        ("The median ratio of measured maximum to assigned scale is 0.86, and "
         "15 of 77 curves sit above 0.9.",
         "The median ratio of measured maximum to assigned scale is %s, and "
         "%s of %s curves sit above 0.9."
         % (EXPOSURE_MEDIAN, EXPOSURE_ABOVE[0], EXPOSURE_ABOVE[1]),
         "matches the supplement", None),
    ]

    report, misses, objs = [], [], []
    for path, edits, label in ((args.ms, ms, "manuscript"),
                               (args.supp, supp, "supplement"),
                               (args.letter, letter, "letter")):
        o = docx.Document(path)
        misses += apply(o, edits, label, report)
        objs.append((o, path))
    for label, done, find, _repl, why in report:
        print("   %-11s %-4s %s" % (label, "ok" if done else "MISS", find[:70]))
        if not done:
            print("                    %s" % why)
    print()
    if misses:
        sys.exit("%d edit(s) did not match; nothing written" % len(misses))
    if args.dry_run:
        print("all matched; --dry-run, nothing written")
        return 0
    os.makedirs(args.out_dir, exist_ok=True)
    for o, path in objs:
        out = os.path.join(args.out_dir, os.path.basename(path))
        o.save(out)
        print("written %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
