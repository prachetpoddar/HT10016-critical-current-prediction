#!/usr/bin/env python3
"""Stop the abstract, introduction and conclusion asserting what Sec. III.A
concedes cannot be tested.

Decision taken: keep the regimes and keep the numbers, drop the word that
overclaims. Sec. III.A and the A4 answer now report the regime labels as the
rule the predictor follows rather than as a tested finding, because sample form
is very nearly a relabelling of source paper in this corpus: one of 29
contributing papers carried more than one form before the anchor repair and
none of 20 does after it, and the clustered null admits three labellings for
the MgB2 cell. Four passages elsewhere still state the distinction as a
finding, and a referee reading the abstract against Sec. III.A would find them.

No number changes. The abstract's 37, 49 and 12 percent are the deposited-anchor
values and they stay, as does Sec. III.E's 0.37, which is the ratio the
dispatch rule is actually keyed to.

Source out_a6/*_final5.docx, output out_regimes/.

    python analysis/apply_two_regime_edits.py --dry-run
    python analysis/apply_two_regime_edits.py --out-dir out_regimes

Run from the repository root.
"""
import argparse
import os

import docx

SRC = "out_a6"
MS = "HT10016_revised_final5.docx"

EDITS = [
    # abstract
    ("and returns two distinct regimes across the studied families: sample "
     "form explains 37% of the within-family variance in the critical-current "
     "anchor for iron chalcogenide 11-type materials, 49% for iron pnictide "
     "122-type, and 12% for MgB2-class.",
     "and assigns two distinct regimes across the studied families: sample "
     "form explains 37% of the within-family variance in the critical-current "
     "anchor for iron chalcogenide 11-type materials, 49% for iron pnictide "
     "122-type, and 12% for MgB2-class. These regimes set the conditioning "
     "rule the predictor follows. Because sample form is very nearly a "
     "relabelling of source paper in this corpus, the separation between them "
     "is not established at any useful significance, and we state the "
     "measurement that would establish it.",
     "the abstract"),
    # introduction
    ("It converts the conditioning structure from an assumption made by the "
     "modeler into a hypothesis tested against the literature, and in doing so "
     "it tells the model not only what to predict but also when to stay "
     "silent.",
     "It converts the conditioning structure from an assumption made by the "
     "modeler into a question put to the literature, and in doing so it tells "
     "the model not only what to predict but also when to stay silent. "
     "Whether this literature can answer that question is itself a result of "
     "the work, and Section III.A reports that on this corpus it cannot, "
     "because sample form arrives one paper at a time.",
     "the introduction"),
    # Sec. III.E, the dispatch rule
    ("sample-form conditioning is informative but not decisive at a ratio of "
     "0.37,",
     "sample-form conditioning is informative but not decisive at a ratio of "
     "0.37 on the deposited anchors,",
     "the dispatch rule"),
    # conclusion
    ("A variance-decomposition diagnostic determines, family by family, "
     "whether sample-form conditioning is required, returning two distinct "
     "regimes across the studied families, and explicit refusal gates prevent "
     "predictions outside the validated scope.",
     "A variance-decomposition diagnostic asks, family by family, whether "
     "sample-form conditioning is required, and assigns two distinct regimes "
     "across the studied families which set the predictor's conditioning rule "
     "without being established as a tested distinction, and explicit refusal "
     "gates prevent predictions outside the validated scope.",
     "the conclusion"),
]

# After the edits, "tested finding" language must not survive anywhere it is
# applied to the conditioning diagnostic. Located, and the run fails if a
# passage carries it without the qualification.
WATCH = ["returns two distinct regimes", "returning two distinct regimes",
         "hypothesis tested against the literature"]


def replace_in_paragraph(p, find, repl):
    text = "".join(r.text for r in p.runs)
    if find not in text:
        return False
    start = text.index(find)
    end = start + len(find)
    pos, first, spans = 0, None, []
    for r in p.runs:
        a, b = pos, pos + len(r.text)
        if b > start and a < end:
            spans.append((r, max(start, a) - a, min(end, b) - a))
            if first is None:
                first = r
        pos = b
    if first is None:
        return False
    for r, i, j in spans:
        r.text = r.text[:i] + (repl if r is first else "") + r.text[j:]
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    d = docx.Document(os.path.join(SRC, MS))
    missed = [why for find, repl, why in EDITS
              if not any(replace_in_paragraph(p, find, repl)
                         for p in d.paragraphs)]
    print("%s: %d edits, %d not found" % (MS, len(EDITS), len(missed)))
    for m in missed:
        print("   MISSING", m)
    left = [w for w in WATCH
            for p in d.paragraphs if w in p.text]
    if left:
        missed += ["overclaiming phrase still present: %s" % w
                   for w in sorted(set(left))]
        for w in sorted(set(left)):
            print("   STILL PRESENT", w)
    if missed:
        print("\nNothing written.")
        return 1
    if a.dry_run or not a.out_dir:
        print("\ndry run: nothing written")
        return 0
    os.makedirs(a.out_dir, exist_ok=True)
    d.save(os.path.join(a.out_dir, MS.replace("_final5", "_final6")))
    print("\nwritten to %s" % a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
