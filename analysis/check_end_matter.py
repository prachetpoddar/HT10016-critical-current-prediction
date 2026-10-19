#!/usr/bin/env python3
"""
check_end_matter.py

The end matter must still be there.

On 2026-10-19 a pass that shortened the AI disclosure removed every paragraph
between that heading and DATA AVAILABILITY. ACKNOWLEDGMENTS sat between them,
so the pass deleted it: two named colleagues, an NSF award, a DARPA award and
two compute allocations, gone from the manuscript with every other check
still passing. Funding acknowledgements are an obligation to the funder, and
nothing was watching them.

This checks the things whose absence is silent: that each end-matter heading
is present, in order, with a non-empty body, and that the funding strings
survive. It is cheap enough to run on every build.

    python3 analysis/check_end_matter.py OUT_DIR
"""

import glob
import os
import sys

import docx

ORDER = ["IV. CONCLUSION",
         "ARTIFICIAL INTELLIGENCE USE DISCLOSURE",
         "ACKNOWLEDGMENTS",
         "DATA AVAILABILITY",
         "REFERENCES"]

# award and allocation identifiers, which no edit has a reason to touch
FUNDING = ["Alexander Balandin", "Aashman Mehta", "#2610404", "#D26AC50023",
           "PHY260151", "NAIRR260036"]


def check(path):
    doc = docx.Document(path)
    ps = [(p.style.name, p.text.strip()) for p in doc.paragraphs]
    whole = " ".join(t for _, t in ps)
    bad = []

    seen = []
    for k, (style, text) in enumerate(ps):
        if style.startswith("Heading") and text.upper() in ORDER:
            seen.append((ORDER.index(text.upper()), k, text.upper()))
    present = [name for _, _, name in seen]
    for name in ORDER:
        if name not in present:
            bad.append("missing heading: %s" % name)
    ranks = [r for r, _, _ in seen]
    if ranks != sorted(ranks):
        bad.append("headings out of order: %s" % present)

    for _, k, name in seen:
        if name == "REFERENCES":
            continue
        body = next((t for _, t in ps[k + 1:k + 5] if t), "")
        if not body:
            bad.append("empty section: %s" % name)

    for phrase in FUNDING:
        if phrase not in whole:
            bad.append("funding text gone: %s" % phrase)

    for line in bad:
        print("   FAIL %s" % line)
    if not bad:
        print("   ok   %d heading(s) in order, %d funding string(s) present"
              % (len(seen), len(FUNDING)))
    return not bad


def main(out_dir):
    paths = sorted(glob.glob(os.path.join(out_dir, "HT10016_revised_*.docx")))
    if not paths:
        print("no manuscript in %s" % out_dir)
        return 1
    ok = True
    for path in paths:
        print(os.path.basename(path))
        ok = check(path) and ok
    print("\nend matter %s" % ("intact" if ok else "IS NOT INTACT"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "out_final60"))
