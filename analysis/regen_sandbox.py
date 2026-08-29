#!/usr/bin/env python3
"""
regen_sandbox.py

Propagates a withdrawal through the derived tables without writing to the real
tree, then reports which differences the withdrawal actually explains.

Why a sandbox. Hand-editing derived tables does not propagate and can be undone:
three of the tables corrected for the withdrawal of
10.1016/0921-4534(94)00021-2 are themselves generated, and their generators read
agent2_dataset_v3_2_2B.csv, which still holds that record's 20 extracted points.
Re-running any of them in place would restore what was withdrawn. Seventy-six
tables sit downstream, so patching outputs by hand is not an option either.

Why not just re-run in place. The chain regenerates phase_3_p31_variance_
decomposition.csv, the source of the paper's central diagnostic. Any drift
accumulated since those files were last generated would surface now and read as
though the withdrawal caused it. Running into a sandbox and diffing separates
the two.

The generators hardcode the repository root, so the copies have that literal
rewritten to point at the sandbox. Only .csv, .py and .json are copied; the
2.8 GB of PDFs are not needed by this chain.

    python regen_sandbox.py setup      # build the sandbox, apply the withdrawal
    ...run the chain inside it, order printed by setup...
    python regen_sandbox.py diff       # compare sandbox against the real tree

Nothing here writes to the real tables. Promoting a sandbox result is a separate,
deliberate copy.
"""
import argparse, csv, datetime, os, re, shutil, sys

REAL_ROOT_LITERAL = "/Users/prachetpoddar/Documents/SuperconductorWorkflow"
PREP_REL = os.path.join("kappa_pipeline", "analysis", "v3_2_9_path_2_prep")
AGENT_REL = "data_agent2"
SOURCE_TABLE = "agent2_dataset_v3_2_2B.csv"

IDENTIFIER = "10.1016/0921-4534(94)00021-2"
UNDERSCORED = "elsevier_10.1016_0921-4534(94)00021-2"
COMPOUND = "Hg0.8V0.2Ba2Ca2Cu3O8"

CHAIN = [
    "phase_3_p18_form3_fits_partial_v2.py",
    "beta_H_identifiability_diagnostic.py",
    "phase_3_p18_cohort_b_electronegativity_analysis.py",
    "phase_3_p31_jc_anchor_sample_form_conditional.py",
]
COPY_EXT = (".csv", ".py", ".json")


def find_real_root():
    d = os.path.abspath(os.getcwd())
    while True:
        if os.path.isdir(os.path.join(d, AGENT_REL)) and \
                os.path.isdir(os.path.join(d, PREP_REL)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            sys.exit("run from v3_2_9_path_2_prep inside SuperconductorWorkflow")
        d = parent


def sandbox_path(real_root, stamp):
    return os.path.join(real_root, "_regen_sandbox_%s" % stamp)


def copy_tree(src, dst):
    n = 0
    for base, _dirs, files in os.walk(src):
        rel = os.path.relpath(base, src)
        for f in files:
            if not f.endswith(COPY_EXT):
                continue
            out_dir = os.path.normpath(os.path.join(dst, rel))
            os.makedirs(out_dir, exist_ok=True)
            shutil.copy2(os.path.join(base, f), os.path.join(out_dir, f))
            n += 1
    return n


def hits(row):
    blob = "\x1f".join(str(v) for v in row.values())
    return IDENTIFIER in blob or UNDERSCORED in blob or COMPOUND in blob


def withdraw(path):
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        cols = rd.fieldnames
        rows = list(rd)
    keep = [r for r in rows if not hits(r)]
    cut = len(rows) - len(keep)
    if cut:
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in keep:
                w.writerow(r)
    return len(rows), cut


# Substituting an absolute sandbox path would bind the copies to whichever
# machine ran setup, and this tree is reachable under two different absolute
# paths. Derive the root from the script's own location instead: a generator
# lives at <root>/kappa_pipeline/analysis/v3_2_9_path_2_prep/, three levels down.
DYNAMIC_ROOT = ('Path(__file__).resolve().parents[3]  '
                '# rewritten by regen_sandbox.py: sandbox root, not the real tree')


def rewrite_roots(sb):
    """Replace any absolute root with the dynamic form. Both the real tree's
    literal and the sandbox's own absolute path are handled, the latter because
    an earlier version of this script substituted one, and that path is only
    valid on the machine that ran it."""
    roots = [REAL_ROOT_LITERAL, os.path.abspath(sb)]
    n = 0
    for base, _d, files in os.walk(sb):
        for f in files:
            if not f.endswith(".py"):
                continue
            fp = os.path.join(base, f)
            src = open(fp, encoding="utf-8", errors="replace").read()
            out = src
            for root in roots:
                if root not in out:
                    continue
                out = re.sub(r'Path\(\s*["\']%s["\']\s*\)' % re.escape(root),
                             DYNAMIC_ROOT, out)
                out = out.replace('"%s"' % root, "str(%s)" % DYNAMIC_ROOT)
                out = out.replace("'%s'" % root, "str(%s)" % DYNAMIC_ROOT)
            if out != src:
                open(fp, "w", encoding="utf-8").write(out)
                n += 1
    return n


def cmd_rewrite(real_root, stamp):
    sb = sandbox_path(real_root, stamp)
    if not os.path.isdir(sb):
        sys.exit("no sandbox at %s" % sb)
    print("rewrote %d scripts in %s" % (rewrite_roots(sb), sb))
    leftovers = []
    for base, _d, files in os.walk(sb):
        for f in files:
            if not f.endswith(".py"):
                continue
            body = open(os.path.join(base, f), encoding="utf-8",
                        errors="replace").read()
            if REAL_ROOT_LITERAL in body or os.path.abspath(sb) in body:
                leftovers.append(os.path.relpath(os.path.join(base, f), sb))
    print("scripts still naming the real tree: %d" % len(leftovers))
    for l in leftovers[:10]:
        print("   %s" % l)


def cmd_setup(real_root, stamp):
    sb = sandbox_path(real_root, stamp)
    if os.path.exists(sb):
        sys.exit("%s already exists; use it or pick another day" % sb)
    n1 = copy_tree(os.path.join(real_root, PREP_REL), os.path.join(sb, PREP_REL))
    n2 = copy_tree(os.path.join(real_root, AGENT_REL), os.path.join(sb, AGENT_REL))
    print("sandbox : %s" % sb)
    print("copied  : %d files from the prep folder, %d from data_agent2" % (n1, n2))

    print("rewrote : %d scripts to point at the sandbox" % rewrite_roots(sb))

    src_table = os.path.join(sb, AGENT_REL, SOURCE_TABLE)
    if not os.path.exists(src_table):
        sys.exit("cannot find %s in the sandbox" % SOURCE_TABLE)
    before, cut = withdraw(src_table)
    print("source  : %s  %d rows, %d withdrawn" % (SOURCE_TABLE, before, cut))

    still = []
    for base, _d, files in os.walk(os.path.join(sb, AGENT_REL)):
        for f in files:
            if not f.endswith(".csv") or f == SOURCE_TABLE:
                continue
            try:
                rows = list(csv.DictReader(open(os.path.join(base, f), newline="")))
            except Exception:
                continue
            if any(hits(r) for r in rows):
                still.append(os.path.relpath(os.path.join(base, f), sb))
    if still:
        print("\nstill carrying the record in the sandbox, by design or otherwise:")
        for s in still:
            print("   %s" % s)
        print("   (the per-paper extraction is kept as the evidence for the")
        print("    withdrawal; check nothing else here feeds the chain)")

    print("\nrun the chain inside the sandbox, in this order:\n")
    print("   cd %s" % os.path.join(sb, PREP_REL))
    for s in CHAIN:
        print("   python %s" % s)
    print("\nthen, from the real prep folder:  python regen_sandbox.py diff")


def load(path):
    try:
        with open(path, newline="") as fh:
            rd = csv.reader(fh)
            rows = list(rd)
        return rows[0] if rows else [], [tuple(r) for r in rows[1:]]
    except Exception:
        return None, None


def cmd_diff(real_root, stamp):
    sb = sandbox_path(real_root, stamp)
    if not os.path.isdir(sb):
        sys.exit("no sandbox at %s; run setup first" % sb)

    same, explained, unexplained, only_one_side = [], [], [], []
    for rel_base in (PREP_REL, AGENT_REL):
        for base, _d, files in os.walk(os.path.join(sb, rel_base)):
            for f in sorted(files):
                if not f.endswith(".csv"):
                    continue
                sp = os.path.join(base, f)
                rel = os.path.relpath(sp, sb)
                rp = os.path.join(real_root, rel)
                sh, sr = load(sp)
                rh, rr = load(rp)
                if sr is None or rr is None:
                    only_one_side.append((rel, "sandbox only" if rr is None
                                          else "real tree only"))
                    continue
                if sh == rh and sr == rr:
                    same.append(rel)
                    continue
                removed = [r for r in rr if r not in set(sr)]
                added = [r for r in sr if r not in set(rr)]
                blob = lambda t: "\x1f".join(str(v) for v in t)
                touched = [r for r in removed
                           if IDENTIFIER in blob(r) or UNDERSCORED in blob(r)
                           or COMPOUND in blob(r)]
                rec = (rel, len(rr), len(sr), len(removed), len(added), len(touched))
                if removed and not added and len(touched) == len(removed):
                    explained.append(rec)
                else:
                    unexplained.append(rec)

    print("identical                       : %d" % len(same))
    print("differ, withdrawal explains it  : %d" % len(explained))
    print("differ, NOT explained           : %d" % len(unexplained))
    print("present on one side only        : %d\n" % len(only_one_side))

    if explained:
        print("explained by the withdrawal:")
        print("   %-56s %6s %6s %5s" % ("table", "real", "new", "cut"))
        for rel, a, b, rm, ad, _t in explained:
            print("   %-56s %6d %6d %5d" % (rel[-56:], a, b, rm))
    if unexplained:
        print("\nNOT explained by the withdrawal. Read every one of these before")
        print("promoting anything; each is drift the withdrawal does not account for.\n")
        print("   %-48s %6s %6s %5s %5s %5s"
              % ("table", "real", "new", "gone", "new+", "ofrec"))
        for rel, a, b, rm, ad, t in unexplained:
            print("   %-48s %6d %6d %5d %5d %5d" % (rel[-48:], a, b, rm, ad, t))
    if only_one_side:
        print("\npresent on one side only:")
        for rel, which in only_one_side:
            print("   %-62s %s" % (rel[-62:], which))
    print("\nNothing was promoted. Copy files out of the sandbox deliberately,")
    print("one at a time, once you have read the differences above.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["setup", "rewrite", "diff"])
    ap.add_argument("--stamp", default=datetime.datetime.now().strftime("%Y%m%d"))
    args = ap.parse_args()
    real_root = find_real_root()
    {"setup": cmd_setup, "rewrite": cmd_rewrite,
     "diff": cmd_diff}[args.command](real_root, args.stamp)


if __name__ == "__main__":
    main()
