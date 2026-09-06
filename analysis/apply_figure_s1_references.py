"""
apply_figure_s1_references.py

Cites Supplemental Figure S1, which the previous step embedded.

A figure nothing refers to is close to a figure that is not there. Section 15
now opens by saying what the section contains and does not mention the figure
sitting inside it, and the response letter tells Referee A that the section
reproduces rows from three files without saying that it also draws the curves
those rows came from, which is closer to what the referee asked for.

Two edits, one in each document.

Usage:
    python3 analysis/apply_figure_s1_references.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final31.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final31.docx"
RESP = "RESPONSE_TO_REFEREES_final31.docx"
OUT = {MAIN: "HT10016_revised_final32.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final32.docx",
       RESP: "RESPONSE_TO_REFEREES_final32.docx"}

EDITS = [
    (SUPP,
     "Referee A asked for examples of the extracted data. This section "
     "reproduces verbatim rows from three of the deposited files so that the "
     "schema, the provenance labels, and the refusal accounting can be "
     "inspected without downloading the deposit.",

     "Referee A asked for examples of the extracted data. This section "
     "reproduces verbatim rows from three of the deposited files so that the "
     "schema, the provenance labels, and the refusal accounting can be "
     "inspected without downloading the deposit, and Fig. S1 shows the curves "
     "behind three such records with the fit each one produced, so that the "
     "extraction, the fitting window and the fit can be checked against each "
     "other by eye. Its three panels are a retained record, a record whose fit "
     "runs to the applicability bound, and a withdrawn one."),

    (RESP,
     "New Section 15 reproduces rows verbatim from three files:",

     "New Section 15 reproduces rows verbatim from three files, and opens with "
     "Fig. S1, which plots the extracted curve, the fitting window and the "
     "resulting fit for one retained record, one that runs to the "
     "applicability bound, and one we withdrew, so that the three outcomes can "
     "be compared directly. The tables are:"),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_figure_s1_references.py IN_DIR OUT_DIR")
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
