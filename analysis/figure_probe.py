#!/usr/bin/env python3
"""
figure_probe.py

Report everything a digitiser spec needs, for one crop of one page, in one call.

Building a spec by hand meant guessing the clip, running the digitiser, reading
whichever of its several refusals came first, changing one number and running
again. That is four or five round trips per figure and there are a dozen figures
left. This does the measuring instead: it reports the detected frame at several
darkness thresholds, the tick candidates on all four sides in both directions
with their spacing, and the exact marker colours present, so the spec can be
written once.

It asserts nothing about the axes. The two values per axis still come off the
printed page, and the overlay is still the check.

    python3 analysis/figure_probe.py --pdf x.pdf --page 6 --clip 0.1 0.5 0.5 0.8
"""
import argparse
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, "analysis")
import pymupdf
from PIL import Image

import figure_digitizer as fd
import axis_ticks as at


def probe(pdf, page_no, clip, scale=4.0, save=None):
    doc = pymupdf.open(pdf)
    page = doc[page_no - 1]
    r = page.rect
    l, t, rr, b = clip
    c = pymupdf.Rect(r.x0 + l * r.width, r.y0 + t * r.height,
                     r.x0 + rr * r.width, r.y0 + b * r.height)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=c)
    arr = np.asarray(Image.frombytes("RGB", (pix.width, pix.height),
                                     pix.samples)).astype(np.int16)
    if save:
        Image.fromarray(arr.astype(np.uint8)).save(save)
    print("crop %dx%d px" % (arr.shape[1], arr.shape[0]))

    frames = {}
    for dk in (110, 150, 170, 190):
        for mf in (0.42, 0.55, 0.70):
            for op in (False, True):
                try:
                    f = fd.detect_frame(arr, darkness=dk, min_frac=mf, open_frame=op)
                except ValueError:
                    continue
                if f[1] - f[0] > 50 and f[3] - f[2] > 50:
                    frames.setdefault(f, []).append((dk, mf, op))
    if not frames:
        print("NO FRAME at any threshold; widen or narrow the clip")
        return
    print("\nframes found (widest first):")
    for f, cfg in sorted(frames.items(), key=lambda kv: -(kv[0][1]-kv[0][0])*(kv[0][3]-kv[0][2]))[:3]:
        print("   %s  w=%d h=%d   from %s" % (f, f[1]-f[0], f[3]-f[2], cfg[:3]))
    frame = max(frames, key=lambda f: (f[1]-f[0])*(f[3]-f[2]))

    print("\nticks on frame %s:" % (frame,))
    for side in ("bottom", "top", "left", "right"):
        best = None
        for dk in (110, 130, 150, 170, 190):
            dark = arr.mean(axis=2) < dk
            for ml in (5, 6, 8, 10):
                tk, used = at.find_ticks_dir(dark, frame, side, min_len=ml)
                for mu in (0.02, 0.05, 0.12):
                    m = at.uniform_majors(tk, min_ticks=3, max_uniformity=mu)
                    if m and len(m["positions"]) >= 3:
                        cand = (len(m["positions"]), dk, ml, mu, used,
                                float(np.mean(np.diff(m["positions"]))),
                                [round(p, 1) for p in m["positions"]])
                        if best is None or cand[0] > best[0]:
                            best = cand
                        break
        if best:
            n, dk, ml, mu, used, step, pos = best
            print("   %-6s %d majors  step %.1f px  (darkness %d, min_len %d, "
                  "uniformity %.2f, %s)\n            %s"
                  % (side, n, step, dk, ml, mu, used, pos))
        else:
            print("   %-6s none" % side)

    flat = arr.reshape(-1, 3).astype(int)
    inside = arr[frame[2]:frame[3], frame[0]:frame[1]].reshape(-1, 3).astype(int)
    sat = inside[(inside.max(1) - inside.min(1)) > 45]
    print("\nmarker colours inside the frame (exact, most common first):")
    for cc, n in Counter(map(tuple, sat)).most_common(8):
        if n >= 8:
            print("   %-16s %d px" % (str(cc), n))
    dk = inside[(inside.max(1) < 90)]
    print("   near-black %d px" % len(dk))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--page", type=int, required=True)
    ap.add_argument("--clip", nargs=4, type=float, required=True)
    ap.add_argument("--scale", type=float, default=4.0)
    ap.add_argument("--save")
    a = ap.parse_args()
    probe(a.pdf, a.page, a.clip, a.scale, a.save)
    return 0


if __name__ == "__main__":
    sys.exit(main())
