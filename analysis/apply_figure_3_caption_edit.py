"""
apply_figure_3_caption_edit.py

Say which anchor cohort Figure 3 plots.

Figure 3 is drawn on the anchors as deposited, and its ratios are 0.37, 0.49
and 0.12. Until 2026-09-06 Table III reported the same three as the result of
that claim, so the figure and the table agreed and neither had to name a
cohort. Table III now leads with the repaired 0.81, 0.37 and 0.04, because
Sec. III.A does. That leaves Figure 3 showing three different numbers with
nothing in its caption to say why.

The caption's closing sentence made it worse. It said the diagnostic is
"independent of the field-axis issues discussed in Sec. III.F", which is true
of the magnetic-field unit repair and false of the anchor repair in the same
section: that repair withdraws 26 of these 96 records and rescales 15.

Usage:
    python3 analysis/apply_figure_3_caption_edit.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final20.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final20.docx"
RESP = "RESPONSE_TO_REFEREES_final20.docx"
OUT = {MAIN: "HT10016_revised_final21.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final21.docx",
       RESP: "RESPONSE_TO_REFEREES_final21.docx"}

EDITS = [(
    MAIN,
    "The quantity plotted is the critical-current anchor, which uses neither "
    "a fitted exponent nor an upper-critical-field scale, so this diagnostic "
    "is independent of the field-axis issues discussed in Sec. III.F.",
    "The quantity plotted is the critical-current anchor, which uses neither "
    "a fitted exponent nor an upper-critical-field scale, so it is unaffected "
    "by the magnetic-field unit repair of Sec. III.F. The anchor repair of "
    "that same section is a separate matter and does reach these records: it "
    "withdraws 26 of the 96 and rescales 15. The panels here plot the anchors "
    "as deposited, and the ratios quoted in this caption are therefore the "
    "deposited ones; Sec. III.A and Table III give both cohorts, and the "
    "regime assignment is the same on each.")]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_figure_3_caption_edit.py IN_DIR OUT_DIR")
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
                sys.exit("%s: %d paragraph(s) carry the Fig. 3 sentence, "
                         "expected exactly 1" % (name, len(hits)))
            new = replace_in_paragraph(hits[0], find, repl)
            if new is None:
                sys.exit("%s: could not place the replacement" % name)
            doc = doc.replace(hits[0], new, 1)
            print("   %-32s Fig. 3 caption, the plotted cohort" % name[:30])
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
