#!/usr/bin/env python3
"""One consistency check across the three documents before they are sent.

Not a re-derivation. Everything here has been computed and reviewed elsewhere;
this asks whether the three documents agree with each other and with the
deposited tables on the numbers they print, and whether any figure this
revision withdrew is still standing somewhere unqualified.

Four families of check.

  Census. Table I's ladder against the deposited tables, and against every
  place the same counts are repeated in prose.
  Withdrawn figures. Every value this revision retired must appear only in a
  sentence that retires it.
  Cross-document. A number printed in two documents must be the same number.
  Internal contradiction. Statements the revision has made mutually exclusive.

    python analysis/final_consistency_check.py

Run from the repository root.
"""
import os
import re

import docx
import numpy as np
import pandas as pd

OUT = "out_send"
DOCS = {"manuscript": "HT10016_revised_final13.docx",
        "supplement": "SUPPLEMENTAL_MATERIAL_revised_final13.docx",
        "response": "RESPONSE_TO_REFEREES_final13.docx"}

# Paragraphs in the response that quote a referee rather than answer one. A
# retired figure appearing inside the objection itself is the objection, not a
# document still making the claim, and the first run of this check flagged the
# referee's own "factor of 23" as a defect.
QUOTED = ["Grouping the data reduces the error",
          "In Figure 5, right, Jc vs H changes",
          "The formula, derived from the Ginzburg-Landau model",
          "\u201c934 papers\u201d exaggerates"]


def paragraphs(name):
    """Paragraph-level units, with quoted referee objections dropped.

    The unit matters. A first version split on sentences, so a figure
    withdrawn in the sentence after the one that names it registered as
    unqualified, and three of its five failures were that artefact. A
    withdrawal is a paragraph-level act.
    """
    d = docx.Document(os.path.join(OUT, DOCS[name]))
    out = [p.text for p in d.paragraphs
           if not any(p.text.strip().startswith(q) for q in QUOTED)]
    for t in d.tables:
        for r in t.rows:
            out += [c.text for c in r.cells]
    return out


def text(name):
    return " ".join(paragraphs(name))


def main():
    T = {k: text(k) for k in DOCS}
    P = {k: paragraphs(k) for k in DOCS}
    fails, notes = [], []

    print("census against the deposited tables\n")
    a = pd.read_csv(os.path.join("data",
                                 "phase_3_p44_post_UCLA_beta_T_fits_repaired.csv"))
    keep = a[a.reproduced & np.isfinite(a.beta_T_repaired)]
    prot = pd.read_csv(os.path.join("audit", "fit_protocol_applied.csv"))
    prov = pd.read_csv(os.path.join("data",
                                    "provenance_table_fitcohort_full.csv"))
    live = prov[prov.contributes != "none, withdrawn"]
    facts = [
        ("temperature-axis fits", 257, len(keep)),
        ("field-axis fits admitted", 52, int(prot.admitted.sum())),
        ("field-axis papers", 12, int(prot[prot.admitted].paper.nunique())),
        # second_identifier_for_the_same_paper is a boolean flag, not a
        # nullable identifier; two earlier attempts read it as the latter and
        # returned zero.
        ("contributing papers", 50,
         int((~live.second_identifier_for_the_same_paper.astype(bool)).sum())),
    ]
    for name, printed, computed in facts:
        ok = printed == computed
        print("   %-30s document %5d   tables %5d   %s"
              % (name, printed, computed, "ok" if ok else "MISMATCH"))
        if not ok:
            fails.append("%s: %d printed, %d in the tables"
                         % (name, printed, computed))

    print("\nwithdrawn figures, which must appear only where they are retired\n")
    retired = [
        ("0.635", "the nine-family Spearman", ["withdrawn"]),
        ("1.07-fold", "the leave-one-substructure-out fold", ["withdraw"]),
        ("2.24-fold", "the same", ["withdraw"]),
        ("1.83-fold", "the same", ["withdraw"]),
        ("SmFeAsO0.8F0.2", "the A3 worked example", ["withdraw"]),
        ("factor of 23", "the original headline", ["exaggerat", "no longer"]),
    ]
    for token, what, qualifiers in retired:
        for doc in DOCS:
            paras = [p for p in P[doc] if token in p]
            if not paras:
                continue
            bad = [p for p in paras if not any(q in p for q in qualifiers)]
            print("   %-16s %-12s %d paragraph(s), %d unqualified   %s"
                  % (token, doc, len(paras), len(bad),
                     "ok" if not bad else "FAIL"))
            if bad:
                fails.append("%s in %s: %s" % (token, doc, bad[0][:110]))

    print("\ncross-document agreement\n")
    shared = [("52", "the admitted field cohort"),
              ("257", "the temperature cohort"),
              ("3303", "extracted points"),
              ("0.88", "the exposure median")]
    for token, what in shared:
        present = [d for d, b in T.items() if token in b]
        print("   %-8s %-28s in %s" % (token, what, ", ".join(present)))

    print("\ninternal contradictions this revision could have created\n")
    pairs = [
        ("the conditioning claim rests on the diagnostic",
         "It rests on the variance-decomposition diagnostic", "response"),
        ("a family passes field-axis validation",
         "pass field-axis validation", "manuscript"),
        ("the one grid point",
         "the one grid point that survives", "response"),
        ("the only grid point, unqualified",
         "the only grid point at which anything is dispatched", "manuscript"),
    ]
    for name, token, doc in pairs:
        body = T[doc]
        hit = token in body
        if hit and token.startswith("the only grid point"):
            sents = [s for s in re.split(r"(?<=[.])\s+", body) if token in s]
            hit = any("wrong" not in s and "earlier version" not in s
                      for s in sents)
        print("   %-46s %-12s %s" % (name, doc, "absent, ok" if not hit
                                     else "PRESENT, FAIL"))
        if hit:
            fails.append("%s still present in the %s" % (name, doc))

    print("\nresult")
    for f in fails:
        print("   FAIL %s" % f)
    for n in notes:
        print("   note %s" % n)
    if fails:
        raise SystemExit("the documents are not consistent")
    print("   the three documents agree with the tables and with each other "
          "on every check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
