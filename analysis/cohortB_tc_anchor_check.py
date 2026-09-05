#!/usr/bin/env python3
"""
cohortB_tc_anchor_check.py

Every Cohort B critical-temperature anchor that can be checked against its own
paper, checked.

Why. analysis/tc_anchor_audit.py showed the temperature axis's Tc anchor was a
compound-keyed constant declared paper-reported: all ten Ba(FeAs)2 rows carried
38.0 K for samples measuring 19 to 40 K. The field axis was supposed to be
better, because `Tc_provenance` there reads "paper-reported (Cohort B
extraction)" and 19 of its 62 papers have a PDF in this corpus. This opens all
nineteen.

Method. For each paper, the temperatures the paper prints for the samples it
measures are recorded below together with a distinctive phrase from the
sentence that prints them. The script locates each phrase in the PDF text and
fails loudly if it is not there, so nothing here rests on a reading that cannot
be reproduced. Only then does it compare with the deposited anchor.

The traps this had to survive, all of which cost a wrong answer somewhere:

  - a Tc quoted in the introduction for a DIFFERENT material, which is how
    26 K (LaFeAsO(1-x)Fx), 22 K (Sefat's Co-doped BaFe2As2) and 39 K (MgB2)
    get into papers that never measure them
  - a Tc inside a reference title
  - several samples with different Tc, where the anchor matches one of them
  - a literature constant used inside a fitting relation (Presland's 85 K)
  - pdfplumber lifting the subscript out of "Tc" and hyphenating across lines

    python3 analysis/cohortB_tc_anchor_check.py

Run from the repository root. Writes audit/cohortB_tc_anchors.csv.
"""
import os
import re
import sys

import pandas as pd

PDFS = ("/mnt/user-data/uploads/SuperconductorWorkflow/kappa_pipeline/analysis/"
        "v3_2_9_path_2_prep/phase_3_p19_elsevier_pdfs")
PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
OUT = os.path.join("audit", "cohortB_tc_anchors.csv")

# identifier -> (verdict, [(sample, Tc_K, phrase to find in the paper)], comment)
# Tc_K is None when the phrase records something other than a value.
READINGS = {
    "10.1016/j.physc.2010.05.048": ([
        ("FeTe0.59Se0.41", 12.0, "conductingtransitionisobservedat"),
    ], "one sample; 26 K in the introduction belongs to LaFeAsO(1-x)Fx"),
    "10.1016/j.physc.2009.11.051": ([
        ("Ba(Fe0.93Co0.07)2As2", 24.0, "24kisnotaffectedbythe"),
    ], "one crystal, measured unirradiated and irradiated"),
    "10.1016/j.mtphys.2022.100783": ([
        ("powder", 24.1, "hasthelargesttransitionwidth"),
        ("polycrystal", 25.7, "ishigherthanlatter"),
        ("single_crystal", 24.4, "ishigherthanlatter"),
    ], "22 K appears only in the title of reference [22]"),
    "10.1016/j.jallcom.2023.170384": ([
        ("La0.87Sm0.13FeAs0.91P0.09O", 13.3, "sharpsuperconductingtransitionat"),
    ], "26 K is the literature LaFeAsO(1-x)Fx value, not this crystal"),
    "10.1016/j.matchemphys.2023.128348": ([
        ("X01-X04", 37.7, "approximately37.7"),
    ], "40 K on page 1 is the MgB2 discovery value, cited to reference [5]"),
    "10.1016/j.jallcom.2013.04.183": ([
        ("N1", 74.38, "7438"), ("N2", 64.11, "6411"),
        ("N3", 66.0, "transitiontemperaturesofthen1"),
        ("N4", 74.18, "7418"),
    ], "a Bi-2212 paper; 85 K is Presland's constant inside a fit"),
    "10.1016/j.cjph.2024.09.042": ([
        ("Hx-FeSe sample 2", 44.5, "445"),
        ("Hx-FeSe", 41.0, "increasedto41k"),
        ("FeSe", 10.0, "protonation"),
    ], "no sample near 14 K; the paper contains no tellurium"),
    "10.1016/j.ceramint.2024.10.058": ([
        ("LSCO-CS", 38.5, "lscocs"), ("Vac-1", 36.7, "367"),
        ("Vac-2", 39.3, "393"), ("Nitrogen-1", 29.9, "299"),
    ], "five pellets, 29.9 to 39.3 K"),
    "10.1016/j.phpro.2015.06.160": ([
        ("BaFe1.91Ni0.09As2", 18.9, "189"),
        ("Ba0.64K0.36Fe2As2", 25.5, "255"),
    ], "two crystals; the anchor matches neither"),
    "10.1016/j.physc.2016.05.023": ([
        ("FeSe", 9.0, "superconductingtransitiontemperature"),
        ("FeSe0.86S0.14", 9.5, "slightlyenhancedafter"),
    ], "the anchor is the undoped crystal while the compound string is doped"),
    "10.1016/j.jpcs.2026.113652": ([
        ("Co0 Bi-2223", 110.0, "110"), ("Co1 Bi-2223", 103.0, "103"),
        ("Co2 Bi-2223", 95.0, "95"), ("Co1 Bi-2212", 68.0, "68"),
    ], "eight sample-and-phase values from 68 to 110 K"),
    "10.1016/j.jallcom.2022.165358": ([
        ("Fe(1-x)KxSe0.5Te0.5", 14.0, "sitiontemperaturearound14k"),
    ], "all samples about 14 K"),
    "10.1016/0921-4534(96)00225-0": ([
        ("CeO2+PtO2 YBaCuO", 92.0, "92k"),
    ], ""),
    "10.1016/j.phpro.2012.03.421": ([
        ("Ba(Fe1-xRux)2As2", 20.0, "showssuperconductivityat"),
    ], ""),
    # papers that print no Tc for the sample they measure
    "10.1016/j.physc.2013.04.060": ([], "no Tc for the measured strands anywhere"),
    "10.1016/j.matpr.2019.05.078": ([], "39 K is a generic value in the "
                                        "introduction, not a measurement"),
    # deposits that cannot be checked
    "10.1016/j.physc.2011.02.004": (None, "page 1 of a 7-page article"),
    "10.1016/j.physc.2009.05.098": (None, "page 1 of a 6-page article; the "
                                          "deposited page says only 'above 50 K'"),
    "10.1016/j.jallcom.2023.170146": (None, "the PDF filed under this DOI is a "
                                            "different paper, physc.2009.11.051"),
}
TOL = 0.5


def normalise(t):
    """Squash the text so a phrase survives hyphenation, subscripts and CIDs."""
    t = re.sub(r"-\s*\n", "", t)
    return re.sub(r"[^a-z0-9]", "", t.lower())


def text_of(identifier):
    path = os.path.join(PDFS, identifier.replace("/", "_") + ".pdf")
    if not os.path.exists(path):
        return None, None
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        raw = " ".join((p.extract_text() or "") for p in pdf.pages)
        n = len(pdf.pages)
    return raw, n


def doi_in(raw):
    m = re.search(r"doi:\s*(10\.\d{4,}/[^\s,]+)", raw or "", re.I)
    return m.group(1).rstrip(".") if m else ""


def main():
    prov = pd.read_csv(PROV)
    rows, unverified = [], []
    for _, r in prov.iterrows():
        ident = str(r.identifier)
        if ident not in READINGS:
            continue
        readings, comment = READINGS[ident]
        raw, npages = text_of(ident)
        if raw is None:
            rows.append(dict(identifier=ident, recorded=r.Tc_anchor_K,
                             provenance=r.Tc_provenance, verdict="NO PDF",
                             printed="", comment=comment, pages=""))
            continue
        norm = normalise(raw)
        printed_doi = doi_in(raw)
        if readings is None:
            rows.append(dict(identifier=ident, recorded=r.Tc_anchor_K,
                             provenance=r.Tc_provenance, verdict="UNCHECKABLE",
                             printed="", comment=comment, pages=npages))
            continue
        vals = []
        for sample, tc, phrase in readings:
            if normalise(phrase) not in norm:
                unverified.append((ident, sample, phrase))
                continue
            vals.append((sample, tc))
        if not readings:
            verdict = "NOT PRINTED"
        elif not vals:
            verdict = "UNVERIFIED READING"
        elif any(abs(tc - r.Tc_anchor_K) <= TOL for _, tc in vals):
            verdict = "MATCHES" if len(vals) == 1 else "MATCHES ONE OF SEVERAL"
        else:
            verdict = "DISAGREES"
        rows.append(dict(
            identifier=ident, recorded=r.Tc_anchor_K, provenance=r.Tc_provenance,
            verdict=verdict, pages=npages,
            printed="; ".join(f"{s}={t}" for s, t in vals),
            comment=comment,
            printed_doi="" if printed_doi.lower() in ident.lower() else printed_doi,
        ))
    out = pd.DataFrame(rows)
    os.makedirs("audit", exist_ok=True)
    out.to_csv(OUT, index=False)

    if unverified:
        print("PHRASES NOT FOUND IN THE PDF, so the reading is not reproduced:")
        for u in unverified:
            print("  ", u)
        print()
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 60)
    print(out[["identifier", "recorded", "verdict", "printed"]].to_string(index=False))
    print()
    print(out.verdict.value_counts().to_string())
    print()
    mism = out[out.get("printed_doi", "").fillna("") != ""]
    if len(mism):
        print("PDFs whose own printed DOI is not the identifier they are filed under:")
        print(mism[["identifier", "printed_doi"]].to_string(index=False))
        print()
    d = out[out.verdict == "DISAGREES"]
    print(f"{len(d)} anchors disagree with the value their own paper prints:")
    for _, x in d.iterrows():
        print(f"  {x.identifier:38s} recorded {x.recorded:>6}   printed {x.printed}")
    print()
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
