#!/usr/bin/env python3
"""
map_dependencies.py

Works out which tables sit downstream of a set of edited ones, and in what order
their generators have to be re-run.

Withdrawing a record from a source table does not propagate on its own. The
withdrawal of 10.1016/0921-4534(94)00021-2 cut four rows from
phase_3_p18_compositional_descriptors_cohortB.csv, but the file derived from it,
phase_3_p18_substructure_descriptor_means.csv, still carried a cuprate_HBCCO row
with four fits, so anything reading the means file still saw the withdrawn
family. That is one instance of a general problem, and patching outputs by hand
is how a table ends up disagreeing with the data it claims to summarise.

This reads every script in the folder, records which CSV files each one reads and
writes, and reports the transitive closure downstream of the seed tables together
with a topological re-run order. It changes nothing.

Resolution is static and therefore incomplete: paths built at runtime, or passed
in as arguments, cannot be resolved and are reported separately rather than
silently dropped. Treat the output as a map to check, not an authority.

    python map_dependencies.py
    python map_dependencies.py --seed some_other_table.csv
"""
import argparse, ast, csv, glob, os, sys
from collections import defaultdict, deque

DEFAULT_SEEDS = [
    "provenance_table_fitcohort_full.csv",
    "phase_3_form3_fits_partial_cohortB_v2.csv",
    "beta_H_logJc0_identifiability_diagnostic.csv",
    "phase_3_p18_compositional_descriptors_cohortB.csv",
    "phase_3_p31_jc_anchor_per_paper.csv",
]
OUT = os.path.join("audit", "dependency_map.csv")
READERS = {"read_csv", "DictReader", "reader"}
WRITERS = {"to_csv", "DictWriter", "writer"}


def literals(node, consts):
    """Every .csv basename this expression could denote."""
    found = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str) \
                and sub.value.endswith(".csv"):
            found.append(os.path.basename(sub.value))
        elif isinstance(sub, ast.Name) and sub.id in consts:
            v = consts[sub.id]
            if v.endswith(".csv"):
                found.append(os.path.basename(v))
    return found


def scan(path):
    """Return (reads, writes, unresolved) for one script."""
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except SyntaxError:
        return set(), set(), ["unparseable"]

    # Paths are commonly assembled rather than written whole: PREP / "x.csv",
    # os.path.join(DIR, "x.csv"), f-strings. Take any .csv string anywhere inside
    # the assigned expression.
    consts = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            continue
        for sub in ast.walk(node.value):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str) \
                    and sub.value.endswith(".csv"):
                consts[node.targets[0].id] = sub.value
                break

    reads, writes, unresolved = set(), set(), []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = (node.func.attr if isinstance(node.func, ast.Attribute)
                else node.func.id if isinstance(node.func, ast.Name) else "")
        if name == "open":
            mode = "r"
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = str(node.args[1].value)
            for kw in node.keywords or []:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = str(kw.value.value)
            hits = literals(node.args[0], consts) if node.args else []
            target = writes if any(m in mode for m in "wax") else reads
            target.update(hits)
        elif name in READERS or name in WRITERS:
            hits = []
            for a in list(node.args) + [k.value for k in (node.keywords or [])]:
                hits += literals(a, consts)
            if not hits and node.args:
                unresolved.append(name)
            (writes if name in WRITERS else reads).update(hits)
    return reads, writes, unresolved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", action="append", default=None)
    args = ap.parse_args()
    seeds = [os.path.basename(s) for s in (args.seed or DEFAULT_SEEDS)]

    if not os.path.exists("provenance_table_fitcohort_full.csv"):
        sys.exit("run from v3_2_9_path_2_prep")

    produced_by = defaultdict(set)     # csv -> scripts that write it
    consumed_by = defaultdict(set)     # csv -> scripts that read it
    script_reads, script_writes = {}, {}
    unresolved = {}

    for path in sorted(glob.glob("*.py")):
        r, w, u = scan(path)
        script_reads[path], script_writes[path] = r, w
        if u:
            unresolved[path] = u
        for f in r:
            consumed_by[f].add(path)
        for f in w:
            produced_by[f].add(path)

    # Breadth-first over "table -> script that reads it -> tables it writes".
    depth = {s: 0 for s in seeds}
    order, queue = [], deque(seeds)
    while queue:
        table = queue.popleft()
        for script in sorted(consumed_by.get(table, ())):
            for out in sorted(script_writes.get(script, ())):
                if out in depth:
                    continue
                depth[out] = depth[table] + 1
                order.append((depth[out], out, script))
                queue.append(out)

    os.makedirs("audit", exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["depth", "table", "regenerated_by", "also_read_by", "exists"])
        for s in seeds:
            w.writerow([0, s, "(edited directly)",
                        " ".join(sorted(consumed_by.get(s, ()))),
                        os.path.exists(s)])
        for d, table, script in sorted(order):
            w.writerow([d, table, script,
                        " ".join(sorted(consumed_by.get(table, ()))),
                        os.path.exists(table)])

    print("scripts scanned      : %d" % len(script_reads))
    print("tables downstream    : %d\n" % len(order))
    print("seed tables (edited directly):")
    for s in seeds:
        readers = sorted(consumed_by.get(s, ()))
        makers = sorted(produced_by.get(s, ()))
        print("   %s" % s)
        print("        read by   : %s" % (", ".join(readers) or "nothing found"))
        print("        written by: %s" % (", ".join(makers) or "nothing found"))
        for mk in makers:
            ins = sorted(script_reads.get(mk, ()))
            print("           ! re-running %s rebuilds this table from: %s"
                  % (mk, ", ".join(ins) or "unresolved inputs"))

    if order:
        print("\nre-run order, shallowest first. Each line regenerates the table")
        print("named from inputs already corrected by the lines above it.\n")
        print("   %-5s %-52s %s" % ("depth", "table", "regenerated by"))
        for d, table, script in sorted(order):
            mark = "" if os.path.exists(table) else "   [not on disk]"
            print("   %-5d %-52s %s%s" % (d, table[:52], script, mark))
    else:
        print("\nNothing downstream resolved statically. That is unlikely to be")
        print("true, so check the unresolved list below before trusting it.")

    if unresolved:
        print("\npaths this pass could not resolve, so their edges are missing:")
        for path, kinds in sorted(unresolved.items())[:20]:
            print("   %-52s %s" % (path, ", ".join(sorted(set(kinds)))))

    rebuilt = [s for s in seeds if produced_by.get(s)]
    if rebuilt:
        print("\nWARNING: %d of the seed tables are themselves generated." % len(rebuilt))
        print("Re-running their generator rebuilds them from upstream. That")
        print("re-applies the correction only where the upstream inputs were")
        print("also corrected; otherwise it silently restores the withdrawn rows.")
        print("Check each generator's inputs above before running it.")

    print("\nwritten to %s" % OUT)


if __name__ == "__main__":
    main()
