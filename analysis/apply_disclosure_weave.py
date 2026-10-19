#!/usr/bin/env python3
"""
apply_disclosure_weave.py

Remove the standalone AI disclosure and place its content where APS puts it.

The policy splits placement: AI used in conducting the research is described
where the methods are, and anything else worth disclosing goes in the
acknowledgement statement. Most of the section already duplicated Sec. II.A,
which names GPT-4o and Claude Opus 4.8, says the models only read plots, and
says all fitting, aggregation, validation and prediction are deterministic
code. Three things were only in the section, and they move:

  the audit models, Claude Opus 5 and Claude Sonnet 5, into the sentence in
  Sec. II.A that reports the dual-model audit of the printed axis label;

  the deposition of the prompts, into the paragraph that describes how the
  second reader is prompted;

  the script assistance and the accountability statement, into
  ACKNOWLEDGMENTS, which is where the policy puts a use that is not part of
  conducting the research.

Reference [36], the Anthropic model documentation, was cited only inside the
section. Deleting it without moving the citation would have left an uncited
entry in the reference list, so [36] rides along with the model namings.

The section is removed last, after its content is confirmed present
elsewhere, so a failure part way through leaves the paper with a duplicate
rather than with a hole. That is the opposite of the order the earlier pass
used, which deleted first and took ACKNOWLEDGMENTS with it.
"""

import copy
import sys

import docx
from docx.oxml.ns import qn

sys.path.insert(0, "analysis")
from runs import replace  # noqa: E402

HEADING = "ARTIFICIAL INTELLIGENCE USE DISCLOSURE"

EDITS = [
    # the audit models, named where the audit is reported
    ("A dual-model audit of the printed axis label across the fitted cohort "
     "found",
     "A dual-model audit of the printed axis label across the fitted cohort, "
     "run by Claude Opus 5 and Claude Sonnet 5 (Anthropic) [36], found"),
    # the second reader keeps its citation, which the section used to carry
    ("It is Claude Opus 4.8 (Anthropic), a model from a different company",
     "It is Claude Opus 4.8 (Anthropic) [36], a model from a different "
     "company"),
    # the prompts, and their deposition
    ('and it is told that "no such data in this paper" is a correct and '
     'expected answer.',
     'and it is told that "no such data in this paper" is a correct and '
     'expected answer. The prompts are fixed per figure and per paper, and '
     'they are deposited with the data.'),
]

ACKNOWLEDGED = (
    " Large language models assisted in structuring the analysis scripts. "
    "The authors directed, reviewed and revised that work, and the authors "
    "take full responsibility for all content, analysis and conclusions."
)

# every one of these has to be in the manuscript when the pass finishes
MUST_SURVIVE = [
    "GPT-4o (OpenAI)",
    "Claude Opus 4.8 (Anthropic) [36]",
    "Claude Opus 5 and Claude Sonnet 5 (Anthropic) [36]",
    "they are deposited with the data",
    "Large language models assisted in structuring the analysis scripts",
    "The authors directed, reviewed and revised that work",
    "the authors take full responsibility for all content, analysis and "
    "conclusions",
    "the first author checked the outputs by hand against the source figures",
    "All curve grouping, fitting, aggregation, validation and prediction are "
    "performed by deterministic code",
]


def weave(doc):
    done = 0
    for old, new in EDITS:
        if any(new in p.text for p in doc.paragraphs):
            continue
        hit = [p for p in doc.paragraphs if old in p.text]
        assert len(hit) == 1, (old[:40], len(hit))
        replace(hit[0], old, new)
        done += 1
    return done


def acknowledge(doc):
    # index by position rather than by object: doc.paragraphs builds fresh
    # Paragraph wrappers on each access, so .index() on one of them fails
    ps = doc.paragraphs
    i = next(k for k, p in enumerate(ps)
             if p.text.strip().upper() == "ACKNOWLEDGMENTS")
    body = next(p for p in ps[i + 1:] if p.text.strip())
    if ACKNOWLEDGED.strip() in body.text:
        return False
    tail = body.text.strip()[-40:]
    replace(body, tail, tail + ACKNOWLEDGED)
    return True


def drop_section(doc):
    ps = doc.paragraphs
    start = next((i for i, p in enumerate(ps)
                  if p.text.strip().upper().startswith(HEADING)), None)
    if start is None:
        return 0
    end = next(i for i, p in enumerate(ps[start + 1:], start + 1)
               if p.style.name.startswith("Heading") and p.text.strip())
    for p in ps[start:end]:
        p._p.getparent().remove(p._p)
    return end - start


def verify(path):
    doc = docx.Document(path)
    # case-blind: a sentence that moved to the head of a paragraph is
    # capitalised there, and the pin was written from mid-sentence
    whole = " ".join(p.text for p in doc.paragraphs).lower()
    for phrase in MUST_SURVIVE:
        assert phrase.lower() in whole, "lost: %s" % phrase[:50]
    assert not any(p.text.strip().upper().startswith(HEADING)
                   for p in doc.paragraphs), "the section is still there"
    # every reference entry must still be cited somewhere in the body.
    # Citations come as lists and as ranges with an en dash, "[11-16]", so a
    # literal search for the number misses the ones inside a range: the first
    # version of this check reported [14] as uncited when it sits in [11-16].
    import re
    refs_at = next(i for i, p in enumerate(doc.paragraphs)
                   if p.text.strip().upper().startswith("REFERENCES"))
    body = " ".join(p.text for p in doc.paragraphs[:refs_at])
    cited = set()
    for token in re.findall(r"\[[0-9,\s\u2013\u2014-]+\]", body):
        for part in token.strip("[]").split(","):
            part = part.strip()
            m = re.match(r"^(\d+)\s*[\u2013\u2014-]\s*(\d+)$", part)
            if m:
                cited.update(range(int(m.group(1)), int(m.group(2)) + 1))
            elif part.isdigit():
                cited.add(int(part))
    for p in doc.paragraphs[refs_at:]:
        m = re.match(r"\[(\d+)\]", p.text.strip())
        if m:
            assert int(m.group(1)) in cited, \
                "reference [%s] is no longer cited" % m.group(1)


if __name__ == "__main__":
    for path in ("out_final60/HT10016_revised_final60.docx",
                 "out_final60/HT10016_revised_final60_HIGHLIGHTED.docx"):
        doc = docx.Document(path)
        edits = weave(doc)
        added = acknowledge(doc)
        doc.save(path)
        # only now, with the content confirmed in place, remove the section
        doc = docx.Document(path)
        here = " ".join(p.text for p in doc.paragraphs).lower()
        for phrase in MUST_SURVIVE:
            if phrase in ACKNOWLEDGED or "Opus 5" in phrase or "deposited" in phrase:
                assert phrase.lower() in here, phrase[:40]
        dropped = drop_section(doc)
        doc.save(path)
        verify(path)
        print("%-46s %d edit(s) in Sec. II.A, acknowledgment %s, %d paragraph(s) dropped"
              % (path.split("/")[-1], edits,
                 "extended" if added else "already extended", dropped))
