#!/usr/bin/env python3
"""Bring the manuscript and the response into line, and fix the checker.

analysis/final_consistency_check.py found three real defects and two artefacts
of its own on the first run. All five are handled here.

REAL, all the same mistake: a figure was retired in one document and left
standing in another.

  Sec. III.A of the manuscript withdraws the Spearman 0.635; the response still
  quotes it as the descriptor's rank correlation.

  The response retires 1.07, 2.24 and 1.83; Sec. III.A of the manuscript still
  reports them, and adds two Stage 3 figures with the same construction.

  The response withdraws the SmFeAsO0.8F0.2 worked example twice over, for the
  kilo-oersted unit error and for not being monotone across the window quoted;
  Assumption 1 of Sec. III.F still gives it, with the same "runs from 1.25 to
  12.14 as temperature rises" phrasing, and still gives the 18-series and
  nine-series counts that the withdrawals reduce to 13 and 6.

ARTEFACTS of the checker, fixed in it rather than in the documents.

  It split on sentences, so a figure withdrawn in the following sentence
  registered as unqualified. It now takes the paragraph as the unit.

  It flagged "factor of 23" in the response, which is the referee's own
  objection quoted before the answer. Quoted objections are excluded.

  Its contributing-paper count summed the wrong columns and returned zero.

Source out_final/*_final11.docx, output out_send/.

    python analysis/apply_document_alignment.py --dry-run
    python analysis/apply_document_alignment.py --out-dir out_send

Run from the repository root.
"""
import argparse
import os

import docx

SRC = "out_final"
MS = "HT10016_revised_final11.docx"
RESP = "RESPONSE_TO_REFEREES_final11.docx"

MS_EDITS = [
    ("The improvement is then between one and about two-fold and depends on "
     "the cohort: across the seven families that carry a descriptor the best "
     "Stage 2 reading gives 1.07-fold, restricted to fits passing physicality "
     "it gives 2.24-fold, and with the cuprate families removed 1.83-fold. "
     "Stage 3 gives 1.37-fold on means across all seven families and 2.20-fold "
     "with the cuprate families removed, where its interquartile bound covers "
     "the residual in four of four families.",
     "We do not report a fold improvement. An earlier version of this section "
     "gave 1.07, 2.24 and 1.83 across the three cohorts, and those are "
     "withdrawn: the sample-form-conditional scope is undefined for the MgB2 "
     "class, because once the cuprate families are removed no other family "
     "contributes a bulk or wire fit, so two of the three divided a "
     "four-family numerator by a three-family denominator, which is the "
     "mismatched-cohort defect this same paragraph identifies in the original "
     "ratio. They were also the lowest of four ways of forming the conditional "
     "prediction, and the lowest is not the same one on every cohort. We give "
     "the errors instead: across the seven families the leave-one-substructure-"
     "out mean absolute error is 12.3 without sample-form conditioning and "
     "14.9 with it, and on the fits passing physicality it is 1.19 and 0.55 "
     "over the three families the conditional scope can score. Neither "
     "predictor is distinguishable from the out-of-sample median of the "
     "training fits, which uses no family and no sample form at all, and "
     "removing any single family moves the comparison across unity. The "
     "corpus cannot separate the two effects, because sample form is nearly "
     "nested within substructure here: wire occurs in one family only, and "
     "holding a substructure out removes most of its forms from the training "
     "pool.",
     "Sec. III.A, the retired fold figures"),
    ("Across the 18 series in which one scale was held over three or more "
     "measurement temperatures, the median absolute rank correlation between "
     "exponent and temperature is 0.70, rising to 0.80 in the nine series "
     "sampled at four or more temperatures. In the clearest case, "
     "SmFeAsO0.8F0.2 with a scale held at 86 T, the fitted exponent runs from "
     "1.25 to 12.14 as temperature rises from 2 to 35 K.",
     "Across the series in which one scale was held over three or more "
     "measurement temperatures, the median absolute rank correlation between "
     "exponent and temperature is 0.80, over 13 series, and 0.80 again over "
     "the 6 sampled at four or more temperatures. On the cohort as first "
     "deposited these were 0.70 over 18 and 0.80 over 9; the withdrawals "
     "reduce the count and leave the effect slightly larger. The worked "
     "example given here previously, SmFeAsO0.8F0.2 with a scale held at 86 T, "
     "is withdrawn: its printed field axis is kilo-oersted recorded as tesla, "
     "so corrected its fits fail the applicability bound, and independently "
     "its exponent is not monotone across the window we quoted, falling from "
     "1.25 at 2 K to 0.82 at 10 K before rising to 12.14 at 35 K. The clearest "
     "surviving case is the Ba(Fe,Co)2As2 single crystal of Ref. [40] with a "
     "scale held at 4.5 T, whose exponent rises from 0.26 to 0.86 across nine "
     "measurement temperatures from 4.2 to 18 K; our audit grades that record "
     "weak, sitting 1.3 to 1.7 times above a retrace of its own figure, and we "
     "offer it as the best surviving illustration rather than a clean one.",
     "Sec. III.F, the withdrawn worked example"),
]

RESP_EDITS = [
    ("We also report the descriptor’s rank correlation as a Spearman "
     "coefficient of 0.635 with a 95% confidence interval from 0.061 to 0.948, "
     "so that the reader can see how weak that signal is and why Stage 1 is "
     "retained for ranking and classification rather than for magnitude.",
     "An earlier version of this reply reported the descriptor's rank "
     "correlation as a Spearman coefficient of 0.635 with a 95% confidence "
     "interval from 0.061 to 0.948. That is withdrawn in Section III.A: it was "
     "computed on a nine-family version of the descriptor table and on the "
     "mean field exponent, where this stage regresses the median, and on the "
     "seven families that remain no interval can be estimated tightly enough "
     "to be worth quoting. What we report instead is the quantity this stage "
     "was validated on, its rank-position error, which is 1.00 with six of the "
     "seven families placed within one position. That is why Stage 1 is "
     "retained for ranking and classification rather than for magnitude.",
     "the response's copy of the withdrawn Spearman"),
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


def apply(path, edits):
    d = docx.Document(path)
    missed = [why for find, repl, why in edits
              if not any(replace_in_paragraph(p, find, repl)
                         for p in d.paragraphs)]
    return d, missed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    ms, m1 = apply(os.path.join(SRC, MS), MS_EDITS)
    resp, m2 = apply(os.path.join(SRC, RESP), RESP_EDITS)
    print("%s: %d edits, %d not found" % (MS, len(MS_EDITS), len(m1)))
    print("%s: %d edits, %d not found" % (RESP, len(RESP_EDITS), len(m2)))
    missed = m1 + m2
    if missed:
        print("\nNothing written.")
        for x in missed:
            print("  ", x)
        return 1
    if a.dry_run or not a.out_dir:
        print("\ndry run: nothing written")
        return 0
    os.makedirs(a.out_dir, exist_ok=True)
    ms.save(os.path.join(a.out_dir, MS.replace("_final11", "_final12")))
    resp.save(os.path.join(a.out_dir, RESP.replace("_final11", "_final12")))
    print("\nwritten to %s" % a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
