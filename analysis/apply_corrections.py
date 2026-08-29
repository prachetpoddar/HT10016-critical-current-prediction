#!/usr/bin/env python3
"""
apply_corrections.py

The data corrections for the HT10016 revision, in one place, so the same
definition can be applied to a regeneration sandbox and later to the real tree.

Three corrections, each traced to the source paper.

1. Withdraw 10.1016/0921-4534(94)00021-2 (Maignan et al., Physica C 243 (1995)
   214). Recorded as Hg0.8V0.2Ba2Ca2Cu3O8 with a 134 K anchor. The paper
   synthesises Hg-1201 and Hg-1212 and reports 90, 115 and 124 K; neither that
   stoichiometry nor "134" appears in it, and 134 K is the literature value for
   Hg-1223, a phase the paper never made.

2. Withdraw 10.1016/S0011-2275(97)00151-3 (Martinez and Duchateau, Cryogenics 37
   (1997) 865). The twelve recorded "Jc" values, 6 to 45, are Kramer currents
   read off the Kramer plot of Fig. 5, whose axis is I_k in A^0.5 T^0.25, not a
   critical current density. Nb3Sn carries of order 1e5 A/cm2, so the recorded
   values are the wrong quantity rather than the wrong scale, and the field range
   runs to 25 T where the measured points stop near 18 T.

3. Correct 10.1038/s41598-022-24044-5 (Piperno et al., Sci. Rep. 13 (2023) 569).
   The digitized figure axis is Jc in MA/cm2 and the wide-to-long converter
   copied the plot coordinates into a column named Jc_A_per_cm2 with no
   conversion, so the record carries about 1 A/cm2 instead of about 1e6. The same
   record is labelled sample_form=wire; the paper is titled "High-performance
   Fe(Se,Te) films on chemical CeO2-based buffer layers" and describes a thin
   film on a buffered substrate throughout. Both the units and the label are
   corrected, in the source tables and in the provenance table.

Correction 3 is guarded so that re-running does not multiply twice.

    python apply_corrections.py --root <path> --dry-run
    python apply_corrections.py --root <path>

--root defaults to the SuperconductorWorkflow directory above the working
directory. Point it at a sandbox first.
"""
import argparse, csv, datetime, os, shutil, sys

PREP_REL = os.path.join("kappa_pipeline", "analysis", "v3_2_9_path_2_prep")
AGENT_REL = "data_agent2"

WITHDRAWALS = [
    dict(identifier="10.1016/0921-4534(94)00021-2",
         tokens=["10.1016/0921-4534(94)00021-2",
                 "elsevier_10.1016_0921-4534(94)00021-2",
                 "Hg0.8V0.2Ba2Ca2Cu3O8"],
         reason="compound and 134 K anchor absent from the source paper"),
    dict(identifier="10.1016/S0011-2275(97)00151-3",
         # Not matched on compound: Nb3Sn appears in other records.
         tokens=["10.1016/S0011-2275(97)00151-3",
                 "elsevier_10.1016_S0011-2275(97)00151-3"],
         reason="recorded Jc values are Kramer currents (A^0.5 T^0.25) from the "
                "Kramer plot, not a critical current density"),
]

UNIT_FIX = dict(
    identifier="10.1038/s41598-022-24044-5",
    tokens=["10.1038/s41598-022-24044-5", "springer_10.1038_s41598-022-24044-5"],
    column="Jc_A_per_cm2",
    factor=1e6,
    guard_below=1e3,          # only scale a record still carrying MA-scale values
    sample_form_from="wire",
    sample_form_to="thin_film",
    reason="figure axis is MA/cm2 and the converter applied no unit conversion; "
           "paper describes a thin film on a buffered substrate, not a wire",
)

# Files carrying rows to withdraw or correct. Raw per-paper digitizations are
# listed too, since they feed the consolidated table.
TARGETS = [
    (AGENT_REL, "agent2_dataset_v3_2_2B.csv"),
    (PREP_REL, "provenance_table_fitcohort_full.csv"),
    (PREP_REL, "phase_3_form3_fits_partial_cohortB_v2.csv"),
    (PREP_REL, "beta_H_logJc0_identifiability_diagnostic.csv"),
    (PREP_REL, "phase_3_p18_compositional_descriptors_cohortB.csv"),
    (PREP_REL, "phase_3_p31_jc_anchor_per_paper.csv"),
]


def blob(row):
    return "\x1f".join(str(v) for v in row.values())


def read(path):
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        return rd.fieldnames, list(rd)


def write(path, cols, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, AGENT_REL)) and \
                os.path.isdir(os.path.join(d, PREP_REL)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            sys.exit("cannot find SuperconductorWorkflow above %s" % start)
        d = parent


def long_files(root):
    out = []
    ext = os.path.join(root, AGENT_REL, "v3_2_2B_extension")
    if os.path.isdir(ext):
        for f in sorted(os.listdir(ext)):
            if f.endswith("_LONG.csv"):
                out.append((os.path.join(AGENT_REL, "v3_2_2B_extension"), f))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root) if args.root else find_root(os.getcwd())
    stamp = datetime.datetime.now().strftime("%Y%m%d")
    backup = os.path.join(root, PREP_REL, "audit", "pre_corrections_%s" % stamp)

    print("root    : %s%s" % (root, "   (DRY RUN)" if args.dry_run else ""))
    print()
    targets = TARGETS + long_files(root)
    report = []

    for rel_dir, name in targets:
        path = os.path.join(root, rel_dir, name)
        if not os.path.exists(path):
            continue
        cols, rows = read(path)
        if not cols:
            continue
        original = len(rows)
        cut = 0
        for wd in WITHDRAWALS:
            before = len(rows)
            rows = [r for r in rows
                    if not any(t in blob(r) for t in wd["tokens"])]
            cut += before - len(rows)

        scaled = relabelled = 0
        col = UNIT_FIX["column"]
        if col in cols:
            for r in rows:
                if not any(t in blob(r) for t in UNIT_FIX["tokens"]):
                    continue
                try:
                    v = float(r[col])
                except (TypeError, ValueError):
                    v = None
                if v is not None and 0 < v < UNIT_FIX["guard_below"]:
                    r[col] = repr(v * UNIT_FIX["factor"])
                    scaled += 1
        if "sample_form" in cols:
            for r in rows:
                if any(t in blob(r) for t in UNIT_FIX["tokens"]) and \
                        r.get("sample_form") == UNIT_FIX["sample_form_from"]:
                    r["sample_form"] = UNIT_FIX["sample_form_to"]
                    relabelled += 1

        if not (cut or scaled or relabelled):
            continue
        # A per-paper extraction emptied by a withdrawal is the evidence for that
        # withdrawal, so it is moved aside rather than blanked. It also feeds the
        # regeneration chain, which reads this directory, so it cannot stay where
        # it is either.
        moved = name.endswith("_LONG.csv") and not rows
        report.append((os.path.join(rel_dir, name), original, len(rows),
                       cut, scaled, relabelled, moved))
        if args.dry_run:
            continue
        os.makedirs(backup, exist_ok=True)
        shutil.copy2(path, os.path.join(backup, name))
        if moved:
            aside = os.path.join(os.path.dirname(path), "withdrawn")
            os.makedirs(aside, exist_ok=True)
            shutil.move(path, os.path.join(aside, name))
        else:
            write(path, cols, rows)

    print("%-58s %6s %6s %5s %6s %5s %s"
          % ("file", "before", "after", "cut", "scaled", "label", ""))
    for name, a, b, cut, sc, rl, moved in report:
        print("%-58s %6d %6d %5d %6d %5d %s"
              % (name[-58:], a, b, cut, sc, rl,
                 "-> withdrawn/" if moved else ""))
    if not report:
        print("   nothing matched; corrections may already be applied")

    print("\nwithdrawn:")
    for wd in WITHDRAWALS:
        print("   %-38s %s" % (wd["identifier"], wd["reason"]))
    print("\ncorrected:")
    print("   %-38s %s" % (UNIT_FIX["identifier"], UNIT_FIX["reason"]))

    if not args.dry_run and report:
        print("\nbackups: %s" % backup)
    if args.dry_run:
        print("\nnothing was written.")


if __name__ == "__main__":
    main()
