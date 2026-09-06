"""
apply_conditioning_claim_edits.py

Four repairs to the manuscript, all found by rebuilding Figure 1 and all
present in the documents before it.

**1. The manuscript and the reply disagree about what carries the conditioning
claim.** Sec. III.A opens the diagnostic paragraph with "The conditioning claim
rests on this test rather than on the stage comparison above". Paragraph 38 of
the reply says resting it there will not do, because sample form is nearly a
relabelling of source paper and no family cell can reach a probability below
0.10 under the only null that respects that structure, and moves the claim onto
the temperature axis. A referee who reads the reply and then looks for that
evidence in the paper does not find it.

**2. The manuscript never reports the temperature-axis permutation test**,
although it reports the field-axis half of the same test in Sec. III.C, at
0.038 with p 0.98. The missing half is the evidence the reply points at:
matched on the seventeen papers common to both versions, the family label
accounts for 0.436 of the between-paper variance before the anchor repair and
0.524 after, with permutation probabilities of 0.016 and 0.007. Source:
audit/headline_recomputed_20260905.md and audit/headline_on_repaired_cohort.csv.

**3. "0.37 on 7" pairs a repaired ratio with a pre-repair count.**
audit/variance_decomposition_repaired.csv has n = 5 for iron_pnictide_122 on
the repaired cohort; 7 is that family's paper count on the deposited one.

**4. Table III carries two cells its own body text has moved past.** The
diagnostic row still reports the deposited 37/49/12 as the result while
Sec. III.A gives the repaired 0.81/0.37/0.04, and the conditioning row still
credits a reduction "by between one and about two-fold" while Sec. III.A says
neither predictor is distinguishable from the out-of-sample median of the
training fits.

Usage:
    python3 analysis/apply_conditioning_claim_edits.py IN_DIR OUT_DIR

Every target must match exactly once or nothing is written.
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final16.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final16.docx"
RESP = "RESPONSE_TO_REFEREES_final16.docx"
OUT = {MAIN: "HT10016_revised_final18.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final18.docx",
       RESP: "RESPONSE_TO_REFEREES_final18.docx"}

EDITS = [
    # ---- 1. what the conditioning claim rests on ----------------------
    (MAIN,
     "The variance-decomposition diagnostic. The conditioning claim rests on "
     "this test rather than on the stage comparison above, and it is computed "
     "on the critical-current anchor,",
     "The variance-decomposition diagnostic. This test is what sets the "
     "conditioning rule the predictor follows, family by family. It is not "
     "what establishes that conditioning is required: as we set out below, "
     "sample form is very nearly a relabelling of source paper in this "
     "corpus, and the claim that substructure conditioning is required rests "
     "on the temperature-axis separation reported in Sec. III.C rather than "
     "on this diagnostic or on the stage comparison above. The diagnostic is "
     "computed on the critical-current anchor,"),

    # ---- 2. the missing half of the permutation test ------------------
    (MAIN,
     "On the field axis we report no family-level verdict at all, for three "
     "reasons.",
     "On the temperature axis the substructure label separates the families "
     "and the anchor repair strengthens the separation. Taking source papers "
     "as the unit and shuffling the substructure label between them, the "
     "fraction of between-paper variance in the temperature exponent that the "
     "family label accounts for is 0.524 with a permutation p of 0.007 after "
     "the repair; matched on the seventeen papers common to both versions it "
     "was 0.436 with p of 0.016 before it. This is the one result in the "
     "paper that improved under every correction, it uses no fitted field "
     "scale, and it is what the conditioning claim rests on. On the field "
     "axis we report no family-level verdict at all, for three reasons."),

    # ---- 3. the pre-repair count beside a repaired ratio --------------
    (MAIN, "the same three are 0.81 on 5 samples, 0.37 on 7 and 0.04 on 13",
     "the same three are 0.81 on 5 samples, 0.37 on 5 and 0.04 on 13"),

    # ---- 4a. Table III, the diagnostic result cell --------------------
    (MAIN,
     "Sample form explains 37%, 49%, and 12% of within-family anchor variance "
     "for iron chalcogenide 11-type, iron pnictide 122-type, and MgB2-class "
     "respectively.",
     "On the repaired anchors sample form explains 81%, 37% and 4% of "
     "within-family anchor variance for iron chalcogenide 11-type, iron "
     "pnictide 122-type and MgB2-class respectively, against 37%, 49% and 12% "
     "on the anchors as deposited. The diagnostic sets the conditioning rule "
     "per family; it does not establish the distinction to significance, and "
     "Sec. III.A gives the clustered-null floors that prevent it from doing "
     "so."),

    # ---- 4b. Table III, the fold-reduction cell -----------------------
    (MAIN,
     "Substructure conditioning reduces field-exponent error by between one "
     "and about two-fold under leave-one-substructure-out validation, "
     "depending on the cohort, and the interquartile bound reported with "
     "Stage 3 covers the residual in four of four families once the cuprate "
     "families are removed.",
     "No fold improvement is reported. Under leave-one-substructure-out the "
     "mean absolute error in the field exponent is 12.3 without sample-form "
     "conditioning and 14.9 with it across the seven families carrying a "
     "descriptor, and 1.19 without and 0.55 with it on the fits passing "
     "physicality over the three families the conditional scope can score. "
     "Neither predictor is distinguishable from the out-of-sample median of "
     "the training fits, and removing any single family moves the comparison "
     "across unity. The interquartile bound reported with Stage 3 covers the "
     "residual in four of four families once the cuprate families are "
     "removed."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_conditioning_claim_edits.py IN_DIR OUT_DIR")
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
                         % (name, len(hits), find[:64]))
            new = replace_in_paragraph(hits[0], find, repl)
            if new is None:
                sys.exit("%s: could not place the replacement for %r"
                         % (name, find[:64]))
            doc = doc.replace(hits[0], new, 1)
            print("   %-30s %s" % (name.split("_")[0], find[:56]))
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
