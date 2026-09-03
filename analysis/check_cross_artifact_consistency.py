#!/usr/bin/env python3
"""Check the manuscript, supplement and response letter against the deposit.

Nothing checked the four artifacts against each other. The response letter in
particular was never touched by any cohort correction and went on quoting a
16-fold conditioning figure the manuscript had abandoned, which is worse than
saying nothing because a referee checks the letter against the paper.

This scans every artifact for strings that a cohort change makes wrong, and for
the current values that should have replaced them. It is deliberately a string
scan rather than a semantic one: the failure mode here has always been a number
surviving in a sentence nobody reread, and a string scan is what catches that.

Two kinds of hit are expected and are listed as allowed: a superseded number
quoted inside a referee's own words, which must not be edited, and a number that
happens to appear as part of a DOI or a data value.

    python analysis/check_cross_artifact_consistency.py --dir <folder>
"""
import argparse
import os
import re
import sys
import zipfile

# string -> why it is stale
STALE = {
    "16-fold": "conditioning claim, superseded by leave-one-substructure-out",
    "4.7-fold": "same",
    "419 temperature": "temperature-axis fits, now 260",
    "4387": "extracted points, now 4146",
    "4247": "extracted points, an older value",
    "4211": "extracted points, superseded by 4146",
    "110 per-paper": "anchor rows, now 96",
    "103 per-paper": "anchor rows, superseded by 96",
    "2615": "archive size, now 2594 papers",
    "Twenty-nine of the 33": "source composition, now eighteen of the 20",
    "69 contributing": "cohort, now 62",
    "43 distinct": "compounds, now 38",
    "ratio is 0.73": "chalcogenide sample-form ratio, now 0.77",
    "ratio is 0.60": "122 sample-form ratio, now 0.35",
    "62% of the residual": "now 59%",
    "44% of the cohort": "now 43%",
    "44% of the substructure": "now 43%",
    "HBCCO": "withdrawn from the cohort",
    "the 44 markers": "Fig. 3 markers, now 34",
    "95 field-axis": "passing field-axis fits, now 94",
    "17 source papers": "field-axis source papers, now 16",
    "0.994": "per-paper leave-one-out, superseded",
    "0.261": "chalcogenide temperature-axis leave-one-out, now 0.588",
    "1.092": "122 temperature-axis leave-one-out, now 1.314",
    "1.721": "1111 temperature-axis leave-one-out, now 3.120",
    "0.641": "chalcogenide field-axis leave-one-out, now 1.093",
    "5.13": "1111 expanded-diversity value, cohort not deposited",
}

# hits that are correct and must stay
ALLOWED = [
    (re.compile(r"yet another number, 69 papers"),
     "quoted from the referee's own report"),
    (re.compile(r"10\.1016"), "a DOI prefix, not a count"),
    (re.compile(r"3\.079"), "a deposited data value"),
    (re.compile(r"such as 10\.10 read as"),
     "describes the superseded presentation"),
    (re.compile(r"quoted 0\.994 against a pre-expansion"),
     "names the withdrawn figures explicitly as withdrawn"),
    (re.compile(r"ratio of 10\.10 to 0\.43"),
     "names the superseded comparison in past tense"),
]


def docx_text(path):
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf8", "ignore")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x))


def plain_text(path):
    return re.sub(r"\s+", " ", open(path, encoding="utf-8", errors="ignore").read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    args = ap.parse_args()

    artifacts = [
        ("manuscript", "HT10016_revised_corrected.docx", docx_text),
        ("supplement", "SUPPLEMENTAL_MATERIAL_revised_corrected.docx", docx_text),
        ("response letter", "RESPONSE_TO_REFEREES_corrected.docx", docx_text),
        ("response letter, markdown", "RESPONSE_TO_REFEREES_corrected.md",
         plain_text),
    ]
    failures = 0
    for label, name, reader in artifacts:
        path = os.path.join(args.dir, name)
        if not os.path.exists(path):
            print("%-26s MISSING  %s" % (label, path))
            failures += 1
            continue
        text = reader(path)
        bad = []
        for token, why in STALE.items():
            for m in re.finditer(re.escape(token), text):
                window = text[max(0, m.start() - 90):m.end() + 90]
                if any(a.search(window) for a, _ in ALLOWED):
                    continue
                bad.append((token, why, window.strip()))
        if bad:
            failures += 1
            print("%-26s %d stale string(s)" % (label, len(bad)))
            for token, why, window in bad:
                print("   %-24s %s" % (token, why))
                print("      ...%s..." % window[:150])
        else:
            print("%-26s clean" % label)

    print()
    if failures:
        print("%d artifact(s) carry a superseded value." % failures)
        return 1
    print("all four artifacts agree with the deposit on every tracked quantity")
    return 0


if __name__ == "__main__":
    sys.exit(main())
