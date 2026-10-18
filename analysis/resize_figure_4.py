#!/usr/bin/env python3
"""
resize_figure_4.py

Figure 4 at 60% per axis of the width it was given on 2026-10-18.

Hossain asked for it smaller twice. The first pass took it from 6.25 to 4.60
inches wide; this takes it to 0.60 of that on each axis, 2.76 by 2.60 inches,
keeping the image's own aspect ratio so check_figures.py still passes.

The figure's paragraph is already centre-aligned, as all five are, so nothing
has to be done to keep it centred on the page. The pass asserts that rather
than assuming it.

Worth knowing: the figure is drawn at 3.5 inches wide in
analysis/manuscript_figure_4.py, so at 2.76 inches its 8.6 pt axis labels set
at about 6.8 pt on the page. That is small but inside what journals print.
Below roughly 2.4 inches they would fall under 6 pt.
"""

import sys

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Emu, Inches
from PIL import Image

TARGETS = ("out_final60/HT10016_revised_final60.docx",
           "out_final60/HT10016_revised_final60_HIGHLIGHTED.docx")

FIG4 = "figures/figure_4_anchor_count.png"
SCALE = 0.60
WAS_IN = 4.60
WIDTH_IN = round(WAS_IN * SCALE, 3)


def ratio():
    with Image.open(FIG4) as im:
        return im.size[0] / im.size[1]


def figure_4(doc):
    want = ratio()
    hits = [s for s in doc.inline_shapes
            if abs(s.width / s.height - want) < 0.01]
    assert len(hits) == 1, len(hits)
    return hits[0]


def paragraph_of(doc, shape):
    for p in doc.paragraphs:
        if shape._inline in p._p.iter(shape._inline.tag):
            return p
    raise ValueError("the drawing is in no paragraph")


def apply(path):
    doc = docx.Document(path)
    shape = figure_4(doc)
    before = (shape.width.inches, shape.height.inches)
    width = Inches(WIDTH_IN)
    shape.width = width
    shape.height = Emu(int(round(width / ratio())))
    paragraph = paragraph_of(doc, shape)
    if paragraph.alignment != WD_ALIGN_PARAGRAPH.CENTER:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.save(path)
    return before, (shape.width.inches, shape.height.inches)


def verify(path):
    doc = docx.Document(path)
    shape = figure_4(doc)
    assert abs(shape.width.inches - WIDTH_IN) < 0.005, shape.width.inches
    assert abs(shape.width / ratio() - shape.height) <= 1
    paragraph = paragraph_of(doc, shape)
    assert paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER, paragraph.alignment
    assert paragraph.paragraph_format.left_indent in (None, 0)
    # the other four keep their width. python-docx builds a new InlineShape
    # on every access, so identity cannot pick Figure 4 out; its aspect ratio
    # can, and it is the only drawing that carries it.
    others = [round(s.width.inches, 2) for s in doc.inline_shapes
              if abs(s.width / s.height - ratio()) >= 0.01]
    assert others == [6.25, 6.25, 6.25, 6.25], others
    rid = shape._inline.graphic.graphicData.pic.blipFill.blip.embed
    assert doc.part.related_parts[rid].blob == open(FIG4, "rb").read()


if __name__ == "__main__":
    for path in TARGETS:
        text = [p.text for p in docx.Document(path).paragraphs]
        was, now = apply(path)
        verify(path)
        assert [p.text for p in docx.Document(path).paragraphs] == text
        print("%-46s Figure 4 %.2f x %.2f -> %.2f x %.2f in, centred"
              % (path.split("/")[-1], was[0], was[1], now[0], now[1]))
