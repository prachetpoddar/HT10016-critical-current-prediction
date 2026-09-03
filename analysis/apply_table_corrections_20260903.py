#!/usr/bin/env python3
"""Three corrections to the deposited tables that need no new extraction.

1. Withdraw the six 10.1038/s41467-025-55880-4 field-axis fits. The source is a
   superconducting-diode-effect study whose text contains no current density in
   any units; see audit/withdraw_s41467_field_axis.md.
2. Give the two records of one paper a shared key. 1002.0208v2 (temperature
   axis) and 10.1016/j.physc.2011.02.004 (field axis) are the same paper under
   two identifiers, so any statistic that clusters by paper across both axes
   currently counts it twice. A `paper_key` column is added to both fit files
   rather than either record being deleted, since both hold real measurements.
3. Move the PrFeAsO0.6F0.12 field-axis fits from the Tier-3 literature default
   to the paper's own irreversibility line.

Everything is backed up first and the script is idempotent.
"""
import csv
import datetime
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
AUDIT = os.path.join(ROOT, "audit")
FITS_H = os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_T = os.path.join(DATA, "phase_3_p44_post_UCLA_beta_T_fits.csv")
REFIT = os.path.join(DATA, "reextraction", "physc_2011_02_004_field_axis_refit.csv")
ANCHORS = os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv")
PROV = os.path.join(DATA, "provenance_table_fitcohort_full.csv")
WITHDRAWN = os.path.join(AUDIT, "withdrawn_records.csv")
DUPES = os.path.join(AUDIT, "duplicate_papers.csv")

SDE = "springer_10.1038_s41467-025-55880-4"
PRFEASO = "elsevier_10.1016_j.physc.2011.02.004"
TWIN = "1002.0208v2.pdf"
TC_ADOPTED = 48.0          # the paper's own stated diamagnetic onset


def read(path):
    with open(path, newline="") as fh:
        r = csv.DictReader(fh)
        return list(r), list(r.fieldnames)


def write(path, rows, cols):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def backup(paths):
    stamp = datetime.datetime.now().strftime("%Y%m%d")
    d = os.path.join(AUDIT, "pre_table_corrections_" + stamp)
    os.makedirs(d, exist_ok=True)
    for p in paths:
        dst = os.path.join(d, os.path.basename(p))
        # Never overwrite an existing backup. This script is idempotent, so a
        # second run would otherwise replace the pre-correction copy with the
        # corrected one and destroy the only record of the original state.
        if os.path.exists(p) and not os.path.exists(dst):
            shutil.copy2(p, dst)
    return d


def main():
    print("backed up to", backup([FITS_H, FITS_T, WITHDRAWN, ANCHORS, PROV]))
    rows_h, cols_h = read(FITS_H)
    rows_t, cols_t = read(FITS_T)

    # ---------------------------------------------------------------- (1)
    drop = [r for r in rows_h if r["arxiv_id"] == SDE]
    rows_h = [r for r in rows_h if r["arxiv_id"] != SDE]
    print("1. withdrew %d field-axis fits from %s (%d at the exponent ceiling)"
          % (len(drop), SDE,
             sum(1 for r in drop if abs(float(r["beta"])) > 29.99)))

    if drop:
        wrows, wcols = read(WITHDRAWN)
        key = "10.1038/s41467-025-55880-4"
        if not any(r.get("identifier") == key for r in wrows):
            entry = {c: "" for c in wcols}
            entry.update({
                "identifier": key,
                "citation": "Superconducting diode effect in Bi2Sr2CaCu2O8+d "
                            "flakes, Nat. Commun. 16 (2025) 55880",
                "source_file": "data/extraction_examples/"
                               "s41467_025_55880_4_field_axis.csv",
                "withdrawn": datetime.date.today().isoformat(),
                "reason": "the paper reports no current density in any units: "
                          "zero occurrences of A/cm and zero of 'current "
                          "density' in its full text. Its currents are Ic in "
                          "microamps and its field sweep reaches 25 mT, while "
                          "the deposit carries 36 rows of Jc in A/cm2 over "
                          "0.01 to 0.25 T at temperatures taken from its "
                          "diode-efficiency discussion, for a sample s2 that "
                          "is not a device in the paper. See "
                          "audit/withdraw_s41467_field_axis.md",
                "status": "%d field-axis fits removed, all at the exponent "
                          "ceiling" % len(drop)})
            wrows.append(entry)
            write(WITHDRAWN, wrows, wcols)

    # The same paper also supplies anchor rows, and the anchor table is what
    # the variance decomposition runs on, so leaving them would keep a
    # withdrawn source inside the paper's pre-registered outcome. One of the two
    # is sample "s2", which is not a device in the paper at all.
    arows, acols = read(ANCHORS)
    a_drop = [r for r in arows if r["paper_id"] == SDE]
    arows = [r for r in arows if r["paper_id"] != SDE]
    write(ANCHORS, arows, acols)
    prows, pcols = read(PROV)
    p_drop = [r for r in prows if "s41467-025-55880-4" in r["identifier"]]
    prows = [r for r in prows if "s41467-025-55880-4" not in r["identifier"]]
    write(PROV, prows, pcols)
    if a_drop or p_drop:
        print("   also removed %d anchor rows (%s) and %d provenance row; "
              "rerun analysis/regenerate_regime_tables.py"
              % (len(a_drop), ", ".join(r["sample_id"] for r in a_drop),
                 len(p_drop)))

    # ---------------------------------------------------------------- (2)
    if "paper_key" not in cols_h:
        cols_h = cols_h + ["paper_key"]
    if "paper_key" not in cols_t:
        cols_t = cols_t + ["paper_key"]
    for r in rows_h:
        r["paper_key"] = TWIN if r["arxiv_id"] == PRFEASO else r["arxiv_id"]
    for r in rows_t:
        r["paper_key"] = r["paper_id"]
    shared = sum(1 for r in rows_h if r["paper_key"] == TWIN)
    shared_t = sum(1 for r in rows_t if r["paper_key"] == TWIN)
    print("2. paper_key added; %s now keys %d field-axis and %d temperature-axis "
          "fits that were counted as two papers" % (TWIN, shared, shared_t))
    with open(DUPES, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["paper_key", "field_axis_id", "temperature_axis_id",
                    "n_field_fits", "n_temperature_fits", "note"])
        w.writerow([TWIN, PRFEASO, TWIN, shared, shared_t,
                    "same paper: Physica C 471 (2011) 215 is arXiv 1002.0208. "
                    "Cluster paper-level tests on paper_key, not on the axis id."])

    # ---------------------------------------------------------------- (3)
    refit = {(float(r["fixed_axis_value"])): r for r in csv.DictReader(open(REFIT))
             if r["Hc2_source"] == "Tier_1_paper_Hirr"
             and float(r["Tc_assumed"] or 0) == TC_ADOPTED}
    n = 0
    for r in rows_h:
        if r["arxiv_id"] != PRFEASO:
            continue
        f = refit.get(float(r["fixed_axis_value"]))
        if not f:
            continue
        r["Hc2_T_used"] = f["Hc2_T_used"]
        r["Hc2_source"] = "Tier_1_paper_Hirr_arXiv_1002.0208_Eq5_Tc_%.0fK" % TC_ADOPTED
        r["n_pts"] = f["n_pts"]
        r["H_axis_range_normalized"] = f["H_axis_range_normalized"]
        r["beta"] = f["beta"]
        r["SE_beta"] = f["SE_beta"]
        r["log_Jc_partial"] = f["log_Jc_partial"]
        r["rms"] = f["rms"]
        r["physicality"] = "ok" if float(f["H_axis_range_normalized"]) >= 0.3 \
            else "H_axis_applicability_bound"
        n += 1
    print("3. moved %d PrFeAsO0.6F0.12 fits onto the paper's own Hirr line" % n)

    write(FITS_H, rows_h, cols_h)
    write(FITS_T, rows_t, cols_t)

    # ------------------------------------------------------------- summary
    import statistics as st
    def tier(r):
        s = r["Hc2_source"]
        return "Tier_1" if s.startswith("Tier_1") else (
            "Tier_2" if s.startswith("Tier_2") else "Tier_3")
    print("\nfield axis after the corrections:")
    print("%-8s %5s %9s %8s %9s %9s" % ("tier", "n", "med beta", "at ceil",
                                        "med win", "passing"))
    for t in ("Tier_1", "Tier_2", "Tier_3"):
        sel = [r for r in rows_h if tier(r) == t]
        if not sel:
            continue
        b = [float(r["beta"]) for r in sel if r["beta"].strip()]
        w = [float(r["H_axis_range_normalized"]) for r in sel
             if r["H_axis_range_normalized"].strip()]
        ok = sum(1 for r in sel if r["ok"] == "True" and r["physicality"] == "ok")
        print("%-8s %5d %9.2f %8d %9.3f %9d"
              % (t, len(sel), st.median(b),
                 sum(1 for x in b if x >= 29.99), st.median(w), ok))


if __name__ == "__main__":
    main()
