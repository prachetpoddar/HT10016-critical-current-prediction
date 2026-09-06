"""
move_audit_to_supplement.py

Moves the letter's self-audit trace into the Supplemental Material and leaves a
summary in its place, B7.

The response letter carried about 1650 words of audit narrative under "Changes
we made on our own": the critical-field scale audit and the rebuild that could
not be completed, the eleven withdrawn papers, the transition-temperature
lookup table, the applicability window applied to one axis, the interaction the
extracted curves do not carry, and the dispatch generator that did not
reproduce its own output. Every one is a finding a referee should be able to
check. None of them is an answer to a question either referee asked.

They move to Section 17 of the Supplemental Material, which is where the audit
material already lives: Section 13 carries the critical-field provenance audit
and Section 16 the disposition of all 94 field-axis fits. The letter keeps a
summary of what the audit found and what it changed, and points to the section
for the evidence.

The letter loses about 1220 words and nothing is lost from the submission.

Usage:
    python3 analysis/move_audit_to_supplement.py IN_DIR OUT_DIR
"""
import os
import re
import shutil
import sys
import zipfile

MAIN = "HT10016_revised_final42.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final42.docx"
RESP = "RESPONSE_TO_REFEREES_final42.docx"
OUT = {MAIN: "HT10016_revised_final43.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final43.docx",
       RESP: "RESPONSE_TO_REFEREES_final43.docx"}

P_RE = re.compile(r"<w:p\b(?:[^>]*/>|.*?</w:p>)", re.S)


def blocks(doc):
    return P_RE.findall(doc)


def flat(block):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", block)).strip()


# The paragraphs that move, identified by their opening words. Each must match
# exactly one paragraph of the letter, which is checked before anything is
# written: a prefix that matched two blocks would silently move the wrong one.
MOVE = [
    "Tracing Referee A's two observations led to a retrospective audit",
    "We attempted a rebuild against a properly temperature-resolved",
    "A further audit of the anchors and the fitting protocol",
    "The audit of the critical-field scale described above did not stop",
    "Eleven papers were withdrawn and one table was not updated.",
    "The temperature-axis fit count in Table I reflects those withdrawals.",
    "The critical-temperature anchor is a lookup table, not a paper-reported",
    "Opening the papers, six of the eighteen on the temperature axis",
    "We have replaced every anchor we could check with the value",
    "The applicability window was applied to one axis and not the other.",
    "The field condition contains nothing independent of its own scale.",
    "The extracted curves carry less structure than the figures",
    "This matters for the exponent that the field axis reports.",
    "The deposited prediction file did not reproduce from its own generator",
]

# What replaces the letter's opening line of that section.
SUMMARY = (
    "We report these because they matter to the results, and because a referee "
    "would reasonably ask why several numbers have moved. Section 17 of the "
    "Supplemental Material carries the trace with the evidence for each "
    "finding; below is what it found and what it changed."
)

SUMMARY_2 = (
    "Tracing Referee A's two observations led to a retrospective audit of the "
    "critical-field scale. Sixteen field-axis papers were read independently by "
    "two vision-language models of a later generation than the pair used for "
    "extraction. For eight of the sixteen, both models reported that the paper "
    "contains no plot of critical field against temperature, while the pipeline "
    "held extracted values for all eight. Across the cohort the assigned scale "
    "barely exceeds the largest field measured on the curve it anchors, at a "
    "median ratio of 0.88, which is how a scale read from a curve endpoint "
    "behaves and not how an independently measured critical field behaves. We "
    "attempted a rebuild against a temperature-resolved scale and could not "
    "complete it: of 29 candidate papers read and span-tested, only the MgB2 "
    "class clears the three-paper threshold we set beforehand, and the 122-type "
    "family, which needed the evidence most, yielded nothing. We report that as "
    "a finding rather than an obstacle, since it is the comparability principle "
    "of this paper applied one level down."
)

SUMMARY_3 = (
    "Continuing that audit turned up five further defects, four of them in "
    "places we had not looked. Eleven papers were withdrawn from the "
    "temperature-axis cohort after we opened their figures, and one table was "
    "not updated with them, so Table I was internally inconsistent and the "
    "extracted-point count was overstated by 843. The transition-temperature "
    "anchor is a lookup table with per-substructure defaults rather than the "
    "paper-reported value the deposit labels it; six of the eighteen "
    "temperature-axis papers are wrong by 5 K or more, and we have replaced "
    "every anchor we could check with the value the paper prints. The "
    "applicability window was imposed on the temperature axis and not on the "
    "field axis, where nineteen of the 94 fits sat above the stated bound; it "
    "is now applied to both, and we say plainly that its field clause contains "
    "nothing independent of its own scale. The extracted curves carry four to "
    "twenty times less interaction between the temperature and field "
    "dependences than pixel traces of the same printed figures, which is why "
    "the field exponent now carries the qualification it does. And the "
    "deposited prediction file did not reproduce from its own generator, and "
    "now does: a scope rule had been applied to the file and never written "
    "into the code, and three of the four scripts that produce the table were "
    "named nowhere. One script now runs all four in order and compares the "
    "result with the released file cell by cell. Regenerating moved two "
    "printed numbers, the spread at 4.2 K and 5 T from 0.0098 dex to 0.0085 "
    "and at 20 K and 5 T from 0.259 to 0.254, and changed nothing else."
)

SUPP_HEADING = ("17. Audit of the anchors, the fitting protocol and the "
                "dispatch generator")
SUPP_INTRO = (
    "This section carries the trace behind the summary given in the response "
    "to referees. Six findings, each with the evidence for it. Section 13 "
    "above reports the critical-field provenance audit these follow from, and "
    "Section 16 the disposition of every field-axis fit they reach."
)


def para(text):
    esc = (text.replace("&", "&amp;").replace("<", "&lt;")
               .replace(">", "&gt;"))
    return "<w:p><w:r><w:t xml:space=\"preserve\">%s</w:t></w:r></w:p>" % esc


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: move_audit_to_supplement.py IN_DIR OUT_DIR")
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)

    # ---- the letter ---------------------------------------------------
    ip = os.path.join(src, RESP)
    zin = zipfile.ZipFile(ip)
    doc = zin.read("word/document.xml").decode("utf-8")
    bl = blocks(doc)
    moved, moved_words = [], 0
    for prefix in MOVE:
        hits = [b for b in bl if flat(b).startswith(prefix)]
        if len(hits) != 1:
            sys.exit("the letter has %d paragraph(s) starting %r, expected 1"
                     % (len(hits), prefix[:60]))
        moved.append(hits[0])
        moved_words += len(flat(hits[0]).split())
    for b in moved:
        if doc.count(b) != 1:
            sys.exit("a paragraph to move is not unique in the document XML")
        doc = doc.replace(b, "", 1)

    old_line = [b for b in bl if flat(b).startswith(
        "We report these because they matter to the results")]
    if len(old_line) != 1:
        sys.exit("could not find the section's opening line, found %d"
                 % len(old_line))
    doc = doc.replace(old_line[0],
                      para(SUMMARY) + para(SUMMARY_2) + para(SUMMARY_3), 1)
    print("   letter: moved %d paragraphs, %d words, and left %d in their place"
          % (len(moved), moved_words,
             len((SUMMARY + SUMMARY_2 + SUMMARY_3).split())))
    write(zin, doc, os.path.join(dst, OUT[RESP]))

    # ---- the supplement -------------------------------------------------
    ip = os.path.join(src, SUPP)
    zin = zipfile.ZipFile(ip)
    doc = zin.read("word/document.xml").decode("utf-8")
    if "17. Audit of the anchors" in doc:
        sys.exit("the supplement already carries a Section 17")
    tail = "<w:sectPr/></w:body>"
    if doc.count(tail) != 1:
        sys.exit("could not find the supplement's body end")
    added = ("<w:p/>" + para(SUPP_HEADING) + para(SUPP_INTRO)
             + "".join(moved))
    doc = doc.replace(tail, added + tail, 1)
    print("   supplement: appended Section 17 with %d paragraphs" % len(moved))
    write(zin, doc, os.path.join(dst, OUT[SUPP]))

    # ---- the manuscript, carried through unchanged ----------------------
    shutil.copy2(os.path.join(src, MAIN), os.path.join(dst, OUT[MAIN]))
    print("   wrote %s" % os.path.join(dst, OUT[MAIN]))
    return 0


def write(zin, doc, op):
    tmp = op + ".part"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item, doc)
            else:
                zout.writestr(item, zin.read(item.filename))
    zin.close()
    shutil.move(tmp, op)
    print("   wrote %s" % op)


if __name__ == "__main__":
    sys.exit(main())
