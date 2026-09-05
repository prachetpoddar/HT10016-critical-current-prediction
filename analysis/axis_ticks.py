#!/usr/bin/env python3
"""
axis_ticks.py

Reads an axis from its tick marks alone: whether it is logarithmic or linear,
and what one decade or one unit is worth in pixels.

Why this replaces reading the labels. The earlier calibration paired a "10" text
span with its superscript to decide a log axis, which needs the labels to be
selectable text and correctly ordered. On this corpus that failed on several
papers and, worse, silently returned "linear" for a log axis, which is a
calibration error that produces plausible numbers.

Tick geometry does not need any of that. A linear axis places its ticks at equal
spacing. A logarithmic axis places minor ticks at log10(2), log10(3) ... within
each decade, so the gaps within a decade fall as 0.301, 0.176, 0.125, 0.097,
0.079, 0.067, 0.058, 0.051, 0.046 of the decade and then reset. That descending
sawtooth is unmistakable and it is visible in pixels with no text at all.

What this buys, and where it stops. For the fitted exponents the absolute scale
is irrelevant. beta_T is the slope of log Jc against log(1 - T/Tc), so scaling
every Jc by any constant shifts only the intercept; measured on 266 re-extracted
points, beta_T is identical to ten decimal places under scale factors of 1e3,
1e-4 and 7.3. beta_H behaves the same way under a scale on the field as long as
the critical field carries the same scale. So for exponents a log axis needs
only its pixels-per-decade, which is tick spacing, and nothing else.

The exception is the anchor layer. log10_Jc_anchor is an absolute quantity and
the variance decomposition compares it across papers, so a per-paper scale error
moves it by log10(k) and does corrupt that result. Anchors still need one
labelled value; exponents do not.

Measured on this corpus. The minor-gap ratio comes out at 6.57 on the log field
axis of 1002.0208 FIG. 5(b) against a predicted 6.5, and at exactly 1.00 on the
linear field axes of 2012.13723 FIG. 4 and 2207.06629 Figure 4, with major-tick
uniformity of 0.003 or better in all three. The discriminator is clean where the
ticks are.

Where it still fails: a y axis with data curves running close to it. The tick
length measurement walks inward from the frame edge until it leaves dark pixels,
so a curve passing near the axis extends what looks like a tick and breaks the
major/minor split. Those axes report kind "unknown" rather than guessing.

    python analysis/axis_ticks.py --pdf x.pdf --page 4
"""
import argparse
import math

import numpy as np

try:
    import pymupdf
except ImportError:
    pymupdf = None

# fractional positions of the decade ticks 1..10 on a log axis
LOG_FRACS = [math.log10(n) for n in range(1, 11)]
LOG_GAPS = np.diff(LOG_FRACS)


def find_ticks(dark, frame, side, min_len=6, max_len=60, direction="inward"):
    """Tick positions along one side of the frame, in pixels.

    A tick is a short dark run perpendicular to the axis, starting at the frame
    edge. Requiring it to start at the edge is what separates ticks from
    gridlines and from data.

    `direction` says which way the ticks point. Published figures do it both
    ways and the choice is not cosmetic: a detector that only walks inward
    finds nothing at all on an outward-ticked axis, which is how this returned
    two frame corners and no ticks on Fig. 6(c) of jallcom.2023.170384.

      "inward"   walk into the plot area. The original behaviour, and the
                 default, so every existing call is unchanged.
      "outward"  walk away from the plot area, into the margin.
      "auto"     try inward, and fall back to outward when inward finds fewer
                 than three ticks. Which one produced the answer is returned by
                 find_ticks_dir, so the choice is visible rather than silent.

    Outward walking has one hazard inward walking does not: the axis label text
    sits in the margin, so `max_len` must stay short enough not to run into it.
    The default of 60 px at dpi_scale 4 is about 3.75 pt, well inside the gap.
    """
    if direction == "auto":
        return find_ticks_dir(dark, frame, side, min_len, max_len)[0]
    if direction not in ("inward", "outward"):
        raise ValueError("direction must be inward, outward or auto")
    out = _walk(dark, frame, side, min_len, max_len, direction)
    return out


def find_ticks_dir(dark, frame, side, min_len=6, max_len=60, min_ticks=3,
                   direction="auto"):
    """find_ticks over both directions, returning (ticks, direction_used).

    direction="auto" walks inward first and only falls back to outward when
    inward finds fewer than min_ticks. That rule fails on an axis whose data
    curves reach the frame: on Fig. 3 of 0806.2839v1 the inward walk finds
    exactly three long runs, all of them curve, which is enough to stop the
    fallback, while the outward walk finds the six decade ticks with a spacing
    uniformity of 0.003. Naming the direction in the spec settles it, so pass
    "inward" or "outward" when auto picks the wrong one.
    """
    if direction in ("inward", "outward"):
        return _walk(dark, frame, side, min_len, max_len, direction), direction
    inw = _walk(dark, frame, side, min_len, max_len, "inward")
    if len(inw) >= min_ticks:
        return inw, "inward"
    outw = _walk(dark, frame, side, min_len, max_len, "outward")
    if len(outw) > len(inw):
        return outw, "outward"
    return inw, "inward"


def _walk(dark, frame, side, min_len, max_len, direction):
    x0, x1, y0, y1 = frame
    flip = -1 if direction == "outward" else 1
    pos = []
    if side in ("bottom", "top"):
        edge = y1 if side == "bottom" else y0
        step = (-1 if side == "bottom" else 1) * flip
        for x in range(x0 + 1, x1):
            n = 0
            for k in range(1, max_len):
                yy = edge + step * k
                if not (0 <= yy < dark.shape[0]) or not dark[yy, x]:
                    break
                n += 1
            if n >= min_len:
                pos.append((x, n))
    else:
        edge = x0 if side == "left" else x1
        step = (1 if side == "left" else -1) * flip
        for y in range(y0 + 1, y1):
            n = 0
            for k in range(1, max_len):
                xx = edge + step * k
                if not (0 <= xx < dark.shape[1]) or not dark[y, xx]:
                    break
                n += 1
            if n >= min_len:
                pos.append((y, n))
    # collapse runs of adjacent columns/rows into one tick at their centre
    out, cur = [], []
    for p, n in pos:
        if cur and p - cur[-1][0] > 3:
            out.append((float(np.mean([c[0] for c in cur])), max(c[1] for c in cur)))
            cur = []
        cur.append((p, n))
    if cur:
        out.append((float(np.mean([c[0] for c in cur])), max(c[1] for c in cur)))
    return out


def classify(ticks, tol=0.16):
    """Decide linear or log from tick spacing, and return the scale.

    Returns a dict with `kind`, and for log the pixels per decade, for linear
    the pixels per tick interval. `score` is the mean relative disagreement
    between the observed gaps and the model, so a caller can refuse a bad fit
    instead of trusting it.
    """
    if len(ticks) < 4:
        return dict(kind="unknown", reason="fewer than 4 ticks", n_ticks=len(ticks))
    p = np.array([t[0] for t in ticks], dtype=float)
    gaps = np.diff(p)
    if gaps.min() <= 0:
        return dict(kind="unknown", reason="non-monotonic ticks", n_ticks=len(p))

    # linear: all gaps equal
    lin = float(np.abs(gaps - gaps.mean()).mean() / gaps.mean())

    # log: gaps should repeat the descending decade pattern. Try every offset
    # into the pattern, since a figure rarely starts exactly at a decade.
    # Pixel rows increase downward, so a y axis runs from high value to low and
    # its decade pattern is the mirror of an x axis's. Both directions are tried
    # rather than assuming one; assuming forward silently classified every log y
    # axis in this corpus as linear.
    best_log, best_off, per_dec, best_dir = 1e9, None, None, None
    for direction, pattern in (("increasing", LOG_GAPS), ("decreasing", LOG_GAPS[::-1])):
        for off in range(9):
            model = np.array([pattern[(off + i) % 9] for i in range(len(gaps))])
            scale = float((gaps / model).mean())
            err = float(np.abs(gaps - model * scale).mean() / gaps.mean())
            if err < best_log:
                best_log, best_off, per_dec, best_dir = err, off, scale, direction

    if lin <= best_log and lin < tol:
        return dict(kind="linear", px_per_tick=float(gaps.mean()),
                    score=round(lin, 4), n_ticks=len(p),
                    first_tick_px=float(p[0]), last_tick_px=float(p[-1]))
    if best_log < lin and best_log < tol:
        return dict(kind="log", px_per_decade=round(per_dec, 3),
                    direction=best_dir, pattern_offset=best_off,
                    score=round(best_log, 4),
                    n_ticks=len(p), first_tick_px=float(p[0]),
                    last_tick_px=float(p[-1]))
    return dict(kind="unknown", reason="neither model fits",
                linear_score=round(lin, 4), log_score=round(best_log, 4),
                n_ticks=len(p))




def classify_by_length(ticks, min_majors=3):
    """Split ticks into major and minor by length, then read the axis from the
    minor spacing inside one major interval.

    This is more reliable than fitting the whole tick sequence to a pattern,
    because it needs only the ticks between two consecutive long ones and does
    not care how the figure's range happens to align with the decades.

    The discriminator is the ratio of the first minor gap to the last within an
    interval. A log decade runs 0.301, 0.176 ... 0.046 of the interval, so that
    ratio is about 6.5. Any linear subdivision has equal gaps, so it is 1. There
    is no realistic axis in between, which is why this separates cleanly where
    fitting the full sequence did not.

    Returns kind, and for a log axis the pixels per decade taken directly from
    the major spacing.
    """
    if len(ticks) < 4:
        return dict(kind="unknown", reason="fewer than 4 ticks", n_ticks=len(ticks))
    pos = np.array([t[0] for t in ticks], float)
    ln = np.array([t[1] for t in ticks], float)
    # The frame corners run the full height of the box and saturate the length
    # measurement, which drags a midpoint split up until only the corners count
    # as major. Drop lengths far above the median first, then split at the
    # largest gap in the surviving lengths rather than at their midpoint.
    med = float(np.median(ln))
    keep = ln <= max(3.0 * med, med + 4)
    pos, ln = pos[keep], ln[keep]
    if len(pos) < 4:
        return dict(kind="unknown", reason="too few ticks after dropping corners",
                    n_ticks=len(ticks))
    uniq = np.array(sorted(set(ln.tolist())), float)
    if len(uniq) < 2:
        return dict(kind="unknown", reason="all ticks the same length",
                    n_ticks=int(len(pos)))
    gi = int(np.argmax(np.diff(uniq)))
    cut = (uniq[gi] + uniq[gi + 1]) / 2.0
    maj = pos[ln >= cut]
    if len(maj) < min_majors or ln.max() - ln.min() < 3:
        return dict(kind="unknown", reason="no clear major/minor split",
                    n_ticks=len(ticks), n_major=int(len(maj)))
    gaps_major = np.diff(maj)
    if gaps_major.min() <= 0:
        return dict(kind="unknown", reason="bad major spacing", n_ticks=len(ticks))
    major_uniform = float(np.abs(gaps_major - gaps_major.mean()).mean() / gaps_major.mean())

    ratios = []
    for a, b in zip(maj[:-1], maj[1:]):
        mn = sorted(p_ for p_ in pos[ln < cut] if a < p_ < b)
        if len(mn) < 4:
            continue
        g = np.diff([a] + mn + [b])
        if g.min() <= 0:
            continue
        ratios.append(float(g[0] / g[-1]))
    if not ratios:
        return dict(kind="unknown", reason="no interval with enough minor ticks",
                    n_ticks=len(ticks), n_major=int(len(maj)),
                    major_spacing_px=round(float(gaps_major.mean()), 2),
                    major_uniformity=round(major_uniform, 4))
    r = float(np.median(ratios))
    kind = "log" if r > 2.5 else ("linear" if r < 1.6 else "unknown")
    out = dict(kind=kind, n_ticks=len(ticks), n_major=int(len(maj)),
               minor_first_over_last=round(r, 2),
               major_spacing_px=round(float(gaps_major.mean()), 2),
               major_uniformity=round(major_uniform, 4),
               n_intervals_used=len(ratios),
               major_positions=[float(x) for x in maj],
               minor_positions=[float(x) for x in pos[ln < cut]],
               n_minor_per_interval=int(round(
                   float(np.median([len([1 for p_ in pos[ln < cut] if a < p_ < b])
                                    for a, b in zip(maj[:-1], maj[1:])])))))
    if kind == "log":
        out["px_per_decade"] = round(float(gaps_major.mean()), 3)
    elif kind == "linear":
        out["px_per_major"] = round(float(gaps_major.mean()), 3)
    else:
        out["reason"] = "minor gap ratio %.2f is between the log and linear cases" % r
    return out



def uniform_majors(ticks, min_ticks=4, max_uniformity=0.02):
    """Find the major ticks of an evenly divided axis, by tick length.

    Why a search over length thresholds rather than a major/minor split. On this
    corpus the tick set is contaminated: the frame corners saturate the length
    measurement, a data curve running to the frame edge reads as a long tick,
    and legend markers sitting on the axis read as short ones. A single
    midpoint split between "long" and "short" therefore lands in the wrong place
    on most figures. What survives contamination is that the *major* ticks of an
    evenly divided axis are equally spaced, so every length threshold is tried
    and the one whose surviving ticks are most evenly spaced is taken, provided
    it clears an absolute uniformity bar.

    Returns None when no threshold qualifies. Refusing is the point: a guessed
    axis scale reproduces the failure this whole module exists to remove.
    """
    if len(ticks) < min_ticks:
        return None
    pos = np.array([t[0] for t in ticks], float)
    ln = np.array([t[1] for t in ticks], float)
    med = float(np.median(ln))
    keep = ln <= max(3.0 * med, med + 4)          # drop the frame corners
    pos, ln = pos[keep], ln[keep]
    best = None
    for thr in sorted(set(ln.tolist())):
        sel = pos[ln >= thr]
        if len(sel) < min_ticks:
            continue
        g = np.diff(np.sort(sel))
        if g.min() <= 0:
            continue
        u = float(np.abs(g - g.mean()).mean() / g.mean())
        if best is None or u < best["uniformity"]:
            best = dict(length_threshold=float(thr), n_major=int(len(sel)),
                        positions=[float(x) for x in np.sort(sel)],
                        spacing_px=float(g.mean()), uniformity=round(u, 5))
    if best is None or best["uniformity"] > max_uniformity:
        return None
    return best


def ratio_between(px_a, px_b, axis):
    """Ratio of the two values at these pixel positions. Log only, no origin."""
    if axis["kind"] != "log":
        raise ValueError("ratios without an origin need a log axis")
    return 10 ** ((px_b - px_a) / axis["px_per_decade"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--page", type=int, required=True)
    ap.add_argument("--scale", type=float, default=4.0)
    args = ap.parse_args()
    import sys
    sys.path.insert(0, "analysis")
    from figure_spec_builder import find_axes_boxes

    doc = pymupdf.open(args.pdf)
    page = doc[args.page - 1]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(args.scale, args.scale))
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height, pix.width, 3).astype(np.int16)
    dark = arr.mean(axis=2) < 110
    for bi, box in enumerate(find_axes_boxes(arr)):
        print("box %d: px x%d-%d y%d-%d" % (bi, box[0], box[1], box[2], box[3]))
        for side in ("bottom", "left"):
            ticks = find_ticks(dark, box, side)
            print("   %-7s %2d ticks" % (side, len(ticks)))
            print("       by length : %s" % classify_by_length(ticks))
            print("       by pattern: %s" % classify(ticks))
    doc.close()


if __name__ == "__main__":
    main()
