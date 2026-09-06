"""
compact_letter_stage5.py

Fourth and last batch of the letter compaction, B7. This pass removes
duplication between answers rather than tightening sentences: the corrections
paragraph restated four values the defects paragraph above it had already
given, the opening summary restated the four claims stated immediately before
it, and the reproducibility paragraph explained at length what one sentence
says.

Usage:
    python3 analysis/compact_letter_stage5.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final45.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final45.docx"
RESP = "RESPONSE_TO_REFEREES_final45.docx"
OUT = {MAIN: "HT10016_revised_final46.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final46.docx",
       RESP: "RESPONSE_TO_REFEREES_final46.docx"}

EDITS = [
    # ---- the opening summary duplicated the four claims above it ---------
    (RESP,
     "The central results survive and are stated more precisely. Universal "
     "reduced-variable scaling does not organize the corpus: it reduces the "
     "within-bin scatter by 13.0% on the standard-deviation scale, the result "
     "is insensitive to a 35% perturbation of the estimated critical fields, "
     "and Sec. III.D now tests the claim directly rather than against an "
     "adoption threshold we could give no construction for. The reduced "
     "coordinates carry no more structure than the same grid rotated to a "
     "random angle, and unnormalized temperature and applied field organize "
     "the same records better by isolating compounds. The conditioning claim "
     "rests on the temperature-axis separation of Sec. III.C, not on the "
     "variance-decomposition diagnostic and not on the error ratio Referee A "
     "questioned. The applicability claim is narrowed, field-axis results "
     "carry the scale that produced them, and the output is restated as "
     "family-scope envelopes with a refusal decision.",

     "Each of the four survives the corrections below, and each is narrower "
     "than the claim it replaces. The conditioning claim rests on the "
     "temperature-axis separation of Sec. III.C, not on the "
     "variance-decomposition diagnostic and not on the error ratio Referee A "
     "questioned. The applicability claim is graded by family and by axis "
     "rather than uniform, field-axis results carry the scale that produced "
     "them, and the output is a family-scope envelope with a refusal decision "
     "rather than a per-compound ranking."),

    # ---- the reproducibility standard ------------------------------------
    (RESP,
     "One further property bears on how the rest of this reply should be read. "
     "Every figure in the paper regenerates from the deposited data pixel for "
     "pixel, the candidate dispatch table regenerates from the deposited "
     "tables cell for cell, every printed count is asserted against those "
     "tables by a script that ships with the paper, and where a quantity could "
     "not be reproduced we say so and give the figure that can. The "
     "corrections listed below are the output of that standard, applied by us "
     "before submission, rather than a list of things we happened to notice.",

     "One property bears on how the rest of this reply should be read. Every "
     "figure regenerates from the deposited data pixel for pixel, the "
     "candidate dispatch table regenerates cell for cell, and every printed "
     "count is asserted against the deposited tables by a script that ships "
     "with the paper. The corrections below are the output of that standard "
     "rather than a list of things we happened to notice."),

    # ---- the corrections list, duplicating the defects above --------------
    (RESP,
     "Several values have been corrected as a result. The MgB2-class compound "
     "leave-one-out error is 0.753 rather than 0.772; the universal scaling "
     "reduction is 13.0% on the standard-deviation scale rather than 14.1%; "
     "the Stage 3 error is 0.816 rather than 0.84 and is no longer called a "
     "leave-one-substructure-out result; the propagated uncertainty is 0.27 "
     "dex rather than 0.29; and the external anchor-count errors are labelled "
     "in dex rather than as dimensionless exponent errors. The fifteen MgB2 "
     "temperature fits are described as the deposited file has them: six rest "
     "on three points rather than one, and the fit we reported with a "
     "root-mean-square residual of 6.3 has one of 6.3 times ten to the minus "
     "fourteen. The 233 evaluated records and the 212 retained after the "
     "calibration screen are record counts covering 183 distinct compounds. "
     "The Supplemental Material now carries the disposition of all 94 "
     "field-axis fits individually, which an earlier version of this letter "
     "said it did. A second pass, made after the tables were frozen, found "
     "seven more, all corrected and none changing a conclusion.",

     "Beyond the five above: the MgB2-class compound leave-one-out error is "
     "0.753 rather than 0.772, the universal scaling reduction is 13.0% on the "
     "standard-deviation scale rather than 14.1%, and the external "
     "anchor-count errors are labelled in dex rather than as dimensionless "
     "exponent errors. The fifteen MgB2 temperature fits are described as the "
     "deposited file has them: six rest on three points rather than one, and "
     "the fit we reported with a root-mean-square residual of 6.3 has one of "
     "6.3 times ten to the minus fourteen. The 233 evaluated records and the "
     "212 retained after the calibration screen are record counts covering 183 "
     "distinct compounds. A second pass, made after the tables were frozen, "
     "found seven more, all corrected and none changing a conclusion."),

    # ---- the narrow spread, closing repetition ----------------------------
    (RESP,
     "The small spread led to the largest change in the paper. The referee was "
     "right, and the explanation is structural. Section III.E now reports it, "
     "and this revision's reduced-field gate has narrowed what there is to "
     "report: only the MgB2 class still dispatches, and the iron chalcogenide "
     "and iron pnictide 122-type dispatches are refused in full. A count needs "
     "correcting first. The dispatch emits at two grid points, not one: 4.2 K "
     "and 5 T, where 86 records cover 84 compounds, and 20 K and 5 T, where 77 "
     "cover 75. Both clear this revision's gates, at reduced temperatures of "
     "0.10 to 0.70 against the 0.7 bound, the upper end reached at the 20 K "
     "point and a reduced field of 0.3226 against the 0.3 bound.",

     "The small spread led to the largest change in the paper. The referee was "
     "right and the explanation is structural, and this revision's "
     "reduced-field gate has narrowed what there is to report: only the MgB2 "
     "class still dispatches. A count needs correcting first. The dispatch "
     "emits at two grid points, not one: 4.2 K and 5 T, where 86 records cover "
     "84 compounds, and 20 K and 5 T, where 77 cover 75, both clearing this "
     "revision's gates at reduced temperatures of 0.10 to 0.70 and a reduced "
     "field of 0.3226."),

    # ---- the audit summary, second half -----------------------------------
    (RESP,
     "The transition-temperature anchor is a lookup table with per-substructure "
     "defaults rather than the paper-reported value the deposit labels it; six "
     "of the eighteen temperature-axis papers are wrong by 5 K or more, and we "
     "have replaced every anchor we could check with the value the paper "
     "prints. The applicability window was imposed on the temperature axis and "
     "not on the field axis, where nineteen of the 94 fits sat above the "
     "stated bound; it is now applied to both, and we say plainly that its "
     "field clause contains nothing independent of its own scale. The "
     "extracted curves carry four to twenty times less interaction between the "
     "temperature and field dependences than pixel traces of the same printed "
     "figures, which is why the field exponent now carries the qualification "
     "it does. And the deposited prediction file did not reproduce from its "
     "own generator, and now does: a scope rule had been applied to the file "
     "and never written into the code, and three of the four scripts that "
     "produce the table were named nowhere. One script now runs all four in "
     "order and compares the result with the released file cell by cell. "
     "Regenerating moved two printed numbers, the spread at 4.2 K and 5 T from "
     "0.0098 dex to 0.0085 and at 20 K and 5 T from 0.259 to 0.254, and "
     "changed nothing else.",

     "The transition-temperature anchor is a lookup table with "
     "per-substructure defaults rather than the paper-reported value the "
     "deposit labels it; six of the eighteen temperature-axis papers are wrong "
     "by 5 K or more, and we have replaced every anchor we could check with "
     "the value the paper prints. The applicability window was imposed on the "
     "temperature axis and not the field axis, where nineteen of the 94 fits "
     "sat above the stated bound; it is now applied to both, and we say "
     "plainly that its field clause contains nothing independent of its own "
     "scale. The extracted curves carry four to twenty times less interaction "
     "between the temperature and field dependences than pixel traces of the "
     "same printed figures, which is why the field exponent carries the "
     "qualification it does. And the deposited prediction file did not "
     "reproduce from its own generator, and now does: a scope rule had been "
     "applied to the file and never written into the code, and three of the "
     "four scripts producing the table were named nowhere. One script now runs "
     "all four and compares the result with the released file cell by cell. "
     "Regenerating moved the spread at 4.2 K and 5 T from 0.0098 dex to 0.0085 "
     "and at 20 K and 5 T from 0.259 to 0.254, and changed nothing else."),

    # ---- the temperature-axis separation, closing ------------------------
    (RESP,
     "The obvious objection to a family label is that it is compound identity "
     "with fewer labels, and that can be settled by enumeration rather than "
     "sampling: the eight compounds admit 966 distinct ways of forming three "
     "families, four reach the observed separation, and the exact probability "
     "is 0.0041, or 0.0083 with one observation per compound. One alternative "
     "grouping separates the exponent slightly better than the substructure "
     "label does, and Sec. III.C says so.",

     "The obvious objection to a family label is that it is compound identity "
     "with fewer labels, and enumeration settles it: the eight compounds admit "
     "966 ways of forming three families, four reach the observed separation, "
     "and the exact probability is 0.0041. One alternative grouping separates "
     "the exponent slightly better than the substructure label does, and "
     "Sec. III.C says so."),

    # ---- the 23-fold, opening --------------------------------------------
    (RESP,
     "The units were wrong. Errors in a fitted exponent are dimensionless, and "
     "labelling them in dex is what made 10.10 read as ten orders of magnitude "
     "in current density. This is corrected throughout. The cohorts were "
     "mismatched too, the larger error coming from nine substructure families "
     "and the smaller from the five carrying populated sample-form cells.",

     "The units were wrong: errors in a fitted exponent are dimensionless, and "
     "labelling them in dex is what made 10.10 read as ten orders of magnitude "
     "in current density. This is corrected throughout. The cohorts were "
     "mismatched too, the larger error coming from nine substructure families "
     "and the smaller from the five with populated sample-form cells."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: compact_letter_stage5.py IN_DIR OUT_DIR")
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    by_file = {}
    for f, find, repl in EDITS:
        by_file.setdefault(f, []).append((find, repl))
    saved = 0
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
            saved += len(find.split()) - len(repl.split())
            print("   %-4d -> %-4d   %s"
                  % (len(find.split()), len(repl.split()), find[:54]))
        tmp = op + ".part"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, doc)
                else:
                    zout.writestr(item, zin.read(item.filename))
        zin.close()
        shutil.move(tmp, op)
    print("   saved %d words" % saved)
    return 0


if __name__ == "__main__":
    sys.exit(main())
