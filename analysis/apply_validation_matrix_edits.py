"""
apply_validation_matrix_edits.py

Propagates one validation status into every place that states one.

The problem, as the senior author put it: the documents give incompatible
validation statements. "Three validated substructure families" appears in the
abstract, in Table III's scope line and in the conclusion, while three other
places say the field axis is not validated at family level; Table IV's
validating-axis column labels the 11-type family "Temperature and field" and
the 122-type and MgB2 classes "Field only"; and Sec. III.E already says, in
prose, that no family carries a validated field axis after this revision and
that Table IV labels the temperature axis alone, which Table IV does not do.

analysis/validation_matrix.py computes the status once, per family and per
axis, with the paper's own estimator on the final cohorts. What it returns:

  temperature axis   iron chalcogenide 11-type 0.546, iron pnictide 1111-type
                     0.513 and iron pnictide 122-type 0.580 all clear the
                     screening-grade threshold. The MgB2 class has no fits in
                     that cohort and is not assessable. The 111-type family
                     holds one compound and is not assessable.
  field axis         the substructure label does not separate the field
                     exponent at all, eta squared 0.033 with a permutation
                     probability of 0.985, so no family-level verdict is
                     reported for any family. The per-family errors are 0.707,
                     1.230, 1.957 and 3.360.

Two consequences the wording has to carry. The three families that clear the
temperature-axis test are not the three the framework dispatches to: the
overlap is two, because the MgB2 class dispatches and is not assessable on that
axis while the 1111-type family is assessable and does not dispatch. And the
MgB2 class, which is the only family that emits anything at the current gate
settings, has no axis validating it.

Usage:
    python3 analysis/apply_validation_matrix_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final34.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final34.docx"
RESP = "RESPONSE_TO_REFEREES_final34.docx"
OUT = {MAIN: "HT10016_revised_final35.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final35.docx",
       RESP: "RESPONSE_TO_REFEREES_final35.docx"}

EDITS = [
    # ---- the abstract -------------------------------------------------
    (MAIN,
     "The framework then emits family-scope critical-current envelopes with "
     "bootstrap uncertainty for three validated substructure families, "
     "together with an explicit refusal decision for every candidate and "
     "prediction target.",

     "The framework then emits family-scope critical-current envelopes with "
     "bootstrap uncertainty for three substructure families, together with an "
     "explicit refusal decision for every candidate and prediction target. We "
     "state what validation stands behind that scope, since it is not uniform. "
     "Three families clear the compound leave-one-out threshold on the "
     "temperature axis, and no family-level verdict is reported on the field "
     "axis, where the substructure label does not separate the exponent at "
     "all. The MgB2 class, which is the only family that emits at the current "
     "gate settings, is one of the three that dispatch and not one of the "
     "three that clear: it carries no fits in the temperature-axis cohort and "
     "so is not assessable on the axis where the test can be run."),

    # ---- Table III's scope line ---------------------------------------
    (MAIN,
     "Candidate dispatch across 183 distinct compounds in three validated "
     "substructure families, of which one emits at the current gate settings.",

     "Candidate dispatch across 183 distinct compounds in three substructure "
     "families, of which one emits at the current gate settings. Two of the "
     "three clear the compound leave-one-out threshold on the temperature "
     "axis; the family that emits is not assessable on that axis and no "
     "family-level field verdict is reported for any family."),

    # ---- the conclusion -----------------------------------------------
    (MAIN,
     "The framework emits family-scope critical-current envelopes with "
     "calibrated uncertainty for three validated substructure families, "
     "together with an explicit refusal decision for each of 183 candidate "
     "compounds and each prediction target, of which 84 compounds receive at "
     "least one dispatched target.",

     "The framework emits family-scope critical-current envelopes with "
     "calibrated uncertainty for three substructure families, together with an "
     "explicit refusal decision for each of 183 candidate compounds and each "
     "prediction target, of which 84 compounds receive at least one dispatched "
     "target. The validation behind that scope is graded and we state it as "
     "such: three families clear the compound leave-one-out threshold on the "
     "temperature axis, no family-level verdict is reported on the field axis, "
     "and the one family that dispatches is not assessable on the temperature "
     "axis."),

    # ---- Table IV, the validating-axis column --------------------------
    (MAIN, "Temperature and field", "Temperature"),
]

# The two "Field only" cells are identical strings, so they are replaced by
# position among the table's cells rather than by content.
# The table's rows run 11-type, 122-type, MgB2-class, so the first "Field
# only" cell is the 122-type row and the second is the MgB2 row. The expected
# count falls from two to one between the two edits, which is what pins the
# order: if the table were ever reordered, the counts would not match.
CELL_EDITS = [("Field only", "Temperature", 2),
              ("Field only", "None reported", 1),
              ("Mixed", "Temperature for two families, none for MgB2-class",
               1)]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_validation_matrix_edits.py IN_DIR OUT_DIR")
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
        if name == MAIN:
            for find, repl, n_expected in CELL_EDITS:
                hits = [p for p in paragraphs(doc)
                        if unescape(plain(p)).strip() == find]
                if len(hits) != n_expected:
                    sys.exit("%s: %d cell(s) equal %r, expected %d"
                             % (name, len(hits), find, n_expected))
                new = replace_in_paragraph(hits[0], find, repl)
                if new is None:
                    sys.exit("%s: could not replace the cell %r" % (name, find))
                doc = doc.replace(hits[0], new, 1)
                print("   %-8s cell %-22s -> %s" % ("HT10016", find, repl))
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
