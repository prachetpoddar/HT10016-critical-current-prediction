#!/usr/bin/env python3
"""
clear_blank_line_marks.py

Remove a mark on the paragraph mark of an EMPTY paragraph.

A w:highlight in w:p/w:pPr/w:rPr colours the paragraph mark, which Word
draws as a yellow block at the end of the line. On a paragraph with text it
is the ordinary consequence of highlighting a quoted passage through to its
end. On an empty paragraph there is nothing but the block, and the reader
sees a yellow smear on a blank line.

The response letter carries three of them, on the blank separators at
paragraphs 84, 131 and 177. The marks on its quoted passages are the
authors' own and are left alone.
"""

import shutil
import sys
import zipfile

from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def blanks_marked(path):
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read("word/document.xml"))
    out = []
    for i, p in enumerate(root.iter(W + "p")):
        if "".join(t.text or "" for t in p.iter(W + "t")).strip():
            continue
        pPr = p.find(W + "pPr")
        rPr = None if pPr is None else pPr.find(W + "rPr")
        if rPr is not None and rPr.find(W + "highlight") is not None:
            out.append(i)
    return out


def clear(path):
    with zipfile.ZipFile(path) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    removed = 0
    out = []
    for info, data in items:
        if info.filename == "word/document.xml":
            root = etree.fromstring(data)
            for p in root.iter(W + "p"):
                if "".join(t.text or "" for t in p.iter(W + "t")).strip():
                    continue
                pPr = p.find(W + "pPr")
                rPr = None if pPr is None else pPr.find(W + "rPr")
                if rPr is None:
                    continue
                for h in rPr.findall(W + "highlight"):
                    rPr.remove(h)
                    removed += 1
            data = etree.tostring(root, xml_declaration=True,
                                  encoding="UTF-8", standalone=True)
        out.append((info, data))
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in out:
            z.writestr(info, data)
    shutil.move(tmp, path)
    assert not blanks_marked(path), "a blank-line mark survived"
    return removed


if __name__ == "__main__":
    for p in sys.argv[1:]:
        before = blanks_marked(p)
        print("%s: %d blank lines marked, removed %d"
              % (p, len(before), clear(p)))
