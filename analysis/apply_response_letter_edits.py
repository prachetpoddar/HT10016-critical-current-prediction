#!/usr/bin/env python3
"""Apply the audited corrections to the response to referees.

The letter was not touched by the manuscript edits and went on quoting the
cohort as it stood in August, including the 16-fold conditioning figure that the
manuscript no longer makes. A response letter that cites numbers the manuscript
has abandoned is worse than one that says nothing, because the referee checks it
against the paper.

Same mechanics as analysis/apply_manuscript_edits.py: literal replacements, run
level in the docx so formatting survives, and nothing written if any edit fails
to find its target. The markdown and the docx are edited from one list so they
cannot drift apart.

    python analysis/apply_response_letter_edits.py --md <md> --docx <docx> --dry-run
"""
import argparse
import os
import re
import shutil
import sys

import docx

EDITS = [
    ("934 articles screened, 69 contributing fitted curves, 43 distinct "
     "compounds, 4387 extracted critical-current points, 23 fully fittable "
     "compounds, 419 temperature-axis fits, 95 field-axis fits drawn from 17 "
     "source papers, and 110 per-paper anchors behind Figure 3. The figure of "
     "69 is no longer introduced first",
     "934 articles screened, 62 contributing fitted curves, 38 distinct "
     "compounds, 4146 extracted critical-current points, 23 fully fittable "
     "compounds, 260 temperature-axis fits, 94 field-axis fits drawn from 16 "
     "source papers, and 96 per-paper anchors behind Figure 3. The figure of "
     "62 is no longer introduced first",
     "Table I of the corrected manuscript"),

    ("61 of the 110 anchors falling in the three panels shown and the 44 "
     "markers they collapse to",
     "52 of the 96 anchors falling in the three panels shown and the 34 "
     "markers they collapse to",
     "phase_3_p31_jc_anchor_per_paper.csv through "
     "analysis/figure_4_source.py"),

    ("On the matched five-family cohort the reduction is 16-fold on means and "
     "4.7-fold on medians, and those are the figures we now report.",
     "Restricting to the matched five-family cohort removes that mismatch but "
     "not a more serious one, which we found on re-examining the comparison: "
     "in both versions the predictor for a held-out family was built from a "
     "pool containing that family's own fits, so neither was a statement about "
     "generalization. Under a leave-one-substructure-out protocol, with the "
     "held-out family withheld at every stage, the improvement is between one "
     "and about two-fold and depends on the cohort: 1.07-fold across the seven "
     "families carrying a descriptor, 2.24-fold on the fits passing "
     "physicality, and 1.83-fold with the cuprate families removed. Those are "
     "the figures we now report, and we no longer offer a single "
     "fold-improvement headline.",
     "analysis/multi_stage_loso.py; audit/multi_stage_loso.csv"),

    ("they account for 62% of the residual mass while representing 44% of the "
     "cohort",
     "they account for 59% of the residual mass while representing 43% of the "
     "cohort",
     "audit/multi_stage_loso.csv, Stage 1 residuals on the seven families "
     "carrying a descriptor"),

    ("all 110 per-paper anchor groups are identical before and after",
     "all 96 per-paper anchor groups are identical before and after",
     "phase_3_p31_jc_anchor_per_paper.csv"),

    ("A caption-scoped screen over the 2615 unique PDFs in the archive finds "
     "137 carrying captions for both measurements",
     "A caption-scoped screen over the 2594 papers in the archive finds 137 "
     "carrying captions for both measurements",
     "data/caption_sweep.csv less 21 rows that are not papers, eleven of them "
     "matplotlib toolbar icons"),
]


def _rewrap(text, doc_text, at, width=88):
    """Wrap a replacement to the surrounding file's line width."""
    line_start = doc_text.rfind("\n", 0, at) + 1
    indent = at - line_start
    out, line, first = [], "", True
    for word in text.split():
        limit = width - (indent if first else 0)
        if line and len(line) + 1 + len(word) > limit:
            out.append(line)
            line, first = word, False
        else:
            line = (line + " " + word) if line else word
    if line:
        out.append(line)
    return "\n".join(out)


def replace_in_paragraph(par, find, repl):
    runs = par.runs
    if not runs:
        return False
    text = "".join(r.text for r in runs)
    at = text.find(find)
    if at < 0:
        return False
    end = at + len(find)
    pos, first = 0, None
    for r in runs:
        s, e = pos, pos + len(r.text)
        if first is None and e > at:
            first = r
            head = r.text[:at - s]
            tail = r.text[end - s:] if e >= end else ""
            r.text = head + repl + tail
            if e >= end:
                return True
        elif first is not None:
            if e <= end:
                r.text = ""
            else:
                r.text = r.text[end - s:]
                return True
        pos = e
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True)
    ap.add_argument("--docx", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    md = open(args.md, encoding="utf-8").read()
    doc = docx.Document(args.docx)
    misses = []

    for find, repl, why in EDITS:
        # The markdown is hard-wrapped, so a sentence that is one string in the
        # docx spans several lines here. Match on collapsed whitespace and
        # rewrap the replacement to the file's own width, or the two files drift
        # apart on exactly the numbers this script exists to align.
        pat = re.compile(r"\s+".join(re.escape(w) for w in find.split()))
        m = pat.search(md)
        in_md = m is not None
        if in_md:
            md = md[:m.start()] + _rewrap(repl, md, m.start()) + md[m.end():]
        in_docx = False
        for par in doc.paragraphs:
            if replace_in_paragraph(par, find, repl):
                in_docx = True
                break
        print("%-9s %-9s %s\n          -> %s\n          %s\n"
              % ("md ok" if in_md else "md MISS",
                 "docx ok" if in_docx else "docx MISS",
                 find[:70], repl[:70], why))
        if not in_md or not in_docx:
            misses.append(find)

    if misses:
        print("%d edit(s) failed to find a target. Nothing written." % len(misses))
        return 1
    if args.dry_run:
        print("%d edits would be applied to both files. Nothing written."
              % len(EDITS))
        return 0

    for src, writer in ((args.md, None), (args.docx, doc)):
        stem, ext = os.path.splitext(os.path.basename(src))
        keep = os.path.join(args.out_dir, stem + "_asfound" + ext)
        if not os.path.exists(keep):
            shutil.copy2(src, keep)
        out = os.path.join(args.out_dir, stem + "_corrected" + ext)
        if writer is None:
            open(out, "w", encoding="utf-8").write(md)
        else:
            writer.save(out)
        print("written %s  (original preserved as %s)" % (out, keep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
