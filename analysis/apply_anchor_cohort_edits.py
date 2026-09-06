"""
apply_anchor_cohort_edits.py

Puts Figure 3, its caption, Table I, Table III, the abstract and the response
letter on one anchor cohort: the repaired one.

Why. Figure 3 drew the deposited 96-row per-paper anchor table while Sec. III.A
and Table III reported both cohorts and the abstract reported only the
deposited one. analysis/figure_4_source.py now draws the repaired cohort, the
70 rows carrying no withdrawal, and this script moves every statement about it
onto the same cohort. The regenerated PNG is swapped into the document in the
same pass, so the embedded image and figures/manuscript_figure_3.png cannot
disagree.

What the repaired cohort gives, from analysis/anchor_form_permutation.py:

  family                 n   sample forms          eta2     exact p   clustered
  iron chalcogenide 11   5   thin film 3, sc 2     0.8090   0.100     4 labellings, p 0.25
  iron pnictide 122      5   thin film 3, sc 2     0.3743   0.300    10 labellings, p 0.30
  MgB2-class            13   wire 8, bulk 5        0.0442   0.487     1 labelling,  p 1

against 0.3737, 0.4877 and 0.1159 on the deposited cohort. The regime letters
are unchanged, A B C against B B C, and the separation between MgB2-class and
the rest is wider.

One correction travels with the cohort change. Sec. III.A said the MgB2-class
cell admits three distinct labellings under the paper-clustered null and can
never return a probability below 0.33. Three is the number of ways to split its
three source papers into two non-empty groups, which does not hold the wire and
bulk sample counts at 8 and 5. Under the size-preserving null, which is what
produced the four and the ten already quoted for the two iron families, the
MgB2-class cell admits one labelling and its probability is identically 1. The
paper was applying one null to two families and a looser one to the third.

The response letter said the anchor count behind Figure 3 does not move because
no withdrawn paper appears in the anchor table. Twenty-six of the ninety-six
rows carry a withdrawal, so it does move, and the supplement already said 70.
That sentence is corrected here.

Usage:
    python3 analysis/apply_anchor_cohort_edits.py IN_DIR OUT_DIR
"""
import hashlib
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final35.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final35.docx"
RESP = "RESPONSE_TO_REFEREES_final35.docx"
OUT = {MAIN: "HT10016_revised_final36.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final36.docx",
       RESP: "RESPONSE_TO_REFEREES_final36.docx"}

FIGURE_3 = os.path.join("figures", "manuscript_figure_3.png")
# The media entry the committed document holds for Figure 3. Named explicitly
# rather than found by elimination: a lookup that takes "the one PNG that does
# not match anything in figures/" would silently pick a different image the
# moment any other figure is regenerated.
FIGURE_3_MEDIA = "word/media/3dc514a50ac7c96dd392cc226e22e9c4a2999c79.png"

EDITS = [
    # ---------------- the abstract -------------------------------------
    (MAIN,
     "and assigns two distinct regimes across the studied families: sample "
     "form explains 37% of the within-family variance in the critical-current "
     "anchor for iron chalcogenide 11-type materials, 49% for iron pnictide "
     "122-type, and 12% for MgB2-class.",

     "and assigns two distinct regimes across the studied families: on the "
     "repaired anchor cohort sample form explains 81% of the within-family "
     "variance in the critical-current anchor for iron chalcogenide 11-type "
     "materials, on five physical samples, 37% for iron pnictide 122-type on "
     "five, and 4% for MgB2-class on 13, against 37%, 49% and 12% on the "
     "anchors as deposited."),

    (MAIN,
     "Because sample form is very nearly a relabelling of source paper in "
     "this corpus, the separation between them is not established at any "
     "useful significance, and we state the measurement that would establish "
     "it.",

     "Because sample form is very nearly a relabelling of source paper in "
     "this corpus, the separation between them is not established at any "
     "useful significance: the exact permutation probability cannot fall "
     "below 0.25 for the strongest of the three families and is identically 1 "
     "for the weakest. We state the measurement that would establish it."),

    # ---------------- Sec. III.A, the clustered null --------------------
    (MAIN,
     "Under a null that shuffles the form label between papers, which is the "
     "only null that respects that structure, the MgB2-class cell admits "
     "three distinct labellings and can therefore never return a p below 0.33 "
     "however clean its separation, and the two iron-based cells admit four "
     "and ten.",

     "Under a null that shuffles the form label between papers, which is the "
     "only null that respects that structure, and that holds each form's "
     "sample count at its observed value, the MgB2-class cell admits a single "
     "labelling and therefore returns a probability of 1 however clean its "
     "separation, while the iron chalcogenide and 122-type cells admit four "
     "labellings and ten. An earlier version of this section gave three "
     "labellings and a floor of 0.33 for the MgB2-class cell, which counts "
     "the ways of splitting its three source papers into two groups without "
     "holding the wire and bulk sample counts fixed, while the four and the "
     "ten were already the size-preserving counts; the same null is now "
     "applied to all three families. The exact probabilities are 0.25 for the "
     "iron chalcogenide cell, which is its floor, 0.30 for the 122-type cell "
     "and 1 for MgB2-class, and analysis/anchor_form_permutation.py "
     "enumerates them. The iron chalcogenide ratio of 0.81 is the largest of "
     "the ten arrangements its five samples admit, so it is the cleanest "
     "separation this cohort can produce and it still cannot reach a "
     "probability below 0.25."),

    (MAIN,
     "Given the MgB2-class cohort size (n = 15 physical samples), a "
     "label-permutation test cannot distinguish this low ratio from a weak "
     "sample-form signal concealed by sampling noise (p = 0.21).",

     "Ignoring the paper structure and permuting the form label directly over "
     "physical samples, which is the more favourable of the two tests, the "
     "MgB2-class ratio gives a probability of 0.49 on the repaired cohort of "
     "13 physical samples and 0.21 on the deposited cohort of 15. Neither "
     "distinguishes this low ratio from a weak sample-form signal concealed "
     "by sampling noise."),

    # ---------------- the Figure 3 caption ------------------------------
    (MAIN,
     "Of the 96 per-paper anchor records of Table I, 56 fall in the three "
     "families shown and the remainder in families not plotted here. The 56 "
     "collapse to the 37 markers drawn, because multiple isotherms of one "
     "physical sample are averaged into a single record before plotting: 12 "
     "for iron chalcogenide 11-type, 10 for iron pnictide 122-type, and 15 "
     "for MgB2-class.",

     "The panels draw the repaired anchor cohort of Sec. III.F, the 70 of the "
     "96 per-paper anchor records of Table I that carry no withdrawal. Of "
     "those 70, 40 fall in the three families shown and the remainder in "
     "families not plotted here. The 40 collapse to the 23 markers drawn, "
     "because multiple isotherms of one physical sample are averaged into a "
     "single record before plotting: 5 for iron chalcogenide 11-type, 5 for "
     "iron pnictide 122-type, and 13 for MgB2-class."),

    (MAIN,
     "Singleton cells are flagged with n = 1.",

     "A cell holding one record is flagged n = 1 and drawn without a median "
     "bar or interquartile band, since one point has no spread to "
     "characterize; no cell of the repaired cohort holds one."),

    (MAIN,
     "The panels here plot the anchors as deposited, and the ratios quoted in "
     "this caption are therefore the deposited ones; Sec. III.A and Table III "
     "give both cohorts, and the regime assignment is the same on each.",

     "The panels here plot the repaired anchors, so the ratios shown are "
     "0.81, 0.37 and 0.04; on the anchors as deposited the same three are "
     "0.37, 0.49 and 0.12, and Sec. III.A and Table III give both cohorts. "
     "The regime assignment is the same on each. The two iron-based panels "
     "rest on five physical samples in two sample forms, and Sec. III.A gives "
     "the exact permutation probabilities that follow from that."),

    # ---------------- Table III's scope line ----------------------------
    (MAIN,
     "Variance decomposition of the per-paper critical-current anchor within "
     "each populated family; 96 per-paper anchors in total, of which 56 fall "
     "in the three families plotted.",

     "Variance decomposition of the per-paper critical-current anchor within "
     "each populated family; 96 per-paper anchors in total, of which the 70 "
     "carrying no withdrawal form the repaired cohort Fig. 3 draws, and 40 of "
     "those fall in the three families plotted."),

    # ---------------- the response letter -------------------------------
    (RESP,
     "and 96 per-paper anchors behind Figure 3.",

     "and 96 per-paper anchors behind Figure 3, of which the 70 carrying no "
     "withdrawal are the cohort the figure now draws."),

    (RESP,
     "The anchor count behind Figure 3 and the candidate compound count do "
     "not move, because no withdrawn paper appears in the anchor table and "
     "the candidate side does not depend on the anchors.",

     "The candidate compound count does not move, because the candidate side "
     "does not depend on the anchors. The anchor count does. Twenty-six of "
     "the 96 per-paper anchor rows carry a withdrawal, so Figure 3 and the "
     "diagnostic of Sec. III.A are now computed on the remaining 70 and both "
     "cohorts are reported. An earlier version of this reply said the anchor "
     "count did not move, and that was wrong."),

    (RESP,
     "so no family cell can reach a probability below 0.10 under the only "
     "null that respects that structure.",

     "so under the only null that respects that structure the iron "
     "chalcogenide cell cannot reach a probability below 0.25, the 122-type "
     "cell below 0.10, and the MgB2-class cell returns 1 whatever its "
     "separation."),

    (RESP,
     "Sample form now explains 4% of the within-family variance in this class "
     "rather than 12%, against 81% for the iron chalcogenides,",

     "Sample form now explains 4% of the within-family variance in this "
     "class rather than 12%, on 13 physical samples, against 81% for the iron "
     "chalcogenides on five,"),
]

# Table I, the anchor row. Replaced by exact cell content so a stray "96"
# elsewhere in the table cannot be hit instead.
CELL_EDITS = [
    (MAIN, "96", "70 of 96", 1),
    (MAIN, "Variance-decomposition diagnostic",
     "Variance-decomposition diagnostic. Fig. 3 draws the 70 rows carrying "
     "no withdrawal; Sec. III.A reports the diagnostic on both cohorts", 1),
]


# The display extent the committed document held for Figure 3, in EMU. The
# width is fixed at the two-column measure and the height follows the image's
# aspect ratio, so only the height is rewritten.
OLD_EXTENT_CY = "2879566"


def _set_extent(doc, png_path, old_cy):
    """Rewrite Figure 3's display height so it matches the new image.

    Returns (document, number of values rewritten). Both wp:extent and the
    a:ext inside pic:spPr carry the pair and Word uses the second, so a run
    that rewrites one and not the other leaves the figure stretched with
    nothing reporting it. The count is returned so the caller can require two.
    """
    from PIL import Image
    with Image.open(png_path) as im:
        w, h = im.size
    cx = 5715000
    cy = str(int(round(cx * h / w)))
    before = doc.count('cy="%s"' % old_cy)
    doc = doc.replace('cx="5715000" cy="%s"' % old_cy,
                      'cx="5715000" cy="%s"' % cy)
    print("   %-8s figure 3 extent cy %s -> %s (image %dx%d)"
          % ("HT10016", old_cy, cy, w, h))
    return doc, before


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_anchor_cohort_edits.py IN_DIR OUT_DIR")
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    if not os.path.exists(FIGURE_3):
        sys.exit("missing %s; run analysis/figure_4_source.py first" % FIGURE_3)
    fresh = open(FIGURE_3, "rb").read()

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

        for target, find, repl, n_expected in CELL_EDITS:
            if target != name:
                continue
            hits = [p for p in paragraphs(doc)
                    if unescape(plain(p)).strip() == find]
            if len(hits) != n_expected:
                sys.exit("%s: %d cell(s) equal %r, expected %d"
                         % (name, len(hits), find, n_expected))
            new = replace_in_paragraph(hits[0], find, repl)
            if new is None:
                sys.exit("%s: could not replace the cell %r" % (name, find))
            doc = doc.replace(hits[0], new, 1)
            print("   %-8s cell %-30s -> %s" % ("HT10016", find, repl[:40]))

        if name == MAIN:
            # The regenerated Figure 3 is a different pixel size, because
            # matplotlib saves it with bbox_inches="tight" and the panels
            # changed shape when the cohort did. The drawing's display extent
            # is stored in the document and does not follow the image, so a
            # swapped PNG leaves the figure stretched by whatever the two
            # aspect ratios differ by. analysis/check_figures.py tests this
            # and reported it, which is why it is corrected here rather than
            # left for a reader to notice.
            doc, n_ext = _set_extent(doc, FIGURE_3, OLD_EXTENT_CY)
            if n_ext != 2:
                sys.exit("%s: rewrote %d extent value(s) for Figure 3, "
                         "expected 2 (wp:extent and a:ext)" % (name, n_ext))

        swapped = False
        tmp = op + ".part"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, doc)
                elif name == MAIN and item.filename == FIGURE_3_MEDIA:
                    old = zin.read(item.filename)
                    zout.writestr(item, fresh)
                    swapped = True
                    print("   %-8s figure 3 media %s -> %s (%d -> %d bytes)"
                          % ("HT10016",
                             hashlib.sha256(old).hexdigest()[:12],
                             hashlib.sha256(fresh).hexdigest()[:12],
                             len(old), len(fresh)))
                else:
                    zout.writestr(item, zin.read(item.filename))
        zin.close()
        if name == MAIN and not swapped:
            os.remove(tmp)
            sys.exit("%s: %s is not in the document, so the regenerated "
                     "Figure 3 was not embedded" % (name, FIGURE_3_MEDIA))
        shutil.move(tmp, op)
        print("   wrote %s" % op)
    return 0


if __name__ == "__main__":
    sys.exit(main())
