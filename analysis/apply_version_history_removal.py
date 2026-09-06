"""
apply_version_history_removal.py

Takes the manuscript's version history out and leaves its limitations in,
action B5.

The manuscript carried about twenty passages whose job was to say what an
earlier draft of itself had said. They were written to be honest about
corrections, and each one is genuinely a correction, but they belong in the
response letter, which now carries every one of them, and not in a paper a
reader meets for the first time. Eighteen sentences of "an earlier version of
this section gave" turn a set of results into a change log.

The cut applied here, in every case:

  out   the reference to a previous draft, and the value that draft printed
  in    the methodological reason the current value is the one reported, the
        properties of the cohort, and every limitation

So Stage 3 no longer says a previous version gave 0.84 and called it a
leave-one-substructure-out error; it says the error has to be computed under
genuine withholding, because a median predicting a held-out family from a pool
that includes it returns zero for two of its five terms, and that under genuine
withholding it is 0.816. The reader learns the same thing about the method and
nothing about the drafting.

Two passages stay, because they are cohort comparisons rather than draft
history: Table III's as-published column beside its repaired one, and Sec. III.F's
pointer to the field-axis verdicts Sec. III.C withdraws, which Table III reports
on both cohorts.

Usage:
    python3 analysis/apply_version_history_removal.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final40.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final40.docx"
RESP = "RESPONSE_TO_REFEREES_final40.docx"
OUT = {MAIN: "HT10016_revised_final41.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final41.docx",
       RESP: "RESPONSE_TO_REFEREES_final41.docx"}

EDITS = [
    # ---- Sec. II.A, the retrieval corpus -------------------------------
    (MAIN,
     "The fitted cohort is not drawn exclusively from those two publishers, "
     "and we state this explicitly because an earlier version of this "
     "manuscript implied otherwise.",
     "The fitted cohort is not drawn exclusively from those two publishers."),

    # ---- Sec. II.B, the reference table --------------------------------
    (MAIN,
     "The reference table warrants a precise description, since an earlier "
     "version of this manuscript called it \"curated substructure reference "
     "values\" without qualification. It contains 53 entries.",
     "The reference table warrants a precise description, because its entries "
     "are not all of one kind. It contains 53 entries."),

    # ---- Sec. III, the two conventions ---------------------------------
    (MAIN,
     "An earlier version of this manuscript reported exponent errors in dex, "
     "which made a value such as 10.10 read as ten orders of magnitude in "
     "current density when it is in fact a dimensionless exponent error.",
     "The distinction carries weight at these magnitudes: a value such as "
     "10.10 is a dimensionless exponent error, not ten orders of magnitude in "
     "current density."),

    # ---- Sec. III.A, Stage 1 --------------------------------------------
    (MAIN,
     "it is not a MAGPIE feature-vector model, and we name it precisely here "
     "because that was ambiguous in the earlier presentation.",
     "it is not a MAGPIE feature-vector model."),

    (MAIN,
     "An earlier version of this section quantified it as a Spearman "
     "coefficient of 0.635 with a 95% confidence interval of [0.061, 0.948]. "
     "That figure is withdrawn: it was computed on the nine-family version of "
     "the descriptor table, two of whose families have since been withdrawn, "
     "and on the mean field exponent where this stage regresses the median. "
     "On the seven families that remain the coefficient is 0.408 on the median "
     "and 0.593 on the mean, and a bootstrap interval on either contains zero "
     "and reaches unity, because",

     "Over the seven families the descriptor table carries, the Spearman "
     "coefficient is 0.408 on the median field exponent, which is the "
     "quantity this stage regresses, and 0.593 on the mean. A bootstrap "
     "interval on either contains zero and reaches unity, because"),

    # ---- Sec. III.A, Stage 2 --------------------------------------------
    (MAIN,
     "The Stage 1 error was computed across the nine substructure families of "
     "an earlier version of this analysis and the Stage 2 error across the "
     "five families that carried populated sample-form cells, so the headline "
     "ratio of 10.10 to 0.43 compares different cohorts.",

     "A ratio of the two stage errors compares different cohorts unless they "
     "are matched, because Stage 1 scores every substructure family carrying a "
     "descriptor while Stage 2 scores only the families with populated "
     "sample-form cells."),

    (MAIN,
     "We do not report a fold improvement. An earlier version of this section "
     "gave 1.07, 2.24 and 1.83 across the three cohorts, and those are "
     "withdrawn: the sample-form-conditional scope is undefined for the MgB2 "
     "class, because once the cuprate families are removed no other family "
     "contributes a bulk or wire fit, so two of the three divided a "
     "four-family numerator by a three-family denominator, which is the "
     "mismatched-cohort defect this same paragraph identifies in the original "
     "ratio. They were also the lowest of four ways of forming the conditional "
     "prediction, and the lowest is not the same one on every cohort.",

     "We do not report a fold improvement, because no defensible one exists on "
     "this cohort. The sample-form-conditional scope is undefined for the MgB2 "
     "class: once the cuprate families are removed no other family contributes "
     "a bulk or wire fit, so a conditional numerator covering four families "
     "would be divided by a three-family denominator, which is the "
     "mismatched-cohort defect this same paragraph identifies. There are also "
     "four ways of forming the conditional prediction, and the one that gives "
     "the smallest ratio is not the same one on every cohort."),

    # ---- Sec. III.A, Stage 3 --------------------------------------------
    (MAIN,
     "An earlier version of this section gave its error as 0.84 in the field "
     "exponent and called it a leave-one-substructure-out error. It is not "
     "one. That figure comes from the same generator and the same run as the "
     "Stage 1 and Stage 2 values withdrawn above, and it carries the same "
     "defect: the median that predicts a held-out family is computed over a "
     "pool that includes that family, so two of its five terms are zero by "
     "construction. Under genuine withholding, on the cuprates-removed cohort "
     "the interquartile result below is computed on, the Stage 3 error is "
     "0.816.",

     "Its error has to be computed under genuine withholding, because a median "
     "that predicts a held-out family from a pool containing that family "
     "returns zero for two of its five terms by construction. On the "
     "cuprates-removed cohort the interquartile result below is computed on, "
     "the Stage 3 error is 0.816."),

    # ---- Sec. III.A, the band cuts --------------------------------------
    (MAIN,
     "The label is assigned by two cuts on the ratio, which we state here "
     "because earlier versions of this manuscript did not:",
     "The label is assigned by two cuts on the ratio, which we state here "
     "because the regime drives the aggregation scope:"),

    # ---- Sec. III.A, the diagnostic -------------------------------------
    (MAIN,
     " An earlier version of this section gave 0.35 for the 122-type family, "
     "which reproduces from no cohort in the deposit and is corrected here.",
     ""),

    (MAIN,
     " An earlier version of this section gave three labellings and a floor of "
     "0.33 for the MgB2-class cell, which counts the ways of splitting its "
     "three source papers into two groups without holding the wire and bulk "
     "sample counts fixed, while the four and the ten were already the "
     "size-preserving counts; the same null is now applied to all three "
     "families.",
     ""),

    # ---- Sec. III.B, the external validation ----------------------------
    (MAIN,
     "We note the unit explicitly because an earlier version of this section "
     "reported it as an error in the field exponent, and because a further "
     "comparison against an in-corpus baseline of 0.567 has been removed: that "
     "value is not derivable from the deposit and it is not on the same scale "
     "as 1.592.",

     "We note the unit explicitly because the quantity is an error in log10 Jc "
     "and not in the field exponent, and because the only in-corpus baseline "
     "available for comparison is on neither the same scale nor derivable from "
     "the deposit, so none is quoted."),

    # ---- Sec. III.C, the MgB2 temperature cohort ------------------------
    (MAIN,
     " An earlier version of this sentence described one fit resting on three "
     "points and one fitting with an rms of 6.3; the second was a "
     "transcription of 6.3 by ten to the minus fourteenth, which is a fit to a "
     "constant, with a temperature exponent of three by ten to the minus "
     "thirteenth and a prefactor of exactly 6.0, and is the best-conditioned "
     "row in the file rather than the worst.",
     ""),

    # ---- Sec. III.C, the separation history -----------------------------
    (MAIN,
     "An earlier version of this section called it the one result that "
     "improved under every correction. That is not accurate: at the step that "
     "removed two papers whose extractions could not be reproduced, eta "
     "squared rose while the permutation probability rose with it,",

     "It does not improve monotonically under the corrections, and we report "
     "both halves of it rather than the one that moves the right way: at the "
     "step that removed two papers whose extractions could not be reproduced, "
     "eta squared rose while the permutation probability rose with it,"),

    # ---- Sec. III.D, the scaling test -----------------------------------
    (MAIN,
     "because any binning of a two-dimensional cloud reduces within-bin "
     "scatter, and an earlier version of this section compared these figures "
     "against a 30% adoption bar for which we could give no construction.",

     "because any binning of a two-dimensional cloud reduces within-bin "
     "scatter, and we can give no construction for an adoption bar to compare "
     "it against."),

    # ---- Sec. III.E, the correlation direction --------------------------
    (MAIN,
     "The direction in which a correlation would move the result is not the "
     "same for all three pairs, and an earlier version of this paragraph "
     "asserted that it was.",
     "The direction in which a correlation would move the result is not the "
     "same for all three pairs."),

    # ---- Sec. III.E, the propagated uncertainty -------------------------
    (MAIN,
     "A previous version gave 0.29 dex from a βT scatter of 1.158, which is "
     "not reproducible from the deposit: that family's temperature-axis fits "
     "give 1.171 on the exponent as deposited, over the 106 rows the deposited "
     "table holds for it, and 0.563 on the repaired exponent, over the 105 of "
     "those that carry one. The repaired exponent is the one the 257-fit "
     "cohort and the rest of this paper use, so it is the one propagated here.",

     "The exponent scatter propagated here is the one on the repaired cohort. "
     "That family's temperature-axis fits give 1.171 on the exponent as "
     "deposited, over the 106 rows the deposited table holds for it, and 0.563 "
     "on the repaired exponent, over the 105 of those that carry one; the "
     "repaired exponent is what the 257-fit cohort and the rest of this paper "
     "use."),

    # ---- Sec. III.E, the withdrawn medians ------------------------------
    (MAIN,
     " An earlier version of this section reported medians of 6.00, 5.75 and "
     "5.32 at 0.1 T across the three families, and a top-quartile slice that "
     "was entirely iron chalcogenide 11-type. Both rest on predictions this "
     "revision's reduced-field gate refuses, and both are withdrawn rather "
     "than restated.",
     ""),

    # ---- Sec. III.E, the grid-point count -------------------------------
    (MAIN,
     " An earlier version of this section called 4.2 K and 5 T the only grid "
     "point at which anything is dispatched, which is wrong.",
     ""),

    (MAIN,
     "and this follows from the inference procedure of Section II.D in a more "
     "specific way than we previously stated.",
     "and this follows from the inference procedure of Section II.D."),

    # ---- Figs. 1 and 2, the extraction stage ----------------------------
    (MAIN,
     "because it is a distinct step with its own provenance and its own "
     "failure modes, and it was not visible as a separate stage in the earlier "
     "presentation of this work.",
     "because it is a distinct step with its own provenance and its own "
     "failure modes."),

    (MAIN,
     "because it is a distinct step with its own failure modes, characterized "
     "in Sec. III.F, and it was not visible as a separate stage in the earlier "
     "presentation of this work.",
     "because it is a distinct step with its own failure modes, characterized "
     "in Sec. III.F."),

    # ---- Sec. III.E, the record and compound counts ---------------------
    (MAIN,
     "since the same compound can be reached through more than one source "
     "paper; the earlier presentation reported record counts as compound "
     "counts, and Table IV now reports both.",
     "since the same compound can be reached through more than one source "
     "paper, and Table IV reports both counts."),

    # ---- the two withdrawals of published values ------------------------
    # These stay, reworded. They withdraw values from the paper as submitted,
    # which the referees read and which Table III reports beside the repaired
    # ones, so they are a cohort comparison rather than draft history.
    (MAIN,
     "and we withdraw the three we previously reported rather than replace "
     "them with their mirror image.",
     "and we report no family-level field verdict rather than replacing the "
     "published values with their mirror image."),

    (MAIN,
     "the field-axis verdicts this manuscript previously reported for iron "
     "pnictide 122-type and MgB2-class are withdrawn in Section III.C,",
     "the published field-axis verdicts for iron pnictide 122-type and "
     "MgB2-class are withdrawn in Section III.C,"),

    # ---- two withdrawals that would otherwise be lost --------------------
    # Every value taken out of the manuscript above is already in the response
    # letter except two: the in-corpus baseline of 0.567 that Sec. III.B used
    # to compare against, and the family medians Sec. III.E reported at 0.1 T.
    # Both were in the paper the referees read. Removing them from the
    # manuscript without putting them in the letter would withdraw them
    # silently, which is the opposite of what this edit is for.
    (RESP,
     "An artificial intelligence use disclosure has been added in accordance "
     "with APS policy,",

     "Two values the submitted manuscript carried are withdrawn and are "
     "recorded here rather than in the paper. Section III.B compared the "
     "one-anchor error of 1.592 dex against an in-corpus baseline of 0.567; "
     "that value is not derivable from the deposit and is not on the same "
     "scale as the quantity it was compared with, so no in-corpus baseline is "
     "quoted. Section III.E reported family medians of 6.00, 5.75 and 5.32 in "
     "log10 Jc at 0.1 T together with a top-quartile slice that was entirely "
     "iron chalcogenide 11-type; every prediction behind both is refused by "
     "this revision's reduced-field gate, so both are withdrawn rather than "
     "restated. An artificial intelligence use disclosure has been added in "
     "accordance with APS policy,"),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_version_history_removal.py IN_DIR OUT_DIR")
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
            print("   %-8s %s" % (name.split("_")[0][:8], find.strip()[:62]))
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
