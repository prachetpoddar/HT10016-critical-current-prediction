#!/usr/bin/env python3
"""
apply_paragraph_spacing.py

One empty paragraph between every pair of adjacent paragraphs, Hossain's
sixth formatting item, including across a section heading.

Two parts of each document are left alone, because a blank line there is not
spacing but damage:

  front matter   the title, the author line, the five affiliations and the
                 contact line are one block, not eight paragraphs of prose.
                 Insertion starts at the first paragraph after it.
  references     45 entries that no journal sets with a blank line between
                 them. Insertion stops at the REFERENCES heading.

The two letters are not touched. Their missing blanks are in the address and
signature blocks, where the same argument applies to the whole document.

A table counts as a separator: a paragraph that follows one already has
something between it and the paragraph before, so nothing is inserted there.
The inserted paragraph takes the style of the paragraph it precedes, so it
occupies one line at that paragraph's size rather than the document default.

"Exactly one" cuts both ways, so a run of two or more blank paragraphs inside
the active range is collapsed to one. The Supplemental Material carried
several. Both halves are idempotent, so the pass can be run again safely.
"""

import sys

import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

P = qn("w:p")


def text_of(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t"))).strip()


def insert_blanks(path, start_after, stop_at):
    doc = docx.Document(path)
    body = doc.element.body
    children = list(body)
    started = start_after is None
    previous = None
    inserted = 0
    for node in children:
        if node.tag != P:
            previous = None          # a table separates two paragraphs
            continue
        text = text_of(node)
        if not started:
            if text.startswith(start_after):
                started = True
            previous = node if text else None
            continue
        if stop_at and text.upper().startswith(stop_at):
            break
        if text and previous is not None:
            blank = OxmlElement("w:p")
            pPr = node.find(qn("w:pPr"))
            if pPr is not None:
                blank.append(pPr.__copy__())
            node.addprevious(blank)
            inserted += 1
        previous = node if text else None
    removed = collapse(body, start_after, stop_at)
    doc.save(path)
    return inserted, removed


def collapse(body, start_after, stop_at):
    """Leave at most one blank paragraph in any run of them."""
    started = start_after is None
    run = []
    removed = 0
    for node in list(body):
        if node.tag != P:
            run = []
            continue
        text = text_of(node)
        if not started:
            if text.startswith(start_after):
                started = True
            continue
        if stop_at and text.upper().startswith(stop_at):
            break
        if text:
            run = []
            continue
        run.append(node)
        if len(run) > 1:
            body.remove(node)
            run.pop()
            removed += 1
    return removed


def verify(path, start_after, stop_at):
    doc = docx.Document(path)
    body = doc.element.body
    started = start_after is None
    previous = None
    bad = []
    for node in body:
        if node.tag != P:
            previous = None
            continue
        text = text_of(node)
        if not started:
            if text.startswith(start_after):
                started = True
            previous = node if text else None
            continue
        if stop_at and text.upper().startswith(stop_at):
            break
        if text and previous is not None:
            bad.append(text[:60])
        if text and previous is None:
            previous = node
        elif not text:
            previous = None
    assert not bad, bad
    # and never two blanks in a row
    runs = 0
    for node in body:
        if node.tag != P:
            runs = 0
            continue
        if text_of(node):
            runs = 0
        else:
            runs += 1
            assert runs < 2, "two blank paragraphs in a row"


JOBS = [
    ("out_final60/HT10016_revised_final60.docx", "ABSTRACT", "REFERENCES"),
    ("out_final60/HT10016_revised_final60_HIGHLIGHTED.docx",
     "ABSTRACT", "REFERENCES"),
    ("out_final60/SUPPLEMENTAL_MATERIAL_revised_final60.docx", "1.", None),
    ("out_final60/SUPPLEMENTAL_MATERIAL_revised_final60_HIGHLIGHTED.docx",
     "1.", None),
]


if __name__ == "__main__":
    for path, start, stop in JOBS:
        before = [p.text for p in docx.Document(path).paragraphs if p.text.strip()]
        n, removed = insert_blanks(path, start, stop)
        after = [p.text for p in docx.Document(path).paragraphs if p.text.strip()]
        assert before == after, "the text changed"
        verify(path, start, stop)
        print("%-54s %3d inserted, %d extra blank(s) removed"
              % (path.split("/")[-1], n, removed))
