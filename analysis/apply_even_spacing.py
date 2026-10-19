#!/usr/bin/env python3
"""
apply_even_spacing.py

Make the vertical spacing even.

The documents carry nine different space-before and space-after combinations
on paragraphs that are otherwise alike, because every pass that inserted a
paragraph copied the properties of whichever paragraph it stood next to. Most
of the variation is on the EMPTY separator paragraphs, which should contribute
one line and nothing else: one of them carried a heading's 24 pt before and
12 pt after, several carried an equation's 12 and 12, and one carried a table
caption's 18 and 7. An empty paragraph with heading spacing prints as a gap
the size of a heading.

What this does NOT flatten is the spacing that belongs to a class of
paragraph and is already uniform within it: 6 pt after on the 46 reference
entries, 12 and 12 on the 22 equation lines, 18 and 7 on the 8 table
captions, 12 and 6 on the 5 figure images, 2 pt after on the affiliations.
Those are the typography, not the unevenness.

Two single outliers are brought into line with their own class:

  Figure 2's caption had no space after it where the other four captions
  have 18 pt;

  one Heading 1 was left-aligned where the other eleven are centred.

Line spacing is already 1.15 everywhere and is asserted rather than set.
"""

import sys

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

TARGETS = ["out_final60/HT10016_revised_final60.docx",
           "out_final60/HT10016_revised_final60_HIGHLIGHTED.docx",
           "out_final60/SUPPLEMENTAL_MATERIAL_revised_final60.docx",
           "out_final60/SUPPLEMENTAL_MATERIAL_revised_final60_HIGHLIGHTED.docx"]

CAPTION_AFTER = 18.0


def neutralise_blanks(doc):
    """An empty paragraph contributes one line and nothing else."""
    changed = 0
    for p in doc.paragraphs:
        if p.text.strip():
            continue
        f = p.paragraph_format
        touched = False
        if p.style.name != "Normal":
            p.style = doc.styles["Normal"]
            touched = True
        if f.space_before is not None:
            f.space_before = None
            touched = True
        if f.space_after is not None:
            f.space_after = None
            touched = True
        if f.alignment is not None:
            f.alignment = None
            touched = True
        changed += touched
    return changed


def even_captions(doc):
    caps = [p for p in doc.paragraphs if p.text.strip().startswith("FIG. ")]
    if not caps:
        return 0
    changed = 0
    for p in caps:
        f = p.paragraph_format
        if f.space_after is None or f.space_after.pt != CAPTION_AFTER:
            f.space_after = Pt(CAPTION_AFTER)
            changed += 1
    return changed


def even_headings(doc):
    changed = 0
    for p in doc.paragraphs:
        if not p.style.name.startswith("Heading") or not p.text.strip():
            continue
        if p.alignment != WD_ALIGN_PARAGRAPH.CENTER:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            changed += 1
    return changed


def verify(path):
    doc = docx.Document(path)
    for p in doc.paragraphs:
        f = p.paragraph_format
        if not p.text.strip():
            assert p.style.name == "Normal", p.style.name
            assert f.space_before is None and f.space_after is None
            assert f.alignment is None
        if p.text.strip().startswith("FIG. "):
            assert f.space_after is not None
            assert f.space_after.pt == CAPTION_AFTER, f.space_after.pt
        if p.style.name.startswith("Heading") and p.text.strip():
            assert p.alignment == WD_ALIGN_PARAGRAPH.CENTER, p.text[:30]
    # one line spacing throughout
    spacings = {p.paragraph_format.line_spacing for p in doc.paragraphs
                if p.paragraph_format.line_spacing is not None}
    assert len(spacings) <= 1, spacings


if __name__ == "__main__":
    for path in TARGETS:
        doc = docx.Document(path)
        before = [p.text for p in doc.paragraphs]
        blanks = neutralise_blanks(doc)
        caps = even_captions(doc)
        heads = even_headings(doc)
        doc.save(path)
        assert [p.text for p in docx.Document(path).paragraphs] == before
        verify(path)
        print("%-54s %3d blank(s) neutralised, %d caption(s), %d heading(s)"
              % (path.split("/")[-1], blanks, caps, heads))
