#!/usr/bin/env python3
"""
apply_hossain_format.py

The formatting items from Hossain's review of the final60 set.

  1. Figure 4 is drawn smaller. It carries less than the others and was the
     largest thing in the paper at 6.25 by 5.89 inches. It goes to 4.60 inches
     wide, keeping its own aspect ratio, which check_figures.py asserts.
  2. Figure 4's axis labels take an initial capital. That is done in
     analysis/manuscript_figure_4.py, and this pass embeds the regenerated
     PNG so the document and figures/figure_4_anchor_count.png stay identical.
  3. The manuscript tables get visible borders. They carried the two-rule
     journal style, a double rule above and below and nothing else. They now
     carry a single rule on every edge and between every cell, which is what
     the Supplemental Material tables already use.
  4. Table text drops one point. The manuscript tables inherit 12 pt and go to
     11; the Supplemental Material rows already set at 10.5 go to 9.5.

Sizes are set on the run rather than the style, because the tables mix
inherited and explicit sizes and only an explicit value on every run makes the
result the same in both.
"""

import copy
import sys

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

FIG4 = "figures/figure_4_anchor_count.png"
# Superseded the same day by analysis/resize_figure_4.py, which takes it to
# 0.60 of that on each axis. Kept in step so a rerun does not undo it.
FIG4_WIDTH_IN = 2.76
EDGES = ("top", "left", "bottom", "right", "insideH", "insideV")


def aspect(path):
    from PIL import Image
    with Image.open(path) as im:
        return im.size[0] / im.size[1]


def resize_and_replace_figure_4(doc):
    """Swap in the regenerated PNG and set the display extent."""
    target = open(FIG4, "rb").read()
    ratio = aspect(FIG4)
    width = Inches(FIG4_WIDTH_IN)
    height = Inches(FIG4_WIDTH_IN / ratio)
    hit = None
    for shape in doc.inline_shapes:
        rid = shape._inline.graphic.graphicData.pic.blipFill.blip.embed
        part = doc.part.related_parts[rid]
        # Figure 4 is the one whose stored image is the anchor-count figure,
        # identified by its aspect ratio among the five. Checked below.
        if abs(shape.width / shape.height - ratio) < 0.01 and shape.width > 0:
            if hit is not None:
                raise ValueError("two shapes share Figure 4's aspect ratio")
            hit = (shape, part)
    if hit is None:
        raise ValueError("Figure 4 not found by aspect ratio")
    shape, part = hit
    part._blob = target
    part.blob  # touch, so a stale cached blob would raise here
    shape.width, shape.height = width, height
    return shape


def border_element(sz=4):
    borders = OxmlElement("w:tblBorders")
    for edge in EDGES:
        e = OxmlElement("w:%s" % edge)
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(sz))
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), "000000")
        borders.append(e)
    return borders


def give_borders(table):
    pr = table._tbl.find(qn("w:tblPr"))
    if pr is None:
        pr = OxmlElement("w:tblPr")
        table._tbl.insert(0, pr)
    old = pr.find(qn("w:tblBorders"))
    if old is not None:
        pr.remove(old)
    pr.append(border_element())


def shrink_table_text(table, inherited):
    """One point off every run. A run with no size of its own inherits the
    document's 12 pt, so it is written out at `inherited` - 1."""
    changed = 0
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    now = run.font.size.pt if run.font.size else inherited
                    run.font.size = Pt(now - 1)
                    changed += 1
    return changed


def manuscript(path):
    doc = docx.Document(path)
    before = [p.text for p in doc.paragraphs]
    shape = resize_and_replace_figure_4(doc)
    runs = 0
    for table in doc.tables:
        give_borders(table)
        runs += shrink_table_text(table, 12.0)
    doc.save(path)
    assert [p.text for p in docx.Document(path).paragraphs] == before
    return shape.width.inches, shape.height.inches, len(doc.tables), runs


def supplement(path):
    doc = docx.Document(path)
    before = [p.text for p in doc.paragraphs]
    runs = 0
    for table in doc.tables:
        give_borders(table)
        runs += shrink_table_text(table, 12.0)
    doc.save(path)
    assert [p.text for p in docx.Document(path).paragraphs] == before
    return len(doc.tables), runs


def verify(path, expect_figure):
    doc = docx.Document(path)
    for table in doc.tables:
        pr = table._tbl.find(qn("w:tblPr"))
        borders = pr.find(qn("w:tblBorders"))
        assert borders is not None, "a table has no borders"
        got = {
            b.tag.split("}")[1]: b.get(qn("w:val")) for b in borders
        }
        assert set(got) == set(EDGES), got
        assert set(got.values()) == {"single"}, got
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        assert run.font.size is not None, "a run kept no size"
                        assert run.font.size.pt <= 11.0, run.font.size.pt
    if expect_figure:
        ratio = aspect(FIG4)
        found = [
            s for s in doc.inline_shapes
            if abs(s.width / s.height - ratio) < 0.01
        ]
        assert len(found) == 1, len(found)
        got = found[0].width.inches
        assert abs(got - FIG4_WIDTH_IN) < 0.01, got
        rid = found[0]._inline.graphic.graphicData.pic.blipFill.blip.embed
        assert doc.part.related_parts[rid].blob == open(FIG4, "rb").read()


if __name__ == "__main__":
    for path in ("out_final60/HT10016_revised_final60.docx",
                 "out_final60/HT10016_revised_final60_HIGHLIGHTED.docx"):
        w, h, n, runs = manuscript(path)
        verify(path, True)
        print("%-46s Fig. 4 %.2f x %.2f in, %d tables bordered, %d runs resized"
              % (path.split("/")[-1], w, h, n, runs))
    for path in ("out_final60/SUPPLEMENTAL_MATERIAL_revised_final60.docx",
                 "out_final60/SUPPLEMENTAL_MATERIAL_revised_final60_HIGHLIGHTED.docx"):
        n, runs = supplement(path)
        verify(path, False)
        print("%-46s %d tables bordered, %d runs resized"
              % (path.split("/")[-1], n, runs))
