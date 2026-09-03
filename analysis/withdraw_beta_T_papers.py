#!/usr/bin/env python3
"""
withdraw_beta_T_papers.py

Withdraws temperature-axis source papers whose deposited Jc series were checked
against the source figure and do not come from it.

Why this exists separately from withdraw_records.py. That script withdraws
records from the field-axis and anchor layers, keyed on DOI tokens that appear
across many deposited tables. The temperature-axis cohort is keyed on arXiv
pdf_name and lives in one table, phase_3_p44_post_UCLA_beta_T_fits.csv, so the
removal is a row filter on that table followed by a regeneration of everything
computed from it. Keeping the two registers apart also keeps the two evidence
standards apart: the entries below were each adjudicated against the figure in
the source PDF, and the reason field records what the figure shows.

How these were found. audit_extraction_integrity.py had never been pointed at
the temperature-axis cohort; it was run against one extraction folder that does
not contain it. Run against the beta_T source it returns 11 FAIL, 26 CHECK and
6 PASS over 43 papers. The ten papers below are those adjudicated against their
PDFs so far, ordered by how the screen ranked them. Every one that was checked
failed, which is the reason the header of the regenerated table carries a
provisional flag: the remaining 33 papers have not been read, and the screen
still flags several of them.

Two signatures recur and neither survives a reading of a figure:

  arithmetic lattice   Jc falls in exactly equal absolute steps along the field
                       axis, and the isotherms are separated by an equally
                       constant step, so the whole record is a 2D lattice in
                       (T, H). Real Jc(H) is convex on a log axis and real
                       isotherms are not equally spaced.

  axis-tick field grid The recorded field values are the log-axis minor ticks
                       of the source figure (1, 2, ... 9, 10, 20, ...) rather
                       than measured field values, sometimes with the decade
                       shifted so the range is physically impossible.

Re-running is safe. Papers already absent are reported and nothing is written
for them.

    python analysis/withdraw_beta_T_papers.py --dry-run
    python analysis/withdraw_beta_T_papers.py

Run from the repository root.
"""
import argparse
import csv
import datetime
import os
import shutil
import subprocess
import sys

DATA = "data"
AUDIT = "audit"
FITS = os.path.join(DATA, "phase_3_p44_post_UCLA_beta_T_fits.csv")
REGISTER_CSV = os.path.join(AUDIT, "withdrawn_beta_T_papers.csv")
BACKUP_DIR = os.path.join(AUDIT, "pre_beta_T_withdrawal_20260903")

REGISTER = [
    dict(
        paper_id="1612.02839v1.pdf",
        arxiv="1612.02839",
        citation="Li et al., Improving quantum-transition temperatures in "
                 "BaFe2As2-based crystals",
        figure="Fig. 6(a)",
        reason=("the figure axis is Jc (MA/cm2) over mu0H on a log axis from "
                "0.01 to 10 T, at 5 K and 13.5 K only. The deposit holds 0.2 to "
                "10 as A/cm2 over fields of 1e-6 to 1e-4 T, which are the "
                "log-axis minor ticks with the decade shifted by 1e-4, and adds "
                "an isotherm at 1.5 K that the paper does not measure; it states "
                "5 to 18.5 K. The deposited series fall monotonically while the "
                "figure shows the fishtail peak the paper describes in text"),
    ),
    dict(
        paper_id="1108.5583v3.pdf",
        arxiv="1108.5583",
        citation="Konczykowski, van der Beek, Tanatar, Mosser, Song, Kwon and "
                 "Prozorov, Phys. Rev. B 84, 180514",
        figure="FIG. 1 and FIG. 3",
        reason=("no figure in this five-page paper carries the deposited "
                "combination of axes. FIG. 3 is 9 to 16 K at a fixed 1 T with a "
                "right ordinate j (kA/cm2) reaching 35; the deposited 4.2, 8 and "
                "12 K come from FIG. 1, whose ordinate is dB/dx in G/um. The "
                "text gives j of order 100 kA/cm2 against a deposited maximum of "
                "500 A/cm2. Each deposited isotherm is ten evenly spaced points "
                "from N to N/10 and each is an exact scaling of the one below"),
    ),
    dict(
        paper_id="2403.19981v1.pdf",
        arxiv="2403.19981",
        citation="Ishida et al., Synthesis of CaKFe4As4 bulk samples with high "
                 "critical current density using a spark plasma sintering "
                 "technique",
        figure="Fig. 5(c)",
        reason=("the axis is Jc (kA cm-2) and the deposit holds the bare numbers "
                "as A cm-2, but the shape is wrong independently of the unit: "
                "the figure's 4.2 K curve falls from about 80 to about 17 across "
                "the field range while the deposit falls from 100 to 6, and the "
                "deposited isotherms start on an exact 10-unit ladder where the "
                "figure's are irregularly spaced. The compound is also wrong: "
                "CaKFe4As4 is a 1144 phase, recorded as K(FeAs)2 and filed under "
                "iron_pnictide_122"),
    ),
    dict(
        paper_id="1109.5479v1.pdf",
        arxiv="1109.5479",
        citation="van der Beek et al., Vortex pinning: a probe for nanoscale "
                 "disorder in iron-based superconductors",
        figure="Fig. 2",
        reason=("the axis is jc (A m-2), recorded as A/cm2, which is why the "
                "deposit exceeds the depairing limit. Beyond the unit, the "
                "deposited fields are the log-axis ticks 0.01 to 0.09 then 0.1 "
                "to 1, and each isotherm falls in exact 5e7 steps over most of "
                "its length, switching to 1e7 steps for the last two, four and "
                "six points respectively, with heads at 9e8, 8e8 and 7e8, so the "
                "isotherms are two steps apart. That tail change is why the "
                "deposit's own exact-arithmetic test does not fire on this "
                "record. The figure shows a B^-1/2 decay to a minimum near 1 T "
                "and a rise, which a descending ramp cannot carry"),
    ),
    dict(
        paper_id="0904.2442v1.pdf",
        arxiv="0904.2442",
        citation="Eisterer, Weber, Jiang, Weiss, Yamamoto, Polyanskii, "
                 "Hellstrom and Larbalestier, Neutron Irradiation of SmFeAsO1-xFx",
        figure="FIG. 3, lower panel",
        reason=("the axis is Jc (A m-2), recorded as A/cm2, giving a deposited "
                "1e9 A/cm2 that is above the depairing limit. The deposit also "
                "holds only 3 to 7 T, on nine points, where the figure spans 0 "
                "to 7 T with of order forty points per isotherm. Every deposited "
                "value is a round multiple of 5e7 and the series descend in runs "
                "of constant step, 1e8 then 5e7, rather than as a reading of a "
                "curve"),
    ),
    dict(
        paper_id="1801.05074v1.pdf",
        arxiv="1801.05074",
        citation="Study of the second magnetization peak and the pinning "
                 "behaviour in Ba(Fe0.935Co0.065)2As2",
        figure="Fig. 8(a)",
        reason=("all twelve deposited isotherms are exact arithmetic ramps in "
                "steps of 20000 A/cm2, and successive isotherms are separated by "
                "the same 20000. The isotherm temperatures are irregular (2, "
                "3.5, 5, 7, 9, 11, 13, 15, 16, 17, 18, 19 K), so the lattice is "
                "in isotherm index against field rather than in temperature "
                "against field, which no measurement produces. The paper's "
                "subject is the second magnetization peak, which a monotonic "
                "ramp cannot represent"),
    ),
    dict(
        paper_id="1002.0248v1.pdf",
        arxiv="1002.0248",
        citation="Yadav and Paulose, The flux pinning force and vortex phase "
                 "diagram of single crystal FeTe0.60Se0.40",
        figure="Fig. 1(a)",
        reason=("the deposited field axis runs 0 to 0.0012 T on 13 points in "
                "steps of 1e-4, that is 0 to 12 gauss, which is not a range over "
                "which Jc(H) is measured. Six of seven isotherms are exact "
                "arithmetic ramps, "
                "and the 8 K record interleaves two series of different "
                "magnitude (10000, 100000, 9500, 80000) within one isotherm"),
    ),
    dict(
        paper_id="2110.15577v1.pdf",
        arxiv="2110.15577",
        citation="Iida et al., Approaching the ultimate superconducting "
                 "properties of (Ba,K)Fe2As2 by naturally formed low-angle grain "
                 "boundary networks",
        figure="Fig. 4",
        reason=("the deposited record is a lattice on a uniform 1 T grid from 0 "
                "to 16 T. Every isotherm descends in steps of exactly 5e5 A/cm2, "
                "15 to 16 of the 16 steps in each, with heads at 1e7, 9e6, 8e6 "
                "and 7e6, so the four isotherms are 1e6 apart at zero field and "
                "5e5 apart at every field above it. The exceptions are a single "
                "1e6 first step at 15 K and two tail steps at 25 and 30 K"),
    ),
    dict(
        paper_id="1003.0946v2.pdf",
        arxiv="1003.0946",
        citation="Ding et al., Comparative study of type-II superconducting "
                 "properties in polycrystalline NdFeAsO0.88F0.12",
        figure="Fig. 8 and Fig. 10",
        reason=("the deposited record is internally incoherent. The 5 K isotherm "
                "contains 10000, 9000, 70, 69, 68, 67, 66, 65, 9000, 8000, 64, "
                "7000: two series three orders of magnitude apart interleaved "
                "within one isotherm, one of which is a unit-count ramp "
                "descending 70, 69, 68. No figure produces this"),
    ),
    dict(
        paper_id="1204.0339v2.pdf",
        arxiv="1204.0339",
        citation="Sharma, Vinod, Sundar and Bharathi, Critical current density "
                 "and magnetic phase diagram of BaFe1.29Ru0.71As2 single crystals",
        figure="Fig. 3(a)",
        reason=("each deposited field value appears twice with different Jc, and "
                "the resulting series alternates down and up in a sawtooth "
                "(100000, 100000, 90000, 95000, 90000, 85000, 80000, 85000). "
                "That is two interleaved ramps, not the fish-tail peak the "
                "figure caption describes"),
    ),
    dict(
        paper_id="1802.09868v1.pdf",
        arxiv="1802.09868",
        citation="Park, Pyon, Ohara, Ito and Tamegai, Field-driven transition in "
                 "the Ba1-xKxFe2As2 superconductor with splayed columnar defects",
        figure="not reached; withdrawn on the deposited record alone",
        reason=("the deposited field axis runs 0 to 0.004 T in steps of 5e-4, "
                "that is 0 to 40 gauss, against a paper reporting Jc over 10 "
                "MA/cm2 and values of 13.9 and 19.5 MA/cm2. The isotherms at 2 "
                "to 20 K are exact ramps in steps of 1e6 and sit 1e6 apart; the "
                "15 K record carries three different Jc at H = 0; and the 25 K "
                "record increases with field on duplicated field values. This "
                "was the one paper the screen failed that the first pass left "
                "in, and leaving it would have made the withdrawal selective on "
                "the screen's own verdict"),
    ),
]

WITHDRAWN = "2026-09-03"


def load(path):
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        return list(rd), rd.fieldnames


def backup(paths):
    """Copy each path into BACKUP_DIR unless a backup is already there.

    The guard matters: an earlier regeneration script in this repository
    overwrote its own backups on a second run, which destroyed the only copy of
    the pre-change state. A backup that already exists is the pre-change state
    and must not be replaced by a post-change one.
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for p in paths:
        if not os.path.exists(p):
            continue
        dest = os.path.join(BACKUP_DIR, os.path.basename(p))
        if os.path.exists(dest):
            print("  backup already present, left alone: %s" % dest)
            continue
        shutil.copy2(p, dest)
        print("  backed up %s -> %s" % (p, dest))


def write_register():
    """Write the register, preserving n_fits_removed from any earlier run.

    On a second run every paper is already absent, so the counts computed in
    this process are all zero. Overwriting the register with those would erase
    the only record of what each withdrawal cost, which is the column a reader
    checks first. Existing non-empty counts therefore win.
    """
    os.makedirs(AUDIT, exist_ok=True)
    prior = {}
    if os.path.exists(REGISTER_CSV):
        with open(REGISTER_CSV, newline="") as fh:
            for r in csv.DictReader(fh):
                v = (r.get("n_fits_removed") or "").strip()
                if v:
                    prior[r["paper_id"]] = v
    with open(REGISTER_CSV, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["paper_id", "arxiv_id", "citation", "figure_checked",
                    "withdrawn", "n_fits_removed", "reason"])
        for e in REGISTER:
            n = e.get("_n", "")
            if not n and e["paper_id"] in prior:
                n = prior[e["paper_id"]]
            elif e["paper_id"] in prior and str(prior[e["paper_id"]]) != str(n):
                n = prior[e["paper_id"]]
            w.writerow([e["paper_id"], e["arxiv"], e["citation"], e["figure"],
                        WITHDRAWN, n, e["reason"]])
    print("  wrote %s (%d entries)" % (REGISTER_CSV, len(REGISTER)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(FITS):
        sys.exit("not found: %s (run from the repository root)" % FITS)

    rows, cols = load(FITS)
    targets = {e["paper_id"] for e in REGISTER}
    present = {r["paper_id"] for r in rows}

    for e in REGISTER:
        n = sum(1 for r in rows if r["paper_id"] == e["paper_id"])
        e["_n"] = n
        if n == 0:
            print("  already absent: %s" % e["paper_id"])
        else:
            print("  %-20s %3d fits to remove" % (e["paper_id"], n))

    keep = [r for r in rows if r["paper_id"] not in targets]
    removed = len(rows) - len(keep)
    print("\n  %d fits in, %d removed, %d remain" % (len(rows), removed, len(keep)))
    print("  papers: %d in, %d remain" % (len(present), len(present - targets)))

    if args.dry_run:
        print("\ndry run, nothing written")
        return

    backup([FITS,
            os.path.join(AUDIT, "temperature_axis_leave_one_out.csv"),
            os.path.join(AUDIT, "leave_one_out_family_size_sensitivity.csv"),
            os.path.join(DATA, "phase_3_p47_compound_leave_out_MAE.csv")])
    with open(FITS, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(keep)
    print("  rewrote %s" % FITS)
    write_register()

    print("\nregenerating everything downstream of the fit table")
    for cmd in (["python3", "analysis/compound_leave_one_out.py"],
                ["python3", "analysis/temperature_axis_summary.py"]):
        print("  $ %s" % " ".join(cmd))
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("    FAILED rc=%d" % r.returncode)
            print("    " + (r.stderr or "").strip()[-800:])
        else:
            tail = [l for l in (r.stdout or "").splitlines() if l.strip()][-6:]
            for l in tail:
                print("    " + l)


if __name__ == "__main__":
    main()
