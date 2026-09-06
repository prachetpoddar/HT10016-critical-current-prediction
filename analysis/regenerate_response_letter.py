"""
regenerate_response_letter.py

Brings the response letter up to the manuscript at v29.

The letter answered every point in both reports and still does, so the
referee-by-referee responses are left alone. What had fallen behind is
everything the 2026-09-06 audit changed. Six items were in the manuscript and
absent from the letter: Stage 3's correction to 0.816, the propagated
uncertainty at 0.27 dex, Form 3 resting on separability rather than on the
Table II margin, the reversal of the applicability result on the rebuilt
exponents, the exhaustive compound-level null, and the source-paper holdout.
Two things the letter did carry were worse than absent, because the manuscript
now contradicts them: that correcting the anchors makes the substructure
separation stronger, and the phrase about the result improving under every
correction.

Three edits.

  1. The substructure paragraph is rewritten. It kept only the half of the
     history that flattered the result. It now carries the pre-withdrawal
     value, the fact that the withdrawal screen is not independent of the
     exponent, the probability that moved the wrong way at the reproducibility
     step, the figure rebuild, and the compound-level null that answers the
     objection the referee is most likely to raise.
  2. A new paragraph under the audit section reports the five defects found on
     2026-09-06 that the letter does not mention.
  3. The corrected-values paragraph gains the values that moved.

Usage:
    python3 analysis/regenerate_response_letter.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final29.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final29.docx"
RESP = "RESPONSE_TO_REFEREES_final29.docx"
OUT = {MAIN: "HT10016_revised_final30.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final30.docx",
       RESP: "RESPONSE_TO_REFEREES_final30.docx"}

EDITS = [
    # ---- 1. the substructure separation, told in full -------------------
    (RESP,
     "On the temperature axis the families separate, and correcting the "
     "anchors makes the separation stronger. Matched on the seventeen papers "
     "common to both versions, the fraction of between-paper variance the "
     "family accounts for rises from 0.44 to 0.52, with a permutation "
     "probability falling from 0.016 to 0.007.",

     "On the temperature axis the families separate. Matched on the seventeen "
     "papers common to both versions, the fraction of between-paper variance "
     "the family accounts for is 0.44 before the anchor correction and 0.52 "
     "after, with permutation probabilities of 0.016 and 0.007. We reported "
     "that earlier as a result that strengthened under every correction, and "
     "we withdraw that description, because the full history does not support "
     "it and a referee reading the deposit would find so. Three things belong "
     "beside the number. Before the eleven paper withdrawals there is no "
     "separation at all: the fraction is 0.107 with a probability of 0.355. "
     "Our own note on those withdrawals records that the screen which selected "
     "them is not independent of the exponent, and that it acted in opposite "
     "directions in different families, so most of the rise cannot be read as "
     "evidence. At the step that removed two papers whose extractions could "
     "not be reproduced, the fraction rose while the probability rose with it, "
     "from 0.012 to 0.016, so the two halves of the result did not move "
     "together. And the exponents themselves do not reproduce from their own "
     "figures: of the fourteen we could score against a pixel trace, none "
     "does, at a median ratio of 0.42. On the exponents rebuilt from those "
     "traces, which are deposited with the paper, the separation survives at "
     "0.359 with a probability of 0.037 while the applicability result does "
     "not. What we can defend is narrower than what we first wrote and it is "
     "tested harder. The obvious objection to a family label is that it is "
     "compound identity with fewer labels, and on this cohort that objection "
     "can be settled by enumeration rather than by sampling: the eight "
     "compounds admit 966 distinct ways of forming three families, four of "
     "them reach the observed separation, and the exact probability is 0.0041, "
     "or 0.0083 with one observation per compound. One of the alternative "
     "groupings separates the exponent slightly better than the substructure "
     "label does, and Sec. III.C says so."),

    # ---- 2. the audit of 2026-09-06 -------------------------------------
    (RESP,
     "We therefore state the substructure result as a temperature-axis result, "
     "and we report the field axis as not separating the families rather than "
     "omitting it.",

     "We therefore state the substructure result as a temperature-axis result, "
     "and we report the field axis as not separating the families rather than "
     "omitting it. A final pass over every reported quantity, made after "
     "the audit above, found five more defects and we correct all of them. The "
     "adoption threshold of 30% that our universality claim was compared "
     "against had no construction anywhere in our analysis, and the quantity "
     "its own defining sentence named as the benchmark was twenty times "
     "smaller. It is withdrawn, and Sec. III.D now tests the scaling claim "
     "directly instead, against coordinates chosen to carry no physics. Stage "
     "3's error of 0.84 was described as a leave-one-substructure-out result "
     "and is not one: the held-out family predicted itself, which is the same "
     "defect we concede above for Stages 1 and 2, from the same run. Under "
     "genuine withholding it is 0.816. The propagated uncertainty of 0.29 dex "
     "used a temperature-exponent scatter that does not reproduce from our own "
     "deposit and that predates the anchor repair; on the repaired exponent it "
     "is 0.27 dex, and the accompanying statement that a correlation between "
     "the terms would make it a lower bound is wrong for this functional form, "
     "so we now claim no bound. Table II's holdout margin does not separate "
     "Form 3 from Form 2 once the three forms are scored on identical rows and "
     "the same compounds, so Sec. II.C now adopts Form 3 for the separability "
     "the rest of the paper requires and reports the comparison as it falls. "
     "And the per-family parameters behind Figure 5 could not be regenerated "
     "from the deposit at all, because the module that produced them fitted "
     "them to the predictor's own output; they are now the family median "
     "exponents over the fitted cohorts, and the figure moves with them."),

    # ---- 3. the corrected values ----------------------------------------
    (RESP,
     "Several values have been corrected as a result. The MgB2-class compound "
     "leave-one-out error is 0.753 rather than 0.772. The universal scaling "
     "reduction is 13.0% on the standard-deviation scale rather than 14.1%.",

     "Several values have been corrected as a result. The MgB2-class compound "
     "leave-one-out error is 0.753 rather than 0.772. The universal scaling "
     "reduction is 13.0% on the standard-deviation scale rather than 14.1%. "
     "The Stage 3 error is 0.816 rather than 0.84 and is no longer called a "
     "leave-one-substructure-out result. The external anchor-count errors are "
     "labelled in dex rather than as dimensionless exponent errors, which is "
     "the same unit repair we describe above applied where we had missed it. "
     "The propagated uncertainty is 0.27 dex rather than 0.29. The fifteen "
     "MgB2 temperature fits are described as the deposited file has them, six "
     "of them resting on three points rather than one, and the fit we reported "
     "with a root-mean-square residual of 6.3 has one of 6.3 times ten to the "
     "minus fourteen. The Supplemental Material now carries the disposition of "
     "all 94 field-axis fits individually, which an earlier version of this "
     "letter said it did."),
    # ---- 4. the second, stale copy of the withdrawn description ---------
    # It sits inside the Referee A response, well away from the paragraph
    # edited above, and repeats the claim that paragraph withdraws. It also
    # carries one of the two pieces of jargon this letter should not use.
    (RESP,
     "The point for this objection is only that the conditioning claim is a "
     "temperature-axis claim, that it is the one result in this paper that "
     "improved under every correction we made, and that neither the ratio the "
     "referee questioned nor the sample-form diagnostic is load-bearing for "
     "it.",

     "The point for this objection is only that the conditioning claim is a "
     "temperature-axis claim, and that neither the ratio the referee "
     "questioned nor the sample-form diagnostic carries it. We had also "
     "described it as the one result that improved under every correction; the "
     "audit section below withdraws that description and gives the full "
     "history in its place."),
]



def main():
    if len(sys.argv) != 3:
        sys.exit("usage: regenerate_response_letter.py IN_DIR OUT_DIR")
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
