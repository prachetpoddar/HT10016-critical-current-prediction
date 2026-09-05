#!/usr/bin/env python3
"""The last four patches, and one of them undoes a mistake I made an hour ago.

**Patch 1, the response, paragraph 38.** My previous edit moved the conditioning
claim off the variance-decomposition diagnostic, which was right, and then
restated the temperature-axis result and wrote "we should have said so in our
first reply rather than leaving the referee to find the strongest result
unstated". That sentence is false. The letter already reports it, in the
disclosure section: paragraphs 79 to 82 give the permutation test, the rise from
0.44 to 0.52 with the probability falling from 0.016 to 0.007 on the seventeen
shared papers, the field-axis 0.055 and 0.038 at 0.93 and 0.98, and the
conclusion that the substructure result is a temperature-axis result. Restating
it as a discovery, and apologising for an omission that did not happen, would
have been worse than the contradiction it replaced. The paragraph now makes the
correction and points at the section that carries the evidence.

**Patch 2, the manuscript, Sec. III.A.** The Spearman 0.635 with an interval of
[0.061, 0.948] is located: it is spearman(max_chi_mean, beta_H_mean) on the
nine-family version of the descriptor table, and a bootstrap of that pair
returns the upper bound. It is stale twice, in cohort and in column, since
Stage 1 regresses the median and two families have left. On the current seven
the value is 0.408 on the median and 0.593 on the mean, and both bootstrap
intervals contain zero and reach 1, because a rank correlation over seven points
with three tied descriptor values cannot do better. The replacement is the rank
result the stage was validated on, which needs no interval and is already the
next sentence but one.

**Patch 3, the manuscript, Sec. III.E.** With the field axis reported as not
validated at family level, "the three families that pass the validation and
population requirements" no longer describes anything, and "the family does not
pass field-axis validation" is not a refusal reason when no family passes. The
dispatch is restated on what actually holds: a validated temperature axis where
the family has one, the population requirement, and a field axis carried as a
labelled limitation, which is what Sec. III.E already says two pages later.

**Patch 4, the response, the audit section.** The deposited prediction file does
not reproduce from its own generator. One paragraph, inserted where the other
self-found defects are listed.

Source out_basis/*_final10.docx, output out_final/.

    python analysis/apply_final_patches.py --dry-run
    python analysis/apply_final_patches.py --out-dir out_final

Run from the repository root.
"""
import argparse
import copy
import os

import docx

SRC = "out_basis"
MS = "HT10016_revised_final10.docx"
RESP = "RESPONSE_TO_REFEREES_final10.docx"

RESP_EDITS = [
    ("What the claim rests on is the temperature axis, and we should have said "
     "so in our first reply rather than leaving the referee to find the "
     "strongest result unstated. Taking source papers as the unit and "
     "shuffling the substructure label between them, the fraction of "
     "between-paper variance in the fitted temperature exponent that the "
     "family label accounts for is 0.524, with a permutation probability of "
     "0.007. On the papers shared by the cohorts before and after the "
     "transition-temperature repairs it rises from 0.436 to 0.524 and the "
     "probability falls from 0.016 to 0.007, so the repairs strengthen it "
     "rather than producing it. That is a family-level result on the axis "
     "whose critical scale is directly reported, and it is the one claim in "
     "this paper that improved under every correction we made. "
     "The field axis carries none of it, and we now say so plainly rather than "
     "reporting a weaker version. The same statistic on the field exponent is "
     "0.055 with a probability of 0.93 on the cohort as published and 0.038 "
     "with 0.98 on the 52 fits our stated protocol admits; matched on the "
     "twelve papers those two share, 0.031 against 0.038. The field exponent "
     "separates no substructure family on any cohort we can construct. "
     "Together with the per-family errors reversing when the anchors are "
     "repaired, that is why Table III now records the field axis as not "
     "validated at family level and reports no verdict for it.",
     "What the claim rests on is the temperature axis, and the evidence is the "
     "permutation test reported under the changes we made on our own, below: "
     "with source papers as the unit and the substructure label shuffled "
     "between them, the family accounts for a rising fraction of the "
     "between-paper variance in the temperature exponent as the anchors are "
     "corrected, while on the field axis it accounts for essentially none "
     "under either version. We do not restate those figures here. The point "
     "for this objection is only that the conditioning claim is a "
     "temperature-axis claim, that it is the one result in this paper that "
     "improved under every correction we made, and that neither the ratio the "
     "referee questioned nor the sample-form diagnostic is load-bearing for "
     "it. It is also why Table III records the field axis as not validated at "
     "family level and reports no verdict for it.",
     "paragraph 38, remove the duplication and the false concession"),
]

MS_EDITS = [
    ("The descriptor carries genuine but weak rank information, Spearman "
     "ρ = 0.635 with a 95% confidence interval of [0.061, 0.948].",
     "The descriptor carries genuine but weak rank information. An earlier "
     "version of this section quantified it as a Spearman coefficient of 0.635 "
     "with a 95% confidence interval of [0.061, 0.948]. That figure is "
     "withdrawn: it was computed on the nine-family version of the descriptor "
     "table, two of whose families have since been withdrawn, and on the mean "
     "field exponent where this stage regresses the median. On the seven "
     "families that remain the coefficient is 0.408 on the median and 0.593 on "
     "the mean, and a bootstrap interval on either contains zero and reaches "
     "unity, because a rank correlation over seven points of which three share "
     "an identical descriptor value cannot be estimated more tightly than "
     "that. We therefore report the rank-position result below, which is the "
     "quantity this stage was validated on and which needs no interval.",
     "Sec. III.A, the withdrawn Spearman"),
    ("Dispatch is restricted to the three families that pass the validation "
     "and population requirements: iron chalcogenide 11-type, iron pnictide "
     "122-type, and MgB2-class.",
     "Dispatch is restricted to the three families that meet the population "
     "requirement and carry a validated temperature axis: iron chalcogenide "
     "11-type, iron pnictide 122-type, and MgB2-class. Because the field axis "
     "is not validated at family level, no dispatched field-axis output is "
     "offered as a validated prediction; each is carried as the labelled "
     "limitation stated later in this section.",
     "Sec. III.E, the dispatch scope"),
    ("and 40 because the family does not pass field-axis validation;",
     "and 40 because the family carries no validated field axis, which after "
     "this revision is true of every family;",
     "Sec. III.E, the refusal reason"),
]

INSERT_AFTER = ("This matters for the exponent that the field axis reports.")
INSERT = (
    "The deposited prediction file does not reproduce from its own generator. "
    "Running the deposited dispatch code on the deposited tables returns the "
    "released file exactly, with one exception: for two records of one paper "
    "the generator commits to a wire sample-form cell and the released file "
    "does not, and those two records carry four of the emitted predictions. "
    "Every other column matches and the remaining predictions differ by at "
    "most 0.014 in log10 Jc, which is the bootstrap draw. The difference "
    "predates this revision and none of the corrections reported above is "
    "implicated. Separately, our withdrawals were applied by editing the "
    "deposited tables while the candidate list is rebuilt from the extraction "
    "directory, so regenerating restores six withdrawn candidates; all six are "
    "refused and no emitted prediction changes, but the generator cannot "
    "enforce a withdrawal and we say so rather than leave a reader to find it. "
    "Both are recorded in the deposited audit.")


def replace_in_paragraph(p, find, repl):
    text = "".join(r.text for r in p.runs)
    if find not in text:
        return False
    start = text.index(find)
    end = start + len(find)
    pos, first, spans = 0, None, []
    for r in p.runs:
        a, b = pos, pos + len(r.text)
        if b > start and a < end:
            spans.append((r, max(start, a) - a, min(end, b) - a))
            if first is None:
                first = r
        pos = b
    if first is None:
        return False
    for r, i, j in spans:
        r.text = r.text[:i] + (repl if r is first else "") + r.text[j:]
    return True


def insert_after(d, anchor_prefix, text):
    anchor = None
    for p in d.paragraphs:
        if p.text.strip().startswith(anchor_prefix):
            anchor = p
    if anchor is None:
        return False
    new = copy.deepcopy(anchor._p)
    anchor._p.addnext(new)
    para = docx.text.paragraph.Paragraph(new, anchor._parent)
    for r in para.runs[1:]:
        r.text = ""
    if para.runs:
        para.runs[0].text = text
    return True


def apply(path, edits):
    d = docx.Document(path)
    missed = [why for find, repl, why in edits
              if not any(replace_in_paragraph(p, find, repl)
                         for p in d.paragraphs)]
    return d, missed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    resp, m1 = apply(os.path.join(SRC, RESP), RESP_EDITS)
    ms, m2 = apply(os.path.join(SRC, MS), MS_EDITS)
    missed = [(RESP, x) for x in m1] + [(MS, x) for x in m2]
    if not insert_after(resp, INSERT_AFTER, INSERT):
        missed.append((RESP, "the deposit disclosure anchor"))
    print("%s: %d edits + 1 insert, %d not found"
          % (RESP, len(RESP_EDITS), len(m1)))
    print("%s: %d edits, %d not found" % (MS, len(MS_EDITS), len(m2)))

    full = " ".join(p.text for p in resp.paragraphs)
    checks = [
        ("the false concession is gone",
         "we should have said so in our first reply" not in full),
        ("the disclosure section still carries the permutation figures",
         "0.016 to 0.007" in full and "0.93 and 0.98" in full),
        ("the temperature figures are not restated in the A10 answer",
         full.count("0.524") <= 1),
        ("the deposit disclosure is present",
         "does not reproduce from its own generator" in full),
    ]
    mf = " ".join(p.text for p in ms.paragraphs)
    checks += [
        ("the withdrawn Spearman is marked withdrawn",
         "0.635" not in mf or "withdrawn" in mf),
        ("the rank result is still stated",
         "rank-position error remains 1.00" in mf),
        ("no family is said to pass field-axis validation",
         "pass field-axis validation" not in mf),
    ]
    print()
    for name, ok in checks:
        print("   %-58s %s" % (name, "ok" if ok else "FAIL"))
        if not ok:
            missed.append(("check", name))

    if missed:
        print("\nNothing written.")
        for m in missed:
            print("  ", m)
        return 1
    if a.dry_run or not a.out_dir:
        print("\ndry run: nothing written")
        return 0
    os.makedirs(a.out_dir, exist_ok=True)
    resp.save(os.path.join(a.out_dir, RESP.replace("_final10", "_final11")))
    ms.save(os.path.join(a.out_dir, MS.replace("_final10", "_final11")))
    print("\nwritten to %s" % a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
