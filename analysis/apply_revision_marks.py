#!/usr/bin/env python3
"""
apply_revision_marks.py

Mark what is new against the ORIGINAL SUBMISSION.

The marks in the delivered copy came from the toolchain lost when the
container was reclaimed, and their baseline was never recorded. Asked what
they meant, the reference list answered for them: the marks there fell on
bracket numbers, volumes and years and on no author name or title, which is a
token diff seeing a renumbered list rather than anyone recording a change.

So the marks are rebuilt against the submitted manuscript the referees read,
which the authors supplied on 2026-10-19.

WHAT A MARK MEANS
A sentence is marked when its wording is not already in the submitted
manuscript. A sentence that was reworded rather than added stays plain, which
is the rule the authors set.

HOW NEWNESS IS DECIDED
The first version of this pass scored a current sentence against each
submitted sentence with difflib on characters and marked it below 0.15. Two
measurements retired that rule.

  - The cut decided almost nothing. A token-overlap prescreen stood in front
    of it, and 717 of the 722 marks were made by the prescreen rejecting
    every candidate, leaving the score at its initial 0.0. Five marks
    involved a computed ratio. The "bimodal distribution" the 0.15 was
    justified by was the prescreen's own output; without it the scores are
    unimodal around 0.45 and almost nothing falls below 0.15.
  - A symmetric score cannot see a split sentence. The revision broke one
    44-token sentence into three. "Rank ordering improves strongly." scores
    0.175 against its own parent, because the parent is ten times longer, so
    two of the three clauses were marked as new and the third was not.

Newness is asymmetric, so the score is too. For a current sentence, take its
content tokens, align them in order against a submitted unit with difflib,
and measure COVERAGE, the fraction of the sentence's tokens that land inside
a matching block. A sentence is old when some submitted unit gives coverage
>= COVER and the number of matched tokens is at least MATCHED. The second
cut is there because coverage alone cannot tell reuse from coincidence in a
short sentence: "This is a property of the method." has two content tokens,
both of which appear in order somewhere in a long submitted paragraph, and
scores 1.00 on four words of nothing. "Rank ordering improves strongly."
also scores 1.00, but on four matched tokens against the sentence it was
split out of, which is reuse.

Submitted units are sentences and whole paragraphs, so a sentence
reassembled from two submitted ones is still seen.

WHERE THE CUTS COME FROM, AND WHERE THE MEASURE RUNS OUT
Two sets were built that need no judgement to label. 77 current sentences
carry a three-digit number that appears nowhere in the submitted manuscript,
so they are new. 58 current sentences are reproduced inside a submitted unit
word for word, so they are old. Against those, the usable range for COVER is
0.60 to 0.75: below 0.60 the pass misses 5 of the 77, and above 0.75 it
starts marking sentences that were reworded rather than added, which the
authors asked to stay plain.

COVER is set at the top of that range. One of the 77 then stays plain, and it
is named in test_revision_marks.py so that it is a recorded limit rather than
a surprise: "A transition-temperature-only baseline reaches 1.166 dex, a
factor of 15, on the same compounds." scores exactly 0.750, the same as the
reworded "The second extracts the data and metadata of each curve from its
source figure." No cut on this measure separates those two, so one of them is
wrong whichever way the cut falls, and the pass takes the error that leaves
an unchanged sentence unmarked rather than marking one that did not change.

Both cuts are measured rather than assumed, and test_revision_marks.py pins
them: it holds sentences on each side of each, and asserts that each cut is
the reason for at least one mark in the delivered file.

The prescreen that remains is sound rather than convenient. Unigram
containment, the fraction of the sentence's tokens present anywhere in the
candidate, is an UPPER BOUND on coverage, because a token inside a matching
block is present. Skipping a candidate whose bound is below the best score so
far can therefore never change the answer, and the test asserts that by
rescoring a sample with the prescreen off.

SENTENCES
The splitter's abbreviation guards were negative lookbehinds placed ahead of
the period, so each one tested the characters after the period and none ever
fired. "the envelope crossing of Sec. III.C is small" split into three, one
of them the bare "III.C". sentence_split.py replaces them.

EQUATIONS
An equation lives in OMML, whose text sits in m:t inside m:r, so the first
version of this pass marked only the "(n)" beside the equation. It is marked
whole or not at all, which is what the authors asked for.

The display test used to be "the paragraph contains an m:oMath", which is
also true of a prose paragraph with an inline formula. One such paragraph was
classified as an equation, scored on its formula alone and marked whole, so
roughly 330 characters of unchanged prose were marked as new, four of its six
sentences being old by this pass's own rule. A display equation is now a
paragraph whose only text outside the mathematics is its number.

Inline mathematics is marked with the sentence it sits in. Its flattened text
is placed at the right offset so that the sentence walk sees it.

HEADINGS
A heading is its own kind, like a reference entry. It is marked only when
the heading itself is new, by the same normalised equality, because a
heading is three or four words and the sentence rule marks anything shorter
than MATCHED tokens. "A. Data extraction layer" is the heading the submitted
manuscript carries and it stays plain; "F. Limitations and assumptions" is
new and marks.

TABLES
Table cells are paragraphs too, but doc.paragraphs does not return them, so
the first version left whatever marks the cells already carried, which is why
they looked partly marked. Marking them sentence by sentence was no better,
because a one-word cell such as "Count" or "934" finds a match somewhere and
stays plain inside an otherwise marked table.

So a table is marked by the ROW, which is the record a reader compares.
Scoring each of the 27 current rows against the 16 rows of the submitted
tables, the closest scores 0.81 and nothing reaches 0.9, so no row survives
unchanged and every row is marked. On this input the 0.95 cut is therefore a
gate that cannot fail, and the test supplies a synthetic unchanged row to
show that it can leave one plain.

REFERENCES
An entry is marked only when the entry itself is new, never because its
number moved. The test is normalised equality, with no tolerance: see
REFERENCE_TOLERANCE below.

BUILD ORDER
The marked copy is built as a byte copy of the clean one and then marked, so
the two cannot drift and the marked copy cannot inherit anything. The clean
copy is stripped first, because it was carrying 93 marks of its own.
"""

import copy
import difflib
import re
import shutil
import zipfile

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

import strip_highlights
from sentence_split import sentences, spans

UPLOADS = "/root/.claude/uploads/d7862995-def6-55d5-961b-73005a2438f5/"

# The manuscript. Module-level names are kept because the tests and the
# other passes address this set by them.
BASELINE = UPLOADS + "10c70489-prachet_paper_prx_v22_1.docx"
TARGET = "out_final60/HT10016_revised_final60_HIGHLIGHTED.docx"
CLEAN = "out_final60/HT10016_revised_final60.docx"

# The supplemental material, whose submitted copy the authors supplied on
# 2026-10-20. It has no display equations, no reference list and no Heading
# styles: its sections are numbered body paragraphs ("3. Substructure
# classification rules"), so the heading arm matches on that shape instead.
# It more than doubled in the revision, 2,472 words to 5,911 and one table
# to seven, so most of it marks.
SUPP_BASELINE = UPLOADS + "5ab8d5d1-SUPPLEMENTAL_MATERIAL_final.docx"
SUPP_TARGET = "out_final60/SUPPLEMENTAL_MATERIAL_revised_final60_HIGHLIGHTED.docx"
SUPP_CLEAN = "out_final60/SUPPLEMENTAL_MATERIAL_revised_final60.docx"

NUMBERED_HEADING = re.compile(r"^\d{1,2}\.\s+[A-Z]")


class DocumentSet:
    """One submitted copy, one clean copy, one marked copy, and the arms
    that apply to them."""

    def __init__(self, name, baseline, clean, target,
                 equations=True, references=True, styled_headings=True):
        self.name = name
        self.baseline = baseline
        self.clean = clean
        self.target = target
        self.equations = equations
        self.references = references
        self.styled_headings = styled_headings

    def is_heading(self, p):
        if self.styled_headings:
            return p.style.name.startswith("Heading")
        t = p.text.strip()
        return bool(NUMBERED_HEADING.match(t)) and len(t.split()) <= 12

MATH = "http://schemas.openxmlformats.org/officeDocument/2006/math"
MR = "{%s}r" % MATH

# Measured cuts. test_revision_marks.py holds sentences either side of both.
# COVER: how much of the sentence must already be in the submitted text.
# MATCHED: how many of its content tokens must match. A sentence with fewer
# than MATCHED content tokens is therefore always marked, because nothing in
# it could show reuse: "This is a property of the method." has two, both of
# which appear in order inside a long submitted paragraph, and scores 1.00
# on four words of nothing.
COVER = 0.75
MATCHED = 4

# Equations: Eq. (2), the one equation the submitted manuscript carries,
# scores 0.886 against its submitted form and the next closest scores 0.627,
# so the cut sits in that gap.
EQUATION = 0.80

# Table rows: the closest of the 27 current rows scores 0.81 against the
# submitted rows. The cut is set above the measured gap because a row whose
# numbers moved is a row that changed.
TABLE_ROW = 0.95

# References are compared by normalised equality. An entry whose page number
# or journal abbreviation changed therefore marks as new. Six entries mark,
# of which five are additions and one, [36], is an updated entry.
REFERENCE_TOLERANCE = None

STOP = set("""a an the and or but of in on at to for from with by as is are was
were be been being this that these those it its which who whom whose than then
so such not no nor if we our us they their them he she his her i""".split())


def norm(s):
    s = re.sub(r"\[[0-9,\s–—-]+\]", "", s)    # citation numbers
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return " ".join(s.split())


def tokens(s):
    return [w for w in norm(s).split() if w not in STOP]


# --------------------------------------------------------------- the score

def score(t, units, usets, prescreen=True):
    """Best coverage of token list t by any submitted unit.

    The prescreen skips a candidate whose unigram containment, an upper
    bound on coverage, cannot beat the best coverage already found.
    """
    if not t:
        return 1.0
    best = 0.0
    for u, us in zip(units, usets):
        if prescreen and sum(1 for w in t if w in us) / len(t) < best:
            continue
        blocks = difflib.SequenceMatcher(None, u, t,
                                         autojunk=False).get_matching_blocks()
        cov = sum(b.size for b in blocks) / len(t)
        if cov > best:
            best = cov
    return best


def is_old(sentence, units, usets):
    t = tokens(sentence)
    if not t:
        return True
    cov = score(t, units, usets)
    return cov >= COVER and cov * len(t) >= MATCHED


def submitted_units(path=None):
    """Sentences and paragraphs of the submitted copy, as token lists."""
    doc = docx.Document(path or BASELINE)
    out = []
    for p in doc.paragraphs:
        if not p.text.strip():
            continue
        out.append(tokens(p.text))
        for s in sentences(p.text.strip()):
            out.append(tokens(s))
    for t in doc.tables:
        for row in t.rows:
            for c in row.cells:
                if c.text.strip():
                    out.append(tokens(c.text))
    out = [u for u in out if u]
    return out, [set(u) for u in out]


# ----------------------------------------------------------- the paragraph

def math_text(el):
    return "".join(t.text or "" for t in el.iter("{%s}t" % MATH))


def compact(s):
    s = re.sub(r"[\s ​]", "", s.lower())
    return re.sub(r"[^a-z0-9=+\-/(),.]", "", s.replace("−", "-"))


NUMBER_ONLY = re.compile(r"^\(?\d{1,2}[a-z]?\)?$")


def is_display_equation(p_el):
    """A paragraph that IS an equation, not one that merely contains maths."""
    if p_el.find("{%s}oMathPara" % MATH) is not None:
        return True
    if p_el.find("{%s}oMath" % MATH) is None:
        return False
    outside = "".join(t.text or "" for t in p_el.iter(qn("w:t"))).strip()
    return outside == "" or bool(NUMBER_ONLY.match(outside))


def pieces(p_el):
    """The paragraph's top-level children that carry text, in order.

    Yields (node, text). An inline m:oMath contributes its flattened
    mathematics, so a sentence that contains a formula gets the right
    offsets and the formula is marked with it.
    """
    for node in list(p_el):
        if node.tag in (qn("w:r"), qn("w:hyperlink")):
            yield node, "".join(t.text or "" for t in node.iter(qn("w:t")))
        elif node.tag in ("{%s}oMath" % MATH, "{%s}oMathPara" % MATH):
            yield node, math_text(node)


def paragraph_text(p_el):
    return "".join(t for _, t in pieces(p_el))


# ------------------------------------------------------------- the marking

def set_yellow(r):
    rPr = r.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        # inside an m:r the w:rPr follows m:rPr, which must stay first
        r.insert(1 if r.find("{%s}rPr" % MATH) is not None else 0, rPr)
    for h in rPr.findall(qn("w:highlight")):
        rPr.remove(h)
    h = OxmlElement("w:highlight")
    h.set(qn("w:val"), "yellow")
    rPr.append(h)


def mark_all_runs(el, on=True):
    """Every run under el, OMML runs included."""
    runs = list(el.iter(qn("w:r"))) + list(el.iter(MR))
    if on:
        for r in runs:
            set_yellow(r)
    return len(runs)


SPLITTABLE = (qn("w:rPr"), qn("w:t"))


def set_text(r, text):
    for t in r.findall(qn("w:t")):
        r.remove(t)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)


def mark_span(p_el, at, length):
    """Highlight [at, at+length), splitting runs where the span ends inside.

    A run is split by deep-copying it, which copies whatever else it holds.
    Splitting a run that carries a tab, a break or a drawing would duplicate
    that element, so such a run is not split: it is marked whole. The
    assertion below records that this only happens when the whole run is
    inside the span, which is the case throughout this manuscript.
    """
    end = at + length
    pos = 0
    for node, text in list(pieces(p_el)):
        start, stop = pos, pos + len(text)
        pos = stop
        if stop <= at or start >= end or not text:
            continue
        if node.tag != qn("w:r"):
            # a hyperlink or an inline formula: mark it whole
            mark_all_runs(node, True)
            continue
        head = text[:max(0, at - start)]
        tail = text[min(len(text), end - start):]
        if head or tail:
            others = [c for c in node if c.tag not in SPLITTABLE]
            assert not others, (
                "run carrying %s would be split at offset %d"
                % (others[0].tag.rsplit("}", 1)[-1], at))
            body = text[len(head):len(text) - len(tail)]
            if head:
                before = copy.deepcopy(node)
                node.addprevious(before)
                set_text(before, head)
            if tail:
                after = copy.deepcopy(node)
                node.addnext(after)
                set_text(after, tail)
            set_text(node, body)
        set_yellow(node)


# ------------------------------------------------------------- the entries

def headings(path=None):
    """Normalised heading text of a document.

    The submitted manuscript styles every paragraph Normal, so its headings
    cannot be found by style. They are taken instead as its short
    paragraphs, which is the shape a heading has, with the leading numeral
    stripped. A short body sentence can land in the set, which can only
    leave a heading plain, never mark one that did not change.
    """
    out = set()
    for p in docx.Document(path or BASELINE).paragraphs:
        t = p.text.strip()
        if t and len(t.split()) <= 10:
            out.add(heading_key(t))
    out.discard("")
    return out


def heading_key(text):
    return norm(re.sub(r"^(?:[IVXLC]+|[A-Z])\.\s*", "", text.strip()))





def reference_entries(path):
    out = {}
    for p in docx.Document(path).paragraphs:
        m = re.match(r"^\[(\d+)\]\s*(.+)$", p.text.strip())
        if m:
            out[int(m.group(1))] = norm(m.group(2))
    return out


def row_key(row):
    return norm(" | ".join(c.text.strip() for c in row.cells))


# ------------------------------------------------------------------ the pass

def build(ds):
    """Strip the clean copy, then write the marked copy as a copy of it."""
    strip_highlights.strip(ds.clean, drop_page_breaks=True)
    shutil.copyfile(ds.clean, ds.target)


MANUSCRIPT = None        # bound below, once DocumentSet instances exist


def main(ds=None):
    ds = ds or MANUSCRIPT
    build(ds)
    units, usets = submitted_units(ds.baseline)
    old_refs = set(reference_entries(ds.baseline).values())
    old_headings = headings(ds.baseline)
    bdoc = docx.Document(ds.baseline)
    base_eq = [compact(p.text) for p in bdoc.paragraphs if p.text.strip()]
    base_rows = [k for t in bdoc.tables for r in t.rows
                 if (k := row_key(r))]

    doc = docx.Document(ds.target)
    ps = doc.paragraphs
    refs_at = next((i for i, p in enumerate(ps)
                    if p.text.strip().upper().startswith("REFERENCES")),
                   len(ps))
    tally = {"body": [0, 0], "heading": [0, 0], "reference": [0, 0],
             "equation": [0, 0], "table row": [0, 0]}

    for i, p in enumerate(ps):
        el = p._p
        text = paragraph_text(el)
        if not text.strip():
            continue
        if i >= refs_at and ds.references:
            m = re.match(r"^\[(\d+)\]\s*(.+)$", text.strip())
            if not m:
                continue
            tally["reference"][1] += 1
            if norm(m.group(2)) not in old_refs:
                mark_span(el, 0, len(text))
                tally["reference"][0] += 1
            continue
        if ds.is_heading(p) and i < refs_at:
            tally["heading"][1] += 1
            if heading_key(text) not in old_headings:
                mark_span(el, 0, len(text))
                tally["heading"][0] += 1
            continue
        if ds.equations and is_display_equation(el):
            tally["equation"][1] += 1
            eq = compact(math_text(el))
            hit = any(difflib.SequenceMatcher(None, eq, b).ratio() >= EQUATION
                      for b in base_eq
                      if abs(len(b) - len(eq)) < max(len(eq), 1))
            if not hit:
                mark_all_runs(el, True)
                tally["equation"][0] += 1
            continue
        for a, b in spans(text):
            s = text[a:b]
            if not s.strip():
                continue
            tally["body"][1] += 1
            if not is_old(s, units, usets):
                mark_span(el, a, b - a)
                tally["body"][0] += 1

    for t in doc.tables:
        for row in t.rows:
            k = row_key(row)
            best = max((difflib.SequenceMatcher(None, k, b).ratio()
                        for b in base_rows), default=0.0) if k else 1.0
            on = best < TABLE_ROW
            tally["table row"][1] += 1
            tally["table row"][0] += 1 if on else 0
            if on:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        mark_all_runs(p._p, True)
    doc.save(ds.target)
    return tally


# ----------------------------------------------------------------- checking

def marks_in(el):
    """True/False per run that carries text, plus the paragraph mark."""
    out = []
    for r in list(el.iter(qn("w:r"))) + list(el.iter(MR)):
        if not "".join(t.text or ""
                       for t in r.iter(qn("w:t"))) and not "".join(
                           t.text or "" for t in r.iter("{%s}t" % MATH)):
            continue
        rPr = r.find(qn("w:rPr"))
        out.append(rPr is not None and rPr.find(qn("w:highlight")) is not None)
    return out


def full_text(path):
    """Every string in the document part, tables, headers and footers too."""
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    out = []
    with zipfile.ZipFile(path) as z:
        for name in sorted(z.namelist()):
            if not name.endswith(".xml"):
                continue
            if not (name == "word/document.xml"
                    or name.startswith("word/header")
                    or name.startswith("word/footer")
                    or name in ("word/footnotes.xml", "word/endnotes.xml")):
                continue
            from lxml import etree
            root = etree.fromstring(z.read(name))
            out.append((name, "".join(
                (t.text or "") for t in root.iter(W + "t", "{%s}t" % MATH))))
    return out


def verify(ds=None):
    ds = ds or MANUSCRIPT
    CLEAN, TARGET = ds.clean, ds.target
    # 1. The clean copy carries no marks at all, anywhere.
    assert strip_highlights.count(CLEAN) == 0, \
        "the clean copy carries %d marks" % strip_highlights.count(CLEAN)

    # 2. The two copies say the same thing, in the body, the tables, the
    #    headers and the footers, not only in doc.paragraphs.
    a, b = full_text(CLEAN), full_text(TARGET)
    assert [n for n, _ in a] == [n for n, _ in b], "the parts differ"
    for (name, x), (_, y) in zip(a, b):
        assert x == y, "the marked copy altered the text of %s" % name

    # 3. Marks live only in the body. A mark in a header, a footer or a
    #    note changes no text, so the text comparison above cannot see one.
    with zipfile.ZipFile(TARGET) as z:
        from lxml import etree
        W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        for name in z.namelist():
            if name == "word/document.xml" or not name.endswith(".xml"):
                continue
            if not (name.startswith("word/header")
                    or name.startswith("word/footer")
                    or name in ("word/footnotes.xml", "word/endnotes.xml")):
                continue
            n = len(etree.fromstring(z.read(name)).findall(".//" + W + "highlight"))
            assert n == 0, "%d marks in %s" % (n, name)

    doc = docx.Document(TARGET)
    ps = doc.paragraphs

    # 4. No mark on a paragraph mark. These render as a yellow block at the
    #    end of the line and are what the clean copy was carrying.
    for i, p in enumerate(ps):
        pPr = p._p.find(qn("w:pPr"))
        rPr = None if pPr is None else pPr.find(qn("w:rPr"))
        assert rPr is None or rPr.find(qn("w:highlight")) is None, \
            "paragraph %d carries a mark on its paragraph mark" % i

    # 5. No mark on an m:ctrlPr, which is invisible to a run walk.
    for p in ps:
        for c in p._p.iter("{%s}ctrlPr" % MATH):
            rPr = c.find(qn("w:rPr"))
            assert rPr is None or rPr.find(qn("w:highlight")) is None, \
                "an equation control property carries a mark"

    # 6. Whole-unit marking: each reference entry, each display equation and
    #    each table row is marked all over or not at all.
    refs_at = next((i for i, p in enumerate(ps)
                    if p.text.strip().upper().startswith("REFERENCES")),
                   len(ps))
    for p in ps[refs_at:]:
        if re.match(r"^\[\d+\]", p.text.strip()):
            assert len(set(marks_in(p._p))) <= 1, \
                "a reference is partly marked: %s" % p.text[:18]
    for p in ps:
        if is_display_equation(p._p):
            assert len(set(marks_in(p._p))) <= 1, \
                "an equation is partly marked: %s" % p.text.strip()[:12]
    for p in ps[:refs_at]:
        if ds.is_heading(p) and p.text.strip():
            assert len(set(marks_in(p._p))) <= 1, \
                "a heading is partly marked: %s" % p.text.strip()[:30]
    for t in doc.tables:
        for row in t.rows:
            states = set()
            for cell in row.cells:
                for p in cell.paragraphs:
                    states.update(marks_in(p._p))
            assert len(states) <= 1, "a table row is partly marked"


MANUSCRIPT = DocumentSet("manuscript", BASELINE, CLEAN, TARGET)
SUPPLEMENT = DocumentSet("supplement", SUPP_BASELINE, SUPP_CLEAN, SUPP_TARGET,
                         equations=False, references=False,
                         styled_headings=False)
SETS = {"manuscript": MANUSCRIPT, "supplement": SUPPLEMENT}


if __name__ == "__main__":
    import sys as _sys
    chosen = [SETS[a] for a in _sys.argv[1:]] or list(SETS.values())
    for ds in chosen:
        tally = main(ds)
        verify(ds)
        print(ds.name)
        for kind in ("body", "heading", "equation", "table row", "reference"):
            m, t = tally[kind]
            if t:
                print("  %-10s %4d of %4d marked (%3.0f%%)"
                      % (kind, m, t, 100.0 * m / t))
