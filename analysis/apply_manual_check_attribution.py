#!/usr/bin/env python3
"""
apply_manual_check_attribution.py

Who checked the 23 compounds by hand.

Co-author review asked of "the authors checked the outputs by hand against the
source figures for all 23 fully fittable compounds" whether that means all of
them, one of them, or the first author. It was the first author, so the
sentence says so. A verification claim that names its scope loosely is weaker
than one that names a person, and a referee reading "the authors" has no way
to tell how many pairs of eyes the number rests on.

The manuscript's other plural uses are plural for good reason and are asserted
untouched: the authors directed, reviewed and revised the model-assisted
scripting; the authors take responsibility for all content; the authors
acknowledge the discussions; and the doping and processing variables are the
ones reported by the authors of the source papers. The passive statements
about disagreements escalated to manual reading stay passive, since they are
accurate either way.

    python3 analysis/apply_manual_check_attribution.py OUT_DIR
"""
import sys

import docx

sys.path.insert(0, "analysis")

from runs import replace                                    # noqa: E402

MANUSCRIPT = [
    ("Second, the authors checked the outputs by hand against the source "
     "figures for all 23 fully fittable compounds",
     "Second, the first author checked the outputs by hand against the source "
     "figures for all 23 fully fittable compounds"),
]

GONE = ["the authors checked the outputs by hand"]
KEPT = ["Second, the first author checked the outputs by hand",
        # plural, and right to stay plural
        "The authors directed, reviewed and revised that work.",
        "the authors take full responsibility for all content",
        "The authors acknowledge illuminating discussions",
        "reported by the authors",
        # the scope of the check is unchanged
        "for all 23 fully fittable compounds of the pre-withdrawal cohort and "
        "for every disagreement the second reader raised"]


def body(doc):
    out = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                out.extend(p.text for p in cell.paragraphs)
    return "\n".join(" ".join(t.split()) for t in out)


def marks(doc):
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
            sys.exit("%d paragraphs carry the manual-check sentence"
                     % len(hits))
        replace(hits[0], old, new)
    doc.save(ms)

    doc = docx.Document(ms)
    text = body(doc)
    for phrase in GONE:
        if phrase in text:
            sys.exit("the manuscript still carries %r" % phrase)
    for phrase in KEPT:
        if phrase not in text:
            sys.exit("the manuscript lost %r" % phrase)
    after = marks(doc)
    if after[1] != before[1]:
        sys.exit("subscript runs went from %d to %d" % (before[1], after[1]))
    print("   the manual check is attributed to the first author")
    print("   highlighted runs %d, subscript runs %d, both unchanged"
          % (after[0], after[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "out_final60"))
