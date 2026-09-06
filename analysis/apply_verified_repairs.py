"""
apply_verified_repairs.py

Five repairs, each one verified against the deposit and then given to an
independent reviewer with instructions to break it. All five survived.

1. **Stage 3's 0.84 is a resubstitution figure presented as a
leave-one-substructure-out error.** In
analysis/phase_3_p39_multi_stage_predictor.py the substructure medians are
built from the full cohort and the prediction for the held-out family is that
family's own median, so the family predicts itself. The deposited artifact
data/phase_3_p39_multi_stage_mae_decomposition.csv records a Stage 3 residual
of 4.44e-16 for the MgB2 class, which is the signature. The paragraph
immediately above withdraws Stages 1 and 2 for this same defect, from the same
generator and the same run. Under genuine withholding, on the cuprates-removed
arm that the next sentence relies on, the value is 0.816.

2. **The external anchor-count errors are in dex and are labelled dimensionless
exponent errors.** analysis/external_anchor_count.py computes
|predicted_log_Jc - actual_log_Jc|, a difference of base-10 logarithms of
critical current. Sec. II.A states the opposite convention and says an earlier
version of the manuscript made exactly this error in the other direction.

3. **The in-corpus baseline of 0.567 has no derivation in the deposit.** It
appears once in the manuscript and once as a literal in
analysis/manuscript_figure_4.py, and it is set beside 1.592, which is a dex
quantity, as though the two were on one scale. The comparison is removed rather
than repaired, because nothing in the repository says what 0.567 is.

4. **The 15 MgB2 temperature fits are misdescribed in both particulars.** In
data/h1b_per_paper_form3_fits.csv six of the fifteen rest on three points, not
one, and the largest rms is 0.474. The reported rms of 6.3 is a transcription
of 6.332e-14: that row fits a constant, with a temperature exponent of 3.1e-13
and a prefactor of exactly 6.0, and it is the best-conditioned row in the file
rather than the worst.

5. **The variance-ratio regime cuts are stated nowhere.**
regime_from_variance_ratio cuts at 0.7 and 0.3, duplicated in three modules.
These are not the applicability window, which is stated three times. Applying
the small-sample bias correction the paper invokes for the MgB2 class uniformly
moves the iron chalcogenide family across the lower cut on the deposited
anchors and the 122-type family across it on the repaired anchors, and leaves
the one surviving upper-regime assignment 0.0007 above its cut.

Usage:
    python3 analysis/apply_verified_repairs.py IN_DIR OUT_DIR

Every target must match exactly once or nothing is written.
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final21.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final21.docx"
RESP = "RESPONSE_TO_REFEREES_final21.docx"
OUT = {MAIN: "HT10016_revised_final22.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final22.docx",
       RESP: "RESPONSE_TO_REFEREES_final22.docx"}

EDITS = [
    # ---- 1. Stage 3 -----------------------------------------------------
    (MAIN,
     "Stage 3 reports a substructure-level central tendency with an explicit "
     "interquartile range, giving a leave-one-substructure-out error of 0.84 "
     "in the field exponent. This exceeds the Stage 2 error because the "
     "reporting scope is broader.",
     "Stage 3 reports a substructure-level central tendency with an explicit "
     "interquartile range. An earlier version of this section gave its error "
     "as 0.84 in the field exponent and called it a leave-one-substructure-out "
     "error. It is not one. That figure comes from the same generator and the "
     "same run as the Stage 1 and Stage 2 values withdrawn above, and it "
     "carries the same defect: the median that predicts a held-out family is "
     "computed over a pool that includes that family, so two of its five terms "
     "are zero by construction. Under genuine withholding, on the "
     "cuprates-removed cohort the interquartile result below is computed on, "
     "the Stage 3 error is 0.816. It exceeds the Stage 2 error because the "
     "reporting scope is broader."),

    # ---- 2 and 3. the K-anchor units and the untraced baseline ----------
    (MAIN,
     "With one anchor compound the pooled mean absolute error is 1.592 in the "
     "field exponent, 2.81 times the in-corpus baseline of 0.567. A "
     "transition-temperature-only baseline reaches 1.166 on the same compounds",
     "With one anchor compound the pooled mean absolute error is 1.592 dex in "
     "log10 Jc. We note the unit explicitly because an earlier version of this "
     "section reported it as an error in the field exponent, and because a "
     "further comparison against an in-corpus baseline of 0.567 has been "
     "removed: that value is not derivable from the deposit and it is not on "
     "the same scale as 1.592. A transition-temperature-only baseline reaches "
     "1.166 dex on the same compounds"),

    (MAIN,
     "One anchor gives 1.592 exponent error and underperforms a "
     "transition-temperature-only baseline;",
     "One anchor gives 1.592 dex in log10 Jc and underperforms a "
     "transition-temperature-only baseline;"),

    (MAIN,
     "Markers show the pooled L1 mean absolute error in the dimensionless "
     "field-dependence exponent at each anchor-count value K.",
     "Markers show the pooled L1 mean absolute error in log10 Jc, in dex, at "
     "each anchor-count value K. This is a prediction error in critical "
     "current and not an error in the field exponent, which the two conventions "
     "of Sec. II.A distinguish."),

    # ---- 4. the MgB2 temperature fits -----------------------------------
    (MAIN,
     "with a median βT of 1.14; two of the fifteen are poorly constrained, "
     "one fitting with an rms of 6.3 in log10 Jc and one resting on three "
     "points.",
     "with a median βT of 1.14. Six of the fifteen rest on three points, "
     "which is the minimum a three-parameter form admits, and two of those six "
     "return temperature exponents of 0.011 and 0.211. The largest rms in the "
     "cohort is 0.474 in log10 Jc. An earlier version of this sentence "
     "described one fit resting on three points and one fitting with an rms of "
     "6.3; the second was a transcription of 6.3 by ten to the minus "
     "fourteenth, which is a fit to a constant, with a temperature exponent of "
     "three by ten to the minus thirteenth and a prefactor of exactly 6.0, and "
     "is the best-conditioned row in the file rather than the worst."),

    # ---- 5. the regime cuts ---------------------------------------------
    (MAIN,
     "This is a direct test of whether sample form is a useful conditioning "
     "variable, and the resulting regime label drives the exponent aggregation "
     "used for prediction.",
     "This is a direct test of whether sample form is a useful conditioning "
     "variable, and the resulting regime label drives the exponent aggregation "
     "used for prediction. The label is assigned by two cuts on the ratio, "
     "which we state here because earlier versions of this manuscript did not: "
     "above 0.7 the family is treated as sample-form dominant, from 0.3 to 0.7 "
     "as moderate, and below 0.3 as minor. These are not the applicability "
     "window of Eq. (1), which uses the same two numbers on reduced "
     "temperature and reduced field. Two qualifications belong with them. The "
     "cuts are applied to the uncorrected ratio, and applying the small-sample "
     "bias correction we invoke for the MgB2 class to every family instead "
     "moves the iron chalcogenide family below the lower cut on the deposited "
     "anchors and the 122-type family below it on the repaired anchors. The "
     "one family that remains above the upper cut clears it by 0.0007. No "
     "dispatched prediction changes under either correction, because the "
     "families that move emit nothing, but the classification is not stable "
     "and we do not present it as one."),

    # ---- 6. the dotted line the figure no longer draws ------------------
    (MAIN,
     "The dashed line marks the transition-temperature-only baseline; the "
     "dotted line marks the in-corpus K = 3 baseline.",
     "The dashed line marks the transition-temperature-only baseline."),

    # ---- 7. what the 45.2 percent compares ------------------------------
    (MAIN,
     "On the matched three monotonic cuprates the one-anchor error is 1.267, "
     "the three-anchor error is 0.694, and the reduction is 45.2%, and that is "
     "the figure we carry.",
     "On the matched three monotonic cuprates the one-anchor error is 1.267 "
     "dex, the three-anchor error is 0.694 dex, and the reduction is 45.2%. "
     "That figure has to be read with the composition of the two held-out sets "
     "in front of it, which we did not previously give. The two arms score "
     "almost entirely different points, 46 against 48 with one shared "
     "coordinate, and they sit in different regimes relative to the anchors: "
     "the one-anchor set is entirely extrapolation, while a little over half "
     "the three-anchor set is interpolation. On the one regime both arms "
     "populate equally, low-side extrapolation with twelve points each, the "
     "improvement is 2.3% rather than 45.2%. The gate is therefore set on a "
     "comparison that is substantially a comparison of where the held-out "
     "points sit, and we report the requirement of three anchors as a "
     "conservative operating choice rather than as a measured 45% gain."),

    # ---- 2 again, in the supplement -------------------------------------
    (SUPP,
     "gives 2.567 for the K = 1 predictor compared with 1.613 for the "
     "transition-temperature-only baseline. These are dimensionless exponent "
     "errors.",
     "gives 2.567 for the K = 1 predictor compared with 1.613 for the "
     "transition-temperature-only baseline. These are errors in log10 Jc, in "
     "dex, not dimensionless exponent errors: the quantity computed by "
     "analysis/external_anchor_count.py is the absolute difference of predicted "
     "and measured log10 Jc. An earlier version of this section labelled them "
     "the other way."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_verified_repairs.py IN_DIR OUT_DIR")
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
