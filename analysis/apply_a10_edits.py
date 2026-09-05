#!/usr/bin/env python3
"""Rewrite A10 to stop quoting a fold improvement.

Referee A objected that the 23-fold reduction is an exaggeration. The letter
concedes it, correctly identifies the cause, says "we no longer offer a single
fold-improvement headline", and then offers three: 1.07, 2.24 and 1.83.

Adversarial review of analysis/a10_on_repaired_cohort.py established that those
three repeat the defect they replace, and this rewrite retires them.

  Two of the three divide a four-family numerator by a three-family
  denominator. The pooled Stage 2 readings are undefined for the MgB2 class,
  because once the cuprates are gated out no other family contributes a bulk or
  wire fit, and the mean silently skips it. That is the same silent skip
  multi_stage_loso.py's docstring gives as the reason the published 16-fold is
  invalid. Matched over the families each reading can score, 2.24 is 2.17 and
  1.83 is 2.11.

  The figure quoted is the lowest-error of four Stage 2 readings, and the
  winner is not the same reading on every cohort. Held to one reading across
  every arm, the seven-family cohort gives 0.83, which is Stage 2 doing worse
  than Stage 1.

  On the 52 fits the stated protocol admits there are four families and so four
  folds, Stage 1 is a two-parameter fit on three training points in each, and
  dropping one family moves the figure from 0.74 to 550.

So the letter now reports the errors and declines the ratio. The concession to
the referee is unchanged and its basis is stronger: the original comparison set
one out-of-sample error against two resubstitution errors, and the honest
replacement is that on this corpus the improvement cannot be distinguished
from none.

Source out_a3/*_final8.docx, output out_a10/.

    python analysis/apply_a10_edits.py --dry-run
    python analysis/apply_a10_edits.py --out-dir out_a10

Run from the repository root.
"""
import argparse
import os

import docx

SRC = "out_a3"
RESP = "RESPONSE_TO_REFEREES_final8.docx"

OLD = (
    "Under a leave-one-substructure-out protocol, with the held-out family "
    "withheld at every stage, the improvement is between one and about "
    "two-fold and depends on the cohort: 1.07-fold across the seven families "
    "carrying a descriptor, 2.24-fold on the fits passing physicality, and "
    "1.83-fold with the cuprate families removed. Those are the figures we now "
    "report, and we no longer offer a single fold-improvement headline.")

NEW = (
    "Under a leave-one-substructure-out protocol, with the held-out family "
    "withheld at every stage, we can no longer report a fold improvement at "
    "all, and we give the errors instead. On the fits passing physicality the "
    "mean absolute error in the exponent is 1.19 without conditioning and 0.55 "
    "with it; across all seven families carrying a descriptor it is 12.3 and "
    "14.9, which is conditioning doing worse than not conditioning. "
    "An earlier version of this reply quoted 1.07, 2.24 and 1.83 for the three "
    "cohorts. We withdraw those three figures because they repeat the defect "
    "they were introduced to replace. The sample-form-conditional scope is "
    "undefined for the MgB2 class, since once the cuprate families are gated "
    "out no other family contributes a bulk or wire fit, so its error is "
    "missing and the mean silently skips it: 2.24 and 1.83 divide a "
    "four-family numerator by a three-family denominator, exactly the "
    "mismatched-cohort error we identify above as the reason the 23-fold was "
    "wrong. Matched over the families the predictor can actually score they "
    "are 2.17 and 2.11. They were also the lowest of four ways of forming the "
    "conditional prediction, and the lowest is not the same one on every "
    "cohort, so the three figures were not a common quantity. "
    "Nor is the protocol stable enough to carry a ratio at this scope. On the "
    "52 field-axis fits that survive the anchor repairs and the fitting "
    "protocol there are four substructure families and therefore four folds, "
    "the unconditioned stage is a two-parameter fit on three training points "
    "in each, and removing any single family moves the ratio between 0.74 and "
    "550. "
    "The referee's objection is therefore conceded more completely than our "
    "first reply conceded it. It is not that 23 was too large. It is that on a "
    "corpus of this size the benefit of conditioning cannot be separated from "
    "the noise of holding a family out, and we report the two errors and the "
    "family count rather than their quotient.")


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

    d = docx.Document(os.path.join(SRC, RESP))
    if not any(replace_in_paragraph(p, OLD, NEW) for p in d.paragraphs):
        print("the A10 passage was not found. Nothing written.")
        return 1
    print("%s: 1 edit applied" % RESP)

    # The three retired figures must appear only where they are withdrawn.
    bad = []
    for p in d.paragraphs:
        t = p.text
        for n in ("1.07-fold", "2.24-fold", "1.83-fold"):
            if n in t and "withdraw" not in t:
                bad.append(n)
    if bad:
        print("\nA withdrawn figure appears unqualified. Nothing written.")
        for b in sorted(set(bad)):
            print("  ", b)
        return 1
    print("the three retired figures appear only where they are withdrawn")

    if a.dry_run or not a.out_dir:
        print("\ndry run: nothing written")
        return 0
    os.makedirs(a.out_dir, exist_ok=True)
    d.save(os.path.join(a.out_dir, RESP.replace("_final8", "_final9")))
    print("\nwritten to %s" % a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
