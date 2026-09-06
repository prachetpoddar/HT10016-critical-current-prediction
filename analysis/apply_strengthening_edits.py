"""
apply_strengthening_edits.py

Four edits that strengthen claims rather than repair them, plus one correction
the strengthening exposed.

1. **"The one result in the paper that improved under every correction" is
false.** At the reproducibility step the permutation probability moved the
wrong way, 0.0117 on the nineteen deposited papers against 0.0158 on the
seventeen matched ones, while eta squared rose. Both are printed as the result,
so the sentence is false on one of the two numbers it names. It is replaced
rather than softened.

2. **The separation is put against an exhaustive compound-level null.** The
paper tests the family label by shuffling it across source papers. The
objection is that family is compound identity with fewer labels, and on a
different statistic in this paper the family label is indeed indistinguishable
from a random regrouping of the same compounds. Here the objection can be
settled by enumeration rather than sampling: the cohort's eight compounds admit
966 distinct ways of forming three families, and four of them reach the
observed separation, an exact probability of 0.0041. Per compound rather than
per paper it is 0.0083. Both are reported, along with the fact that under the
narrower size-matched null one alternative grouping separates the exponent
slightly better than the real one.

3. **The unreduced-coordinate result gains its robustness.** It was reported
with a paired interval and no sensitivity. The direction holds in all seven
leave-one-family-out refits, at four minimum cell sizes, and with the duplicate
digitisation of one figure removed, and that is what makes it more than one
number.

4. **The source-paper holdout is connected to the thesis it supports.** It sat
in Sec. II.C as a fact about model selection. It is the heterogeneity result
arriving from a second direction and Sec. III.D now says so.

Usage:
    python3 analysis/apply_strengthening_edits.py IN_DIR OUT_DIR
"""
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_compound_label_edits import (paragraphs, plain,          # noqa: E402
                                        replace_in_paragraph, unescape)

MAIN = "HT10016_revised_final28.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final28.docx"
RESP = "RESPONSE_TO_REFEREES_final28.docx"
OUT = {MAIN: "HT10016_revised_final29.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final29.docx",
       RESP: "RESPONSE_TO_REFEREES_final29.docx"}

EDITS = [
    # ---- 1 and 2: the separation sentence -------------------------------
    (MAIN,
     "This is the one result in the paper that improved under every "
     "correction, it uses no fitted field scale, and it is what the "
     "conditioning claim rests on.",

     "It uses no fitted field scale, and it is what the conditioning claim "
     "rests on. An earlier version of this section called it the one result "
     "that improved under every correction. That is not accurate: at the step "
     "that removed two papers whose extractions could not be reproduced, eta "
     "squared rose while the permutation probability rose with it, from 0.012 "
     "on nineteen papers to 0.016 on the seventeen matched ones, and both are "
     "reported as the result. We test the label against a stronger null than "
     "a shuffle across papers, because the family label is constant within a "
     "compound and the obvious objection is that it is compound identity with "
     "fewer labels. The seventeen papers carry eight compounds, and every "
     "distinct way of forming three families from those eight compounds can be "
     "enumerated rather than sampled: there are 966, and four of them reach "
     "the observed separation, an exact probability of 0.0041. Taking one "
     "observation per compound instead of per paper it is 0.0083. Restricting "
     "the enumeration to groupings that also match the real family sizes "
     "leaves 280, of which two reach it, and one of those two is an "
     "alternative grouping that separates the exponent slightly better than "
     "the substructure label does, at 0.532. The family label is therefore not "
     "a relabelling of compound identity on this axis, and it is also not the "
     "only grouping of these compounds that would separate the exponent. The "
     "enumeration is in analysis/family_label_compound_null.py."),

    # ---- 3: the unreduced-coordinate result -----------------------------
    (MAIN,
     "Both tests point the same way as the percentage: the organizing "
     "variables here are material identity and measurement context, not "
     "reduced temperature and reduced field.",

     "That direction is not one number. It holds in all seven "
     "leave-one-family-out refits, at minimum cell sizes of 3, 5, 8 and 12, "
     "and with the duplicate digitisation of one figure removed. Both tests "
     "point the same way as the percentage: the organizing variables here are "
     "material identity and measurement context, not reduced temperature and "
     "reduced field. A third line of evidence reaches the same place from "
     "model selection rather than from binning. Under a source-paper holdout, "
     "in which every measurement of a held-out source is withheld, none of the "
     "three candidate functional forms of Sec. II.C reaches a median error "
     "below 0.9 dex, against 0.32 to 0.45 dex when the holdout is drawn point "
     "by point within a compound. That is a factor of eight or more in "
     "critical current between predicting an unseen measurement of a source "
     "already seen and predicting an unseen source. It rests on the eight "
     "compounds that draw on more than one source, so we report it as a "
     "direction rather than as a measurement."),
]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_strengthening_edits.py IN_DIR OUT_DIR")
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    by_file = {}
    for f, find, repl in EDITS:
        by_file.setdefault(f, []).append((find, repl))
    for name in (MAIN, SUPP, RESP):
        ip, op = os.path.join(src, name), os.path.join(dst, OUT[name])
        if not os.path.exists(ip):
            sys.exit("missing input: %s" % ip)
        zin = zipfile.ZipFile(ip)
        doc = zin.read("word/document.xml").decode("utf-8")
        for find, repl in by_file.get(name, []):
            hits = [p for p in paragraphs(doc) if find in unescape(plain(p))]
            if len(hits) != 1:
                sys.exit("%s: %d paragraph(s) contain %r, expected exactly 1"
                         % (name, len(hits), find[:70]))
            new = replace_in_paragraph(hits[0], find, repl)
            if new is None:
                sys.exit("%s: could not place the replacement for %r"
                         % (name, find[:70]))
            doc = doc.replace(hits[0], new, 1)
            print("   %-8s %s" % (name.split("_")[0][:8], find[:62]))
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
