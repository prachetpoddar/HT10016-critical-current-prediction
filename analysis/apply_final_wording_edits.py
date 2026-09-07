"""
apply_final_wording_edits.py

Hossain's five closing items. Wording only; no analysis changes and no number
moves.

1  One formulation for the sample-form claim. The Results text already said
   the diagnostic sets an operational rule and does not establish a sample-form
   effect, because sample form is nearly a relabelling of source paper. Table
   III's claim cell still said "required conditioning variable", the Fig. 3
   caption still said "requiring sample-form-conditioned prediction", and the
   conclusion still called substructure family and sample form "the required
   conditioning variables". All three now use the same formulation: sample form
   defines an operational conditioning regime in the present corpus. The 81%,
   37% and 4% effect sizes and the source-paper confounding caveat stay, and the
   broader claim that measurement context must be preserved is untouched.

2  Validation language matched to the dispatch logic. Fig. 1's caption said
   envelopes are emitted "only when the validation gates are satisfied", and
   Fig. 5's said "validated candidate substructures". Neither is true of a
   framework whose only emitting family is not assessable on the axis where the
   test can be run. Both now say what the gates actually do and that the
   validation status travels with the output.

3  The residual positive field-axis claim removed. Table III's interpretation
   said conditioning "recovers signal that pooled regression treats as noise",
   and the conclusion still gave an at-most-two-fold field-exponent improvement,
   in a paper that reports no family-level field verdict and an unstable
   comparison. Both now state the field axis as inconclusive at this corpus size
   and provenance quality. The temperature-axis separation, the universal-scaling
   failure, the source-paper holdout and the critical-scale provenance finding
   are untouched.

4  The response letter closed as a finished audit. "A pass ... found five more
   defects" followed by "a second pass ... found seven more" reads as an audit
   still expanding. One framing replaces both, and the quantitative detail of
   each correction stays where it was.

Usage:
    python3 analysis/apply_final_wording_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final51.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final51.docx"
RESP = "RESPONSE_TO_REFEREES_final51.docx"
OUT = {MAIN: "HT10016_revised_final52.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final52.docx",
       RESP: "RESPONSE_TO_REFEREES_final52.docx"}

EDITS = [
    # ---------------- 1, one sample-form formulation --------------------
    (MAIN,
     "Sample form is a required conditioning variable.",
     "Sample form defines an operational conditioning regime in the present "
     "corpus."),

    (MAIN,
     "The fraction of variance explained by sample form defines the prediction "
     "regime. Iron chalcogenide 11-type materials show strong sample-form "
     "separation, requiring sample-form-conditioned prediction. Iron pnictide "
     "122-type materials show intermediate separation, so sample-form "
     "conditioning is used when available. MgB2-class materials show weak "
     "separation, so the model falls back to substructure-level aggregation.",

     "The fraction of variance explained by sample form defines the "
     "operational conditioning regime the predictor follows in this corpus, "
     "and not an independently established sample-form effect: sample form is "
     "very nearly a relabelling of source paper here, which Sec. III.A states "
     "with the exact probabilities that follow from it. Iron chalcogenide "
     "11-type materials show the strongest separation, so the predictor "
     "conditions on sample form where the cell is populated. Iron pnictide "
     "122-type materials show intermediate separation and are conditioned the "
     "same way where the cell allows. MgB2-class materials show weak "
     "separation, so the model uses substructure-level aggregation "
     "throughout."),

    (MAIN,
     "In superconductors this work identifies substructure family and sample "
     "form as the required conditioning variables.",

     "In superconductors this work identifies substructure family as the "
     "conditioning variable the data separate, and sample form as one that "
     "defines an operational conditioning regime in the present corpus."),

    # ---------------- 2, validation language ----------------------------
    (MAIN,
     "emits family-scope critical-current envelopes only when the validation "
     "gates are satisfied,",

     "emits family-scope critical-current envelopes when the applicable "
     "refusal gates are satisfied, with axis-specific validation status "
     "carried with the output,"),

    (MAIN,
     "FIG. 5. Family-scope critical-current envelopes for validated candidate "
     "substructures, plotted across the range over which the exponents are "
     "validated.",

     "FIG. 5. Family-scope critical-current envelopes with axis-specific "
     "validation status, plotted across the range over which the exponents are "
     "validated."),

    # ---------------- 3, the field-axis claim ---------------------------
    (MAIN,
     "Conditioning reduces cross-family exponent error.",
     "Conditioning reduces the cross-family field-exponent error."),

    (MAIN,
     "Conditioning recovers signal that pooled regression treats as noise, "
     "subject to the field-scale qualification of Sec. III.F.",

     "Inconclusive at the present corpus size and provenance quality. The "
     "comparison is unstable across cohorts, neither predictor is "
     "distinguishable from an unconditioned median, and no family-level "
     "field-axis verdict is retained."),

    (MAIN,
     "Conditioning by substructure reduces the cross-family field-exponent "
     "error by at most about two-fold under leave-one-substructure-out "
     "validation, and by less on some cohorts.",

     "On the field axis the effect of conditioning is inconclusive at the "
     "present corpus size and provenance quality: the leave-one-substructure-"
     "out comparison is unstable across cohorts, neither predictor is "
     "distinguishable from an unconditioned median, and no family-level "
     "verdict is retained."),

    # ---------------- 4, the letter as a finished audit -----------------
    (RESP,
     "A pass over every reported quantity found five more defects, all "
     "corrected.",

     "Our final reproducibility audit identified the following additional "
     "inconsistencies; all have been corrected and are now covered by "
     "automated consistency checks."),

    (RESP,
     "Beyond the five above: the MgB2-class compound leave-one-out error",
     "The same audit also reached the following. The MgB2-class compound "
     "leave-one-out error"),

    (RESP,
     "A second pass, made after the tables were frozen, found seven more, all "
     "corrected and none changing a conclusion. Section III.A applied",

     "Section III.A applied"),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_final_wording_edits.py IN_DIR OUT_DIR")
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
            print("   %-8s %s" % (name.split("_")[0][:8], find[:60]))
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
