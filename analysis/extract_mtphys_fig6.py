"""
extract_mtphys_fig6.py

Digitise Fig. 6 of 10.1016/j.mtphys.2022.100783, both panels, from the
publisher PDF.

Why this is a script of its own rather than a spec for
analysis/figure_digitizer.py. That tool locates the plot box as the outermost
long dark lines in the crop, which assumes the crop is the axes box. This figure
breaks the assumption: its legend is drawn on top of the frame's right edge and
extends past it, so a crop tight enough to exclude the legend cuts the frame and
a crop wide enough to hold the legend makes the legend's own borders the
outermost long lines. The detector then returns two adjacent columns near the
left edge and calls that the plot box, which is a silent wrong answer rather
than a refusal. The frame here is therefore measured with the panel's geometry
stated explicitly and checked, rather than discovered.

Everything else follows the same discipline: the calibration comes from measured
tick positions, the conversion is written out with the points, the recovered
points are re-projected onto the source image, and an overlay is produced so a
reader can see whether the extraction sits on the curves.

What a human supplies, and it is the same three or four numbers the tool asks
for: the value at the first and last major tick on each axis, read off the
printed figure.

    python3 analysis/extract_mtphys_fig6.py --panel b --overlay
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

try:
    import pymupdf
except ImportError:
    pymupdf = None

PDF = ("/mnt/user-data/uploads/SuperconductorWorkflow/kappa_pipeline/analysis/"
       "v3_2_9_path_2_prep/phase_3_p19_elsevier_pdfs/"
       "10.1016_j.mtphys.2022.100783.pdf")
PAGE = 6
OUT = os.path.join("data", "reextraction")

# left, top, right, bottom as fractions of the page
CLIP = {"a": [0.0800, 0.0726, 0.4200, 0.2581],
        "b": [0.5577, 0.0726, 0.8930, 0.2581]}

# The two numbers per axis a human reads off the figure. The y axis is the one
# that matters for the anchor: panel (a) is decades 1e3 to 1e6 and panel (b) is
# 1e3 to 1e5, and that single decade is the whole defect being corrected.
AXES = {"a": dict(x_first=1.0, x_last=7.0, y_bottom=1e3, y_top=1e6),
        "b": dict(x_first=1.0, x_last=7.0, y_bottom=1e3, y_top=1e5)}

SERIES = {
    "4.2K": (4.2, [0, 0, 0]),        "6K":  (6.0,  [180, 21, 52]),
    "8K":   (8.0, [27, 9, 179]),     "10K": (10.0, [61, 134, 115]),
    "12K":  (12.0, [173, 43, 166]),  "14K": (14.0, [149, 162, 50]),
    "16K":  (16.0, [27, 17, 99]),    "17K": (17.0, [78, 8, 16]),
    "18K":  (18.0, [205, 61, 122]),  "19K": (19.0, [13, 111, 64]),
    "20K":  (20.0, [19, 4, 106]),    "21K": (21.0, [206, 135, 56]),
}


def render(panel, scale=4.0):
    if pymupdf is None:
        sys.exit("pymupdf is required")
    doc = pymupdf.open(PDF)
    page = doc[PAGE - 1]
    r = page.rect
    l, t, rr, b = CLIP[panel]
    clip = pymupdf.Rect(r.x0 + l * r.width, r.y0 + t * r.height,
                        r.x0 + rr * r.width, r.y0 + b * r.height)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img


def column_runs(ink, arr, x_left, x_right, y_top, y_bot, min_run=2, merge=10):
    """Every vertical run of marker ink in each column, with its mean colour.

    A run is one symbol's cross-section, or two overlapping symbols of the same
    curve. Runs are the unit the tracer works in, because a run is a thing the
    image actually contains, whereas "the point of series k in column j" is a
    thing the extractor has to decide.
    """
    out = {}
    for j in range(x_left + 2, x_right - 1):
        col = np.nonzero(ink[:, j])[0]
        if not len(col):
            continue
        runs, grp = [], [col[0]]
        for y in col[1:]:
            # An open symbol crosses a column as TWO thin runs, its upper and
            # its lower arc, with white between them. Splitting on a two-pixel
            # gap therefore returns two runs per marker, and the tracer follows
            # the top edge and the bottom edge as two different curves that
            # keep swapping. Merging across the symbol height puts them back
            # together.
            if y - grp[-1] > merge:
                if len(grp) >= min_run:
                    runs.append(grp)
                grp = []
            grp.append(y)
        if len(grp) >= min_run:
            runs.append(grp)
        made = []
        for g in runs:
            px = arr[g, j]
            # The ink of an open symbol is its outline; its interior is white,
            # and averaging the run gives grey whatever colour the symbol is.
            # Six of the first tracks came back at [102, 102, 102] for exactly
            # that reason. Take the most chromatic quarter instead.
            chroma = px.max(axis=1) - px.min(axis=1)
            k = max(1, len(px) // 4)
            sel = px[np.argsort(-chroma)[:k]]
            made.append((float(np.mean(g)), len(g), sel.mean(axis=0)))
        out[j] = made
    return out


def trace(runs, x_left, x_right, max_jump=6.0, min_len=40, max_gap=6):
    """Follow each curve from the right edge leftwards, run to run.

    Colour discrimination fails on this figure: three of the twelve series are
    dark blues whose printed values differ by a few units, and clustering the
    ink returns the blends rather than the inks. Continuity does not care. The
    curves are ordered and non-crossing over most of the field range, and they
    are widely separated at the right edge where each ends, so a track started
    there and extended one column at a time stays on its own curve. Colour is
    then used once, on the whole track, to say which temperature it is, which
    is a far easier question than asking it of a single pixel.
    """
    # One pass per column, not per run, so a track is extended at most once in
    # a column. Matching run by run lets two runs of different curves both
    # claim the same track in a crowded column, and the track then jumps
    # between curves; the greedy pairing below gives each track its closest
    # unclaimed run and leaves the rest to start their own.
    cols = sorted([j for j in runs], reverse=True)
    tracks = []
    for j in cols:
        pairs = []
        for ri, (y, n, c) in enumerate(runs[j]):
            for ti, t in enumerate(tracks):
                gap = t["last_col"] - j
                if gap <= 0 or gap > max_gap:
                    continue
                # Predict where this track should be, from its own recent
                # slope. A fixed window around the last y breaks every curve
                # into fragments on the steep left-hand side, which is what the
                # first version did: 46 tracks, none spanning the axis.
                pred = t["y"] + t["slope"] * (-gap)
                tol = max_jump + abs(t["slope"]) * gap
                d = abs(pred - y)
                if d <= tol:
                    pairs.append((d, ri, ti))
        pairs.sort()
        used_r, used_t = set(), set()
        for d, ri, ti in pairs:
            if ri in used_r or ti in used_t:
                continue
            used_r.add(ri)
            used_t.add(ti)
            y, n, c = runs[j][ri]
            t = tracks[ti]
            prev_y, prev_col = t["y"], t["last_col"]
            t["pts"].append((float(j), y, n))
            t["cols"].append(c)
            step = (y - prev_y) / max(1, prev_col - j)
            t["slope"] = 0.7 * t["slope"] + 0.3 * (-step)
            t["y"] = y
            t["last_col"] = j
        for ri, (y, n, c) in enumerate(runs[j]):
            if ri not in used_r:
                tracks.append(dict(pts=[(float(j), y, n)], cols=[c], y=y,
                                   last_col=j, slope=0.0))
    return stitch([t for t in tracks if len(t["pts"]) >= 8], min_len=min_len)


def _endslope(pts, k=12):
    """Slope in rows per column at the low-column end of a track."""
    p = sorted(pts)[:k]
    if len(p) < 3:
        return 0.0
    x = np.array([q[0] for q in p]); y = np.array([q[1] for q in p])
    return float(np.polyfit(x, y, 1)[0])


def stitch(tracks, min_len=40, max_gap=40, tol=10.0, colour_tol=70.0):
    """Join track fragments that continue one another.

    A single tracing pass fragments: a marker missing from a few columns, or
    two curves brushing past each other, ends a track and starts another, and
    on this figure that left less than half the plotted data in tracks long
    enough to use. Fragments of one curve are recognisable, though. They are
    adjacent in x, they continue each other's slope, and they are the same
    colour. Joining on all three is what a single pass cannot do, because at
    the moment a track breaks there is nothing yet to join it to.
    """
    tracks = [dict(t) for t in tracks]
    for t in tracks:
        t["pts"] = sorted(t["pts"])
        t["x0"], t["x1"] = t["pts"][0][0], t["pts"][-1][0]
        t["rgb"] = np.median(np.array(t["cols"]), axis=0)
    changed = True
    while changed:
        changed = False
        tracks.sort(key=lambda t: -len(t["pts"]))
        for a in tracks:
            if a.get("dead"):
                continue
            best, bd = None, None
            for b in tracks:
                if b is a or b.get("dead"):
                    continue
                gap = a["x0"] - b["x1"]
                if not (0 < gap <= max_gap):
                    continue
                if np.abs(a["rgb"] - b["rgb"]).sum() > colour_tol:
                    continue
                pred = a["pts"][0][1] + _endslope(a["pts"]) * (-gap)
                d = abs(pred - b["pts"][-1][1])
                if d <= tol + 0.5 * gap and (bd is None or d < bd):
                    best, bd = b, d
            if best is not None:
                a["pts"] = sorted(a["pts"] + best["pts"])
                a["cols"] = a["cols"] + best["cols"]
                a["x0"] = a["pts"][0][0]
                a["rgb"] = np.median(np.array(a["cols"]), axis=0)
                best["dead"] = True
                changed = True
    return [t for t in tracks
            if not t.get("dead") and len(t["pts"]) >= min_len]


def traced_series(arr, frame, lx0, ly1):
    """Trace every curve, then name each trace by its colour. STAGED, NOT DONE.

    Status, so the next person does not repeat the four models that failed.

      * a per-series colour tolerance returned about 650 points for each of the
        twelve series, which is one curve twelve times;
      * connected components merged whole runs of markers, because the symbols
        touch, and the size bound then dropped the merged blobs;
      * a topmost-run-per-column rule is right only for the topmost curve and
        strung readings across several curves for the other eleven;
      * a median-row-per-column rule with nearest-colour assignment follows the
        curves broadly but loses the three dark blues into each other, whose
        printed inks differ by a few units, and left the 20 K series with four
        points.

    What is here now traces runs by continuity and stitches the fragments, and
    it recovers long tracks: several span most of the axis. It is still not
    good enough to deposit. Fragments remain, the run-merge height trades
    fragmentation against fusing two adjacent curves, and a third of the traces
    come back grey because the ink they captured is an anti-aliased blend
    rather than a symbol outline.

    What it needs is a marker model: the symbols are squares, circles,
    triangles and diamonds of a known size, so matching a template per series
    would separate curves that a colour test and a continuity test both lose.
    That is the next thing to build, and it is why this returns nothing unless
    asked.
    """
    x_left, x_right, y_top, y_bot = frame
    ink = arr.max(axis=2) < 215
    ink[:y_top + 2] = False
    ink[y_bot - 1:] = False
    ink[:, :x_left + 2] = False
    ink[:, x_right - 1:] = False
    ink[y_top:int(ly1), int(lx0):] = False
    runs = column_runs(ink, arr, x_left, x_right, y_top, y_bot, merge=10)
    tracks = trace(runs, x_left, x_right, max_gap=12)
    tracks.sort(key=lambda t: -len(t["pts"]))

    # name each track by its nearest legend colour, one series per track
    pal = {k: np.array(v[1], dtype=float) for k, v in SERIES.items()}
    out, taken = {}, set()
    for t in tracks:
        best, bd = None, None
        for k, c in pal.items():
            if k in taken:
                continue
            d = float(np.abs(t["rgb"] - c).sum())
            if bd is None or d < bd:
                best, bd = k, d
        if best is None:
            break
        taken.add(best)
        out[best] = [(p[0], p[1], p[2]) for p in t["pts"]]
    return out


def _despike(pts, win=21, tol_px=9.0):
    """Drop readings that disagree with their neighbours along the curve.

    A misassigned pixel puts a reading on a different curve, and a single one
    is invisible in a table of six hundred. Against a rolling median of the
    same series it is not: a curve is smooth on the scale of a few columns and
    an intruder is not. Points that survive are reported; the count of those
    dropped is reported too, because a series losing most of its readings here
    means the colour assignment failed rather than that the curve is noisy.
    """
    if len(pts) < 5:
        return pts
    pts = sorted(pts)
    ys = np.array([p[1] for p in pts], dtype=float)
    n = len(ys)
    half = max(2, win // 2)
    med = np.array([np.median(ys[max(0, i - half):min(n, i + half + 1)])
                    for i in range(n)])
    keep = np.abs(ys - med) <= tol_px
    return [p for p, k in zip(pts, keep) if k]


def find_markers_mask(mask, min_px=6, max_px=900):
    """Centroids of connected blobs in a boolean mask, with size bounds.

    The same rule analysis/figure_digitizer.find_markers uses, taking a mask
    rather than a colour so it can be fed the nearest-colour assignment above.
    """
    from scipy import ndimage
    lab, n = ndimage.label(mask, structure=np.ones((3, 3), dtype=bool))
    if not n:
        return []
    out = []
    for sl, i in zip(ndimage.find_objects(lab), range(1, n + 1)):
        comp = (lab[sl] == i)
        size = int(comp.sum())
        if not (min_px <= size <= max_px):
            continue
        ys, xs = np.nonzero(comp)
        out.append((float(xs.mean() + sl[1].start),
                    float(ys.mean() + sl[0].start), size))
    return out


def frame_and_ticks(arr):
    """The plot box, and the major tick columns along its bottom edge.

    The box is taken as the leftmost full-height dark column and the outermost
    full-width dark rows, then the right edge as the last column reaching 70% of
    the box height. Major ticks are the long inward marks; minors are half as
    long and are dropped, and the majors are then required to be evenly spaced
    to 2%, which is what catches a curve pixel read as a tick.
    """
    g = arr.mean(axis=2)
    h, w = g.shape
    dark = g < 190
    rows = [i for i in range(h) if dark[i].mean() > 0.70]
    if len(rows) < 2:
        sys.exit("no horizontal frame lines found")
    y_top, y_bot = rows[0], rows[-1]
    colf = dark[y_top:y_bot + 1].mean(axis=0)
    cols = [j for j in range(w) if colf[j] > 0.70]
    if len(cols) < 2:
        sys.exit("no vertical frame lines found")
    x_left, x_right = cols[0], cols[-1]

    inner = g[y_bot - 16:y_bot - 1, :] < 110
    length = inner.sum(axis=0)
    runs, cur = [], []
    for j in range(x_left + 2, x_right - 1):
        if length[j] >= 4:
            cur.append(j)
        elif cur:
            runs.append((sum(cur) / len(cur), int(max(length[c] for c in cur))))
            cur = []
    if cur:
        runs.append((sum(cur) / len(cur), int(max(length[c] for c in cur))))
    if not runs:
        sys.exit("no tick marks found along the bottom axis")
    longest = max(r[1] for r in runs)
    majors = [p for p, L in runs if L >= 0.75 * longest]
    if len(majors) < 3:
        sys.exit("fewer than three major ticks found")
    # Fit a lattice rather than walking the list. A single spurious tick, a
    # curve pixel that happens to reach as far inward as a real mark, breaks a
    # forward walk at the first bad gap and takes every later tick with it: on
    # this panel that left three "majors" at 123.5, 215.5 and 291.5, of which
    # the third is the intruder and the two after it are real. Choosing the
    # largest evenly spaced subset instead is immune to that.
    diffs = np.diff(majors)
    step = float(np.median([d for d in diffs
                            if abs(d - np.median(diffs)) <= 0.35 * np.median(diffs)]))
    best = []
    for anchor in majors:
        cand = [p for p in majors
                if abs(((p - anchor) / step) - round((p - anchor) / step))
                <= 0.12]
        # one tick per lattice site, the closest
        site = {}
        for p in cand:
            k = int(round((p - anchor) / step))
            if k not in site or abs(p - (anchor + k * step)) < abs(site[k] - (anchor + k * step)):
                site[k] = p
        cand = [site[k] for k in sorted(site)]
        if len(cand) > len(best):
            best = cand
    keep = best
    if len(keep) < 4:
        sys.exit("fewer than four evenly spaced major ticks: %s" % keep)
    steps = np.diff(keep)
    if (steps.std() / steps.mean()) > 0.02:
        sys.exit("major ticks are not evenly spaced to 2 per cent: %s" % keep)
    dropped = [p for p in majors if p not in keep]
    if dropped:
        print("   dropped %d tick(s) off the lattice: %s"
              % (len(dropped), [round(x, 1) for x in dropped]))
    return (x_left, x_right, y_top, y_bot), keep, float(steps.mean())


def extract(panel, scale=4.0, overlay=False, spec_tol_px=9.0,
            use_trace=False):
    img = render(panel, scale)
    arr = np.asarray(img).astype(int)
    frame, majors, step = frame_and_ticks(arr)
    x_left, x_right, y_top, y_bot = frame
    ax = AXES[panel]
    n = len(majors) - 1
    per_major = (ax["x_last"] - ax["x_first"]) / n
    if abs(per_major - round(per_major, 6)) > 1e-9 and abs(per_major - 1.0) > 1e-6:
        print("   note: implied step per major tick is %.6f" % per_major)

    def x_of(px):
        return ax["x_first"] + (px - majors[0]) / step * per_major

    dec = np.log10(ax["y_top"]) - np.log10(ax["y_bottom"])

    def y_of(py):
        return 10 ** (np.log10(ax["y_top"]) - (py - y_top) / (y_bot - y_top) * dec)

    # the legend, as a fraction of the box, excluded from every series
    lx0 = x_left + 0.62 * (x_right - x_left)
    ly1 = y_top + 0.62 * (y_bot - y_top)

    # Assign every pixel to its NEAREST series colour rather than testing each
    # series against a tolerance of its own. With twelve series on one axis the
    # per-series test is hopeless: a tolerance loose enough to catch a series
    # through its anti-aliased edges also catches its neighbours, and the first
    # run of this script returned about 650 points for every one of the twelve,
    # which is the same curve twelve times. Nearest-colour assignment makes the
    # series mutually exclusive by construction, and the distance cut then only
    # has to separate marker ink from the white ground.
    traced = {}
    if use_trace:
        traced = traced_series(arr, frame, lx0, ly1)

    rows, report = [], []
    mx, mn = arr.max(axis=2), arr.min(axis=2)
    names = list(SERIES)
    pal = np.array([SERIES[n][1] for n in names])
    flat = arr.reshape(-1, 3)
    dist = np.linalg.norm(flat[:, None, :] - pal[None, :, :], axis=2)
    nearest = dist.argmin(axis=1).reshape(arr.shape[:2])
    best = dist.min(axis=1).reshape(arr.shape[:2])
    ink = (best < 90) & (mx < 235)
    for name, (temp, rgb) in SERIES.items():
        idx = names.index(name)
        m = ink & (nearest == idx)
        if rgb == [0, 0, 0]:
            m &= (mx < 110) & ((mx - mn) < 45)
        m[:y_top + 2] = False
        m[y_bot - 1:] = False
        m[:, :x_left + 2] = False
        m[:, x_right - 1:] = False
        m[y_top:int(ly1), int(lx0):] = False
        # One centroid per marker, not one reading per column. Taking the
        # topmost run in each column latches onto whatever anti-aliased pixel
        # of a neighbouring curve happened to be assigned to this series, and
        # the overlay showed exactly that: red readings strung across several
        # curves at once, and a line of them along the top frame. A marker is a
        # connected blob, so find the blobs.
        if rgb == [0, 0, 0]:
            # 4.2 K is the topmost curve in both panels and the only
            # unsaturated dark series, so it separates from the other eleven
            # without any colour reasoning, and the topmost run in each column
            # is unambiguously its marker. This is the series the critical
            # current anchor is read from.
            pts = []
            for j in range(x_left + 2, x_right - 1):
                col = np.nonzero(m[:, j])[0]
                if len(col) < 2:
                    continue
                grp = [col[0]]
                for y in col[1:]:
                    if y - grp[-1] > 8:
                        break
                    grp.append(y)
                pts.append((float(j), (grp[0] + grp[-1]) / 2.0, len(grp)))
        elif use_trace:
            pts = traced.get(name, [])
        else:
            # One reading per column, from the median row of this series' own
            # pixels in that column.
            #
            # Two earlier models failed here and are worth naming. Connected
            # components merge whole runs of markers, because the symbols touch
            # on a dense curve, so the counts came out meaningless. A
            # topmost-run rule reads whatever sits highest in the column, which
            # is only ever right for the topmost curve and strung readings
            # across several curves for the other eleven.
            #
            # An open symbol contributes its outline to a column, so the median
            # row of that outline is the symbol's centre, and where consecutive
            # symbols overlap in one column the median stays on the curve
            # because they sit at almost the same height. What this cannot fix
            # is a pixel assigned to the wrong series, so the readings are then
            # required to agree with their own neighbours.
            pts = []
            for j in range(x_left + 2, x_right - 1):
                col = np.nonzero(m[:, j])[0]
                if len(col) < int(3 * (scale / 4.0)):
                    continue
                pts.append((float(j), float(np.median(col)), int(len(col))))
            pts = _despike(pts, win=int(21 * (scale / 4.0)) | 1,
                           tol_px=float(spec_tol_px))
        pts.sort()
        for px, py, npix in pts:
            rows.append(dict(paper_id="10.1016/j.mtphys.2022.100783",
                             panel="Fig. 6(%s)" % panel, series=name,
                             temperature_K=temp,
                             field_T=round(float(x_of(px)), 6),
                             Jc_A_per_cm2=round(float(y_of(py)), 3),
                             px=round(float(px), 2), py=round(float(py), 2),
                             n_pixels=int(npix)))
        report.append((name, len(pts)))

    meta = dict(paper_id="10.1016/j.mtphys.2022.100783", page=PAGE,
                panel="Fig. 6(%s)" % panel, pdf=os.path.basename(PDF),
                clip=CLIP[panel], dpi_scale=scale,
                image_px=[int(arr.shape[1]), int(arr.shape[0])],
                frame_px=dict(x_left=x_left, x_right=x_right,
                              y_top=y_top, y_bottom=y_bot),
                major_tick_px=[round(float(p), 2) for p in majors],
                px_per_major=round(step, 4),
                implied_step_per_major=round(per_major, 6),
                axes_supplied=ax,
                axis_span_from_frame=dict(
                    x=[round(float(x_of(x_left)), 4),
                       round(float(x_of(x_right)), 4)],
                    y=[ax["y_bottom"], ax["y_top"]]),
                n_points=len(rows),
                per_series={k: v for k, v in report})

    os.makedirs(OUT, exist_ok=True)
    # The staged tracer must not be able to overwrite the deposited extraction.
    # It already did once in testing, replacing a validated 478-point 4.2 K
    # series with 340 traced points of uncertain identity, and nothing but the
    # console output said so.
    stem = os.path.join(OUT, "mtphys_2022_100783_fig6%s%s"
                        % (panel, "_staged" if use_trace else ""))
    import csv
    with open(stem + "_points.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    json.dump(meta, open(stem + "_calibration.json", "w"), indent=1)

    if overlay:
        ov = img.copy()
        d = ImageDraw.Draw(ov)
        d.rectangle([x_left, y_top, x_right, y_bot], outline=(0, 160, 255), width=2)
        for p in majors:
            d.line([(p, y_bot), (p, y_bot - 22)], fill=(0, 160, 255), width=2)
        for r in rows:
            x, y = r["px"], r["py"]
            d.ellipse([x - 2, y - 2, x + 2, y + 2], outline=(255, 0, 0))
        ov.save(stem + "_overlay.png")
    print("panel %s: frame %s, %d major ticks %.2f px apart" % (panel, frame,
                                                               len(majors), step))
    print("   x span of the box: %.3f to %.3f" % (x_of(x_left), x_of(x_right)))
    for k, v in report:
        print("   %-6s %4d points" % (k, v))
    print("   written %s_points.csv, _calibration.json%s"
          % (stem, ", _overlay.png" if overlay else ""))
    return rows, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", choices=["a", "b"], default="b")
    ap.add_argument("--overlay", action="store_true")
    ap.add_argument("--trace", action="store_true",
                    help="use the staged curve tracer for the coloured series. "
                         "Not deposit quality; see traced_series().")
    ap.add_argument("--series", default=None,
                    help="extract only this series, e.g. 4.2K")
    a = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    if a.series:
        keep = {a.series: SERIES[a.series]}
        SERIES.clear(); SERIES.update(keep)
    extract(a.panel, overlay=a.overlay, use_trace=a.trace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
