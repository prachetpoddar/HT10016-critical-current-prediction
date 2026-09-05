#!/usr/bin/env python3
"""Rewrite the conditioning diagnostic in Sec. III.A and answer A4 on it.

Decision taken: agree with Referee A more fully than the letter currently does,
and concede the test separately from the result.

  The result agrees with him harder. After the anchor repair sample form
  explains 4 percent of the within-family variance in the MgB2 class, not 12,
  and corrected for the upward bias the statistic carries at small n the value
  is negative.

  The test cannot establish anything. Sample form is very nearly a relabelling
  of source paper: 1 of 29 papers carried more than one form before the repair
  and 0 of 20 do after it. Under the null that shuffles the form label between
  papers, which is the only null that respects that structure, the MgB2 cell
  admits three distinct labellings and can never return a p below 0.33. The
  other two families admit four and ten.

  The anchor defects are conceded separately, as an extraction failure rather
  than a limit of the literature. 26 of 96 rows contradicted their source
  figures and are withdrawn; 15 more carried a scale error and are corrected.

Values from analysis/apply_jc_anchor_repairs.py and
audit/jc_anchor_repair_20260905.md.

Source is out_field/*_final3.docx, output out_a4/.

Not edited, located and printed. The 0.37 and 0.12 propagate into the abstract,
the two-regime framing of the introduction and conclusion, and the prediction
rule of Sec. III.E. Rewriting those changes what the paper claims rather than
what it reports, so they are left for the authors, and the script refuses to
write if any of them has moved.

One number in Sec. III.A does not reproduce from any deposited cohort and is
corrected on the way past: the text gives iron pnictide 122-type as 0.35, where
data/phase_3_p31_variance_decomposition.csv has 0.4877, phase_3_p58 has 0.5599
and the pre-withdrawal p58 snapshot has 0.5988. There is no cohort in the
repository that returns 0.35.

    python analysis/apply_a4_conditioning_edits.py --dry-run
    python analysis/apply_a4_conditioning_edits.py --out-dir out_a4

Run from the repository root.
"""
import argparse
import os

import docx

SRC = "out_field"
MS = "HT10016_revised_final3.docx"
RESP = "RESPONSE_TO_REFEREES_final3.docx"

OLD_MS = (
    "The diagnostic yields two distinct outcomes, summarized in Fig. 3. For "
    "iron chalcogenide 11-type materials the ratio is 0.37: sample form "
    "accounts for a substantial minority of the relevant variance, so "
    "sample-form conditioning is informative rather than required, the "
    "predictor uses Stage 2 medians where the cell is populated, and the "
    "within-cell interquartile range captures the remaining compound-level "
    "variation. For iron pnictide 122-type the ratio is 0.35: sample form "
    "still carries information, so conditioning is applied when sample form is "
    "known, falling back to the single-crystal cell rather than to Stage 3 "
    "when it is not, which is the rule the dispatch commits to for every "
    "122-type record. For MgB2-class the ratio drops to 0.12: sample form "
    "explains little of the variance, so the predictor uses "
    "substructure-aggregate scope with the full interquartile range as "
    "uncertainty.")

NEW_MS = (
    "The diagnostic yields two distinct outcomes, summarized in Fig. 3, and we "
    "state at the outset what it can and cannot establish. On the deposited "
    "anchors the ratio is 0.37 for iron chalcogenide 11-type, 0.49 for iron "
    "pnictide 122-type and 0.12 for MgB2-class. An earlier version of this "
    "section gave 0.35 for the 122-type family, which reproduces from no "
    "cohort in the deposit and is corrected here. After the anchor repair of "
    "Section III.F, which withdraws 26 of the 96 rows and corrects a scale "
    "error on 15 more, the same three are 0.81 on 5 samples, 0.37 on 7 and "
    "0.04 on 13. The direction is unchanged and the separation between the "
    "MgB2 class and the others is wider, so the regime distinction the "
    "predictor uses is the one the data indicate: sample-form conditioning is "
    "informative rather than required for the two iron-based families, the "
    "predictor uses Stage 2 medians where the cell is populated and falls back "
    "to the single-crystal cell otherwise, and for MgB2-class it uses "
    "substructure-aggregate scope with the full interquartile range as "
    "uncertainty. What the diagnostic does not do is establish that "
    "distinction to any standard of significance, and the reason is structural "
    "rather than a matter of sample size alone. Sample form is very nearly a "
    "relabelling of source paper in this corpus: one of the 29 contributing "
    "papers carried more than one sample form before the repair and none of "
    "the 20 does after it. Under a null that shuffles the form label between "
    "papers, which is the only null that respects that structure, the "
    "MgB2-class cell admits three distinct labellings and can therefore never "
    "return a p below 0.33 however clean its separation, and the two "
    "iron-based cells admit four and ten. Corrected for the upward bias this "
    "statistic carries at small sample size, the MgB2-class value is negative, "
    "which is to say its between-form separation is smaller than the grouping "
    "produces by chance. We therefore report the regime labels as the rule the "
    "predictor follows and as consistent with the data, not as a tested "
    "finding, and we state the measurement that would test them: source papers "
    "reporting several sample forms of one compound, which this corpus does "
    "not supply.")

OLD_RESP = (
    "On MgB2, the referee’s observation and our diagnostic agree, and we "
    "have made the connection explicit. The variance-decomposition test finds "
    "that sample form explains only 12% of the within-family variance in this "
    "class, against 37% for the iron chalcogenides. Section III.A now states "
    "that this is consistent with the two-band character of MgB2 and with its "
    "documented sensitivity to production route, both of which act through "
    "variables that a sample-form label does not capture. The diagnostic does "
    "not merely fail here; it identifies the family in which the conditioning "
    "variable we tested is the wrong one.")

NEW_RESP = (
    "On MgB2 the referee’s observation and our diagnostic agree, and after "
    "repairing the anchor table they agree more strongly than we first "
    "reported. Sample form now explains 4% of the within-family variance in "
    "this class rather than 12%, against 81% for the iron chalcogenides, and "
    "corrected for the upward bias this statistic carries at small sample size "
    "the MgB2-class value is negative: the separation between sample forms in "
    "this class is smaller than the grouping produces by chance. Section III.A "
    "states that this is consistent with the two-band character of MgB2 and "
    "with its documented sensitivity to production route, both of which act "
    "through variables a sample-form label does not capture. "
    "We have to concede the test itself, separately from the result, and we "
    "would rather state this than let the referee find it. Sample form is very "
    "nearly a relabelling of source paper in this corpus: one of the 29 "
    "contributing papers carried more than one sample form before the repair "
    "and none of the 20 does after it. Under a null that shuffles the form "
    "label between papers, which is the only null that respects that "
    "structure, the MgB2-class cell admits three distinct labellings and can "
    "never return a p below 0.33 however clean the separation, and the other "
    "two families admit four and ten. The diagnostic therefore cannot "
    "establish the regime distinction it is used to draw, and Section III.A "
    "now reports the regime labels as the rule the predictor follows rather "
    "than as a tested finding. What would settle it is source papers reporting "
    "several sample forms of one compound, which the corpus we retrieved does "
    "not contain; we name that as the specific data requirement rather than as "
    "a general call for more data. "
    "Separately, and this is our error rather than a limit of the literature: "
    "26 of the 96 anchor rows behind this diagnostic held values that "
    "contradict their source figures and are withdrawn, and 15 more carried a "
    "scale error on the current or field axis and are corrected. The audit "
    "that found them is deposited with the analysis.")

# Passages carrying 0.37 or 0.12 into claims rather than into the diagnostic.
# Located, never edited.
FLAG_MS = [
    "sample form explains 37% of the within-family variance",
    "returns two distinct regimes across the studied families",
    "at a ratio of 0.37",
    "returning two distinct regimes across the studied families",
]


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

    missed = []
    ms = docx.Document(os.path.join(SRC, MS))
    if not any(replace_in_paragraph(p, OLD_MS, NEW_MS) for p in ms.paragraphs):
        missed.append("Sec. III.A, the three ratios")
    rp = docx.Document(os.path.join(SRC, RESP))
    if not any(replace_in_paragraph(p, OLD_RESP, NEW_RESP) for p in rp.paragraphs):
        missed.append("A4, the MgB2 answer")

    print("%s: 1 edit, %s" % (MS, "found" if "Sec. III.A, the three ratios"
                              not in missed else "NOT FOUND"))
    print("%s: 1 edit, %s" % (RESP, "found" if "A4, the MgB2 answer"
                              not in missed else "NOT FOUND"))

    print("\npassages carrying the diagnostic into a claim, located and not "
          "edited")
    for f in FLAG_MS:
        hit = [i for i, p in enumerate(ms.paragraphs) if f in p.text]
        print("   [%s] %s" % ("found" if hit else "NOT FOUND", f[:62]))
        if not hit:
            missed.append("flag: " + f[:40])
    print("   The abstract, the introduction and the conclusion all state two "
          "distinct regimes")
    print("   as a finding, and Sec. III.E states the 0.37 as the rule for the "
          "chalcogenide")
    print("   dispatch. Those are claims rather than reported numbers, and "
          "changing them changes")
    print("   what the paper asserts, so they are left for the authors.")

    if missed:
        print("\nNothing written.")
        for m in missed:
            print("  ", m)
        return 1
    if a.dry_run or not a.out_dir:
        print("\ndry run: nothing written")
        return 0
    os.makedirs(a.out_dir, exist_ok=True)
    ms.save(os.path.join(a.out_dir, MS.replace("_final3", "_final4")))
    rp.save(os.path.join(a.out_dir, RESP.replace("_final3", "_final4")))
    print("\nwritten to %s" % a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
