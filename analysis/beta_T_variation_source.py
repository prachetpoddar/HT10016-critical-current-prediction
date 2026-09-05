#!/usr/bin/env python3
"""
beta_T_variation_source.py

Where the temperature exponent's variation with applied field comes from.

The open item. On 2026-09-05 the temperature axis was rebuilt from pixel traces
and beta_T turned out to vary with the field it is fitted at, by a half-range of
1.35 against a quoted uncertainty of 0.32. That was reported as showing a single
exponent hides real structure.

The retrace recorded the same day gives a competing explanation. If the surface
a fit is made from is separable, log Jc(T, H) = a(T) + b(H), then at fixed field
the temperature dependence is a(T) plus a constant, so regressing on
log(1 - T/Tc) with Tc fixed per paper returns the SAME slope at every field.
beta_T would be exactly constant in H. Any variation must then come from
somewhere other than the sample.

Three candidates, and this separates them.

  1. QUANTISATION. The deposited values carry one to three significant figures
     and sit on a shared geometric ladder of eight to forty-six distinct
     mantissas. Rounding an exactly separable surface to that precision breaks
     the separability, and the break is not the same at every field, so beta_T
     acquires a spread from nothing but the rounding.

     WHAT THIS CANNOT DO, and the first version of this script claimed it
     could. The size of the quantisation null depends on which quantisation
     model is used, and the models do not agree: rounding every cell at the
     paper's median precision gives one answer, rounding each cell at its own
     precision gives half of it, rounding at the paper's finest precision gives
     a tenth, and snapping to the paper's own observed mantissa ladder gives
     zero, because a shared ladder makes the columns exact rung shifts of one
     another and beta_T exactly constant. Nor is there any per-paper
     association between the null and the observed spread. So the honest
     statement is that the observed spread is of the SAME ORDER as what
     quantisation can inject and the two cannot be separated on these data.
     All four nulls are printed. None of them is the answer on its own.
  2. THE WINDOW. If the isotherms available change with field, the fit is over a
     different temperature set at different fields.
  3. THE SAMPLE. The printed figure really does carry interaction, and the
     variation is a property of the material.

Method. beta_T is first reproduced from the extraction bit for bit, so the rule
is known before anything is changed: log10 Jc against log10(1 - T/Tc) over the
fit's own [T_min, T_max] at its own field, every row kept, no per-temperature
collapse. That reproduces 257 of the 258 deposited fits with an extraction to
1e-3. Then the same fit is run on

  - the extraction, giving the deposited spread
  - the extraction's own additive fit, quantised four ways, giving the range of
    spreads quantisation can produce on its own
  - the pixel trace of the same figure, resampled onto the same fields and
    fitted over the same window with the same Tc, giving the spread a reading of
    the printed curves produces. The extraction arm is then refitted on exactly
    the fields the figure arm survives on, because comparing a half-range over
    twenty-one fields with one over nine is not a comparison. The figure arm
    also carries its own floor: the scatter of a trace about a smooth curve
    propagated through an exactly separable surface, which is what a reading of
    a real figure produces from nothing.

    python3 analysis/beta_T_variation_source.py
    python3 analysis/beta_T_variation_source.py --selftest

Run from the repository root. Writes audit/beta_T_variation_source.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

WIDE = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
        "agent2_dataset_v3_2_1.csv")
FITS = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
RE = os.path.join("data", "reextraction")
OUT = os.path.join("audit", "beta_T_variation_source.csv")

TRACE = {
    "0806.2839v1.pdf": "0806_2839v1_fig3",
    "0903.0004v2.pdf": "0903_0004v2_fig6b",
    "0906.0444v1.pdf": "0906_0444v1_fig3a",
    "1002.0208v2.pdf": "1002_0208v2_fig5a",
    "1009.4896v1.pdf": "1009_4896v1_fig2b",
    "1104.0477v2.pdf": "1104_0477v2_fig3c",
    "1108.0407v1.pdf": "1108_0407v1_fig5d",
    "1111.3923v1.pdf": "1111_3923v1_fig4a",
    "1502.05345v1.pdf": "1502_05345v1_fig4b_Hc",
    "1611.08455v1.pdf": "1611_08455v1_fig5b_bothsamples",
    "1903.00866v2.pdf": "1903_00866v2_fig4",
    "2012.13723v3.pdf": "2012.13723_fig4",
    "2207.06629v1.pdf": "2207.06629_fig4",
    "2308.10492v1.pdf": "2308_10492v1_fig2b",
    "2510.10264v1.pdf": "2510_10264v1_fig4a",
    "2511.19058v1.pdf": "2511_19058v1_fig2b",
}
MIN_FIELDS = 4


def beta_T(T, J, Tc):
    """The deposited rule: log10 Jc on log10(1 - T/Tc), every row kept."""
    T = np.asarray(T, float)
    J = np.asarray(J, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        x = np.log10(1 - T / Tc)
        y = np.log10(J)
    m = np.isfinite(x) & np.isfinite(y) & (J > 0)
    if m.sum() < 3:
        return np.nan, 0
    return float(np.polyfit(x[m], y[m], 1)[0]), int(m.sum())


def sigfigs(x):
    s = f"{x:.10e}".split("e")[0].rstrip("0").rstrip(".")
    return max(len(s.replace("-", "").replace(".", "")), 1)


def round_sig(v, n):
    if v <= 0 or not np.isfinite(v):
        return v
    mag = int(np.floor(np.log10(abs(v))))
    return round(v, -(mag - (n - 1)))


def additive_surface(M):
    """The best separable approximation: row mean plus column mean minus grand."""
    return (M.mean(axis=1, keepdims=True) + M.mean(axis=0, keepdims=True)
            - M.mean())


def quantisation_nulls(piv, Ts, Tc):
    """The beta_T spread four quantisation models inject into a separable surface.

    The base surface is the paper's own additive fit, which is exactly separable
    and therefore has a constant beta_T before anything is done to it. What
    differs between the four is only how it is written down.
    """
    J = piv.to_numpy(float)
    M = np.log10(J)
    A = 10.0 ** additive_surface(M)
    sig = np.vectorize(sigfigs)(J)
    out = {}

    def spread(B):
        return half_range([beta_T(Ts, B[:, k], Tc)[0] for k in range(B.shape[1])])

    for name, n in (("q_median_sigfig", int(np.median(sig))),
                    ("q_min_sigfig", int(sig.min())),
                    ("q_max_sigfig", int(sig.max()))):
        out[name] = round(spread(np.vectorize(round_sig)(A, n)), 3)
    # each cell at its own recorded precision
    out["q_own_sigfig"] = round(spread(
        np.vectorize(round_sig)(A, sig)), 3)
    # snapped to the paper's own observed mantissa ladder, which is what the
    # values actually sit on
    man = np.unique(np.round(J / 10.0 ** np.floor(np.log10(J)), 6))

    def snap(v):
        d = np.floor(np.log10(v))
        m = v / 10.0 ** d
        return float(man[np.argmin(np.abs(man - m))] * 10.0 ** d)
    out["q_own_ladder"] = round(spread(np.vectorize(snap)(A)), 3)
    out["sig_min"] = int(sig.min())
    out["sig_med"] = int(np.median(sig))
    out["sig_max"] = int(sig.max())
    out["n_mantissas"] = int(len(man))
    return out


def half_range(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    return float((v.max() - v.min()) / 2) if len(v) >= 2 else np.nan


def field_scale_groups(H):
    """Split a field grid at any jump of more than a hundredfold.

    1903.00866v2's extraction holds 0.0005 to 0.005 T and 0.5 to 5.0 T for what
    are the same physical fields written on two unit scales, from different
    pages. Pivoting them as one surface produced the largest half-range in the
    table and it was a spread across unit systems, not across field.
    """
    H = np.sort(np.unique(np.asarray(H, float)))
    pos = H[H > 0]
    if len(pos) < 2:
        return [H]
    groups, cur = [], [pos[0]]
    for a, b in zip(pos[:-1], pos[1:]):
        if b / a > 50:
            groups.append(cur)
            cur = []
        cur.append(b)
    groups.append(cur)
    if len(groups) == 1:
        return [H]
    # zero belongs with the group it is on the scale of; give it to the largest
    big = max(range(len(groups)), key=lambda i: len(groups[i]))
    out = [np.array(g) for g in groups]
    if (H == 0).any():
        out[big] = np.concatenate([[0.0], out[big]])
    return out


def paper_table(wide, fits, pk):
    """The (T, H) cells of one paper's fit window, as a rectangular matrix.

    Returns (matrix, note). The note records what had to be done to get one, so
    that a paper carrying two unit systems or duplicated cells is not read as if
    it were clean.
    """
    f = fits[fits.paper_key == pk]
    if not len(f):
        return None, "no fits"
    tmin, tmax = f.T_min.min(), f.T_max.max()
    w = wide[(wide.pdf_name == pk) & (wide.temperature_K >= tmin - 1e-9)
             & (wide.temperature_K <= tmax + 1e-9) & (wide.Jc > 0)]
    if not len(w):
        return None, "no extraction in the window"
    notes = []
    groups = field_scale_groups(w.field_T)
    if len(groups) > 1:
        # choose by which scale the DEPOSITED fits use, not by which has more
        # points. Picking the larger group sent 1502.05345v1 to a scale its own
        # fits never touch and made it unscorable.
        dep = f.field_T.to_numpy(float)
        share = [np.isin(dep, g).mean() for g in groups]
        best = int(np.argmax(share))
        if sorted(share)[-2] > 0.25:
            return None, (f"the deposited fits straddle two field scales, "
                          f"{', '.join(f'{g.min():g} to {g.max():g}' for g in groups)}, "
                          f"which are the same physical fields in two unit "
                          f"systems; its deposited half-range is a spread "
                          f"across unit systems and is excluded")
        keep = groups[best]
        notes.append(f"two field scales, kept {keep.min():g} to {keep.max():g}, "
                     f"the one {share[best]*100:.0f}% of its own fits use")
        w = w[w.field_T.isin(keep)]
    dup = w.groupby(["temperature_K", "field_T"]).size()
    if (dup > 1).any():
        spread = (w.groupby(["temperature_K", "field_T"]).Jc.max()
                  / w.groupby(["temperature_K", "field_T"]).Jc.min()).max()
        notes.append(f"{int((dup > 1).sum())} cells duplicated, worst "
                     f"{spread:.0f}x apart, medianed")
    piv = w.pivot_table(index="temperature_K", columns="field_T",
                        values="Jc", aggfunc="median")
    piv = piv.dropna(axis=1, how="any")
    if piv.shape[0] < 3 or piv.shape[1] < MIN_FIELDS:
        return None, "no rectangular window"
    return piv, "; ".join(notes)


def trace_isotherms(name):
    p = os.path.join(RE, name + "_points.csv")
    if not os.path.exists(p):
        return None
    d = pd.read_csv(p)
    return {float(T): (g.field_T.to_numpy(float), g.Jc_A_per_cm2.to_numpy(float))
            for T, g in d.groupby("temperature_K")}


def selftest():
    bad = 0
    H = np.array([0., 1., 2., 3., 4., 5.])
    Ts = np.array([2., 5., 8., 11.])
    Tc = 20.0

    # 1. On an exactly separable surface beta_T must not move with field.
    J = np.outer((1 - Ts / Tc) ** 1.7, (1 - H / 9.) ** 1.1) * 1e6
    b = [beta_T(Ts, J[:, k], Tc)[0] for k in range(len(H))]
    hr = half_range(b)
    ok = hr < 1e-9
    print(f"  [{'PASS' if ok else 'FAIL'}] separable surface: beta_T half-range "
          f"{hr:.2e} across field, want < 1e-9")
    bad += not ok

    # 2. Rounding that surface to one figure must give it a spread.
    Jr = np.vectorize(lambda v: round_sig(v, 1))(J)
    hr1 = half_range([beta_T(Ts, Jr[:, k], Tc)[0] for k in range(len(H))])
    ok = hr1 > 0.02
    print(f"  [{'PASS' if ok else 'FAIL'}] the same surface rounded to one "
          f"significant figure: half-range {hr1:.4f}, want > 0.02")
    bad += not ok

    # 3. A surface with a falling Hc2(T) must give a spread at full precision,
    #    so the statistic is not only sensitive to rounding.
    Jh = np.array([[1e6 * (1 - T / Tc) ** 1.7
                    * max(1 - h / (9. * (1 - (T / Tc) ** 2)), 1e-6) ** 1.1
                    for h in H] for T in Ts])
    hr2 = half_range([beta_T(Ts, Jh[:, k], Tc)[0] for k in range(len(H))])
    ok = hr2 > 0.05
    print(f"  [{'PASS' if ok else 'FAIL'}] Hc2(T) surface at full precision: "
          f"half-range {hr2:.4f}, want > 0.05")
    bad += not ok

    # 4. round_sig must round, and must be monotone in the number of figures.
    ok = (round_sig(123456., 1) == 100000. and round_sig(123456., 3) == 123000.
          and round_sig(123456., 6) == 123456.)
    print(f"  [{'PASS' if ok else 'FAIL'}] round_sig at 1, 3, 6 figures: "
          f"{round_sig(123456., 1):.0f}, {round_sig(123456., 3):.0f}, "
          f"{round_sig(123456., 6):.0f}")
    bad += not ok
    # 5. additive_surface: exactly separable, and equivariant under a
    #    multiplicative rescale of the input. Nothing tested it, and dropping
    #    its grand-mean term leaves it separable while shifting every cell
    #    against the rounding grid, which moves the whole quantisation result
    #    with no visible symptom.
    M = np.log10(np.outer((1 - Ts / Tc) ** 1.7, (1 - H / 9.) ** 1.1) * 1e6)
    A = additive_surface(M)
    inter = A - (A.mean(axis=1, keepdims=True) + A.mean(axis=0, keepdims=True)
                 - A.mean())
    resc = additive_surface(M + np.log10(7.0))
    ok = (np.abs(inter).max() < 1e-12
          and np.abs(A - M).max() < 1e-12
          and np.abs((resc - A) - np.log10(7.0)).max() < 1e-12)
    print(f"  [{'PASS' if ok else 'FAIL'}] additive_surface reproduces an "
          f"already-separable surface to {np.abs(A - M).max():.1e} and shifts "
          f"by exactly log10(7) when the input is scaled by 7")
    bad += not ok

    # 6. round_sig at the decade carry, below one, and its own post-condition
    cases = [(9.99e5, 1, 1e6), (999999., 1, 1e6), (0.001234, 2, 0.0012),
             (0.0987, 1, 0.1)]
    ok = all(abs(round_sig(v, n) - want) <= abs(want) * 1e-9
             for v, n, want in cases)
    post = all(sigfigs(round_sig(v, n)) <= n for v, n, _ in cases)
    print(f"  [{'PASS' if ok and post else 'FAIL'}] round_sig at the decade "
          f"carry and below one: "
          f"{[round_sig(v, n) for v, n, _ in cases]}, and its output never "
          f"carries more figures than asked")
    bad += not (ok and post)

    # 7. paper_table must notice a duplicated cell and two field scales
    small = [0.001, 0.002, 0.003, 0.004]
    large = [1.0, 2.0, 3.0, 4.0]
    recs = []
    for T in (2., 4., 6.):
        for Hf in small + large:
            recs.append(dict(pdf_name="x", temperature_K=T, field_T=Hf,
                             Jc=1e5 * (1 - T / 20.) / (1 + Hf)))
    recs.append(dict(pdf_name="x", temperature_K=2., field_T=small[0],
                     Jc=6e6))          # a duplicated cell, 60x apart
    wide = pd.DataFrame(recs)
    ff = pd.DataFrame(dict(paper_key=["x"] * 4, T_min=[2.] * 4,
                           T_max=[6.] * 4, field_T=small))
    _, note = paper_table(wide, ff, "x")
    ok = "duplicated" in note and "field scale" in note
    print(f"  [{'PASS' if ok else 'FAIL'}] paper_table reports what it had to "
          f"do: {note!r}")
    bad += not ok

    print("  selftest:", "all guards fire" if not bad
          else f"{bad} GUARD(S) DID NOT FIRE")
    return bad


def main():
    if "--selftest" in sys.argv:
        return selftest()
    print("selftest first")
    if selftest():
        print("THE STATISTIC DOES NOT BEHAVE. Nothing below is trustworthy.")
        return 1
    print()
    wide = pd.read_csv(WIDE)
    fits = pd.read_csv(FITS)

    # reproduction before change
    ok = tot = 0
    misses = []
    for _, r in fits.iterrows():
        g = wide[(wide.pdf_name == r.paper_key)
                 & (np.isclose(wide.field_T, r.field_T))]
        if not len(g):
            continue
        g = g[(g.temperature_K >= r.T_min - 1e-9)
              & (g.temperature_K <= r.T_max + 1e-9)]
        b, n = beta_T(g.temperature_K, g.Jc, r.Tc_K)
        tot += 1
        hit = np.isfinite(b) and abs(b - r.beta_T) < 1e-3 and n == r.n_T_pts
        ok += hit
        if not hit:
            misses.append((r.paper_key, r.field_T, r.beta_T, b, r.n_T_pts, n))
    print(f"reproduction before change: the deposited beta_T is recovered from "
          f"the extraction for {ok} of {tot} fits that have one")
    if ok / max(tot, 1) < 0.95:
        print("  THE FIT RULE IS NOT REPRODUCED. Everything below is guesswork.")
        return 1
    for pk, H, dep, got, nd, ng in misses:
        sib = fits[(fits.paper_key == pk) & (fits.field_T != H)].beta_T
        print(f"  the one that does not: {pk} at {H:g} T, deposited {dep:.4f}, "
              f"the rule gives {got:.4f} on the same {ng} points")
        if len(sib):
            print(f"    every other field of that paper reproduces and lies in "
                  f"{sib.min():.3f} to {sib.max():.3f}, so this single "
                  f"departure carries "
                  f"{100 * (1 - (sib.max() - sib.min()) / (fits[fits.paper_key == pk].beta_T.max() - fits[fits.paper_key == pk].beta_T.min())):.0f}% "
                  f"of that paper's deposited half-range. It is not a random "
                  f"miss, it is the extreme value.")
    print()

    rows = []
    for pk, f in fits.groupby("paper_key"):
        Tc = f.Tc_K.iloc[0]
        piv, note = paper_table(wide, fits, pk)
        rec = dict(paper=pk, Tc=Tc, n_fits=len(f),
                   deposited_half_range=round(half_range(f.beta_T), 3),
                   note=note)
        if piv is None:
            rows.append(rec)
            continue
        Ts = piv.index.to_numpy(float)
        Hs = piv.columns.to_numpy(float)
        J = piv.to_numpy(float)
        rec["n_T"], rec["n_H"] = len(Ts), len(Hs)
        b_ext = np.array([beta_T(Ts, J[:, k], Tc)[0] for k in range(len(Hs))])
        rec["extraction_half_range"] = round(half_range(b_ext), 3)
        rec.update(quantisation_nulls(piv, Ts, Tc))

        # the figure, on the fields it can actually reach, and the extraction
        # refitted on exactly those fields
        rec["figure_note"] = ""
        tr = trace_isotherms(TRACE[pk]) if pk in TRACE else None
        if pk not in TRACE:
            rec["figure_note"] = "no trace"
        elif tr is None:
            rec["figure_note"] = "trace file missing"
        else:
            shared = [T for T in Ts if any(abs(T - t) < 0.05 for t in tr)]
            if len(shared) < 3:
                rec["figure_note"] = (f"only {len(shared)} isotherm labels "
                                      f"match the figure's")
            else:
                cols, scat = [], []
                for T in shared:
                    key = min(tr, key=lambda t: abs(t - T))
                    Ht, Jt = tr[key]
                    o = np.argsort(Ht)
                    Ht, Jt = Ht[o], Jt[o]
                    good = Jt > 0
                    Ht, Jt = Ht[good], Jt[good]
                    uH, idx = np.unique(Ht, return_inverse=True)
                    uJ = np.array([np.exp(np.mean(np.log(Jt[idx == i])))
                                   for i in range(len(uH))])
                    # reading scatter of this isotherm about a smooth curve
                    if len(uH) >= 6:
                        x = np.log10(np.clip(uH, 1e-9, None))
                        c = np.polyfit(x, np.log10(uJ), 3)
                        scat.append(np.std(np.log10(uJ) - np.polyval(c, x)))
                    inside = (Hs >= uH.min()) & (Hs <= uH.max())
                    col = np.full(len(Hs), np.nan)
                    col[inside] = 10 ** np.interp(Hs[inside], uH, np.log10(uJ))
                    cols.append(col)
                Jfig = np.array(cols)
                use = np.isfinite(Jfig).all(axis=0)
                if use.sum() < MIN_FIELDS:
                    lo = min(min(tr[k][0]) for k in tr)
                    hi = max(max(tr[k][0]) for k in tr)
                    rec["figure_note"] = (
                        f"the extraction's fields ({Hs.min():.3g} to "
                        f"{Hs.max():.3g}) and the figure's ({lo:.3g} to "
                        f"{hi:.3g}) overlap on {int(use.sum())} points")
                else:
                    idxs = np.where(use)[0]
                    Tarr = np.array(shared)
                    rec["figure_half_range"] = round(half_range(
                        [beta_T(Tarr, Jfig[:, k], Tc)[0] for k in idxs]), 3)
                    # the extraction on EXACTLY those fields and isotherms
                    rsel = [i for i, T in enumerate(Ts)
                            if any(abs(T - t) < 1e-9 for t in shared)]
                    rec["extraction_paired"] = round(half_range(
                        [beta_T(Ts[rsel], J[np.ix_(rsel, [k])].ravel(), Tc)[0]
                         for k in idxs]), 3)
                    # interior only: drop the lowest and highest surviving field
                    if len(idxs) >= MIN_FIELDS + 2:
                        inner = idxs[1:-1]
                        rec["figure_interior"] = round(half_range(
                            [beta_T(Tarr, Jfig[:, k], Tc)[0] for k in inner]), 3)
                        rec["extraction_interior"] = round(half_range(
                            [beta_T(Ts[rsel], J[np.ix_(rsel, [k])].ravel(), Tc)[0]
                             for k in inner]), 3)
                    # what the trace's own reading scatter injects into an
                    # exactly separable surface of the same shape
                    if scat:
                        sd = float(np.median(scat))
                        rec["trace_scatter_dex"] = round(sd, 3)
                        Af = 10.0 ** additive_surface(np.log10(Jfig[:, idxs]))
                        rng = np.random.default_rng(0)
                        floors = []
                        for _ in range(40):
                            N = Af * 10 ** rng.normal(0, sd, Af.shape)
                            floors.append(half_range(
                                [beta_T(Tarr, N[:, k], Tc)[0]
                                 for k in range(N.shape[1])]))
                        rec["figure_floor"] = round(float(np.median(floors)), 3)
                    rec["figure_n_H"] = int(use.sum())
                    rec["figure_n_T"] = len(shared)
        rows.append(rec)
    t = pd.DataFrame(rows)
    os.makedirs("audit", exist_ok=True)
    t.to_csv(OUT, index=False)
    pd.set_option("display.width", 260)
    print("half-range of beta_T across applied field, in the DEPOSIT")
    c1 = [c for c in ["paper", "n_T", "n_H", "sig_min", "sig_med", "sig_max",
                      "n_mantissas", "deposited_half_range",
                      "extraction_half_range", "note"] if c in t.columns]
    print(t[c1].to_string(index=False))
    s = t.dropna(subset=["extraction_half_range"])
    print()
    print(f"{len(s)} of {len(t)} papers have a rectangular fit window")
    print(f"  median deposited half-range   {s.deposited_half_range.median():.3f}")
    print(f"  median on the rebuilt window  {s.extraction_half_range.median():.3f}")
    print()
    print("QUANTISATION. Four models of how these numbers were written down, "
          "each applied to the paper's OWN additive fit, which has a constant "
          "beta_T before it is written down at all:")
    for col, what in (("q_min_sigfig", "every cell at the paper's finest precision"),
                      ("q_median_sigfig", "every cell at the paper's median precision"),
                      ("q_own_sigfig", "each cell at its own recorded precision"),
                      ("q_own_ladder", "snapped to the paper's own mantissa ladder")):
        if col in s:
            print(f"  {s[col].median():6.3f}   {what}")
    print(f"  {s.extraction_half_range.median():6.3f}   OBSERVED")
    from scipy.stats import spearmanr
    ok2 = s.dropna(subset=["q_median_sigfig", "extraction_half_range"])
    rho = spearmanr(ok2.q_median_sigfig, ok2.extraction_half_range)
    ratios = (ok2.q_median_sigfig / ok2.extraction_half_range).replace(
        [np.inf, -np.inf], np.nan).dropna()
    print(f"  per-paper rank correlation between the null and the observed "
          f"spread: rho = {rho.statistic:.3f}, p = {rho.pvalue:.2f} over "
          f"{len(ok2)} papers")
    print(f"  per-paper ratio of null to observed runs "
          f"{ratios.min():.2f} to {ratios.max():.2f}")
    print("  SO: the observed spread is of the same order as what quantisation "
          "can inject, and the two cannot be separated on these data. The "
          "quantisation account is not established and is not reported as "
          "though it were.")
    print()
    print("=" * 78)
    print("THE FIGURE, PAIRED: same isotherms, same fields, same Tc, same rule")
    print("=" * 78)
    g = t.dropna(subset=["figure_half_range"])
    c2 = [c for c in ["paper", "figure_n_T", "figure_n_H", "extraction_paired",
                      "figure_half_range", "extraction_interior",
                      "figure_interior", "trace_scatter_dex", "figure_floor"]
          if c in t.columns]
    print(g[c2].to_string(index=False))
    print()
    if len(g):
        print(f"  paired, over {len(g)} papers: extraction "
              f"{g.extraction_paired.median():.3f}, figure "
              f"{g.figure_half_range.median():.3f}, the figure larger in "
              f"{int((g.figure_half_range > g.extraction_paired).sum())} "
              f"of {len(g)}")
        gi = g.dropna(subset=["figure_interior"])
        if len(gi):
            print(f"  interior fields only, {len(gi)} papers: extraction "
                  f"{gi.extraction_interior.median():.3f}, figure "
                  f"{gi.figure_interior.median():.3f}, the figure larger in "
                  f"{int((gi.figure_interior > gi.extraction_interior).sum())} "
                  f"of {len(gi)}")
        gf = g.dropna(subset=["figure_floor"])
        if len(gf):
            marg = (gf.figure_half_range / gf.figure_floor)
            print(f"  the figure arm has its own floor: its reading scatter "
                  f"propagated through an exactly separable surface of the "
                  f"same shape. The figure half-range is "
                  f"{marg.min():.1f} to {marg.max():.1f} times that floor, "
                  f"median {marg.median():.1f}; "
                  f"{int((marg < 1.5).sum())} of {len(gf)} papers are within "
                  f"1.5 times it and should not be leaned on")
    print()
    ex = t[t.figure_half_range.isna() & (t.figure_note.fillna("") != "")]
    print(f"papers with no figure comparison, and why. These are not neutral "
          f"exclusions: several are papers whose extraction field axis "
          f"disagrees with its own figure by three or four orders of "
          f"magnitude, and those papers stay in the deposit tables above with "
          f"no flag.")
    for _, r in ex.iterrows():
        print(f"  {r.paper:22s} {r.figure_note}")
    print()
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
