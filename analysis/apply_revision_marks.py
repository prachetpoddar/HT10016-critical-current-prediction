#!/usr/bin/env python3
"""
apply_revision_marks.py

Mark what is new against the ORIGINAL SUBMISSION.

The marks in the delivered copy came from the toolchain lost when the
container was reclaimed, and their baseline was never recorded. Asked what
they meant, the reference list answered for them: the marks there fell on
bracket numbers, volumes and years and on no author name or title, which is a
token diff seeing a renumbered list rather than anyone recording a change.

So the marks are rebuilt from scratch against the submitted manuscript the
referees read, which the authors supplied on 2026-10-19. A sentence in the
current manuscript is marked when no sentence in the submitted one matches
it. Matching is on normalised text first and then on a similarity ratio, so a
sentence that only had its spacing or its reference numbers shifted does not
read as new.

The reference list follows the rule the authors set: an entry is marked only
when the entry itself is new, never because its number moved.

Equations and tables are handled as their own kinds, because neither is made
of w:t runs that a sentence walk can see. An equation lives in OMML, whose
text sits in m:t inside m:r, so the first version of this pass marked only
the "(n)" beside the equation and never the mathematics. An equation is
marked whole or not at all, which is what the authors asked for. Newness is
decided on the equation's flattened text: the submitted manuscript carries
no OMML at all and exactly one equation, written inline as text, so eleven
of the twelve current equations are new and Eq. (2) is not.

Table cells are paragraphs too, but doc.paragraphs does not return them, so
the first version left whatever marks the cells already carried: between 67
and 92 per cent of each table, from the old toolchain, which is why they
looked partly marked. Marking them sentence by sentence was no better,
because a one-word cell such as "Count" or "934" finds a match somewhere in
the submitted text and stays plain inside an otherwise marked table.

So a table is marked by the ROW, which is the record a reader compares.
Scoring each of the 27 current rows against the 16 rows of the submitted
tables, the closest scores 0.81 and nothing reaches 0.9, so no row survives
the revision unchanged and every row is marked. The threshold is set at 0.95
rather than at the measured gap, because a row whose numbers moved is a row
that changed.

Sentence splitting protects the abbreviations this corpus is full of, Sec.,
Fig., Eq., Ref., et al. and initials, because splitting "Sec. III.F" into two
sentences would mark half a pointer and leave the other half plain.
"""

import copy
import difflib
import re
import sys

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASELINE = "/root/.claude/uploads/d7862995-def6-55d5-961b-73005a2438f5/" \
           "10c70489-prachet_paper_prx_v22_1.docx"
TARGET = "out_final60/HT10016_revised_final60_HIGHLIGHTED.docx"
CLEAN = "out_final60/HT10016_revised_final60.docx"

ABBR = (r'(?<!\bSec)(?<!\bSecs)(?<!\bFig)(?<!\bFigs)(?<!\bEq)(?<!\bEqs)'
        r'(?<!\bRef)(?<!\bRefs)(?<!\bTab)(?<!\bNo)(?<!\bvs)(?<!\bal)(?<!\bcf)'
        r'(?<!\bDr)(?<!\bProf)(?<!\bapprox)(?<!\be\.g)(?<!\bi\.e)(?<!\bSupp)'
        r'(?<!\bMater)(?<!\s[A-Z])')
SPLIT = re.compile(ABBR + r'(?<=[.!?])\s+(?=[A-Z(β])')
# The cut sits in the valley of the measured distribution. Scoring every
# current sentence against its best counterpart in the submitted manuscript
# gives a bimodal result: 774 of 1258 score below 0.1, meaning no counterpart
# at all, 1 sentence falls between 0.1 and 0.2, and the rest spread from 0.2
# upward. So 0.15 separates "this is new" from "this had a counterpart that
# was reworded" without the cut landing inside a cluster. A sentence that was
# rewritten rather than added therefore stays unmarked; marking those too
# means raising this to about 0.85, which marks 88% of the paper.
SIMILAR = 0.15


def sentences(text):
    return [s for s in SPLIT.split(text) if s.strip()]


def norm(s):
    s = re.sub(r"\[[0-9,\s–—-]+\]", "", s)      # citation numbers
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return " ".join(s.split())


def baseline_sentences():
    doc = docx.Document(BASELINE)
    out = []
    for p in doc.paragraphs:
        if p.text.strip():
            out.extend(sentences(p.text.strip()))
    for t in doc.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    if p.text.strip():
                        out.extend(sentences(p.text.strip()))
    return out


def is_old(sentence, exact, pool):
    k = norm(sentence)
    if not k:
        return True
    if k in exact:
        return True
    tk = set(k.split())
    best = 0.0
    for b in pool:
        tb = set(b.split())
        if len(tk & tb) / max(1, len(tk | tb)) < 0.25:
            continue
        r = difflib.SequenceMatcher(None, b, k).ratio()
        if r > best:
            best = r
        if best >= 0.97:
            break
    return best >= SIMILAR


MATH = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def math_text(p_el):
    return re.sub(r"\s+", "", "".join(
        t.text or "" for t in p_el.iter("{%s}t" % MATH)))


def is_equation(p_el):
    return (p_el.find("{%s}oMath" % MATH) is not None
            or p_el.find("{%s}oMathPara" % MATH) is not None)


def compact(s):
    s = re.sub(r"[\s\u2009\u200b]", "", s.lower())
    return re.sub(r"[^a-z0-9=+\-/(),.]", "", s.replace("\u2212", "-"))


def mark_all_runs(p_el, on):
    """Every run in the paragraph, OMML runs included."""
    runs = list(p_el.iter(qn("w:r"))) + list(p_el.iter("{%s}r" % MATH))
    for r in runs:
        rPr = r.find(qn("w:rPr"))
        if rPr is None:
            if not on:
                continue
            rPr = OxmlElement("w:rPr")
            # inside an m:r the w:rPr follows m:rPr, which must stay first
            at = 1 if r.find("{%s}rPr" % MATH) is not None else 0
            r.insert(at, rPr)
        for h in rPr.findall(qn("w:highlight")):
            rPr.remove(h)
        if on:
            h = OxmlElement("w:highlight")
            h.set(qn("w:val"), "yellow")
            rPr.append(h)
    return len(runs)


def clear_marks(paragraph):
    for r in paragraph._p.iter(qn("w:r")):
        rPr = r.find(qn("w:rPr"))
        if rPr is None:
            continue
        for h in rPr.findall(qn("w:highlight")):
            rPr.remove(h)


def mark_span(paragraph, at, length):
    """Highlight [at, at+length), splitting runs as needed."""
    end = at + length
    pos = 0
    for node in list(paragraph._p):
        if node.tag not in (qn("w:r"), qn("w:hyperlink")):
            continue
        text = "".join(t.text or "" for t in node.iter(qn("w:t")))
        start, stop = pos, pos + len(text)
        pos = stop
        if stop <= at or start >= end:
            continue
        if node.tag == qn("w:hyperlink"):
            for r in node.iter(qn("w:r")):
                set_yellow(r)
            continue
        head = text[:max(0, at - start)]
        body = text[max(0, at - start):min(len(text), end - start)]
        tail = text[min(len(text), end - start):]
        if head:
            before = copy.deepcopy(node)
            node.addprevious(before)
            set_text(before, head)
        if tail:
            after = copy.deepcopy(node)
            node.addnext(after)
            set_text(after, tail)
            pos = start + len(head) + len(body)
        set_text(node, body)
        set_yellow(node)


def set_text(r, text):
    for t in r.findall(qn("w:t")):
        r.remove(t)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)


def set_yellow(r):
    rPr = r.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        r.insert(0, rPr)
    for h in rPr.findall(qn("w:highlight")):
        rPr.remove(h)
    h = OxmlElement("w:highlight")
    h.set(qn("w:val"), "yellow")
    rPr.append(h)


def reference_entries(path):
    doc = docx.Document(path)
    ps = [p.text.strip() for p in doc.paragraphs]
    out = {}
    for t in ps:
        m = re.match(r"^\[(\d+)\]\s*(.+)$", t)
        if m:
            out[int(m.group(1))] = norm(m.group(2))
    return out


def table_paragraphs(doc):
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def main():
    base = baseline_sentences()
    exact = {norm(s) for s in base}
    pool = [k for k in exact if k]
    old_refs = set(reference_entries(BASELINE).values())
    bdoc = docx.Document(BASELINE)
    baseline_compact = [compact(p.text) for p in bdoc.paragraphs if p.text.strip()]

    doc = docx.Document(TARGET)
    ps = doc.paragraphs
    refs_at = next(i for i, p in enumerate(ps)
                   if p.text.strip().upper().startswith("REFERENCES"))
    marked = total = 0
    for i, p in enumerate(ps):
        text = "".join(t.text or "" for t in p._p.iter(qn("w:t")))
        if not text.strip():
            continue
        clear_marks(p)
        if i >= refs_at:
            m = re.match(r"^\[(\d+)\]\s*(.+)$", text.strip())
            if m:
                total += 1
                if norm(m.group(2)) not in old_refs:
                    mark_span(p, 0, len(text))
                    marked += 1
            continue
        if is_equation(p._p):
            total += 1
            eq = compact(math_text(p._p))
            # 0.80, from the measurement: Eq. (2), the one equation the
            # submitted manuscript carries, scores 0.886 against it and the
            # next closest scores 0.627, so the cut sits in that gap.
            hit = any(difflib.SequenceMatcher(None, eq, b).ratio() >= 0.80
                      for b in baseline_compact if abs(len(b) - len(eq))
                      < max(len(eq), 1))
            if not hit:
                mark_all_runs(p._p, True)
                marked += 1
            continue
        at = 0
        for s in sentences(text):
            k = text.find(s, at)
            if k < 0:
                at += len(s)
                continue
            total += 1
            if not is_old(s, exact, pool):
                mark_span(p, k, len(s))
                marked += 1
            at = k + len(s)
    # tables, marked by the row
    base_rows = []
    for t in bdoc.tables:
        for r in t.rows:
            k = norm(" | ".join(c.text.strip() for c in r.cells))
            if k:
                base_rows.append(k)
    for t in doc.tables:
        for row in t.rows:
            k = norm(" | ".join(c.text.strip() for c in row.cells))
            best = max((difflib.SequenceMatcher(None, k, b).ratio()
                        for b in base_rows), default=0.0) if k else 1.0
            on = best < 0.95
            total += 1
            marked += 1 if on else 0
            for cell in row.cells:
                for p in cell.paragraphs:
                    mark_all_runs(p._p, on)
    doc.save(TARGET)
    return marked, total


def verify():
    a = [p.text for p in docx.Document(CLEAN).paragraphs]
    b = [p.text for p in docx.Document(TARGET).paragraphs]
    assert a == b, "the marked copy no longer matches the clean one"
    doc = docx.Document(TARGET)
    ps = doc.paragraphs
    refs_at = next(i for i, p in enumerate(ps)
                   if p.text.strip().upper().startswith("REFERENCES"))
    for p in ps[refs_at:]:
        if not re.match(r"^\[\d+\]", p.text.strip()):
            continue
        runs = [r for r in p._p.iter(qn("w:r"))
                if "".join(t.text or "" for t in r.iter(qn("w:t")))]
        states = set()
        for r in runs:
            rPr = r.find(qn("w:rPr"))
            h = None if rPr is None else rPr.find(qn("w:highlight"))
            states.add(h is not None)
        assert len(states) <= 1, "a reference is partly marked: %s" % p.text[:18]
    for p in ps:
        if not is_equation(p._p):
            continue
        states = set()
        for r in list(p._p.iter(qn("w:r"))) + list(p._p.iter("{%s}r" % MATH)):
            rPr = r.find(qn("w:rPr"))
            h = None if rPr is None else rPr.find(qn("w:highlight"))
            states.add(h is not None)
        assert len(states) <= 1, \
            "an equation is partly marked: %s" % p.text.strip()[:12]
    for t in doc.tables:
        for row in t.rows:
            states = set()
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p._p.iter(qn("w:r")):
                        if not "".join(x.text or "" for x in r.iter(qn("w:t"))):
                            continue
                        rPr = r.find(qn("w:rPr"))
                        h = None if rPr is None else rPr.find(qn("w:highlight"))
                        states.add(h is not None)
            assert len(states) <= 1, "a table row is partly marked"


if __name__ == "__main__":
    marked, total = main()
    verify()
    print("marked %d of %d sentences and reference entries (%.0f%%)"
          % (marked, total, 100.0 * marked / total))
