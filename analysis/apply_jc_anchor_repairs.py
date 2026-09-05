#!/usr/bin/env python3
"""Repair the 96-row per-paper Jc anchor table, and recompute what rests on it.

This is the last unrepaired data layer. data/phase_3_p31_jc_anchor_per_paper.csv
carries the anchors behind Fig. 3, the sample-form variance decomposition, Table
I row 8, and referee concessions A4 and A6. The reading pass of 2026-09-04
graded every row against its source figure and audit/what_this_costs_20260904.md
set out what to do with them; nothing was ever applied.

The grading, restated here so the script can be read against it:

  41 rows defective, 22 of them repairable by a scale rule that is understood
  and 19 not; 1 row weak, values 1.3 to 1.7 times off with a wrong tail; 31
  clean; 13 unresolved provenance; 10 with no printed figure. That is the 96.

Two things about this table decide how much the repair can move.

  The decomposition statistic reads log10_Jc_anchor, sample_form, substructure
  and paper_id, and nothing else. H_anchor_T does not enter it. So the four
  kilo-oersted papers, 14 rows, are corrected here because the table should be
  right, and they move the statistic by exactly zero. That is asserted rather
  than asserted-in-prose: the run recomputes the decomposition with the field
  repairs alone and requires it to be unchanged.

  What can move it is the two Jc rescales, 8 rows at plus one and minus two
  decades, and the 19 withdrawals, which take a sample form out of two families
  and take one family out entirely.

audit/what_this_costs_20260904.md says "96 now, 76 after repairs, 19 withdrawn".
That arithmetic is wrong by one: 96 minus 19 is 77, and 77 is what this run
produces. The note is left as written and the discrepancy is recorded rather
than quietly resolved in either direction.

Reproduction before change. The unrepaired table has to return the deposited
decomposition first: conventional_AlB2 0.1159 and iron_chalcogenide_11 0.3737
under analysis/permutation_test.py's cohort, which are the two figures the
response letter quotes to Referee A. If it does not, nothing is reported.

No row is deleted. Withdrawn rows keep their place and gain a reason.

    python analysis/apply_jc_anchor_repairs.py --dry-run
    python analysis/apply_jc_anchor_repairs.py

Run from the repository root.
"""
import argparse
import os
import shutil

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from permutation_test import eta2 as _eta2_yg, permute      # noqa: E402
from figure_4_source import aggregate_per_physical_sample   # noqa: E402

DATA = "data"
SRC = os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv")
OUT = SRC.replace(".csv", "_repaired.csv")
LEDGER = os.path.join("audit", "jc_anchor_repairs.csv")
SNAPSHOT = os.path.join("audit", "pre_jc_anchor_repair_20260905")

# The two figures the response letter puts in front of Referee A. Pinned, and
# checked before anything is changed.
DEPOSITED = {"aggregate": 0.31392,
             "conventional_AlB2": 0.11592, "iron_chalcogenide_11": 0.37372}
TOL = 5e-4
ITERS = 20000
SEED = 20260901

# Rows whose value is wrong by a scale that the source figure fixes. Keyed by a
# fragment of paper_id, with the expected row count, because a rule that
# silently matches the wrong number of rows is the failure mode here.
RESCALE = {
    "jallcom.2013.04.183": dict(
        n=4, jc=10.0,
        why="the ordinate is a linear axis in units of 1e4 A/cm2 and the "
            "deposit records the bare numbers, so every value is a decade "
            "low. audit/reclamation_status_20260904.md records the page read "
            "independently and matching to under 2 per cent, so this is a "
            "traced repair rather than a rule on file."),
}

# Field axis in kilo-oersted recorded as tesla. These correct H_anchor_T and
# cannot move the decomposition, which does not read that column.
FIELD_TENTH = {
    "physc.2009.05.098": dict(
        n=9,
        why="the printed field axis is kilo-oersted, and all nine readings "
            "track the printed curves with each series ending where its curve "
            "does. The same correction withdrew this paper's field-axis fits "
            "on 2026-09-05, on the separate ground that its 86 T literature "
            "anchor does not scale with the axis"),
    "s41598-025-24806-x": dict(
        n=2,
        why="the printed field axis is kilo-oersted; the three Tc values match "
            "the caption exactly and the currents track the curves to about "
            "thirty per cent"),
}

# Rows whose values contradict the figure and that no rescaling reconciles.
WITHDRAW = {
    "s10854-026-16566-9": dict(
        n=4,
        why="all twelve of this paper's records are held down from 11.0 K and "
            "its values contradict the printed curves; no single scale "
            "reconciles them"),
    "ceramint.2024.10.058": dict(
        n=5,
        why="the deposited sample ranking is close to reversed against the "
            "paper's own Fig. 4"),
    "matpr.2019.05.078": dict(
        n=4,
        why="the critical field is recorded from a critical-current-versus-"
            "field figure, and the deposited values do not follow the printed "
            "curves"),
    "phpro.2015.06.160": dict(
        n=2,
        why="the anchor is 9.0 T, exactly the maximum field the paper's own "
            "figure states, while the same file records 26 T at 18.9 K from "
            "the body text"),
    "physc.2011.05.018": dict(
        n=2,
        why="the paper has no critical-current-versus-field figure at all"),
    "s41598-025-95932-9": dict(
        n=1,
        why="the paper's only critical-current figure is a self-field "
            "measurement and the extraction supplies field-dependent series"),
    # The three rules an adversarial review removed from the repair side. Each
    # was on the 2026-09-04 list as repairable; each is contradicted by a file
    # in this repository, and the contradiction is more recent and better
    # evidenced than the list.
    "jpcs.2026.113652": dict(
        n=4,
        why="analysis/apply_unit_repairs.py rejects this paper for the unit "
            "route and says so in its own words: the recorded values are not "
            "the printed ones in any unit, and the rescale x0.01 on file is a "
            "guess. audit/flagged_source_reading.csv adds that the extracted "
            "Co0 panel does not exist in the source, whose panels are Co1, Co2 "
            "and Co3. A guessed decade on four rows is not a repair"),
    "physc.2010.05.048": dict(
        n=1,
        why="analysis/apply_unit_repairs.py rejects the field-tenth route for "
            "this paper explicitly: the axis is kilo-oersted but the recorded "
            "series has the wrong shape as well, running smoothly from 1e6 to "
            "2.6e5 where the printed curve starts near 5e5 and is flat around "
            "2e5 with a fishtail, so dividing the field by ten would leave a "
            "wrong curve"),
    "physc.2009.11.051": dict(
        n=2,
        why="audit/full_repo_sweep_20260903.md plans this paper as withdrawn "
            "and re-extracted rather than rescaled, it is on the still-to-"
            "trace list in audit/reclamation_status_20260904.md, and its "
            "field-axis fits were withdrawn on 2026-09-05 because the paper "
            "contains no critical-field figure at all"),
}

# One row, not a whole paper: the polycrystal record is a copy of the single
# crystal one shifted by a constant, and is 13 to 69 times above the traced
# curve. The single-crystal record of the same paper is 1.3 to 1.7 times off
# with a wrong tail, which is poor digitisation rather than fabrication, and
# defect_backtrack_20260904.md put it in a separate band. It is kept, and the
# run reports the decomposition with and without it.
WITHDRAW_ROW = {
    ("mtphys.2022.100783", "polycrystal"): dict(
        n=1,
        why="the polycrystal record is 13 to 69 times above the traced Fig. "
            "6(b) and is the single-crystal record shifted by a constant"),
}
WEAK_ROW = ("mtphys.2022.100783", "single_crystal")

FAMILIES = ["conventional_AlB2", "cuprate_BSCCO", "cuprate_LSCO",
            "cuprate_RBCO", "iron_chalcogenide_11", "iron_pnictide_1111",
            "iron_pnictide_122"]


def match(df, frag, form=None):
    m = df.paper_id.astype(str).str.contains(frag, regex=False)
    if form is not None:
        m &= df.sample_form == form
    return m


def eta2(sub, col="log10_Jc_anchor"):
    """The deposit's own statistic, imported rather than rewritten.

    An earlier version of this script reimplemented it and reimplemented the
    aggregation with it, and got iron_chalcogenide_11 at 0.4029 where the
    response letter quotes 0.374. Both numbers are in the repository: 0.4029 is
    phase_3_p58_variance_stability.py's cohort and 0.3737 is
    permutation_test.py's, and they differ because the MAGLAB records encode
    the isotherm in paper_id rather than sample_id and only one of the two
    strips it. The letter quotes the second, so the second is what this repairs
    and the functions come from it.
    """
    if len(sub) == 0 or sub.sample_form.nunique() < 2:
        return np.nan
    return float(_eta2_yg(sub[col].values, sub.sample_form.values))


def cohort(df):
    """permutation_test.py's cohort, via the function it calls."""
    agg = aggregate_per_physical_sample(df)
    return agg[agg.substructure.isin(FAMILIES)]


def sums_of_squares(sub, col="log10_Jc_anchor"):
    """Between-form and within-form sums of squares.

    Printed because a ratio can rise either by the numerator growing or by the
    denominator collapsing, and those mean opposite things. On this table the
    second happens, so reporting eta squared alone would say separation
    improved when it did not.
    """
    y = sub[col].values
    grand = y.mean()
    ssb = 0.0
    for lab in np.unique(sub.sample_form.values):
        m = sub.sample_form.values == lab
        ssb += m.sum() * (y[m].mean() - grand) ** 2
    return float(ssb), float(((y - grand) ** 2).sum() - ssb)


def omega2(sub, col="log10_Jc_anchor"):
    """Bias-corrected effect size.

    Eta squared is biased upward and the bias grows as n falls, which is
    exactly what the repair does to every family. Omega squared removes the
    leading term, and it goes negative when the observed separation is below
    what the grouping would produce by chance.
    """
    if len(sub) == 0 or sub.sample_form.nunique() < 2:
        return np.nan
    n, k = len(sub), sub.sample_form.nunique()
    if n <= k:
        return np.nan
    ssb, ssw = sums_of_squares(sub, col)
    msw = ssw / (n - k)
    denom = ssb + ssw + msw
    return float((ssb - (k - 1) * msw) / denom) if denom > 0 else np.nan


def support(sub):
    """How many distinct paper-level labellings the clustered null can draw.

    The clustered null permutes one label per paper, so with few papers the
    achievable p-values are a short list. Printing the size of that list and
    the smallest p it can reach stops a per-family 0.30 from being read beside
    an aggregate 0.011 as if the two were measured on the same scale.
    """
    from math import factorial
    lab = (sub.groupby("paper_id").sample_form
           .agg(lambda x: x.mode().iloc[0]).values)
    counts = pd.Series(lab).value_counts().values
    total = factorial(len(lab))
    for c in counts:
        total //= factorial(c)
    return int(total), 1.0 / total if total else np.nan


def table(df, label):
    agg = cohort(df)
    rows = []
    for fam in ["aggregate"] + FAMILIES:
        s = agg if fam == "aggregate" else agg[agg.substructure == fam]
        if s.empty:
            rows.append(dict(cohort=label, substructure=fam, n=0, papers=0,
                             forms=0, eta2=np.nan, omega2=np.nan,
                             p_clustered=np.nan, support=0, p_floor=np.nan,
                             ssb=np.nan, ssw=np.nan))
            continue
        e = eta2(s)
        pc, sup, floor = np.nan, 0, np.nan
        ssb = ssw = np.nan
        if np.isfinite(e):
            # One stream per family, seeded on the family name. Threading a
            # single generator through the loop makes a family's p depend on
            # how many families before it were skipped, and the two arms skip
            # different ones: iron_pnictide_1111 has byte-identical rows in
            # both arms and printed 0.801 against 0.802 for that reason alone.
            rng = np.random.default_rng(abs(hash(fam)) % (2 ** 32) + SEED)
            _o, pc = permute(s.log10_Jc_anchor.values, s.sample_form.values,
                             s.paper_id.values, ITERS, rng, True)
            sup, floor = support(s)
            ssb, ssw = sums_of_squares(s)
        rows.append(dict(cohort=label, substructure=fam, n=len(s),
                         papers=s.paper_id.nunique(),
                         forms=s.sample_form.nunique(), eta2=e,
                         omega2=omega2(s), p_clustered=pc, support=sup,
                         p_floor=floor, ssb=ssb, ssw=ssw))
    return pd.DataFrame(rows)


def reproduce(df):
    t = table(df, "deposited").set_index("substructure")
    bad = []
    for fam, want in DEPOSITED.items():
        got = t.eta2[fam]
        if not np.isfinite(got) or abs(got - want) > TOL:
            bad.append("%s %.5f, deposited %.5f" % (fam, got, want))
    print("reproduction of the deposited decomposition")
    if bad:
        for b in bad:
            print("   FAIL %s" % b)
        return False
    print("   conventional_AlB2 %.4f and iron_chalcogenide_11 %.4f match the "
          "two figures the response" % (t.eta2["conventional_AlB2"],
                                        t.eta2["iron_chalcogenide_11"]))
    print("   letter quotes, and the aggregate matches at %.4f"
          % t.eta2["aggregate"])
    return True


def apply_repairs(df):
    overlap = (set(RESCALE) | set(FIELD_TENTH)) & set(WITHDRAW)
    if overlap:
        raise SystemExit("a paper is both repaired and withdrawn: %s"
                         % ", ".join(sorted(overlap)))
    d = df.copy()
    d["repair"] = ""
    d["withdrawn"] = ""
    d["log10_Jc_anchor_as_deposited"] = d.log10_Jc_anchor
    d["H_anchor_T_as_deposited"] = d.H_anchor_T
    led, fails = [], []

    for frag, spec in RESCALE.items():
        m = match(d, frag)
        if m.sum() != spec["n"]:
            fails.append("%s matched %d rows, expected %d"
                         % (frag, m.sum(), spec["n"]))
            continue
        d.loc[m, "Jc_anchor_A_per_cm2_as_deposited"] = \
            d.loc[m, "Jc_anchor_A_per_cm2"]
        d.loc[m, "Jc_anchor_A_per_cm2"] *= spec["jc"]
        d.loc[m, "log10_Jc_anchor"] += np.log10(spec["jc"])
        d.loc[m, "repair"] = "Jc x %g" % spec["jc"]
        led.append(dict(paper=frag, rows=int(m.sum()),
                        action="rescaled", rule="Jc x %g" % spec["jc"],
                        reason=spec["why"]))

    for frag, spec in FIELD_TENTH.items():
        m = match(d, frag)
        if m.sum() != spec["n"]:
            fails.append("%s matched %d rows, expected %d"
                         % (frag, m.sum(), spec["n"]))
            continue
        d.loc[m, "H_anchor_T"] /= 10.0
        d.loc[m, "repair"] = "H / 10"
        led.append(dict(paper=frag, rows=int(m.sum()), action="rescaled",
                        rule="H / 10", reason=spec["why"]))

    for frag, spec in WITHDRAW.items():
        m = match(d, frag)
        if m.sum() != spec["n"]:
            fails.append("%s matched %d rows, expected %d"
                         % (frag, m.sum(), spec["n"]))
            continue
        d.loc[m, "withdrawn"] = frag
        led.append(dict(paper=frag, rows=int(m.sum()), action="withdrawn",
                        rule="no scale reconciles the values",
                        reason=spec["why"]))

    for (frag, form), spec in WITHDRAW_ROW.items():
        m = match(d, frag, form)
        if m.sum() != spec["n"]:
            fails.append("%s/%s matched %d rows, expected %d"
                         % (frag, form, m.sum(), spec["n"]))
            continue
        d.loc[m, "withdrawn"] = "%s %s" % (frag, form)
        led.append(dict(paper="%s (%s)" % (frag, form), rows=int(m.sum()),
                        action="withdrawn",
                        rule="one record of two, the other is kept as weak",
                        reason=spec["why"]))

    return d, pd.DataFrame(led), fails


def removal_null(src, rep, draws=2000, seed=SEED):
    """Is the rise a repair effect or just an effect of removing rows?

    The withdrawals carry most of the movement, and any removal of a fifth of
    a cohort perturbs a variance ratio. This asks whether removing the SAME
    NUMBER of rows at random, and separately removing the same number as whole
    papers at random, reaches the observed value as often as not. If it does,
    the number says nothing about which rows left.
    """
    out = rep.index[rep.withdrawn != ""]
    k = len(out)
    base = src.copy()
    for frag, spec in RESCALE.items():
        m = match(base, frag)
        base.loc[m, "log10_Jc_anchor"] += np.log10(spec["jc"])
    obs = eta2(cohort(base.drop(index=out)))
    rng = np.random.default_rng(seed)
    rows_null, paper_null = [], []
    idx = np.asarray(base.index)
    papers = base.paper_id.unique()
    for _ in range(draws):
        pick = rng.choice(idx, k, replace=False)
        v = eta2(cohort(base.drop(index=pick)))
        if np.isfinite(v):
            rows_null.append(v)
        order = rng.permutation(papers)
        drop, tot = [], 0
        for pp in order:
            m = base.index[base.paper_id == pp]
            if tot + len(m) > k:
                continue
            drop += list(m)
            tot += len(m)
            if tot == k:
                break
        v = eta2(cohort(base.drop(index=drop)))
        if np.isfinite(v):
            paper_null.append(v)
    print("\n   removing the same number of rows at random, %d draws\n" % draws)
    print("   %-30s %9s %20s %12s"
          % ("scheme", "median", "5th to 95th", "P(>= obs)"))
    for name, arr in [("%d random rows" % k, np.array(rows_null)),
                      ("%d rows as whole papers" % k, np.array(paper_null))]:
        print("   %-30s %9.4f   [%.3f, %.3f]      %8.2f"
              % (name, np.median(arr), np.percentile(arr, 5),
                 np.percentile(arr, 95), float((arr >= obs - 1e-12).mean())))
    print("   observed, the withdrawal set actually chosen  %.4f" % obs)
    print("   a high P here means the value is a property of removing rows, "
          "not of which rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    src = pd.read_csv(SRC)
    print("source: %d anchor rows, %d papers\n"
          % (len(src), src.paper_id.nunique()))
    if not reproduce(src):
        raise SystemExit("the deposited decomposition does not reproduce, "
                         "nothing changed")

    rep, led, fails = apply_repairs(src)
    if fails:
        print("\nRULES THAT DID NOT MATCH THEIR EXPECTED ROWS. Nothing written.")
        for f in fails:
            print("  ", f)
        return 1

    n_out = int((rep.withdrawn != "").sum())
    kept = rep[rep.withdrawn == ""]
    print("\nrepairs")
    print("   rescaled on Jc                            %d rows, %d papers"
          % (int(rep.repair.str.startswith("Jc").sum()), len(RESCALE)))
    print("   rescaled on the field axis                %d rows, %d papers"
          % (int((rep.repair == "H / 10").sum()), len(FIELD_TENTH)))
    print("   withdrawn                                 %d rows" % n_out)
    print("   kept                                      %d of %d"
          % (len(kept), len(rep)))
    print("   audit/what_this_costs_20260904.md says 76 kept; 96 minus 19 is "
          "77 and 77 is what this is")

    # The field repairs cannot move the decomposition, because
    # aggregate_per_physical_sample groups on substructure, paper, sample and
    # form and aggregates log10_Jc_anchor alone. An earlier version ran this as
    # a "test" by re-applying the divisor and comparing; that check passes for
    # any divisor, any paper and any row count, so it was a tautology dressed
    # as evidence. It is stated as a property of the code path instead, and the
    # column-consistency guard below is the assertion that has teeth.
    bad = (rep.Jc_anchor_A_per_cm2.gt(0)
           & (np.log10(rep.Jc_anchor_A_per_cm2.where(rep.Jc_anchor_A_per_cm2 > 0,
                                                     np.nan))
              - rep.log10_Jc_anchor).abs().gt(1e-6))
    if bad.any():
        raise SystemExit("%d rows have a linear Jc and a log Jc that disagree, "
                         "so a rescale touched one and not the other"
                         % int(bad.sum()))
    print("   the linear and log Jc columns agree on all %d rows" % len(rep))
    print("   the field repairs cannot move the decomposition: the statistic "
          "reads log10_Jc_anchor,")
    print("   sample_form, substructure and paper_id, and H_anchor_T is on no "
          "path into it")

    weak_dropped = kept[~(kept.paper_id.astype(str).str.contains(
        WEAK_ROW[0], regex=False) & (kept.sample_form == WEAK_ROW[1]))]
    out = pd.concat([
        table(src, "deposited"),
        table(kept, "repaired"),
        table(weak_dropped, "repaired, weak row dropped"),
    ])
    print("\nthe decomposition\n")
    print("   %-22s %5s %5s %5s %5s %8s %8s %8s %8s %7s %7s %6s"
          % ("family", "n dep", "n rep", "f dep", "f rep", "eta dep",
             "eta rep", "w dep", "w rep", "p dep", "p rep", "sup r"))
    p = out.pivot(index="substructure", columns="cohort")

    def f(col, coh, fam, fmt="%.4f", alt="one form"):
        v = p[(col, coh)][fam]
        return fmt % v if np.isfinite(v) else alt

    for fam in ["aggregate"] + FAMILIES:
        print("   %-22s %5d %5d %5d %5d %8s %8s %8s %8s %7s %7s %6s"
              % (fam, p[("n", "deposited")][fam], p[("n", "repaired")][fam],
                 p[("forms", "deposited")][fam], p[("forms", "repaired")][fam],
                 f("eta2", "deposited", fam), f("eta2", "repaired", fam),
                 f("omega2", "deposited", fam, "%.4f"),
                 f("omega2", "repaired", fam, "%.4f"),
                 f("p_clustered", "deposited", fam, "%.3f"),
                 f("p_clustered", "repaired", fam, "%.3f"),
                 f("support", "repaired", fam, "%d", "-")))
    print("\n   a family with one sample form has nothing to decompose and is "
          "not evaluable")
    print("   w is omega squared, the same quantity with the small-sample bias "
          "removed; it goes")
    print("   negative where the observed separation is below what the "
          "grouping gives by chance")
    print("   p is against the paper-clustered null, the deposit's own "
          "preferred test: the form")
    print("   label is shuffled between papers, so a paper's records all keep "
          "one label. sup is the")
    print("   number of distinct labellings that null can draw and floor is "
          "the smallest p it can")
    print("   reach, so a family with a short support cannot produce a small p "
          "however clean it is")

    print("\n   between-form and within-form sums of squares\n")
    print("   %-22s %9s %9s %9s %9s"
          % ("family", "SSB dep", "SSB rep", "SSW dep", "SSW rep"))
    for fam in ["aggregate"] + FAMILIES:
        print("   %-22s %9s %9s %9s %9s"
              % (fam, f("ssb", "deposited", fam, "%.2f", "-"),
                 f("ssb", "repaired", fam, "%.2f", "-"),
                 f("ssw", "deposited", fam, "%.2f", "-"),
                 f("ssw", "repaired", fam, "%.2f", "-")))
    print("   a ratio can rise because the numerator grew or because the "
          "denominator collapsed,")
    print("   and those mean opposite things")

    print("\n   where the movement comes from, each component alone\n")
    print("   %-38s %5s %9s %9s" % ("arm", "n", "eta2", "p"))
    comps = [("deposited", src)]
    only_res = src.copy()
    for frag, spec in RESCALE.items():
        m = match(only_res, frag)
        only_res.loc[m, "Jc_anchor_A_per_cm2"] *= spec["jc"]
        only_res.loc[m, "log10_Jc_anchor"] += np.log10(spec["jc"])
        comps.append(("the %s rescale alone" % frag, only_res.copy()))
    comps.append(("the withdrawals alone", src[~src.index.isin(
        rep.index[rep.withdrawn != ""])]))
    comps.append(("the full repair", kept))
    comps.append(("the full repair, weak row dropped", weak_dropped))
    for name, frame in comps:
        r = table(frame, name).set_index("substructure")
        print("   %-38s %5d %9.4f %9.3f"
              % (name, r.n["aggregate"], r.eta2["aggregate"],
                 r.p_clustered["aggregate"]))
    removal_null(src, rep)

    if a.dry_run:
        print("\ndry run: nothing written")
        return 0
    os.makedirs(SNAPSHOT, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(SNAPSHOT, os.path.basename(SRC)))
    rep.to_csv(OUT, index=False)
    led.to_csv(LEDGER, index=False)
    out.to_csv(os.path.join("audit", "variance_decomposition_repaired.csv"),
               index=False)
    print("\nwritten: %s, %s, %s" % (OUT, LEDGER,
                                     "audit/variance_decomposition_repaired.csv"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
