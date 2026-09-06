"""
compact_letter_stage3.py

Second batch of the letter compaction, B7, and one correction the compaction
found.

The correction first. Two answers in the letter gave incompatible floors for
the clustered null. The MgB2 answer said the MgB2-class cell admits three
labellings and can never return a probability below 0.33; the conditioning
answer, four pages later, said it returns 1 whatever its separation. The second
is right and is what Sec. III.A of the manuscript now states: under a null that
holds each form's sample count at its observed value, that family admits one
labelling. The first is corrected here.

The compaction cuts each answer to the concern, the test, the change and the
claim that survives, and removes what the letter states elsewhere. Fifteen
paragraphs in this batch.

Usage:
    python3 analysis/compact_letter_stage3.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final43.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final43.docx"
RESP = "RESPONSE_TO_REFEREES_final43.docx"
OUT = {MAIN: "HT10016_revised_final44.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final44.docx",
       RESP: "RESPONSE_TO_REFEREES_final44.docx"}

EDITS = [
    # ---- the MgB2 answer: the wrong floor, and the length ---------------
    (RESP,
     "Section III.A states that this is consistent with the two-band character "
     "of MgB2 and its documented sensitivity to production route, both acting "
     "through variables a sample-form label does not capture. We concede the "
     "test itself, separately from the result. Sample form is very nearly a "
     "relabelling of source paper in this corpus: one of the 29 contributing "
     "papers carried more than one sample form before the repair and none of "
     "the 20 does after it. Under a null that shuffles the form label between "
     "papers, the only null that respects that structure, the MgB2-class cell "
     "admits three distinct labellings and can never return a p below 0.33 "
     "however clean the separation, and the other two families admit four and "
     "ten. The diagnostic therefore cannot establish the regime distinction it "
     "is used to draw, and Section III.A now reports the regime labels as the "
     "rule the predictor follows rather than as a tested finding. What would "
     "settle it is source papers reporting several sample forms of one "
     "compound, which our corpus does not contain; we name that as the "
     "specific data requirement. Separately, and this is our error rather than "
     "a limit of the literature: 26 of the 96 anchor rows behind this "
     "diagnostic held values contradicting their source figures and are "
     "withdrawn, and 15 more carried a scale error on the current or field "
     "axis and are corrected. The audit that found them is deposited with the "
     "analysis.",

     "Section III.A reads that as consistent with the two-band character of "
     "MgB2 and its documented sensitivity to production route, both acting "
     "through variables a sample-form label does not capture. We concede the "
     "test itself, separately from the result. Sample form is very nearly a "
     "relabelling of source paper here: one of the 29 contributing papers "
     "carried more than one sample form before the repair and none of the 20 "
     "does after it. Under a null that shuffles the form label between papers "
     "and holds each form's sample count fixed, which is the only null that "
     "respects that structure, the MgB2-class cell admits a single labelling "
     "and returns a probability of 1 however clean the separation, while the "
     "iron chalcogenide and 122-type cells admit four labellings and ten, with "
     "floors of 0.25 and 0.10. The diagnostic cannot establish the regime "
     "distinction it is used to draw, and Section III.A now reports the regime "
     "labels as the rule the predictor follows rather than as a tested "
     "finding. What would settle it is source papers reporting several sample "
     "forms of one compound, which our corpus does not contain. Separately, "
     "and this is our error rather than a limit of the literature: 26 of the "
     "96 anchor rows behind this diagnostic held values contradicting their "
     "source figures and are withdrawn, and 15 more carried a scale error and "
     "are corrected."),

    # ---- the narrow spread ----------------------------------------------
    (RESP,
     "Section III.E and an earlier version of this letter both said one grid "
     "point; the assertion behind that wording checks that a single field is "
     "emitted, which is true, and we read it as a single grid point, which it "
     "is not. At 4.2 K and 5 T the 86 records span 0.0085 dex, 1.4% of the "
     "0.60 dex bootstrap interval there; at 20 K and 5 T the 77 records span "
     "0.254 dex. At 20 K the explanation we gave holds: the conditioning fixes "
     "every parameter of the expression, the compound-specific inputs are the "
     "critical-field anchor and the transition temperature, and the prediction "
     "regresses on the temperature term with a slope of 1.21 and an R squared "
     "of 0.996, recovering the family exponent of 1.14. At 4.2 K it cannot "
     "enter, and this is the part we had not seen. The model is anchored at a "
     "reference point whose temperature is 4.2 K at a reference point and its "
     "temperature term is the difference between log10(1 - T/Tc) and the same "
     "quantity at that reference, whose temperature is 4.2 K. That difference "
     "is therefore identically zero for every candidate whatever its "
     "transition temperature, and across 59 distinct anchors from 8.9 to 41.4 "
     "K the largest value the term takes is exactly zero. Every dispatched "
     "record also carries the same 15.5 T parent anchor, so the field term is "
     "one shared number. The prediction there is a single family-level "
     "constant, 4.980 in log10 Jc, the family's critical-current anchor of "
     "5.324 displaced by 0.344 dex. The referee's reading is right and the "
     "figure supports it more strongly than we claimed. The 0.0085 dex is not "
     "a spread between compounds: all 86 records have identical model inputs "
     "and differ only in their draw from one bootstrap stream over a pool of "
     "18 fits. Resampling that pool 84 times independently returns a span of "
     "0.0092 dex with a standard deviation of 0.0016, of which the observed "
     "value is an ordinary draw. It is evidence that the predictor is constant "
     "at that point and evidence of nothing else, and we no longer offer it as "
     "a measured quantity. A compound-resolved spread would need a dispatch "
     "grid that does not evaluate at the anchor's own reference temperature, "
     "which the present grid does.",

     "The wording that said one grid point came from an assertion that checks "
     "a single field is emitted, which is true. At 4.2 K and 5 T the 86 "
     "records span 0.0085 dex, 1.4% of the 0.60 dex bootstrap interval there; "
     "at 20 K and 5 T the 77 records span 0.254 dex. At 20 K our explanation "
     "holds: the conditioning fixes every parameter of the expression, the "
     "compound-specific inputs are the critical-field anchor and the "
     "transition temperature, and the prediction regresses on the temperature "
     "term with a slope of 1.21 and an R squared of 0.996, recovering the "
     "family exponent of 1.14. At 4.2 K the transition temperature cannot "
     "enter at all, and this is the part we had not seen. The model is "
     "anchored at a reference point whose temperature is 4.2 K, so the "
     "temperature term is the difference of a quantity from itself and is "
     "identically zero for every candidate; across 59 distinct anchors from "
     "8.9 to 41.4 K the largest value it takes is exactly zero. Every "
     "dispatched record also carries the same 15.5 T parent anchor, so the "
     "field term is one shared number, and the prediction there is a single "
     "family-level constant of 4.980 in log10 Jc, the family's "
     "critical-current anchor of 5.324 displaced by 0.344 dex. The referee's "
     "reading is right and the figure supports it more strongly than we "
     "claimed. The 0.0085 dex is not a spread between compounds: all 86 "
     "records have identical model inputs and differ only in their draw from "
     "one bootstrap stream over a pool of 18 fits, and resampling that pool 84 "
     "times independently returns 0.0092 dex with a standard deviation of "
     "0.0016. It is evidence that the predictor is constant at that point and "
     "evidence of nothing else, and we no longer offer it as a measured "
     "quantity. A compound-resolved spread would need a grid that does not "
     "evaluate at the anchor's own reference temperature."),

    # ---- the 23-fold ------------------------------------------------------
    (RESP,
     "The cohorts were mismatched too: the larger error came from the nine "
     "substructure families of an earlier version of this analysis and the "
     "smaller from the five carrying populated sample-form cells. Matching "
     "them removes that defect but not a worse one we found on re-examination: "
     "in both versions the predictor for a held-out family was built from a "
     "pool containing that family's own fits, so neither was a statement about "
     "generalization. Under leave-one-substructure-out we can report no fold "
     "improvement at all, and give the errors instead.",

     "The cohorts were mismatched too, the larger error coming from nine "
     "substructure families and the smaller from the five carrying populated "
     "sample-form cells. Matching them removes that defect but not a worse one: "
     "in both, the predictor for a held-out family was built from a pool "
     "containing that family's own fits, so neither was a statement about "
     "generalization. Under leave-one-substructure-out we report no fold "
     "improvement at all, and give the errors instead."),

    (RESP,
     "The referee is further correct that the cuprates dominate the residual: "
     "Section 1 of the Supplemental Material reports 59% of the residual mass "
     "against 43% of the cohort, and three cuprate substructures reach the "
     "imposed regression ceiling because their measured field windows lie far "
     "below the critical field. Every exponent entering the ratio inherits the "
     "field-scale qualification described below. The same test found the "
     "mismatched-cohort error a second time: the 26.8% anchor-count reduction "
     "in Section III.B compared a three-compound one-anchor value against a "
     "four-compound three-anchor one, and the matched pair, 1.267 to 0.694, "
     "gives 45.2%, which is the figure we now carry.",

     "The referee is further correct that the cuprates dominate the residual: "
     "Supplemental Sec. 1 reports 59% of the residual mass against 43% of the "
     "cohort, three cuprate substructures reaching the regression ceiling "
     "because their measured field windows lie far below the critical field. "
     "The same test found the mismatched-cohort error a second time: the 26.8% "
     "anchor-count reduction in Sec. III.B compared a three-compound "
     "one-anchor value against a four-compound three-anchor one, and the "
     "matched pair, 1.267 to 0.694, gives 45.2%, which we now carry."),

    # ---- the field-exponent drift ----------------------------------------
    (RESP,
     "Across the series holding one scale over three or more temperatures the "
     "median absolute rank correlation between exponent and temperature is "
     "0.80. On the repaired cohort that is 13 series, and 6 sampled at four or "
     "more temperatures, both at 0.80; as first deposited it was 18 series at "
     "0.70, so the effect is unchanged in direction and slightly larger. A "
     "series is one source paper, one sample and one held scale, which is what "
     "makes the scale held by construction. We withdraw the worked example we "
     "gave. Its source, Physica C 469 (2009) 590, prints its field axis in "
     "kilo-oersted and the extraction recorded the bare numbers as tesla; "
     "corrected, its measured span falls to 0.053 of the assigned scale and "
     "all eight of its fits fail the 0.3 applicability bound. The exponent was "
     "also not monotone over the window we quoted, falling from 1.25 at 2 K to "
     "0.82 at 10 K before rising to 12.14 at 35 K, so the sentence would have "
     "needed correcting whatever became of the unit. The clearest surviving "
     "case is",

     "Across the series holding one scale over three or more temperatures the "
     "median absolute rank correlation between exponent and temperature is "
     "0.80, on 13 series and on the 6 sampled at four or more temperatures; as "
     "first deposited it was 0.70 on 18, so the effect is unchanged in "
     "direction and slightly larger. A series is one source paper, one sample "
     "and one held scale, which is what makes the scale held by construction. "
     "We withdraw the worked example we gave: its source prints its field axis "
     "in kilo-oersted and the extraction recorded the bare numbers as tesla, "
     "so its measured span is 0.053 of the assigned scale and all eight of its "
     "fits fail the 0.3 applicability bound, and its exponent was not monotone "
     "over the window we quoted in any case. The clearest surviving case is"),

    # ---- the correction list ---------------------------------------------
    (RESP,
     "Several values have been corrected as a result. The MgB2-class compound "
     "leave-one-out error is 0.753 rather than 0.772, and the universal "
     "scaling reduction is 13.0% on the standard-deviation scale rather than "
     "14.1%. The Stage 3 error is 0.816 rather than 0.84 and is no longer "
     "called a leave-one-substructure-out result. The external anchor-count "
     "errors are labelled in dex rather than as dimensionless exponent errors, "
     "the same unit repair described above applied where we had missed it. The "
     "propagated uncertainty is 0.27 dex rather than 0.29. The fifteen MgB2 "
     "temperature fits are described as the deposited file has them: six rest "
     "on three points rather than one, and the fit we reported with a "
     "root-mean-square residual of 6.3 has one of 6.3 times ten to the minus "
     "fourteen. The 233 evaluated records and the 212 retained after the "
     "calibration screen are record counts covering 183 distinct compounds, in "
     "which one compound may appear more than once. The Supplemental Material "
     "now carries the disposition of all 94 field-axis fits individually, "
     "which an earlier version of this letter said it did.",

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
     "said it did."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: compact_letter_stage3.py IN_DIR OUT_DIR")
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
            print("   %-4d -> %-4d words   %s"
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
