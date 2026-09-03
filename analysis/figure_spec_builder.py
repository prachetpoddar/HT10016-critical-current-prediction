#!/usr/bin/env python3
"""
figure_spec_builder.py

Drafts a digitiser spec for every Jc figure it can find in a PDF, by measuring
the page rather than by being told about it.

Why this is a separate step. figure_digitizer.py needs a page, a crop, whether
each axis is logarithmic, and a colour for each series. Typing those by hand for
thirty papers is slow and, worse, is the point at which a mistake becomes
invisible: a wrong colour silently relabels an isotherm. Everything here is read
off the PDF, and the two things that cannot be are reported as candidates for a
person to confirm rather than guessed silently.

What is measured, in order:

  the figure       pages whose text carries a Jc or critical-current caption
  the frame        the outermost long dark rows and columns in the crop
  the axis type    logarithmic if the tick labels are a "10" span with a
                   superscript, linear if they are plain numbers
  the series       colours that occupy a meaningful number of pixels inside the
                   frame and are not grey
  the legend       a temperature label such as "4 K" inside the frame, paired
                   with the nearest coloured marker to its left

The legend pairing is the one inference here, and it is the one that would
silently mislabel an isotherm, so it is emitted with the pixel distance that
justified it and any series it could not pair is left with a null temperature
rather than a plausible one.

    python analysis/figure_spec_builder.py --pdf x.pdf --out-dir specs/
    python analysis/figure_spec_builder.py --dir arxiv_pdfs/ --out-dir specs/
"""
import argparse
import collections
import glob
import json
import math
import os
import re

import numpy as np

try:
    import pymupdf
except ImportError:
    pymupdf = None

CAPTION = re.compile(r"(?:FIG\.?|Figure|Fig\.)\s*([0-9]+)\s*[.:|]?\s*([^\n]{0,160})")
JC_CAP = re.compile(r"critical current|\bJ\s?c\b|\bjc\b", re.I)
TEMP_LABEL = re.compile(r"^\s*([0-9]{1,3}(?:\.[0-9]+)?)\s*K\s*$")
NUM = re.compile(r"^[-+]?[0-9]*\.?[0-9]+$")


def is_grey(rgb, tol=40):
    return max(rgb) - min(rgb) < tol



def _runs(mask_line, min_len):
    """Start,end of dark runs of at least min_len along a 1-D boolean line."""
    out, start = [], None
    for i, v in enumerate(mask_line):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_len:
                out.append((start, i - 1))
            start = None
    if start is not None and len(mask_line) - start >= min_len:
        out.append((start, len(mask_line) - 1))
    return out


def find_axes_boxes(arr, darkness=110, min_side=120, max_frac=0.92):
    """Locate plot frames anywhere on a rendered page.

    Guessing a crop from fixed page fractions fails whenever a figure is not
    where the guess put it, which on this corpus was 21 of 26 papers. A plot
    frame is instead found directly: long horizontal dark runs are paired with
    long vertical ones, and a pair is accepted only when all four edges are
    actually dark along the box they would form. Boxes that span almost the
    whole page are dropped, since those are page borders and table rules.
    """
    dark = arr.mean(axis=2) < darkness
    h, w = dark.shape
    hcand = []
    for y in range(h):
        for a, b in _runs(dark[y], min_side):
            hcand.append((y, a, b))
    vcand = []
    for x in range(w):
        for a, b in _runs(dark[:, x], min_side):
            vcand.append((x, a, b))
    def dedupe(c):
        c.sort()
        out = []
        for v in c:
            if out and abs(v[0] - out[-1][0]) <= 3 and abs(v[1] - out[-1][1]) <= 6:
                continue
            out.append(v)
        return out
    hcand, vcand = dedupe(hcand), dedupe(vcand)
    if not hcand or not vcand:
        return []
    boxes = []
    hcand.sort()
    vcand.sort()
    for i, (ytop, xa1, xb1) in enumerate(hcand):
        for (ybot, xa2, xb2) in hcand[i + 1:]:
            if ybot - ytop < min_side:
                continue
            x0 = max(xa1, xa2)
            x1 = min(xb1, xb2)
            if x1 - x0 < min_side:
                continue
            if (x1 - x0) > max_frac * w and (ybot - ytop) > max_frac * h:
                continue
            # A frame line is routinely broken by tick marks crossing it, by a
            # marker sitting on it, or by antialiasing, so require the column to
            # be dark over most of the box height rather than in one unbroken
            # run. Demanding contiguity missed a box whose left edge was split
            # into two segments by exactly this.
            def covered(x):
                if not (0 <= x < w):
                    return 0.0
                seg = dark[ytop:ybot + 1, max(0, x - 1):min(w, x + 2)].any(axis=1)
                return float(seg.mean())
            lcov = max(covered(x0 + dx) for dx in (-2, -1, 0, 1, 2))
            rcov = max(covered(x1 + dx) for dx in (-2, -1, 0, 1, 2))
            if lcov >= 0.85 and rcov >= 0.85:
                boxes.append((x0, x1, ytop, ybot))
    # keep the largest non-overlapping boxes
    boxes.sort(key=lambda b: -((b[1] - b[0]) * (b[3] - b[2])))
    kept = []
    for b in boxes:
        if all(not (b[0] < k[1] and k[0] < b[1] and b[2] < k[3] and k[2] < b[3])
               for k in kept):
            kept.append(b)
        if len(kept) >= 6:
            break
    return kept


def frame_of(arr, darkness=110, min_frac=0.55):
    dark = arr.mean(axis=2) < darkness
    h, w = dark.shape
    rows = np.where(dark.sum(axis=1) >= min_frac * w)[0]
    cols = np.where(dark.sum(axis=0) >= min_frac * h)[0]
    if len(rows) < 2 or len(cols) < 2:
        return None
    return int(cols[0]), int(cols[-1]), int(rows[0]), int(rows[-1])


def spans_in(page, rect):
    out = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                x0, y0, x1, y1 = sp["bbox"]
                if rect.x0 <= x0 <= rect.x1 and rect.y0 <= y0 <= rect.y1:
                    t = sp["text"].strip()
                    if t:
                        out.append((t, sp["bbox"]))
    return out


def axis_is_log(page, rect):
    """Log if a '10' span is followed by a superscript number."""
    sp = spans_in(page, rect)
    for t, bb in sp:
        if t != "10":
            continue
        for t2, bb2 in sp:
            if bb2 is bb:
                continue
            if NUM.match(t2) and 0 <= bb2[0] - bb[2] < 6 and bb2[1] < bb[1] + 2:
                return True
    return False


def series_colours(arr, frame, min_px=300, quant=24):
    x0, x1, y0, y1 = frame
    sub = arr[y0 + 4:y1 - 3, x0 + 4:x1 - 3].reshape(-1, 3)
    q = (sub // quant) * quant
    cnt = collections.Counter(map(tuple, q))
    out = []
    for col, n in cnt.most_common(40):
        if n < min_px:
            continue
        if min(col) > 200:            # background
            continue
        if is_grey(col):              # ink, frame, text
            continue
        out.append((list(int(c) for c in col), int(n)))
    return out


def legend_pairs(page, arr, frame, clip, scale):
    """Pair each 'N K' label inside the frame with the nearest colour to its left."""
    x0, x1, y0, y1 = frame
    rect = pymupdf.Rect(clip.x0 + x0 / scale, clip.y0 + y0 / scale,
                        clip.x0 + x1 / scale, clip.y0 + y1 / scale)
    pairs = []
    for t, bb in spans_in(page, rect):
        m = TEMP_LABEL.match(t)
        if not m:
            continue
        px = int((bb[0] - clip.x0) * scale)
        py = int(((bb[1] + bb[3]) / 2 - clip.y0) * scale)
        best, bestd = None, None
        for dx in range(4, 90):
            xx = px - dx
            if xx <= x0:
                break
            for dy in (-4, -2, 0, 2, 4):
                yy = py + dy
                if not (y0 < yy < y1):
                    continue
                c = arr[yy, xx]
                if min(c) > 200 or is_grey(c):
                    continue
                if best is None:
                    best, bestd = [int(v) for v in c], dx
                break
            if best:
                break
        pairs.append(dict(temperature_K=float(m.group(1)),
                          rgb=best, marker_distance_px=bestd))
    return pairs


def build(pdf, out_dir, dpi_scale=4.0):
    doc = pymupdf.open(pdf)
    stem = os.path.splitext(os.path.basename(pdf))[0]
    made = []
    for i, page in enumerate(doc):
        txt = page.get_text()
        caps = [(m.group(1), " ".join(m.group(2).split()))
                for m in CAPTION.finditer(txt) if JC_CAP.search(m.group(2))]
        if not caps:
            continue
        r = page.rect
        pix = page.get_pixmap(matrix=pymupdf.Matrix(dpi_scale, dpi_scale))
        full = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, 3).astype(np.int16)
        boxes = find_axes_boxes(full)
        if not boxes:
            continue
        # score each detected axes box by how many series colours it holds
        scored = []
        for bx in boxes:
            cols = series_colours(full, bx)
            scored.append((len(cols), (bx[1] - bx[0]) * (bx[3] - bx[2]), bx, cols))
        scored.sort(key=lambda t: (-t[0], -t[1]))
        n_col, _area, bx, cols = scored[0]
        if not cols:
            continue
        x0, x1, y0, y1 = bx
        # widen the crop so the axis tick labels come with it
        pad_x, pad_y = int(0.16 * (x1 - x0)), int(0.14 * (y1 - y0))
        cx0 = max(0, x0 - pad_x); cx1 = min(pix.width, x1 + int(0.04 * (x1 - x0)))
        cy0 = max(0, y0 - int(0.05 * (y1 - y0))); cy1 = min(pix.height, y1 + pad_y)
        clip_frac = [cx0 / pix.width, cy0 / pix.height, cx1 / pix.width, cy1 / pix.height]
        clip = pymupdf.Rect(r.x0 + clip_frac[0] * r.width, r.y0 + clip_frac[1] * r.height,
                            r.x0 + clip_frac[2] * r.width, r.y0 + clip_frac[3] * r.height)
        sub = full[cy0:cy1, cx0:cx1]
        subframe = (x0 - cx0, x1 - cx0, y0 - cy0, y1 - cy0)
        pairs = legend_pairs(page, sub, subframe, clip, dpi_scale)
        series, used = [], set()
        for p_ in pairs:
            if not p_["rgb"]:
                continue
            near, nd = None, 1e9
            for c, n in cols:
                d = sum((a - b) ** 2 for a, b in zip(c, p_["rgb"])) ** 0.5
                if d < nd:
                    near, nd = c, d
            if near and nd < 90 and tuple(near) not in used:
                used.add(tuple(near))
                series.append(dict(name="%gK" % p_["temperature_K"],
                                   temperature_K=p_["temperature_K"], rgb=near,
                                   tol=45, colour_match_distance=round(nd, 1),
                                   marker_distance_px=p_["marker_distance_px"]))
        unpaired = [dict(name=None, temperature_K=None, rgb=c, tol=45, pixels=n)
                    for c, n in cols if tuple(c) not in used]
        xr = pymupdf.Rect(clip.x0, clip.y0 + (clip.y1 - clip.y0) * 0.80, clip.x1, clip.y1 + 25)
        yr = pymupdf.Rect(clip.x0 - 40, clip.y0, clip.x0 + (clip.x1 - clip.x0) * 0.22, clip.y1)
        spec = dict(paper_id=os.path.basename(pdf), pdf=pdf, page=i + 1,
                    figure=caps[0][0], caption=caps[0][1][:140],
                    clip=[round(v, 4) for v in clip_frac], dpi_scale=dpi_scale,
                    inset=6, mask_text=True,
                    x=dict(log=axis_is_log(page, xr), label="field_T"),
                    y=dict(log=axis_is_log(page, yr), label="Jc_A_per_cm2"),
                    series=series, unpaired_colours=unpaired,
                    n_axes_boxes_on_page=len(boxes),
                    needs_review=(not series) or bool(unpaired))
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "%s_p%d_fig%s.json" % (stem, i + 1, caps[0][0]))
        json.dump(spec, open(path, "w"), indent=2)
        made.append((path, len(series), len(unpaired), spec["y"]["log"]))
    doc.close()
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf")
    ap.add_argument("--dir")
    ap.add_argument("--out-dir", default="analysis/reextraction_specs/auto")
    args = ap.parse_args()
    if pymupdf is None:
        raise SystemExit("pymupdf required")
    pdfs = [args.pdf] if args.pdf else sorted(glob.glob(os.path.join(args.dir, "*.pdf")))
    tot = ok = 0
    for p in pdfs:
        try:
            made = build(p, args.out_dir)
        except Exception as e:
            print("%-28s ERROR %s" % (os.path.basename(p)[:28], e))
            continue
        tot += 1
        if made:
            ok += 1
        if not made:
            print("%-28s no Jc figure with a detectable frame" % os.path.basename(p)[:28])
        for path, ns, nu, ylog in made:
            print("%-28s %-34s %d series, %d unpaired colours, y-log=%s"
                  % (os.path.basename(p)[:28], os.path.basename(path)[:34], ns, nu, ylog))
    print("\n%d PDFs, %d produced at least one draft spec" % (tot, ok))


if __name__ == "__main__":
    main()
