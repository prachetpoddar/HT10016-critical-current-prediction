#!/usr/bin/env python3
"""
strip_highlights.py

Remove every yellow mark from a .docx, in every place a mark can live.

The clean deliverable was found carrying 93 of them. 86 sat on paragraph
marks, in w:p/w:pPr/w:rPr, where they render as a yellow block at the end of
the line, 78 of those on otherwise blank lines. The other 7 sat inside the
OMML of one inline equation, 5 on m:r runs and 2 on m:ctrlPr. None of them
came from the marking pass: they are what the lost toolchain left behind, and
the marking pass could not reach them, because its clear step iterated w:r
and a paragraph mark is not a w:r.

So the clear step is replaced by this one, which walks the XML of every part
rather than the paragraph objects of one, and asserts afterwards that nothing
is left.
"""

import shutil
import sys
import zipfile

from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PARTS = ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml")


def _is_part(name):
    return (name in PARTS
            or name.startswith("word/header")
            or name.startswith("word/footer")) and name.endswith(".xml")


def count(path):
    """Every w:highlight in every part of the file, whatever its colour."""
    n = 0
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not _is_part(name):
                continue
            n += len(etree.fromstring(z.read(name)).findall(".//" + W + "highlight"))
    return n


def strip(src, dst=None, drop_page_breaks=False):
    """Write src with every w:highlight removed. Returns how many went.

    drop_page_breaks also removes w:lastRenderedPageBreak, Word's cache of
    where the pages fell when it last laid the file out. Word rebuilds it on
    open. It is removed before marking because it is the one element that
    sits inside a run alongside text, so splitting that run to mark half of
    it would deep-copy the break and leave two.
    """
    dst = dst or src
    removed = 0
    with zipfile.ZipFile(src) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    out = []
    for info, data in items:
        if _is_part(info.filename):
            root = etree.fromstring(data)
            hits = root.findall(".//" + W + "highlight")
            for h in hits:
                h.getparent().remove(h)
            removed += len(hits)
            if drop_page_breaks:
                for b in root.findall(".//" + W + "lastRenderedPageBreak"):
                    b.getparent().remove(b)
            data = etree.tostring(root, xml_declaration=True,
                                  encoding="UTF-8", standalone=True)
        out.append((info, data))
    tmp = str(dst) + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in out:
            z.writestr(info, data)
    shutil.move(tmp, dst)
    assert count(dst) == 0, "a mark survived the strip"
    return removed


if __name__ == "__main__":
    for p in sys.argv[1:]:
        before = count(p)
        print("%s: %d marks, removed %d" % (p, before, strip(p)))
