"""
restructure_response_letter.py

Reorders the response letter so the results lead. Nothing is removed.

The problem, measured rather than asserted. At v33 the letter ran 17 pages.
Thirty-seven percent of its paragraphs contained a concession or a correction,
eleven opened by conceding, and six paragraphs in the whole document stated a
result with no apology attached. There was no page a referee could turn to that
said what the paper found. The manuscript does not have this property: 17
percent of its body paragraphs carry a withdrawal and two of 133 open with one,
so this is a defect in the reply and not in the paper.

Three changes.

  1. A section at the front, "What the paper establishes", stating the four
     claims with the evidence that carries them, and noting that every figure
     regenerates from the deposit and every printed count is asserted against
     it. The letter had never said either.

  2. Nine responses reordered so the answer comes first and the concession
     follows it. Every concession is kept, word for word where it was already
     brief. What changes is which sentence the referee reads first.

  3. The duplication between the referee responses and the audit sections is
     less than a reading suggested: of 23 numeric tokens shared between them
     most are small integers, and the genuine repeats are cohort counts that
     are legitimately cross-referenced. Rather than merge sections on a wrong
     premise, the two places that do repeat a whole finding are trimmed to a
     reference.

The numeric guard from analysis/compact_response_letter.py applies here too:
the multiset of numbers in the letter must be unchanged apart from those the
new section introduces, which are declared.

Usage:
    python3 analysis/restructure_response_letter.py IN_DIR OUT_DIR
"""
import os
import re
import shutil
import sys
import zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final33.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final33.docx"
RESP = "RESPONSE_TO_REFEREES_final33.docx"
OUT = {MAIN: "HT10016_revised_final34.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final34.docx",
       RESP: "RESPONSE_TO_REFEREES_final34.docx"}

NEW = "/tmp/restr"
REORDER = [9, 12, 14, 17, 22, 32, 34, 40, 60]
# The paragraph the new section is inserted before: the first line of the
# summary that currently opens the letter.
INSERT_BEFORE = "The central results survive and are stated more precisely."


def plain_paragraphs(doc):
    return [t for t in (unescape(plain(p)).strip() for p in paragraphs(doc))
            if t]


def numbers(s):
    return Counter(t.rstrip(",.") for t in
                   re.findall(r'\d[\d,]*\.?\d*%?', s))


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: restructure_response_letter.py IN_DIR OUT_DIR")
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    for name in (MAIN, SUPP):
        shutil.copy(os.path.join(src, name), os.path.join(dst, OUT[name]))

    ip = os.path.join(src, RESP)
    zin = zipfile.ZipFile(ip)
    doc = zin.read("word/document.xml").decode("utf-8")
    before = plain_paragraphs(doc)
    nums_before = numbers(" ".join(before))

    print("reordering so the answer leads\n")
    for i in REORDER:
        path = os.path.join(NEW, "new_%d.txt" % i)
        if not os.path.exists(path):
            sys.exit("missing replacement text: %s" % path)
        new = " ".join(open(path).read().split())
        old = before[i]
        if numbers(new) != numbers(old):
            sys.exit("paragraph %d changed its numbers; this step reorders "
                     "and does not rewrite figures.\n   dropped %s\n   added %s"
                     % (i, dict(numbers(old) - numbers(new)),
                        dict(numbers(new) - numbers(old))))
        hits = [p for p in paragraphs(doc) if unescape(plain(p)).strip() == old]
        if len(hits) != 1:
            sys.exit("paragraph %d matched %d times, expected exactly 1"
                     % (i, len(hits)))
        out = replace_in_paragraph(hits[0], old, new)
        if out is None:
            sys.exit("could not place the replacement for paragraph %d" % i)
        doc = doc.replace(hits[0], out, 1)
        print("   [%2d] opens: %s" % (i, " ".join(new.split()[:11])))

    after = plain_paragraphs(doc)
    if numbers(" ".join(after)) != nums_before:
        sys.exit("the reordering changed the letter's numbers")
    print("\n   every number preserved through the reordering")

    tmp = os.path.join(dst, OUT[RESP]) + ".part"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item, doc)
            else:
                zout.writestr(item, zin.read(item.filename))
    zin.close()
    shutil.move(tmp, os.path.join(dst, OUT[RESP]))

    # ---- the opening section, inserted with the document model -----------
    import docx
    path = os.path.join(dst, OUT[RESP])
    d = docx.Document(path)
    if any("What the paper establishes" in p.text for p in d.paragraphs):
        sys.exit("the letter already carries the opening section")
    hits = [p for p in d.paragraphs if p.text.strip().startswith(INSERT_BEFORE)]
    if len(hits) != 1:
        sys.exit("found %d paragraphs opening with %r, expected exactly 1"
                 % (len(hits), INSERT_BEFORE))
    anchor = hits[0]
    lines = [l.strip() for l in open(os.path.join(NEW, "opening.txt"))
             if l.strip()]
    for l in lines:
        p = anchor.insert_paragraph_before(l)
        p.style = anchor.style
    d.save(path)

    d = docx.Document(path)
    words = sum(len(p.text.split()) for p in d.paragraphs)
    print("   inserted the opening section, %d paragraphs, %d words"
          % (len(lines), sum(len(l.split()) for l in lines)))
    print("   the letter is now %d words in %d paragraphs"
          % (words, len([p for p in d.paragraphs if p.text.strip()])))
    for name in (MAIN, SUPP, RESP):
        print("   wrote %s" % os.path.join(dst, OUT[name]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
