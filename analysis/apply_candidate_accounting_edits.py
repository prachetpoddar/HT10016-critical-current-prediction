"""
apply_candidate_accounting_edits.py

Removes the stale candidate accounting from the Supplemental Material and one
anchor-provenance count from Table IV, action A4.

Four defects, each checked against data/phase_3_p57_de_novo_predictions.csv.

  Sec. 9 gave the iron chalcogenide 11-type family 55 candidates. The deposited
  file carries 441 tuples for it over a nine-point grid, so the family has 49
  records, which is what Table IV of the main text prints. Every other count in
  Sec. 9 reproduces exactly: 105 and 87 for MgB2-class, 79 and 37 for the
  122-type family, and 173 of 233 with coverage against 60 without.

  Sec. 9 and Table IV both gave seven paper-reported anchors for the iron
  chalcogenide family beside 24 reference-table anchors. Seven and 24 is 31,
  and the family holds 29 compounds. The deposit carries five anchors of type
  exact and 24 of type c_parent, which is 29. The same two counts reproduce for
  the other two families, one and 84 for MgB2-class and six and three for the
  122-type, so the defect is in this family alone.

  Sec. 12 compared the committed prediction scope against a substructure-
  aggregate fallback at 4.2 K and 1 T, on 53 non-refused iron chalcogenide
  candidates and 37 of the 122-type. The deposited file has no non-refused row
  at 1 T in any family: every 0.1 and 1 T target is refused for lying below the
  validated reduced field, which Sec. III.E of the main text states. Both
  families the comparison ran on emit nothing at any grid point, and the family
  that does emit was excluded from the comparison by construction. Nothing is
  left to compare, so the section is withdrawn rather than recomputed.

  The paragraph under Table S6 read a 0.22 dex field span off a candidate with
  a 16 T anchor. That candidate, Co0.05Fe0.95Se1, emits nothing under the
  current gates: its 0.1 and 1 T targets are refused for lying below the
  validated reduced field and its 5 T target for family field-axis validation.
  No dispatched candidate has a field span to read, because every dispatched
  target in the file is at 5 T.

Sec. 10 is left alone. Its screen counts, 21 refused below 4.2 K and 212
retained, of which 130 fall below the family calibration range and 82 at or
above with 81 inside, all reproduce from the deposit on the same record basis,
as do the five refusal rates and the 321 of 540 split under Table S6.

Usage:
    python3 analysis/apply_candidate_accounting_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final37.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final37.docx"
RESP = "RESPONSE_TO_REFEREES_final37.docx"
OUT = {MAIN: "HT10016_revised_final38.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final38.docx",
       RESP: "RESPONSE_TO_REFEREES_final38.docx"}

EDITS = [
    # ---- Sec. 9, the candidate count ------------------------------------
    (SUPP,
     "The 11-type iron chalcogenide has 55 candidates and complete coverage.",
     "The 11-type iron chalcogenide has 49 candidates and complete coverage."),

    # ---- Sec. 9, the anchor provenance ----------------------------------
    (SUPP,
     "seven anchors are paper-reported and 24 use FeSe, FeTe, or FeSe-Te "
     "substructure-reference anchors with deviation flags.",

     "five anchors are paper-reported and 24 use FeSe, FeTe, or FeSe-Te "
     "substructure-reference anchors with deviation flags, which together are "
     "the family's 29 compounds. An earlier version gave seven paper-reported "
     "anchors, which with the 24 exceeded the compound count."),

    # ---- Table IV, the same two counts ----------------------------------
    (MAIN,
     "Seven paper-reported anchors and 24 reference-table anchors",
     "Five paper-reported anchors and 24 reference-table anchors"),

    # ---- Sec. 12, withdrawn ---------------------------------------------
    (SUPP,
     "12. Prediction-scope sensitivity",
     "12. Prediction-scope sensitivity, withdrawn"),

    (SUPP,
     "The scope-sensitivity analysis compares the committed prediction scope "
     "with a substructure-aggregate fallback at the reference point "
     "T = 4.2 K and H = 1 T. For the 11-type iron chalcogenide, 53 non-refused "
     "candidates are evaluated. The median committed-minus-aggregate shift is "
     "−0.0003 dex, with an interquartile range of "
     "[−0.0007, −0.0003] dex. For the 122-type iron pnictide, 37 "
     "non-refused candidates are evaluated. The median shift is −0.018 "
     "dex, with an interquartile range of [−0.018, −0.018] dex. The "
     "MgB2 class is omitted from this comparison because its committed "
     "prediction scope is already a substructure aggregate.",

     "This section reported a comparison between the committed prediction "
     "scope and a substructure-aggregate fallback at the reference point "
     "T = 4.2 K and H = 1 T, on 53 non-refused iron chalcogenide 11-type "
     "candidates and 37 of the 122-type. It is withdrawn. The deposited "
     "prediction file holds no non-refused row at 1 T in any family: every "
     "target at 0.1 and 1 T is refused for lying below the validated reduced "
     "field, which Sec. III.E of the main text states. The two families the "
     "comparison ran on emit nothing at any grid point of this revision, and "
     "the one family that does emit, MgB2-class, was excluded from the "
     "comparison by construction, because its committed scope is already the "
     "substructure aggregate. There is nothing left to compare."),

    (SUPP,
     "These shifts are much smaller than the median bootstrap "
     "confidence-interval width of 0.61 dex, a factor of about 4.1 in Jc. For "
     "the 11-type iron chalcogenide, the negligible shift reflects the current "
     "cohort composition: the single-crystal cell dominates the Cohort B fits "
     "that pass the physicality checks. For iron pnictide 122-type, the "
     "committed rule gives a slightly more conservative prediction than the "
     "pooled substructure-aggregate rule, with a downward shift of about 18 "
     "millidex. The committed-scope predictions are therefore retained as the "
     "headline values because they meet the variance-decomposition diagnostic "
     "and produce changes that remain well below the calibrated uncertainty "
     "scale.",

     "The conclusion that rested on the comparison is withdrawn with it. It "
     "read that the committed-scope predictions are retained as the headline "
     "values because the shifts they produce are far below the calibrated "
     "uncertainty scale. The rule each family follows is set in Sec. II.D and "
     "reported in Sec. III.E of the main text, and the reason MgB2-class uses "
     "substructure-aggregate scope is the variance-decomposition diagnostic "
     "of Sec. III.A, not this comparison."),

    # ---- the paragraph under Table S6 ------------------------------------
    (SUPP,
     "The first three rows illustrate the structural property discussed in "
     "Sec. III.E of the main text: the field dependence over the evaluated "
     "grid is small, 0.22 dex from 0.1 to 5 T, because 5 T is a reduced field "
     "of 0.31 against this candidate’s 16 T anchor.",

     "The first two rows are the only kind of dispatched target the file "
     "holds, MgB2-class at 5 T. Every dispatched target in the file is at that "
     "field, because the 0.1 and 1 T targets of the same candidates are "
     "refused for lying below the validated reduced field, so neither this "
     "excerpt nor the file behind it can show how a dispatched prediction "
     "varies with field. What the two rows show is the span at fixed field "
     "across the two dispatched temperatures, 0.313 dex between 4.2 and 20 K. "
     "An earlier version of this paragraph read a 0.22 dex field span off a "
     "candidate with a 16 T anchor; that candidate is refused at all nine of "
     "its grid points under the gates of this revision."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_candidate_accounting_edits.py IN_DIR OUT_DIR")
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
