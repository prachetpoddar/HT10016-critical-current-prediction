"""
apply_figure_1_caption_edit.py

Bring the Fig. 1 caption into line with the redrawn figure.

Figure 1 was two panels, a corpus funnel and a per-family dispatch bar chart.
It is now the three-panel overview of the reference layout: the funnel, the
aggregation and the diagnostic that carries the conditioning claim, and the
bounded dispatch scope. The caption still described the old panels, and a
caption that names panels the figure does not have is worse than no caption.

The rest of the caption is left alone. It is correct and it carries the
counts, which the figure and Table I already agree on through
analysis/figure_counts.py.

Usage:
    python3 analysis/apply_figure_1_caption_edit.py IN_DIR OUT_DIR
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain, replace_in_paragraph,  # noqa: E402
                                        unescape)
import shutil                                                    # noqa: E402
import zipfile                                                   # noqa: E402

MAIN = "HT10016_revised_final15.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final15.docx"
RESP = "RESPONSE_TO_REFEREES_final15.docx"
OUT = {MAIN: "HT10016_revised_final16.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final16.docx",
       RESP: "RESPONSE_TO_REFEREES_final16.docx"}

FIND = ("(a) The path from the retrieval corpus to the cohorts that carry "
        "each fitted quantity, with the count at every stage. (b) Candidate "
        "dispatch by substructure family, showing for each family how many "
        "of its candidate compounds receive at least one emitted prediction "
        "and how many are refused, with the gate that refused them.")

REPL = ("(a) The path from the retrieval corpus to the cohorts that carry "
        "each fitted quantity, with the count at every stage and the three "
        "screens a published curve passes on the way. (b) The three "
        "aggregation scopes, the per-axis expression they fit, and the "
        "variance-decomposition diagnostic; the conditioning claim rests on "
        "that diagnostic and not on the comparison between stages, for the "
        "reasons given in Sec. III.A. (c) The three conditions a prediction "
        "target satisfies to be dispatched, which is how the five refusal "
        "codes group, with the reduced-variable scaling result and the "
        "dispatch outcome.")

EDITS = [(MAIN, FIND, REPL)]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_figure_1_caption_edit.py IN_DIR OUT_DIR")
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
                sys.exit("%s: %d paragraph(s) contain the Fig. 1 panel "
                         "sentences, expected exactly 1" % (name, len(hits)))
            new = replace_in_paragraph(hits[0], find, repl)
            if new is None:
                sys.exit("%s: could not place the replacement" % name)
            doc = doc.replace(hits[0], new, 1)
            print("   %-30s Fig. 1 caption panels (a), (b), (c)" % name[:28])
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
