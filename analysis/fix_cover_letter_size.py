#!/usr/bin/env python3
"""
fix_cover_letter_size.py

The cover letter's signature block sat at 11 pt while the body sat at 12 pt.

The Times New Roman 12 pass set the Normal style and the runs it could see, but
the cover letter also carries an 11 pt default in docDefaults and seven runs
with an explicit 11 pt size on the signature block. Word resolves those ahead
of the style, so the closing six lines printed a point smaller than the letter
above them.

This sets the document default to 12 pt and removes the explicit size from
every run that carried one, leaving the size to the style everywhere.
"""

import sys
import zipfile

import docx
from docx.oxml.ns import qn
from docx.shared import Pt


def fix(path):
    doc = docx.Document(path)
    doc.styles["Normal"].font.size = Pt(12)
    cleared = []
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            if run.font.size is not None and run.font.size.pt != 12:
                cleared.append((run.font.size.pt, run.text[:60]))
                run.font.size = None
    defaults = doc.styles.element.find(qn("w:docDefaults"))
    moved = []
    for sz in defaults.iter(qn("w:sz")):
        if sz.get(qn("w:val")) != "24":
            moved.append(int(sz.get(qn("w:val"))) / 2)
            sz.set(qn("w:val"), "24")
    for sz in defaults.iter(qn("w:szCs")):
        sz.set(qn("w:val"), "24")
    doc.save(path)
    return cleared, moved


def verify(path):
    doc = docx.Document(path)
    bad = [
        (r.font.size.pt, r.text[:40])
        for p in doc.paragraphs for r in p.runs
        if r.font.size is not None and r.font.size.pt != 12
    ]
    assert not bad, bad
    assert doc.styles["Normal"].font.size.pt == 12
    styles = zipfile.ZipFile(path).read("word/styles.xml").decode("utf8")
    head = styles.split("</w:docDefaults>")[0]
    assert 'w:sz w:val="24"' in head, "docDefaults still not 12 pt"
    assert 'w:sz w:val="22"' not in head, "an 11 pt default survives"
    return True


if __name__ == "__main__":
    for path in sys.argv[1:]:
        before = [p.text for p in docx.Document(path).paragraphs]
        cleared, moved = fix(path)
        assert [p.text for p in docx.Document(path).paragraphs] == before
        verify(path)
        print("%s: default %s -> 12.0 pt, %d run size(s) cleared"
              % (path.split("/")[-1], moved or "already 12", len(cleared)))
        for size, text in cleared:
            print("    %.1f pt  %s" % (size, text))
