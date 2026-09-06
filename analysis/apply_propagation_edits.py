"""
apply_propagation_edits.py

Four edits to the substructure-aggregate quadrature, in Sec. III.E and
Supplement Sec. 8, after analysis/propagated_uncertainty.py recomputed it from
the deposit.

Three defects.

**The temperature-exponent scatter is the pre-repair one, and the printed value
does not reproduce.** The two documents give the inputs as 0.265 in
log10 Jc,partial, 1.158 in beta_T and 0.920 in beta_H over the iron pnictide
122-type scope. The first and third reproduce to four digits. The second does
not: the deposit returns 1.171 for that family's exponent as deposited and
0.563 for the repaired exponent, and every one of the 106 rows was repaired,
from a default 38.0 K anchor to a paper-reported one. The repaired exponent is
what the 257-fit cohort and the rest of the paper use, so the quadrature is now
computed on it and the result moves from 0.29 dex to 0.27. The value 1.158 does
appear in the deposit, as the pooled unconditioned per-paper field-axis
validation error over 94 fits printed two paragraphs below in the same
supplement section. The coincidence is noted; the attribution is not asserted.

**The correlation caveat points the wrong way.** Both documents say that a
positive correlation makes the independent quadrature an understatement, so
0.29 should be read as a lower bound. Write log10 Jc as the anchor plus
beta_T log10(1 - T/Tc) plus beta_H log10(1 - H/Hc2). The derivative with
respect to the anchor is +1 and both logarithms are negative, so the two
anchor-to-exponent cross terms are negative and only the exponent-to-exponent
term is positive. On the corrected inputs at 5 T the three coefficients are
-0.0274, -0.0223 and +0.0044, so a uniform positive correlation lowers the
propagated uncertainty. The claim of a lower bound is withdrawn and no bound is
claimed in either direction.

**The scope dispatches nothing.** The 122-type scope emits no prediction under
the refusal gates of this revision, which the paper states three times. The
same propagation on the MgB2 class, the only family that dispatches, gives 0.49
dex at 4.2 K and 0.57 at 20 K, and those are the figures that attach to the
predictions the framework actually makes.

Usage:
    python3 analysis/apply_propagation_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final24.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final24.docx"
RESP = "RESPONSE_TO_REFEREES_final24.docx"
OUT = {MAIN: "HT10016_revised_final25.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final25.docx",
       RESP: "RESPONSE_TO_REFEREES_final25.docx"}

NB = " "

EDITS = [
    # ---- 1. Sec. III.E, the quadrature itself --------------------------
    (MAIN,
     "The substructure-aggregate quadrature gives 0.29 dex at one sigma, "
     "computed from residual standard deviations of 0.265 in log10 Jc,partial, "
     "1.158 in βT, and 0.920 in βH within the iron pnictide "
     "122-type scope, and it is flat to within 0.005 dex across the evaluated "
     "field grid.",

     "The substructure-aggregate quadrature gives 0.27 dex at one sigma within "
     "the iron pnictide 122-type scope, computed from residual standard "
     "deviations of 0.265 in log10 Jc,partial, 0.563 in βT, and 0.920 in "
     "βH, and it is flat to within 0.005 dex across the evaluated field "
     "grid. A previous version gave 0.29 dex from a βT scatter of 1.158, "
     "which is not reproducible from the deposit: that family's 106 "
     "temperature-axis fits give 1.171 on the exponent as deposited and 0.563 "
     "on the repaired exponent, and every one of them was repaired. The "
     "repaired exponent is the one the 257-fit cohort and the rest of this "
     "paper use, so it is the one propagated here. This scope emits no "
     "prediction under the refusal gates of this revision. On the MgB2 class, "
     "the only family that does emit, the same propagation gives 0.49 dex at "
     "4.2 K and 0.57 dex at 20 K, and those are the figures that attach to the "
     "dispatched predictions."),

    # ---- 2. Sec. III.E, the correlation caveat -------------------------
    (MAIN,
     "Where the terms are in fact positively correlated the quadrature above "
     "understates the aggregate uncertainty, so the figure we quote should be "
     "read as a lower bound on the structural component [39].",

     "The direction in which a correlation would move the result is not the "
     "same for all three pairs, and an earlier version of this paragraph "
     "asserted that it was. Writing log10 Jc as the anchor plus βT "
     "log10(1 - T/Tc) plus βH log10(1 - H/Hc2,0), the derivative with "
     "respect to the anchor is positive while both logarithms are negative, so "
     "a positive correlation between the anchor and either exponent lowers the "
     "propagated variance and only a positive correlation between the two "
     "exponents raises it. The two anchor terms dominate, and a uniform "
     "positive correlation therefore lowers the quoted figure rather than "
     "raising it. We claim no bound in either direction [39]."),

    # ---- 3. Supplement Sec. 8, the numerical details -------------------
    (SUPP,
     "For the iron pnictide 122-type family these are 0.265 in log Jc," + NB
     + "partial, 1.158 in βT, and 0.920 in βH, measured across 36 "
     "field-axis fits passing physicality and 106 temperature-axis fits. "
     "Evaluated at 4.2 K against a 22 K transition temperature and a 50 T "
     "upper critical field, the quadrature gives 0.285 dex at 0.1 T, 0.286 dex "
     "at 1 T, and 0.289 dex at 5 T, which the main text quotes as 0.29 dex.",

     "For the iron pnictide 122-type family these are 0.265 in log Jc," + NB
     + "partial and 0.920 in βH across the 36 field-axis fits passing "
     "physicality, and 0.563 in βT across that family's 106 "
     "temperature-axis fits. Evaluated at 4.2 K against a 22 K transition "
     "temperature and a 50 T upper critical field, the quadrature gives 0.270 "
     "dex at 0.1 T, 0.270 dex at 1 T, and 0.273 dex at 5 T, which the main "
     "text quotes as 0.27 dex. A previous version gave 0.285, 0.286 and 0.289 "
     "from a βT scatter of 1.158. That value is not reproducible from the "
     "deposit under any mask or estimator we tried: the same 106 fits give "
     "1.171 on the exponent as deposited and 0.563 on the repaired exponent, "
     "which is the one used throughout. The value 1.158 does appear in the "
     "deposit, as the pooled unconditioned per-paper field-axis validation "
     "error over 94 fits reported two paragraphs below; we note the "
     "coincidence without asserting that it is the source. On the MgB2 class, "
     "which is the only family that dispatches, the same propagation gives "
     "0.486 dex at 4.2 K and 0.573 dex at 20 K, at 5 T against a 38 K "
     "transition temperature and a 15.5 T upper critical field, drawing the "
     "temperature-exponent scatter from the separate per-paper cohort of 15 "
     "MgB2 fits because the 257-fit cohort carries none. The propagation is "
     "regenerated by analysis/propagated_uncertainty.py."),

    # ---- 4. Supplement Sec. 8, the correlation caveat ------------------
    (SUPP,
     "Where the terms are in fact positively correlated, independent "
     "quadrature understates the aggregate uncertainty, so 0.29 dex should be "
     "read as a lower bound on the structural component rather than as a "
     "complete accounting.",

     "The sign of a correlation correction is not the same for all three "
     "pairs. The derivative of log10 Jc with respect to the anchor is positive "
     "and the two logarithmic factors multiplying the exponents are negative, "
     "so a positive correlation between the anchor and either exponent lowers "
     "the propagated variance while a positive correlation between the two "
     "exponents raises it. On the corrected inputs at 5 T the three cross-term "
     "coefficients are -0.0274, -0.0223 and +0.0044, so their sum is negative "
     "and a uniform positive correlation lowers the result: 0.273 dex at zero "
     "correlation, 0.238 at 0.4 and 0.196 at 0.8. An earlier version of this "
     "section said the opposite, that independent quadrature understates the "
     "aggregate, which is wrong for this functional form; we therefore claim "
     "no bound in either direction."),
    # ---- 5. Table III, the uncertainty row -----------------------------
    (MAIN,
     "One-sigma uncertainty is 0.29 dex in log10 Jc, propagated in quadrature "
     "over the three fitted terms.",

     "One-sigma uncertainty is 0.27 dex in log10 Jc on the iron pnictide "
     "122-type scope, propagated in quadrature over the three fitted terms on "
     "the repaired temperature exponent. That scope dispatches nothing; on the "
     "MgB2 class, which does, the same propagation gives 0.49 dex at 4.2 K and "
     "0.57 dex at 20 K."),
]



def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_propagation_edits.py IN_DIR OUT_DIR")
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
