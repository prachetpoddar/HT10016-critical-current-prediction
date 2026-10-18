#!/usr/bin/env python3
"""
apply_paragraph_splits.py

Hossain's ceiling of ten lines per paragraph, applied to the manuscript body.

Run as two steps, repeated until the planner finds nothing left to do, since
a piece renders a little longer than the share of the original paragraph it
was cut from and a 19-line paragraph cut in two can leave an 11-line half:

    python3 analysis/plan_paragraph_splits.py <docx> <plan.json>
    python3 analysis/apply_paragraph_splits.py [supplement] <plan.json>

The manuscript converged in three passes and the Supplemental Material in
two. The plan file is a working file and is not deposited.

Measuring this needs the rendered page rather than a character count, so the
break points come from analysis/plan_paragraph_splits.py, which renders the
document, counts the lines each paragraph actually occupies, and partitions
its sentences so that no piece exceeds ten lines. That planner also chooses
WHERE to break: among the partitions that fit, it prefers the ones whose new
paragraphs do not open on a bare referent, since a paragraph beginning "It
also requires" has lost its subject the moment a blank line sits above it.
One break could not be placed that way and its opening sentence is rewritten
here, in REWRITES, before the split runs.

The floor of five lines is deliberately not applied. It would reverse the
flow pass of 9 October, which kept eighteen short declaratives on purpose,
and most of the paragraphs under five lines are reference entries or the
numbered steps of the inference procedure, where padding to five lines would
be worse than leaving them.

The split works on the paragraph's own children rather than on its runs,
because python-docx reports a hyperlink's text in paragraph.text but not in
paragraph.runs, and the data-availability paragraph carries one. A run that
straddles the break is divided with its properties copied, so a highlighted
passage stays highlighted on both sides.
"""

import copy
import json
import re
import sys

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.path.insert(0, "analysis")
from runs import replace  # noqa: E402

PLAN = "/tmp/paragraph_splits.json"
MANUSCRIPT = ("out_final60/HT10016_revised_final60.docx",
              "out_final60/HT10016_revised_final60_HIGHLIGHTED.docx")
SUPPLEMENT = ("out_final60/SUPPLEMENTAL_MATERIAL_revised_final60.docx",
              "out_final60/SUPPLEMENTAL_MATERIAL_revised_final60_HIGHLIGHTED.docx")

# The one break the planner could not place away from a bare referent. "Their"
# refers to the two candidates named in the sentence above, which is now the
# last sentence of the paragraph before.
REWRITES = [(
    "Their transition-temperature anchors of 1.5 and 3.4 K fall far below the "
    "8.0 to 14.5 K anchors of the family's calibration cohort.",
    "The two candidates carry transition-temperature anchors of 1.5 and "
    "3.4 K, far below the 8.0 to 14.5 K anchors of the family's calibration "
    "cohort.",
)]

# Three breaks from the later passes left a paragraph opening on a referent
# whose antecedent had moved into the paragraph above. The planner avoids this
# where a partition allows it; these three had no alternative that also held
# the ten-line ceiling, so the opening phrase names its subject instead.
OPENINGS = [
    ("They take Hc2,0 from the compiled reference table",
     "They take ", "Those two tests take "),
    ("These refusals do not remove the compounds from the workflow",
     "These refusals ", "The field-axis refusals "),
    ("These six predictions are excluded from every total",
     "These six predictions ", "The six screened predictions "),
]

TEXTY = (qn("w:r"), qn("w:hyperlink"))


def child_text(node):
    return "".join(t.text or "" for t in node.iter(qn("w:t")))


def para_text(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))


def set_run_text(r, text):
    for t in r.findall(qn("w:t")):
        r.remove(t)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)


def split_paragraph(p, offset):
    """Break p at `offset` characters, returning the new paragraph element."""
    new = OxmlElement("w:p")
    pPr = p.find(qn("w:pPr"))
    if pPr is not None:
        new.append(copy.deepcopy(pPr))
    pos = 0
    moving = []
    for node in list(p):
        if node.tag not in TEXTY:
            continue
        text = child_text(node)
        start, stop = pos, pos + len(text)
        pos = stop
        if moving:
            moving.append(node)
            continue
        if stop <= offset:
            continue
        if start == offset:
            moving.append(node)
            continue
        # the break falls inside this child
        if node.tag != qn("w:r"):
            raise ValueError("the break falls inside a hyperlink")
        head = text[: offset - start]
        tail = text[offset - start:]
        tailrun = copy.deepcopy(node)
        set_run_text(node, head)
        set_run_text(tailrun, tail)
        node.addnext(tailrun)
        moving.append(tailrun)
    if not moving:
        raise ValueError("offset %d is past the end of the paragraph" % offset)
    for node in moving:
        p.remove(node)
        new.append(node)
    p.addnext(new)
    trim_edges(p, new)
    blank = OxmlElement("w:p")
    if pPr is not None:
        blank.append(copy.deepcopy(pPr))
    p.addnext(blank)
    return new


def trim_edges(first, second):
    last = [n for n in first if n.tag in TEXTY]
    if last:
        ts = last[-1].findall(qn("w:t")) or list(last[-1].iter(qn("w:t")))
        if ts:
            ts[-1].text = (ts[-1].text or "").rstrip()
    head = [n for n in second if n.tag in TEXTY]
    if head:
        ts = head[0].findall(qn("w:t")) or list(head[0].iter(qn("w:t")))
        if ts:
            ts[0].text = (ts[0].text or "").lstrip()


def body_paragraphs(doc):
    return [p for p in doc.paragraphs if p.text.strip()]


def apply(path, plan, rewrites, openings):
    doc = docx.Document(path)
    for old, new in rewrites:
        hit = [p for p in doc.paragraphs if old in p.text]
        if not hit:
            # already applied on an earlier pass; the planner runs more than
            # once because a split piece renders a little longer than the
            # share of the original paragraph it was cut from
            assert any(new in p.text for p in doc.paragraphs), path
            continue
        assert len(hit) == 1, (path, len(hit))
        replace(hit[0], old, new)
    for probe, was, now in openings:
        hit = [p for p in doc.paragraphs if p.text.strip().startswith(probe)]
        if not hit:
            assert any(p.text.strip().startswith(now + probe[len(was):])
                       for p in doc.paragraphs), probe
            continue
        assert len(hit) == 1, (probe[:40], len(hit))
        replace(hit[0], was, now)
    doc.save(path)

    doc = docx.Document(path)
    done = 0
    for entry in plan:
        opening = entry["sentences"][0][:80]
        hit = [p for p in doc.paragraphs if p.text.strip().startswith(opening)]
        assert len(hit) == 1, (opening[:40], len(hit))
        p = hit[0]._p
        text = para_text(p)
        offsets = []
        cursor = 0
        for m in entry["marks"]:
            probe = entry["sentences"][m]
            for was, now in REWRITES:
                probe = probe.replace(was, now)
            probe = probe[:70]
            at = text.find(probe, cursor)
            assert at > 0, (entry["sentences"][0][:40], probe[:40])
            assert text.find(probe, at + 1) < 0, "the break sentence is not unique"
            assert text[at - 1] == " ", repr(text[at - 6:at + 6])
            cursor = at + 1
            offsets.append(at)
        for at in sorted(offsets, reverse=True):
            split_paragraph(p, at)
            done += 1
    doc.save(path)
    return done


def verify(path, plan, original):
    doc = docx.Document(path)
    joined = " ".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    assert re.sub(r"\s+", " ", joined) == re.sub(r"\s+", " ", original), \
        "the running text changed"
    runs = 0
    for p in doc.paragraphs:
        if p.text.strip():
            runs = 0
        else:
            runs += 1
            assert runs < 2, "two blank paragraphs in a row"


if __name__ == "__main__":
    plan = json.load(open(sys.argv[2] if len(sys.argv) > 2 else PLAN))
    supplement = len(sys.argv) > 1 and sys.argv[1] == "supplement"
    group = SUPPLEMENT if supplement else MANUSCRIPT
    rewrites = [] if supplement else REWRITES
    openings = [] if supplement else OPENINGS
    for path in group:
        doc = docx.Document(path)
        before = " ".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
        for old, new in rewrites:
            before = before.replace(old, new)
        for probe, was, now in openings:
            before = before.replace(probe, now + probe[len(was):])
        n = apply(path, plan, rewrites, openings)
        verify(path, plan, before)
        print("%-46s %d paragraph(s) split at %d break(s)"
              % (path.split("/")[-1], len(plan), n))
