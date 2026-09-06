"""
compact_letter_stage6.py

Final batch of the letter compaction, B7. Referee B's six clarification
answers and three of Referee A's limitation answers, each cut to what changed
in the paper and where to find it.

Usage:
    python3 analysis/compact_letter_stage6.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final46.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final46.docx"
RESP = "RESPONSE_TO_REFEREES_final46.docx"
OUT = {MAIN: "HT10016_revised_final47.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final47.docx",
       RESP: "RESPONSE_TO_REFEREES_final47.docx"}

EDITS = [
    (RESP,
     "Not quite. The earlier text invited that reading, and we have corrected "
     "it. There is one model and three prediction scopes over the same fitted "
     "exponents. Section II.D now carries a short paragraph headed Three "
     "scopes, not three models which states this directly. Stage 1 regresses "
     "the exponent against a compositional descriptor and is used for rank "
     "signal and substructure classification, not as a final predictor. Stage "
     "2 uses the median exponent within a cell defined by substructure and "
     "sample form, and is selected when the candidate’s sample form is "
     "known and that cell is populated. Stage 3 uses the substructure-level "
     "median with the within-family interquartile range retained as "
     "uncertainty, and is selected when the sample form is unknown or the cell "
     "is too sparse. The variance-decomposition diagnostic decides, family by "
     "family, whether Stage 2 is justified at all. What differs between the "
     "three is the scope over which the same quantities are aggregated, not "
     "the class of model.",

     "Not quite, and the earlier text invited that reading. There is one model "
     "and three prediction scopes over the same fitted exponents, which "
     "Section II.D now states under the heading Three scopes, not three "
     "models. Stage 1 regresses the exponent against a compositional "
     "descriptor and serves for rank signal and substructure classification, "
     "not as a final predictor. Stage 2 takes the median exponent within a "
     "(substructure, sample form) cell when the candidate's form is known and "
     "that cell is populated. Stage 3 takes the substructure-level median with "
     "the within-family interquartile range as uncertainty, when the form is "
     "unknown or the cell is too sparse, and the variance-decomposition "
     "diagnostic decides family by family whether Stage 2 is justified at all. "
     "What differs is the scope over which the same quantities are aggregated, "
     "not the class of model."),

    (RESP,
     "The referee’s reconstruction is correct. We have written it out as "
     "a numbered procedure in Section II.D so that a reader need not "
     "reconstruct it. For a candidate with no critical-current measurements: "
     "assign the substructure family from stoichiometry and crystal system, "
     "refusing if the family is unpopulated or the classification is "
     "ambiguous; obtain the transition temperature anchor, and the critical "
     "field anchor if a field-axis prediction is requested, refusing that "
     "target if the required anchor is unavailable; check that at least three "
     "anchor measurements are available for the candidate; read the "
     "variance-decomposition regime for that family to select Stage 2 or Stage "
     "3; take the median parameters from the selected cell; evaluate the "
     "expression at the requested temperature and field and propagate "
     "uncertainty by quadrature over the three fitted terms; and apply the "
     "remaining gates, refusing with a reason code if any fails. We close the "
     "procedure by noting that the parameter-taking and evaluation steps use "
     "family-level quantities only, which is the structural fact underlying "
     "our decision to withhold per-compound rankings.",

     "The referee's reconstruction is correct, and Section II.D now writes it "
     "out as a numbered procedure. For a candidate with no critical-current "
     "measurements: assign the substructure family from stoichiometry and "
     "crystal system, refusing if it is unpopulated or ambiguous; obtain the "
     "transition-temperature anchor, and the critical-field anchor if a "
     "field-axis target is requested, refusing that target if it is "
     "unavailable; require at least three anchor measurements; read the "
     "variance-decomposition regime for the family to select Stage 2 or Stage "
     "3; take the median parameters from that cell; evaluate the expression "
     "and propagate uncertainty by quadrature over the three fitted terms; and "
     "apply the remaining gates, refusing with a reason code if any fails. The "
     "procedure closes by noting that the parameter and evaluation steps use "
     "family-level quantities only, which is why we withhold per-compound "
     "rankings."),

    (RESP,
     "They are not the MAGPIE set. We now name the model rather than leaving "
     "it to be inferred. Section III.A states that the Stage 1 regression is a "
     "univariate ordinary least squares fit on the mean maximum Pauling "
     "electronegativity, evaluated across seven substructure families with "
     "leave-one-substructure-out validation. An earlier version of this reply "
     "reported the descriptor's rank correlation as a Spearman coefficient of "
     "0.635 with a 95% confidence interval from 0.061 to 0.948. That is "
     "withdrawn in Section III.A: it was computed on a nine-family version of "
     "the descriptor table and on the mean field exponent, where this stage "
     "regresses the median, and on the seven families that remain no interval "
     "can be estimated tightly enough to be worth quoting. What we report "
     "instead is the quantity this stage was validated on, its rank-position "
     "error, which is 1.00 with six of the seven families placed within one "
     "position. That is why Stage 1 is retained for ranking and classification "
     "rather than for magnitude.",

     "They are not the MAGPIE set, and we now name the model rather than "
     "leaving it to be inferred: Section III.A states that the Stage 1 "
     "regression is a univariate ordinary least squares fit on the mean "
     "maximum Pauling electronegativity across seven substructure families "
     "with leave-one-substructure-out validation. We withdraw the Spearman "
     "coefficient of 0.635 with its interval from 0.061 to 0.948 that an "
     "earlier version of this reply quoted: it was computed on a nine-family "
     "descriptor table and on the mean field exponent where this stage "
     "regresses the median, and on the seven families that remain no interval "
     "can be estimated tightly enough to be worth quoting. We report instead "
     "the quantity this stage was validated on, its rank-position error of "
     "1.00 with six of seven families placed within one position, which is why "
     "Stage 1 is retained for ranking and classification rather than for "
     "magnitude."),

    (RESP,
     "Defined at first use in Section II.C, together with the intercept and "
     "the dex convention. A scaling exponent is the fitted power to which the "
     "reduced distance from a critical scale is raised, and it is "
     "dimensionless. The referee’s question also exposed a second "
     "problem, which we have now separated out. The manuscript previously used "
     "one symbol for the field exponent while the analysis realized it against "
     "two different definitions of the critical scale. Section II.C now "
     "carries a paragraph headed Two implementations of the field-axis "
     "critical scale. The two are identical for the 61 of 159 fits that fall "
     "back to the literature default. For the 98 fits where a paper-derived "
     "value was resolved, that value is a median factor of 6.4 smaller. Every "
     "result in Section III is labelled with the implementation that produced "
     "it.",

     "Defined at first use in Section II.C, with the intercept and the dex "
     "convention: a scaling exponent is the fitted power to which the reduced "
     "distance from a critical scale is raised, and it is dimensionless. The "
     "question also exposed a second problem. The manuscript used one symbol "
     "for the field exponent while the analysis realized it against two "
     "definitions of the critical scale, which Section II.C now separates "
     "under the heading Two implementations of the field-axis critical scale. "
     "The two are identical for the 61 of 159 fits that fall back to the "
     "literature default; for the 98 where a paper-derived value was resolved, "
     "that value is a median factor of 6.4 smaller. Every result in Section "
     "III is labelled with the implementation that produced it."),

    (RESP,
     "The runtime workflow is now six stages rather than five. Following the "
     "referee's arrows showed that a stage was missing from the architecture, "
     "not only a line: between extraction and fitting the workflow resolves "
     "the transition temperature and the critical field for each fitted curve, "
     "and that stage was not shown at all. It is where the defects reported "
     "below occur. The critical-scale resolution stage is now shown explicitly "
     "with its provenance tiers, and the caption specifies labelled arrows "
     "carrying the information passed between stages. The figure has been "
     "redrawn to that specification: a vertical six-stage flow in which every "
     "arrow is labelled with what it carries, and the critical-scale "
     "resolution stage is highlighted. The refusal branch leaves the dispatch "
     "stage explicitly, so that refusal reads as an output of the predictor "
     "rather than as an omission.",

     "Following the referee's arrows showed that a stage was missing from the "
     "architecture, not only a line: between extraction and fitting the "
     "workflow resolves the transition temperature and the critical field for "
     "each fitted curve, and that stage was not shown at all. It is where the "
     "defects reported below occur. The workflow is now six stages, redrawn as "
     "a vertical flow in which every arrow is labelled with what it carries "
     "and the critical-scale resolution stage is shown explicitly with its "
     "provenance tiers. The refusal branch leaves the dispatch stage "
     "explicitly, so that refusal reads as an output of the predictor rather "
     "than as an omission."),

    (RESP,
     "The data-layer limitations of Section III.F now record that the "
     "framework has not been validated on the deployed conductor materials, "
     "that REBCO in particular does not obey our expression over the ranges of "
     "interest, and that the cuprates enter the work two ways, five cuprate "
     "papers in the fitted cohort and four out-of-corpus cuprates as the "
     "external validation set, where they exhibit measurement-window "
     "saturation. We concede the point and state it as a limit on the work "
     "rather than as a gap to be filled later. We add the referee's point that "
     "these materials have critical fields higher than can be directly "
     "measured and a much stronger field-angle dependence, which means that "
     "extending the framework to them is not a matter of adding data. It would "
     "require a functional form appropriate to their pinning behaviour and an "
     "orientation-resolved treatment that our current extraction does not "
     "support.",

     "The data-layer limitations of Section III.F now record that the "
     "framework has not been validated on the deployed conductor materials, "
     "that REBCO in particular does not obey our expression over the ranges of "
     "interest, and that the cuprates enter two ways, five papers in the "
     "fitted cohort and four out-of-corpus cuprates as the external validation "
     "set where they show measurement-window saturation. We state it as a "
     "limit on the work rather than a gap to be filled later, and add the "
     "referee's point that these materials have critical fields higher than "
     "can be directly measured and a much stronger field-angle dependence. "
     "Extending the framework to them is not a matter of adding data: it would "
     "need a functional form appropriate to their pinning behaviour and an "
     "orientation-resolved treatment our extraction does not support."),

    (RESP,
     "We have adopted this reframing as the paper’s stated output rather "
     "than as a caveat added to it. The abstract now says that the framework "
     "emits family-scope envelopes together with an explicit refusal decision, "
     "and that within a family the envelope is a single curve shared by all "
     "member candidates. Section III.E demonstrates it with the counts given "
     "above, Assumption 4 of Section III.F states it as a bound on inferential "
     "scope, and the caption of Figure 5 repeats it. We have removed the "
     "phrasing that could be read as a ranking of 183 candidate compounds, and "
     "we say directly that such a reading is available from a quick look at a "
     "candidate table but is not what the method does.",

     "We have adopted this reframing as the paper's stated output rather than "
     "a caveat added to it. The abstract now says the framework emits "
     "family-scope envelopes with an explicit refusal decision, and that "
     "within a family the envelope is one curve shared by all member "
     "candidates; Section III.E demonstrates it with the counts above, "
     "Assumption 4 of Section III.F states it as a bound on inferential scope, "
     "and Figure 5's caption repeats it. We have removed the phrasing that "
     "could be read as a ranking of 183 candidates."),

    (RESP,
     "Both points are now stated as limitations rather than left implicit. "
     "Section II.B records that upper critical fields in anisotropic "
     "superconductors are orientation-dependent, that for Fe(Te,Se) the "
     "reported values differ by more than a factor of two between the two "
     "principal orientations, and that orientation is captured as free text "
     "for 26 records but is not propagated into the fits while several of the "
     "reference anchors are orientation resolved. The anchors and the "
     "measurements are therefore not guaranteed to describe the same field "
     "configuration, and Section III.F repeats this among the field-axis "
     "caveats. On current direction we have to concede rather than answer: the "
     "extraction does not record the current direction relative to the crystal "
     "axes, so we cannot condition on it, and for the anisotropic families "
     "that is a real limitation of the dataset rather than of the model.",

     "Both points are now stated as limitations rather than left implicit. "
     "Section II.B records that upper critical fields in anisotropic "
     "superconductors are orientation-dependent, that for Fe(Te,Se) the "
     "reported values differ by more than a factor of two between the two "
     "principal orientations, and that orientation is captured as free text "
     "for 26 records but not propagated into the fits while several reference "
     "anchors are orientation resolved, so anchors and measurements are not "
     "guaranteed to describe the same field configuration. On current "
     "direction we concede rather than answer: the extraction does not record "
     "it relative to the crystal axes, so we cannot condition on it, and for "
     "the anisotropic families that is a limitation of the dataset rather than "
     "of the model."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: compact_letter_stage6.py IN_DIR OUT_DIR")
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
                  % (len(find.split()), len(repl.split()), find[:52]))
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
