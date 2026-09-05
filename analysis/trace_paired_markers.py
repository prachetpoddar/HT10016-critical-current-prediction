#!/usr/bin/env python3
"""
trace_paired_markers.py

Digitise a figure whose isotherms come in filled/open pairs of the same colour.

Fig. 3 of physc.2010.05.048 draws ten isotherms as five colours, each colour
carrying a filled marker for the even temperature and an open one for the odd:
2 K filled and 3 K open in dark red, 4 K and 5 K in orange, and so on. Colour
alone cannot separate a pair, and the spec-driven digitiser matches on colour.

What separates them is order. The isotherms never cross, so within one colour
the upper branch at every field is the colder member. This walks each colour
column by column, splits the matching pixels into an upper and a lower cluster
wherever both are present, and assigns the colder temperature to the upper one.
Where only one cluster is present the column is dropped rather than guessed.

The axis calibration is taken from figure_digitizer, so the two routes share one
calibration and only the pixel selection differs.

    python3 analysis/trace_paired_markers.py --spec specs/<name>.json

Run from the repository root.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, "analysis")
import figure_digitizer as fd


def clusters(rows, gap=6):
    """Split a sorted array of row indices into runs separated by more than gap."""
    out, cur = [], [rows[0]]
    for r in rows[1:]:
        if r - cur[-1] > gap:
            out.append(cur)
            cur = []
        cur.append(r)
    out.append(cur)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out-dir", default="data/reextraction")
    args = ap.parse_args()
    spec = json.load(open(args.spec))

    rows_, meta, report, arr, frame, ax, ay, conv = fd.digitize(spec)
    px2pt_x, px2pt_y = conv
    x0, x1, y0, y1 = frame
    grey = arr.mean(axis=2)

    pairs = spec["paired_series"]
    out = []
    for p in pairs:
        rgb = np.array(p["rgb"], float)
        tol = float(p.get("tol", 70))
        d = np.sqrt(((arr.astype(float) - rgb) ** 2).sum(axis=2))
        m = d < tol
        ins = int(p.get("inset", 8))
        m[:y0 + ins, :] = False
        m[y1 - ins:, :] = False
        m[:, :x0 + ins] = False
        m[:, x1 - ins:] = False
        for box in spec.get("exclude_boxes", []) + p.get("exclude_boxes", []):
            l_, t_, r_, b_ = box
            h_, w_ = arr.shape[:2]
            m[int(t_ * h_):int(b_ * h_), int(l_ * w_):int(r_ * w_)] = False
        nb = int(p.get("n_bins", 34))
        edges = np.linspace(x0, x1, nb + 1)
        for i in range(nb):
            cols = range(int(edges[i]), int(edges[i + 1]))
            rr = np.where(m[:, list(cols)].any(axis=1))[0]
            if len(rr) == 0:
                continue
            cl = clusters(rr)
            cl = [c for c in cl if len(c) >= int(p.get("min_run", 2))]
            if len(cl) != 2:
                continue
            px = float(np.mean([edges[i], edges[i + 1]]))
            for c, name, T in ((cl[0], p["upper"], p["upper_T"]),
                               (cl[1], p["lower"], p["lower_T"])):
                py = float(np.mean(c))
                out.append(dict(paper_id=spec["paper_id"], series=name,
                                temperature_K=T,
                                field_T=round(ax.to_data(px2pt_x(px)), 6),
                                Jc_A_per_cm2=round(ay.to_data(px2pt_y(py)), 3),
                                px=round(px, 2), py=round(py, 2),
                                n_pixels=len(c)))

    import csv
    stem = os.path.splitext(os.path.basename(args.spec))[0]
    path = os.path.join(args.out_dir, stem + "_points.csv")
    cols = ["paper_id", "series", "temperature_K", "field_T",
            "Jc_A_per_cm2", "px", "py", "n_pixels"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    meta["n_points"] = len(out)
    json.dump(meta, open(os.path.join(args.out_dir, stem + "_calibration.json"), "w"),
              indent=2)
    print("frame px: x %d-%d, y %d-%d" % frame)
    print("x ticks: %s" % [v for v, _ in meta["x_ticks_read"]])
    print("y ticks: %s" % [v for v, _ in meta["y_ticks_read"]])
    print("axis span: x %s  y %s" % (meta["axis_span_from_ticks"]["x"],
                                     meta["axis_span_from_ticks"]["y"]))
    for p in pairs:
        for nm in (p["upper"], p["lower"]):
            n = sum(1 for r in out if r["series"] == nm)
            v = [r["Jc_A_per_cm2"] for r in out if r["series"] == nm]
            print("  %-10s %3d points  Jc %.3g .. %.3g"
                  % (nm, n, max(v) if v else 0, min(v) if v else 0))
    print("total %d points, written to %s" % (len(out), path))


if __name__ == "__main__":
    main()
