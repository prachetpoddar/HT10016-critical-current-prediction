"""
compact_response_letter.py

Shortens the response letter without dropping anything from it.

The letter had grown to 9781 words across 91 paragraphs, most of the growth in
the ten longest, and three of those ran past 500 words each. The referee-by-
referee structure is unchanged and every fact, number, concession and
cross-reference is kept. What is cut is restatement: framing sentences that
announce what the next sentence is about, a fact given twice in two
paragraphs of the same section, and phrasing that says at length what it can
say once.

Two things are deliberately not cut. The self-critical framing is the tone of
the letter and is kept at least once per section, because a reply that
withdraws this much and does not say so plainly reads worse, not better. And
every numeric token is preserved: the script asserts it, comparing the
multiset of numbers in the letter before and after, so a compaction that
silently drops a figure fails here rather than reaching a referee.

The replacement paragraphs are read from files rather than embedded, and the
paragraph they replace is located by its own text taken from the source
document rather than retyped, so no transcription error can enter.

Usage:
    python3 analysis/compact_response_letter.py IN_DIR OUT_DIR
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

MAIN = "HT10016_revised_final32.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final32.docx"
RESP = "RESPONSE_TO_REFEREES_final32.docx"
OUT = {MAIN: "HT10016_revised_final33.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final33.docx",
       RESP: "RESPONSE_TO_REFEREES_final33.docx"}

NEW = os.path.join("/tmp", "comp")
# paragraph index among the non-empty paragraphs, in document order
REPLACE = [4, 10, 16, 17, 20, 23, 27, 28, 34, 37, 38, 65, 66, 81, 83, 87]


def plain_paragraphs(doc):
    out = []
    for p in paragraphs(doc):
        t = unescape(plain(p)).strip()
        if t:
            out.append(t)
    return out


def numbers(s):
    """Every numeric token, with trailing punctuation stripped.

    Comparing raw matches made "Stages 1 and 2, from" differ from "Stages 1
    and 2 and from" on the token "2,", which is a change of punctuation and
    not of fact. The comparison is about figures, so the figures are what it
    compares.
    """
    return Counter(t.rstrip(",.") for t in
                   re.findall(r'\d[\d,]*\.?\d*%?', s))


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: compact_response_letter.py IN_DIR OUT_DIR")
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    for name in (MAIN, SUPP):
        shutil.copy(os.path.join(src, name), os.path.join(dst, OUT[name]))

    ip = os.path.join(src, RESP)
    if not os.path.exists(ip):
        sys.exit("missing input: %s" % ip)
    zin = zipfile.ZipFile(ip)
    doc = zin.read("word/document.xml").decode("utf-8")
    before = plain_paragraphs(doc)
    n_before = sum(len(p.split()) for p in before)
    nums_before = numbers(" ".join(before))

    for i in REPLACE:
        path = os.path.join(NEW, "new_%d.txt" % i)
        if not os.path.exists(path):
            sys.exit("missing replacement text: %s" % path)
        new = " ".join(open(path).read().split())
        old = before[i]
        hits = [p for p in paragraphs(doc) if unescape(plain(p)).strip() == old]
        if len(hits) != 1:
            sys.exit("paragraph %d matched %d times in the document, expected "
                     "exactly 1" % (i, len(hits)))
        out = replace_in_paragraph(hits[0], old, new)
        if out is None:
            sys.exit("could not place the replacement for paragraph %d" % i)
        doc = doc.replace(hits[0], out, 1)
        print("   [%2d] %4d -> %4d words" % (i, len(old.split()),
                                             len(new.split())))

    after = plain_paragraphs(doc)
    n_after = sum(len(p.split()) for p in after)
    nums_after = numbers(" ".join(after))
    if len(after) != len(before):
        sys.exit("the paragraph count changed from %d to %d; this script only "
                 "rewrites paragraphs" % (len(before), len(after)))
    # Paragraph 23 quoted the Figure 5 envelope crossing at a reduced field
    # of 0.59 with a gap of 0.40 dex. Figure 5's family parameters were
    # rebuilt on 2026-09-06 and the manuscript now says 0.58 and 0.69; the
    # letter had not been updated and nothing caught it, because the figure
    # checks compare images and the text checks compare the manuscript. This
    # is the one intended numeric change, so it is declared rather than
    # allowed through by loosening the comparison.
    ALLOWED_LOST = Counter({"0.59": 1, "0.40": 1})
    ALLOWED_GAINED = Counter({"0.58": 1, "0.69": 1})
    lost = nums_before - nums_after - ALLOWED_LOST
    gained = nums_after - nums_before - ALLOWED_GAINED
    if lost or gained:
        sys.exit("the compaction changed the numbers in the letter.\n"
                 "   dropped: %s\n   added:   %s"
                 % (dict(lost) or "none", dict(gained) or "none"))
    print("\n   the stale Figure 5 crossing is corrected: 0.59 to 0.58 and "
          "0.40 to 0.69 dex")
    print("   %d numeric tokens preserved exactly, %d distinct"
          % (sum(nums_after.values()), len(nums_after)))
    print("   %d words to %d, a reduction of %.1f%%"
          % (n_before, n_after, 100.0 * (n_before - n_after) / n_before))

    op = os.path.join(dst, OUT[RESP])
    tmp = op + ".part"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item, doc)
            else:
                zout.writestr(item, zin.read(item.filename))
    zin.close()
    shutil.move(tmp, op)
    for name in (MAIN, SUPP, RESP):
        print("   wrote %s" % os.path.join(dst, OUT[name]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
