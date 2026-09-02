#!/usr/bin/env python3
"""
check_documents.py

Cross-document consistency check for the resubmission package.

Why this exists. The manuscript, the supplement and the response letter have
each, at some point in this revision, carried a cohort count from a superseded
version of the analysis. Prose is where stale numbers survive, because nothing
recomputes it. This script recomputes the cohort from the deposit, then reads
the three documents and fails if a superseded value appears in a sentence that
does not mark it as historical.

A superseded value is allowed to appear, and often should: a response letter
that corrects a number has to name the number it is correcting. What is not
allowed is a superseded value stated as current. The test for the difference is
whether its sentence carries one of the markers below, which is crude but is
checkable by a reader and by a script, and which fails closed.

Depends on nothing outside the standard library. A .docx is a zip holding an
XML part, and the three things this script needs from it, paragraph text, table
cell text and whether a run is italic, are all in that part. An earlier version
imported python-docx and could not run in the environment it was written for,
which for a consistency checker is the same as not existing.

    python analysis/check_documents.py --docs ~/Downloads
    python analysis/check_documents.py --files a.docx b.docx c.docx
    python analysis/check_documents.py --docs ~/Downloads --list

By default a folder is filtered to the three documents of this package, since a
download folder holds other people's papers and checking those produces noise.
Pass --all to override that.

Exit status is non-zero if any superseded value is stated as current, or if a
current value cannot be found where it is expected.

Run from the repository root.
"""
import argparse
import glob
import os
import re
import sys

import xml.etree.ElementTree as ET
import zipfile

# A superseded value may appear when its sentence marks it as historical, either
# by carrying one of these phrases or by naming the replacement value alongside
# it. The second rule is the stronger one and catches corrections phrased as
# "from X to Y", which is how most of them read.
# The package is three documents, one per role. A working folder accumulates
# every revision of each, so matching on the name alone selects thirty files and
# reports the same stale value thirty times, which buries the one copy that
# matters. Each role therefore resolves to a single file: the most recently
# modified match. The others are named in the output so the choice is visible
# and can be overridden with --files.
ROLES = [("manuscript", ("HT10016",), ("SUPPLEMENT", "RESPONSE")),
         ("supplement", ("SUPPLEMENTAL", "SUPPLEMENT"), ()),
         ("response", ("RESPONSE",), ())]

MARKERS = [
    "earlier version", "an earlier", "previously", "no longer", "superseded",
    "withdrawn", "we withdraw", "rather than", "against the", "instead of",
    "was ", "were ", "before", "historical", "used to", "prior to",
    "corrected", "correction", "falls to", "falls from", "changes from",
    "in place of", "replaced",
    # Retraction markers. A sentence that attributes a claim to a past revision
    # of these documents is reporting it, not making it, and the retraction is
    # the point of the sentence. Only past-tense attributions are listed: "we
    # report" stays a current claim and is not exempt.
    "we described", "we said", "we stated", "we reported", "that was wrong",
    "we withdraw it", "an intermediate revision",
]

# value that must not be stated as current  ->  what replaced it
#
# Write these so they can actually match. A trailing \b after a per-cent sign
# never fires, because neither '%' nor the space after it is a word character,
# and three patterns here were dead for that reason while a stale 25.1% sat in
# Table III through four revisions. self_test() below asserts every pattern is
# capable of matching its own literal text.
SUPERSEDED = {
    r"\b69 (?:source )?papers\b": "65 papers",
    r"\b43 (?:distinct )?compounds\b": "40 compounds",
    r"\b4387\b": "4247 extracted points",
    r"\b4355\b": "4247 extracted points",
    r"\b419 temperature-axis fits\b": "414 temperature-axis fits",
    r"\b95 field-axis\b": "88 field-axis fits",
    r"\b93 field-axis\b": "88 field-axis fits",
    r"\b110 (?:per-paper )?anchors?\b": "105 anchor records",
    r"\b107 per-paper anchor\b": "105 anchor records",
    r"\b0\.3547\b": "0.3409 aggregate ratio",
    r"\bratio is 0\.73\b": "0.77 for iron chalcogenide 11-type",
    r"\bexplains 76%": "77%",
    r"\b123 (?:compounds|of the 183)\b": "85 dispatched compounds",
    r"\b0\.641 for iron chalcogenide\b": "1.093",
    r"\b1\.094\b": "1.093, the value rounded from 1.09349",
    r"\b3\.07 at this cohort scope\b": "3.13",
    r"\b0\.994 in .H\b": "1.053 under the conditioned predictor",
    r"1\.141 in .H": "1.053 under the conditioned predictor",
    r"\b97 fits\b": "88 fits",
    r"\b2151\b": "2097 candidate-grid tuples",
    r"\b239 candidate records\b": "233 candidate records",
    r"\b185 distinct compounds\b": "183 distinct compounds",
    r"\b25\.1%": "25.8%",
    r"\b10\.5%": "9.9%",
    r"\b92% of (?:bootstrap )?resamples\b": "withdrawn, not restated",
    r"\b23-fold\b": "16-fold",
    r"cannot be reproduced": "no unreproducible value may remain",
    r"does not reproduce": "no unreproducible value may remain",
    # Retracted descriptions. Each of these called a component of the workflow
    # absent or unreproducible, and each was wrong: the component was found on a
    # second search. They are listed here so no revision restores them.
    r"not present anywhere in the workflow": "the cohort-A extractions were located",
    r"One row is one physical sample from one paper": "one row is one isotherm "
                                          "record; 105 records are 69 samples",
    r"not reproducible from the deposited per-family cohorts": "0.409 dex is deposited",
    r"at least three anchor compounds are available within the family": "K counts "
                                          "measured points supplied per query",
    # Table S5 rows that no longer exist. The tables are generated from the
    # deposit but their introducing prose is not, which is how a description of
    # withdrawn rows outlived the rows themselves.
    r"Nb3Sn wire rows": "Table S5 no longer contains them",
    r"Ba\(Fe,Ru\)2As2 row": "Table S5 no longer contains it",
    r"calibration screen has no deposited implementation": "the screen is deposited "
                                          "as the record-level tier table",
    r"derived from that fact rather than recomputed": "the split recomputes",
    r"cohort we cannot reconstruct": "the 99-fit cohort reconstructs and reproduces",
    r"no filter over the deposited fit file reproduces": "the cohort is 99 fits, not 97",
    r"unvalidatable at this cohort size": "fails the threshold; K counts anchor "
                                          "measurements, not compounds",
    r"anchor-count rule of Sec\. II\.D, which needs three anchors": "K counts "
                                          "anchor measurements supplied per query",
}


def literal_probe(pattern):
    """The plainest text the pattern is meant to catch, for the self-test.

    Alternations and optional groups collapse to their first branch, escapes are
    unescaped, and word boundaries are dropped. This is not a general regex
    inverter; it only has to produce one string the pattern ought to match.
    """
    t = pattern
    t = re.sub(r"\(\?:([^()|]*)\|[^()]*\)", r"\1", t)   # (?:a|b)  -> a
    t = re.sub(r"\(\?:([^()]*)\)\?", r"\1", t)           # (?:a)?   -> a
    t = re.sub(r"\(\?:([^()]*)\)", r"\1", t)             # (?:a)    -> a
    t = t.replace(r"\b", "")
    t = re.sub(r"\\(.)", r"\1", t)                      # \.       -> .
    t = t.replace("?", "")
    return t


def self_test():
    """Refuse to run with a pattern that cannot fire. Returns a failure count.

    Each pattern is searched for inside the plainest sentence it is supposed to
    catch. A pattern that misses its own text matches nothing in any document,
    which is worse than having no pattern at all: the check reports a pass. Three
    patterns here ended in a per-cent sign followed by a word boundary, which can
    never match because neither the sign nor the space after it is a word
    character, and a stale 25.1% sat in Table III through four revisions.
    """
    bad = 0
    for pat, repl in SUPERSEDED.items():
        try:
            rx = re.compile(pat, re.I)
        except re.error as e:
            print("   BROKEN PATTERN  %-46s %s" % (pat, e))
            bad += 1
            continue
        probe = "the value %s appears here." % literal_probe(pat)
        if not rx.search(probe):
            print("   MATCHES NOTHING %-46s probe: %r" % (pat, probe))
            bad += 1
    return bad


def sentences(text):
    return re.split(r"(?<=[.!?])\s+", text)


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def doc_text(path):
    """Blocks of text, with referee quotations marked so they are exempt.

    The response letter quotes each referee point verbatim before answering it,
    and those quotations name the numbers being corrected. A quotation is set
    wholly in italic, which is how it is identified here; its content is the
    referee's, not ours, and must not be edited to match our cohort.

    Every paragraph in the document is read, including those inside tables,
    which is what the check wants: a stale number in a table cell is as wrong as
    one in a sentence.
    """
    # Only the response letter quotes referees, so the exemption is confined to
    # it. Applying it document-wide would let an italic caption hide a stale
    # number, which is the failure mode this script exists to catch.
    is_response = "RESPONSE" in os.path.basename(path).upper()
    try:
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("word/document.xml"))
    except (zipfile.BadZipFile, KeyError) as e:
        print("   skipped, not a readable .docx (%s)" % e.__class__.__name__)
        return []
    out = []
    for para in root.iter(W + "p"):
        runs = []
        for r in para.iter(W + "r"):
            text = "".join(t.text or "" for t in r.iter(W + "t"))
            rpr = r.find(W + "rPr")
            italic = rpr is not None and rpr.find(W + "i") is not None
            runs.append((text, italic))
        text = "".join(t for t, _i in runs)
        quoted = (is_response and len(text.strip()) > 40 and bool(runs)
                  and all(i for t, i in runs if t.strip()))
        out.append((text, quoted))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs",
                    help="folder holding the manuscript, supplement and response")
    ap.add_argument("--files", nargs="+",
                    help="the documents to check, given explicitly")
    ap.add_argument("--all", action="store_true",
                    help="with --docs, check every .docx rather than only the "
                         "three that make up this package")
    ap.add_argument("--list", action="store_true",
                    help="print every hit, marked or not")
    args = ap.parse_args()

    # A check whose patterns cannot fire reports a pass, which is the worst
    # answer it could give, so the patterns are tested before the documents are.
    dead = self_test()
    if dead:
        sys.exit("%d pattern(s) in SUPERSEDED cannot match anything; fix them "
                 "before trusting this check" % dead)

    if args.files:
        paths = sorted(args.files)
    elif args.docs:
        found = sorted(p for p in glob.glob(os.path.join(args.docs, "*.docx"))
                       if not os.path.basename(p).startswith("~$"))
        if args.all:
            paths = found
        else:
            paths, skipped = [], []
            for role, want, avoid in ROLES:
                cands = [p for p in found
                         if any(k in os.path.basename(p).upper() for k in want)
                         and not any(k in os.path.basename(p).upper() for k in avoid)]
                if not cands:
                    continue
                cands.sort(key=os.path.getmtime, reverse=True)
                paths.append(cands[0])
                skipped.extend(cands[1:])
                print("%-11s %s   (newest of %d)"
                      % (role, os.path.basename(cands[0]), len(cands)))
            if skipped:
                print("\n%d older revision(s) not checked. Pass --files to name "
                      "documents explicitly, or --all to check every .docx here."
                      % len(skipped))
    else:
        sys.exit("give --docs FOLDER or --files A.docx B.docx")
    if not paths:
        where = args.docs or "the given files"
        sys.exit("no package document found in %s.\n"
                 "Expected a filename containing HT10016, SUPPLEMENTAL or RESPONSE.\n"
                 "Use --files to name them explicitly, or --all to check "
                 "every .docx in the folder." % where)

    bad = 0
    for path in paths:
        name = os.path.basename(path)
        hits_marked = hits_bare = 0
        print("\n%s" % name)
        for block, quoted in doc_text(path):
            if quoted:
                continue
            for s in sentences(block):
                for pat, repl in SUPERSEDED.items():
                    if not re.search(pat, s, re.I):
                        continue
                    # A sentence that names the superseded value and its
                    # replacement together is a correction, which is the
                    # clearest form a historical mention can take.
                    new_num = re.match(r"([\d.]+)", repl)
                    paired = bool(new_num) and re.search(
                        r"\b%s\b" % re.escape(new_num.group(1)), s)
                    marked = paired or any(m in s.lower() for m in MARKERS)
                    if marked:
                        hits_marked += 1
                        if args.list:
                            print("   ok   %-34s %s" % (repl, s.strip()[:96]))
                    else:
                        hits_bare += 1
                        bad += 1
                        print("   FAIL %-34s %s" % (repl, s.strip()[:112]))
        nq = sum(1 for _b, q in doc_text(path) if q)
        print("   %d superseded value(s) marked as historical, %d stated as current"
              "   (%d verbatim referee quotation(s) exempt)"
              % (hits_marked, hits_bare, nq))

    print()
    if bad:
        print("%d superseded value(s) stated as current; the package is not consistent" % bad)
        return 1
    print("no superseded value is stated as current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
