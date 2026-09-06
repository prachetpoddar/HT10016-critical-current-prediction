"""
functional_form_comparison.py

Table II, regenerated with a holdout the paper does not disown, and with the
three forms scored on identical rows.

Why this exists. Table II selects Form 3 for the whole paper, and four things
about it were wrong.

  * Its generator is not in the deposit. The fitter and its input dataset both
    live outside this repository, so nothing here could reproduce the table.
    Both are now deposited: data/functional_form_input.csv is the fitter's
    input reduced to the columns it reads, value-for-value identical to the
    original in the same row order, and
    data/form3_per_compound_fits_as_published.csv is the original's own
    per-compound output, which this module reproduces to 1e-6 before it
    reports anything.

  * Its holdout is drawn point by point inside a compound, so every held-out
    point sits on a curve whose other points trained the model. Sec. II.B
    rejects that pooling in writing.

  * Its caption says "identical splits across forms". The original draws one
    default_rng(42) per compound and consumes it inside the form loop, so each
    form gets a different permutation. No compound has identical Form 1 and
    Form 3 holdouts and every overlap sits at the chance rate.

  * Because the three forms also filter to different frames, they are scored
    on different rows and on different numbers of compounds. Form 2 is scored
    on 22 compounds against 23 for the other two, and the compound it loses is
    the one with the smallest Form 3 error in the cohort. Half the published
    Form 2 to Form 3 margin is that, not functional form.

What the module does about the last point, which an independent review had to
force. Every construction other than the reproduction runs on the COMMON
FRAME: the rows that pass all three forms' filters. One split is drawn on that
frame and all three forms train and test on exactly the same rows, so a
difference between two numbers in a row of the output is a difference between
two functional forms and nothing else. The forms are scoreable together or not
at all, so no row of the table averages over a ragged set of compounds.

The three constructions, each changing one thing:

  point   a shared 80/20 point split. Isolates the caption's false claim from
          the granularity of the split.
  curve   whole isotherms held out, keyed (pdf_name, compound_raw,
          temperature_K). Keying on the page instead, as an earlier version
          did, is wrong twice: fifty groups mix several samples measured at
          one temperature, and twenty-five isotherms span two pages, so half
          of a held-out curve stays in training. This is the same defect the
          repository already recorded for a (paper, temperature) key.
  paper   whole source papers held out.

Bounds on the fit. The original calls least_squares unbounded, and on a
training set whose field column is degenerate the field exponent is not
identifiable: for HfRe2 the published Table II fit carries a field exponent of
2.9e6 on a column spanning 1e-5 T, and under a paper-level holdout Pr2FeAs2O
returns exponents of 1e5 and predictions of -9426 dex. That is a rank
deficiency, not a result. Exponents are bounded here to +/- 50, which no
physical fit approaches, and every fit that reaches a bound is counted and
printed rather than averaged in silently.

Usage:
    python3 analysis/functional_form_comparison.py

Writes audit/functional_form_comparison.csv.
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

IN = os.path.join("data", "functional_form_input.csv")
REF = os.path.join("data", "form3_per_compound_fits_as_published.csv")
WITHDRAWN = os.path.join("audit", "withdrawn_beta_T_papers.csv")
OUT = os.path.join("audit", "functional_form_comparison.csv")

ALPHA_FIXED = 0.047
# Recovered, not guessed: the value at which Form 1 returns the published
# median 0.597 and mean 0.672 together. The repository's earlier stub guessed
# 1e-3 and returned 0.603, which is why an earlier pass called Form 1
# unreproducible. Enters Form 1 only.
LOG_H_EPS = 1e-6
RNG_SEED = 42
HOLDOUT_FRAC = 0.20
T_MAX_FRAC = 0.95
HC2_MAX_FRAC = 0.95
FORMS = ("form1", "form2", "form3")

MIN_PTS = 20            # the original's skip rule
MIN_DISTINCT_T = 3      # the original's skip rule
MIN_HOLDOUT = 5         # a two-point average must not weigh as much as MgB2
EXP_BOUND = 50.0        # no physical exponent is near this
N_WITHDRAWN = 11
N_WITHDRAWN_ROWS = 997
# The eighteen sources opened and compared against their printed figures in
# audit/cohortA_all_eighteen_read_20260904.md, every one of which was found
# defective. None of them is in the withdrawal ledger: the project's answer to
# them was reextraction, not withdrawal, and fourteen carry a repaired point
# file under data/reextraction. Table II's input predates all of that, so it
# holds all eighteen in the form the screen rejected, and the withdrawal filter
# removes eleven different papers. The comparison is therefore also run with
# these removed.
SCREEN_FAILED = (
    "0806.2839v1", "0903.0004v2", "0906.0444v1", "0907.0147v2",
    "1002.0208v2", "1009.4896v1", "1104.0477v2", "1108.0407v1",
    "1111.3923v1", "1502.05345v1", "1611.08455v1", "1903.00866v2",
    "2012.13723v3", "2207.06629v1", "2305.10034v1", "2308.10492v1",
    "2510.10264v1", "2511.19058v1")
MIN_GUARD_COMPOUNDS = 8
SEEDS = tuple(range(42, 62))

PUBLISHED = {"form1": 0.597, "form2": 0.352, "form3": 0.260}
PUBLISHED_MEAN = {"form1": 0.672, "form2": 0.578, "form3": 0.519}


# ------------------------------------------------------------------ the data
def load(path=IN):
    d = pd.read_csv(path)
    d["T_over_Tc"] = d.temperature_K / d.Tc_K
    d["H_over_Hc2_0"] = d.field_T / d.Hc2_T_lit
    omt = 1.0 - d.T_over_Tc
    d["Hc2_at_T"] = d.Hc2_T_lit * omt.clip(lower=0.0)
    d["one_minus_H_over_Hc2_T"] = 1.0 - d.field_T / d.Hc2_at_T.replace(0.0,
                                                                      np.nan)
    d["one_minus_H_over_Hc2_0"] = 1.0 - d.H_over_Hc2_0
    return d


def filter_per_form(df, form):
    base = df[(df.T_over_Tc < T_MAX_FRAC) & (df.field_T >= 0.0)]
    if form == "form1":
        return base
    if form == "form2":
        return base[(base.one_minus_H_over_Hc2_T > 1.0 - HC2_MAX_FRAC)
                    & base.one_minus_H_over_Hc2_T.notna()]
    return base[base.one_minus_H_over_Hc2_0 > 1.0 - HC2_MAX_FRAC]


def common_frame(cd):
    """The rows every form keeps. The only frame the comparison is run on."""
    idx = filter_per_form(cd, "form1").index
    for form in ("form2", "form3"):
        idx = idx.intersection(filter_per_form(cd, form).index)
    return cd.loc[idx]


# ------------------------------------------------------------- the three forms
def predict(form, p, d):
    omt = np.clip(1.0 - d.T_over_Tc.values, 1e-6, None)
    if form == "form1":
        a, b = p
        return a + b * np.log10(omt) - ALPHA_FIXED * np.log10(
            np.maximum(d.field_T.values, LOG_H_EPS))
    if form == "form2":
        a, b, g = p
        arg = np.clip(1.0 - d.field_T.values
                      / np.clip(d.Hc2_at_T.values, 1e-6, None), 1e-6, None)
        return a + b * np.log10(omt) + g * np.log10(arg)
    a, b, g = p
    omh = np.clip(1.0 - d.H_over_Hc2_0.values, 1e-6, None)
    return a + b * np.log10(omt) + g * np.log10(omh)


def fit(form, tr, bounded):
    y = tr.log_Jc.values
    p0 = ([float(np.median(y)), 1.5] if form == "form1"
          else [float(np.median(y)), 1.5, 1.0])
    kw = {}
    if bounded:
        n = len(p0)
        kw["bounds"] = ([-1e3] + [-EXP_BOUND] * (n - 1),
                        [1e3] + [EXP_BOUND] * (n - 1))
    sol = least_squares(lambda p: predict(form, p, tr) - y, p0,
                        method="trf", **kw)
    hit = bool(bounded and np.any(np.abs(sol.x[1:]) >= EXP_BOUND - 1e-6))
    return sol.x, hit


def score(form, tr, ho, bounded=True):
    p, hit = fit(form, tr, bounded)
    mae = float(np.mean(np.abs(ho.log_Jc.values - predict(form, p, ho))))
    return mae, hit, p


# ----------------------------------------------------------------- the splits
def curve_key(d):
    """One isotherm of one sample from one source. Not the page."""
    return (d.pdf_name.astype(str) + "|" + d.compound_raw.astype(str)
            + "|" + d.temperature_K.astype(str))


KEYFN = {"point": lambda d: pd.Series(d.index, index=d.index),
         "curve": curve_key,
         "paper": lambda d: d.pdf_name.astype(str)}


def choose_held(keys, rng):
    k = np.array(sorted(set(keys)))
    if len(k) < 2:
        return None
    n_out = min(max(1, int(round(HOLDOUT_FRAC * len(k)))), len(k) - 1)
    return set(k[rng.permutation(len(k))[:n_out]])


def usable(tr, ho):
    return (len(ho) >= MIN_HOLDOUT and len(tr) >= MIN_PTS
            and tr.temperature_K.nunique() >= MIN_DISTINCT_T)


def run_common(cd, mode, bounded=True, seed=RNG_SEED):
    """One compound, one construction, on the common frame.

    All three forms get the identical training and holdout rows, so the row
    this returns is a comparison between functional forms and nothing else.
    Returns None when the compound cannot be scored, which is a property of
    the compound and not of any one form.
    """
    f = common_frame(cd)
    if len(f) < MIN_PTS or f.temperature_K.nunique() < MIN_DISTINCT_T:
        return None
    rng = np.random.default_rng(seed)
    keys = KEYFN[mode](f)
    held = choose_held(keys, rng)
    if held is None:
        return None
    m = keys.isin(held)
    tr, ho = f[~m], f[m]
    if not usable(tr, ho):
        return None
    out = {"n_train": len(tr), "n_holdout": len(ho)}
    for form in FORMS:
        # The rows are chosen once, above, and handed to all three forms
        # unchanged. run_common records them so a guard can check that on the
        # path the table actually uses, rather than on a re-derivation: an
        # earlier guard asserted an identity that was algebraically true for
        # any input, and a mutation that redrew the split per form passed it
        # and moved every number in the output.
        mae, hit, _ = score(form, tr, ho, bounded)
        out[form] = mae
        out[form + "_bound_hit"] = hit
        out[form + "_rows"] = (tuple(tr.index), tuple(ho.index))
    return out


def run_published(cd):
    """The original construction, for reproduction only.

    One stream per compound, consumed inside the form loop, on each form's own
    frame. Every detail of that matters: a reimplementation that draws the
    three splits in another order returns different numbers that look just as
    reasonable.
    """
    rng = np.random.default_rng(RNG_SEED)
    out = {}
    for form in FORMS:
        f = filter_per_form(cd, form)
        if len(f) < MIN_PTS or f.temperature_K.nunique() < MIN_DISTINCT_T:
            continue
        n = len(f)
        idx = np.arange(n)
        rng.shuffle(idx)
        cut = int(round((1 - HOLDOUT_FRAC) * n))
        tr, ho = f.iloc[idx[:cut]], f.iloc[idx[cut:]]
        mae, _, p = score(form, tr, ho, bounded=False)
        out[form] = mae
        out[form + "_params"] = p
        out[form + "_holdout_index"] = set(ho.index)
        out[form + "_n_train"] = len(tr)
        out[form + "_n_holdout"] = len(ho)
    return out


# ------------------------------------------------------------------ the guards
def gate_reproduction(d, compounds):
    """Per-compound agreement with the original's own deposited output.

    Six rounded aggregates are not a reproduction check: the published median
    clears a 5e-4 tolerance by 1.4e-4, which a scipy release could move. The
    original deposited its Form 3 table per compound, so that is what is
    asserted, along with the training and holdout sizes, which pin the filters,
    the skip rule and the position of Form 3 in the random stream.
    """
    ref = pd.read_csv(REF).set_index("mp_formula")
    worst, n = 0.0, 0
    bad = []
    for c in compounds:
        r = run_published(d[d.mp_formula == c])
        want = ref.loc[c] if c in ref.index else None
        if want is None or str(want.form3_status) != "ok":
            if "form3" in r:
                bad.append("%s: scored here, skipped in the deposit" % c)
            continue
        if "form3" not in r:
            bad.append("%s: skipped here, scored in the deposit" % c)
            continue
        n += 1
        for got, exp, what in ((r["form3"], want.form3_holdout_MAE, "MAE"),
                               (r["form3_n_train"], want.form3_n_train, "train"),
                               (r["form3_n_holdout"], want.form3_n_holdout,
                                "holdout")):
            if what == "MAE":
                rel = abs(got - exp) / max(abs(exp), 1e-12)
                worst = max(worst, rel)
                if rel > 1e-6:
                    bad.append("%s: Form 3 MAE %.9f against the deposited "
                               "%.9f" % (c, got, exp))
            elif int(got) != int(exp):
                bad.append("%s: Form 3 %s size %d against the deposited %d"
                           % (c, what, int(got), int(exp)))
    if n == 0:
        bad.append("no compound was compared; the reference did not load")
    if bad:
        raise SystemExit("this is not the same fitter, so nothing downstream "
                         "means anything:\n   " + "\n   ".join(bad))
    print("   reproduces the deposited Form 3 table on %d compounds, worst "
          "relative disagreement %.2e" % (n, worst))


def gate_aggregates(pub):
    bad = []
    for form in FORMS:
        if abs(pub[form]["median"] - PUBLISHED[form]) > 5e-4:
            bad.append("%s median %.4f against %.3f"
                       % (form, pub[form]["median"], PUBLISHED[form]))
        if abs(pub[form]["mean"] - PUBLISHED_MEAN[form]) > 5e-4:
            bad.append("%s mean %.4f against %.3f"
                       % (form, pub[form]["mean"], PUBLISHED_MEAN[form]))
    if bad:
        raise SystemExit("Table II does not reproduce:\n   "
                         + "\n   ".join(bad))
    print("   reproduces Table II: median %.4f / %.4f / %.4f, "
          "mean %.4f / %.4f / %.4f"
          % tuple([pub[f]["median"] for f in FORMS]
                  + [pub[f]["mean"] for f in FORMS]))


def gate_rows_are_shared(d, compounds):
    """The claim that makes every non-published row a like-for-like comparison.

    It is checked on the frames run_common actually uses, not on a private
    re-derivation, because an earlier version checked an identity that was
    algebraically true for any input and left the whole construction unguarded:
    a mutation that redrew the split per form passed it and moved every number.
    """
    checked = 0
    for mode in ("point", "curve", "paper"):
        for c in compounds:
            r = run_common(d[d.mp_formula == c], mode)
            if r is None:
                continue
            rows = {f: r[f + "_rows"] for f in FORMS}
            if len(set(rows.values())) != 1:
                raise SystemExit(
                    "%s / %s: the three forms were scored on different rows; "
                    "train sizes %s, holdout sizes %s"
                    % (c, mode, [len(rows[f][0]) for f in FORMS],
                       [len(rows[f][1]) for f in FORMS]))
            if set(rows["form1"][0]) & set(rows["form1"][1]):
                raise SystemExit("%s / %s: training and holdout overlap"
                                 % (c, mode))
            checked += 1
    if checked < 3 * MIN_GUARD_COMPOUNDS:
        raise SystemExit("the shared-rows check ran on only %d compound-runs; "
                         "at least %d were expected, so the guard is not "
                         "covering the table"
                         % (checked, 3 * MIN_GUARD_COMPOUNDS))
    print("   identical training and holdout rows across the three forms on "
          "all %d compound-runs" % checked)


def gate_published_splits_differ(d, compounds):
    """The caption's claim, tested rather than asserted."""
    same = n = 0
    for c in compounds:
        r = run_published(d[d.mp_formula == c])
        if "form1_holdout_index" in r and "form3_holdout_index" in r:
            n += 1
            same += int(r["form1_holdout_index"] == r["form3_holdout_index"])
    if n == 0:
        raise SystemExit("the split check ran on no compound")
    if same:
        raise SystemExit("%d compound(s) share a Form 1 and Form 3 holdout "
                         "under the published construction; the caption would "
                         "then be right" % same)
    print("   identical Form 1 / Form 3 holdouts on 0 of %d compounds under "
          "the published construction" % n)


# -------------------------------------------------------------- diagnostics
def report_unbounded(d, compounds):
    """The published table's own non-identifiable fits."""
    rows = []
    for c in compounds:
        r = run_published(d[d.mp_formula == c])
        for form in ("form2", "form3"):
            p = r.get(form + "_params")
            if p is not None and abs(p[-1]) > EXP_BOUND:
                rows.append((c, form, float(p[-1])))
    if rows:
        print("   fits in the published construction whose field exponent "
              "exceeds %g:" % EXP_BOUND)
        for c, form, g in sorted(rows, key=lambda t: -abs(t[2])):
            print("      %-22s %-6s %12.4g" % (c, form, g))
    return rows


def report_curve_leakage(d, compounds):
    """Held-out rows with an exact twin still in training."""
    leaked = total = 0
    for c in compounds:
        cd = d[d.mp_formula == c]
        f = common_frame(cd)
        if len(f) < MIN_PTS:
            continue
        rng = np.random.default_rng(RNG_SEED)
        keys = curve_key(f)
        held = choose_held(keys, rng)
        if held is None:
            continue
        m = keys.isin(held)
        tr, ho = f[~m], f[m]
        if not usable(tr, ho):
            continue
        seen = set(zip(tr.pdf_name, tr.temperature_K, tr.field_T))
        total += len(ho)
        leaked += sum(1 for t in zip(ho.pdf_name, ho.temperature_K, ho.field_T)
                      if t in seen)
    print("   curve holdout: %d of %d held-out rows share an exact "
          "(source, temperature, field) coordinate with a training row, from "
          "another sample in the same source" % (leaked, total))
    return leaked, total


# ------------------------------------------------------------------- the table
def summarise_published(d, compounds):
    per = {f: [] for f in FORMS}
    for c in compounds:
        r = run_published(d[d.mp_formula == c])
        for f in FORMS:
            if f in r and np.isfinite(r[f]):
                per[f].append(r[f])
    return {f: dict(median=float(np.median(per[f])),
                    mean=float(np.mean(per[f])), n=len(per[f]))
            for f in FORMS}


def withdrawal_filter(d):
    w = pd.read_csv(WITHDRAWN)
    keys = set(w.paper_id.dropna().astype(str))
    present = keys & set(d.pdf_name.astype(str))
    if len(present) != N_WITHDRAWN or len(keys) != N_WITHDRAWN:
        raise SystemExit("the withdrawal ledger holds %d papers and %d of them "
                         "appear in the input; %d was expected for both"
                         % (len(keys), len(present), N_WITHDRAWN))
    out = d[~d.pdf_name.astype(str).isin(keys)]
    if len(d) - len(out) != N_WITHDRAWN_ROWS:
        raise SystemExit("the withdrawals removed %d rows, not the %d this "
                         "input carried when it was deposited"
                         % (len(d) - len(out), N_WITHDRAWN_ROWS))
    return out


# ----------------------------------------------------------- the comparison
def sweep(frame, compounds, mode):
    """Every compound, every seed, on identical rows.

    One split is a coin toss with n between eight and twenty-two. An
    independent review varied only the seed and found the ordering of the
    three forms changing on a third of draws, so a single split cannot carry
    the comparison and is not reported. What is reported is each compound's
    error across SEEDS draws, and then the direction of the paired difference
    across compounds, which is what the ordering of two functional forms
    actually means.
    """
    per = {}
    hits = set()
    for c in compounds:
        cd = frame[frame.mp_formula == c]
        got = {f: [] for f in FORMS}
        for seed in SEEDS:
            r = run_common(cd, mode, seed=seed)
            if r is None:
                continue
            for f in FORMS:
                got[f].append(r[f])
                if r[f + "_bound_hit"]:
                    hits.add(c)
        if got["form1"]:
            per[c] = {f: float(np.median(got[f])) for f in FORMS}
    return per, hits


def sign_p(wins, n):
    """Two-sided sign test, exact."""
    if n == 0:
        return float("nan")
    from math import comb
    k = max(wins, n - wins)
    tail = sum(comb(n, i) for i in range(k, n + 1)) / float(2 ** n)
    return min(1.0, 2 * tail)


def report(frame, label, mode, drop_ill):
    per, hits = sweep(frame, sorted(frame.mp_formula.unique()), mode)
    if drop_ill:
        per = {c: v for c, v in per.items() if c not in hits}
    if not per:
        return None
    med = {f: float(np.median([per[c][f] for c in per])) for f in FORMS}
    w32 = sum(per[c]["form3"] < per[c]["form2"] for c in per)
    w31 = sum(per[c]["form3"] < per[c]["form1"] for c in per)
    n = len(per)
    row = dict(cohort=label, construction=mode,
               scope="well conditioned" if drop_ill else "all scoreable",
               n_compounds=n, n_ill_conditioned=len(hits),
               form1=med["form1"], form2=med["form2"], form3=med["form3"],
               form3_beats_form2=w32, p_vs_form2=sign_p(w32, n),
               form3_beats_form1=w31, p_vs_form1=sign_p(w31, n))
    print("   %-40s %7.3f %7.3f %7.3f %4d   %2d/%-2d %6.3f   %2d/%-2d %6.3f"
          % ("%s / %s / %s" % (label, mode, row["scope"]),
             med["form1"], med["form2"], med["form3"], n,
             w32, n, row["p_vs_form2"], w31, n, row["p_vs_form1"]))
    return row


def bound_sensitivity(frame, label):
    """The ordering, at three exponent bounds.

    The bound is a choice, so it is swept rather than asserted. An independent
    review showed that at a bound of 2 the ordering inverts and at 1e9 it
    widens, and that neither is caught by any gate. What the sweep is for is
    to say which conclusions do not depend on it.
    """
    global EXP_BOUND
    keep = EXP_BOUND
    print("\n   exponent bound sweep on %s, well-conditioned compounds only"
          % label)
    print("   %-7s %-6s %7s %7s %7s %4s  %-11s %-11s"
          % ("bound", "split", "form1", "form2", "form3", "n",
             "3 over 2", "3 over 1"))
    for b in (10.0, 50.0, 200.0):
        EXP_BOUND = b
        for mode in ("point", "curve", "paper"):
            per, hits = sweep(frame, sorted(frame.mp_formula.unique()), mode)
            per = {c: v for c, v in per.items() if c not in hits}
            if not per:
                continue
            med = {f: float(np.median([per[c][f] for c in per]))
                   for f in FORMS}
            n = len(per)
            w32 = sum(per[c]["form3"] < per[c]["form2"] for c in per)
            w31 = sum(per[c]["form3"] < per[c]["form1"] for c in per)
            print("   %-7g %-6s %7.3f %7.3f %7.3f %4d  %2d/%-2d %6.3f  "
                  "%2d/%-2d %6.3f" % (b, mode, med["form1"], med["form2"],
                                      med["form3"], n, w32, n, sign_p(w32, n),
                                      w31, n, sign_p(w31, n)))
    EXP_BOUND = keep


def screen_filter(d):
    """Drop the eighteen sources that failed the read against their figures.

    Asserted rather than assumed: all eighteen have to be present in the input,
    because the point of the cohort is that Table II was computed before any of
    them was screened.
    """
    keys = {p + ".pdf" for p in SCREEN_FAILED}
    present = keys & set(d.pdf_name.astype(str))
    if len(present) != len(SCREEN_FAILED):
        raise SystemExit("%d of the %d screen-failed sources are in the "
                         "input; all of them were expected, missing %s"
                         % (len(present), len(SCREEN_FAILED),
                            sorted(keys - present)))
    if keys & set(pd.read_csv(WITHDRAWN).paper_id.astype(str)):
        raise SystemExit("a screen-failed source is also in the withdrawal "
                         "ledger; the two sets were disjoint when this was "
                         "written and the cohorts below assume it")
    return d[~d.pdf_name.astype(str).isin(keys)]


def main():
    for p in (IN, REF, WITHDRAWN):
        if not os.path.exists(p):
            sys.exit("missing input: %s" % p)
    d = load()
    compounds = sorted(d.mp_formula.unique())
    print("functional-form comparison\n")
    print("   %d rows, %d compounds, %d sources, %d isotherms"
          % (len(d), len(compounds), d.pdf_name.nunique(),
             d.groupby(["pdf_name", "compound_raw", "temperature_K"]).ngroups))

    gate_reproduction(d, compounds)
    gate_aggregates(summarise_published(d, compounds))
    gate_published_splits_differ(d, compounds)
    gate_rows_are_shared(d, compounds)
    ill = report_unbounded(d, compounds)
    report_curve_leakage(d, compounds)

    dw = withdrawal_filter(d)
    print("   the eleven withdrawals remove %d of %d rows"
          % (len(d) - len(dw), len(d)))
    print("   %d seeds per compound per construction" % len(SEEDS))

    hdr = ("   %-40s %7s %7s %7s %4s   %-9s %-9s"
           % ("cohort / construction / scope", "form1", "form2", "form3",
              "n", "3 over 2", "3 over 1"))
    print("\n" + hdr)
    print("   " + "-" * (len(hdr) - 3))
    out = []
    ds = screen_filter(d)
    print("   the eighteen screen-failed sources remove %d of %d rows and "
          "%d of %d compounds" % (len(d) - len(ds), len(d),
                                  d.mp_formula.nunique()
                                  - ds.mp_formula.nunique(),
                                  d.mp_formula.nunique()))
    for label, frame in (("as published", d), ("withdrawals removed", dw),
                         ("screen-failed removed", ds)):
        for mode in ("point", "curve", "paper"):
            for drop_ill in (False, True):
                r = report(frame, label, mode, drop_ill)
                if r:
                    out.append(r)
    pd.DataFrame(out).to_csv(OUT, index=False)
    bound_sensitivity(dw, "the post-withdrawal cohort")
    print("\n   Medians are each compound's median over %d seeds, then the "
          "median over compounds." % len(SEEDS))
    print("   The two right-hand columns are how many compounds Form 3 beats "
          "the other form on,")
    print("   paired on identical rows, with an exact two-sided sign test.")
    print("   wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
