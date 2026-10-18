#!/usr/bin/env python3
"""
apply_rebuild_caveat.py

Two corrections found by checking the final60 set against the deposit.

1. The response letter printed the pre-withdrawal permutation probability as
   0.358. The deposit records 0.355, in
   audit/retrace_20260906/temperature_axis_separation.md, and 0.358 appears
   nowhere in the deposit as that quantity. The submitted draft said 0.355, so
   a digit moved somewhere in the drafts between.

2. Section III.C cited the pixel-trace rebuild only where it supports the
   paper: "They give 0.359 with a permutation probability of 0.037. The
   separation therefore holds under an independent extraction of the figures
   behind it." The same rebuild also contradicts the applicability bound stated
   earlier in the same section, and an earlier draft said so. Running
   analysis/temperature_axis_cohorts.py prints both halves:

       The separation holds on both exponent sets, at 0.007 and 0.037 ...
       The applicability result does not. Every family clears the threshold
       of 1 on the deposited exponents ... On the rebuilt exponents none
       clears it per fit ... the median moves from 1.285 to 2.576, while the
       deposited cohort restricted to the 16 shared papers still gives 1.277.

   Citing one half of a result the deposit publishes whole is the kind of thing
   a referee holding the deposit finds in one command. The second half goes
   back in, beside the first.

Every figure below is from the deposit: 0.42 and the fourteen scorable traces
from audit/temperature_axis_adjudicated_20260905.md, the three errors and the
two medians from analysis/temperature_axis_cohorts.py.

The highlighted copies carry the revision marks, and the anchor sentence is
already yellow there, so the inserted span inherits the mark from the run it
starts in.
"""

import sys

import docx

sys.path.insert(0, "analysis")
from runs import replace  # noqa: E402

ANCHOR = (
    "The separation therefore holds under an independent extraction of the "
    "figures behind it."
)

ADDED = (
    " The same rebuild does not support the applicability bound. Of the "
    "seventeen figures traced, fourteen can be scored, and none of them "
    "reproduces its deposited exponent. The median ratio of refitted to "
    "deposited exponent is 0.42. On the rebuilt exponents the three compound "
    "leave-one-out errors are 1.435, 1.184 and 2.415, all above the threshold "
    "rather than below it. The cause is the exponents and not the composition. "
    "The deposited cohort restricted to the same sixteen papers still gives a "
    "median exponent of 1.277, against the rebuild's 2.576."
)

LETTER_OLD = "a variance fraction of 0.107 and a probability of 0.358"
LETTER_NEW = "a variance fraction of 0.107 and a probability of 0.355"


def paragraph_with(doc, text):
    for paragraph in doc.paragraphs:
        if text in "".join(r.text for r in paragraph.runs):
            return paragraph
    raise ValueError("no paragraph carries %r" % text[:60])


def do_manuscript(path):
    doc = docx.Document(path)
    paragraph = paragraph_with(doc, ANCHOR)
    assert ADDED.strip() not in "".join(r.text for r in paragraph.runs)
    replace(paragraph, ANCHOR, ANCHOR + ADDED)
    doc.save(path)


def do_letter(path):
    doc = docx.Document(path)
    paragraph = paragraph_with(doc, LETTER_OLD)
    replace(paragraph, LETTER_OLD, LETTER_NEW)
    doc.save(path)


def verify_manuscript(path, marked):
    from docx.enum.text import WD_COLOR_INDEX
    doc = docx.Document(path)
    paragraph = paragraph_with(doc, ANCHOR)
    text = "".join(r.text for r in paragraph.runs)
    assert ANCHOR + ADDED in text, "the addition did not land after the anchor"
    for token in ("0.42", "1.435", "1.184", "2.415", "1.277", "2.576"):
        assert token in text, token
    if marked:
        yellow = "".join(
            r.text for r in paragraph.runs
            if r.font.highlight_color == WD_COLOR_INDEX.YELLOW
        )
        assert ADDED.strip() in yellow, "the addition is not marked"


def verify_letter(path):
    doc = docx.Document(path)
    text = "\n".join(p.text for p in doc.paragraphs)
    assert LETTER_NEW in text
    assert "0.358" not in text, "an 0.358 survives in the letter"


if __name__ == "__main__":
    do_manuscript("out_final60/HT10016_revised_final60.docx")
    do_manuscript("out_final60/HT10016_revised_final60_HIGHLIGHTED.docx")
    do_letter("out_final60/RESPONSE_TO_REFEREES_final60.docx")
    verify_manuscript("out_final60/HT10016_revised_final60.docx", False)
    verify_manuscript("out_final60/HT10016_revised_final60_HIGHLIGHTED.docx", True)
    verify_letter("out_final60/RESPONSE_TO_REFEREES_final60.docx")
    print("manuscript: the rebuild caveat is in Sec. III.C, clean and marked")
    print("letter:     0.358 -> 0.355")
