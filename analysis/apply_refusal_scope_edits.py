"""
apply_refusal_scope_edits.py

Makes one claim consistent: what the refusal gates actually screen.

Four places said the framework refuses to predict outside its validated scope.
After this revision that is not true of the framework as it now stands, and the
conclusion says so two sentences later in the same paragraph. The one family
that emits at the current gate settings, MgB2-class, carries no fits in the
temperature-axis cohort, so the compound leave-one-out test cannot be run on it
at all, and no family carries a validated field axis. The gates test a target
against the window the exponents were calibrated over, and on the field axis
they refuse a family that failed validation. They do not refuse a family that
could not be assessed, which is the family that emits.

The fix is to say window where the documents said validated scope, and to state
the gap once, plainly, rather than let the conclusion contradict its own opening
sentence.

  manuscript Sec. II.C   "inside the validated scope" -> inside the calibrated
                         window, carrying its validation status
  manuscript Sec. II.D   the refusal-logic paragraph gains the sentence saying
                         which families the gates cannot screen
  manuscript conclusion  "prevent predictions outside the validated scope" ->
                         outside the calibrated window
  response opening       the four-claims list, which led with the sentence

Usage:
    python3 analysis/apply_refusal_scope_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final36.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final36.docx"
RESP = "RESPONSE_TO_REFEREES_final36.docx"
OUT = {MAIN: "HT10016_revised_final37.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final37.docx",
       RESP: "RESPONSE_TO_REFEREES_final37.docx"}

EDITS = [
    # ---- Sec. II.C, the third of the three operations -------------------
    (MAIN,
     "Third, the model emits a prediction only when the target compound lies "
     "inside the validated scope.",

     "Third, the model emits a prediction only when the target lies inside "
     "the window over which the exponents were calibrated, and every emitted "
     "value carries the validation status of its family and axis."),

    # ---- Sec. II.D, the refusal-logic paragraph -------------------------
    (MAIN,
     "The refusal system is part of the model definition, setting the "
     "physical and statistical scope over which predictions are valid.",

     "The refusal system is part of the model definition, setting the window "
     "over which predictions are emitted. One thing it does not do, and we "
     "state it here rather than leave it to be inferred: a family that cannot "
     "be assessed on an axis is not refused on that axis. On the field axis a "
     "family that fails validation is refused, and 1.9% of candidate grid "
     "points are refused for that reason. On the temperature axis there is no "
     "such gate, and the MgB2 class carries no fits in the temperature-axis "
     "cohort, so the compound leave-one-out test cannot be run on it and it "
     "dispatches under the same gates as a family that passed. Section III.C "
     "gives the status of each family on each axis, and every emitted value "
     "carries it."),

    # ---- the conclusion -------------------------------------------------
    (MAIN,
     "and explicit refusal gates prevent predictions outside the validated "
     "scope.",

     "and explicit refusal gates prevent predictions outside the window over "
     "which the exponents were calibrated."),

    # ---- the response letter's opening claim ----------------------------
    (RESP,
     "The framework declines to predict outside its validated scope. Of the "
     "targets it was asked for, 1054 are refused for lying below the "
     "validated reduced field and 93 for lying at or above the "
     "reduced-temperature bound, leaving 163 emitted over 84 compounds, each "
     "carrying the scope it was emitted under.",

     "The framework declines to predict outside the window its exponents were "
     "calibrated over, and labels every value it does emit with the "
     "validation behind it. Of the targets it was asked for, 1054 are refused "
     "for lying below the calibrated reduced field and 93 for lying at or "
     "above the reduced-temperature bound, leaving 163 emitted over 84 "
     "compounds. We are explicit about what the gates do not do. They test a "
     "target against that window, and on the field axis they refuse a family "
     "that failed validation, but nothing refuses a family that could not be "
     "assessed. That is the family which emits: MgB2-class carries no fits in "
     "the temperature-axis cohort, so the compound leave-one-out test cannot "
     "be run on it. The emitted values say so."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_refusal_scope_edits.py IN_DIR OUT_DIR")
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
