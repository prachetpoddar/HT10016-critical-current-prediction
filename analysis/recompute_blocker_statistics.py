#!/usr/bin/env python3
"""Recompute, on the repaired cohort, the statistics that could not simply be
renumbered.

audit/repaired_cohort_edits_20260905.md lists passages that were left alone
when the census counts were corrected, because each quotes a cohort size beside
a statistic computed on that cohort. Changing 94 to 52 next to a median taken
over the 94 would be the same class of error the correction exists to remove.
This script computes the replacements.

It went through adversarial review before anything here was reported, and the
review found seven defects that changed an answer. Each is now either fixed or
printed as a caveat beside the number it qualifies, because most of them are
not bugs that can be fixed away: they are properties of the repaired cohort
that make a like-for-like comparison impossible, and the honest output is the
comparison plus the reason it does not mean what it looks like.

What changed after review, in the order the numbers moved.

  The field exponent scored was the wrong one. beta_repaired in the anchor
  repair table is bit-identical to the protocol table's beta_nofloor, the
  exponent fitted WITHOUT the retention floor the stated protocol imposes. The
  cohort was defined by the protocol and the numbers were the pre-protocol
  ones. The protocol's beta is used now; it differs on 3 of the 52 by up to
  0.183.

  The deposited intervals were reported at the wrong seed. The deposit was
  computed at seed 20260901 and this script ran at 0. Point estimates are
  seed-invariant so nothing looked wrong, but the Stage 2 upper bound moved by
  0.025. Both arms now run at the deposited seed and the deposited arm is
  asserted against audit/per_paper_field_validation.csv.

  The Stage 2 arms are not the same statistic. Stage 2 conditions on
  substructure and sample form, so a fit with no matching pool from another
  paper is unscorable. On the deposit that drops 12 of 94 and leaves a cohort
  that is 73 percent iron-based. On the repaired cohort it drops 33 of 52 and
  leaves 19 fits that are 89 percent MgB2. The two numbers are the error of
  different material classes. The composition of both is printed.

  The interval on 19 fits is not an interval. per_paper_validation resamples
  residuals independently, and the residuals are clustered by paper: one paper
  supplies 7 of the 19. A paper-level resample is computed alongside and is
  reported as the one to read.

  The scale-of-exposure ratio changed its denominator. The published figure
  divides by Hc2_T_used; an earlier version of this script divided by the
  repaired anchor and set the result beside the published one. All three rules
  are computed now and the like-for-like row is labelled.

  The dispersion control was computed on a different cohort from the error it
  normalises. Each arm's spread is now measured on that arm's own fits.

  The bootstrap fraction is not a test of the predictor. It counts resamples
  whose error falls below a fixed 1.0, and predicting every fit by its family's
  own median already gives an error equal to the family's mean absolute
  deviation. Every family whose deviation is below 1.0 clears the threshold
  with a predictor that has no leave-one-out content. The deviation is printed
  next to the fraction and the ratio of the two is printed as well, and it
  exceeds 1 in every family in both arms, which is to say the leave-one-out
  predictor is worse than the in-sample family median everywhere.

What this script does not do.

  It does not build its own predictor. Blockers 1, 2 and 4 come from
  analysis/compound_leave_one_out.py, which is imported and called rather than
  reimplemented, so that any difference between the two columns is the cohort
  and not a rewrite. The only additions are the paper-level resample and the
  cell composition, both of which read that module's own cohort.

  It does not touch blocker 5, which is re-derived by re-running the original
  closed-form fitter in analysis/rerun_closed_form_without_withdrawn.py.

The repaired cohorts, and the rule that defines each.

  Temperature axis. The 257 fits of
  data/phase_3_p44_post_UCLA_beta_T_fits_repaired.csv that reproduce from the
  extraction and carry a finite exponent after the Tc repairs. beta_T is the
  repaired exponent. Three fits do not reproduce and are dropped.

  Field axis. The 52 fits admitted by analysis/fit_protocol.py, the stated
  protocol applied to the repaired anchors, carrying that protocol's exponent.
  physicality is written "ok" and no other row is carried, because
  compound_leave_one_out.load() filters on that column. On this cohort the
  relabelling is a no-op: all 52 already carried "ok", so nothing that failed
  the physicality gate is admitted here and the substitution is untested.

    python analysis/recompute_blocker_statistics.py

Run from the repository root.
"""
import collections
import os
import shutil
import statistics as st
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compound_leave_one_out as clo          # noqa: E402

DATA = "data"
BASE_REPAIRED = os.path.join("audit", "repaired_base_20260905")
FITS_A = os.path.join(DATA, "phase_3_p44_post_UCLA_beta_T_fits.csv")
FITS_A_REP = FITS_A.replace(".csv", "_repaired.csv")
FITS_B_REP = os.path.join(DATA,
                          "phase_3_form3_fits_partial_cohortB_v2_repaired.csv")
PROTOCOL = os.path.join("audit", "fit_protocol_applied.csv")
ANCHORS = os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv")
DEPOSITED_PP = os.path.join("audit", "per_paper_field_validation.csv")
SOURCE_B = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
            "agent2_dataset_v3_2_2B.csv")
# analysis/fit_protocol.py's H_FLOOR, the fraction of the anchor a retained
# point has to stay below.
FLOOR = 0.05
OUT = os.path.join("audit", "blocker_statistics_repaired.csv")

# The deposit's own settings. Running at anything else reproduces the deposited
# point estimates and not the deposited intervals, which is how a wrong seed
# survives inspection.
ITERS = 2000
SEED = 20260901
PP_ITERS = 5000

# What the documents print. Read, not decorative: the deposited arm is asserted
# against these before either arm is reported.
PRINTED = {
    "temperature cohort": 260,
    "temperature MAE": {"iron_chalcogenide_11": 0.5880938940339523,
                        "iron_pnictide_122": 1.314362897725905,
                        "iron_pnictide_1111": 3.1201737077470875},
    "field cohort": 94,
    "field papers": 16,
    "stage2": (82, 1.2566204273398942, 1.0062406281275498, 1.611549322809956),
    "pooled": (94, 1.1578103275780431, 0.9001851869187484, 1.4967057875217746),
    "scale ratio median": 0.80,
    "scale ratio above 0.9": (15, 94),
}


def build_repaired_base():
    """Assemble the two repaired cohorts. Writing them is a separate step."""
    a = pd.read_csv(FITS_A_REP)
    keep = a[a.reproduced & np.isfinite(a.beta_T_repaired)].copy()
    dropped = len(a) - len(keep)
    keep["beta_T_as_deposited"] = keep.beta_T
    keep["beta_T"] = keep.beta_T_repaired
    b = pd.read_csv(FITS_B_REP)
    p = pd.read_csv(PROTOCOL)
    # The protocol's own exponent, not the anchor table's. beta_repaired there
    # is the no-floor fit; the floor is Decision 1 of the stated protocol and
    # dropping it scores a cohort the protocol defined with numbers the
    # protocol rejected.
    n_admitted = int(p.admitted.sum())
    ad = p[p.admitted][["paper", "sample", "T", "beta", "beta_nofloor",
                        "has_lever", "admitted", "clears_field_clause"]].copy()
    ad = ad.rename(columns={"beta": "beta_protocol"})
    b["T"] = b.fixed_axis_value
    m = b.merge(ad, left_on=["paper_key", "sample_identifier", "T"],
                right_on=["paper", "sample", "T"], how="inner")
    if len(m) != len(ad):
        raise SystemExit("the admitted set did not join one to one: %d rows "
                         "from %d admitted fits" % (len(m), len(ad)))
    if m.duplicated(["paper_key", "sample_identifier", "T"]).any():
        raise SystemExit("the join produced duplicate fits")
    m["beta_as_deposited"] = m.beta
    m["beta_anchor_repaired"] = m.beta_repaired
    m["beta"] = m.beta_protocol
    m["physicality_as_deposited"] = m.physicality
    m["physicality"] = "ok"
    if not m.admitted.all() or len(m) != n_admitted:
        raise SystemExit("the field cohort is not the admitted set: %d rows, "
                         "%d admitted in the protocol table"
                         % (int(m.admitted.sum()), n_admitted))
    m = m.drop(columns=["paper", "sample", "T"])

    moved = int((m.beta_protocol - m.beta_anchor_repaired).abs().gt(1e-12).sum())
    print("repaired cohorts assembled")
    print("   temperature-axis fits   %d kept, %d dropped as unreproduced"
          % (len(keep), dropped))
    print("   field-axis fits         %d admitted by the stated protocol, "
          "%d papers" % (len(m), m.arxiv_id.nunique()))
    print("   the retention floor moves the exponent on %d of them, by up to "
          "%.4f" % (moved, (m.beta_protocol - m.beta_anchor_repaired)
                    .abs().max()))
    print("   %d of the %d admitted fits clear the field clause without "
          "clearing the lever" % (int((~m.has_lever).sum()), len(m)))
    return keep, m


def write_base(keep, m):
    """The three tables compound_leave_one_out.load() reads."""
    os.makedirs(BASE_REPAIRED, exist_ok=True)
    keep.to_csv(os.path.join(BASE_REPAIRED,
                             "phase_3_p44_post_UCLA_beta_T_fits.csv"),
                index=False)
    m.to_csv(os.path.join(BASE_REPAIRED,
                          "phase_3_form3_fits_partial_cohortB_v2.csv"),
             index=False)
    shutil.copyfile(ANCHORS,
                    os.path.join(BASE_REPAIRED,
                                 "phase_3_p31_jc_anchor_per_paper.csv"))
    print("   written to %s" % BASE_REPAIRED)


def selftest(keep, m):
    """Guards on the base. Each has been shown to fire on the input it guards.

    Two guards an earlier version carried are gone. They compared a column
    against the column it had been assigned from three lines earlier, so they
    were tautologies: the mutation they were written to catch, assigning in the
    reverse direction, left them passing and silently turned the repaired arm
    into the deposited one. They are replaced by comparisons against the
    deposited file, which is the only thing that can tell the two apart.
    """
    fails = []
    dep = pd.read_csv(FITS_A)

    # The repaired exponents must actually differ from the deposited ones, on
    # the fits the repair table says it touched. This is what a reversed
    # assignment breaks and what an equality check against the source cannot
    # see.
    touched = keep[keep.repair.notna()
                   & ~keep.repair.astype(str).str.startswith("Tc unchanged")]
    same = int(np.isclose(touched.beta_T.values,
                          touched.beta_T_as_deposited.values).sum())
    if len(touched) == 0:
        fails.append("no fit is marked as repaired")
    elif same > 0.5 * len(touched):
        fails.append("%d of %d repaired fits carry the deposited exponent"
                     % (same, len(touched)))

    # The temperature cohort must be a subset of the deposited one and must
    # carry the deposited exponent in its comparison column.
    dm = dep.set_index(["paper_id", "field_T", "Tc_K"]).beta_T
    km = keep.set_index(["paper_id", "field_T", "Tc_K"]).beta_T_as_deposited
    common = km.index.intersection(dm.index)
    if len(common) < 0.9 * len(km):
        fails.append("only %d of %d repaired fits match a deposited fit"
                     % (len(common), len(km)))
    elif not np.allclose(km.loc[common].values, dm.loc[common].values):
        fails.append("beta_T_as_deposited is not the deposited exponent")

    # The scored field exponent must differ from the deposited one. Comparing
    # it against beta_protocol, the column it was assigned from, is a
    # tautology: a first version did that and the reversed assignment, which
    # scores the deposited exponent and moves the repaired Stage 2 error from
    # 1.57 to 1.04, passed every guard.
    # The scored exponent should differ materially from the deposited one on
    # exactly the fits whose anchor moved or whose retention floor bites, and
    # on no others. Those two conditions are read from the anchor columns and
    # from beta_nofloor, neither of which the assignment touches, so the count
    # is an independent prediction. The two populations separate by three
    # orders of magnitude, 4e-5 against 1.5e-2, so the 1e-3 cut is not near
    # anything.
    anchor_moved = (m.Hc2_repaired - m.Hc2_T_used).abs() > 1e-12
    floor_bites = (m.beta - m.beta_nofloor).abs() > 1e-12
    want = int((anchor_moved | floor_bites).sum())
    got = int((m.beta - m.beta_as_deposited).abs().gt(1e-3).sum())
    if got != want:
        fails.append("%d field fits differ materially from the deposited "
                     "exponent, %d should" % (got, want))
    if int(floor_bites.sum()) == 0:
        fails.append("the retention floor moves no exponent, so the scored "
                     "column is the no-floor fit")

    # physicality is assigned "ok" two lines above, so checking it here proves
    # nothing. What matters is that no row entered carrying a physicality the
    # deposit rejected, which is a property of the cohort and not of the
    # assignment.
    bad_phys = sorted(set(m.physicality_as_deposited) - {"ok"})
    if bad_phys:
        fails.append("relabelled as ok despite a deposited physicality of %s"
                     % ", ".join(bad_phys))
    if not m.passing_repaired.all():
        fails.append("an admitted fit does not pass the repaired anchor test")

    an = pd.read_csv(ANCHORS)
    fmap = an.drop_duplicates("paper_id").set_index("paper_id") \
             .substructure.to_dict()
    miss = sorted(set(m.arxiv_id) - set(fmap))
    if miss:
        fails.append("no family label for %s" % ", ".join(miss))

    print("\nselftest, 8 guards")
    for f in fails:
        print("   FAIL %s" % f)
    if not fails:
        print("   all pass")
    return not fails


LOO_T = os.path.join("audit", "temperature_axis_leave_one_out.csv")


def check_deposited_arm(dep_run, pp_dep, pp_pool_dep):
    """The deposited arm has to come back as the deposit, or the comparison is
    against something nobody published.

    The strata are checked as well as the point estimates, because the point
    estimates do not depend on the resample count and the strata do. Without
    this, halving ITERS moves every resample fraction printed and nothing
    notices.
    """
    bad = []
    for name, v in PRINTED["temperature MAE"].items():
        got = dep_run["temperature"][name][0]
        if abs(got - v) > 1e-9:
            bad.append("%s MAE %.6f, deposited %.6f" % (name, got, v))
    for label, got, want in [("stage2", pp_dep, PRINTED["stage2"]),
                             ("pooled", pp_pool_dep, PRINTED["pooled"])]:
        if got[3] != want[0]:
            bad.append("%s scored %d fits, deposited %d" % (label, got[3],
                                                            want[0]))
        for i, j in ((0, 1), (1, 2), (2, 3)):
            if abs(got[i] - want[j]) > 1e-6:
                bad.append("%s value %d is %.6f, deposited %.6f"
                           % (label, i, got[i], want[j]))
    if os.path.exists(LOO_T):
        want = pd.read_csv(LOO_T)
        for _i, row in want.iterrows():
            st_ = dep_run["temperature"][row.substructure][3] \
                .get(int(row.resample_n_compounds))
            if st_ is None:
                bad.append("%s has no %d-compound stratum"
                           % (row.substructure, row.resample_n_compounds))
                continue
            if st_["n"] != int(row.n_resamples) or \
                    st_["hits"] != int(row.n_below_threshold):
                bad.append("%s %dc stratum %d/%d, deposited %d/%d"
                           % (row.substructure, row.resample_n_compounds,
                              st_["hits"], st_["n"], row.n_below_threshold,
                              row.n_resamples))
    else:
        bad.append("%s is missing, the strata cannot be checked" % LOO_T)
    if pp_dep[4] != PRINTED["field papers"]:
        bad.append("deposited per-paper cohort has %d papers, published %d"
                   % (pp_dep[4], PRINTED["field papers"]))
    print("\nthe deposited arm against the deposited files")
    if bad:
        for b in bad:
            print("   FAIL %s" % b)
        return False
    print("   temperature MAEs, bootstrap strata and both per-paper rows "
          "reproduce the deposit")
    print("   the deposited field-axis MAEs printed below are the "
          "post-withdrawal regeneration")
    print("   of Table III, not the values Table III prints: "
          "iron_chalcogenide_11 and iron_pnictide_1111")
    print("   were 0.6412 and 3.0656 before the withdrawals and the "
          "sample-form corrections")
    return True


def cluster_bootstrap(f, seed, iters=PP_ITERS, conditioned=True):
    """The per-paper statistic with papers, not residuals, as the unit.

    compound_leave_one_out.per_paper_validation resamples the residual vector
    independently. Its residuals are clustered by paper, and in the repaired
    Stage 2 arm one paper supplies 7 of 19, so an independent resample treats
    seven readings of one figure as seven independent observations and returns
    an interval that is too narrow. This keeps each paper's residuals together.
    It does not re-run the leave-one-paper-out loop, so the uncertainty in the
    training median is still not represented in either version.
    """
    blocks = {}
    for p in f.arxiv_id.unique():
        train = f[f.arxiv_id != p]
        test = f[f.arxiv_id == p]
        if train.empty:
            continue
        r = []
        if not conditioned:
            r = list((test.beta - train.beta.median()).abs().values)
        else:
            for _i, row in test.iterrows():
                pool = train[(train.substructure == row.substructure)
                             & (train.sample_form == row.sample_form)]
                if pool.empty:
                    continue
                r.append(abs(row.beta - pool.beta.median()))
        if r:
            blocks[p] = np.asarray(r, dtype=float)
    keys = list(blocks)
    rng = np.random.default_rng(seed)
    draws = np.empty(iters)
    for i in range(iters):
        pick = rng.integers(0, len(keys), len(keys))
        draws[i] = np.concatenate([blocks[keys[j]] for j in pick]).mean()
    allr = np.concatenate([blocks[k] for k in keys])
    return (float(allr.mean()), float(np.percentile(draws, 2.5)),
            float(np.percentile(draws, 97.5)), len(allr), len(keys))


def stage2_cells(f):
    """Which substructure and sample-form cells Stage 2 can actually score.

    Printed because the two arms are not the same statistic and nothing else
    in the output says so. A fit whose (substructure, sample form) cell is
    represented by no other paper has no pool and is dropped, so the scored set
    is a projection of the cohort and not the cohort.
    """
    cells = collections.Counter()
    for p in f.arxiv_id.unique():
        train = f[f.arxiv_id != p]
        test = f[f.arxiv_id == p]
        if train.empty:
            continue
        for _i, row in test.iterrows():
            pool = train[(train.substructure == row.substructure)
                         & (train.sample_form == row.sample_form)]
            if len(pool):
                cells[(row.substructure, row.sample_form)] += 1
    return cells


def pooled_fraction(strata):
    """The fraction of scorable resamples clearing the threshold, with the
    strata that make it up.

    compound_leave_one_out states, as a design decision, that a single pooled
    fraction must not be reported because the strata are not comparable: a
    two-compound resample predicts a held-out compound from exactly one other.
    The pooled number is computed here because the manuscript quotes one, and
    the strata are returned with it so the printout can show what carries it.
    """
    if not strata:
        return float("nan"), ""
    scor = sum(s["n"] for k, s in strata.items() if k >= 2)
    hits = sum(s["hits"] for k, s in strata.items() if k >= 2)
    parts = []
    for k in sorted(strata):
        s = strata[k]
        if k < 2:
            parts.append("%dc unscorable" % k)
            continue
        parts.append("%dc %d/%d, %d distinct"
                     % (k, s["hits"], s["n"], len(s["multisets"])))
    return (hits / scor if scor else float("nan")), "; ".join(parts)


def dispersion(frame, col, families):
    """Mean absolute deviation from the family median, on the frame's own fits.

    This is the error of predicting every fit by its family's median with no
    fit held out, so it is the floor a leave-one-compound-out predictor has to
    beat, and it is what the fixed threshold of 1.0 is really testing. An
    earlier version computed both arms' deviations from the 257 surviving fits
    while the deposited error came from all 260, which made the ratio of the
    two incoherent. Each arm now uses its own cohort.
    """
    out = {}
    for name in families:
        s = frame[frame.substructure == name]
        if s.empty:
            continue
        v = s[col].values
        out[name] = (float(np.mean(np.abs(v - np.median(v)))), len(s),
                     s.compound_formula.nunique())
    return out


def family_counts(keep, dep):
    print("\nblocker 2, composition of the temperature-exponent cohort\n")
    print("   %-40s %8s %8s" % ("", "deposited", "repaired"))
    print("   %-40s %8d %8d" % ("fits", len(dep), len(keep)))
    print("   %-40s %8d %8d" % ("distinct compounds",
                                dep.compound_formula.nunique(),
                                keep.compound_formula.nunique()))
    mg_d = int(dep.compound_formula.astype(str).str.contains("MgB").sum())
    mg_r = int(keep.compound_formula.astype(str).str.contains("MgB").sum())
    print("   %-40s %8d %8d" % ("MgB2 fits", mg_d, mg_r))
    if mg_d == 0:
        print("      the absence of MgB2 is not a consequence of the repair; "
              "the deposited cohort has none either")
    cd = dep.compound_formula.value_counts()
    cr = keep.compound_formula.value_counts()
    for name in cd.index:
        print("      %-37s %8d %8d" % (name, cd[name], cr.get(name, 0)))
    gone = sorted(set(cd.index) - set(cr.index))
    if gone:
        print("      the two compounds the repair removes are single fits: %s"
              % ", ".join("%s (%d)" % (g, cd[g]) for g in gone))
    return cr


def scale_ratio(m):
    """Blocker 3: measured maximum over assigned scale, on the admitted 52.

    Three rules, because they give three answers and only one of them can be
    set beside the published figure.

      published rule. Divide by Hc2_T_used and take the points below it. This
      is what analysis/recompute_supplement_numbers.py does and what produced
      the published 0.80 over 94 curves. Applied to the 52 it is the
      like-for-like recompute.

      repaired scale. Divide by the repaired anchor instead. A different
      quantity: it reports the exposure of the cohort against the scale the
      audit assigned, not against the scale the published figure used.

      the fit's own points. The window and exponent in the repaired table were
      cut at the OLD anchor, or at 0.95 of it, whichever reproduced the
      deposited fit, and then divided by the REPAIRED anchor. The protocol's
      retention floor then cuts at 0.05 of the repaired one. None of those is
      "points below the assigned scale". This row uses the set that actually
      produced range_repaired, recovering the per-fit factor by requiring the
      point count to match n_pts_repaired, and it is the row whose window
      reproduction should be high.

      the protocol's retained points. retain() cuts at the repaired anchor and
      then drops any point within 0.05 of it, so this is the set the admitted
      exponents were actually fitted on. A floor at 0.05 caps the ratio at 0.95
      by construction, so "above 0.9" on this row can only mean "in 0.90 to
      0.95". An earlier version printed that caveat under the other three rows,
      where it is false: on the published rule 6 of the 11 ratios above 0.9 are
      also above 0.95.

    Each row is checked against the target that belongs to it. The published
    rule reproduces the deposited window and point count, H_axis_range_
    normalized and n_pts; the repaired rules reproduce range_repaired and
    n_pts_repaired. Scoring the published rule against the repaired target,
    which a first version did, understated its reproduction by six fits.
    """
    print("\nblocker 3, scale of the exposure, on the admitted cohort")
    if not os.path.exists(SOURCE_B):
        print("   skipped: %s is not present" % SOURCE_B)
        return None
    src = pd.read_csv(SOURCE_B, low_memory=False)
    src = src[src.primary_scan_direction == "H"]
    grp = {k: g for k, g in src.groupby(
        ["arxiv_id", "compound_formula", "doping_or_composition"])}

    # label, cut column, cut factor (None = recover per fit), denominator,
    # window target, point-count target, apply the protocol floor
    rules = [
        ("published rule, Hc2_T_used", "Hc2_T_used", 1.0, "Hc2_T_used",
         "H_axis_range_normalized", "n_pts", False),
        ("repaired scale", "Hc2_repaired", 1.0, "Hc2_repaired",
         "range_repaired", "n_pts_repaired", False),
        ("the fit's own points", "Hc2_T_used", None, "Hc2_repaired",
         "range_repaired", "n_pts_repaired", False),
        ("the protocol's retained points", "Hc2_repaired", 1.0, "Hc2_repaired",
         None, None, True),
    ]
    print("\n   %-30s %8s %8s %10s %10s %10s"
          % ("rule", "matched", "median", "above 0.9", "window ok", "n_pts ok"))
    rows = []
    for label, col, fac, dcol, wcol, ncol, floor in rules:
        ratios, matched, repro, counts = [], 0, 0, 0
        for _i, r in m.iterrows():
            g = grp.get((r.arxiv_id, r.compound_formula, r.sample_identifier))
            if g is None:
                continue
            g = g[np.isclose(g.fixed_axis_value.astype(float),
                             float(r.fixed_axis_value), atol=1e-6)]
            H = pd.to_numeric(g.field_T, errors="coerce").dropna().values
            scale = float(r[col])
            if fac is None:
                # apply_anchor_repairs picked 1.0 or 0.95 per fit, whichever
                # reproduced the deposited point count, and did not record
                # which. Recovering it by the point count is exact where the
                # two differ and immaterial where they do not.
                cand = [f for f in (1.0, 0.95)
                        if len(H[H < f * scale]) == int(r.n_pts_repaired)]
                f_use = cand[0] if cand else 1.0
            else:
                f_use = fac
            used = H[H < f_use * scale]
            if floor:
                used = used[1.0 - used / scale >= FLOOR]
            if len(used) < 2:
                continue
            matched += 1
            denom = float(r[dcol])
            if wcol is not None and abs((used.max() - used.min()) / denom
                                        - float(r[wcol])) <= 0.02:
                repro += 1
            if ncol is not None and int(r[ncol]) == len(used):
                counts += 1
            ratios.append(used.max() / denom)
        rows.append((label, matched, st.median(ratios), ratios))
        print("   %-30s %8d %8.3f %6d/%-3d %10s %10s"
              % (label, matched, st.median(ratios),
                 sum(1 for x in ratios if x > 0.9), len(ratios),
                 "%d/%d" % (repro, matched) if wcol else "n/a",
                 "%d/%d" % (counts, matched) if ncol else "n/a"))
    # The published rule, run over the deposited passing cohort, has to return
    # the published figure. Without this nothing pins the rule itself, and
    # swapping the denominator in the first row would move the like-for-like
    # answer with no diagnostic at all.
    dep_b = pd.read_csv(os.path.join(DATA,
                                     "phase_3_form3_fits_partial_cohortB_v2.csv"))
    dep_b = dep_b[(dep_b.ok.astype(str) == "True")
                  & (dep_b.physicality == "ok")]
    dr = []
    for _i, r in dep_b.iterrows():
        g = grp.get((r.arxiv_id, r.compound_formula, r.sample_identifier))
        if g is None:
            continue
        g = g[np.isclose(g.fixed_axis_value.astype(float),
                         float(r.fixed_axis_value), atol=1e-6)]
        H = pd.to_numeric(g.field_T, errors="coerce").dropna().values
        hc2 = float(r.Hc2_T_used)
        used = H[H < hc2]
        if len(used) >= 2:
            dr.append(used.max() / hc2)
    ok = (abs(st.median(dr) - PRINTED["scale ratio median"]) < 0.005
          and sum(1 for x in dr if x > 0.9) == PRINTED["scale ratio above 0.9"][0]
          and len(dr) == PRINTED["scale ratio above 0.9"][1])
    print("\n   the same rule on the deposited passing cohort  %.3f, %d of %d"
          % (st.median(dr), sum(1 for x in dr if x > 0.9), len(dr)))
    print("   as published                                   %.2f, %d of %d  %s"
          % (PRINTED["scale ratio median"], *PRINTED["scale ratio above 0.9"],
             "matches" if ok else "DOES NOT MATCH"))
    if not ok:
        raise SystemExit("the published rule does not reproduce the published "
                         "figure, so no row here is like-for-like")
    print("   the like-for-like row is the first. Exposure rises: the share "
          "above 0.9 moves from")
    print("   %d of %d, %.0f percent, to %d of %d, %.0f percent."
          % (PRINTED["scale ratio above 0.9"][0],
             PRINTED["scale ratio above 0.9"][1],
             100.0 * PRINTED["scale ratio above 0.9"][0]
             / PRINTED["scale ratio above 0.9"][1],
             sum(1 for x in rows[0][3] if x > 0.9), len(rows[0][3]),
             100.0 * sum(1 for x in rows[0][3] if x > 0.9) / len(rows[0][3])))
    return rows


def main():
    keep, m = build_repaired_base()
    if not selftest(keep, m):
        raise SystemExit("selftest failed, nothing reported")
    # The base is written only once the guards pass, so a failed run cannot
    # leave a directory labelled "repaired" for another script to read.
    write_base(keep, m)

    dep_a = pd.read_csv(FITS_A)
    if len(dep_a) != PRINTED["temperature cohort"]:
        raise SystemExit("the deposited temperature table holds %d fits, the "
                         "documents print %d"
                         % (len(dep_a), PRINTED["temperature cohort"]))
    family_counts(keep, dep_a)
    sc = scale_ratio(m)

    print("\nrunning the deposited cohort")
    dep = clo.run(DATA, ITERS, SEED, verbose=False)
    print("running the repaired cohort")
    rep = clo.run(BASE_REPAIRED, ITERS, SEED, verbose=False)

    _bt_d, f_d = clo.load(DATA)
    if len(f_d) != PRINTED["field cohort"]:
        raise SystemExit("the deposited passing field cohort holds %d fits, "
                         "the documents print %d"
                         % (len(f_d), PRINTED["field cohort"]))
    _bt_r, f_r = clo.load(BASE_REPAIRED)
    pp_d = clo.per_paper_validation(f_d, PP_ITERS, SEED, conditioned=True)
    pp_pd = clo.per_paper_validation(f_d, PP_ITERS, SEED, conditioned=False)
    pp_r = clo.per_paper_validation(f_r, PP_ITERS, SEED, conditioned=True)
    pp_pr = clo.per_paper_validation(f_r, PP_ITERS, SEED, conditioned=False)
    if not check_deposited_arm(dep, pp_d, pp_pd):
        raise SystemExit("the deposited arm does not reproduce the deposit")

    spread_d = dispersion(pd.read_csv(FITS_A), "beta_T", clo.FAMILIES_T)
    spread_r = dispersion(keep, "beta_T", clo.FAMILIES_T)
    # A column slip here, reading beta_T_as_deposited for the repaired arm,
    # restores the cohort mismatch this function was rewritten to remove and
    # changes every MAE/dev printed. It is caught by requiring the two to
    # differ.
    shadow = dispersion(keep, "beta_T_as_deposited", clo.FAMILIES_T)
    if all(abs(spread_r[k][0] - shadow[k][0]) < 1e-12 for k in spread_r):
        raise SystemExit("the repaired spread is the deposited spread")

    print("\n" + "=" * 78)
    print("deposited cohort against repaired cohort")
    print("=" * 78)

    print("\nblocker 1, temperature-axis leave-one-compound-out\n")
    print("   %-22s %6s %6s %8s %8s %6s %6s %8s %8s"
          % ("family", "n dep", "n rep", "MAE dep", "MAE rep", "c dep",
             "c rep", "MAE/dev", "  (rep)"))
    for name in clo.FAMILIES_T:
        d, r = dep["temperature"].get(name), rep["temperature"].get(name)
        sd, sr = spread_d.get(name), spread_r.get(name)
        print("   %-22s %6d %6d %8.4f %8.4f %6d %6d %8.2f %8.2f"
              % (name, sd[1], sr[1], d[0], r[0], sd[2], sr[2],
                 d[0] / sd[0], r[0] / sr[0]))
    print("\n   %-22s %10s %10s   %s"
          % ("family", "dev dep", "dev rep", "resamples below 1.0"))
    for name in clo.FAMILIES_T:
        d, r = dep["temperature"][name], rep["temperature"][name]
        fd, pd_ = pooled_fraction(d[3])
        fr, pr_ = pooled_fraction(r[3])
        print("   %-22s %10.3f %10.3f   %.0f%% -> %.0f%%"
              % (name, spread_d[name][0], spread_r[name][0],
                 100 * fd, 100 * fr))
        print("      deposited strata  %s" % pd_)
        print("      repaired strata   %s" % pr_)
    print("\n   dev is the mean absolute deviation of the family's exponents "
          "from their own median.")
    print("   It is the error of predicting every fit by that median with "
          "nothing held out, and the")
    print("   median is the constant that minimises it, so MAE/dev is an "
          "out-of-sample error over")
    print("   an in-sample optimum and is at least 1 for any data. Its level "
          "says nothing; only the")
    print("   change between the two arms does, and it falls in two families "
          "of three.")
    print("   The resample fraction counts resamples whose error falls below "
          "a fixed 1.0. That is an")
    print("   absolute bar on a scale the repairs compress, and dev crossing "
          "1.0 is most of what")
    print("   moves it: iron_pnictide_1111 goes from dev 1.456 to 0.438 and "
          "from 21 to 100 percent.")
    print("   It is not the whole story. iron_pnictide_122 sits below 1.0 in "
          "both arms and still")
    print("   moves from 30 to 98 percent, so the bar is not simply reporting "
          "which side of 1.0 the")
    print("   family sits on, and MAE/dev falls in both moving families, "
          "which compression alone")
    print("   would not produce.")
    inband = sorted(set(keep.substructure.dropna()) - set(clo.FAMILIES_T))
    if inband:
        n = int(keep.substructure.isin(inband).sum())
        nd = int(dep_a.substructure.isin(inband).sum())
        print("   %d of the 260 deposited fits and %d of the %d repaired ones "
              "are in families this" % (nd, n, len(keep)))
        print("   table does not cover (%s). That is a property of "
              "compound_leave_one_out's" % ", ".join(inband))
        print("   family list, not of the repair.")

    print("\nblocker 4, per-paper leave-one-out on the field exponent\n")
    print("   %-34s %5s %8s %18s %18s"
          % ("predictor", "fits", "MAE", "residual resample",
             "paper resample"))
    for label, cond, a, b in [
            ("Stage 2, deposited", True, pp_d, f_d),
            ("Stage 2, repaired", True, pp_r, f_r),
            ("pooled median, deposited", False, pp_pd, f_d),
            ("pooled median, repaired", False, pp_pr, f_r)]:
        cb = cluster_bootstrap(b, SEED, conditioned=cond)
        if abs(cb[0] - a[0]) > 1e-9 or cb[3] != a[3]:
            raise SystemExit("%s: the paper resample scores a different "
                             "residual set (%.6f over %d against %.6f over "
                             "%d)" % (label, cb[0], cb[3], a[0], a[3]))
        cells = stage2_cells(b) if cond else None
        if cells is not None and sum(cells.values()) != a[3]:
            raise SystemExit("%s: the cell table totals %d, the predictor "
                             "scores %d" % (label, sum(cells.values()), a[3]))
        print("   %-34s %5d %8.4f   [%.3f, %.3f]   [%.3f, %.3f]  %2d papers"
              % (label, a[3], a[0], a[1], a[2], cb[1], cb[2], cb[4]))
    print("\n   cohorts: %d papers deposited, %d repaired. The papers column "
          "above is the number of" % (pp_d[4], pp_r[4]))
    print("   papers each row's resample actually draws from, which is "
          "smaller wherever Stage 2")
    print("   cannot score a paper at all.")
    print("   Read the paper resample. The residual resample treats several "
          "readings of one figure")
    print("   as independent observations and is too narrow, most sharply in "
          "the repaired Stage 2")
    print("   arm, where 19 residuals come from 6 papers. Neither version "
          "carries the uncertainty")
    print("   in the training median, whose pools go down to a single fit, so "
          "both are floors on")
    print("   the width rather than the width.")
    for label, f in [("deposited", f_d), ("repaired", f_r)]:
        cells = stage2_cells(f)
        tot = sum(cells.values())
        print("\n   Stage 2 scorable cells, %s (%d of %d fits)"
              % (label, tot, len(f)))
        for (sub, form), n in cells.most_common():
            print("      %-24s %-16s %3d" % (sub, form, n))
    print("\n   The deposited Stage 2 cohort is majority iron-based; the "
          "repaired one is majority")
    print("   MgB2. The two MAEs are the errors of different material "
          "classes, not the same")
    print("   statistic on a smaller cohort.")

    print("\n   field-axis leave-one-compound-out by family\n")
    print("   %-22s %6s %6s %6s %6s %10s %10s"
          % ("family", "n dep", "n rep", "c dep", "c rep", "MAE dep",
             "MAE rep"))
    for name in clo.FAMILIES_H:
        d, r = dep["field"].get(name), rep["field"].get(name)
        if d is None and r is None:
            continue
        print("   %-22s %6s %6s %6s %6s %10s %10s"
              % (name, d[3] if d else 0, r[3] if r else 0,
                 d[2] if d else 0, r[2] if r else 0,
                 "%.4f" % d[0] if d else "absent",
                 "%.4f" % r[0] if r else "absent"))

    rows = []
    for name in clo.FAMILIES_T:
        d, r = dep["temperature"][name], rep["temperature"][name]
        rows.append(dict(axis="T", statistic="leave_one_compound_out",
                         label=name, n_dep=spread_d[name][1],
                         n_rep=spread_r[name][1], value_dep=d[0],
                         value_rep=r[0], dev_dep=spread_d[name][0],
                         dev_rep=spread_r[name][0],
                         compounds_dep=spread_d[name][2],
                         compounds_rep=spread_r[name][2],
                         frac_dep=pooled_fraction(d[3])[0],
                         frac_rep=pooled_fraction(r[3])[0]))
    for name in clo.FAMILIES_H:
        d, r = dep["field"].get(name), rep["field"].get(name)
        rows.append(dict(axis="H", statistic="leave_one_compound_out",
                         label=name, n_dep=d[3] if d else 0,
                         n_rep=r[3] if r else 0,
                         value_dep=d[0] if d else np.nan,
                         value_rep=r[0] if r else np.nan,
                         compounds_dep=d[2] if d else 0,
                         compounds_rep=r[2] if r else 0))
    for label, a, b_ in [("per_paper_stage2", pp_d, pp_r),
                         ("per_paper_pooled", pp_pd, pp_pr)]:
        rows.append(dict(axis="H", statistic=label, label=label,
                         n_dep=a[3], n_rep=b_[3], value_dep=a[0],
                         value_rep=b_[0], ci_lo_dep=a[1], ci_hi_dep=a[2],
                         ci_lo_rep=b_[1], ci_hi_rep=b_[2]))
    if sc:
        for label, matched, med, ratios in sc:
            rows.append(dict(axis="H", statistic="scale_ratio", label=label,
                             n_rep=len(ratios), value_rep=med,
                             above_0_9_rep=sum(1 for x in ratios if x > 0.9)))
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("\n   written to %s" % OUT)
    print("\nblocker 5 is recomputed by "
          "analysis/rerun_closed_form_without_withdrawn.py.")


if __name__ == "__main__":
    main()
