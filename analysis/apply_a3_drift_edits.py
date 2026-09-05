#!/usr/bin/env python3
"""Rewrite A3's quantification of the exponent drift.

Everything here comes from analysis/exponent_drift_series.py, which went
through the adversarial-review gate. The gate refuted the first version of that
analysis, which claimed the letter's figures never reproduced. They reproduce
exactly on the release table; the error was mine, in a grouping key that split
eight papers' temperature sweeps into singletons.

What changes.

  The three aggregate figures are restated on the current table and labelled
  with the table each belongs to. 18 series at three or more temperatures with
  a median absolute rank correlation of 0.700 and 9 at four or more with 0.800
  were correct at deposit; the withdrawals reduce them to 13 and 6, both at
  0.800. The effect the referee anticipated is unchanged in direction and
  slightly stronger in magnitude.

  The worked example is replaced, for two independent reasons that the letter
  states rather than picks between. Its field axis is kilo-oersted recorded as
  tesla, so corrected it fails the applicability bound and its fits were
  withdrawn. And its exponent is not monotone over the quoted window: it falls
  from 1.252 at 2 K to 0.819 at 10 K before rising to 12.145 at 35 K, so the
  sentence describes a rise that does not happen over the first third of the
  range.

  The replacement carries its own caveat in the same sentence. Exactly two
  series in the surviving cohort clear the filters, both from one paper, and
  the usable one is graded weak: 1.3 to 1.7 times high with a wrong tail. A
  worked example offered without that grading would repeat the A1 defect.

Source out_a1/*_final7.docx, output out_a3/.

    python analysis/apply_a3_drift_edits.py --dry-run
    python analysis/apply_a3_drift_edits.py --out-dir out_a3

Run from the repository root.
"""
import argparse
import os

import docx

SRC = "out_a1"
RESP = "RESPONSE_TO_REFEREES_final7.docx"

OLD = (
    "Across the 18 series in which one scale was held over three or more "
    "measurement temperatures, the median absolute rank correlation between "
    "exponent and temperature is 0.70, rising to 0.80 in the nine series "
    "sampled at four or more temperatures. In the clearest case, "
    "SmFeAsO0.8F0.2 with a scale held at 86 T, the fitted exponent runs from "
    "1.25 to 12.14 as the temperature rises from 2 to 35 K.")

NEW = (
    "Across the series in which one scale was held over three or more "
    "measurement temperatures, the median absolute rank correlation between "
    "exponent and temperature is 0.80. That figure has moved since the "
    "deposited version of this analysis and we give both: on the table as "
    "first deposited there were 18 such series with a median of 0.70, rising "
    "to 0.80 in the nine sampled at four or more temperatures, and after the "
    "withdrawals described below there are 13 and 6, both at 0.80. The effect "
    "the referee anticipated is unchanged in direction and slightly larger. "
    "A series here is one source paper, one sample and one held critical "
    "scale, which is what makes the scale held by construction; the statistic "
    "is the rank correlation between the fixed measurement temperature and the "
    "fitted field exponent. "
    "We withdraw the worked example we gave, for two reasons rather than one. "
    "Its source, Physica C 469 (2009) 590, prints its field axis in "
    "kilo-oersted and the extraction recorded the bare numbers as tesla; "
    "corrected, the measured span falls from 0.53 to 0.053 of the assigned "
    "scale, all eight of its fits fail the 0.3 applicability bound, and they "
    "are withdrawn. Independently of that, the exponent is not monotone over "
    "the window we quoted: it falls from 1.25 at 2 K to 0.82 at 10 K before "
    "rising to 12.14 at 35 K, and the rank correlation over that window is "
    "0.79 rather than the near-unity our phrasing implied. The sentence "
    "described a rise that does not happen over the first third of its own "
    "range, and we would have had to correct it whatever became of the unit. "
    "In its place, and with a caveat we state rather than leave for the "
    "reader to find: the clearest surviving case is the Ba(Fe,Co)2As2 single "
    "crystal of Materials Today Physics 27 (2022) 100783, with a scale held "
    "at 4.5 T, whose fitted exponent rises from 0.26 to 0.86 across nine "
    "measurement temperatures from 4.2 to 18 K with a rank correlation of "
    "1.00. Exactly two series in the surviving cohort clear our filters and "
    "both come from that paper, the other being a polycrystal record we have "
    "since identified as a copy of this one and withdrawn. This record is "
    "itself graded weak in our audit, sitting 1.3 to 1.7 times above a "
    "retrace of its own figure with a wrong tail, so we offer it as the best "
    "surviving illustration and not as a clean one.")


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    d = docx.Document(os.path.join(SRC, RESP))
    if not any(replace_in_paragraph(p, OLD, NEW) for p in d.paragraphs):
        print("the A3 passage was not found. Nothing written.")
        return 1
    print("%s: 1 edit applied" % RESP)

    # The withdrawn example must not survive anywhere unqualified, and the
    # retracted "never reproduced" framing must not have reached the document.
    bad = []
    for p in d.paragraphs:
        t = p.text
        if "SmFeAsO0.8F0.2" in t and "withdraw" not in t:
            bad.append("the withdrawn example appears unqualified")
        if "does not reproduce" in t and "18 series" in t:
            bad.append("the retracted framing is in the text")
    if bad:
        print("\nNothing written.")
        for b in sorted(set(bad)):
            print("  ", b)
        return 1
    print("the withdrawn example appears only where it is withdrawn")

    if a.dry_run or not a.out_dir:
        print("\ndry run: nothing written")
        return 0
    os.makedirs(a.out_dir, exist_ok=True)
    d.save(os.path.join(a.out_dir, RESP.replace("_final7", "_final8")))
    print("\nwritten to %s" % a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
