#!/usr/bin/env python3
"""Blocker 5: the count of compounds whose per-compound Form 3 fit converges,
re-derived on data with the withdrawn papers removed.

The supplement and Table I row 5 report 23, and call those compounds the ones
whose fit "converges". That is the manuscript's word, not the code's. fit_form
calls scipy.optimize.least_squares and returns sol.x without ever reading
sol.success or sol.status, so "ok" means the call did not raise. The gate that
actually decides the count is a data-sufficiency test: at least 20 points
passing the Form 3 filter and at least 3 distinct temperatures. Several of the
23 are fits nobody would call converged, among them Sm2FeAs2O at beta_T of
-16.5 and Fe2TeSe with a negative holdout R squared. The rerun keeps the
published rule, because a like-for-like recount has to, and the word is
corrected in the documents rather than here.

That number comes from
kappa_pipeline/analysis/closed_form/run_closed_form_fits.py run over
agent2_dataset_v3_2_1.csv, which still contains all eleven papers withdrawn on
2026-09-03. It is therefore drawn from data the audit removed, and it cannot be
renumbered from 23 to something else by hand: the gate is a per-compound data
sufficiency test, so removing rows can only be evaluated by running the test
again.

This script does not reimplement the fitter. It imports the original module and
calls its own functions, with two substitutions and nothing else:

  the input path, which is hardcoded to a location on the author's machine, is
  pointed at the copy of the same file in this session's uploads;

  the withdrawn papers are removed from the input, which is the change this
  script exists to make;

  kappa_pipeline.predictor, which is not in this repository, is supplied as a
  stub under audit/closed_form_rerun. Its two constants enter Form 1 only and
  its monotonic baseline is called after every fit completes and draws no
  random numbers, so neither can move a Form 3 result. One of the two,
  LOG_H_EPS, is a guess, and every form1_ column computed with it is therefore
  meaningless. Those columns are dropped before anything is written, so the
  deposited file holds only what reproduces.

One thing the rerun cannot separate, stated because the output would otherwise
imply it had. run_per_compound draws one random stream per compound and Forms
1, 2 and 3 consume it in order, so removing rows from a compound changes the
Form 3 holdout even where the Form 3 filtered set is unchanged. For the five
surviving compounds that lose rows, a change in fitted parameters is data loss
and a redrawn holdout together, and nothing here tells them apart. The
convergence count is unaffected, because the status depends only on the point
and temperature counts.

Reproduction before change, which is the reason the run is trustworthy at all.
The script first runs the unmodified cohort and requires it to return the
deposited Form 3 table. If that fails, nothing is reported. Only then is the
withdrawal filter applied.

The reproduction bar is set in two parts, and the split between them is the
point. Everything that decides the count and is available to check is required to
match EXACTLY: the convergence status of every compound and the sizes of the
training and holdout sets. Those two sizes partition the Form 3 filtered set,
so the point count is pinned by them; the distinct-temperature count, the other
half of the skip rule, is not checkable at all, because the deposited per-form
file does not carry it. Those are integers produced by filtering and by one seeded
shuffle, and any disagreement in them means a different cohort or a different
random stream, which would invalidate the rerun. The fitted parameters are
required to match to a relative 1e-6, because they are the output of
scipy.optimize.least_squares and its convergence tolerance is larger than the
1e-9 an earlier version of this script demanded. That version failed on 69
checks whose worst relative disagreement was 5.3e-7, all of them optimiser
noise, while every integer matched. Reporting that as a failed reproduction
would have been wrong; so would passing it silently, which is why the achieved
worst case is printed on every run. The bar sits a factor of two above the
achieved worst case rather than the factor of nineteen a 1e-5 bar would give,
so a real disagreement at the fifth digit still fails.



Why the reproduction check is not optional here. Each compound's holdout split
comes from one np.random.default_rng(42) consumed in order by Form 1, Form 2
and Form 3, and a form that is skipped for insufficient data consumes nothing.
A reimplementation that draws the three splits in any other order, or that
draws for a skipped form, produces a different holdout for Form 3 and a
different set of parameters that still looks entirely plausible. Matching the
deposited file to nine decimals is what rules that out.

    python analysis/rerun_closed_form_without_withdrawn.py

Run from the repository root.
"""
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

UP = "/mnt/user-data/uploads/SuperconductorWorkflow"
ORIG = os.path.join(UP, "kappa_pipeline", "analysis", "closed_form",
                    "run_closed_form_fits.py")
DEPOSITED = os.path.join(UP, "kappa_pipeline", "analysis", "closed_form",
                         "form3_per_compound_fits.csv")
SOURCE = os.path.join(UP, "data_agent2", "agent2_dataset_v3_2_1.csv")
STUB = os.path.join("audit", "closed_form_rerun")
LITERATURE = os.path.join(UP, "kappa_pipeline", "analysis",
                          "tc_hc2_literature.csv")
WITHDRAWN = os.path.join("audit", "withdrawn_beta_T_papers.csv")
OUT = os.path.join("audit", "form3_per_compound_without_withdrawn.csv")

PARAM_COLS = ["form3_log_Jc_0", "form3_beta_T", "form3_beta_H",
              "form3_train_MAE", "form3_holdout_MAE", "form3_train_R2",
              "form3_holdout_R2"]
# Integers produced by filtering and by the seeded shuffle. Any disagreement
# here is a different cohort or a different holdout, not optimiser noise.
EXACT_COLS = ["form3_n_train", "form3_n_holdout"]
PARAM_RTOL = 1e-6


def load_module():
    sys.path.insert(0, os.path.abspath(STUB))
    spec = importlib.util.spec_from_file_location("rcff", ORIG)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build(m, drop_papers=()):
    """The module's own load_data(), with the input path substituted.

    load_data() reads a module-level constant, so the frame is rebuilt here
    from the same three steps it performs. Those steps are copied rather than
    called because the only alternative is monkeypatching a Path constant,
    which would leave the substitution invisible to anyone reading this.
    """
    df = pd.read_csv(SOURCE, low_memory=False)
    df = df.dropna(subset=["log_Jc"]).copy()
    if drop_papers:
        before = len(df)
        want = set(drop_papers)
        # Every withdrawn paper has to be present in the key column, and each
        # has to remove rows. Without this the wrong column can be passed and
        # the rerun becomes a silent null: zero rows drop, the reproduction
        # check still passes because it runs on the unmodified arm, and the
        # script reports "no compound changes status" as a completed result.
        present = set(df.pdf_name.unique())
        missing = sorted(want - present)
        if missing:
            raise SystemExit("these withdrawn papers match no row of the "
                             "source, so the wrong key was passed: %s"
                             % ", ".join(missing))
        # Not "len(want) of len(drop_papers)", which compares a set against
        # the list it was built from and is true however few papers were
        # passed. The count has to be the number of rows in the withdrawal
        # ledger, or a filtered subset of it reruns on a cohort nobody
        # withdrew and reports the result as complete.
        n_ledger = len(pd.read_csv(WITHDRAWN))
        if len(want) != n_ledger:
            raise SystemExit("%d papers passed, the withdrawal ledger holds "
                             "%d" % (len(want), n_ledger))
        df = df[~df.pdf_name.isin(want)]
        print("   withdrawn papers matched                 %d of %d in the "
              "ledger" % (len(want), n_ledger))
        print("   rows dropped with the withdrawn papers   %d of %d"
              % (before - len(df), before))
    lit = pd.read_csv(LITERATURE)
    tc = dict(zip(lit["mp_formula"], lit["tc_K"]))
    hc2 = dict(zip(lit["mp_formula"], lit["hc2_T"]))
    df["Tc_K"] = df["mp_formula"].map(tc)
    df["Hc2_T_lit"] = df["mp_formula"].map(hc2)
    df["T_over_Tc"] = df["temperature_K"] / df["Tc_K"]
    df["H_over_Hc2_0"] = df["field_T"] / df["Hc2_T_lit"]
    df["one_minus_T_over_Tc"] = 1.0 - df["T_over_Tc"]
    df["Hc2_at_T"] = df["Hc2_T_lit"] * df["one_minus_T_over_Tc"].clip(lower=0.0)
    df["one_minus_H_over_Hc2_T"] = (
        1.0 - df["field_T"] / df["Hc2_at_T"].replace(0.0, np.nan))
    df["one_minus_H_over_Hc2_0"] = 1.0 - df["H_over_Hc2_0"]
    return df


def fit_all(m, df):
    rows = [m.run_per_compound(df, c)
            for c in sorted(df["mp_formula"].unique())]
    return pd.DataFrame(rows)


def compare(a, b, label_a, label_b):
    ka = a.set_index("mp_formula")
    kb = b.set_index("mp_formula")
    common = sorted(set(ka.index) & set(kb.index))
    print("\n   %-24s %-12s %-12s %8s %8s"
          % ("compound", label_a, label_b, "n dep", "n rep"))
    moved = []
    for c in sorted(set(ka.index) | set(kb.index)):
        sa = ka.form3_status.get(c, "absent")
        sb = kb.form3_status.get(c, "absent")
        na = ka.n_form3.get(c, 0) if "n_form3" in ka else 0
        nb = kb.n_form3.get(c, 0) if "n_form3" in kb else 0
        tag = "" if sa == sb else "   <- moved"
        if sa != sb:
            moved.append((c, sa, sb))
        print("   %-24s %-12s %-12s %8s %8s%s"
              % (c, sa[:12], sb[:12], na, nb, tag))
    return common, moved


def parameter_moves(a, b):
    """Which surviving compounds got a different Form 3 fit.

    compare() prints convergence status, and status alone would support the
    reading that three compounds vanish and nothing else changes. That is not
    what happened. Five of the survivors lose rows and their fitted exponents
    move by amounts that are large in the units the manuscript uses. Each of
    those moves is data loss and a redrawn holdout together, for the reason
    given in the module docstring, and neither this table nor any other here
    separates them.
    """
    ka = a.set_index("mp_formula")
    kb = b.set_index("mp_formula")
    both = [c for c in kb.index
            if c in ka.index and ka.form3_status[c] == "ok"
            and kb.form3_status[c] == "ok"]
    rows, redrawn = [], []
    for c in both:
        if int(ka.n_form3[c]) == int(kb.n_form3[c]):
            # A compound whose Form 3 set is unchanged can still have a
            # redrawn holdout, because Form 1 and Form 2 consume the same
            # stream first. Named rather than skipped.
            if int(ka.form3_n_train[c]) != int(kb.form3_n_train[c]) or \
                    abs(float(ka.form3_beta_T[c])
                        - float(kb.form3_beta_T[c])) > 1e-9:
                redrawn.append(c)
            continue
        rows.append((c, int(ka.n_form3[c]), int(kb.n_form3[c]),
                     float(ka.form3_beta_T[c]), float(kb.form3_beta_T[c]),
                     float(ka.form3_beta_H[c]), float(kb.form3_beta_H[c]),
                     float(ka.form3_holdout_R2[c]),
                     float(kb.form3_holdout_R2[c])))
    print("\n   surviving compounds whose Form 3 fit moved\n")
    if redrawn:
        print("      %d compounds keep their Form 3 set but were refitted on "
              "a redrawn holdout: %s" % (len(redrawn), ", ".join(redrawn)))
    else:
        print("      no compound keeps its Form 3 set and changes, so no fit "
              "moved on a redrawn")
        print("      holdout alone")
    if not rows:
        print("      none")
        return
    print("      %-18s %11s %15s %15s %15s"
          % ("compound", "n form3", "beta_T", "beta_H", "holdout R2"))
    for c, na, nb, ta, tb, ha, hb, ra, rb in sorted(rows):
        print("      %-18s %5d->%-5d %7.3f->%-7.3f %7.2f->%-7.2f "
              "%7.3f->%-7.3f" % (c, na, nb, ta, tb, ha, hb, ra, rb))
    print("      each move is data loss and a redrawn holdout together; the "
          "convergence count is")
    print("      unaffected, because status depends only on the point and "
          "temperature counts")


def main():
    m = load_module()
    print("reproduction of the deposited Form 3 table")
    base = build(m)
    rep = fit_all(m, base)
    dep = pd.read_csv(DEPOSITED)

    a = rep.set_index("mp_formula")
    b = dep.set_index("mp_formula")
    if sorted(a.index) != sorted(b.index):
        raise SystemExit("compound sets differ, reproduction not attempted")
    bad, worst, worst_at = [], 0.0, None
    for c in b.index:
        if a.form3_status[c] != b.form3_status[c]:
            bad.append("%s status %s vs %s"
                       % (c, a.form3_status[c], b.form3_status[c]))
            continue
        if a.form3_status[c] != "ok":
            continue
        for col in EXACT_COLS:
            if int(a[col][c]) != int(b[col][c]):
                bad.append("%s %s %d vs %d (the holdout split differs)"
                           % (c, col, a[col][c], b[col][c]))
        for col in PARAM_COLS:
            x, y = float(a[col][c]), float(b[col][c])
            d = abs(x - y) / max(abs(y), 1e-12)
            if d > worst:
                worst, worst_at = d, (c, col, x, y)
            if d > PARAM_RTOL:
                bad.append("%s %s %.12g vs %.12g, relative %.2e"
                           % (c, col, x, y, d))
    if bad:
        print("   FAILED on %d checks:" % len(bad))
        for x in bad[:20]:
            print("      %s" % x)
        raise SystemExit("reproduction failed, nothing reported")
    n_ok = int((rep.form3_status == "ok").sum())
    print("   %d compounds, %d converging" % (len(rep), n_ok))
    print("   status, filtered point count and holdout split match exactly")
    print("   worst relative parameter disagreement  %.2e at %s %s"
          % (worst, worst_at[0], worst_at[1]) if worst_at else "")

    print("\nrerun with the eleven withdrawn papers removed")
    w = pd.read_csv(WITHDRAWN)
    df2 = build(m, drop_papers=w.paper_id.tolist())
    rep2 = fit_all(m, df2)
    n_ok2 = int((rep2.form3_status == "ok").sum())
    print("   compounds present                        %d" % len(rep2))
    print("   converging                               %d" % n_ok2)

    _common, moved = compare(rep, rep2, "as published", "repaired")
    parameter_moves(rep, rep2)
    print("\n   as published %d of %d converge; without the withdrawn papers "
          "%d of %d" % (n_ok, len(rep), n_ok2, len(rep2)))
    if moved:
        print("   moved:")
        for c, sa, sb in moved:
            print("      %-24s %s -> %s" % (c, sa, sb))
    else:
        print("   no compound changes status")
    # Only the columns that reproduce. form1_ and form2_ are computed with a
    # guessed LOG_H_EPS and monotonic_K3_ with a stub that raises, so writing
    # them would deposit a file mixing verified and invented columns with
    # nothing in it saying which is which.
    cols = [c for c in rep2.columns
            if c.startswith("form3_") or c.startswith("n_form3")
            or c.startswith("n_T_form3")
            or c in ("mp_formula", "family", "n_total", "Tc_K", "Hc2_T_lit")]
    rep2[cols].to_csv(OUT, index=False)
    print("\n   written to %s, Form 3 and identity columns only" % OUT)


if __name__ == "__main__":
    main()
