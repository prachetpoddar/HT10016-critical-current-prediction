#!/usr/bin/env python3
"""Recompute the supplement's field-scale exposure and archive-size figures.

Both were static numbers with no generator, which is how they came to describe a
cohort that no longer exists.

The exposure figures need the field a fit actually used, not the field the paper
measured. Several curves are digitized well beyond the assigned critical scale
and the fit drops those points, so a ratio taken over every measured point comes
out above one and means nothing. Matching on the points below the assigned scale
reproduces the deposited window on 90 of 94 curves and the point counts on the
same 90, which is what makes the match checkable rather than asserted.

    python analysis/recompute_supplement_numbers.py --source <extraction csv>
"""
import argparse
import collections
import csv
import os

import pandas as pd
import re
import statistics as st

DATA = "data"
THREE = {"iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"}
ICONS = {"back", "filesave", "forward", "hand", "help", "home", "matplotlib",
         "move", "qt4_editor_options", "subplots", "zoom_to_rect"}
PROJECT_FIGURE = re.compile(
    r"^(bulk_correlation_plot|cross_class_kappa_jc0|figure_1_|"
    r"kappa_jc_extended_correlation|kappa_vs_tc_scatter|option_A_|"
    r"manuscript_figure_)")


def archive_size():
    rows = list(csv.DictReader(open(os.path.join(DATA, "caption_sweep.csv"))))
    non = [r for r in rows
           if r["pdf"][:-4] in ICONS or PROJECT_FIGURE.match(r["pdf"][:-4])]
    both = [r for r in rows if r["both"] == "1"]
    print("archive")
    print("   rows in caption_sweep.csv                 %d" % len(rows))
    print("   of which are not papers                   %d "
          "(%d matplotlib toolbar icons, %d project figures)"
          % (len(non), sum(1 for r in non if r["pdf"][:-4] in ICONS),
             sum(1 for r in non if PROJECT_FIGURE.match(r["pdf"][:-4]))))
    print("   papers                                    %d" % (len(rows) - len(non)))
    print("   captions naming both quantities           %d" % len(both))
    assert not any(b["pdf"][:-4] in ICONS or PROJECT_FIGURE.match(b["pdf"][:-4])
                   for b in both), "a non-paper reached the 'both' count"


def exposure(source):
    src = [r for r in csv.DictReader(open(source))
           if r["primary_scan_direction"] == "H"]
    fits = [r for r in csv.DictReader(
        open(os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv")))
        if r["ok"] == "True" and r["physicality"] == "ok"]
    grp = collections.defaultdict(list)
    for r in src:
        try:
            grp[(r["arxiv_id"], r["compound_formula"], r["doping_or_composition"],
                 round(float(r["fixed_axis_value"]), 3))].append(float(r["field_T"]))
        except ValueError:
            pass

    ratios, reproduced, counts_agree, matched = [], 0, 0, 0
    for f in fits:
        k = (f["arxiv_id"], f["compound_formula"], f["sample_identifier"],
             round(float(f["fixed_axis_value"]), 3))
        H = grp.get(k)
        if not H:
            continue
        hc2 = float(f["Hc2_T_used"])
        used = [h for h in H if h < hc2]
        if len(used) < 2:
            continue
        matched += 1
        if abs((max(used) - min(used)) / hc2
               - float(f["H_axis_range_normalized"])) <= 0.02:
            reproduced += 1
        if int(f["n_pts"]) == len(used):
            counts_agree += 1
        ratios.append(max(used) / hc2)

    print("\nscale of the exposure")
    print("   passing fits                              %d" % len(fits))
    print("   matched to a source curve                 %d" % matched)
    print("   deposited window reproduced               %d" % reproduced)
    print("   deposited point count reproduced          %d" % counts_agree)
    print("   median measured maximum / assigned scale  %.3f" % st.median(ratios))
    print("   ratio above 0.9                           %d of %d"
          % (sum(1 for x in ratios if x > 0.9), len(ratios)))

    sel = classify()

    q, tot = 0, 0
    for _i, row in sel.iterrows():
        k = (row.arxiv_id, row.compound_formula, row.sample_identifier,
             round(float(row.fixed_axis_value), 3))
        H = grp.get(k)
        if not H:
            continue
        tot += 1
        try:
            dflt = float(row.Hc2_T_default)
        except (TypeError, ValueError):
            continue
        used = [h for h in H if h < dflt]
        if len(used) >= 2 and (max(used) - min(used)) / dflt > 0.3:
            q += 1
    print("   clearing the 0.3 span against Hc2,0       %d of %d" % (q, tot))


AGREEMENT = os.path.join("audit", "dual_model_critical_field_agreement.csv")


def classify():
    """How the three dispatched families' field-axis curves get their scale.

    This reads deposited tables only, so it runs whether or not the extraction
    dataset behind the exposure ratio is available. Splitting it out of
    exposure() is what makes that possible: it was the only part of the
    function that did not need --source, and requiring an argument nobody can
    supply made it unreachable.
    """
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import compound_leave_one_out as clo
    _bt, fr = clo.load(DATA)
    sel = fr[fr.substructure.isin(THREE)]
    lab = collections.Counter()
    for s in sel.Hc2_source:
        if "H_irr" in s or "Birr" in s:
            lab["irreversibility field"] += 1
        elif "ambiguous" in s:
            lab["unlabelled"] += 1
        elif s.startswith("Tier_3"):
            lab["literature default"] += 1
        elif "Hc2" in s:
            lab["upper critical field"] += 1
        else:
            lab["other Tier 1 or 2"] += 1
    print("\nthe three dispatched families")
    print("   field-axis curves                         %d" % len(sel))
    for k, v in lab.most_common():
        print("   %-41s %d" % (k, v))
    print("   irreversibility field or unlabelled       %d of %d"
          % (lab["irreversibility field"] + lab["unlabelled"], len(sel)))
    return sel


def eight_paper_exposure():
    """How many field-axis curves take their scale from a paper the dual-model
    audit found carries no critical-field data at all.

    This used to be listed as not recomputable because the audit's paper list
    was not deposited. It is deposited now, as
    audit/dual_model_critical_field_agreement.csv, sixteen papers with a
    verdict each; the eight that matter are the AGREE_NO_DATA rows, where both
    extraction models independently reported that the paper prints no critical
    field.

    The join rule, stated here rather than left implicit: the fit table's
    arxiv_id carries a publisher prefix that the audit table does not, so the
    prefix is stripped before matching. Nothing else is transformed, and the
    seven papers that contribute curves all match exactly.
    """
    import compound_leave_one_out as clo
    if not os.path.exists(AGREEMENT):
        print("\n   %s is missing, so the eight-paper count is not "
              "recomputable" % AGREEMENT)
        return
    ag = pd.read_csv(AGREEMENT)
    eight = set(ag.loc[ag.verdict == "AGREE_NO_DATA", "paper"])
    _bt, fr = clo.load(DATA)
    sel = fr[fr.substructure.isin(THREE)].copy()

    def strip(a):
        t = str(a)
        for pre in ("elsevier_", "springer_", "iop_"):
            t = t.replace(pre, "")
        return t

    sel["key"] = sel.arxiv_id.map(strip)
    hit = sel[sel.key.isin(eight)]
    print("\nthe dual-model critical-field audit")
    print("   papers audited                            %d" % len(ag))
    print("   reporting no critical-field data          %d" % len(eight))
    print("   three-family curves taking their scale")
    print("      from one of those papers               %d of %d, %.0f%%"
          % (len(hit), len(sel), 100.0 * len(hit) / len(sel)))
    for k, n in hit.key.value_counts().items():
        print("         %-38s %d" % (k, n))
    unseen = sorted(eight - set(hit.key))
    if unseen:
        print("   audited papers contributing no curve      %s"
              % ", ".join(unseen))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source",
                    help="the wide-to-long extraction dataset behind the "
                         "field-axis fits (agent2_dataset_v3_2_2B.csv). Not in "
                         "this deposit; without it the exposure ratio is "
                         "skipped and the rest still runs.")
    args = ap.parse_args()
    archive_size()
    if args.source:
        exposure(args.source)
    else:
        # The ratio needs the per-point extraction dataset, which this deposit
        # does not carry. Saying so is better than requiring an argument nobody
        # can supply and thereby making the parts that DO recompute
        # unreachable: the three-family count, the irreversibility split and
        # the eight-paper exposure all read deposited tables only.
        print("\nscale of the exposure")
        print("   skipped: pass --source with the extraction dataset behind "
              "the field-axis fits")
        classify()
    eight_paper_exposure()
    print("\nNot recomputable here: the count qualifying after the "
          "magnetic-field unit corrections, which needs the pre-correction "
          "extraction dataset.")


if __name__ == "__main__":
    main()
