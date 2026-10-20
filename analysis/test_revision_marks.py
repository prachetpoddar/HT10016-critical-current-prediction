#!/usr/bin/env python3
"""
test_revision_marks.py

Tests for apply_revision_marks.py, written against the defects an
independent review found in its predecessor rather than against the code.

The review's two standing lessons drive the file:

  - A prefilter in front of a documented threshold becomes the real
    threshold. So PRESCREEN below rescores a sample with the prescreen off
    and requires the same answer, which is a property the prescreen has by
    construction (unigram containment bounds coverage from above) and which
    is therefore worth asserting rather than arguing.

  - A whole-or-nothing writer makes its own partial-marking check
    unreachable. The three whole-unit assertions in verify() cannot be
    violated by the pass itself, so MUTATIONS violates them by hand, along
    with the six defect classes that walked through the old verify()
    untouched. Every mutation here must make verify() fail.

Each check says what it covers. Self-verification bottoms out: the
assertions added here could themselves be mutated, and that regress is not
followed. What is claimed is that each listed mutation now fails, and that
the two decision cuts are pinned by named sentences.
"""

import random
import shutil
import sys
import zipfile

from lxml import etree

sys.path.insert(0, "/home/claude/ht_gh/analysis")

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

import apply_revision_marks as arm
import strip_highlights
from sentence_split import sentences

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SCRATCH = ("/tmp/claude-0/-home-claude/"
           "d7862995-def6-55d5-961b-73005a2438f5/scratchpad/rev")

PASS, FAIL = [], []


def check(name, fn):
    try:
        fn()
    except AssertionError as e:
        FAIL.append("%s: %s" % (name, e))
    except Exception as e:
        FAIL.append("%s: crashed, %s: %s" % (name, type(e).__name__, e))
    else:
        PASS.append(name)


# --------------------------------------------------------------- the splitter

SPLIT_CASES = [
    # (text, expected number of sentences)
    ("The envelope crossing of Sec. III.C is small. See Fig. 4 and Eq. (3).", 2),
    ("We extract records (Sec. II.A), assign anchors (Sec. II.B), and stop.", 1),
    ("Reported in Ref. [12]. Also in Refs. [3, 4].", 2),
    ("The exponent is 1.14. Figure 4 shows it.", 2),
    ("At 4.2 K the term is zero. (1) enforces this.", 2),
    ("Values near 0.95 of Tc are excluded.", 1),
]


def test_splitter():
    """Covers: the abbreviation guards fire, which they never did before."""
    for text, n in SPLIT_CASES:
        got = sentences(text)
        assert len(got) == n, "%r split into %d, expected %d: %r" % (
            text, len(got), n, got)


# ------------------------------------------------------------------ the cuts

# Sentences held either side of each cut, so that moving a cut fails here.
# Each was read against its best submitted counterpart before being listed.
OLD_SENTENCES = [
    # reworded, not added: the submitted manuscript says the same thing
    "In superconductivity, this approach has been especially effective for "
    "predicting the transition temperature Tc.",
    # identical but for the spacing of Jc (T,H)
    "Critical current density Jc(T,H) determines the practical operating "
    "range of a superconductor.",
    # the clause the revision split off a longer submitted sentence, which
    # the character-ratio score scored at 0.175 and marked as new
    "Rank ordering improves strongly.",
    "The methods follow the workflow of Figs. 1 and 2 in four steps.",
    # the third clause of the sentence the revision split in three, which
    # the old pass left plain while marking the other two
    "Precision at K = 3, the fraction of the true top three compounds that "
    "appear in the predicted top three, reaches 1.000.",
    # reworded, and sitting exactly on the coverage cut
    "The second extracts the data and metadata of each curve from its "
    "source figure.",
]

NEW_SENTENCES = [
    # the statement that turns a promise into a deposit, left plain by the
    # character-ratio score because one candidate passed its prescreen at
    # exactly 0.250 and then scored 0.624
    "The extracted critical-current dataset and the code are openly "
    "available in https://doi.org/10.5281/zenodo.23485083.",
    # wholly new discussion added for the referees
    "All 441 candidate-grid targets of iron chalcogenide 11-type are refused.",
    "Check that at least K = 3 anchor measurements are available for the "
    "candidate, and refuse it otherwise.",
    # new figures: 257 and 52 appear nowhere in the submitted manuscript
    "This analysis yields 257 temperature-axis fits and 52 field-axis fits.",
    # a new result, with 441 absent from the submitted manuscript
    "All 441 candidate-grid targets of iron chalcogenide 11-type are refused.",
    "On these three, the pooled error falls to 0.694 dex.",
]

# What the measure cannot do. This sentence is new (1.166 appears nowhere in
# the submitted manuscript) and scores exactly on the coverage cut, the same
# as the reworded sentence listed above it in OLD_SENTENCES. The pass leaves
# it plain. Listed so that the limit is recorded rather than discovered.
KNOWN_MISSES = [
    "A transition-temperature-only baseline reaches 1.166 dex, a factor of "
    "15, on the same compounds.",
]


def test_known_misses_are_still_what_was_recorded():
    """Covers: the recorded limit has not quietly grown or gone away."""
    units, usets = arm.submitted_units()
    for s in KNOWN_MISSES:
        cov = arm.score(arm.tokens(s), units, usets)
        assert arm.is_old(s, units, usets), \
            "recorded miss is now marked (cov=%.3f); update the list" % cov


def test_objective_sets():
    """Covers: accuracy on two sets that need no judgement to label.

    New: sentences carrying a three-digit number absent from the submitted
    vocabulary. Old: sentences reproduced word for word inside a submitted
    unit. Measured on the delivered file, not on a fixture.
    """
    units, usets = arm.submitted_units()
    vocab = set()
    for u in units:
        vocab.update(u)
    flat = " || ".join(" ".join(u) for u in units)
    ps = docx.Document(arm.CLEAN).paragraphs
    refs_at = next(i for i, p in enumerate(ps)
                   if p.text.strip().upper().startswith("REFERENCES"))
    new_set, old_set = [], []
    for i, p in enumerate(ps):
        if i >= refs_at or arm.is_display_equation(p._p):
            continue
        text = arm.paragraph_text(p._p)
        if not text.strip():
            continue
        for s in sentences(text):
            tk = arm.tokens(s)
            if not tk:
                continue
            nums = [w for w in tk if w.isdigit() and len(w) >= 3]
            if nums and any(n not in vocab for n in nums):
                new_set.append(s)
            elif len(tk) >= 6 and " ".join(tk) in flat:
                old_set.append(s)
    assert len(new_set) >= 70, "the objective new set shrank to %d" % len(new_set)
    assert len(old_set) >= 50, "the objective old set shrank to %d" % len(old_set)
    missed = [s for s in new_set if arm.is_old(s, units, usets)]
    wrong = [s for s in old_set if not arm.is_old(s, units, usets)]
    assert not wrong, "%d word-for-word sentences were marked new: %s" \
        % (len(wrong), [x[:50] for x in wrong])
    assert len(missed) <= len(KNOWN_MISSES), \
        "%d of %d objectively new sentences stay plain, %d recorded: %s" \
        % (len(missed), len(new_set), len(KNOWN_MISSES),
           [x[:60] for x in missed])
    print("    objective sets: %d new (%d plain, all recorded), %d old (0 marked)"
          % (len(new_set), len(missed), len(old_set)))


def test_cuts():
    """Covers: COVER and MATCHED decide these named sentences correctly."""
    units, usets = arm.submitted_units()
    for s in OLD_SENTENCES:
        t = arm.tokens(s)
        cov = arm.score(t, units, usets)
        assert arm.is_old(s, units, usets), \
            "called new at cov=%.2f matched=%.0f: %s" % (cov, cov * len(t), s[:60])
    for s in NEW_SENTENCES:
        t = arm.tokens(s)
        cov = arm.score(t, units, usets)
        assert not arm.is_old(s, units, usets), \
            "called old at cov=%.2f matched=%.0f: %s" % (cov, cov * len(t), s[:60])
    # A short sentence whose few tokens happen to appear in a long submitted
    # paragraph must not be called old on coverage alone.
    short = "This is a property of the method."
    assert not arm.is_old(short, units, usets), \
        "a two-token sentence was called old at coverage %.2f" \
        % arm.score(arm.tokens(short), units, usets)


def test_cuts_are_load_bearing():
    """Covers: each cut is at a boundary, not parked where nothing changes.

    A knob exercised only by overriding it proves nothing about the shipped
    value, so this asserts that the shipped value sits next to a sentence
    that flips. Both cuts must be the reason for at least one decision.
    """
    units, usets = arm.submitted_units()
    # Each cut must be the reason for at least one decision in the body,
    # measured on the delivered file rather than on the listed examples.
    doc = docx.Document(arm.CLEAN)
    body = []
    for p in doc.paragraphs:
        if arm.is_display_equation(p._p):
            continue
        t = arm.paragraph_text(p._p)
        if t.strip():
            body.extend(x for x in sentences(t) if arm.tokens(x))
    by_cover = by_matched = 0
    for s in body:
        t = arm.tokens(s)
        c = arm.score(t, units, usets)
        if c < arm.COVER and c * len(t) >= min(arm.MATCHED, len(t)):
            by_cover += 1
        if c >= arm.COVER and c * len(t) < min(arm.MATCHED, len(t)):
            by_matched += 1
    assert by_cover > 0, "the coverage cut decides nothing"
    assert by_matched > 0, "the matched-token cut decides nothing"
    print("    coverage cut decides %d marks, matched-token cut %d"
          % (by_cover, by_matched))


def test_prescreen_is_sound():
    """Covers: the prescreen cannot change an answer.

    Unigram containment is an upper bound on block coverage, so a candidate
    the prescreen skips could not have beaten the running best. Measured on
    a sample rather than argued.
    """
    units, usets = arm.submitted_units()
    doc = docx.Document(arm.CLEAN)
    pool = []
    for p in doc.paragraphs:
        t = arm.paragraph_text(p._p)
        if t.strip():
            pool.extend(s for s in sentences(t) if arm.tokens(s))
    random.seed(3)
    for s in random.sample(pool, 120):
        t = arm.tokens(s)
        on = arm.score(t, units, usets, prescreen=True)
        off = arm.score(t, units, usets, prescreen=False)
        assert on == off, "prescreen changed %r from %s to %s" % (s[:40], off, on)


# ------------------------------------------------------- the writer's limits

def test_mark_span_refuses_to_duplicate():
    """Covers: the gate on splitting a run that holds more than text.

    Deep-copying a run to split it copies whatever else the run holds, so a
    run with a tab inside it would end up with two. The gate must fire on a
    planted tab rather than silently duplicating it.
    """
    d = docx.Document()
    p = d.add_paragraph()
    r = p.add_run()
    r._r.append(OxmlElement("w:tab"))
    arm.set_text(r._r, "Old one. New two.")
    r._r.append(OxmlElement("w:tab"))
    try:
        arm.mark_span(p._p, 10, 7)
    except AssertionError as e:
        assert "tab" in str(e), "fired, but not about the tab: %s" % e
    else:
        raise AssertionError("a run carrying a tab was split silently")


def test_table_gate_can_pass():
    """Covers: the 0.95 row cut can leave a row plain.

    On this manuscript no row scores above 0.81, so the cut never fires and
    the arm is indistinguishable from "mark every row". A row copied
    verbatim out of the submitted manuscript must stay plain, or the cut is
    a gate that cannot fail.
    """
    import difflib
    bdoc = docx.Document(arm.BASELINE)
    rows = [k for t in bdoc.tables for r in t.rows if (k := arm.row_key(r))]
    assert rows, "the submitted manuscript has no table rows"
    best = max(difflib.SequenceMatcher(None, rows[0], b).ratio() for b in rows)
    assert best >= arm.TABLE_ROW, \
        "a verbatim submitted row scores %.3f, below the %.2f cut" \
        % (best, arm.TABLE_ROW)
    changed = arm.norm(rows[0] + " and a new column of numbers 1 2 3 4 5 6")
    worst = max(difflib.SequenceMatcher(None, changed, b).ratio() for b in rows)
    assert worst < arm.TABLE_ROW, \
        "a row with a column added still scores %.3f" % worst


def test_display_equation_test():
    """Covers: a prose paragraph with inline maths is not an equation.

    The old test was "the paragraph contains an m:oMath", which classified
    one six-sentence prose paragraph as an equation and marked it whole.
    """
    doc = docx.Document(arm.CLEAN)
    eqs = [p for p in doc.paragraphs if arm.is_display_equation(p._p)]
    assert len(eqs) == 11, "expected 11 display equations, found %d" % len(eqs)
    for p in eqs:
        outside = p.text.strip()
        assert outside == "" or arm.NUMBER_ONLY.match(outside), \
            "paragraph classified as an equation carries prose: %r" % outside[:60]
    inline = [p for p in doc.paragraphs
              if p._p.find("{%s}oMath" % arm.MATH) is not None
              and not arm.is_display_equation(p._p)]
    assert inline, "no paragraph with inline maths, so the test is vacuous"


# ----------------------------------------------------------- the mutations

def _planted(mutate, clean_too=False, ds=None):
    """Copy a delivered pair, mutate one, and require verify() to fail."""
    ds = ds or arm.MANUSCRIPT
    c = SCRATCH + "/mut_clean.docx"
    t = SCRATCH + "/mut_marked.docx"
    shutil.copyfile(ds.clean, c)
    shutil.copyfile(ds.target, t)
    mutate(c if clean_too else t)
    planted = arm.DocumentSet(
        "planted", ds.baseline, c, t,
        equations=ds.equations, references=ds.references,
        styled_headings=ds.styled_headings)
    try:
        arm.verify(planted)
    except AssertionError:
        return
    raise AssertionError("verify() passed the mutation")


def _edit(path, fn):
    with zipfile.ZipFile(path) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    out = []
    for info, data in items:
        if info.filename == "word/document.xml":
            root = etree.fromstring(data)
            fn(root)
            data = etree.tostring(root, xml_declaration=True,
                                  encoding="UTF-8", standalone=True)
        out.append((info, data))
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in out:
            z.writestr(info, data)


def _yellow_into(rPr):
    h = etree.SubElement(rPr, W + "highlight")
    h.set(W + "val", "yellow")


def _mark_paragraph_mark(root):
    for p in root.iter(W + "p"):
        pPr = p.find(W + "pPr")
        if pPr is None:
            pPr = etree.Element(W + "pPr")
            p.insert(0, pPr)
        rPr = pPr.find(W + "rPr")
        if rPr is None:
            rPr = etree.SubElement(pPr, W + "rPr")
        _yellow_into(rPr)
        return
    raise AssertionError("no paragraph to mutate")


def _mark_ctrlpr(root):
    M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
    for c in root.iter(M + "ctrlPr"):
        rPr = c.find(W + "rPr")
        if rPr is None:
            rPr = etree.SubElement(c, W + "rPr")
        _yellow_into(rPr)
        return
    raise AssertionError("no m:ctrlPr to mutate")


def _change_table_cell_text(root):
    for tbl in root.iter(W + "tbl"):
        for t in tbl.iter(W + "t"):
            if (t.text or "").strip():
                t.text = (t.text or "") + " XYZ"
                return
    raise AssertionError("no table cell text to mutate")


def _partly_mark_a_reference(root):
    """Drop the mark on one run of a marked reference entry."""
    for p in root.iter(W + "p"):
        text = "".join(x.text or "" for x in p.iter(W + "t"))
        if not text.strip().startswith("["):
            continue
        runs = [r for r in p.iter(W + "r")
                if "".join(x.text or "" for x in r.iter(W + "t"))]
        marked = [r for r in runs
                  if r.find(W + "rPr") is not None
                  and r.find(W + "rPr").find(W + "highlight") is not None]
        if len(marked) > 1:
            rPr = marked[0].find(W + "rPr")
            rPr.remove(rPr.find(W + "highlight"))
            return
    raise AssertionError("no multi-run marked reference to mutate")


def _partly_mark_an_equation(root):
    M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
    for p in root.iter(W + "p"):
        rs = [r for r in p.iter(M + "r")
              if r.find(W + "rPr") is not None
              and r.find(W + "rPr").find(W + "highlight") is not None]
        if len(rs) > 1:
            rPr = rs[0].find(W + "rPr")
            rPr.remove(rPr.find(W + "highlight"))
            return
    raise AssertionError("no multi-run marked equation to mutate")


def _partly_mark_a_heading(root):
    """Drop the mark on one run of the one marked heading."""
    for p in root.iter(W + "p"):
        pPr = p.find(W + "pPr")
        st = None if pPr is None else pPr.find(W + "pStyle")
        if st is None or "eading" not in (st.get(W + "val") or ""):
            continue
        rs = [r for r in p.iter(W + "r")
              if "".join(x.text or "" for x in r.iter(W + "t"))
              and r.find(W + "rPr") is not None
              and r.find(W + "rPr").find(W + "highlight") is not None]
        if len(rs) > 1:
            rPr = rs[0].find(W + "rPr")
            rPr.remove(rPr.find(W + "highlight"))
            return
    raise AssertionError("no multi-run marked heading to mutate")


def _partly_mark_a_table_row(root):
    for tbl in root.iter(W + "tbl"):
        for tr in tbl.iter(W + "tr"):
            rs = [r for r in tr.iter(W + "r")
                  if "".join(x.text or "" for x in r.iter(W + "t"))
                  and r.find(W + "rPr") is not None
                  and r.find(W + "rPr").find(W + "highlight") is not None]
            if len(rs) > 1:
                rPr = rs[0].find(W + "rPr")
                rPr.remove(rPr.find(W + "highlight"))
                return
    raise AssertionError("no multi-run marked table row to mutate")


def _mark_the_footer(path):
    with zipfile.ZipFile(path) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    out, done = [], False
    for info, data in items:
        if info.filename.startswith("word/footer") and not done:
            root = etree.fromstring(data)
            for r in root.iter(W + "r"):
                if "".join(x.text or "" for x in r.iter(W + "t")):
                    rPr = r.find(W + "rPr")
                    if rPr is None:
                        rPr = etree.Element(W + "rPr")
                        r.insert(0, rPr)
                    _yellow_into(rPr)
                    done = True
                    break
            data = etree.tostring(root, xml_declaration=True,
                                  encoding="UTF-8", standalone=True)
        out.append((info, data))
    assert done, "no footer run to mutate"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in out:
            z.writestr(info, data)


# The six classes that walked through the old verify(), plus the three
# whole-unit violations it did catch, kept so a regression shows up here.
MUTATIONS = [
    ("paragraph mark marked (old M8)",
     lambda p: _edit(p, _mark_paragraph_mark), False),
    ("m:ctrlPr marked (old M7)",
     lambda p: _edit(p, _mark_ctrlpr), False),
    ("table cell text changed (old M9)",
     lambda p: _edit(p, _change_table_cell_text), False),
    ("footer marked (old M10)", _mark_the_footer, False),
    ("a mark left in the clean copy (finding 1)",
     lambda p: _edit(p, _mark_paragraph_mark), True),
    ("reference partly marked (old M1)",
     lambda p: _edit(p, _partly_mark_a_reference), False),
    ("equation partly marked (old M2)",
     lambda p: _edit(p, _partly_mark_an_equation), False),
    ("table row partly marked (old M3)",
     lambda p: _edit(p, _partly_mark_a_table_row), False),
    ("heading partly marked",
     lambda p: _edit(p, _partly_mark_a_heading), False),
]


def test_mutations():
    """Covers: verify() now fails on each planted defect."""
    import os
    os.makedirs(SCRATCH, exist_ok=True)
    for name, mutate, clean_too in MUTATIONS:
        try:
            _planted(mutate, clean_too)
        except AssertionError as e:
            raise AssertionError("%s -> %s" % (name, e))


def test_the_grader_runs():
    """Covers: the mutation loop is not silently empty.

    A meta-check, because a harness that plants nothing prints a clean run.
    """
    assert len(MUTATIONS) >= 9, "the mutation set shrank"
    assert len(SPLIT_CASES) >= 6, "the splitter cases shrank"
    assert OLD_SENTENCES and NEW_SENTENCES, "the decision set is empty"


def test_delivered_pair():
    """Covers: the files on disk pass, which is the claim that ships.

    Both sets, because the supplement run once wrote its own document into
    the manuscript's marked path: main() saved to the module constant
    rather than to the set it had been given, and nothing but this noticed.
    """
    for ds in arm.SETS.values():
        assert strip_highlights.count(ds.clean) == 0, \
            "%s: the clean copy carries marks" % ds.name
        arm.verify(ds)


def test_each_set_writes_its_own_files():
    """Covers: a run of one set cannot touch another set's files.

    The defect this exists for: main(SUPPLEMENT) saved the supplement into
    the manuscript's marked path, because one save call still named the
    module constant. Checks the first paragraph of each marked copy against
    its own clean copy rather than trusting the path.
    """
    for ds in arm.SETS.values():
        a = docx.Document(ds.clean).paragraphs[0].text.strip()
        b = docx.Document(ds.target).paragraphs[0].text.strip()
        assert a == b, "%s: marked copy opens with %r, clean with %r" \
            % (ds.name, b[:60], a[:60])
    paths = [ds.target for ds in arm.SETS.values()]
    assert len(paths) == len(set(paths)), "two sets share a marked path"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            check(name, fn)
    for n in PASS:
        print("  ok    %s" % n)
    for f in FAIL:
        print("  FAIL  %s" % f)
    print("\n%d passed, %d failed" % (len(PASS), len(FAIL)))
    sys.exit(1 if FAIL else 0)
