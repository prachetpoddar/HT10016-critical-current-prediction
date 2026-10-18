#!/usr/bin/env python3
"""
apply_coauthor_review.py

Wording changes from co-author review of the version-59 manuscript, and one
count the earlier pass left behind.

The reviewed copy is text-identical to version 59, sentence for sentence, so
the review is comment-only. Five wording changes are applied:

  1. The abstract's two framing questions ran present then past. Both are
     present now.

  2. The refusal half of the diagnostic is stated as refraining from
     predicting rather than as staying silent.

  3. The goal is one sentence instead of two.

  4. The record definition is one sentence instead of two.

  5. Sec. II.A names the two plot readers, GPT-4o (OpenAI) for the curve-level
     extraction and Claude Opus 4.8 (Anthropic) for the second reading, which
     is how the artificial-intelligence disclosure already names them, so the
     two sections agree. It also says "company" rather than "organization",
     since the point is that the second reader comes from a different vendor.

One question from the review is left open in the text: whether "the authors
checked the outputs by hand" means all of them or one, which only the authors
can settle.

A sixth edit is not from the review. The Conclusion counted the conditioning
regimes on the deposited cohort and said two, while Sec. III.A was corrected
to three outcomes on 2026-10-09 and the Conclusion was missed. The
diagnostic's bands are three, sample-form dominant above 0.7, moderate from
0.3 to 0.7 and minor below 0.3, and the three families land in one each at
0.81, 0.37 and 0.04 on the repaired anchors, which is also why Sec. III.E
states three rules. The two now agree, and the pass asserts all three
statements of the count together.

    python3 analysis/apply_coauthor_review.py OUT_DIR
"""
import copy
import sys

import docx

sys.path.insert(0, "analysis")

from runs import replace                                    # noqa: E402

MANUSCRIPT = [
    # 1. Both questions in the present tense.
    ("which measurements are physically comparable, and were the "
     "normalization scales measured on the same specimen?",
     "which measurements are physically comparable, and whether the "
     "normalization scales are measured on the same specimen?"),

    # 2. Her phrase for the refusal half of the diagnostic.
    ("The answer tells the model both what to predict and when to stay "
     "silent.",
     "The answer tells the model both what to predict and when to refrain "
     "from predicting."),

    # 3. The goal, in one sentence.
    ("Our goal is concrete. We aim to predict, from published literature "
     "alone,",
     "Our concrete goal is to predict, from published literature alone,"),

    # 4. The record, in one sentence.
    ("Here each record is a curve. It is tied to a source paper, a physical "
     "sample, a sample form, and a fixed value of the other measurement "
     "axis.",
     "Here each record is a curve, tied to a source paper, a physical "
     "sample, a sample form, and a fixed value of the other measurement "
     "axis."),

    # Not hers. The Conclusion still counted the regimes on the deposited
    # cohort. Sec. III.A was corrected to three outcomes on 2026-10-09 and the
    # Conclusion was missed, so the paper said three in one place and two in
    # the other. The diagnostic's own bands are three, sample-form dominant
    # above 0.7, moderate from 0.3 to 0.7 and minor below 0.3, and the three
    # families land in one each at 0.81, 0.37 and 0.04 on the repaired
    # anchors, which is also why Sec. III.E states three rules.
    ("It assigns two distinct regimes across the studied families.",
     "It assigns three distinct regimes across the studied families."),

    # 5. The two readers, named as the disclosure names them.
    ("The first model read every figure under a constrained output schema, in "
     "three disambiguation passes. A second reader checks the reliability of "
     "that extraction. It is a model from a different organization and a "
     "different generation.",
     "The first model, GPT-4o (OpenAI), read every figure under a constrained "
     "output schema, in three disambiguation passes. A second reader checks "
     "the reliability of that extraction. It is Claude Opus 4.8 (Anthropic), "
     "a model from a different company and a different generation."),
]

GONE = ["were the normalization scales measured",
        "assigns two distinct regimes",
        "when to stay silent",
        "Our goal is concrete.",
        "Here each record is a curve. It",
        "a different organization and a different generation"]
KEPT = ["whether the normalization scales are measured on the same specimen",
        "It assigns three distinct regimes across the studied families.",
        # the two places the count has to agree with
        "The diagnostic yields three distinct outcomes",
        "Above 0.7 the family is treated as sample-form dominant, from 0.3 to "
        "0.7 as moderate, and below 0.3 as minor.",
        "when to refrain from predicting",
        "Our concrete goal is to predict",
        "Here each record is a curve, tied to a source paper",
        "The first model, GPT-4o (OpenAI), read every figure",
        "It is Claude Opus 4.8 (Anthropic), a model from a different company",
        # the disclosure the new names are taken from, unchanged
        "Curve-level extraction was performed by a single model, GPT-4o "
        "(OpenAI)",
        "A second independent reader, Claude Opus 4.8 (Anthropic)",
        # item 6, left for the authors to settle
        "the authors checked the outputs by hand against the source figures"]


def mark(paragraph, span):
    """Highlight one span, splitting the run it sits in.

    Four of the five edits land inside runs the highlighter had already
    marked, so they are visible in the editor's copy without anything further.
    The abstract's framing sentences were not marked, so the first edit came
    out unmarked while the others show. The marked copy exists to show this
    round's changes, and the as-submitted baseline the highlighter needs is
    not in the deposit, so this one span is marked here instead.
    """
    from docx.enum.text import WD_COLOR_INDEX
    for run in paragraph.runs:
        at = run.text.find(span)
        if at < 0:
            continue
        tail = run.text[at + len(span):]
        run.text = run.text[:at]
        new = copy.deepcopy(run._element)
        run._element.addnext(new)
        import docx.text.run as _r
        hot = _r.Run(new, paragraph)
        hot.text = span
        hot.font.highlight_color = WD_COLOR_INDEX.YELLOW
        rest = copy.deepcopy(run._element)
        new.addnext(rest)
        after = _r.Run(rest, paragraph)
        after.text = tail
        after.font.highlight_color = None
        return True
    return False


ABSTRACT_SPAN = ("and whether the normalization scales are measured on the "
                 "same specimen?")


def body(doc):
    out = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                out.extend(p.text for p in cell.paragraphs)
    return "\n".join(" ".join(t.split()) for t in out)


def marks(doc):
    """(highlighted runs, subscript runs), so an edit cannot quietly drop
    either. The manuscript here is the marked copy, and the marking is what
    the editor reads."""
    hot = sub = 0
    for para in doc.paragraphs:
        for run in para.runs:
            if str(run.font.highlight_color).startswith("YELLOW"):
                hot += 1
            if run.font.subscript:
                sub += 1
    return hot, sub


def main(out_dir):
    tag = out_dir.rstrip("/").split("/")[-1].replace("out_", "")
    ms = "%s/HT10016_revised_%s_HIGHLIGHTED.docx" % (out_dir, tag)

    doc = docx.Document(ms)
    before = marks(doc)
    for old, new in MANUSCRIPT:
        hits = [p for p in doc.paragraphs if old in p.text]
        if len(hits) != 1:
            sys.exit("%d paragraphs carry %r" % (len(hits), old[:60]))
        replace(hits[0], old, new)

    for para in doc.paragraphs:
        if para.text.strip().startswith("ABSTRACT") and \
                ABSTRACT_SPAN in para.text:
            if not mark(para, ABSTRACT_SPAN):
                sys.exit("the abstract edit could not be marked")
            break
    else:
        sys.exit("the abstract edit is not where it was expected")
    doc.save(ms)

    doc = docx.Document(ms)
    after = marks(doc)
    text = body(doc)
    for phrase in GONE:
        if phrase in text:
            sys.exit("the manuscript still carries %r" % phrase)
    for phrase in KEPT:
        if phrase not in text:
            sys.exit("the manuscript lost %r" % phrase)
    if after[1] != before[1]:
        sys.exit("subscript runs went from %d to %d" % (before[1], after[1]))
    if after[0] < before[0] - len(MANUSCRIPT):
        sys.exit("highlighted runs fell from %d to %d" % (before[0], after[0]))

    print("   %d of review edits applied" % len(MANUSCRIPT))
    print("   highlighted runs %d -> %d, subscript runs %d unchanged"
          % (before[0], after[0], after[1]))
    print("   left for the authors: who checked the 23 compounds by hand")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "out_final60"))
