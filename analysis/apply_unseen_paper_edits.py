"""
apply_unseen_paper_edits.py

Moves the source-paper holdout result to the front of the paper, action B4, and
corrects two things about it that checking it turned up.

The result. Withholding every measurement of a source paper, none of the three
candidate functional forms reaches a median error of 0.90 dex on the eight
compounds that draw on more than one source: audit/functional_form_comparison.csv
gives 0.903, 0.900 and 0.949 on the current cohort, against 0.472, 0.322 and
0.323 under a point-level split within a compound. It is the paper's most direct
measurement of the heterogeneity the whole framework is built around, and it sat
in the last sentence of the functional-form comparison in Sec. II.C. It now
appears in the abstract and in the introduction as well.

Two corrections. The response letter gave the within-compound range as 0.32 to
0.45 dex; the deposit gives 0.32 to 0.39 for the two forms that are not
withdrawn and 0.32 to 0.50 across all three, and 0.45 reproduces from nothing.
And it called the gap "a factor of eight in critical current between predicting
an unseen measurement and predicting an unseen paper". Eight is the unseen-paper
error expressed as a factor, 10 to the 0.900, not the ratio between the two
regimes, which is 10 to the 0.578 or about four. Both are fixed.

Usage:
    python3 analysis/apply_unseen_paper_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final48.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final48.docx"
RESP = "RESPONSE_TO_REFEREES_final48.docx"
OUT = {MAIN: "HT10016_revised_final49.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final49.docx",
       RESP: "RESPONSE_TO_REFEREES_final49.docx"}

EDITS = [
    # ---- the abstract ----------------------------------------------------
    (MAIN,
     "These regimes set the conditioning rule the predictor follows.",

     "These regimes set the conditioning rule the predictor follows. A "
     "holdout that withholds every measurement of a source paper puts a number "
     "on the heterogeneity the framework is built for: no candidate functional "
     "form reaches a median error of 0.90 dex on an unseen paper, a factor of "
     "eight in critical current, against 0.32 to 0.39 dex when the withheld "
     "measurements come from within a compound."),

    # ---- the introduction -------------------------------------------------
    (MAIN,
     "Whether this literature can answer that question is itself a result of "
     "the work, and Section III.A reports that on this corpus it cannot, "
     "because sample form arrives one paper at a time.",

     "Whether this literature can answer that question is itself a result of "
     "the work, and Section III.A reports that on this corpus it cannot, "
     "because sample form arrives one paper at a time. The size of the "
     "difficulty can be measured rather than asserted. Withholding every "
     "measurement of a source paper leaves no candidate functional form with a "
     "median error better than 0.90 dex, a factor of eight in critical "
     "current, where withholding measurements from within a compound leaves "
     "0.32 to 0.39 dex, a factor of about two. Predicting an unseen paper and "
     "predicting an unseen measurement are not the same problem, and Section "
     "II.C reports the comparison in full."),

    # ---- Sec. II.C, the source-paper holdout ------------------------------
    (MAIN,
     "Under a source-paper holdout, in which every measurement of a held-out "
     "source is withheld, no form reaches a median error below 0.9 dex on the "
     "eight compounds drawing on more than one source.",

     "Under a source-paper holdout, in which every measurement of a held-out "
     "source is withheld, the three forms give 0.903, 0.900 and 0.949 dex on "
     "the eight compounds drawing on more than one source, against 0.472, "
     "0.322 and 0.323 under a point-level split on the same cohort. None "
     "reaches 0.90 dex on an unseen paper, and an error of that size is a "
     "factor of eight in critical current against a factor of about two within "
     "a compound. This is the most direct measurement in the paper of the "
     "heterogeneity the framework is built for, and the abstract and Section I "
     "state it as such."),

    # ---- the response letter ----------------------------------------------
    (RESP,
     "Under a holdout that withholds every measurement of a paper, none of the "
     "three candidate functional forms reaches a median error below 0.9 dex, "
     "against 0.32 to 0.45 dex when the holdout is drawn within a compound. "
     "That is a factor of eight in critical current between predicting an "
     "unseen measurement and predicting an unseen paper, and it is the "
     "heterogeneity this paper is about, measured a second way.",

     "Under a holdout that withholds every measurement of a paper, none of the "
     "three candidate functional forms reaches a median error of 0.90 dex on "
     "the eight compounds drawing on more than one source, against 0.32 to "
     "0.39 dex when the holdout is drawn within a compound. An error of 0.90 "
     "dex is a factor of eight in critical current, against a factor of about "
     "two within a compound. It is the heterogeneity this paper is about, "
     "measured a second way, and it now appears in the abstract and the "
     "introduction rather than only in the functional-form comparison."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_unseen_paper_edits.py IN_DIR OUT_DIR")
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    by_file = {}
    for f, find, repl in EDITS:
        by_file.setdefault(f, []).append((find, repl))
    for name in (MAIN, SUPP, RESP):
        ip, op = os.path.join(src, name), os.path.join(dst, OUT[name])
        if not os.path.exists(ip):
            sys.exit("missing input: %s" % ip)
        zin = zipfile.ZipFile(ip)
        doc = zin.read("word/document.xml").decode("utf-8")
        for find, repl in by_file.get(name, []):
            hits = [p for p in paragraphs(doc) if find in unescape(plain(p))]
            if len(hits) != 1:
                sys.exit("%s: %d paragraph(s) contain %r, expected exactly 1"
                         % (name, len(hits), find[:70]))
            new = replace_in_paragraph(hits[0], find, repl)
            if new is None:
                sys.exit("%s: could not place the replacement for %r"
                         % (name, find[:70]))
            doc = doc.replace(hits[0], new, 1)
            print("   %-8s %s" % (name.split("_")[0][:8], find[:62]))
        tmp = op + ".part"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, doc)
                else:
                    zout.writestr(item, zin.read(item.filename))
        zin.close()
        shutil.move(tmp, op)
        print("   wrote %s" % op)
    return 0


if __name__ == "__main__":
    sys.exit(main())
