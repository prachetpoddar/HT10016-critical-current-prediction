"""
apply_post_freeze_letter_edits.py

Brings the response letter's inventory of corrections up to the frozen tables,
action A6.

The letter says a final pass over every reported quantity found five defects and
lists them. The pass was not final. Seven more were found after it, while
rebuilding Figure 3 on the repaired anchors, making the refusal claim consistent,
clearing the stale candidate accounting out of the Supplemental Material, and
making the dispatch table reproduce from its own code. None changes a
conclusion, and one of them strengthens a caveat the letter already makes, but
a referee reading the deposit would find all seven and they belong in the reply
rather than in a commit message.

  1  Sec. III.A applied a size-preserving clustered null to two families and a
     looser one to the third, so the MgB2-class floor read 0.33 where the
     family admits one labelling and its probability is identically 1.
  2  Four places said the framework refuses to predict outside its validated
     scope, which the conclusion contradicted two sentences later.
  3  Supplemental Sec. 9 gave the iron chalcogenide family 55 candidates
     against Table IV's 49.
  4  Sec. 9 and Table IV gave that family seven paper-reported anchors beside
     24 reference-table ones, which is 31 against 29 compounds; the deposit
     gives five.
  5  Supplemental Sec. 12 reported on 53 and 37 non-refused candidates at 1 T,
     where the deposit has none in any family.
  6  The paragraph under Table S6 read a field span off a candidate refused at
     all nine of its grid points.
  7  Two counts were quoted on the cohort as deposited inside sentences quoting
     the repaired one: 106 temperature-axis fits for the 122-type family and 20
     source papers for the cohort.

The dispatch-table reproduction, the eighth, is already reported in its own
paragraph of the audit section and is not repeated here.

Usage:
    python3 analysis/apply_post_freeze_letter_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final39.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final39.docx"
RESP = "RESPONSE_TO_REFEREES_final39.docx"
OUT = {MAIN: "HT10016_revised_final40.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final40.docx",
       RESP: "RESPONSE_TO_REFEREES_final40.docx"}

EDITS = [
    (RESP,
     "A final pass over every reported quantity found five more defects, all "
     "corrected.",
     "A pass over every reported quantity found five more defects, all "
     "corrected."),

    (RESP,
     "An artificial intelligence use disclosure has been added in accordance "
     "with APS policy,",

     "A second pass, made after the tables were frozen, found seven more. All "
     "are corrected and none changes a conclusion. Section III.A was applying "
     "a clustered null that holds the sample-form counts fixed to two families "
     "and a looser one to the third, which made the MgB2-class floor read as a "
     "probability of 0.33; under the same null it applies to the other two, "
     "that family admits a single labelling and its probability is identically "
     "1, so the caveat we make there is stronger than we stated it. Four "
     "places said the framework refuses to predict outside its validated "
     "scope, which our own conclusion contradicted two sentences later: the "
     "gates test a target against the window the exponents were calibrated "
     "over, and nothing refuses a family that could not be assessed, which is "
     "the family that emits. Section 9 of the Supplemental Material gave the "
     "iron chalcogenide family 55 candidates against Table IV's 49, and both "
     "that section and Table IV gave it seven paper-reported anchors beside 24 "
     "reference-table ones, which is more anchors than the family has "
     "compounds; the deposit gives five. Section 12 reported a scope "
     "comparison on 53 and 37 non-refused candidates at 1 T, where the "
     "deposited file has none in any family, and we withdraw it rather than "
     "recompute it, because the two families it ran on emit nothing and the "
     "one that emits was excluded from it by construction. The paragraph under "
     "Table S6 read a field span off a candidate that is refused at all nine "
     "of its grid points. And two counts were quoted on the cohort as "
     "deposited inside sentences quoting the repaired one: the iron pnictide "
     "122-type family carries 105 temperature-axis fits rather than 106, and "
     "the temperature-axis cohort is drawn from 18 source papers, all of them "
     "arXiv preprints, rather than 18 of 20. An artificial intelligence use "
     "disclosure has been added in accordance with APS policy,"),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_post_freeze_letter_edits.py IN_DIR OUT_DIR")
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
