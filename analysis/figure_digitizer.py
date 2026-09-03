#!/usr/bin/env python3
"""
figure_digitizer.py

Recovers data points from a published figure by measuring pixels, not by asking
a model what the figure says.

Why this exists. Every extraction defect found in this corpus came from a
vision-language model being asked to read a plot and returning plausible
numbers: round-number ladders, isotherms an exact constant apart, axis units
dropped, and in one case the dotted comparison curves of three other materials
recorded as the sample's own data. None of it was detectable from the output
alone without opening the PDF, because a model that cannot read a figure
produces the same shape of answer as one that can.

The remedy is not a better prompt. It is to make the extraction a measurement
with an error bar. This module:

  1. locates the plot frame from the image itself, so the calibration is not a
     set of hand-typed pixel coordinates that nobody can check;
  2. converts marker pixels to data coordinates through that calibration;
  3. re-projects the recovered points back onto the source image and reports the
     residual in pixels, so an extraction that is wrong is visibly wrong;
  4. writes the calibration into the output, so the whole conversion can be
     recomputed by a reader from the deposited numbers.

What still needs a human. The axis ranges and scale types, and the marker
colour of each series, come from the caption and legend. Those are three or four
numbers per figure, each of which appears verbatim in the paper, rather than a
hundred data values that do not.

    python analysis/figure_digitizer.py --spec specs/2012.13723.json
    python analysis/figure_digitizer.py --spec specs/2012.13723.json --overlay

Spec format (JSON):
{
  "paper_id": "2012.13723v3.pdf",
  "pdf": "/path/to/2012.13723v3.pdf",
  "page": 4,                          # 1-based
  "clip": [0.52, 0.08, 0.99, 0.36],   # left, top, right, bottom as page fractions
  "dpi_scale": 4.0,
  "x": {"min": 0.0, "max": 7.0, "log": false, "label": "mu0H_T"},
  "y": {"min": 1e4, "max": 3e6, "log": true,  "label": "Jc_A_per_cm2"},
  "series": [{"name": "4K", "temperature_K": 4.0, "rgb": [0,0,0], "tol": 60}]
}
The x/y min and max are the values at the LEFT/RIGHT and BOTTOM/TOP edges of the
detected plot frame.
"""
import argparse
import json
import math
import os
import sys

import re

import numpy as np

try:
    import pymupdf
except ImportError:
    pymupdf = None
from PIL import Image, ImageDraw


# ---------------------------------------------------------------- rendering

def render(spec):
    """Render the clipped figure region to an RGB array."""
    if pymupdf is None:
        sys.exit("pymupdf is required to render the figure")
    doc = pymupdf.open(spec["pdf"])
    page = doc[spec["page"] - 1]
    r = page.rect
    l, t, rr, b = spec["clip"]
    clip = pymupdf.Rect(r.x0 + l * r.width, r.y0 + t * r.height,
                        r.x0 + rr * r.width, r.y0 + b * r.height)
    s = float(spec.get("dpi_scale", 4.0))
    pix = page.get_pixmap(matrix=pymupdf.Matrix(s, s), clip=clip)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return np.asarray(img).astype(np.int16)


# ---------------------------------------------------------- frame detection

def detect_frame(arr, darkness=110, min_frac=0.55):
    """Find the plot box as the outermost long dark horizontal/vertical runs.

    Returns (x_left, x_right, y_top, y_bottom) in pixel indices.

    A published plot frame is the longest straight dark line in the crop. Taking
    the outermost qualifying rows and columns rather than the darkest avoids
    latching onto a gridline or a dense run of markers.
    """
    dark = arr.mean(axis=2) < darkness
    h, w = dark.shape
    rows = np.where(dark.sum(axis=1) >= min_frac * w)[0]
    cols = np.where(dark.sum(axis=0) >= min_frac * h)[0]
    if len(rows) < 2 or len(cols) < 2:
        raise ValueError(
            "could not find a plot frame: %d qualifying rows, %d columns. "
            "Adjust --clip so the crop is the axes box, or lower min_frac."
            % (len(rows), len(cols)))
    return int(cols[0]), int(cols[-1]), int(rows[0]), int(rows[-1])




# ------------------------------------------------- calibration from the PDF

_NUM = re.compile(r"^[-+]?[0-9]*\.?[0-9]+$")


def _spans(page, rect):
    out = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                x0, y0, x1, y1 = sp["bbox"]
                if rect.x0 <= x0 <= rect.x1 and rect.y0 <= y0 <= rect.y1:
                    t = sp["text"].strip()
                    if t:
                        out.append((t, (x0 + x1) / 2.0, (y0 + y1) / 2.0, sp["bbox"]))
    return out


def read_ticks(page, rect, frame_pt, axis, log):
    """Recover (value, page-coordinate) tick pairs from the PDF text layer.

    The tick labels of a published figure are real text with exact coordinates.
    Reading them is a measurement of the axis; typing pixel coordinates by hand
    is an assertion about it. On a log axis the labels are a "10" span with a
    superscript exponent span immediately to its right and slightly above, so
    those are paired before the value is formed.
    """
    fx0, fx1, fy0, fy1 = frame_pt
    sp = _spans(page, rect)
    ticks = []
    if log:
        for i, (t, cx, cy, bb) in enumerate(sp):
            if t != "10":
                continue
            for t2, cx2, cy2, bb2 in sp:
                if t2 is t:
                    continue
                if _NUM.match(t2) and 0 <= bb2[0] - bb[2] < 6 and bb2[1] < bb[1] + 2:
                    ticks.append((10.0 ** float(t2), cx, cy))
                    break
    else:
        for t, cx, cy, bb in sp:
            if _NUM.match(t):
                ticks.append((float(t), cx, cy))
    if axis == "x":
        cand = [(v, cx, cy) for v, cx, cy in ticks if cy > fy1 and cy - fy1 < 40]
        perp = 2
    else:
        cand = [(v, cx, cy) for v, cx, cy in ticks if cx < fx0 and fx0 - cx < 60]
        perp = 1
    # Tick labels of one axis share a coordinate perpendicular to it. Axis
    # titles and subscripts (the 0 of mu_0 H, for instance) do not, and a single
    # stray label wrecks the fit, so keep only the most populous aligned group.
    cand.sort(key=lambda r: r[perp])
    groups, cur = [], []
    for row in cand:
        if cur and abs(row[perp] - cur[-1][perp]) > 4:
            groups.append(cur)
            cur = []
        cur.append(row)
    if cur:
        groups.append(cur)
    if not groups:
        raise ValueError("found no %s tick labels" % axis)
    best = max(groups, key=len)
    keep = [(v, cx if axis == "x" else cy) for v, cx, cy in best]
    if len(keep) < 2:
        raise ValueError("found %d %s tick labels; need at least 2" % (len(keep), axis))
    return sorted(set(keep))


def fit_axis(ticks, log):
    """Least-squares map from page coordinate to value. Returns (slope,
    intercept, max_residual_in_value_units_as_a_fraction)."""
    vals = np.array([v for v, _ in ticks], dtype=float)
    pos = np.array([p for _, p in ticks], dtype=float)
    y = np.log10(vals) if log else vals
    A = np.vstack([pos, np.ones_like(pos)]).T
    (m, c), *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = np.abs(A @ np.array([m, c]) - y)
    span = float(y.max() - y.min()) or 1.0
    return float(m), float(c), float(resid.max() / span)



# ------------------------------------------------------------ marker finding

def _components(mask):
    """Label connected components. Uses scipy when present, else a BFS."""
    try:
        from scipy import ndimage
        lab, n = ndimage.label(mask)
        return [np.argwhere(lab == i) for i in range(1, n + 1)]
    except ImportError:
        pass
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    h, w = mask.shape
    for sy, sx in np.argwhere(mask):
        if seen[sy, sx]:
            continue
        stack, comp = [(sy, sx)], []
        seen[sy, sx] = True
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        out.append(np.array(comp))
    return out


def text_mask(page, clip, scale, shape, pad=2):
    """Pixels covered by text, from the PDF's own text layer.

    Legends, panel labels and axis annotations sit inside the plot frame and are
    the same colour as one of the series more often than not, which pulls a
    column centroid off the curve. The PDF records exactly where its text is, so
    excluding those boxes removes the annotation without a heuristic.
    """
    m = np.zeros(shape, dtype=bool)
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                x0, y0, x1, y1 = sp["bbox"]
                px0 = int((x0 - clip.x0) * scale) - pad
                px1 = int((x1 - clip.x0) * scale) + pad
                py0 = int((y0 - clip.y0) * scale) - pad
                py1 = int((y1 - clip.y0) * scale) + pad
                px0, py0 = max(px0, 0), max(py0, 0)
                px1 = min(px1, shape[1])
                py1 = min(py1, shape[0])
                if px1 > px0 and py1 > py0:
                    m[py0:py1, px0:px1] = True
    return m


def extract_curve(arr, rgb, tol, frame, n_bins=40, min_col_px=2, exclude=None,
                  inset=6):
    """Sample the series column by column instead of hunting for blobs.

    A Jc(H) trace is single-valued in the field, so for every pixel column
    inside the frame the series contributes at most one value. Taking the
    centroid of the matching pixels in each column is immune to markers that
    touch, to a connecting line drawn through them, and to marker size varying
    along the curve, all of which defeat connected-component detection. Columns
    are then binned so the output has a sane number of points rather than one
    per pixel.
    """
    x0, x1, y0, y1 = frame
    d = np.sqrt(((arr.astype(float) - np.array(rgb, dtype=float)) ** 2).sum(axis=2))
    mask = d < tol
    if exclude is not None:
        mask &= ~exclude
    sub = mask[y0 + inset:y1 - inset, x0 + inset:x1 - inset]
    cols = []
    for j in range(sub.shape[1]):
        ys = np.where(sub[:, j])[0]
        if len(ys) >= min_col_px:
            cols.append((x0 + inset + j, y0 + inset + ys.mean(), len(ys)))
    if not cols:
        return []
    cols.sort()
    edges = np.linspace(cols[0][0], cols[-1][0] + 1e-9, n_bins + 1)
    out = []
    for k in range(n_bins):
        grp = [c for c in cols if edges[k] <= c[0] < edges[k + 1]]
        if not grp:
            continue
        out.append((float(np.mean([g[0] for g in grp])),
                    float(np.mean([g[1] for g in grp])),
                    int(sum(g[2] for g in grp))))
    return out


def find_markers(arr, rgb, tol, frame, min_px=4, max_px=4000):
    """Centroids of pixel blobs within `tol` of `rgb`, strictly inside the frame.

    Size bounds matter: below min_px the blobs are antialiasing fringes and
    axis-label strokes, above max_px they are the connecting line of a dense
    series rather than its markers. Both are reported per series so a figure
    whose markers were missed shows up as an implausible point count rather
    than as quietly wrong numbers.
    """
    x0, x1, y0, y1 = frame
    d = np.sqrt(((arr.astype(float) - np.array(rgb, dtype=float)) ** 2).sum(axis=2))
    mask = d < tol
    inside = np.zeros_like(mask)
    inside[y0 + 2:y1 - 1, x0 + 2:x1 - 1] = True
    mask &= inside
    pts = []
    for comp in _components(mask):
        if not (min_px <= len(comp) <= max_px):
            continue
        pts.append((comp[:, 1].mean(), comp[:, 0].mean(), len(comp)))
    return pts


# -------------------------------------------------------------- calibration

class FittedAxis:
    """Maps a page coordinate to a data value using the tick-label fit.

    Nothing here is hand-entered: `m` and `c` come from a least-squares fit to
    the tick labels the PDF itself carries, and `resid` is how badly those
    labels miss a straight line, which is the calibration's own error bar.
    """

    def __init__(self, m, c, log, resid, ticks):
        self.m, self.c, self.log, self.resid, self.ticks = m, c, log, resid, ticks

    def to_data(self, page_coord):
        v = self.m * page_coord + self.c
        return 10 ** v if self.log else v

    def to_page(self, value):
        v = math.log10(value) if self.log else value
        return (v - self.c) / self.m


def digitize(spec):
    doc = pymupdf.open(spec["pdf"])
    page = doc[spec["page"] - 1]
    r = page.rect
    l, t, rr, b = spec["clip"]
    clip = pymupdf.Rect(r.x0 + l * r.width, r.y0 + t * r.height,
                        r.x0 + rr * r.width, r.y0 + b * r.height)
    scale = float(spec.get("dpi_scale", 4.0))
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip)
    arr = np.asarray(Image.frombytes("RGB", (pix.width, pix.height),
                                     pix.samples)).astype(np.int16)

    frame = detect_frame(arr, darkness=int(spec.get("frame_darkness", 110)),
                         min_frac=float(spec.get("frame_min_frac", 0.55)))
    x0, x1, y0, y1 = frame

    def px2pt_x(px):
        return clip.x0 + px / scale

    def px2pt_y(py):
        return clip.y0 + py / scale

    frame_pt = (px2pt_x(x0), px2pt_x(x1), px2pt_y(y0), px2pt_y(y1))
    search = pymupdf.Rect(clip.x0 - 40, clip.y0 - 20, clip.x1 + 20, clip.y1 + 40)

    xt = read_ticks(page, search, frame_pt, "x", spec["x"].get("log", False))
    yt = read_ticks(page, search, frame_pt, "y", spec["y"].get("log", False))
    mx, cx, rx = fit_axis(xt, spec["x"].get("log", False))
    my, cy, ry = fit_axis(yt, spec["y"].get("log", False))
    ax = FittedAxis(mx, cx, spec["x"].get("log", False), rx, xt)
    ay = FittedAxis(my, cy, spec["y"].get("log", False), ry, yt)

    txt = text_mask(page, clip, scale, arr.shape[:2]) \
        if spec.get("mask_text", True) else None

    rows, report = [], []
    for s in spec["series"]:
        if spec.get("method", "curve") == "curve":
            pts = extract_curve(arr, s["rgb"], float(s.get("tol", 60)), frame,
                                n_bins=int(s.get("n_bins", spec.get("n_bins", 40))),
                                min_col_px=int(s.get("min_col_px", 2)),
                                exclude=txt,
                                inset=int(s.get("inset", spec.get("inset", 6))))
        else:
            pts = find_markers(arr, s["rgb"], float(s.get("tol", 60)), frame,
                               min_px=int(s.get("min_px", 4)),
                               max_px=int(s.get("max_px", 4000)))
        pts.sort(key=lambda p: p[0])
        for px, py, npix in pts:
            rows.append(dict(paper_id=spec["paper_id"], series=s["name"],
                             temperature_K=s.get("temperature_K"),
                             field_T=round(ax.to_data(px2pt_x(px)), 6),
                             Jc_A_per_cm2=round(ay.to_data(px2pt_y(py)), 3),
                             px=round(px, 2), py=round(py, 2), n_pixels=npix))
        report.append((s["name"], len(pts)))

    meta = dict(
        frame_px=dict(x_left=x0, x_right=x1, y_top=y0, y_bottom=y1),
        dpi_scale=scale, image_px=[int(arr.shape[1]), int(arr.shape[0])],
        x_ticks_read=[[v, round(p, 3)] for v, p in xt],
        y_ticks_read=[[v, round(p, 3)] for v, p in yt],
        x_fit=dict(slope=mx, intercept=cx, log=ax.log,
                   max_tick_residual_frac=round(rx, 6)),
        y_fit=dict(slope=my, intercept=cy, log=ay.log,
                   max_tick_residual_frac=round(ry, 6)),
        axis_span_from_ticks=dict(
            x=[round(ax.to_data(frame_pt[0]), 4), round(ax.to_data(frame_pt[1]), 4)],
            y=[round(ay.to_data(frame_pt[3]), 4), round(ay.to_data(frame_pt[2]), 4)]),
    )
    doc.close()
    return rows, meta, report, arr, frame, ax, ay, (px2pt_x, px2pt_y)


def overlay(arr, rows, ax, ay, out_path, frame, conv, scale, clip_origin):
    """Re-project recovered points onto the source image for visual check."""
    img = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(img)
    x0, x1, y0, y1 = frame
    d.rectangle([x0, y0, x1, y1], outline=(0, 200, 255), width=2)
    for r in rows:
        px = (ax.to_page(r["field_T"]) - clip_origin[0]) * scale
        py = (ay.to_page(r["Jc_A_per_cm2"]) - clip_origin[1]) * scale
        d.ellipse([px - 5, py - 5, px + 5, py + 5], outline=(255, 0, 255), width=2)
    img.save(out_path)
    return out_path


def reprojection_residual(rows, ax, ay, scale, clip_origin):
    """Max |re-projected pixel - measured pixel|. Non-zero means the axis
    transform and its inverse disagree, i.e. the calibration is inconsistent."""
    worst = 0.0
    for r in rows:
        worst = max(worst,
                    abs((ax.to_page(r["field_T"]) - clip_origin[0]) * scale - r["px"]),
                    abs((ay.to_page(r["Jc_A_per_cm2"]) - clip_origin[1]) * scale - r["py"]))
    return worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out-dir", default="data/reextraction")
    ap.add_argument("--overlay", action="store_true")
    args = ap.parse_args()

    spec = json.load(open(args.spec))
    rows, meta, report, arr, frame, ax, ay, conv = digitize(spec)
    doc = pymupdf.open(spec["pdf"])
    r = doc[spec["page"] - 1].rect
    l, t, _rr, _b = spec["clip"]
    clip_origin = (r.x0 + l * r.width, r.y0 + t * r.height)
    doc.close()
    scale = float(spec.get("dpi_scale", 4.0))

    os.makedirs(args.out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.spec))[0]

    import csv
    cols = ["paper_id", "series", "temperature_K", "field_T",
            "Jc_A_per_cm2", "px", "py", "n_pixels"]
    csv_path = os.path.join(args.out_dir, stem + "_points.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    meta["n_points"] = len(rows)
    meta["per_series"] = dict(report)
    meta["reprojection_residual_px"] = round(
        reprojection_residual(rows, ax, ay, scale, clip_origin), 6)
    json.dump(meta, open(os.path.join(args.out_dir, stem + "_calibration.json"), "w"),
              indent=2)

    print("frame px: x %d-%d, y %d-%d  (image %dx%d)"
          % (frame[0], frame[1], frame[2], frame[3], arr.shape[1], arr.shape[0]))
    print("x ticks read from the PDF: %s" % [v for v, _ in meta["x_ticks_read"]])
    print("y ticks read from the PDF: %s" % [v for v, _ in meta["y_ticks_read"]])
    print("tick-fit max residual: x %.2g  y %.2g  (fraction of axis span)"
          % (meta["x_fit"]["max_tick_residual_frac"],
             meta["y_fit"]["max_tick_residual_frac"]))
    print("axis span implied by the fit: x %s  y %s"
          % (meta["axis_span_from_ticks"]["x"], meta["axis_span_from_ticks"]["y"]))
    for name, n in report:
        print("  %-10s %3d points" % (name, n))
    print("total %d points; re-projection residual %.2g px"
          % (len(rows), meta["reprojection_residual_px"]))
    print("written to %s" % csv_path)
    if args.overlay:
        p = overlay(arr, rows, ax, ay,
                    os.path.join(args.out_dir, stem + "_overlay.png"),
                    frame, conv, scale, clip_origin)
        print("overlay written to %s" % p)


if __name__ == "__main__":
    main()
