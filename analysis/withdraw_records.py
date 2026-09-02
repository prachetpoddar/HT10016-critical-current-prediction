#!/usr/bin/env python3
"""
withdraw_records.py

Withdraws source records from the deposited tables and regenerates everything
downstream of them in the same run.

Why this supersedes withdraw_record.py. That script removed a record from the
source tables and stopped. The derived table
phase_3_p31_variance_decomposition.csv was never regenerated, so the deposit
carried a decomposition computed from data that no longer existed: it reported
n = 77 and an aggregate ratio of 0.2876 against a source table that gives 76 and
0.3058, and it still listed a cuprate_HBCCO family for the withdrawn record.
A withdrawal that does not propagate leaves the deposit disagreeing with itself,
which is worse than not withdrawing at all, because the disagreement is silent.
Withdrawal and regeneration therefore happen here in one place and one command.

The register below is the whole set of withdrawn records. Each entry states the
identifier, the tokens that find it, and the reason, so that the deposit
documents its own exclusions rather than requiring a reader to reconstruct them
from commit messages.

Re-running is safe. A record already absent is reported as such and nothing is
written for it, so this can be run after any edit to confirm the deposit is
consistent.

    python analysis/withdraw_records.py --dry-run
    python analysis/withdraw_records.py

Run from the repository root.
"""
import argparse, csv, datetime, os, shutil, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

DATA = "data"
AUDIT = "audit"

REGISTER = [
    dict(
        identifier="10.1016/0921-4534(94)00021-2",
        tokens=["10.1016/0921-4534(94)00021-2",
                "elsevier_10.1016_0921-4534(94)00021-2",
                "Hg0.8V0.2Ba2Ca2Cu3O8"],
        citation="Maignan et al., Physica C 243 (1995) 214",
        reason=("recorded as Hg0.8V0.2Ba2Ca2Cu3O8 with a 134 K anchor. The paper "
                "synthesises Hg-1201 and Hg-1212 and reports 90, 115 and 124 K; "
                "neither that stoichiometry nor the string 134 appears in it, and "
                "134 K is the literature value for Hg-1223, a phase it never made"),
        withdrawn="2026-08-29",
    ),
    dict(
        identifier="10.1016/S0011-2275(97)00151-3",
        # Deliberately not matched on the compound: Nb3Sn appears in unrelated
        # rows of caption_sweep.csv, which is a screen over the retrieval archive
        # and is not part of the fitted cohort.
        tokens=["10.1016/S0011-2275(97)00151-3",
                "elsevier_10.1016_S0011-2275(97)00151-3"],
        citation="Martinez and Duchateau, Cryogenics 37 (1997) 865",
        reason=("the twelve recorded Jc values, 6 to 45, are Kramer currents read "
                "off the Kramer plot of Fig. 5, whose axis is I_k in A^0.5 T^0.25. "
                "That is a different physical quantity, not a mis-scaled one: "
                "Nb3Sn carries of order 1e5 A/cm2. The recorded field range also "
                "runs to 25 T where the measured points stop near 18 T"),
        withdrawn="2026-09-01",
    ),
    dict(
        identifier="10.1016/j.physc.2010.03.003",
        tokens=["10.1016/j.physc.2010.03.003",
                "elsevier_10.1016_j.physc.2010.03.003"],
        citation="Taen et al., Physica C 470 (2010) S391",
        reason=("the 25 recorded values are a log ladder. Three of the five "
                "isotherms fall by exactly 0.5000 dex per point across field "
                "intervals of 4.5, 10, 10 and 25 T, so the factor between "
                "consecutive points does not depend on how far the field moved. "
                "That is not a reading of a curve. The recorded field range also "
                "runs to 50 T against the record's own Hc2 of 47 T. The linear "
                "arithmetic screen did not see this because a Jc(H) figure is "
                "drawn on a log axis; analysis/audit_extraction_integrity.py now "
                "carries a log_ladder signature, which fires on this file and on "
                "no other in the corpus"),
        withdrawn="2026-09-01",
    ),
    dict(
        identifier="10.1016/j.physb.2025.417755",
        tokens=["10.1016/j.physb.2025.417755",
                "elsevier_10.1016_j.physb.2025.417755"],
        citation="Miglani and Varma, Physica B 716 (2025) 417755",
        reason=("the anchor records 2.0e6 A/cm2 at 2 K and self field for the "
                "as-grown crystal, where the paper states that the self-field Jc "
                "at 2 K for the as-grown sample is 1.4e5 A/cm2, a factor of 14. "
                "No internal signature fires on the five "
                "point series, so the alternative was to replace the anchor with "
                "the value the paper prints at exactly this condition, which is "
                "reading the paper rather than assuming a rescale. That was the "
                "recommended option and it was not taken. It is recorded here "
                "because the choice has a consequence: substituting 1.4e5 moves "
                "the iron chalcogenide ratio to 0.5793 and its pre-registered "
                "outcome from A to B, whereas withdrawal leaves it at 0.7687 and "
                "in A. A reader should be able to see that the option which "
                "preserves the pre-registered outcome is the one taken, and "
                "decide for themselves"),
        withdrawn="2026-09-01",
    ),
]

# Deposited tables that must not carry a withdrawn record.
TARGETS = [
    "phase_3_p31_jc_anchor_per_paper.csv",
    "provenance_table_fitcohort_full.csv",
    "phase_3_form3_fits_partial_cohortB_v2.csv",
    "phase_3_p57_de_novo_predictions.csv",
    "phase_3_p47_compound_leave_out_MAE.csv",
    "phase_3_p56_candidate_tier_assignment.csv",
    "phase_3_p44_post_UCLA_beta_T_fits.csv",
    "reduced_variable_scaling.csv",
]

# Left alone on purpose, and why. Each of these would be wrong to edit.
UNTOUCHED = [
    ("data/caption_sweep.csv",
     "a screen over the retrieval archive, not the fitted cohort; its Nb3Sn rows "
     "are unrelated arXiv papers and the withdrawn papers remain in the archive"),
    ("audit/*.csv",
     "audit outputs record the finding and must keep the withdrawn rows"),
    ("the raw per-paper extractions",
     "retained as the evidence for each withdrawal; an audit trail that deletes "
     "its own evidence is worth less than one that does not"),
]

DERIVED = "phase_3_p31_variance_decomposition.csv"


def blob(row):
    return "\x1f".join(str(v) for v in row.values())


def carries(row, rec):
    b = blob(row)
    return any(t in b for t in rec["tokens"])


def read(path):
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        return rd.fieldnames, list(rd)


def regenerate_decomposition(dry, corrected_rows=None, corrected_cols=None):
    """Rebuild the variance decomposition from the corrected anchor table.

    This is the step whose omission produced the stale deposit. It is not
    optional and is not behind a flag.

    Under --dry-run the anchor table on disk has not been edited, so reading it
    back would preview the decomposition of the UNCORRECTED cohort and report a
    number the real run will not produce. The corrected rows are therefore
    passed in and used directly, so the dry run previews what the real run does.
    """
    import pandas as pd
    from figure_4_source import (aggregate_per_physical_sample,
                                 compute_variance_decomposition)
    src = os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv")
    out = os.path.join(DATA, DERIVED)
    if corrected_rows is not None:
        df = pd.DataFrame(corrected_rows, columns=corrected_cols)
        for c in ("log10_Jc_anchor",):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    else:
        df = pd.read_csv(src)
    vd = compute_variance_decomposition(aggregate_per_physical_sample(df))
    stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    vd["note"] = vd["note"].fillna("")
    agg = vd["scope"] == "aggregate_all"
    vd.loc[agg, "note"] = (
        "derived from phase_3_p31_jc_anchor_per_paper.csv via "
        "analysis/figure_4_source.py (aggregate_per_physical_sample + "
        "compute_variance_decomposition); regenerated %s by "
        "analysis/withdraw_records.py" % stamp)
    before = None
    if os.path.exists(out):
        _c, rows = read(out)
        for r in rows:
            if r.get("scope") == "aggregate_all":
                before = (r.get("n_papers"), r.get("ratio_between_total"))
    a = vd[agg].iloc[0]
    after = (str(int(a.n_papers)), repr(float(a.ratio_between_total)))
    if not dry:
        vd.to_csv(out, index=False)
    return before, after, vd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not os.path.isdir(DATA):
        sys.exit("run from the repository root")

    stamp = datetime.datetime.now().strftime("%Y%m%d")
    backup = os.path.join(AUDIT, "pre_withdrawal_%s" % stamp)
    report, manifest = [], []
    anchor_rows = anchor_cols = None

    for name in TARGETS:
        path = os.path.join(DATA, name)
        if not os.path.exists(path):
            continue
        cols, rows = read(path)
        if not cols:
            continue
        keep, cut = rows, 0
        for rec in REGISTER:
            before = len(keep)
            removed = [r for r in keep if carries(r, rec)]
            keep = [r for r in keep if not carries(r, rec)]
            cut += before - len(keep)
            for r in removed:
                manifest.append(dict(
                    identifier=rec["identifier"], citation=rec["citation"],
                    source_file=path, withdrawn=rec["withdrawn"],
                    reason=rec["reason"],
                    row="; ".join("%s=%s" % (k, v) for k, v in r.items() if v)))
        if name == "phase_3_p31_jc_anchor_per_paper.csv":
            anchor_rows, anchor_cols = keep, cols
        if not cut:
            continue
        report.append((name, len(rows), len(keep), cut))
        if not args.dry_run:
            os.makedirs(backup, exist_ok=True)
            shutil.copy2(path, os.path.join(backup, name))
            with open(path, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols)
                w.writeheader()
                for r in keep:
                    w.writerow(r)

    print("withdrawal register%s\n" % ("   (DRY RUN)" if args.dry_run else ""))
    for rec in REGISTER:
        print("   %-32s %s" % (rec["identifier"], rec["citation"]))
    print()
    if report:
        print("%-52s %6s %6s %5s" % ("table", "before", "after", "cut"))
        for name, a, b, c in report:
            print("%-52s %6d %6d %5d" % (name[:52], a, b, c))
    else:
        print("no table carried a registered record; the deposit is already clean")
    print()

    before, after, vd = regenerate_decomposition(
        args.dry_run, anchor_rows, anchor_cols)
    print("regenerated %s" % DERIVED)
    if before:
        print("   aggregate before : n=%s ratio=%s" % before)
    print("   aggregate after  : n=%s ratio=%s" % after)
    print("   families now     : %s"
          % ", ".join(sorted(vd[vd.scope == "per_substructure"].substructure)))
    print()

    if manifest and not args.dry_run:
        os.makedirs(AUDIT, exist_ok=True)
        mpath = os.path.join(AUDIT, "withdrawn_records.csv")
        with open(mpath, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(manifest[0]))
            w.writeheader()
            for m in manifest:
                w.writerow(m)
        print("manifest: %s  (%d rows)" % (mpath, len(manifest)))
        print("backups : %s" % backup)

    print("\nleft alone on purpose:")
    for what, why in UNTOUCHED:
        print("   %-34s %s" % (what, why))
    if args.dry_run:
        print("\nnothing was written.")


if __name__ == "__main__":
    main()
