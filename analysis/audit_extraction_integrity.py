#!/usr/bin/env python3
"""
audit_extraction_integrity.py

Tests whether each per-paper extraction contains values that were plausibly read
off a figure, or values that were generated.

Why this exists. The record for 10.1016/j.mtphys.2022.100783 carried two sample
forms whose Jc series were the same numbers one grid step apart: 35 of its 40
polycrystal points shared an (H, Jc) pair with a single-crystal point, and seven
of eight downstream fits were bit-identical between the two forms. The recorded
polycrystal Jc was also an order of magnitude above what that paper states. That
is not a reading error, so the question is not "is this value slightly wrong"
but "was this series read at all", and that question has to be asked of every
extraction rather than of the one that happened to be checked.

The tests are internal. None of them needs the source PDF, which matters because
the corpus is 2.8 GB of PDFs and a per-paper read is the expensive step; this
narrows which papers are worth that read.

Six signatures, in rough order of how hard they are to explain innocently:

  duplicate_series    Two series in one file have an identical Jc tuple. Two
                      different samples, or one sample at two temperatures,
                      producing the same numbers to full precision does not
                      happen in measured data.

  arithmetic          Jc falls in exactly equal absolute steps across four or
                      more points. Jc(H) is convex on a log axis over any real
                      field range, so equal absolute steps are the signature of
                      a generated ramp, most clearly when the field spacing is
                      itself uneven (0, 1, 10, 20, 50 T).

  log_ladder          log10(Jc) falls in exactly equal steps across four or more
                      points. This is the same defect as arithmetic expressed on
                      the axis a Jc(H) figure is actually drawn on, and the
                      linear test cannot see it: a series at 10^6.5, 10^6.0,
                      10^5.5, 10^5.0, 10^4.5 has five different absolute steps
                      and one log step. A constant factor per point requires the
                      factor to be independent of how far the field moved, so
                      the signature is strongest, and here is only reported, when
                      the field spacing is uneven.

  shifted_series      Two series differ by a constant offset at every point.
                      One series copied and displaced.

  round_saturation    Fraction of Jc values that are exactly one significant
                      figure. Chance is about 0.1. Coarse digitization against
                      gridlines can raise this legitimately, so on its own it is
                      a flag and not a finding; it is reported as a number and
                      only counts toward a verdict above 0.9 with enough points.

  grid_quantized      All Jc values in a series are integer multiples of a
                      common step that is large relative to the series range.

  field_implausible   Field values beyond the record's own recorded Hc2, or a
                      non-monotonic Jc(H) at fixed temperature.

Verdicts. FAIL means at least one signature that measured data does not produce:
a duplicated series, a shifted series, or an arithmetic run. CHECK means
round-number saturation or grid quantization heavy enough to be worth a PDF
read. PASS means nothing fired, which is evidence of nothing beyond the absence
of these particular defects.

    python audit_extraction_integrity.py --dir <extraction folder>
    python audit_extraction_integrity.py --dir <folder> --csv audit/extraction_integrity.csv
"""
import argparse, csv, glob, math, os
from collections import defaultdict

MIN_SERIES = 4          # points needed before sequence tests mean anything
ROUND_FAIL = 0.90       # round fraction that counts toward a verdict on its own
ROUND_CHECK = 0.50
MIN_N_FOR_ROUND = 8


def one_sig_fig(v):
    if v <= 0:
        return False
    e = math.floor(math.log10(v))
    m = v / 10 ** e
    return abs(m - round(m)) < 1e-9


def load(path):
    """Return (rows, columns) or (None, None) if this is not a Jc long table."""
    try:
        with open(path, newline="") as fh:
            rd = csv.DictReader(fh)
            cols = rd.fieldnames or []
            rows = list(rd)
    except Exception:
        return None, None
    if not rows or "Jc_A_per_cm2" not in cols:
        return None, None
    return rows, cols


def series_of(rows):
    """Group into measurement series keyed by (sample_form, sample_id, T)."""
    g = defaultdict(list)
    for r in rows:
        try:
            h = float(r.get("field_T", "nan"))
            j = float(r["Jc_A_per_cm2"])
        except (TypeError, ValueError):
            continue
        if not (j > 0) or math.isnan(h):
            continue
        key = (r.get("sample_form", ""), r.get("sample_id", "") or r.get("notes", ""),
               r.get("temperature_K", ""))
        g[key].append((h, j))
    return {k: sorted(v) for k, v in g.items() if v}


def is_arithmetic(jc):
    if len(jc) < MIN_SERIES:
        return False
    d = [round(jc[i + 1] - jc[i], 6) for i in range(len(jc) - 1)]
    return len(set(d)) == 1 and d[0] != 0


def log_ladder(pts):
    """Exactly equal log10(Jc) steps against uneven field spacing.

    Returns (step, n) or None. Uneven field spacing is required because an
    evenly sampled field axis over a short range can give near-equal log steps
    from a genuine exponential decay, whereas a constant factor per point across
    intervals of 4.5 T and 25 T cannot be read off any real curve.
    """
    if len(pts) < MIN_SERIES:
        return None
    h = [x for x, _j in pts]
    lj = [math.log10(j) for _h, j in pts]
    d = [round(lj[i + 1] - lj[i], 4) for i in range(len(lj) - 1)]
    if len(set(d)) != 1 or abs(d[0]) < 1e-9:
        return None
    hs = [round(h[i + 1] - h[i], 4) for i in range(len(h) - 1)]
    if len(set(hs)) == 1:
        return None
    return d[0], len(pts)


def grid_step(jc):
    """Largest step g such that every value is an integer multiple of g.

    Reported relative to the series range, so a series spanning 1e5 whose values
    are all multiples of 1e4 scores 0.1 and one on a 1e5 grid scores 1.0.
    """
    ints = [int(round(v)) for v in jc]
    g = 0
    for v in ints:
        g = math.gcd(g, abs(v))
    rng = max(jc) - min(jc)
    if g == 0 or rng == 0:
        return 0, 0.0
    return g, g / rng


def non_monotonic(pts):
    """Count field-ordered points where Jc rises. One rise can be real (a peak
    effect); several across a series is a reading or generation defect."""
    return sum(1 for i in range(len(pts) - 1) if pts[i + 1][1] > pts[i][1] * 1.001)


def audit_file(path):
    rows, cols = load(path)
    name = os.path.basename(path)
    if rows is None:
        return None
    ser = series_of(rows)

    vals = [float(r["Jc_A_per_cm2"]) for r in rows
            if _f(r.get("Jc_A_per_cm2")) and float(r["Jc_A_per_cm2"]) > 0]
    round_frac = (sum(1 for v in vals if one_sig_fig(v)) / len(vals)) if vals else 0.0

    findings = []
    # duplicated and shifted series
    keys = sorted(ser)
    for i, a in enumerate(keys):
        ja = tuple(j for _h, j in ser[a])
        for b in keys[i + 1:]:
            jb = tuple(j for _h, j in ser[b])
            if len(ja) != len(jb) or len(ja) < MIN_SERIES:
                continue
            if ja == jb:
                findings.append(("duplicate_series", "%s == %s" % (_k(a), _k(b))))
                continue
            diffs = {round(x - y, 6) for x, y in zip(ja, jb)}
            if len(diffs) == 1 and abs(next(iter(diffs))) > 0:
                findings.append(("shifted_series", "%s = %s %+g" %
                                 (_k(a), _k(b), next(iter(diffs)))))

    for k, pts in ser.items():
        jc = [j for _h, j in pts]
        if is_arithmetic(jc):
            findings.append(("arithmetic", "%s step %+g over %d pts"
                             % (_k(k), jc[1] - jc[0], len(jc))))
        lad = log_ladder(pts)
        if lad:
            findings.append(("log_ladder", "%s step %+.4f dex over %d pts, "
                             "uneven field spacing" % (_k(k), lad[0], lad[1])))
        if len(jc) >= MIN_SERIES:
            g, rel = grid_step(jc)
            if rel >= 0.20:
                findings.append(("grid_quantized", "%s all multiples of %g "
                                 "(%.0f%% of range)" % (_k(k), g, 100 * rel)))
        nm = non_monotonic(pts)
        if nm >= 2:
            findings.append(("non_monotonic", "%s %d rises with field" % (_k(k), nm)))

    # field range against the record's own Hc2
    hc2 = set()
    for r in rows:
        if _f(r.get("hc2_T")):
            hc2.add(float(r["hc2_T"]))
    if len(hc2) == 1:
        h0 = next(iter(hc2))
        hi = max((float(r["field_T"]) for r in rows if _f(r.get("field_T"))), default=0)
        if h0 > 0 and hi > h0:
            findings.append(("field_beyond_hc2", "max H %g T exceeds recorded Hc2 %g T"
                             % (hi, h0)))

    kinds = {k for k, _ in findings}
    # Tier A: two series carrying identical numbers. No measurement produces it.
    # Tier B: an exact arithmetic run of five or more, or a series that is
    #         another series plus a constant at every point. Both are shapes of
    #         generated data; neither survives a plausible reading of a figure.
    # Tier C: round-number saturation and grid quantization. Coarse digitization
    #         against gridlines can produce these, so they mark a file for a PDF
    #         read rather than condemning it.
    tier_a = "duplicate_series" in kinds
    tier_b = any(k == "shifted_series" for k, _ in findings) or \
        any(k == "arithmetic" and int(d.rsplit(" ", 2)[-2]) >= 5
            for k, d in findings if k == "arithmetic") or \
        "log_ladder" in kinds
    tier_c = (round_frac >= ROUND_FAIL and len(vals) >= MIN_N_FOR_ROUND) or \
        "grid_quantized" in kinds
    if tier_a or tier_b:
        verdict = "FAIL"
    elif tier_c or round_frac >= ROUND_CHECK or "non_monotonic" in kinds or \
            "field_beyond_hc2" in kinds:
        verdict = "CHECK"
    else:
        verdict = "PASS"
    tier = "A" if tier_a else "B" if tier_b else "C" if tier_c else ""

    return dict(file=name, tier=tier,
                route=("vision" if "VISION_PASS" in name else "named"),
                n_points=len(vals), n_series=len(ser), round_frac=round_frac,
                verdict=verdict, n_findings=len(findings),
                kinds=" ".join(sorted(kinds)), findings=findings)


def _f(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def _k(k):
    form, sid, t = k
    sid = (sid or "")[:18]
    return "%s/%s/T=%s" % (form or "?", sid or "?", t or "?")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    results = []
    for p in sorted(glob.glob(os.path.join(args.dir, "*.csv"))):
        r = audit_file(p)
        if r:
            results.append(r)

    order = {"FAIL": 0, "CHECK": 1, "PASS": 2}
    results.sort(key=lambda r: (order[r["verdict"]], -r["round_frac"]))

    print("%-4s %-4s %-6s %5s %4s %6s  %s"
          % ("", "tier", "route", "pts", "ser", "round", "file"))
    for r in results:
        print("%-4s %-4s %-6s %5d %4d %6.2f  %s"
              % (r["verdict"][:4], r["tier"], r["route"], r["n_points"],
                 r["n_series"], r["round_frac"], r["file"][:64]))

    counts = defaultdict(int)
    for r in results:
        counts[r["verdict"]] += 1
    print("\n%d files: %d FAIL, %d CHECK, %d PASS"
          % (len(results), counts["FAIL"], counts["CHECK"], counts["PASS"]))
    for route in ("vision", "named"):
        sub = [r for r in results if r["route"] == route]
        if sub:
            f = sum(1 for r in sub if r["verdict"] == "FAIL")
            print("   %-6s route: %2d files, %2d FAIL, median round fraction %.2f"
                  % (route, len(sub), f,
                     sorted(r["round_frac"] for r in sub)[len(sub) // 2]))

    if not args.quiet:
        print("\nfindings, worst first\n")
        for r in results:
            if r["verdict"] == "PASS":
                continue
            print("%s  %s" % (r["verdict"], r["file"]))
            for kind, detail in r["findings"][:8]:
                print("     %-18s %s" % (kind, detail))
            if len(r["findings"]) > 8:
                print("     ... %d more" % (len(r["findings"]) - 8))
            if not r["findings"]:
                print("     %-18s %.2f of %d values are one significant figure"
                      % ("round_saturation", r["round_frac"], r["n_points"]))
            print()

    if args.csv:
        os.makedirs(os.path.dirname(args.csv) or ".", exist_ok=True)
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["file", "route", "verdict", "tier", "n_points", "n_series",
                        "round_fraction", "signatures", "detail"])
            for r in results:
                w.writerow([r["file"], r["route"], r["verdict"], r["tier"], r["n_points"],
                            r["n_series"], "%.4f" % r["round_frac"], r["kinds"],
                            " | ".join("%s: %s" % kv for kv in r["findings"])])
        print("written to %s" % args.csv)


if __name__ == "__main__":
    main()
