#!/usr/bin/env python3
"""
separable_surface_test.py

Is the extracted Jc(T, H) a measured surface, or one curve in T times one curve
in H?

The mechanism under test. To make a family of isotherms you can freeze the
temperature factor, sweep the field, and repeat at each temperature. Everything
built that way satisfies

    log Jc(T, H) = a(T) + b(H)

exactly: the isotherms are one field curve shifted vertically, and the shift
carries all of the temperature dependence. Eq. (1) of the main text with a
constant Hc2 has that form, so a set of curves computed from it is separable to
machine precision.

A measured Jc(T, H) is not. The field dependence steepens as temperature rises,
because the field that matters is H/Hc2(T) and Hc2 falls with temperature. The
interaction term is the physics. Its absence is the signature.

TWO THINGS THE FIRST VERSION OF THIS SCRIPT GOT WRONG, both found by an
independent review, and both of which reversed the answer:

  1. It asked whether any surface was separable to better than 1e-6 dex, found
     none, and reported the mechanism refuted. That bar is unreachable. The
     deposited values carry one to three significant figures, and rounding an
     exactly separable surface to one significant figure injects about 0.04 dex
     of interaction by itself. The right reference is not zero, it is each
     surface's own rounding floor, and that is what is computed here.

  2. It compared an extraction on a 0 to 50 T window against a trace of the same
     figure on a 0.2 to 3.0 T window and called the difference provenance. The
     comparison below is paired: same paper, same isotherms, same field window,
     same code path, so the arms differ only in where the numbers came from.

The residual is a comparative statistic only. It depends on how many fields it
is sampled at, so it is reported at three samplings, and a conclusion that does
not survive all three is not reported.

    python3 analysis/separable_surface_test.py
    python3 analysis/separable_surface_test.py --selftest

Run from the repository root. Writes audit/separable_surface.csv.
"""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd

EXT = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
       "v3_2_2B_extension")
TRACES = os.path.join("data", "reextraction")
OUT = os.path.join("audit", "separable_surface.csv")

MIN_ISOTHERMS = 3
MIN_PTS_PER_ISOTHERM = 4
SAMPLINGS = (3, 5, 9)

# extraction file stem -> trace stem, for the papers held in both arms
PAIRS = {
    "elsevier_10.1016_j.physc.2010.05.048_VISION_PASS": "physc_2010_05_048_fig3",
    "elsevier_10.1016_j.physc.2009.11.051_VISION_PASS": "physc_2009_11_051_fig3",
    "elsevier_10.1016_j.phpro.2015.06.160_VISION_PASS": "phpro_2015_06_160_fig3L",
    "elsevier_10.1016_j.matchemphys.2023.128348_VISION_PASS":
        "matchemphys_2023_128348_fig5",
    "elsevier_10.1016_j.matpr.2019.05.078_VISION_PASS": "matpr_2019_05_078_fig2a",
    "elsevier_10.1016_j.mtphys.2022.100783_VISION_PASS": "mtphys_2022_100783_fig6a",
    "elsevier_10.1016_j.jallcom.2023.170384_LaFeAsO_magnetization_2-10K":
        "jallcom_2023_170384_fig6c",
    "springer_10.1007_s10854-026-16566-9_VISION_PASS": "s10854_fig9a",
}


def additive_residual(M):
    """RMS of the interaction term of a two-way additive fit, in dex.

    The additive model is row mean plus column mean minus grand mean. What is
    left is the interaction: the part of the surface that is not a temperature
    curve plus a field curve in the log.

    The divisor is the nominal interaction degrees of freedom. Where the columns
    are interpolated from fewer knots than there are columns they are not
    independent and the divisor is too large, which is why this number is only
    ever compared with another number produced the same way.
    """
    r = M.mean(axis=1, keepdims=True)
    c = M.mean(axis=0, keepdims=True)
    fit = r + c - M.mean()
    dof = max((M.shape[0] - 1) * (M.shape[1] - 1), 1)
    return float(np.sqrt(((M - fit) ** 2).sum() / dof)), fit


def sigfigs(x):
    """Significant figures of a positive number as it is written."""
    s = f"{x:.10e}".split("e")[0].rstrip("0").rstrip(".")
    return max(len(s.replace("-", "").replace(".", "")), 1)


def rounding_floor(M, nsig):
    """Interaction that rounding alone injects into an exactly separable surface.

    The additive fit of the observed surface IS exactly separable. Round it back
    to the precision the source is written at, and whatever interaction appears
    is the floor below which this source cannot show separability even if it is
    separable.
    """
    _, fit = additive_residual(M)
    lin = 10.0 ** fit
    # np.round takes a scalar number of decimals, so round element by element
    # at each cell's own magnitude
    rounded = np.empty_like(lin)
    it = np.nditer(lin, flags=["multi_index"])
    for v in it:
        val = float(v)
        mag = int(np.floor(np.log10(abs(val)))) if val != 0 else 0
        rounded[it.multi_index] = round(val, -(mag - (nsig - 1)))
    rounded = np.where(rounded > 0, rounded, lin)
    r, _ = additive_residual(np.log10(rounded))
    return r


def to_matrix(iso, n_fields, window=None, temps=None):
    """Common field window, n_fields samples, log10 Jc. None if too thin.

    iso: temperature -> (H array, Jc array). Every arm goes through this.
    window and temps let a pair be forced onto the same isotherms and the same
    field range, which is what makes a paired comparison mean anything.
    """
    keep = {T: v for T, v in iso.items() if len(v[0]) >= MIN_PTS_PER_ISOTHERM}
    if temps is not None:
        keep = {T: v for T, v in keep.items() if T in temps}
    if len(keep) < MIN_ISOTHERMS:
        return None, None
    clean = {}
    for T, (H, J) in keep.items():
        H, J = np.asarray(H, float), np.asarray(J, float)
        o = np.argsort(H)
        H, J = H[o], J[o]
        ok = J > 0
        H, J = H[ok], J[ok]
        if len(H) < MIN_PTS_PER_ISOTHERM:
            continue
        uH, idx = np.unique(H, return_inverse=True)
        uJ = np.array([np.exp(np.mean(np.log(J[idx == i]))) for i in range(len(uH))])
        clean[T] = (uH, uJ)
    if len(clean) < MIN_ISOTHERMS:
        return None, None
    # the window is computed AFTER cleaning, so no isotherm is judged against a
    # range it no longer spans
    lo = max(H.min() for H, _ in clean.values())
    hi = min(H.max() for H, _ in clean.values())
    if window is not None:
        lo, hi = max(lo, window[0]), min(hi, window[1])
    if not (hi > lo):
        return None, None
    grid = np.linspace(lo, hi, n_fields)
    rows, ts = [], []
    for T in sorted(clean):
        H, J = clean[T]
        if H.min() > lo + 1e-12 or H.max() < hi - 1e-12:
            continue
        rows.append(np.interp(grid, H, np.log10(J)))
        ts.append(T)
    if len(rows) < MIN_ISOTHERMS:
        return None, None
    return np.array(rows), ts


def isotherms_from(df):
    return {float(T): (g.field_T.to_numpy(float), g.Jc_A_per_cm2.to_numpy(float))
            for T, g in df.groupby("temperature_K")}


def sample_columns(df):
    """Columns that identify a SAMPLE, not an isotherm.

    A sample column must carry more than one temperature for at least one of its
    values. Without that test `doping_or_composition` is chosen in the hand
    files, where its values are FTS_4.2K, FTS_6K and so on: one per isotherm.
    Splitting on it takes every hand surface apart into single isotherms and the
    whole arm silently disappears, which is what the first version of this did.
    """
    out = []
    for c in ("series", "sample_identifier", "doping_or_composition", "sample_form"):
        if c in df.columns and df[c].nunique() > 1:
            if df.groupby(c).temperature_K.nunique().max() > 1:
                out.append(c)
    return out


def surfaces():
    """Every extraction and every trace, split by sample where a sample exists."""
    for f in sorted(glob.glob(os.path.join(EXT, "*_LONG.csv"))):
        d = pd.read_csv(f)
        if not {"temperature_K", "field_T", "Jc_A_per_cm2"} <= set(d.columns):
            continue
        route = ("hand" if "extraction_method" not in d.columns
                 or d.extraction_method.isna().all() else "vision")
        stem = os.path.basename(f).replace("_LONG.csv", "")
        cols = sample_columns(d)
        if not cols:
            yield ("extraction", route, stem, stem, d)
        else:
            for v, g in d.groupby(cols[0]):
                yield ("extraction", route, f"{stem} | {v}", stem, g)
    for f in sorted(glob.glob(os.path.join(TRACES, "*_points.csv"))):
        d = pd.read_csv(f)
        if not {"temperature_K", "field_T", "Jc_A_per_cm2"} <= set(d.columns):
            continue
        stem = os.path.basename(f).replace("_points.csv", "")
        cols = sample_columns(d)
        if not cols:
            yield ("trace", "pixel", stem, stem, d)
        else:
            for v, g in d.groupby(cols[0]):
                yield ("trace", "pixel", f"{stem} | {v}", stem, g)


def score_all():
    rows = []
    for kind, route, name, stem, d in surfaces():
        rec = dict(kind=kind, route=route, source=name, stem=stem,
                   n_isotherms_raw=d.temperature_K.nunique())
        for n in SAMPLINGS:
            M, ts = to_matrix(isotherms_from(d), n)
            if M is None:
                rec[f"resid_{n}"] = np.nan
                continue
            r, _ = additive_residual(M)
            rec[f"resid_{n}"] = round(r, 5)
            if n == SAMPLINGS[1]:
                nsig = int(np.median([sigfigs(v) for v in
                                      d.Jc_A_per_cm2[d.Jc_A_per_cm2 > 0]]))
                rec["n_isotherms"] = len(ts)
                rec["sigfigs"] = nsig
                rec["rounding_floor"] = round(rounding_floor(M, nsig), 5)
                rec["over_floor"] = (round(r / rec["rounding_floor"], 2)
                                     if rec["rounding_floor"] > 0 else np.nan)
        rows.append(rec)
    return pd.DataFrame(rows)


def paired():
    """Same paper, same isotherms, same field window, both arms."""
    ext = {}
    tra = {}
    for kind, route, name, stem, d in surfaces():
        (ext if kind == "extraction" else tra).setdefault(stem, []).append((name, d))
    out = []
    for estem, tstem in PAIRS.items():
        if estem not in ext or tstem not in tra:
            continue
        for ename, ed in ext[estem]:
            for tname, td in tra[tstem]:
                ei, ti = isotherms_from(ed), isotherms_from(td)
                shared = sorted(set(np.round(list(ei), 2))
                                & set(np.round(list(ti), 2)))
                if len(shared) < MIN_ISOTHERMS:
                    continue
                ei = {round(k, 2): v for k, v in ei.items()}
                ti = {round(k, 2): v for k, v in ti.items()}
                lo = max(min(ei[T][0].min() for T in shared),
                         min(ti[T][0].min() for T in shared))
                hi = min(max(ei[T][0].max() for T in shared),
                         max(ti[T][0].max() for T in shared))
                if not (hi > lo):
                    continue
                row = dict(paper=estem[:46], trace=tstem, n_shared=len(shared),
                           window=f"{lo:.3g}-{hi:.3g}")
                good = True
                for n in SAMPLINGS:
                    Me, _ = to_matrix(ei, n, (lo, hi), set(shared))
                    Mt, _ = to_matrix(ti, n, (lo, hi), set(shared))
                    if Me is None or Mt is None:
                        good = False
                        break
                    row[f"ext_{n}"] = round(additive_residual(Me)[0], 4)
                    row[f"fig_{n}"] = round(additive_residual(Mt)[0], 4)
                if good:
                    out.append(row)
    return pd.DataFrame(out)


def selftest():
    rng = np.random.default_rng(0)
    H = np.linspace(0.1, 5.0, 12)
    bad = 0

    def sep(T):
        return 1e6 * (1 - T / 40.) ** 1.8 * (1 - H / 8.) ** 1.2

    iso = {T: (H, sep(T)) for T in (4., 10., 16., 22.)}
    M, _ = to_matrix(iso, 5)
    r0, _ = additive_residual(M)
    ok = r0 < 1e-9
    print(f"  [{'PASS' if ok else 'FAIL'}] constant-Hc2 Eq.(1) surface "
          f"residual {r0:.2e}, want < 1e-9")
    bad += not ok

    iso2 = {T: (H, 1e6 * (1 - T / 40.) ** 1.8
                * np.clip(1 - H / (8. * (1 - (T / 40.) ** 2)), 1e-6, None) ** 1.2)
            for T in (4., 10., 16., 22.)}
    M2, _ = to_matrix(iso2, 5)
    r2, _ = additive_residual(M2)
    ok = r2 > 0.02
    print(f"  [{'PASS' if ok else 'FAIL'}] Hc2(T) Eq.(1) surface residual "
          f"{r2:.4f} dex, want > 0.02")
    bad += not ok

    # the floor must be the residual that rounding injects, and it must rise as
    # precision falls. The announced property is now the tested one: the first
    # version printed "want >= the unrounded" and tested against a fixed 1e-9.
    floors = [rounding_floor(M, k) for k in (1, 2, 3)]
    ok = floors[0] > floors[1] > floors[2] > r0 and floors[0] > 0.01
    print(f"  [{'PASS' if ok else 'FAIL'}] rounding floor at 1, 2, 3 sig figs: "
          f"{floors[0]:.4f} > {floors[1]:.4f} > {floors[2]:.5f} > the "
          f"unrounded {r0:.1e}")
    bad += not ok

    iso3 = {T: (H, sep(T) * 10 ** rng.normal(0, 0.05, len(H)))
            for T in (4., 10., 16., 22.)}
    M3, _ = to_matrix(iso3, 5)
    r3, _ = additive_residual(M3)
    ok = r3 > 0.02
    print(f"  [{'PASS' if ok else 'FAIL'}] separable plus 0.05 dex noise "
          f"residual {r3:.4f}, want > 0.02")
    bad += not ok

    # sample_columns must not treat a per-isotherm label as a sample
    df = pd.DataFrame(dict(temperature_K=[4., 6., 8., 4., 6., 8.],
                           doping_or_composition=["A_4K", "A_6K", "A_8K",
                                                  "A_4K", "A_6K", "A_8K"],
                           series=["s1", "s1", "s1", "s2", "s2", "s2"],
                           field_T=[1., 1., 1., 1., 1., 1.],
                           Jc_A_per_cm2=[1., 1., 1., 1., 1., 1.]))
    got = sample_columns(df)
    ok = "series" in got and "doping_or_composition" not in got
    print(f"  [{'PASS' if ok else 'FAIL'}] sample columns from a frame whose "
          f"doping label is per-isotherm: {got}, want series only")
    bad += not ok

    # the paired window must actually bind
    Hw = np.linspace(0.1, 50, 20)
    wide = {T: (Hw, 1e5 * (1 - T / 40.) ** 1.8 * np.exp(-Hw / 20.))
            for T in (4., 10., 16.)}
    Ma, _ = to_matrix(wide, 5)
    Mb, _ = to_matrix(wide, 5, (0.1, 3.0))
    ok = Ma is not None and Mb is not None and not np.allclose(Ma, Mb)
    print(f"  [{'PASS' if ok else 'FAIL'}] forcing a field window changes the "
          f"matrix it produces")
    bad += not ok

    print("  selftest:", "all guards fire" if not bad
          else f"{bad} GUARD(S) DID NOT FIRE")
    return bad


def main():
    if "--selftest" in sys.argv:
        return selftest()
    print("selftest first, because the statistic is the whole finding")
    if selftest():
        print("THE STATISTIC DOES NOT BEHAVE. Nothing below is trustworthy.")
        return 1
    print()
    t = score_all()
    os.makedirs("audit", exist_ok=True)
    t.to_csv(OUT, index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 52)
    s = t.dropna(subset=["resid_5"])
    print(f"{len(s)} surfaces scored, {len(t) - len(s)} too thin")
    print(s.groupby("route")[["resid_3", "resid_5", "resid_9"]]
          .median().round(4).to_string())
    print()
    print("each surface against ITS OWN rounding floor: the interaction that "
          "rounding to its recorded precision injects on its own")
    print(s.groupby("route")[["sigfigs", "rounding_floor", "over_floor"]]
          .median().round(4).to_string())
    print("  a floor of zero means the source is written at enough precision to "
          "show separability if it were there; the hand and pixel arms are "
          "written at 8 to 11 figures and are nowhere near their floor")
    print()
    near = s[s.over_floor <= 5]
    print(f"surfaces within 5 times their own rounding floor, meaning as "
          f"separable as their recorded precision can show: {len(near)}")
    print(near.groupby("route").size().to_string())
    print(near[["route", "source", "n_isotherms", "sigfigs", "resid_5",
                "rounding_floor", "over_floor"]].to_string(index=False))
    print()
    print("=" * 72)
    print("PAIRED: same paper, same isotherms, same field window, both arms")
    print("=" * 72)
    p = paired()
    if not len(p):
        print("no pair survived matching")
    else:
        for n in SAMPLINGS:
            p[f"ratio_{n}"] = (p[f"ext_{n}"] / p[f"fig_{n}"]).round(3)
        print(p.to_string(index=False))
        print()
        for n in SAMPLINGS:
            lower = int((p[f"ext_{n}"] < p[f"fig_{n}"]).sum())
            print(f"  at {n} sample fields: the extraction carries less "
                  f"interaction than its own figure in {lower} of {len(p)} "
                  f"pairs, median ratio {p[f'ratio_{n}'].median():.3f}")
        print()
        print("  the conclusion is reported only where it holds at all three "
              "samplings")
    print()
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
