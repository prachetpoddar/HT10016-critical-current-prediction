#!/usr/bin/env python3
"""Rewrite A6 and Sec. III.E on the narrow dispatch spread.

Decision taken: agree with Referee A more fully than the letter does, give the
mechanism, and say plainly what the quoted figure can and cannot support.

Everything written in comes from analysis/dispatch_spread_mechanism.py, which
went through the adversarial-review gate, and every number is computed on the
DEPOSITED prediction file, which is the file the paper reports.

Four things go in.

  A count the paper gets wrong. The dispatch emits at two grid points, not one:
  4.2 K and 5 T with 86 records over 84 compounds, and 20 K and 5 T with 77
  records over 75. Both clear the gates this revision introduced, at reduced
  temperatures of 0.48 to 0.70 against the 0.7 bound and a reduced field of
  0.3226 against the 0.3 bound. Three passages say "the one grid point"; the
  assertion behind that wording checks that one FIELD is emitted, which is
  true, and appears to have been read as one grid point.

  The letter's explanation is right at 20 K and cannot be right at 4.2 K. At
  20 K the prediction regresses on the temperature term the model forms with
  slope 1.22 and R squared 0.996, recovering the family exponent of 1.14, so
  the candidate's transition temperature enters exactly as described. At 4.2 K
  it cannot enter at all, because 4.2 K is the reference temperature at which
  the model is anchored and the temperature term is then identically zero for
  every candidate whatever its Tc. Nothing in the manuscript, the supplement or
  the letter says this.

  The 0.0098 dex is not a measurement. With the temperature term zero and the
  15.5 T anchor common, the 86 records have identical model inputs and differ
  only in their draw from one bootstrap stream over an 18-fit pool. Resampling
  that pool 84 times independently gives a span of 0.0092 with a standard
  deviation of 0.0016, of which the observed value is an ordinary draw. It is
  therefore evidence that the predictor is constant, which is the referee's
  point, and evidence of nothing else.

  The interval is not all sampling. The median width at that point is 0.6024
  dex on records carrying a parent anchor and 0.3949 dex on the three carrying
  an exact one, so about 0.21 dex of the quoted width is a deterministic plus
  or minus 20 percent anchor envelope rather than bootstrap spread. At the
  upper perturbation that envelope evaluates the model at a reduced field of
  0.269, below the 0.3 bound the same revision introduced.

Two things deliberately stay out.

  The regenerated dispatch. Running the generator gives a wider spread at both
  grid points, and audit/dispatch_spread_20260905.md records why that must not
  be reported: the widening is present on the tables as originally released, so
  it is not a result of the corrections, and it comes from a conditional cell
  holding 8 fits from 2 papers whose own fits are a quarter of the pool.

  That the deposited prediction file does not reproduce from its own generator.
  That is a disclosure decision about the deposit rather than an answer to A6,
  and it is left for the authors.

Source out_a4/*_final4.docx, output out_a6/.

    python analysis/apply_a6_spread_edits.py --dry-run
    python analysis/apply_a6_spread_edits.py --out-dir out_a6

Run from the repository root.
"""
import argparse
import os

import docx

SRC = "out_a4"
MS = "HT10016_revised_final4.docx"
RESP = "RESPONSE_TO_REFEREES_final4.docx"

OLD_RESP_27 = (
    "At 4.2 K and 5 T, the one grid point that survives the gate, the 86 "
    "MgB2-class records covering 84 distinct compounds span 0.0098 dex, which "
    "is 1.6% of the 0.60 dex bootstrap interval at that point. The "
    "conditioning fixes every parameter of the expression, and the "
    "compound-specific inputs are the critical-field anchor, which enters "
    "through the field term, and the transition temperature, which enters "
    "through the temperature term. The narrow spread was therefore not "
    "evidence of precision. The predictor is constant by construction, and the "
    "paper now says so and states what the framework may claim as a result.")

NEW_RESP_27 = (
    "We have to correct a count before answering. The dispatch emits at two "
    "grid points, not one: 4.2 K and 5 T, where 86 records cover 84 "
    "compounds, and 20 K and 5 T, where 77 cover 75. Both clear this "
    "revision's gates, at reduced temperatures of 0.48 to 0.70 against the 0.7 "
    "bound and a reduced field of 0.3226 against the 0.3 bound. Section III.E "
    "and an earlier version of this letter both said one grid point; the "
    "assertion behind that wording checks that a single field is emitted, "
    "which is true, and we read it as a single grid point, which it is not. "
    "At 4.2 K and 5 T the 86 records span 0.0098 dex, 1.6% of the 0.60 dex "
    "bootstrap interval at that point; at 20 K and 5 T the 77 records span "
    "0.259 dex. "
    "At 20 K the explanation we gave holds: the conditioning fixes every "
    "parameter of the expression and the compound-specific inputs are the "
    "critical-field anchor and the transition temperature. The prediction "
    "regresses on the temperature term the model forms with a slope of 1.22 "
    "and an R squared of 0.996, recovering the family exponent of 1.14, so the "
    "candidate's own transition temperature enters exactly as described. "
    "At 4.2 K it cannot enter, and this is the part we had not seen. The model "
    "is anchored at a reference point, and its temperature term is the "
    "difference between log10(1 - T/Tc) and the same quantity at that "
    "reference. The reference temperature is 4.2 K. At 4.2 K the difference is "
    "therefore identically zero for every candidate whatever its transition "
    "temperature, and across 59 distinct anchors from 8.9 to 41.4 K the "
    "largest value that term takes is exactly zero. Every dispatched record "
    "also carries the same 15.5 T parent critical-field anchor, so the field "
    "term is one shared number. The prediction at that grid point is a single "
    "family-level constant, 4.980 in log10 Jc, which is the family's own "
    "critical-current anchor of 5.324 displaced by 0.344 dex by the shared "
    "field term. "
    "So the referee's reading is right and the figure supports it more "
    "strongly than we claimed. What the 0.0098 dex measures is not a spread "
    "between compounds. With the temperature term zero and the field anchor "
    "common, all 86 records have identical model inputs and differ only in "
    "their draw from one bootstrap stream over a pool of 18 fits. Resampling "
    "that pool 84 times independently returns a span of 0.0092 dex with a "
    "standard deviation of 0.0016, of which the observed value is an ordinary "
    "draw. The number is evidence that the predictor is constant at that point "
    "and evidence of nothing else, and we no longer offer it as a measured "
    "quantity. What would let us report a compound-resolved spread is a "
    "dispatch grid that does not evaluate at the anchor's own reference "
    "temperature, which the present grid does, and we state that as the "
    "specific change rather than as a general limitation.")

OLD_RESP_22 = (
    "We report the family median at the one grid point that survives the "
    "refusal gates, 4.2 K and 5 T, which is a reduced field of 0.3226 rather "
    "than the near-self-field point the referee identified.")
NEW_RESP_22 = (
    "We report the family median at 4.2 K and 5 T, one of the two grid points "
    "that survive the refusal gates, which is a reduced field of 0.3226 rather "
    "than the near-self-field point the referee identified.")

OLD_RESP_28 = (
    "over the 163 predictions that survive our refusal gates the median full "
    "width is 0.61 dex, a factor of about 4.1, and the manuscript now reports "
    "that.")
NEW_RESP_28 = (
    "over the 163 predictions that survive our refusal gates the median full "
    "width is 0.61 dex, a factor of about 4.1, and 0.60 dex at the 4.2 K grid "
    "point specifically. We should also say what that width is made of. On the "
    "three records carrying an exact critical-field anchor it is 0.395 dex; on "
    "the 83 carrying a parent anchor it is 0.602. The difference is a "
    "deterministic plus or minus 20 percent perturbation envelope on the "
    "parent anchor rather than bootstrap spread, so about a third of the "
    "quoted width is not sampling uncertainty. At the upper perturbation that "
    "envelope evaluates the model at a reduced field of 0.269, below the 0.3 "
    "applicability bound this revision introduced, which we flag as a defect "
    "in the envelope rather than defend.")

OLD_MS_130 = (
    "At 4.2 K and 5 T, the only grid point at which anything is dispatched, "
    "the 86 MgB2-class prediction records covering 84 distinct compounds span "
    "0.0098 dex, which is 1.6% of the 0.60 dex bootstrap interval at the same "
    "point. The family emits one value for every purpose the paper claims. "
    "This follows from the inference procedure of Section II.D: the "
    "substructure and sample-form conditioning fixes every parameter of "
    "Eq. (2), and the compound-specific inputs are the upper-critical-field "
    "anchor, which enters through the field term, and the "
    "transition-temperature anchor, which enters through the temperature term. "
    "Every dispatched record carries the same 15.5 T parent anchor, so the "
    "field term is common to all of them and the residual spread is about 60 "
    "times smaller than the uncertainty on any one prediction.")

NEW_MS_130 = (
    "The dispatch emits at two grid points. At 4.2 K and 5 T the 86 "
    "MgB2-class prediction records covering 84 distinct compounds span 0.0098 "
    "dex, which is 1.6% of the 0.60 dex bootstrap interval at the same point; "
    "at 20 K and 5 T the 77 records covering 75 compounds span 0.259 dex. Both "
    "points clear the gates of this revision, at reduced temperatures of 0.48 "
    "to 0.70 and a reduced field of 0.3226. An earlier version of this section "
    "called 4.2 K and 5 T the only grid point at which anything is dispatched, "
    "which is wrong. The family emits one value for every purpose the paper "
    "claims at the lower point, and this follows from the inference procedure "
    "of Section II.D in a more specific way than we previously stated. The "
    "substructure and sample-form conditioning fixes every parameter of "
    "Eq. (2); every dispatched record carries the same 15.5 T parent anchor, "
    "so the field term is common to all of them; and the model is anchored at "
    "a reference point whose temperature is 4.2 K, so at 4.2 K the temperature "
    "term is the difference of a quantity from itself and is identically zero "
    "for every candidate whatever its transition-temperature anchor. Across 59 "
    "distinct anchors from 8.9 to 41.4 K the largest value that term takes is "
    "exactly zero. The prediction at that grid point is therefore a single "
    "family-level constant, and the residual 0.0098 dex is the bootstrap draw "
    "over an 18-fit pool rather than variation between compounds: resampling "
    "that pool 84 times independently returns 0.0092 dex with a standard "
    "deviation of 0.0016. At 20 K the transition-temperature anchor does "
    "enter, and the prediction regresses on the temperature term with a slope "
    "of 1.22 and an R squared of 0.996, recovering the family exponent of "
    "1.14.")


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

    jobs = [
        (RESP, [(OLD_RESP_22, NEW_RESP_22, "A5, the one-grid-point aside"),
                (OLD_RESP_27, NEW_RESP_27, "A6, the small-spread answer"),
                (OLD_RESP_28, NEW_RESP_28, "A6, the interval width")]),
        (MS, [(OLD_MS_130, NEW_MS_130, "Sec. III.E, why no per-compound "
                                       "rankings")]),
    ]
    docs, all_missed = [], []
    for name, edits in jobs:
        d, missed = apply(os.path.join(SRC, name), edits)
        docs.append((name, d))
        all_missed += [(name, m) for m in missed]
        print("%s: %d edits, %d not found" % (name, len(edits), len(missed)))

    # The retracted number must not have reached a document.
    for name, d in docs:
        for p in d.paragraphs:
            if "0.2242" in p.text or "0.2255" in p.text:
                all_missed.append((name, "the retracted regenerated span is "
                                         "in the text"))
    if all_missed:
        print("\nNothing written.")
        for m in all_missed:
            print("  ", m)
        return 1
    if a.dry_run or not a.out_dir:
        print("\ndry run: nothing written")
        return 0
    os.makedirs(a.out_dir, exist_ok=True)
    for name, d in docs:
        d.save(os.path.join(a.out_dir, name.replace("_final4", "_final5")))
    print("\nwritten to %s" % a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
