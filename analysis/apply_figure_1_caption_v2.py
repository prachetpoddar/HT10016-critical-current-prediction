"""
apply_figure_1_caption_v2.py

The Fig. 1 caption again, for the panels the figure now has.

Two of its sentences went stale in the same session that wrote them. Panel (b)
said the conditioning claim rests on the variance-decomposition diagnostic,
which was true of the caption when it was written and false four edits later,
after Sec. III.A was repaired to say the claim rests on the temperature-axis
separation. Panel (c) said its three circles are how the five refusal codes
group; the panel now carries the gate Venn of Sec. II.D, which shows three of
those codes and does not claim to partition them.

Usage:
    python3 analysis/apply_figure_1_caption_v2.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final18.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final18.docx"
RESP = "RESPONSE_TO_REFEREES_final18.docx"
OUT = {MAIN: "HT10016_revised_final20.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final20.docx",
       RESP: "RESPONSE_TO_REFEREES_final20.docx"}

FIND = ("(b) The three aggregation scopes, the per-axis expression they fit, "
        "and the variance-decomposition diagnostic; the conditioning claim "
        "rests on that diagnostic and not on the comparison between stages, "
        "for the reasons given in Sec. III.A. (c) The three conditions a "
        "prediction target satisfies to be dispatched, which is how the five "
        "refusal codes group, with the reduced-variable scaling result and "
        "the dispatch outcome.")

REPL = ("(b) The per-axis expression, the three scopes at which its exponents "
        "are aggregated, prototype structures of the four substructure "
        "families, and the sample-form diagnostic that sets the conditioning "
        "rule the predictor follows; the conditioning claim itself rests on "
        "the temperature-axis separation of Sec. III.C rather than on that "
        "diagnostic, for the reasons given in Sec. III.A. (c) Three of the "
        "gates a prediction target passes to be dispatched, the "
        "reduced-variable scaling result, a family-scope envelope with its "
        "bootstrap interval, and the dispatch outcome.")

EDITS = [(MAIN, FIND, REPL)]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_figure_1_caption_v2.py IN_DIR OUT_DIR")
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
                sys.exit("%s: %d paragraph(s) carry the Fig. 1 panel "
                         "sentences, expected exactly 1" % (name, len(hits)))
            new = replace_in_paragraph(hits[0], find, repl)
            if new is None:
                sys.exit("%s: could not place the replacement" % name)
            doc = doc.replace(hits[0], new, 1)
            print("   %-32s Fig. 1 caption, panels (b) and (c)" % name[:30])
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
