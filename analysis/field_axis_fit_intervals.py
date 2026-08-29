#!/usr/bin/env python3
"""
field_axis_fit_intervals.py

Where do the field-axis fits actually sit in reduced field?

Section III.E and Assumption 1 of the manuscript state that the dispatched
predictions are "extrapolations of the fitted form outside the range over which
its exponents were validated", citing the applicability criterion
(H_max - H_min)/Hc2,0 > 0.3. That criterion is a condition on the width of the
fitted interval, which the manuscript says itself, and not on where the interval
begins. A curve admitted with a span of 0.4 whose measurements start at zero
field covers reduced field 0 to 0.4, and a dispatch point at reduced field 0.002
to 0.32 then lies inside the fitted interval rather than beyond it.

Settling that needs the lower endpoint of each fitted sweep, which the fits table
does not carry. This recovers it from the per-point extraction and reports, per
substructure, where the fitted intervals begin and end in reduced field and what
fraction of them contain the dispatch grid.

    python field_axis_fit_intervals.py
"""
import csv, glob, os, statistics as st, sys, collections

# Run from v3_2_9_path_2_prep. The extraction lives outside it, so walk up for
# the first ancestor holding data_agent2 rather than assuming a home directory.
PREP = os.getcwd()


def _find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, "data_agent2")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            sys.exit("cannot find data_agent2 above %s; run from "
                     "v3_2_9_path_2_prep" % start)
        d = parent


ROOT = _find_root(PREP)
LONG = os.path.join(ROOT, "data_agent2", "*", "*LONG*.csv")
FITS = os.path.join(PREP, "phase_3_form3_fits_partial_cohortB_v2.csv")
DIAG = os.path.join(PREP, "beta_H_logJc0_identifiability_diagnostic.csv")
OUT = os.path.join(PREP, "audit", "field_axis_fit_intervals.csv")

# The three dispatched families and the reduced-field range the dispatch grid
# covers, as stated in Sec. III.E: 0.1, 1 and 5 T against anchors of 15.5 to 60 T.
DISPATCH_LO, DISPATCH_HI = 0.002, 0.32
DISPATCHED = {"iron_chalcogenide_11", "iron_pnictide_122", "conventional_AlB2"}


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    sub_of = {}
    for r in csv.DictReader(open(DIAG)):
        sub_of.setdefault(r["compound_formula"], r["substructure"])

    # lower and upper endpoint of every field sweep in the extraction
    sweeps = collections.defaultdict(list)
    nfiles = 0
    for path in sorted(glob.glob(LONG)):
        nfiles += 1
        for r in csv.DictReader(open(path)):
            if (r.get("primary_scan_direction") or "").strip().upper() != "H":
                continue
            h = num(r.get("field_T"))
            if h is None:
                continue
            key = (r.get("arxiv_id"), r.get("compound_formula"),
                   r.get("sample_form"), r.get("fixed_axis_value"))
            sweeps[key].append(h)

    rows, unmatched = [], 0
    for r in csv.DictReader(open(FITS)):
        if (r.get("fixed_axis") or "").strip() != "T":
            continue
        hc2 = num(r.get("Hc2_T_used"))
        if not hc2:
            continue
        key = (r.get("arxiv_id"), r.get("compound_formula"),
               r.get("sample_form"), r.get("fixed_axis_value"))
        pts = sweeps.get(key)
        if not pts:
            unmatched += 1
            continue
        h_lo, h_hi = min(pts) / hc2, max(pts) / hc2
        sub = sub_of.get(r["compound_formula"], "unmapped")
        rows.append(dict(
            arxiv_id=r["arxiv_id"], compound_formula=r["compound_formula"],
            substructure=sub, sample_form=r["sample_form"],
            fixed_T_K=r["fixed_axis_value"], Hc2_T_used=hc2, n_points=len(pts),
            H_min_T=min(pts), H_max_T=max(pts),
            h_reduced_min=round(h_lo, 5), h_reduced_max=round(h_hi, 5),
            span=round(h_hi - h_lo, 5),
            contains_dispatch_grid=(h_lo <= DISPATCH_LO and h_hi >= DISPATCH_HI),
            contains_lowest_dispatch_point=(h_lo <= DISPATCH_LO),
        ))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    w = csv.DictWriter(open(OUT, "w", newline=""), fieldnames=list(rows[0]))
    w.writeheader()
    for r in rows:
        w.writerow(r)

    print("extraction files read      : %d" % nfiles)
    print("field-axis fits matched    : %d   unmatched: %d" % (len(rows), unmatched))
    print("dispatch grid spans reduced field %.3f to %.2f\n" % (DISPATCH_LO, DISPATCH_HI))
    hdr = "%-26s %4s %9s %9s %9s %9s"
    print(hdr % ("substructure", "n", "med h_lo", "max h_lo", "med h_hi", "min h_hi"))
    for sub in sorted({r["substructure"] for r in rows}):
        g = [r for r in rows if r["substructure"] == sub]
        lo = [r["h_reduced_min"] for r in g]
        hi = [r["h_reduced_max"] for r in g]
        print(hdr % (sub + (" *" if sub in DISPATCHED else ""), len(g),
                     "%.4f" % st.median(lo), "%.4f" % max(lo),
                     "%.3f" % st.median(hi), "%.3f" % min(hi)))
    print("\n(* = dispatched family)\n")
    for label, pred in (("start at or below the lowest dispatch point",
                         lambda r: r["contains_lowest_dispatch_point"]),
                        ("contain the whole dispatch grid",
                         lambda r: r["contains_dispatch_grid"])):
        d = [r for r in rows if r["substructure"] in DISPATCHED]
        n = sum(1 for r in d if pred(r))
        print("dispatched-family fits that %-44s %d/%d = %.0f%%"
              % (label, n, len(d), 100 * n / len(d)))
    # The blanket statement "every dispatched point lies outside the fitted
    # range" is not what the intervals show. Containment depends on the family
    # and on which of the three evaluated fields is meant, so report it that way.
    ANCHORS = {"iron_chalcogenide_11": [16.0, 30.0, 47.0],
               "iron_pnictide_122": [50.0, 60.0],
               "conventional_AlB2": [15.5]}
    print("\nfraction of a family's field-axis fits whose fitted interval")
    print("contains each evaluated dispatch field, per anchor:\n")
    print("%-24s %7s %9s %8s %8s" % ("substructure", "anchor", "field_T", "h", "inside"))
    for sub, anchors in ANCHORS.items():
        g = [r for r in rows if r["substructure"] == sub]
        if not g:
            continue
        for anchor in anchors:
            for field_T in (0.1, 1.0, 5.0):
                h = field_T / anchor
                n = sum(1 for r in g
                        if r["h_reduced_min"] <= h <= r["h_reduced_max"])
                print("%-24s %7.1f %9.1f %8.4f %5d/%-3d %.0f%%"
                      % (sub, anchor, field_T, h, n, len(g), 100 * n / len(g)))
        print()
    print("written to %s" % OUT)


if __name__ == "__main__":
    main()
