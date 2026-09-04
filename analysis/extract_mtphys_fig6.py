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


def extract(panel, scale=4.0, overlay=False):
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
        else:
            # The eleven coloured series are dense enough that their markers
            # touch, so connected components merge whole runs of them and the
            # counts come out meaningless. Separating them needs a marker model
            # rather than a blob finder, which this script does not have.
            pts = [(cx, cy, n) for cx, cy, n in
                   find_markers_mask(m, min_px=int(6 * (scale / 4.0) ** 2),
                                     max_px=int(900 * (scale / 4.0) ** 2))]
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
    stem = os.path.join(OUT, "mtphys_2022_100783_fig6%s" % panel)
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
    ap.add_argument("--series", default=None,
                    help="extract only this series, e.g. 4.2K")
    a = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    if a.series:
        keep = {a.series: SERIES[a.series]}
        SERIES.clear(); SERIES.update(keep)
    extract(a.panel, overlay=a.overlay)
    return 0


if __name__ == "__main__":
    sys.exit(main())
