#!/usr/bin/env python3
"""Rebuild Tables S1, S4 and S5 in the supplement from the surviving records.

This answers A1. Referee A asked for examples from the dataset and was invited
to check them against the source figures. Table S4 printed twelve anchor rows
and Table S5 seven fit rows, and by 2026-09-05 six of the twelve and five of
the seven came from records that three separate withdrawal ledgers had removed.
The invitation was to check the part of the deposit that fails.

Table S1 is rebuilt in the same pass for a different reason: it summed the
provenance table without reading the disposition column that
apply_provenance_status.py added, so it printed 62 papers, 38 compounds and
4146 points against Table I's corrected 50, 35 and 3303, in the same document.

Nothing here is written by hand. analysis/build_supplement_tables.py holds the
selection rule for each table and now reads every withdrawal ledger in the
repository and the repaired anchor and fit tables, so the rows are chosen by
the same rules on a cohort that exists. What changed in the tables is therefore
the cohort, not the rule.

The shapes must match the document exactly. If a rebuilt table has a different
number of rows or columns than the one it replaces, the run refuses: silently
writing a shorter table would leave stale rows below it.

    python analysis/apply_supplement_table_rebuild_20260905.py --dry-run
    python analysis/apply_supplement_table_rebuild_20260905.py --out-dir out_a1

Run from the repository root.
"""
import argparse
import json
import os
import subprocess
import sys

import docx

SRC = "out_regimes"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final6.docx"
# document table index -> key in the generator's output
TABLES = {0: "S1", 3: "S4", 4: "S5"}

# The prose around the two worked-example tables describes rows that are gone.
PROSE = [
    ("The five rows from ceramint.2024.10.058 show what conditioning is for: "
     "five bulk specimens of the same compound from the same paper, differing "
     "only in processing atmosphere, span 0.26 dex. The two rows from "
     "mtphys.2022.100783 show the sample-form effect within one paper.",
     "The four rows from jallcom.2013.04.183 show the processing spread the "
     "diagnostic is meant to detect: four bulk specimens of the same compound "
     "from the same paper, differing only in substitution level, span 0.15 "
     "dex, and the four from matchemphys.2023.128348 span 0.25 dex. No "
     "surviving paper shows the sample-form contrast this table was built to "
     "show. Of the 22 papers with anchor records after the withdrawals of "
     "Sec. 14, not one contributes more than a single sample form, so a "
     "within-paper comparison of forms cannot be drawn from any of them. That "
     "is the same limitation Sec. III.A reports for the diagnostic itself, "
     "visible here at the level of one table.",
     "the Table S4 examples"),
    ("the 96-row file behind the variance-decomposition diagnostic of "
     "Sec. III.A of the main text. One row is one isotherm record, a single "
     "sample from one paper at one measurement temperature, so the 96 rows "
     "cover 60 physical samples.",
     "the file behind the variance-decomposition diagnostic of Sec. III.A of "
     "the main text, which held 96 rows covering 60 physical samples and holds "
     "70 after the anchor repairs of Sec. 14. One row is one isotherm record, "
     "a single sample from one paper at one measurement temperature. The "
     "excerpt is drawn from the 61 of those rows whose source paper is not "
     "withdrawn by any ledger, which is a stricter rule than the diagnostic "
     "applies and is used here because a worked example exists to be checked "
     "against its source.",
     "the Table S4 caption on the file size"),
    ("the first three rows are wire, single crystal, and polycrystal "
     "respectively.",
     "the first three rows are single crystal, polycrystal and bulk "
     "respectively.",
     "the Table S5 form note"),
    ("Table S5 is an excerpt from phase_3_form3_fits_partial_cohortB_v2.csv.",
     "Table S5 is an excerpt from phase_3_form3_fits_partial_cohortB_v2.csv, "
     "restricted to fits whose source paper is not withdrawn by any ledger.",
     "the Table S5 source note"),
]


def build():
    out = os.path.join("audit", "supplement_tables_20260905.json")
    subprocess.run([sys.executable, "analysis/build_supplement_tables.py",
                    "--json", out], check=True, capture_output=True)
    return json.load(open(out))


def replace_in_paragraph(p, find, repl):
    text = "".join(r.text for r in p.runs)
    if find not in text:
        return False
    start = text.index(find)
    end = start + len(find)
    pos, first, spans = 0, None, []
    for r in p.runs:
        x, y = pos, pos + len(r.text)
        if y > start and x < end:
            spans.append((r, max(start, x) - x, min(end, y) - x))
            if first is None:
                first = r
        pos = y
    if first is None:
        return False
    for r, i, j in spans:
        r.text = r.text[:i] + (repl if r is first else "") + r.text[j:]
    return True


def set_cell(cell, text):
    """Replace a cell's text, keeping the first run's formatting."""
    p = cell.paragraphs[0]
    if not p.runs:
        p.add_run("")
    p.runs[0].text = str(text)
    for r in p.runs[1:]:
        r.text = ""
    for extra in cell.paragraphs[1:]:
        for r in extra.runs:
            r.text = ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    tables = build()
    d = docx.Document(os.path.join(SRC, SUPP))
    fails = []
    for ti, key in TABLES.items():
        rows = tables[key]
        t = d.tables[ti]
        want_rows, want_cols = len(rows) + 1, len(rows[0])
        print("Table %s: document %d rows x %d cols, rebuilt %d x %d"
              % (key, len(t.rows), len(t.columns), want_rows, want_cols))
        if len(t.rows) != want_rows or len(t.columns) != want_cols:
            fails.append("%s: shape %dx%d against the document's %dx%d"
                         % (key, want_rows, want_cols, len(t.rows),
                            len(t.columns)))
    if fails:
        print("\nShapes do not match. Nothing written.")
        for f in fails:
            print("  ", f)
        return 1

    missed = [why for find, repl, why in PROSE
              if not any(replace_in_paragraph(p, find, repl)
                         for p in d.paragraphs)]
    if missed:
        print("\nProse edits that found no target. Nothing written.")
        for m in missed:
            print("  ", m)
        return 1
    print("prose edits applied: %d" % len(PROSE))

    changed = 0
    for ti, key in TABLES.items():
        t = d.tables[ti]
        for i, row in enumerate(tables[key], start=1):
            for j, v in enumerate(row.values()):
                if t.rows[i].cells[j].text.strip() != str(v):
                    changed += 1
                set_cell(t.rows[i].cells[j], v)
    print("\ncells rewritten with a different value: %d" % changed)

    # No withdrawn identifier may appear anywhere in the three tables. The
    # generator asserts this over its own rows; this asserts it over the
    # document, which is what a referee reads.
    sys.path.insert(0, os.path.abspath("analysis"))
    import build_supplement_tables as bst          # noqa: E402
    banned = bst.withdrawn_tokens()
    stale = []
    for ti in TABLES:
        for r in d.tables[ti].rows:
            for c in r.cells:
                for b in banned:
                    if b and b in c.text:
                        stale.append((TABLES[ti], b))
    if stale:
        print("\nA withdrawn identifier is still in a table. Nothing written.")
        for s in sorted(set(stale)):
            print("  ", s)
        return 1
    print("no withdrawn identifier appears in S1, S4 or S5")

    if a.dry_run or not a.out_dir:
        print("\ndry run: nothing written")
        return 0
    os.makedirs(a.out_dir, exist_ok=True)
    d.save(os.path.join(a.out_dir, SUPP.replace("_final6", "_final7")))
    print("\nwritten to %s" % a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
