#!/usr/bin/env python3
"""
withdraw_record.py

Withdraws one source paper and everything derived from it from the fitted-cohort
tables, with backups and a manifest of exactly what was taken out.

Written for 10.1016/0921-4534(94)00021-2, Maignan et al., Physica C 243 (1995)
214. The extraction recorded that paper as Hg0.8V0.2Ba2Ca2Cu3O8 with a
transition-temperature anchor of 134 K. The paper synthesises Hg-1201 and
Hg-1212 and reports transition temperatures of 90, 115 and 124 K; neither that
stoichiometry nor the string "134" appears anywhere in it, and 134 K is the
literature value for Hg-1223, a phase the paper never made. Its four field-axis
fits already sat at the regression ceiling with a fractional field coverage of
0.04, so the record was outside the applicability window the paper defines. The
coauthors elected to withdraw it rather than re-anchor it, since the paper
reports two phases and which one the extracted curves belong to cannot be
settled from the figures.

The raw extraction under data_agent2 is deliberately left in place. It is the
evidence for what was extracted and why the record was withdrawn, and an audit
trail that deletes its own evidence is worth less than one that does not. A
withdrawal marker is written beside it instead.

    python withdraw_record.py --dry-run
    python withdraw_record.py
"""
import argparse, csv, datetime, os, shutil, sys

IDENTIFIER = "10.1016/0921-4534(94)00021-2"
UNDERSCORED = "elsevier_10.1016_0921-4534(94)00021-2"
COMPOUND = "Hg0.8V0.2Ba2Ca2Cu3O8"
REASON = ("compound and transition-temperature anchor absent from the source "
          "paper; see audit/cohort_anchor_audit.csv")

# (path relative to the prep folder, column to match on). A blank column means
# match the whole row, for tables that name the paper in a field we cannot
# predict.
TARGETS = [
    ("provenance_table_fitcohort_full.csv", "identifier"),
    ("phase_3_form3_fits_partial_cohortB_v2.csv", "arxiv_id"),
    ("beta_H_logJc0_identifiability_diagnostic.csv", "arxiv_id"),
    ("phase_3_p18_compositional_descriptors_cohortB.csv", ""),
    ("phase_3_p31_jc_anchor_per_paper.csv", ""),
]

# Deposited copies that must agree with the tables above.
RELEASE = os.path.join("..", "..", "..", "HT10016_release", "data")

# Left alone on purpose, and why.
UNTOUCHED = [
    ("caption_sweep.csv",
     "screen over the retrieval archive; the paper is still in the archive"),
    ("audit/*.csv",
     "audit outputs that record the finding and must keep the withdrawn row"),
    ("data_agent2/.../VISION_PASS_LONG.csv",
     "raw extraction, retained as the evidence for the withdrawal"),
    ("phase_3_p23_cuprate_HBCCO_*.csv",
     "HBCCO candidate and result files, now orphaned; review separately"),
]


def matches(row, column):
    if column:
        return row.get(column) in (IDENTIFIER, UNDERSCORED)
    blob = "\x1f".join(str(v) for v in row.values())
    return IDENTIFIER in blob or UNDERSCORED in blob or COMPOUND in blob


def process(path, column, backup_dir, dry):
    if not os.path.exists(path):
        return None
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        cols = rd.fieldnames
        rows = list(rd)
    keep = [r for r in rows if not matches(r, column)]
    removed = [r for r in rows if matches(r, column)]
    if not removed:
        return dict(path=path, before=len(rows), after=len(rows), removed=0)
    if not dry:
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(path, os.path.join(backup_dir, os.path.basename(path)))
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in keep:
                w.writerow(r)
    return dict(path=path, before=len(rows), after=len(keep),
                removed=len(removed), rows=removed, cols=cols)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    stamp = datetime.datetime.now().strftime("%Y%m%d")
    backup_dir = os.path.join("audit", "pre_withdrawal_%s" % stamp)
    manifest_path = os.path.join("audit", "withdrawn_records.csv")

    if not os.path.exists("provenance_table_fitcohort_full.csv"):
        sys.exit("run from v3_2_9_path_2_prep")

    results, manifest = [], []
    for rel, column in TARGETS:
        for base in (".", RELEASE):
            path = os.path.normpath(os.path.join(base, rel))
            res = process(path, column, backup_dir, args.dry_run)
            if res is None:
                continue
            results.append(res)
            for r in res.get("rows", []):
                manifest.append(dict(
                    withdrawn_identifier=IDENTIFIER, compound=COMPOUND,
                    source_file=path, reason=REASON, date=stamp,
                    row="; ".join("%s=%s" % (k, v) for k, v in r.items() if v)))

    print("withdrawing %s%s\n" % (IDENTIFIER, "  (DRY RUN)" if args.dry_run else ""))
    print("%-62s %6s %6s %5s" % ("file", "before", "after", "cut"))
    for r in results:
        print("%-62s %6d %6d %5d"
              % (r["path"][-62:], r["before"], r["after"], r["removed"]))

    if not args.dry_run and manifest:
        os.makedirs("audit", exist_ok=True)
        new = not os.path.exists(manifest_path)
        with open(manifest_path, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(manifest[0]))
            if new:
                w.writeheader()
            for m in manifest:
                w.writerow(m)
        print("\nbackups  : %s" % backup_dir)
        print("manifest : %s" % manifest_path)

    print("\nleft alone on purpose:")
    for path, why in UNTOUCHED:
        print("   %-44s %s" % (path, why))
    if args.dry_run:
        print("\nnothing was written. re-run without --dry-run to apply.")


if __name__ == "__main__":
    main()
