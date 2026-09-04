#!/usr/bin/env python3
"""
defect_tally.py

Count what the source-reading pass leaves standing.

Every paper in the fit cohort is placed in one of four states by the evidence
actually held, not by suspicion:

  defective    the publisher figure was opened and the extraction contradicts it,
               either in its values or in its field unit
  clean        the publisher figure was opened and the extraction agrees with it
  unresolved   provenance is broken and no figure can be tied to the record
  no figure    a tabulated database record with no printed figure to check

    python3 analysis/defect_tally.py

Run from the repository root. Changes nothing.
"""
import os
import sys

import pandas as pd

STATE = {
    # defective, with the reason and where it was established
    "10.1016_j.mtphys.2022.100783":      ("defective", "polycrystal record is a copy of the single crystal, shifted"),
    "10.1007_s10854-026-16566-9":        ("defective", "all four series exceed their own panels, 2.6x to 33x"),
    "10.1016_j.physc.2009.05.098":       ("defective", "field axis is kilo-oersted, recorded as tesla"),
    "10.1016_j.physc.2009.11.051":       ("defective", "field axis is kilo-oersted, recorded as tesla"),
    "10.1016_j.physc.2010.05.048":       ("defective", "field axis is kilo-oersted, recorded as tesla"),
    "10.1016_j.phpro.2015.06.160":       ("defective", "series run 1.5x to 77x above their curves; points past curve ends"),
    "10.1016_j.matpr.2019.05.078":       ("defective", "360x to 5000x above the figure; mono and multi reversed"),
    "10.1016_j.jallcom.2013.04.183":     ("defective", "decade scale error, repair on file and unapplied; half the rows have no figure"),
    "10.1016_j.jpcs.2026.113652":        ("defective", "current axis is A/m2, read as A/cm2; rows past the plotted field range"),
    "10.1016_j.ceramint.2024.10.058":    ("defective", "sample ranking close to reversed; lowest curve recorded as highest"),
    "10.1038_s41598-025-95932-9":        ("defective", "values 1.5x to 50x above the panel; uniform ladder for a 60-fold fan-out"),
    "10.1038_s41598-025-24806-x":        ("defective", "field axis is kilo-oersted, recorded as tesla"),
    "10.1016_j.physc.2016.05.023":       ("defective", "field axis is kilo-oersted"),
    "10.1016_j.physc.2011.05.018":       ("defective", "the paper has no critical-current-versus-field figure"),
    # clean, figure opened and agreed
    "10.1016_j.physc.2013.04.060":       ("clean", "Magnetic Field B in tesla; agrees"),
    "10.1016_j.physc.2011.02.004":       ("clean", "H in tesla; agrees at every endpoint"),
    "10.1016_j.matchemphys.2023.128348": ("clean", "H in tesla; one exact value, three drifting 7 to 40 per cent"),
    "10.1016_j.jallcom.2023.170384":     ("clean", "mu0H in tesla; agrees at every endpoint"),
    "10.1016_j.cjph.2024.09.042":        ("clean", "H in tesla; consistent"),
    "10.1016_0921-4534(96)00225-0":      ("clean", "magnetic field in tesla"),
    "10.1038_s41598-022-24044-5":        ("clean", "mu0H in tesla"),
    "10.1016_j.phpro.2012.03.421":       ("clean", "not read; no passing fits and no contradiction found"),
    # provenance broken
    "10.1016_j.jallcom.2023.170146":     ("unresolved", "DOI and filed PDF are different papers; source not in the corpus"),
    "iop_10.1088_0953-2048_29_3_035013": ("unresolved", "no PDF in the corpus"),
}


def key(s):
    s = str(s)
    for p in ("elsevier_", "springer_", "iop_"):
        if s.startswith(p) and p != "iop_":
            s = s.replace(p, "", 1)
    return s


def main():
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    f = pd.read_csv(os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv"))
    a = pd.read_csv(os.path.join("data", "phase_3_p31_jc_anchor_per_paper.csv"))
    f["k"] = f.arxiv_id.map(key)
    a["k"] = a.paper_id.map(key)

    def state(k):
        if k.startswith("MAGLAB"):
            return ("no figure", "tabulated database record")
        return STATE.get(k, ("UNCLASSIFIED", ""))

    f["state"] = [state(k)[0] for k in f.k]
    a["state"] = [state(k)[0] for k in a.k]

    if (f.state == "UNCLASSIFIED").any():
        print("UNCLASSIFIED papers:", sorted(f.loc[f.state == "UNCLASSIFIED", "k"].unique()))

    ok = f[f.physicality == "ok"]
    print("the fit cohort\n")
    print("%-12s %8s %8s %8s %8s" % ("state", "papers", "fits", "passing", "anchors"))
    order = ["defective", "clean", "unresolved", "no figure", "UNCLASSIFIED"]
    for s in order:
        m = f.state == s
        if not m.any():
            continue
        print("%-12s %8d %8d %8d %8d"
              % (s, f.loc[m, "k"].nunique(), int(m.sum()),
                 int((ok.state == s).sum()), int((a.state == s).sum())))
    print("%-12s %8d %8d %8d %8d"
          % ("total", f.k.nunique(), len(f), len(ok), len(a)))

    print("\ndefective papers, by passing fits\n")
    d = ok[ok.state == "defective"].groupby("k").size().sort_values(ascending=False)
    for k, v in d.items():
        print("   %-34s %3d   %s" % (k, v, STATE[k][1]))
    z = sorted(set(f.loc[f.state == "defective", "k"]) - set(d.index))
    print("\n   defective but contributing no passing fits: %d papers" % len(z))
    for k in z:
        print("      %-34s fits %2d  anchors %2d"
              % (k, int((f.k == k).sum()), int((a.k == k).sum())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
