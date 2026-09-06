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

    python analysis/final_consistency_check.py OUT_DIR

OUT_DIR holds the three documents to check. It is required, and the three are
discovered by prefix rather than by version-stamped filename.

It used to be neither: the directory and all three filenames were constants
naming the final13 documents of 2026-09-05, and the script accepted and
ignored any arguments given to it. Three later stages of the document lineage
were checked by passing their paths on the command line, and every one of
those runs read final13 and reported that it passed. A checker that reads a
file nobody asked it to read is worse than no checker, because its output is
quoted.

Run from the repository root.
"""
import os
import re

import docx
import numpy as np
import pandas as pd

# Filled by main() from the required OUT_DIR argument. Prefixes, not names,
# so the check follows the lineage instead of pinning one stage of it.
PREFIX = {"manuscript": "HT10016_revised_",
          "supplement": "SUPPLEMENTAL_MATERIAL_revised_",
          "response": "RESPONSE_TO_REFEREES_"}
OUT = None
DOCS = {}


def resolve(out_dir):
    """Find exactly one document per prefix in out_dir, or refuse."""
    global OUT, DOCS
    if not os.path.isdir(out_dir):
        raise SystemExit("not a directory: %s" % out_dir)
    names = [n for n in sorted(os.listdir(out_dir))
             if n.endswith(".docx") and not n.startswith("~$")]
    OUT = out_dir
    DOCS = {}
    for key, pre in PREFIX.items():
        hit = [n for n in names if n.startswith(pre)]
        if len(hit) != 1:
            raise SystemExit(
                "%s: found %d file(s) starting %r, need exactly one: %s"
                % (out_dir, len(hit), pre, ", ".join(hit) or "none"))
        DOCS[key] = hit[0]
    print("checking")
    for key in ("manuscript", "supplement", "response"):
        print("   %-11s %s" % (key, os.path.join(out_dir, DOCS[key])))
    print()

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
            # One unit per row, not per cell. A table row is a single
            # statement: the disposition table names a specimen in one cell
            # and gives the reason it was dropped in another, and splitting
            # them made a withdrawn record read as an unqualified mention of
            # the withdrawn worked example. This is the same defect the
            # paragraph rule above was written to avoid, one level down.
            out.append(" ".join(c.text for c in r.cells))
    return out


def text(name):
    return " ".join(paragraphs(name))


def main():
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: final_consistency_check.py OUT_DIR")
    resolve(sys.argv[1])
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

    print("\nimages, which the text checks above cannot see\n")
    import zipfile as _zip
    want_images = {"manuscript": 5, "supplement": 1, "response": 0}
    for key, n_want in want_images.items():
        z = _zip.ZipFile(os.path.join(OUT, DOCS[key]))
        got = len([n for n in z.namelist() if n.startswith("word/media/")])
        ok = got == n_want
        print("   %-30s document %5d   expected %5d   %s"
              % (key + " images", got, n_want, "ok" if ok else "MISMATCH"))
        if not ok:
            fails.append("%s holds %d image(s), expected %d"
                         % (key, got, n_want))

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
        # The same claim, on the manuscript side. Only the response was
        # watched, and the manuscript kept saying for two revisions that the
        # claim rests on the diagnostic while reply paragraph 38 said resting
        # it there will not do. Rebuilding Figure 1 is what found it.
        ("the conditioning claim rests on the diagnostic",
         "The conditioning claim rests on this test", "manuscript"),
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

    # The nine repairs of 2026-09-06. Each is a value or a phrase that was
    # verified against the deposit and then attacked by an independent
    # reviewer, so an edit that reintroduces the old form should fail here
    # rather than reach a referee a second time.
    print("\nthe repairs of 2026-09-06\n")
    repaired = [
        # (name, token, document, must_be_present)
        ("Stage 3 quoted as a leave-one-out error",
         "giving a leave-one-substructure-out error of 0.84", "manuscript",
         False),
        ("the genuine Stage 3 value", "the Stage 3 error is 0.816",
         "manuscript", True),
        ("the K-anchor error labelled an exponent error",
         "1.592 exponent error", "manuscript", False),
        ("the K-anchor error labelled dex", "1.592 dex in log10 Jc",
         "manuscript", True),
        # The token is the comparison, not the number: the sentence that
        # retires 0.567 has to name it, so a bare "0.567" test fires on the
        # retirement itself. That false positive was left in place long enough
        # to confirm the check fires at all.
        ("the untraced in-corpus baseline",
         "2.81 times the in-corpus baseline", "manuscript", False),
        ("the regime composition behind 45.2 percent",
         "the improvement is 2.3%", "manuscript", True),
        ("the MgB2 rms transcription", "an rms of 6.3 in log10 Jc and one "
         "resting on three points", "manuscript", False),
        ("the six three-point MgB2 fits",
         "Six of the fifteen rest on three points", "manuscript", True),
        ("the variance-ratio cuts", "above 0.7 the family is treated as "
         "sample-form dominant", "manuscript", True),
        # The 30 percent adoption threshold, withdrawn 2026-09-06. It had no
        # construction anywhere in the repository, and its own defining
        # sentence set it twenty times above the benchmark it named. What
        # replaces it is a test, so both halves are checked: the bar must be
        # gone from every document, and the two tests that replace it must be
        # present.
        ("the withdrawn adoption threshold, main text",
         "below the 30% adoption threshold", "manuscript", False),
        ("the withdrawn adoption threshold, Sec. III.D",
         "the 30% threshold required for adopting universality", "manuscript",
         False),
        ("the withdrawn adoption threshold, response letter",
         "does not clear our 30% threshold", "response", False),
        ("the rotation test", "rotated to a random angle", "manuscript", True),
        ("the unnormalized-coordinate test",
         "67.0% on 42 cells against 39.3% on 73", "manuscript", True),
        ("the reason the unnormalized grid wins",
         "separates compounds rather than collapsing them", "manuscript",
         True),
        # Table II and the form selection, rebuilt 2026-09-06. The published
        # margin does not separate Forms 2 and 3 once they are scored on the
        # same rows and the same compounds, so the section no longer claims
        # it does, and the caption no longer says the splits are identical.
        ("Form 3 adopted on the Table II margin",
         "Form 3 was adopted on that empirical basis", "manuscript", False),
        ("the caption's identical-splits claim",
         "identical splits across forms", "manuscript", False),
        ("the reason Form 3 is adopted",
         "the only one of the three that separates", "manuscript", True),
        ("Form 3 against Form 2 stated as no separation",
         "at 0.118 and 0.267, which is not a separation", "manuscript", True),
        ("the like-for-like Form 2 to Form 3 margin",
         "0.012 dex rather than 0.092", "manuscript", True),
        # The propagated uncertainty, repaired 2026-09-06. The printed
        # beta_T scatter of 1.158 is not reproducible and is the pre-repair
        # quantity; the correlation caveat pointed the wrong way for this
        # functional form; and the scope quoted dispatches nothing.
        ("the unreproducible beta_T scatter", "1.158 in \u03b2T, and 0.920",
         "manuscript", False),
        ("the corrected quadrature", "gives 0.27 dex at one sigma",
         "manuscript", True),
        ("the MgB2 scope figures",
         "0.49 dex at 4.2 K and 0.57 dex at 20 K", "manuscript", True),
        ("the backwards correlation caveat, main text",
         "read as a lower bound on the structural component", "manuscript",
         False),
        ("the backwards correlation caveat, supplement",
         "should be read as a lower bound on the structural component",
         "supplement", False),
        ("the corrected correlation sign",
         "only a positive correlation between the two exponents raises it",
         "manuscript", True),
        # Figure 5, rebuilt 2026-09-06. The family parameters were a frozen
        # artifact from a cohort state not in the deposit; they are now the
        # family medians over the fitted cohorts, so the envelopes and the
        # crossing move with them.
        ("the stale envelope crossing", "reduced field of 0.59", "manuscript",
         False),
        ("the rebuilt envelope crossing", "reduced field of 0.58",
         "manuscript", True),
        ("the band said to be per-family",
         "per-grid-point intervals are narrower in low-uncertainty regions",
         "manuscript", False),
        ("the band named as one family's",
         "every one of which is MgB2-class", "manuscript", True),
        ("the family parameters' provenance",
         "regenerated by analysis/fit_family_params.py", "manuscript", True),
        # The two disclosure repairs of 2026-09-06. Eq. (1) as printed
        # returns 63 field-axis fits and Sec. III.C reports 52, and the
        # response letter's promise of a 94-fit disposition table was not
        # kept by the supplement.
        ("the axis the window is applied to",
         "In this revision both conditions are imposed on both axes",
         "manuscript", True),
        ("the 63 to 52 cost, in the manuscript",
         "removes 11 of the 63 fits", "manuscript", True),
        ("the promised disposition table",
         "Disposition of the 94 field-axis fits", "supplement", True),
        # The figure-rebuilt exponents, disclosed 2026-09-06. None of the
        # deposited temperature-axis exponents reproduces from its source
        # figure, the rebuild is deposited, and on it the separation survives
        # while the applicability result does not.
        ("the figure rebuild is reported",
         "median ratio of refitted to deposited is 0.42", "manuscript", True),
        ("the separation survives the rebuild",
         "0.359 with a permutation probability of 0.037", "manuscript", True),
        ("the applicability result does not",
         "1.435, 1.184 and 2.415", "manuscript", True),
        ("the composition is not the cause",
         "still gives a median exponent of 1.277", "manuscript", True),
        # The strengthening pass of 2026-09-06.
        ("the false improved-under-every-correction claim",
         "the one result in the paper that improved under every correction",
         "manuscript", False),
        ("the probability that moved the wrong way",
         "from 0.012 on nineteen papers to 0.016 on the seventeen matched",
         "manuscript", True),
        ("the exhaustive compound-level null",
         "there are 966, and four of them reach the observed separation",
         "manuscript", True),
        ("the alternative grouping that does better",
         "separates the exponent slightly better than the substructure label "
         "does, at 0.532", "manuscript", True),
        ("the unreduced result's robustness",
         "at minimum cell sizes of 3, 5, 8 and 12", "manuscript", True),
        ("the source holdout connected to the thesis",
         "reaches a median error below 0.9 dex, against 0.32 to 0.45 dex",
         "manuscript", True),
        # The response letter brought up to the manuscript, 2026-09-06. It
        # had kept only the half of the separation's history that flattered
        # it, and six of the audit's corrections were absent from it.
        ("the letter's one-sided separation history",
         "correcting the anchors makes the separation stronger", "response",
         False),
        ("the pre-withdrawal value in the letter",
         "the fraction is 0.107 with a probability of 0.355", "response",
         True),
        ("the compound-level null in the letter",
         "966 distinct ways of forming three families", "response", True),
        # The token is the count and the fact, not the sentence that carried
        # them: the compaction of 2026-09-06 rewrote this paragraph and the
        # longer phrasing this check used to require went with it.
        ("the audit's five defects in the letter",
         "found five more defects", "response", True),
        ("Stage 3 corrected in the letter",
         "0.816 rather than 0.84", "response", True),
        ("the propagation corrected in the letter",
         "0.27 dex rather than 0.29", "response", True),
        # The description was withdrawn in one paragraph and repeated in
        # another, well away from it, inside the Referee A response.
        ("the second, stale copy of the withdrawn description",
         "the one result in this paper that improved under every correction "
         "we made", "response", False),
        ("the retraction of it, in the referee response",
         "the audit section below withdraws that description", "response",
         True),
        # Supplemental Figure S1, embedded 2026-09-06. It had a generator
        # and a committed PNG since 2026-09-02 and appeared in no document,
        # and its generator could not run because the paper behind its
        # middle panel had been withdrawn from the field axis.
        ("the Figure S1 caption", "FIG. S1.", "supplement", True),
        ("the replacement panel's record", "j.jallcom.2013.04.183",
         "supplement", True),
        ("the withdrawal that forced it", "s41467-025-55880-4", "supplement",
         True),
        ("Figure S1 cited in its own section",
         "Fig. S1 shows the curves behind three such records", "supplement",
         True),
        ("Figure S1 cited to the referee",
         "opens with Fig. S1", "response", True),
        # The Figure 5 crossing, which the letter still quoted at its
        # pre-rebuild value. The figure checks compare images and the text
        # checks compared only the manuscript, so nothing looked at whether
        # the letter agreed with either.
        ("the stale crossing in the letter", "reduced field of 0.59",
         "response", False),
        ("the rebuilt crossing in the letter", "reduced field of 0.58",
         "response", True),
        # The opening section added 2026-09-06. The letter had no page that
        # said what the paper found: 37 percent of its paragraphs carried a
        # concession, eleven opened with one, and six stated a result with
        # no apology attached.
        ("the letter states what the paper establishes",
         "What the paper establishes", "response", True),
        ("the four claims are in the letter's opening",
         "The framework declines to predict outside its validated scope",
         "response", True),
        ("the reproducibility standard is stated",
         "every printed count is asserted against the deposited tables",
         "response", True),
        # One validation status, propagated 2026-09-06. The phrase "three
        # validated substructure families" meant three different things in
        # the abstract, Table III and the conclusion, and Table IV's
        # validating-axis column contradicted Sec. III.E's own prose.
        ("the ambiguous validated-families phrase",
         "three validated substructure families", "manuscript", False),
        ("the temperature-axis test named in the abstract",
         "clear the compound leave-one-out threshold on the temperature axis",
         "manuscript", True),
        ("the dispatching family stated as not assessable",
         "not assessable on the axis where the test can be run", "manuscript",
         True),
        ("Table IV no longer claims a field axis",
         "Field only", "manuscript", False),
        ("the supplement's exponent-error label",
         "baseline. These are dimensionless exponent errors.", "supplement",
         False),
        # One anchor cohort, propagated 2026-09-06. Figure 3 drew the
        # deposited 96-row table while Sec. III.A and Table III reported both
        # cohorts and the abstract reported only the deposited one. The figure
        # now draws the repaired 70, and the size-preserving clustered null is
        # applied to all three families rather than to two of them.
        ("the abstract leads with the repaired anchors",
         "on the repaired anchor cohort sample form explains 81%",
         "manuscript", True),
        ("the deposited anchors kept beside them in the abstract",
         "against 37%, 49% and 12% on the anchors as deposited",
         "manuscript", True),
        ("the caption's stale deposited-panel claim",
         "The panels here plot the anchors as deposited", "manuscript", False),
        ("the caption names the cohort it draws",
         "the 70 of the 96 per-paper anchor records of Table I that carry no "
         "withdrawal", "manuscript", True),
        ("the stale marker count in the caption",
         "The 56 collapse to the 37 markers drawn", "manuscript", False),
        ("the withdrawn MgB2 labelling floor",
         "admits three distinct labellings", "manuscript", False),
        ("the size-preserving null applied to all three",
         "the MgB2-class cell admits a single labelling", "manuscript", True),
        ("the exact permutation probabilities are given",
         "0.25 for the iron chalcogenide cell, which is its floor",
         "manuscript", True),
        ("the enumeration is deposited",
         "analysis/anchor_form_permutation.py", "manuscript", True),
        ("the stale MgB2 permutation sentence",
         "Given the MgB2-class cohort size (n = 15 physical samples)",
         "manuscript", False),
        ("the letter's false unchanged-anchor-count claim",
         "The anchor count behind Figure 3 and the candidate compound count "
         "do not move", "response", False),
        ("the letter states that the anchor count moves",
         "Twenty-six of the 96 per-paper anchor rows carry a withdrawal",
         "response", True),
        ("the letter's per-family floors",
         "the MgB2-class cell returns 1 whatever its separation", "response",
         True),
    ]
    for name, token, doc, want in repaired:
        hit = token in T[doc]
        ok = hit == want
        print("   %-46s %-12s %s" % (name, doc,
                                     ("present, ok" if want else "absent, ok")
                                     if ok else
                                     ("MISSING, FAIL" if want
                                      else "PRESENT, FAIL")))
        if not ok:
            fails.append("%s: %s in the %s"
                         % (name, "missing" if want else "still present", doc))

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
