#!/usr/bin/env python3
"""Reproduction test for the tick-geometry calibration.

The geometry route must reproduce the read-the-labels route before it is trusted
anywhere the labels are missing. 2012.13723 FIG. 4 is the only figure in the
corpus whose x axis can be calibrated both ways, so it is the test.

It also asserts the refusal. Every left (y) axis tried so far fails to yield an
evenly spaced major set, and the function must return an error rather than a
number. A test that only checked the success path would let a silent guess
through, which is the exact failure this module exists to remove.

    python analysis/test_geometry_calibration.py --pdf <2012.13723v3.pdf>
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "reextraction_specs", "2012.13723_fig4.json")


def run(spec_path, out_dir):
    subprocess.run([sys.executable,
                    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "figure_digitizer.py"),
                    "--spec", spec_path, "--out-dir", out_dir],
                   check=True, capture_output=True)
    stem = os.path.splitext(os.path.basename(spec_path))[0]
    import csv
    return (list(csv.DictReader(open(os.path.join(out_dir, stem + "_points.csv")))),
            json.load(open(os.path.join(out_dir, stem + "_calibration.json"))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--tol-x", type=float, default=0.005,
                    help="max allowed field difference, in the axis units")
    args = ap.parse_args()

    base = json.load(open(SPEC))
    base["pdf"] = args.pdf
    fails = []
    with tempfile.TemporaryDirectory() as d:
        a = dict(base)
        pa = os.path.join(d, "text.json")
        json.dump(a, open(pa, "w"))
        rows_text, meta_text = run(pa, d)

        b = json.loads(json.dumps(base))
        b["x"] = {"log": False, "label": "field_T", "calibration": "geometry",
                  "geometry": {"first_major": 1.0, "last_major": 6.0}}
        pb = os.path.join(d, "geom.json")
        json.dump(b, open(pb, "w"))
        rows_geom, meta_geom = run(pb, d)

        if len(rows_text) != len(rows_geom):
            fails.append("point counts differ: %d against %d"
                         % (len(rows_text), len(rows_geom)))
        else:
            dx = max(abs(float(x["field_T"]) - float(y["field_T"]))
                     for x, y in zip(rows_text, rows_geom))
            dy = max(abs(float(x["Jc_A_per_cm2"]) / float(y["Jc_A_per_cm2"]) - 1)
                     for x, y in zip(rows_text, rows_geom))
            print("points            %d" % len(rows_text))
            print("max field diff    %.5f (tolerance %.5f)" % (dx, args.tol_x))
            print("max Jc rel diff   %.3g" % dy)
            if dx > args.tol_x:
                fails.append("field difference %.5f exceeds %.5f" % (dx, args.tol_x))
            if dy > 1e-9:
                fails.append("Jc changed, but only the x axis was switched")

        g = meta_geom.get("geometry_calibration", {}).get("x")
        if not g:
            fails.append("no geometry diagnostics were recorded")
        else:
            print("majors found      %d, spacing %.2f px, uniformity %.5f"
                  % (g["n_major"], g["spacing_px"], g["uniformity"]))
            print("implied step      %s, round: %s"
                  % (g["implied_step_per_major"], g["step_is_round"]))
            if not g["step_is_round"]:
                fails.append("the implied per-major step is not a round number")

        # mutations: a wrong typed value must be refused, not merely flagged.
        # The re-projection residual does not catch these, because the pixels
        # are measured correctly and only their labelling is wrong.
        for label, (first, last) in (("wrong first", (2.0, 6.0)),
                                     ("wrong last", (1.0, 7.0)),
                                     ("swapped", (6.0, 1.0))):
            m = json.loads(json.dumps(base))
            m["x"] = {"log": False, "label": "field_T",
                      "calibration": "geometry",
                      "geometry": {"first_major": first, "last_major": last}}
            pm = os.path.join(d, "mut.json")
            json.dump(m, open(pm, "w"))
            rm = subprocess.run(
                [sys.executable,
                 os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "figure_digitizer.py"),
                 "--spec", pm, "--out-dir", d], capture_output=True, text=True)
            if rm.returncode == 0:
                fails.append("mutation '%s' was accepted; it must be refused"
                             % label)
            elif "not a round number" not in rm.stderr:
                fails.append("mutation '%s' failed for the wrong reason" % label)
            else:
                print("mutation %-12s refused, as required" % label)

        # the refusal path: the y axis of this same figure must not calibrate
        c = json.loads(json.dumps(base))
        c["y"] = {"log": True, "label": "Jc_A_per_cm2", "calibration": "geometry",
                  "geometry": {"first_major": 1e4, "last_major": 1e6}}
        pc = os.path.join(d, "yfail.json")
        json.dump(c, open(pc, "w"))
        r = subprocess.run([sys.executable,
                            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "figure_digitizer.py"),
                            "--spec", pc, "--out-dir", d],
                           capture_output=True, text=True)
        if r.returncode == 0:
            fails.append("the y axis calibrated from geometry; it must refuse, "
                         "because its major ticks are not evenly spaced once a "
                         "data curve reaches the frame")
        elif "cannot be calibrated from geometry" not in r.stderr:
            fails.append("the y axis failed for the wrong reason: %s"
                         % r.stderr.strip().splitlines()[-1:])
        else:
            print("y axis            refused, as required")

    if fails:
        print("\nFAIL")
        for f in fails:
            print("  " + f)
        sys.exit(1)
    print("\nPASS")


if __name__ == "__main__":
    main()
