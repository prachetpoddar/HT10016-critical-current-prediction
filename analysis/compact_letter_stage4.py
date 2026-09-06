"""
compact_letter_stage4.py

Third batch of the letter compaction, B7. Nine answers, cut to the concern, the
test, the change and the claim that survives.

Usage:
    python3 analysis/compact_letter_stage4.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final44.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final44.docx"
RESP = "RESPONSE_TO_REFEREES_final44.docx"
OUT = {MAIN: "HT10016_revised_final45.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final45.docx",
       RESP: "RESPONSE_TO_REFEREES_final45.docx"}

EDITS = [
    # ---- the deposited examples -----------------------------------------
    (RESP,
     "Table S4 gives curve-level anchor records, one row per physical sample "
     "per paper, including five bulk specimens of the same compound from one "
     "paper that differ only in processing atmosphere and span 0.26 dex. Table "
     "S5 gives fitted field-axis exponents alongside both critical-field "
     "values, the resolved one used in the fit and the literature "
     "zero-temperature one, with the provenance string for each. Table S6 "
     "gives candidate dispatch rows, including refused rows carrying their "
     "reason code and no value. We selected these rows to be useful rather "
     "than favourable: Table S5 includes the fits whose resolved scale sits "
     "far below the literature value and whose exponents run against the "
     "numerical bound, since those are the fits that motivate the "
     "qualification in Sec. III.F, and they should be visible in the paper "
     "rather than only in the deposit.",

     "Table S4 gives curve-level anchor records, one row per physical sample "
     "per paper, including five bulk specimens of one compound from one paper "
     "that differ only in processing atmosphere and span 0.26 dex. Table S5 "
     "gives fitted field-axis exponents beside both critical-field values, the "
     "resolved one used in the fit and the literature zero-temperature one, "
     "with the provenance of each. Table S6 gives candidate dispatch rows, "
     "including refused rows carrying their reason code and no value. We "
     "selected the rows to be useful rather than favourable: Table S5 includes "
     "the fits whose resolved scale sits far below the literature value and "
     "whose exponents run against the numerical bound, which are the fits that "
     "motivate the qualification in Sec. III.F."),

    # ---- the WHH answer ---------------------------------------------------
    (RESP,
     "Table II gives the holdout comparison that motivated the choice, in "
     "which the alternative carrying an explicit temperature-dependent "
     "critical field reached 0.352 dex against 0.260 dex for the adopted form, "
     "and we now report that comparison as an empirical trade rather than a "
     "physical justification. For completeness we should note that we motivate "
     "the expression from the reduced-scale logic of the Kramer and "
     "pinning-force descriptions rather than from Ginzburg-Landau theory, "
     "which Section II.C now states with those forms given as Eq. (3). The "
     "referee’s objection holds either way, since a reduced-distance power law "
     "is an expansion near the critical scale whatever motivates it, and we do "
     "not read the fitted exponent as a pinning-mechanism exponent.",

     "Table II gives the holdout comparison that motivated the choice, in "
     "which the alternative carrying an explicit temperature-dependent "
     "critical field reached 0.352 dex against 0.260 dex for the adopted form, "
     "reported now as an empirical trade rather than a physical justification. "
     "We motivate the expression from the reduced-scale logic of the Kramer "
     "and pinning-force descriptions rather than from Ginzburg-Landau theory, "
     "which Section II.C states with those forms as Eq. (3). The referee's "
     "objection holds either way, since a reduced-distance power law is an "
     "expansion near the critical scale whatever motivates it, and we do not "
     "read the fitted exponent as a pinning-mechanism exponent."),

    # ---- the applicability window -----------------------------------------
    (RESP,
     "A per-point gate on each half of the window removed 1054 targets below "
     "the reduced-field bound and 93 at or above the reduced-temperature "
     "bound, leaving 163 emitted targets over 84 compounds, all at a reduced "
     "field of 0.3226. We should be exact about that bound. Eq. (1) admits a "
     "curve to the fit on the width of its measured field interval, not on "
     "where a single point sits, so the two are not the same test; we apply "
     "the stricter reading to what we emit and say so. Assumption 1 now states "
     "both plainly, and Section III.E carries the second as a labelled "
     "limitation ahead of any dispatched value rather than after it.",

     "A per-point gate on each half of the window removed 1054 targets below "
     "the reduced-field bound and 93 at or above the reduced-temperature "
     "bound, leaving 163 emitted targets over 84 compounds, all at a reduced "
     "field of 0.3226. Eq. (1) admits a curve to the fit on the width of its "
     "measured field interval rather than on where a single point sits, so the "
     "two are not the same test; we apply the stricter reading to what we emit "
     "and say so. Assumption 1 states both, and Section III.E carries the "
     "second as a labelled limitation ahead of any dispatched value."),

    # ---- Figure 5 redrawn ---------------------------------------------------
    (RESP,
     "We have adopted the suggestion. Figure 5 is redrawn against reduced "
     "field over the window across which the exponent is validated, rather "
     "than against absolute field to 10 T, where the reduced field reaches "
     "only about 0.2. Redrawing it changed a claim. The three fields at which "
     "the dispatch grid is evaluated all fall in the low-reduced-field corner, "
     "and plotted across the validated range the envelopes are not parallel: "
     "the iron chalcogenide and iron pnictide curves cross at a reduced field "
     "of 0.58, above which the 122-type envelope is the higher of the two, by "
     "0.69 dex at a reduced field of 0.9. Section III.E previously said the "
     "family ordering was unchanged at every evaluated field. That remains "
     "true of the three evaluated fields, and the text now says so in those "
     "terms and reports the crossing alongside it. The screening claim is now "
     "limited to low reduced field. The crossing follows from the fitted field "
     "exponents and the critical-field anchors, the two quantities Section "
     "III.F qualifies, so we report it to bound the screening claim and not as "
     "a prediction that the 122-type family overtakes the 11-type in high "
     "field. We would not have seen this without the referee's suggestion.",

     "We have adopted the suggestion, and it changed a claim. Figure 5 is "
     "redrawn against reduced field over the window across which the exponent "
     "is validated, rather than against absolute field to 10 T where the "
     "reduced field reaches only about 0.2. The three evaluated fields all "
     "fall in the low-reduced-field corner, and across the validated range the "
     "envelopes are not parallel: the iron chalcogenide and 122-type curves "
     "cross at a reduced field of 0.58, above which the 122-type envelope is "
     "higher, by 0.69 dex at 0.9. Section III.E previously said the family "
     "ordering was unchanged at every evaluated field; that remains true of "
     "the three evaluated fields, and the text now says so in those terms and "
     "reports the crossing beside it. The screening claim is limited to low "
     "reduced field. Since the crossing follows from the fitted field "
     "exponents and the critical-field anchors, the two quantities Section "
     "III.F qualifies, we report it to bound that claim and not as a "
     "prediction that the 122-type family overtakes the 11-type in high field. "
     "We would not have seen it without the referee's suggestion."),

    # ---- the interval width -------------------------------------------------
    (RESP,
     "On precision, we have adopted the referee's correction and no longer "
     "carry a third digit. The width itself has changed. The 0.388 dex the "
     "referee read was the median over the predictions emitted before this "
     "revision's reduced-field gate; over the 163 predictions that survive our "
     "refusal gates the median full width is 0.61 dex, a factor of about 4.1, "
     "and 0.60 dex at the 4.2 K grid point. We should also say what that width "
     "is made of. On the three records carrying an exact critical-field anchor "
     "it is 0.398 dex; on the 83 carrying a parent anchor it is 0.602. The "
     "difference is a deterministic plus or minus 20 percent perturbation "
     "envelope on the parent anchor rather than bootstrap spread, so about a "
     "third of the quoted width is not sampling uncertainty. At the upper "
     "perturbation that envelope evaluates the model at a reduced field of "
     "0.269, below the 0.3 applicability bound this revision introduced, which "
     "we flag as a defect in the envelope rather than defend. Fitted errors "
     "and exponents are still given to three figures where they are compared "
     "across families, since rounding to two would collapse distinctions the "
     "applicability table turns on, and we have removed the third digit "
     "wherever it carried no comparison. We have also adopted the suggested "
     "gloss, giving the width as a factor in the critical current rather than "
     "only in dex: it is a factor of about 4.1, and Table S2 carries the same "
     "conversion for dex generally.",

     "On precision we have adopted the referee's correction and no longer "
     "carry a third digit where it carried no comparison; it is kept where "
     "errors are compared across families, since rounding to two would "
     "collapse distinctions the applicability table turns on. The width itself "
     "has changed. The 0.388 dex the referee read was the median before this "
     "revision's reduced-field gate; over the 163 surviving predictions it is "
     "0.61 dex, a factor of about 4.1, and 0.60 dex at the 4.2 K grid point. "
     "We should say what that width is made of. On the three records carrying "
     "an exact critical-field anchor it is 0.398 dex and on the 83 carrying a "
     "parent anchor 0.602, the difference being a deterministic plus or minus "
     "20 percent envelope on the parent anchor rather than bootstrap spread, "
     "so about a third of the quoted width is not sampling uncertainty. At the "
     "upper perturbation that envelope evaluates the model at a reduced field "
     "of 0.269, below the 0.3 bound this revision introduced, which we flag as "
     "a defect in the envelope rather than defend. We have also adopted the "
     "suggested gloss, giving the width as a factor in the critical current: "
     "about 4.1, with Table S2 carrying the conversion generally."),

    # ---- Table I ------------------------------------------------------------
    (RESP,
     "We accept the objection and have separated the screening corpus from the "
     "evidence base for any fitted quantity. The counts for contributing "
     "papers, compounds and extracted points are lower than in the previous "
     "revision because eleven papers were withdrawn and their provenance rows "
     "had not been removed with them; the reasons are set out below. The "
     "figure of 50 now appears first in the main text rather than in the "
     "Supplemental Material, and the abstract leads with the smaller numbers "
     "rather than with 934. The referee is also right that the figure and the "
     "tables appear to disagree, and we should have labelled the difference. "
     "The markers in Figure 3 are per physical sample, one per source paper "
     "and specimen with multiple isotherms of the same specimen averaged into "
     "a single record, while the tables count per-curve fits, so the two are "
     "different objects. The caption now gives both numbers, the 56 of the 96 "
     "anchors falling in the three panels shown and the 37 markers they "
     "collapse to, and we accept that the panels are overplotted enough that "
     "counting the markers by eye could not have given the right figure.",

     "We accept the objection and have separated the screening corpus from the "
     "evidence base for any fitted quantity. The counts for contributing "
     "papers, compounds and extracted points are lower than in the previous "
     "revision because eleven papers were withdrawn and their provenance rows "
     "had not been removed with them. The figure of 50 now appears first in "
     "the main text, and the abstract leads with the smaller numbers rather "
     "than with 934. The referee is also right that the figure and the tables "
     "appear to disagree, and we should have labelled the difference: the "
     "markers in Figure 3 are per physical sample, with multiple isotherms of "
     "one specimen averaged into a single record, while the tables count "
     "per-curve fits. The caption now gives both the anchors falling in the "
     "three panels shown and the markers they collapse to."),

    # ---- where the conditioning claim rests ---------------------------------
    (RESP,
     "The conditioning claim no longer rests on this ratio at all, and we have "
     "to be careful about what we move it onto. An earlier version of this "
     "reply rested it on the variance-decomposition diagnostic. That will not "
     "do, for the reason conceded above: sample form is very nearly a "
     "relabelling of source paper, so under the only null that respects that "
     "structure the iron chalcogenide cell cannot reach a probability below "
     "0.25, the 122-type cell below 0.10, and the MgB2-class cell returns 1 "
     "whatever its separation. We also said there that the 96 per-paper anchor "
     "groups behind it were unchanged by the magnetic-field unit repair, which "
     "was true of that repair and has since been overtaken: 26 of those 96 "
     "rows held values contradicting their source figures and are withdrawn, "
     "and 4 more carried a scale error and are corrected. The claim rests on "
     "the temperature axis, and the evidence is the permutation test reported "
     "below: with source papers as the unit and the substructure label "
     "shuffled between them, the family accounts for a rising fraction of the "
     "between-paper variance in the temperature exponent as the anchors are "
     "corrected, while on the field axis it accounts for essentially none. "
     "Neither the ratio the referee questioned nor the sample-form diagnostic "
     "carries the claim. We had also described it as the one result that "
     "improved under every correction; the audit section below withdraws that "
     "description and gives the full history. It is also why Table III records "
     "the field axis as not validated at family level and reports no verdict "
     "for it.",

     "The conditioning claim no longer rests on this ratio at all, and it "
     "cannot rest on the variance-decomposition diagnostic either, for the "
     "reason conceded above: sample form is very nearly a relabelling of "
     "source paper, so under the only null that respects that structure the "
     "iron chalcogenide cell cannot reach a probability below 0.25, the "
     "122-type cell below 0.10, and the MgB2-class cell returns 1 whatever its "
     "separation. The claim rests on the temperature axis, and the evidence is "
     "the permutation test reported below: with source papers as the unit and "
     "the substructure label shuffled between them, the family accounts for a "
     "rising fraction of the between-paper variance in the temperature "
     "exponent as the anchors are corrected, while on the field axis it "
     "accounts for essentially none. That is also why Table III records the "
     "field axis as not validated at family level and reports no verdict for "
     "it. We had described the temperature result as the one that improved "
     "under every correction; the section below withdraws that description and "
     "gives the full history."),

    # ---- the temperature-axis separation ------------------------------------
    (RESP,
     "We reported that earlier as a result that strengthened under every "
     "correction, and we withdraw that description, because the full history "
     "does not support it and a referee reading the deposit would find so. "
     "Three things belong beside the number. Before the eleven paper "
     "withdrawals there is no separation at all: the fraction is 0.107 with a "
     "probability of 0.355, and our own note on those withdrawals records that "
     "the screen which selected them is not independent of the exponent and "
     "acted in opposite directions in different families, so most of the rise "
     "cannot be read as evidence. At the step that removed two papers whose "
     "extractions could not be reproduced, the fraction rose while the "
     "probability rose with it, from 0.012 to 0.016, so the two halves of the "
     "result did not move together. And the exponents do not reproduce from "
     "their own figures: of the fourteen we could score against a pixel trace, "
     "none does, at a median ratio of 0.42. On the exponents rebuilt from "
     "those traces, deposited with the paper, the separation survives at 0.359 "
     "with a probability of 0.037 while the applicability result does not. "
     "What we can defend is narrower than what we first wrote and it is tested "
     "harder.",

     "We withdraw the description of this as a result that strengthened under "
     "every correction, because the full history does not support it. Three "
     "things belong beside the number. Before the eleven paper withdrawals "
     "there is no separation at all, at 0.107 with a probability of 0.355, and "
     "our own note on those withdrawals records that the screen which selected "
     "them is not independent of the exponent and acted in opposite directions "
     "in different families, so most of the rise cannot be read as evidence. "
     "At the step that removed two papers whose extractions could not be "
     "reproduced, the fraction rose while the probability rose with it, from "
     "0.012 to 0.016. And the exponents do not reproduce from their own "
     "figures: of the fourteen we could score against a pixel trace none does, "
     "at a median ratio of 0.42, though on the exponents rebuilt from those "
     "traces the separation survives at 0.359 with a probability of 0.037 "
     "while the applicability result does not. What we can defend is narrower "
     "than what we first wrote and is tested harder."),

    # ---- the five defects ----------------------------------------------------
    (RESP,
     "The propagated uncertainty of 0.29 dex used a temperature-exponent "
     "scatter that does not reproduce from our own deposit and predates the "
     "anchor repair; on the repaired exponent it is 0.27 dex, and the "
     "accompanying statement that a correlation between the terms would make "
     "it a lower bound is wrong for this functional form, so we claim no "
     "bound. Table II's holdout margin does not separate Form 3 from Form 2 "
     "once the three forms are scored on identical rows and the same "
     "compounds, so Sec. II.C adopts Form 3 for the separability the rest of "
     "the paper requires and reports the comparison as it falls. And the "
     "per-family parameters behind Figure 5 could not be regenerated from the "
     "deposit at all, because the module producing them fitted them to the "
     "predictor's own output; they are now the family median exponents over "
     "the fitted cohorts, and the figure moves with them.",

     "The propagated uncertainty of 0.29 dex used a temperature-exponent "
     "scatter that does not reproduce from our own deposit; on the repaired "
     "exponent it is 0.27 dex, and the accompanying claim that a correlation "
     "between the terms would make it a lower bound is wrong for this "
     "functional form, so we claim no bound. Table II's holdout margin does "
     "not separate Form 3 from Form 2 once the three forms are scored on "
     "identical rows and compounds, so Sec. II.C adopts Form 3 for the "
     "separability the rest of the paper requires and reports the comparison "
     "as it falls. And the per-family parameters behind Figure 5 could not be "
     "regenerated at all, because the module producing them fitted them to the "
     "predictor's own output; they are now family median exponents over the "
     "fitted cohorts, and the figure moves with them."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: compact_letter_stage4.py IN_DIR OUT_DIR")
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
