"""
apply_threshold_replacement.py

Removes the 30 percent adoption threshold from the manuscript and puts a test
in its place.

Why. Sec. III.D and the abstract turned on a bar: "Both fall below the 30%
adoption threshold, which marks the level at which a universal law would
substantially exceed the gain observed from family-conditional aggregation."
Nothing in the repository derives 30; it appears only as a literal in figure
code. The quantity the sentence names as its own benchmark is the
family-conditional holdout gain given two paragraphs later, 0.604 dex against
0.613, which is 1.47 percent, so the bar stood twenty times above its stated
benchmark. Lowering it to 1.47 is not the repair either, because a within-bin
scatter reduction and an out-of-sample error reduction are different
quantities and neither converts into the other.

An attempt to derive the bar by putting both schemes on one scale was written
and withdrawn: against the correct null for a nominal label, a random
regrouping of the same compounds into labels with the same size profile, the
family grouping's excess is -2.4 percent at a probability of 0.60, so it
cannot define a threshold. Three of the seven family labels in that cohort are
one compound from one paper. This does not touch the temperature-axis
conditioning result, which is a different statistic on the fitted exponent and
is tested against a paper-clustered null.

What goes in instead, from analysis/scaling_collapse_test.py on the
point-level rebuild cohort of 6070 digitized points, 27 papers, 18 compounds,
171 curves:

  * Rotation. Standardize the two reduced coordinates and bin on a grid
    rotated to a random angle. Geometry and local density are unchanged and
    only the meaning of the axes is destroyed. Over 400 rotations the physical
    grid gives 39.3 percent against the rotated grids' 41.6 on the same
    statistic.
  * Unnormalized coordinates. Binning the same records on laboratory
    temperature and applied field gives 67.0 percent on 42 cells against 39.3
    on 73. Paired on the same resampled curves the gap is 27.7 points, 95
    percent interval 4.7 to 37.5, and the reduced coordinates win on 0.8
    percent of 500 draws. Seventeen of the 42 unnormalized cells hold a single
    compound against three of 73, so that grid separates compounds rather than
    collapsing them.

The percentages already in the paper are kept as descriptive statistics. What
is removed is their comparison against a bar with no construction.

Usage:
    python3 analysis/apply_threshold_replacement.py IN_DIR OUT_DIR

Every target must match exactly once or nothing is written.
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final22.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final22.docx"
RESP = "RESPONSE_TO_REFEREES_final22.docx"
OUT = {MAIN: "HT10016_revised_final23.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final23.docx",
       RESP: "RESPONSE_TO_REFEREES_final23.docx"}

EDITS = [
    # ---- 1. the abstract ----------------------------------------------
    (MAIN,
     "Universal reduced-variable scaling does not clear the threshold we set "
     "for it: normalizing temperature and field by their critical values "
     "reduces the within-bin standard deviation of log10 Jc by only 13.0%, a "
     "variance-scale reduction of 24.3%, both below the 30% adoption "
     "threshold, and the result is unchanged on the standard-deviation scale "
     "under a 35% perturbation of the estimated critical fields.",

     "Universal reduced-variable scaling does not organize this corpus: "
     "normalizing temperature and field by their critical values reduces the "
     "within-bin standard deviation of log10 Jc by only 13.0%, a "
     "variance-scale reduction of 24.3%, the result is unchanged on the "
     "standard-deviation scale under a 35% perturbation of the estimated "
     "critical fields, and on a point-level rebuild of the same test the "
     "reduced coordinates carry no more structure than the same grid rotated "
     "to a random angle."),

    # ---- 2. the introduction ------------------------------------------
    (MAIN,
     "Both fall below the 30% adoption threshold, which marks the level at "
     "which a universal law would substantially exceed the gain observed from "
     "family-conditional aggregation.",

     "We set no numerical adoption threshold against those figures. The "
     "quantity that would define one, the gain from family-conditional "
     "aggregation, is measured on a different scale, as an out-of-sample "
     "error rather than a within-bin scatter, and it is not distinguishable "
     "from zero. Section III.D instead tests the scaling claim directly, "
     "against coordinates chosen to carry no physics."),

    # ---- 3. Sec. III.D, the comparison itself --------------------------
    (MAIN,
     "Both fall well below the 30% threshold required for adopting "
     "universality as the prediction scope. We report the standard-deviation "
     "figure as primary and give the variance-scale equivalent explicitly, "
     "because the two differ by roughly a factor of two and the distinction "
     "is a recurring source of confusion in scaling-collapse claims.",

     "We report the standard-deviation figure as primary and give the "
     "variance-scale equivalent explicitly, because the two differ by roughly "
     "a factor of two and the distinction is a recurring source of confusion "
     "in scaling-collapse claims. A percentage on its own does not settle "
     "whether a collapse has occurred, because any binning of a "
     "two-dimensional cloud reduces within-bin scatter, and an earlier "
     "version of this section compared these figures against a 30% adoption "
     "bar for which we could give no construction. We therefore test the "
     "claim directly, on a point-level rebuild of this cohort covering 6070 "
     "digitized points from 27 papers, 18 compounds and 171 curves. First, "
     "standardize the two reduced coordinates and bin on a grid rotated to a "
     "random angle, which leaves the geometry and the local density of the "
     "cloud unchanged and destroys only the meaning of the axes. Over 400 "
     "rotations the physical grid gives 39.3% against the rotated grids' "
     "41.6% on the same statistic, so the reduced coordinates are not better "
     "than a random rotation of themselves. Second, bin the same records on "
     "unnormalized temperature and applied field. That grid reduces the "
     "within-cell standard deviation by 67.0% on 42 cells against 39.3% on "
     "73, and paired on the same resampled curves it wins by 27.7 points with "
     "a 95% interval of 4.7 to 37.5. The mechanism is visible in the cell "
     "composition: seventeen of the forty-two unnormalized cells hold a "
     "single compound against three of the seventy-three reduced cells, so "
     "the unnormalized grid separates compounds rather than collapsing them. "
     "Measurements cluster at a few conventional temperatures and low applied "
     "fields, and that convention tracks the material. Both tests point the "
     "same way as the percentage: the organizing variables here are material "
     "identity and measurement context, not reduced temperature and reduced "
     "field."),

    # ---- 4. Sec. III.D, the perturbation paragraph ---------------------
    (MAIN,
     "Perturbing all 14 by independent lognormal factors with a 35% one-sigma "
     "scale error and repeating the binning 400 times, no draw exceeded 30% "
     "on the standard-deviation scale, and 9 of 400 exceeded it on the "
     "variance scale. The conclusion is therefore insensitive to the accuracy "
     "of the estimated critical fields on the standard-deviation scale. We "
     "note the one qualification: on the variance scale 9 of the 400 draws do "
     "reach 30%, so the result is secure on the metric we report as primary "
     "and marginal on the other, and we prefer to say so rather than to "
     "describe it as insensitive without qualification.",

     "Perturbing all 14 by independent lognormal factors with a 35% one-sigma "
     "scale error and repeating the binning 400 times, the standard-deviation "
     "reduction stayed below 30% in every draw and the variance-scale "
     "reduction reached 30% in 9 of the 400. The reduction is therefore "
     "stable against the accuracy of the estimated critical fields on the "
     "metric we report as primary and moves a little on the other. The 30% "
     "figure appears here only as the reference level used in the original "
     "submission, and it no longer carries a decision."),

    # ---- 5. Table III, the universality row ----------------------------
    (MAIN,
     "Within-bin standard deviation falls 13.0%, variance-scale equivalent "
     "24.3%, both below the 30% adoption threshold. Zero of 400 "
     "critical-field perturbation draws reach 30% on the standard-deviation "
     "scale.",

     "Within-bin standard deviation falls 13.0%, variance-scale equivalent "
     "24.3%. On a point-level rebuild the reduced coordinates give no more "
     "reduction than the same grid rotated to a random angle, 39.3% against "
     "41.6% over 400 rotations, and unnormalized temperature and field do "
     "better on the same records, 67.0% on 42 cells against 39.3% on 73, by "
     "isolating compounds. Zero of 400 critical-field perturbation draws "
     "exceed 30% on the standard-deviation scale."),

    # ---- 6. the conclusion ---------------------------------------------
    (MAIN,
     "Universal reduced-variable scaling reduces the within-bin scatter by "
     "only 13.0% on the standard-deviation scale and 24.3% on the variance "
     "scale, both below the 30% adoption threshold, and the "
     "standard-deviation-scale result insensitive to a 35% perturbation of "
     "the estimated critical fields, with the variance-scale result marginal "
     "under that test.",

     "Universal reduced-variable scaling reduces the within-bin scatter by "
     "only 13.0% on the standard-deviation scale and 24.3% on the variance "
     "scale, with the standard-deviation-scale result insensitive to a 35% "
     "perturbation of the estimated critical fields and the variance-scale "
     "result marginal under that test. Two direct tests point the same way: "
     "the reduced coordinates carry no more structure than the same grid "
     "rotated to a random angle, and unnormalized temperature and applied "
     "field organize the same records better by isolating compounds."),
    # ---- 7. the response letter, which still cites the bar and still
    #         attributes the conditioning claim to the diagnostic the
    #         manuscript moved it off ------------------------------------
    (RESP,
     "Universal reduced-variable scaling does not clear our 30% threshold. It "
     "reduces the within-bin scatter by 13.0% on the standard-deviation "
     "scale, replacing a previously reported 14.1% whose numerator and "
     "denominator had been computed on different populations. That result is "
     "insensitive to a 35% perturbation of the estimated critical fields. The "
     "conditioning claim now rests on the variance-decomposition diagnostic, "
     "which uses the critical-current anchor and involves neither a fitted "
     "exponent nor a critical field scale, rather than on the error ratio "
     "Referee A questioned.",

     "Universal reduced-variable scaling does not organize the corpus. It "
     "reduces the within-bin scatter by 13.0% on the standard-deviation "
     "scale, replacing a previously reported 14.1% whose numerator and "
     "denominator had been computed on different populations, and that result "
     "is insensitive to a 35% perturbation of the estimated critical fields. "
     "We have withdrawn the 30% adoption threshold that figure was compared "
     "against in the previous version, because we could give no construction "
     "for it, and Sec. III.D now tests the scaling claim directly instead: "
     "the reduced coordinates carry no more structure than the same grid "
     "rotated to a random angle, and unnormalized temperature and applied "
     "field organize the same records better by isolating compounds. The "
     "conditioning claim rests on the temperature-axis separation reported in "
     "Sec. III.C, not on the variance-decomposition diagnostic and not on the "
     "error ratio Referee A questioned; the diagnostic sets the conditioning "
     "rule per family and is reported with the clustered-null floors that "
     "prevent it from establishing the distinction."),
]



def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_threshold_replacement.py IN_DIR OUT_DIR")
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
