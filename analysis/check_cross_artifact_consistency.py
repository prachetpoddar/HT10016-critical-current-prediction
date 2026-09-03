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
    # The candidate-dispatch accounting, which Table IV and the Fig. 1 caption
    # carried through the whole revision because no check reads a figure.
    "185 distinct": "candidate compounds, now 183",
    "185 candidates": "candidate compounds, now 183",
    "239 / 185 / 125": "Table IV combined row, now 233 / 183 / 85",
    "55 / 31 / 31": "Table IV chalcogenide row, now 49 / 29 / 0",
    "79 / 51 / 9": "Table IV 122 row, now 79 / 51 / 0",
    "125 compounds receive": "dispatched compounds, now 85",
    "25.1%": "Hc2-unavailable refusal share, now 25.8%",
    "10.5%": "above-Tc refusal share, now 9.9%",
    "for want of a critical-field anchor":
        "one refusal code of four, and not the largest",
    # Sec. III.E as it read before the reduced-field gate closed two of the
    # three dispatch families. These were carried as outstanding while the
    # passages were rewritten; they are ordinary stale tokens now.
    "185 candidate compounds": "candidate compounds, now 183",
    "125 of the 185": "dispatched compounds, now 85 of 183",
    "123 rather than 125": "the outlier screen no longer changes the count",
    "Of the 185, 125": "dispatched compounds, now 85 of 183",
    "239 candidate records": "candidate records, now 233",
    "Of the 239 records": "candidate records, now 233",
    "179 of the 239": "Hc2 coverage, now 173 of 233",
    "2151 candidate-grid tuples": "now 2097",
    "218 are retained": "retained after the calibration screen, now 212",
    "0.39 dex": "pre-gate interval width, now 0.82 dex over the emitted rows",
    "0.19 dex": "half the pre-gate width, now 0.41 dex",
    "identical to nine decimal places":
        "the within-family spread is 0.0098 dex, not identity",
    "lowest evaluated field of 0.1 T":
        "every target at 0.1 T is refused; the emitted grid is 5 T",
    "one-sigma uncertainty of about 0.10 dex":
        "derived from the pre-gate width, now 0.21 dex",
    # Found by adversarial review after the gate went in. The checker printed
    # "all four artifacts agree" while these sat in the .docx, every one of
    # them falsified by the reduced-field gate the checker was written for.
    "0.002 and 0.3": "pre-gate reduced-field range; every emitted row is at "
                     "0.3226",
    "reduced fields of order 0.01": "Assumption 1, contradicted by Sec. III.E "
                                    "in the same document",
    "barely above the 0.3 bound": "compares one evaluation point against a "
                                  "bound defined on a fitted curve's field "
                                  "SPAN; a point has no span",
    "87 of 186 fits": "field-axis fits, now 61 of 159",
    "99 fits where a paper-derived value": "now 98",
    "median factor of 5.2 smaller": "now 6.43",
    "29 of the 33 source papers": "now eighteen of the 20",
    "0.012, 0.005, and 0.055 dex": "pre-gate field shifts",
    "factor of about 2.5 in the critical current":
        "the interval is 0.82 dex, a factor of 6.7",
    "the 125 the dispatch routine emits": "now 84",
    "53 chalcogenide": "that family now emits nothing",
    "37 iron pnictide 122-type records": "that family now emits nothing",
    # The temperature-window gate, which refused 93 targets and moved every
    # number derived from the emitted set.
    # The classifier correction: four anchor rows left other_unclassified.
    "0.7687": "chalcogenide ratio before the classifier fix, now 0.3737",
    "ratio is 0.77": "chalcogenide ratio, now 0.37",
    "explains 73%": "chalcogenide share, now 37%",
    "60% for iron pnictide": "the 122 share, pre-withdrawal; now 49%",
    "77%, 35%, and 12%": "now 37%, 49% and 12%",
    "three distinct regimes": "two remain, B and C",
    "three distinct outcomes": "two remain, B and C",
    "conditioning is mandatory": "no family now requires it outright",
    "conditioning is essential": "no family now requires it outright",
    "52 of the 96": "anchors in the plotted families, now 56 of 96",
    "34 markers": "now 37",
    "0.82 dex": "interval width before the temperature gate, now 0.61",
    "factor of about 6.7": "now about 4.1",
    "0.41 dex around each curve": "Fig. 5 half-width, now 0.31",
    "one-sigma uncertainty of about 0.21 dex": "now 0.16",
    "256 predictions": "emitted targets, now 163",
    "90 of the 186 fits": "now 89 of 159",
    "29 of the 33 temperature-axis": "the cohort holds 20 papers",
    "233 / 183 / 85": "Table IV combined row, now 233 / 183 / 84",
    "105 / 103 / 85": "Table IV MgB2 row, now 105 / 103 / 84",
}

# Tokens that ARE stale and have NOT been corrected yet, listed so that the
# script reports them as outstanding rather than either hiding them or failing
# the run. Everything here belongs to one block: the candidate-dispatch
# accounting, which the reduced-field gate changed and which cannot be
# corrected by swapping numbers because two of the three dispatch families now
# emit nothing at all. Moving a token out of here and into STALE is what
# records that the passage has actually been rewritten.
OUTSTANDING = set()   # every passage below has now been rewritten

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
    (re.compile(r"Why not 0\.39 dex\?"),
     "quoted verbatim from the referee's own report"),
]


def repeated_phrases(text, n=8, min_chars=40):
    """Immediately repeated phrases, which is how a bad edit shows up.

    An edit whose find string is a PREFIX of its replacement matches its own
    output on a second run and appends the new clause twice. That happened to
    the Fig. 5 caption, which read "...which at present is the MgB2 class
    alone, which at present is the MgB2 class alone,". No check saw it: every
    number was right and no tracked token was present. This one reads the
    sentence instead of the numbers.
    """
    w = re.sub(r"\s+", " ", text).split(" ")
    out = []
    for i in range(len(w) - 2 * n):
        a, b = " ".join(w[i:i + n]), " ".join(w[i + n:i + 2 * n])
        if a == b and len(a) >= min_chars:
            out.append(a)
    return sorted(set(out))


def docx_text(path):
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf8", "ignore")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x))


def plain_text(path):
    return re.sub(r"\s+", " ", open(path, encoding="utf-8", errors="ignore").read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    # Outstanding items fail the run by default. An earlier version printed
    # them and returned 0, which meant the script could enumerate eight known
    # contradictions and still say the artifacts agree. A gate that goes green
    # on a run that has just listed contradictions cannot be wired into
    # anything. Pass --allow-outstanding to run it as a report instead.
    ap.add_argument("--allow-outstanding", action="store_true",
                    help="report the outstanding rewrites without failing")
    args = ap.parse_args()

    artifacts = [
        ("manuscript", "HT10016_revised_corrected.docx", docx_text),
        ("supplement", "SUPPLEMENTAL_MATERIAL_revised_corrected.docx", docx_text),
        ("response letter", "RESPONSE_TO_REFEREES_corrected.docx", docx_text),
        ("response letter, markdown", "RESPONSE_TO_REFEREES_corrected.md",
         plain_text),
    ]
    failures = 0
    outstanding = []
    for label, name, reader in artifacts:
        path = os.path.join(args.dir, name)
        if not os.path.exists(path):
            print("%-26s MISSING  %s" % (label, path))
            failures += 1
            continue
        text = reader(path)
        bad, pending = [], []
        for token, why in list(STALE.items()) + [(t, "not yet rewritten")
                                                 for t in sorted(OUTSTANDING)]:
            for m in re.finditer(re.escape(token), text):
                window = text[max(0, m.start() - 90):m.end() + 90]
                if any(a.search(window) for a, _ in ALLOWED):
                    continue
                (pending if token in OUTSTANDING else bad).append(
                    (token, why, window.strip()))
        outstanding.extend((label, t) for t, _, _ in pending)
        for phrase in repeated_phrases(text):
            bad.append(("a phrase repeats itself", "an edit matched its own "
                        "output", phrase))
        if bad:
            failures += 1
            print("%-26s %d stale string(s)" % (label, len(bad)))
            for token, why, window in bad:
                print("   %-24s %s" % (token, why))
                print("      ...%s..." % window[:150])
        elif pending:
            print("%-26s clean, %d outstanding" % (label, len(pending)))
        else:
            print("%-26s clean" % label)

    if outstanding:
        print("\noutstanding, the candidate-dispatch accounting the "
              "reduced-field gate changed:\n")
        seen = set()
        for label, token in outstanding:
            if (label, token) in seen:
                continue
            seen.add((label, token))
            print("   %-26s %s" % (label, token))
        print("\n   %d occurrence(s). These need the passage rewritten, not a "
              "number swapped:" % len(outstanding))
        print("   two of the three dispatch families now emit nothing, and the "
              "surviving")
        print("   grid carries one field, so the family medians and the "
              "uncertainty width")
        print("   are quoted at a field where nothing is dispatched.")

    print()
    if failures:
        print("%d artifact(s) carry a superseded value." % failures)
        return 1
    if outstanding and not args.allow_outstanding:
        print("every tracked number agrees with the deposit, but %d passage(s) "
              "still need rewriting; run with --allow-outstanding to treat "
              "this as a report." % len(outstanding))
        return 2
    if outstanding:
        print("every tracked number agrees with the deposit; %d passage(s) "
              "still need rewriting, accepted by --allow-outstanding."
              % len(outstanding))
        return 0
    print("all four artifacts agree with the deposit on every tracked quantity")
    return 0


if __name__ == "__main__":
    sys.exit(main())
