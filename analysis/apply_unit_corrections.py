#!/usr/bin/env python3
"""
apply_unit_corrections.py

Corrections that change a value or a label rather than removing a record, with
the same rule as withdraw_records.py: every table that carries the record is
corrected in one run, so the deposit cannot end up half corrected.

Why this exists. The Fe(Se,Te) record was corrected once already and the
correction reached two fields out of four. log10_Jc_anchor was multiplied and
sample_form was relabelled in the anchor table; Jc_anchor_A_per_cm2 in the same
table was left in MA/cm2, and sample_form stayed "wire" in the provenance and
Form 3 tables. The deposit therefore carried one row whose two Jc columns
disagreed by a factor of a million, and one sample described as a thin film in
one table and a wire in two others. A referee asked four times to see this data.

Correction 1, units. 10.1038/s41598-022-24044-5, Piperno et al., Sci. Rep. 13
(2023) 569. The digitized figure axis is Jc in MA/cm2 and the wide-to-long
converter copied plot coordinates into a column named Jc_A_per_cm2 with no
conversion. The log column was later fixed and the linear column was not.
Values of 0.10 to 1.03 A/cm2 for a superconducting film are absurd on their
face; the log column's 1e5 to 1e6 A/cm2 is what the paper reports.

Correction 2, sample form. The same paper is titled "High-performance Fe(Se,Te)
films on chemical CeO2-based buffer layers" and describes a thin film on a
buffered substrate throughout. It is not a wire.

Both are guarded. The unit correction only fires on a value still small enough
to be un-multiplied, so re-running cannot multiply twice, and the relabel only
fires where the old label is still present. Running this on a corrected deposit
reports that there is nothing to do.

    python analysis/apply_unit_corrections.py --dry-run
    python analysis/apply_unit_corrections.py

Run from the repository root.
"""
import argparse, csv, datetime, os, shutil, sys

DATA = "data"
AUDIT = "audit"

RECORD = "s41598-022-24044-5"

UNIT_FIX = dict(
    column="Jc_anchor_A_per_cm2",
    factor=1e6,
    only_if_below=1e3,      # a corrected row is ~1e5 and will not re-fire
    reason="figure axis is MA/cm2; the converter applied no unit conversion",
)

LABEL_FIX = dict(
    column="sample_form",
    old="wire",
    new="thin_film",
    reason="the paper describes a thin film on a buffered substrate, not a wire",
)

# Sample-form relabels, each read from the source paper's own description of what
# it made. These were found by verifying the CHECK-verdict extractions against
# their PDFs; two of them sat in families previously described as clean.
FORM_FIXES = [
    dict(token="j.physc.2009.05.098", old="thin_film", new="polycrystal",
         citation="Physica C 469 (2009) 915",
         reason="the paper states 'We have prepared two kinds of polycrystalline "
                "samples of iron-oxypnictide superconductors'. The recorded Jc is "
                "the intragranular value from magneto-optical imaging of those "
                "polycrystals, not a thin-film measurement"),
    dict(token="j.physc.2011.02.004", old="unknown", new="polycrystal",
         citation="Physica C 471 (2011) 258",
         reason="the abstract reads 'The magnetization of the PrFeAsO0.60F0.12 "
                "polycrystalline sample has been measured'"),
    dict(token="j.jallcom.2023.170384", old="unknown", new="single_crystal",
         citation="J. Alloys Compd. 958 (2023) 170384",
         reason="titled 'Emergence of superconductivity in single-crystalline "
                "LaFeAsO under simultaneous Sm and P substitution'; measurements "
                "are on single-crystalline samples"),
]


def read(path):
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        return rd.fieldnames, list(rd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")

    stamp = datetime.datetime.now().strftime("%Y%m%d")
    backup = os.path.join(AUDIT, "pre_unit_correction_%s" % stamp)
    report = []

    for name in sorted(os.listdir(DATA)):
        if not name.endswith(".csv"):
            continue
        path = os.path.join(DATA, name)
        cols, rows = read(path)
        if not cols:
            continue
        scaled = relabelled = 0
        for r in rows:
            blob = "\x1f".join(str(v) for v in r.values())
            for fx in FORM_FIXES:
                if fx["token"] in blob and r.get(fx["column"] if "column" in fx
                                                else "sample_form") == fx["old"]:
                    r["sample_form"] = fx["new"]
                    relabelled += 1
            if RECORD not in blob:
                continue
            c = UNIT_FIX["column"]
            if c in cols:
                try:
                    v = float(r[c])
                except (TypeError, ValueError):
                    v = None
                if v is not None and 0 < v < UNIT_FIX["only_if_below"]:
                    r[c] = repr(v * UNIT_FIX["factor"])
                    scaled += 1
            c = LABEL_FIX["column"]
            if c in cols and r.get(c) == LABEL_FIX["old"]:
                r[c] = LABEL_FIX["new"]
                relabelled += 1
        if not (scaled or relabelled):
            continue
        report.append((name, scaled, relabelled))
        if not args.dry_run:
            os.makedirs(backup, exist_ok=True)
            shutil.copy2(path, os.path.join(backup, name))
            with open(path, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols)
                w.writeheader()
                for r in rows:
                    w.writerow(r)

    print("correcting %s%s\n" % (RECORD, "   (DRY RUN)" if args.dry_run else ""))
    if report:
        print("%-52s %8s %10s" % ("table", "rescaled", "relabelled"))
        for name, s, l in report:
            print("%-52s %8d %10d" % (name[:52], s, l))
    else:
        print("nothing matched; the deposit is already corrected")
    print("\n   units : %s" % UNIT_FIX["reason"])
    print("   label : %s" % LABEL_FIX["reason"])
    for fx in FORM_FIXES:
        print("   form  : %-24s %s -> %s" % (fx["token"], fx["old"], fx["new"]))
        print("           %s" % fx["citation"])
    if report and not args.dry_run:
        print("\nbackups: %s" % backup)
    if args.dry_run:
        print("\nnothing was written.")


if __name__ == "__main__":
    main()
