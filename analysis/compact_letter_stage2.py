"""
compact_letter_stage2.py

First batch of the letter compaction, B7. Each answer is cut to four beats:
the concern, the test we ran, the change we made, and the claim that survives.
What goes is narrative, defensive framing, and facts the letter already states
somewhere else.

Five passages in this batch, 2315 words down to about 1200.

  P11  the opening summary repeated the 14.1% withdrawal, which the correction
       list at the end states, and closed by defending the manuscript's length
  P23  the field-exponent drift answer recounted the withdrawal of a worked
       example at the length of the investigation rather than of the finding
  P34  the narrow-spread answer restated the mechanism three times
  P44  the 23-fold answer carried the arithmetic of two withdrawn ratios
  P94  the correction list read as a paragraph and is now one sentence per
       correction with the reason attached

Nothing is dropped that appears nowhere else. Every number withdrawn here is
still withdrawn somewhere in the letter, which
analysis/final_consistency_check.py asserts.

Usage:
    python3 analysis/compact_letter_stage2.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final41.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final41.docx"
RESP = "RESPONSE_TO_REFEREES_final41.docx"
OUT = {MAIN: "HT10016_revised_final42.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final42.docx",
       RESP: "RESPONSE_TO_REFEREES_final42.docx"}

EDITS = [
    # ---------------- the opening summary -------------------------------
    (RESP,
     "The central results survive and are stated more precisely. Universal "
     "reduced-variable scaling does not organize the corpus. It reduces the "
     "within-bin scatter by 13.0% on the standard-deviation scale, replacing a "
     "previously reported 14.1% whose numerator and denominator had been "
     "computed on different populations, and that result is insensitive to a "
     "35% perturbation of the estimated critical fields. We have withdrawn the "
     "30% adoption threshold it was compared against, because we could give no "
     "construction for it, and Sec. III.D now tests the scaling claim "
     "directly: the reduced coordinates carry no more structure than the same "
     "grid rotated to a random angle, and unnormalized temperature and applied "
     "field organize the same records better by isolating compounds. The "
     "conditioning claim rests on the temperature-axis separation of Sec. "
     "III.C, not on the variance-decomposition diagnostic and not on the error "
     "ratio Referee A questioned. The applicability claim is narrowed, the "
     "field-axis results are retained but labelled with the scale that "
     "produced them, and the output is restated as family-scope envelopes "
     "together with a refusal decision. The manuscript is longer because each "
     "point needed its evidence set out, and it carries eleven displayed "
     "equations, four tables, and a numbered inference procedure.",

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
     "family-scope envelopes with a refusal decision."),

    # ---------------- the field-exponent drift ---------------------------
    (RESP,
     "That figure has moved since the deposited version and we give both: as "
     "first deposited there were 18 such series with a median of 0.70, rising "
     "to 0.80 in the nine sampled at four or more temperatures, and after the "
     "withdrawals described below there are 13 and 6, both at 0.80. The effect "
     "is unchanged in direction and slightly larger. A series is one source "
     "paper, one sample and one held scale, which is what makes the scale held "
     "by construction. We withdraw the worked example we gave, for two "
     "reasons. Its source, Physica C 469 (2009) 590, prints its field axis in "
     "kilo-oersted and the extraction recorded the bare numbers as tesla; "
     "corrected, the measured span falls from 0.53 to 0.053 of the assigned "
     "scale, all eight of its fits fail the 0.3 applicability bound, and they "
     "are withdrawn. Independently, the exponent is not monotone over the "
     "window we quoted: it falls from 1.25 at 2 K to 0.82 at 10 K before "
     "rising to 12.14 at 35 K, a rank correlation of 0.79 rather than the "
     "near-unity our phrasing implied. The sentence described a rise that does "
     "not happen over the first third of its own range, and we would have had "
     "to correct it whatever became of the unit. In its place, with a caveat "
     "we state rather than leave to be found: the clearest surviving case is "
     "the Ba(Fe,Co)2As2 single crystal of Materials Today Physics 27 (2022) "
     "100783, scale held at 4.5 T, whose exponent rises from 0.26 to 0.86 "
     "across nine temperatures from 4.2 to 18 K with a rank correlation of "
     "1.00. Exactly two series in the surviving cohort clear our filters and "
     "both come from that paper, the other a polycrystal record we have since "
     "identified as a copy of this one and withdrawn. This record is itself "
     "graded weak in our audit, sitting 1.3 to 1.7 times above a retrace of "
     "its own figure with a wrong tail, so we offer it as the best surviving "
     "illustration and not as a clean one. Over that range the exponent "
     "measures the misspecification rather than the pinning physics.",

     "On the repaired cohort that is 13 series, and 6 sampled at four or more "
     "temperatures, both at 0.80; as first deposited it was 18 series at 0.70, "
     "so the effect is unchanged in direction and slightly larger. A series is "
     "one source paper, one sample and one held scale, which is what makes the "
     "scale held by construction. We withdraw the worked example we gave. Its "
     "source, Physica C 469 (2009) 590, prints its field axis in kilo-oersted "
     "and the extraction recorded the bare numbers as tesla; corrected, its "
     "measured span falls to 0.053 of the assigned scale and all eight of its "
     "fits fail the 0.3 applicability bound. The exponent was also not "
     "monotone over the window we quoted, falling from 1.25 at 2 K to 0.82 at "
     "10 K before rising to 12.14 at 35 K, so the sentence would have needed "
     "correcting whatever became of the unit. The clearest surviving case is "
     "the Ba(Fe,Co)2As2 single crystal of Materials Today Physics 27 (2022) "
     "100783, scale held at 4.5 T, whose exponent rises from 0.26 to 0.86 "
     "across nine temperatures from 4.2 to 18 K with a rank correlation of "
     "1.00. We offer it as the best surviving illustration and not a clean "
     "one: our own audit grades it weak, and only two series in the surviving "
     "cohort clear our filters, both from that paper. Over that range the "
     "exponent measures the misspecification rather than the pinning physics."),

    # ---------------- the 23-fold answer ---------------------------------
    (RESP,
     "We withdraw the 1.07, 2.24 and 1.83 an earlier version of this reply "
     "quoted, because they repeat the defect they were introduced to replace. "
     "The sample-form scope is undefined for the MgB2 class, since once the "
     "cuprate families are gated out no other family contributes a bulk or "
     "wire fit, so 2.24 and 1.83 divide a four-family numerator by a "
     "three-family denominator, which is the mismatched-cohort error we "
     "identify above as the reason the 23-fold was wrong. Matched over the "
     "families the predictor can score they are 2.17 and 2.11; they were also "
     "the lowest of four ways of forming the conditional prediction, and the "
     "lowest is not the same one on every cohort. Nor is the protocol stable "
     "at this scope: on the 52 field-axis fits surviving the anchor repairs "
     "and the fitting protocol there are four families and four folds, the "
     "unconditioned stage is a two-parameter fit on three training points in "
     "each, and removing any single family moves the ratio between 0.74 and "
     "550. The objection is conceded more completely than our first reply "
     "conceded it. It is not that 23 was too large. It is that on a corpus of "
     "this size the benefit of conditioning cannot be separated from the noise "
     "of holding a family out, and we report the two errors and the family "
     "count rather than their quotient.",

     "We withdraw the 1.07, 2.24 and 1.83 an earlier version of this reply "
     "quoted, because they repeat the defect they were introduced to replace: "
     "the sample-form scope is undefined for the MgB2 class once the cuprate "
     "families are gated out, so two of the three divide a four-family "
     "numerator by a three-family denominator. Nor is any such ratio stable at "
     "this scope. On the 52 field-axis fits surviving the anchor repairs there "
     "are four families and four folds, the unconditioned stage is a "
     "two-parameter fit on three training points in each, and removing any "
     "single family moves the ratio between 0.74 and 550. The objection is "
     "conceded more completely than our first reply conceded it. It is not "
     "that 23 was too large. It is that on a corpus of this size the benefit "
     "of conditioning cannot be separated from the noise of holding a family "
     "out, so we report the two errors and the family count rather than their "
     "quotient."),

    # ---------------- the correction list --------------------------------
    (RESP,
     "The fifteen MgB2 temperature fits are described as the deposited file "
     "has them, six resting on three points rather than one, and the fit we "
     "reported with a root-mean-square residual of 6.3 has one of 6.3 times "
     "ten to the minus fourteen. The candidate cohort comprises 183 distinct "
     "compounds, and the 233 evaluated records and 212 retained after the "
     "calibration screen are record counts in which one compound may appear "
     "more than once. The Supplemental Material now carries the disposition of "
     "all 94 field-axis fits individually, which an earlier version of this "
     "letter said it did. A second pass, made after the tables were frozen, "
     "found seven more. All are corrected and none changes a conclusion. "
     "Section III.A was applying a clustered null that holds the sample-form "
     "counts fixed to two families and a looser one to the third, which made "
     "the MgB2-class floor read as a probability of 0.33; under the same null "
     "it applies to the other two, that family admits a single labelling and "
     "its probability is identically 1, so the caveat we make there is "
     "stronger than we stated it. Four places said the framework refuses to "
     "predict outside its validated scope, which our own conclusion "
     "contradicted two sentences later: the gates test a target against the "
     "window the exponents were calibrated over, and nothing refuses a family "
     "that could not be assessed, which is the family that emits. Section 9 of "
     "the Supplemental Material gave the iron chalcogenide family 55 "
     "candidates against Table IV's 49, and both that section and Table IV "
     "gave it seven paper-reported anchors beside 24 reference-table ones, "
     "which is more anchors than the family has compounds; the deposit gives "
     "five. Section 12 reported a scope comparison on 53 and 37 non-refused "
     "candidates at 1 T, where the deposited file has none in any family, and "
     "we withdraw it rather than recompute it, because the two families it ran "
     "on emit nothing and the one that emits was excluded from it by "
     "construction. The paragraph under Table S6 read a field span off a "
     "candidate that is refused at all nine of its grid points. And two counts "
     "were quoted on the cohort as deposited inside sentences quoting the "
     "repaired one: the iron pnictide 122-type family carries 105 "
     "temperature-axis fits rather than 106, and the temperature-axis cohort "
     "is drawn from 18 source papers, all of them arXiv preprints, rather than "
     "18 of 20. Two values the submitted manuscript carried are withdrawn and "
     "are recorded here rather than in the paper. Section III.B compared the "
     "one-anchor error of 1.592 dex against an in-corpus baseline of 0.567; "
     "that value is not derivable from the deposit and is not on the same "
     "scale as the quantity it was compared with, so no in-corpus baseline is "
     "quoted. Section III.E reported family medians of 6.00, 5.75 and 5.32 in "
     "log10 Jc at 0.1 T together with a top-quartile slice that was entirely "
     "iron chalcogenide 11-type; every prediction behind both is refused by "
     "this revision's reduced-field gate, so both are withdrawn rather than "
     "restated.",

     "The fifteen MgB2 temperature fits are described as the deposited file "
     "has them: six rest on three points rather than one, and the fit we "
     "reported with a root-mean-square residual of 6.3 has one of 6.3 times "
     "ten to the minus fourteen. The 233 evaluated records and the 212 "
     "retained after the calibration screen are record counts covering 183 "
     "distinct compounds, in which one compound may appear more than once. The "
     "Supplemental Material now carries the disposition of all 94 field-axis "
     "fits individually, which an earlier version of this letter said it did. "
     "A second pass, made after the tables were frozen, found seven more, all "
     "corrected and none changing a conclusion. Section III.A applied a "
     "clustered null holding the sample-form counts fixed to two families and "
     "a looser one to the third, which made the MgB2-class floor read as 0.33; "
     "under the same null, that family admits one labelling and its "
     "probability is identically 1, so the caveat we make there is stronger "
     "than we stated it. Four places said the framework refuses to predict "
     "outside its validated scope, which our own conclusion contradicted two "
     "sentences later: the gates test a target against the calibrated window, "
     "and nothing refuses a family that could not be assessed, which is the "
     "family that emits. Supplemental Sec. 9 gave the iron chalcogenide family "
     "55 candidates against Table IV's 49, and both gave it seven "
     "paper-reported anchors beside 24 reference-table ones, more anchors than "
     "the family has compounds; the deposit gives five. Supplemental Sec. 12 "
     "compared prediction scopes on 53 and 37 non-refused candidates at 1 T, "
     "where the deposited file has none in any family; we withdraw it rather "
     "than recompute it, since the families it ran on emit nothing and the one "
     "that emits was excluded by construction. The paragraph under Table S6 "
     "read a field span off a candidate refused at all nine of its grid "
     "points. And two counts were quoted on the cohort as deposited inside "
     "sentences quoting the repaired one: the 122-type family carries 105 "
     "temperature-axis fits rather than 106, and the temperature-axis cohort "
     "comes from 18 source papers, all arXiv preprints, rather than 18 of 20. "
     "Two values the submitted manuscript carried are withdrawn and recorded "
     "here rather than in the paper: the in-corpus baseline of 0.567 that "
     "Sec. III.B compared the 1.592 dex one-anchor error against, which is "
     "neither derivable from the deposit nor on the same scale, and the family "
     "medians of 6.00, 5.75 and 5.32 in log10 Jc at 0.1 T that Sec. III.E "
     "reported with a top-quartile slice entirely of iron chalcogenide "
     "11-type, every prediction behind which this revision's reduced-field "
     "gate refuses."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: compact_letter_stage2.py IN_DIR OUT_DIR")
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
            print("   %-8s %-4d -> %-4d words   %s"
                  % (name.split("_")[0][:8], len(find.split()),
                     len(repl.split()), find[:46]))
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
