"""
apply_hossain_writing_edits.py

Hossain's writing items B1, B3 and B6, and two things his exact wording shows
were only partly done.

B3, the abstract as a four-step argument. Problem, method, robust findings,
general implication, in that order. It led with the ill-defined regression
target already; what it did not do was separate the three findings that survive
the audit from the diagnostics that set the predictor's rule. Those are now
distinct, and the deposited-anchor ratios come out, since a comparison between
two cohorts of a diagnostic the paper says cannot be established is not an
abstract-level result. The repaired ratios stay, with the confounding
qualification A2 asks to keep, and the abstract falls from 617 words to about
470.

B1, predictive scope as the central idea. The question the paper answers has
two halves and only one was stated: which measurements may be compared, and
whether the scale that normalizes them was measured on the same specimen. The
second half is what the critical-field provenance audit of Sec. III.F is about,
and stating it in Sec. I makes that audit part of the result rather than an
apology for it. Sec. III.F now opens by pointing back to it.

B6, transitions that carry the argument. Sections III.B and III.C already had
them. III.A, III.C's rebuild, III.D, III.E and III.F did not, and now do, each
saying why the analysis that follows is necessary rather than only what it is.

Two corrections from his exact wording. A6 asks for the source-paper holdout to
be stated with its scope; the letter still headed it "Nothing generalizes across
source papers", which is broader than eight compounds support. And A3's done-when
is satisfied, which was checked rather than assumed: the manuscript states that
no dispatched field-axis output is offered as a validated prediction, in
Sec. III.E and again in its limitation.

Usage:
    python3 analysis/apply_hossain_writing_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final49.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final49.docx"
RESP = "RESPONSE_TO_REFEREES_final49.docx"
OUT = {MAIN: "HT10016_revised_final50.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final50.docx",
       RESP: "RESPONSE_TO_REFEREES_final50.docx"}

# ---------------------------------------------------------------- B3
ABSTRACT_OLD = (
    "We introduce a substructure- and sample-form-conditioned framework built "
    "from 50 papers that contribute fitted critical-current curves, covering "
    "35 compound labels, which reduce to 27 distinct composition keys, and "
    "3303 extracted data points, drawn from a screened retrieval corpus of 934 "
    "articles, and which retains the experimental context of each measured "
    "curve. A variance-decomposition diagnostic tests, family by family, "
    "whether sample form is a required conditioning variable, and assigns two "
    "distinct regimes across the studied families: on the repaired anchor "
    "cohort sample form explains 81% of the within-family variance in the "
    "critical-current anchor for iron chalcogenide 11-type materials, on five "
    "physical samples, 37% for iron pnictide 122-type on five, and 4% for "
    "MgB2-class on 13, against 37%, 49% and 12% on the anchors as deposited. "
    "These regimes set the conditioning rule the predictor follows. A holdout "
    "that withholds every measurement of a source paper puts a number on the "
    "heterogeneity the framework is built for: no candidate functional form "
    "reaches a median error of 0.90 dex on an unseen paper, a factor of eight "
    "in critical current, against 0.32 to 0.39 dex when the withheld "
    "measurements come from within a compound. Because sample form is very "
    "nearly a relabelling of source paper in this corpus, the separation "
    "between them is not established at any useful significance: the exact "
    "permutation probability cannot fall below 0.25 for the strongest of the "
    "three families and is identically 1 for the weakest. We state the "
    "measurement that would establish it. Universal reduced-variable scaling "
    "does not organize this corpus: normalizing temperature and field by their "
    "critical values reduces the within-bin standard deviation of log10 Jc by "
    "only 13.0%, a variance-scale reduction of 24.3%, the result is unchanged "
    "on the standard-deviation scale under a 35% perturbation of the estimated "
    "critical fields, and on a point-level rebuild of the same test the "
    "reduced coordinates carry no more structure than the same grid rotated to "
    "a random angle. The framework then emits family-scope critical-current "
    "envelopes with bootstrap uncertainty for three substructure families, "
    "together with an explicit refusal decision for every candidate and "
    "prediction target. We state what validation stands behind that scope, "
    "since it is not uniform. Three families clear the compound leave-one-out "
    "threshold on the temperature axis, and no family-level verdict is "
    "reported on the field axis, where the substructure label does not "
    "separate the exponent at all. The MgB2 class, which is the only family "
    "that emits at the current gate settings, is one of the three that "
    "dispatch and not one of the three that clear: it carries no fits in the "
    "temperature-axis cohort and so is not assessable on the axis where the "
    "test can be run. Within a family the emitted envelope is a single curve "
    "shared by all member candidates: the output is a scope decision and a "
    "family envelope, not a per-compound ranking, and we show that this is a "
    "structural property of the predictor rather than a conservative reading "
    "of a marginal signal. The same principle, establishing which measurements "
    "may be compared before comparing them, applies to any AI-for-physics "
    "problem in which the measured property depends strongly on preparation "
    "route, sample geometry, or measurement protocol."
)

ABSTRACT_NEW = (
    "The prior question is therefore not how to predict but which measurements "
    "may be compared, and whether the scale used to normalize them was "
    "measured on the same specimen. We introduce a substructure- and "
    "sample-form-conditioned framework built from 50 source papers that "
    "contribute fitted critical-current curves, covering 35 compound labels "
    "and 3303 extracted data points drawn from a screened retrieval corpus of "
    "934 articles. Each fitted curve keeps the experimental context of its "
    "measurement, is anchored to a transition temperature and an upper "
    "critical field whose provenance is recorded, and contributes its "
    "exponents only within a scope the data support; every prediction target "
    "then passes explicit refusal gates or is refused with a reason. Three "
    "findings survive. Universal reduced-variable scaling does not organize "
    "this corpus: normalizing temperature and field by their critical values "
    "reduces the within-bin standard deviation of log10 Jc by only 13.0%, a "
    "variance-scale reduction of 24.3%, the result is unchanged under a 35% "
    "perturbation of the estimated critical fields, and on a point-level "
    "rebuild the reduced coordinates carry no more structure than the same "
    "grid rotated to a random angle. Substructure family does separate the "
    "temperature exponent, accounting for 0.52 of the between-paper variance "
    "at a permutation probability of 0.007, and it survives on exponents "
    "rebuilt independently from the source figures, at 0.36 and 0.037. And "
    "generalization across unseen source papers is poor for all three tested "
    "parameterizations on the eight compounds drawing on more than one source: "
    "no form reaches a median error of 0.90 dex on an unseen paper, a factor "
    "of eight in critical current, against 0.32 to 0.39 dex when the withheld "
    "measurements come from within a compound. A variance-decomposition "
    "diagnostic sets the conditioning rule family by family, and on the "
    "repaired anchor cohort sample form explains 81%, 37% and 4% of the "
    "within-family variance in the critical-current anchor for the iron "
    "chalcogenide 11-type, iron pnictide 122-type and MgB2 classes; because "
    "sample form is very nearly a relabelling of source paper here, those "
    "ratios define an operational rule rather than an established sample-form "
    "effect, and we state the measurement that would establish one. The "
    "framework emits family-scope critical-current envelopes with bootstrap "
    "uncertainty together with an explicit refusal decision for every "
    "candidate and target, and carries the validation behind each: three "
    "families clear the compound leave-one-out threshold on the temperature "
    "axis, no family-level verdict is reported on the field axis, and the one "
    "family that emits under the current gates is not assessable on the axis "
    "where the test can be run. Within a family the envelope is a single curve "
    "shared by all member candidates, so the output is a scope decision rather "
    "than a per-compound ranking. Establishing which measurements may be "
    "compared, and whether the scale that normalizes them was measured on the "
    "same specimen, applies to any AI-for-physics problem in which the "
    "measured property depends strongly on preparation route, sample geometry, "
    "or measurement protocol."
)

EDITS = [
    (MAIN, ABSTRACT_OLD, ABSTRACT_NEW),

    # ---------------------------------------------------------- B1
    (MAIN,
     "Our central contribution is a variance-decomposition diagnostic that "
     "answers exactly this question.",

     "That prior question has two halves, and this paper is organized around "
     "both. Which measurements may be compared with one another, and does the "
     "scale used to normalize them belong to the specimen that was measured? "
     "The first is a question about the comparison class and the second about "
     "provenance, and a literature-derived predictor that answers neither "
     "reports a number whose meaning cannot be traced. Section III.F reports "
     "what happens when the second is put to this corpus, and that answer is "
     "part of the result rather than a caveat on it. Our central contribution "
     "is a variance-decomposition diagnostic that answers the first."),

    # ---------------------------------------------------------- B6
    (MAIN,
     "Aggregation across three scopes. Stage 1 classifies compounds by "
     "substructure and regresses the field exponent against a compositional "
     "descriptor.",

     "The first question is whether the data support conditioning at all, and "
     "at which scope, so we begin with the aggregation the predictor performs "
     "and the diagnostic that chooses between its scopes. Aggregation across "
     "three scopes. Stage 1 classifies compounds by substructure and regresses "
     "the field exponent against a compositional descriptor."),

    (MAIN,
     "Each of the 23 fully fittable compounds of the pre-withdrawal cohort is "
     "held out in turn while the remainder train the predictor,",

     "Having bounded applicability by family and by axis, we now ask whether "
     "any grouping is needed at all, by testing the alternative the literature "
     "usually assumes: that reduced variables collapse the corpus into a "
     "single law. The in-corpus ranking test comes first, because it "
     "establishes that the predictor carries rank signal before the collapse "
     "is tested against it. Each of the 23 fully fittable compounds of the "
     "pre-withdrawal cohort is held out in turn while the remainder train the "
     "predictor,"),

    (MAIN,
     "Uncertainty in the substructure aggregate is propagated in quadrature "
     "over the three fitted terms rather than taken from the spread of any one "
     "of them.",

     "Having identified the limits of family-level applicability, and having "
     "shown that no universal law replaces them, we finally test how refusal "
     "changes what the framework emits. Uncertainty in the substructure "
     "aggregate is propagated in quadrature over the three fitted terms rather "
     "than taken from the spread of any one of them."),

    (MAIN,
     "Four assumptions and one data-layer finding bound the generalizability "
     "of the framework.",

     "Every quantity above is only as well defined as the scales that "
     "normalize it, which is the second half of the question set out in "
     "Section I. Four assumptions and one data-layer finding bound the "
     "generalizability of the framework."),

    # ---------------------------------------------------------- A6 scope
    (RESP,
     "Nothing generalizes across source papers. Under a holdout that withholds "
     "every measurement of a paper, none of the three candidate functional "
     "forms reaches a median error of 0.90 dex on the eight compounds drawing "
     "on more than one source,",

     "Generalization across unseen source papers is poor for all three tested "
     "parameterizations, on the eight compounds that draw on more than one "
     "source. Under a holdout that withholds every measurement of a paper, "
     "none of the three candidate functional forms reaches a median error of "
     "0.90 dex on those compounds,"),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_hossain_writing_edits.py IN_DIR OUT_DIR")
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
                     len(repl.split()), find[:44]))
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
