"""
apply_dispatch_rebuild_edits.py

Puts the documents on the regenerated dispatch table, and corrects the cohort
counts a working checker found once it was pointed at the right files, A5.

The dispatch table now reproduces. It did not before, for two reasons.

  The generator routed the MgB2 records of one paper, matpr.2019.05.078,
  through a (conventional_AlB2, wire) sample-form cell, because that paper's
  fits carry a wire label. Sec. II.D commits a family in the minor-separation
  regime to substructure-aggregate scope, and the released file already carried
  the aggregate scope for those records, so the rule had been applied to the
  file and never to the code. The generator now reads the regime from the
  deposited variance decomposition, which is the source Sec. III.A reports.
  audit/dispatch_spread_20260905.md sets out why the wire cell should not be
  used: it holds 8 fits from 2 papers, and the records it predicts come from
  one of them, so a quarter of the pool is the thing being predicted.

  The table was never the output of one script. Three steps run after the
  predictor, applying the withdrawals and the two clauses of the applicability
  window, and only the first was named anywhere. analysis/rebuild_dispatch.py
  runs all four in order and compares the result with the deposited file cell
  by cell. It now reports no difference.

Two printed numbers move, both toward the claim they support. The spread of the
dispatched set at 4.2 K and 5 T falls from 0.0098 dex to 0.0085, and at 20 K
and 5 T from 0.259 to 0.254. The regression slope at 20 K moves from 1.22 to
1.21. Everything else holds: 163 emitted predictions, 84 compounds, all five
refusal counts, the 4.980 family constant, the 5.324 anchor and its 0.344 dex
displacement, the median widths of 0.61 and 0.60 dex, and the 321 of 540 split.
The width on the three exact-anchor records moves from 0.395 to 0.398.

Four counts are corrected as well. analysis/check_claims_against_deposit.py has
been reading three filenames that stopped existing several stages of the
document lineage ago, so every run reported three missing artifacts, bound zero
tokens, and passed. Pointed at the current documents it binds 58 and disagrees
on three quantities, of which two were its own stale definitions and one was
real: the documents print 106 temperature-axis fits for the iron pnictide
122-type family and 20 source papers for the temperature-axis cohort, which are
the counts on the cohort as deposited, while the same sentences print 257 for
the cohort as a whole, which is the repaired one. On the repaired cohort the
122-type family holds 105 fits and the cohort is drawn from 18 source papers,
all of them arXiv preprints rather than 18 of 20. The 0.563 scatter printed
beside the 106 was already computed on the 105.

One further number is made exact. The emitted set spans reduced temperatures
from 0.10 to 0.70, not 0.48 to 0.70; the narrower range is the 20 K point
alone.

Usage:
    python3 analysis/apply_dispatch_rebuild_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final38.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final38.docx"
RESP = "RESPONSE_TO_REFEREES_final38.docx"
OUT = {MAIN: "HT10016_revised_final39.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final39.docx",
       RESP: "RESPONSE_TO_REFEREES_final39.docx"}

EDITS = [
    # ------------- Sec. III.E, the dispatch spread ----------------------
    (MAIN,
     "span 0.0098 dex, which is 1.6% of the 0.60 dex bootstrap interval at "
     "the same point; at 20 K and 5 T the 77 records covering 75 compounds "
     "span 0.259 dex. Both points clear the gates of this revision, at "
     "reduced temperatures of 0.48 to 0.70 and a reduced field of 0.3226.",

     "span 0.0085 dex, which is 1.4% of the 0.60 dex bootstrap interval at "
     "the same point; at 20 K and 5 T the 77 records covering 75 compounds "
     "span 0.254 dex. Both points clear the gates of this revision, at "
     "reduced temperatures of 0.10 to 0.70, the upper end reached at the 20 K "
     "point, and a reduced field of 0.3226."),

    (MAIN,
     "and the residual 0.0098 dex is the bootstrap draw over an 18-fit pool",
     "and the residual 0.0085 dex is the bootstrap draw over an 18-fit pool"),

    (MAIN,
     "the prediction regresses on the temperature term with a slope of 1.22 "
     "and an R squared of 0.996, recovering the family exponent of 1.14.",
     "the prediction regresses on the temperature term with a slope of 1.21 "
     "and an R squared of 0.996, recovering the family exponent of 1.14."),

    # ------------- the temperature-axis cohort counts -------------------
    (MAIN,
     "Eighteen of the 20 source papers behind the temperature-axis exponent "
     "cohort are arXiv preprints,",
     "All 18 source papers behind the temperature-axis exponent cohort are "
     "arXiv preprints,"),

    (MAIN,
     "in the iron pnictide 122-type family the 36 field-axis fits and the 106 "
     "temperature-axis fits share no source paper and compound in common.",
     "in the iron pnictide 122-type family the 36 field-axis fits and the 105 "
     "temperature-axis fits share no source paper and compound in common."),

    (MAIN,
     "that family's 106 temperature-axis fits give 1.171 on the exponent as "
     "deposited and 0.563 on the repaired exponent, and every one of them was "
     "repaired.",

     "that family's temperature-axis fits give 1.171 on the exponent as "
     "deposited, over the 106 rows the deposited table holds for it, and "
     "0.563 on the repaired exponent, over the 105 of those that carry one."),

    # ------------- Data Availability ------------------------------------
    (MAIN,
     "so that results reported through each path can be reproduced "
     "independently.",

     "so that results reported through each path can be reproduced "
     "independently. The candidate dispatch table is the output of four "
     "scripts run in order, the predictor followed by the record withdrawals "
     "and the two clauses of the applicability window, and a fifth runs them "
     "and compares the result with the deposited file cell by cell."),

    # ------------- the supplement ---------------------------------------
    (SUPP,
     "and 0.563 in βT across that family's 106 temperature-axis fits.",
     "and 0.563 in βT across the 105 temperature-axis fits that family "
     "carries in the repaired cohort."),

    (SUPP,
     "18 of the 20 temperature-axis source papers are arXiv preprints,",
     "all 18 temperature-axis source papers are arXiv preprints,"),

    # ------------- the response letter -----------------------------------
    (RESP,
     "At 4.2 K and 5 T the 86 records span 0.0098 dex, 1.6% of the 0.60 dex "
     "bootstrap interval there; at 20 K and 5 T the 77 records span 0.259 "
     "dex.",
     "At 4.2 K and 5 T the 86 records span 0.0085 dex, 1.4% of the 0.60 dex "
     "bootstrap interval there; at 20 K and 5 T the 77 records span 0.254 "
     "dex."),

    (RESP,
     "the prediction regresses on the temperature term with a slope of 1.22 "
     "and an R squared of 0.996",
     "the prediction regresses on the temperature term with a slope of 1.21 "
     "and an R squared of 0.996"),

    (RESP,
     "The 0.0098 dex is not a spread between compounds:",
     "The 0.0085 dex is not a spread between compounds:"),

    (RESP,
     "On the three records carrying an exact critical-field anchor it is "
     "0.395 dex; on the 83 carrying a parent anchor it is 0.602.",
     "On the three records carrying an exact critical-field anchor it is "
     "0.398 dex; on the 83 carrying a parent anchor it is 0.602."),

    (RESP,
     "that 18 of the 20 source papers behind the temperature-axis cohort are "
     "arXiv preprints,",
     "that all 18 source papers behind the temperature-axis cohort are arXiv "
     "preprints,"),

    (RESP,
     "Both clear this revision's gates, at reduced temperatures of 0.48 to "
     "0.70 against the 0.7 bound",
     "Both clear this revision's gates, at reduced temperatures of 0.10 to "
     "0.70 against the 0.7 bound, the upper end reached at the 20 K point"),

    # ------------- the reproduction disclosure, now a fix ----------------
    (RESP,
     "The deposited prediction file does not reproduce from its own "
     "generator. Running the deposited dispatch code on the deposited tables "
     "returns the released file exactly, with one exception: for two records "
     "of one paper the generator commits to a wire sample-form cell and the "
     "released file does not, and those two records carry four of the emitted "
     "predictions. Every other column matches and the remaining predictions "
     "differ by at most 0.014 in log10 Jc, which is the bootstrap draw. The "
     "difference predates this revision and none of the corrections reported "
     "above is implicated. Separately, our withdrawals were applied by "
     "editing the deposited tables while the candidate list is rebuilt from "
     "the extraction directory, so regenerating restores six withdrawn "
     "candidates; all six are refused and no emitted prediction changes, but "
     "the generator cannot enforce a withdrawal and we say so rather than "
     "leave a reader to find it. Both are recorded in the deposited audit.",

     "The deposited prediction file did not reproduce from its own generator, "
     "and now does. Two things stood between them. For the records of one "
     "paper the generator committed to a wire sample-form cell while the "
     "released file used the substructure aggregate, which is what Sec. II.D "
     "prescribes for a family in the minor-separation regime; the rule had "
     "been applied to the file and never written into the code, and the code "
     "now reads the regime from the deposited variance decomposition. That "
     "cell should not have been used in any case: it holds eight fits from "
     "two papers, and the records it predicts come from one of them, so a "
     "quarter of the pool is the thing being predicted, which is the "
     "relabelling problem we concede above. Second, the dispatch table was "
     "never the output of one script. Three steps run after the predictor, "
     "applying our record withdrawals and the two clauses of the "
     "applicability window, and only the first was named anywhere, so a "
     "reader who ran it alone got 2151 rows against our 2097 and two of the "
     "five refusal codes. One script now runs all four in order and compares "
     "the result with the released file cell by cell. Regenerating moved two "
     "printed numbers, both toward the claim they support: the spread at "
     "4.2 K and 5 T falls from 0.0098 dex to 0.0085 and at 20 K and 5 T from "
     "0.259 to 0.254. The 163 emitted predictions, the 84 compounds and all "
     "five refusal counts are unchanged."),

    # ------------- the reproducibility standard --------------------------
    (RESP,
     "Every figure in the paper regenerates from the deposited data, every "
     "printed count is asserted against the deposited tables by a script that "
     "ships with the paper,",

     "Every figure in the paper regenerates from the deposited data pixel for "
     "pixel, the candidate dispatch table regenerates from the deposited "
     "tables cell for cell, every printed count is asserted against those "
     "tables by a script that ships with the paper,"),
]


# The regenerated Figure 5 goes in with the text. Its shaded envelope is drawn
# at half the median bootstrap width over the emitted set, which moved with the
# dispatch table from 0.6117 dex to 0.6124, so the committed PNG changed and the
# copy in the document has to change with it. The caption's 0.31 dex is half of
# either and does not move. Named explicitly rather than found by elimination,
# for the reason given on FIGURE_3_MEDIA in
# analysis/apply_anchor_cohort_edits.py.
FIGURE_5 = os.path.join("figures", "manuscript_figure_5.png")
FIGURE_5_MEDIA = "word/media/ad7e70672d769313d2aa9207701a11fd21f18804.png"
FIGURE_5_OLD_CY = "2718509"


def _set_extent(doc, png_path, old_cy, label):
    """Rewrite one drawing's display height to match its image.

    Both wp:extent and the a:ext inside pic:spPr carry the pair and Word uses
    the second, so a run that rewrites one and not the other leaves the figure
    stretched with nothing reporting it. The count is returned so the caller
    can require two.
    """
    from PIL import Image
    with Image.open(png_path) as im:
        w, h = im.size
    cx = 5715000
    cy = str(int(round(cx * h / w)))
    before = doc.count('cx="5715000" cy="%s"' % old_cy)
    doc = doc.replace('cx="5715000" cy="%s"' % old_cy,
                      'cx="5715000" cy="%s"' % cy)
    if cy != old_cy:
        print("   %-8s %s extent cy %s -> %s (image %dx%d)"
              % ("HT10016", label, old_cy, cy, w, h))
    return doc, before


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_dispatch_rebuild_edits.py IN_DIR OUT_DIR")
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
        swapped = False
        if name == MAIN:
            if not os.path.exists(FIGURE_5):
                sys.exit("missing %s; run analysis/manuscript_figure_5.py "
                         "first" % FIGURE_5)
            fresh = open(FIGURE_5, "rb").read()
            doc, n_ext = _set_extent(doc, FIGURE_5, FIGURE_5_OLD_CY,
                                     "figure 5")
            if n_ext != 2:
                sys.exit("%s: found %d extent value(s) for Figure 5, "
                         "expected 2" % (name, n_ext))
        tmp = op + ".part"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, doc)
                elif name == MAIN and item.filename == FIGURE_5_MEDIA:
                    old_bytes = zin.read(item.filename)
                    zout.writestr(item, fresh)
                    swapped = True
                    print("   %-8s figure 5 media %d -> %d bytes"
                          % ("HT10016", len(old_bytes), len(fresh)))
                else:
                    zout.writestr(item, zin.read(item.filename))
        zin.close()
        if name == MAIN and not swapped:
            os.remove(tmp)
            sys.exit("%s: %s is not in the document, so the regenerated "
                     "Figure 5 was not embedded" % (name, FIGURE_5_MEDIA))
        shutil.move(tmp, op)
        print("   wrote %s" % op)
    return 0


if __name__ == "__main__":
    sys.exit(main())
