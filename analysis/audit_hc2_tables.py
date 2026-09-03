#!/usr/bin/env python3
"""Cross-table consistency checks on the upper critical field.

verify_deposit.py checks that one physical sample carries one sample form across
every table, and that the Jc anchor's two columns agree. It has no check of any
kind on Hc2, which is the other quantity carried in more than one deposited
table and the one whose provenance the field-axis result depends on. That gap is
why a paper could have its critical scale changed in the fit table this session
while the provenance table went on describing the old value.

Six checks, each on the deposit alone:

  1. A Tier-3 fit uses the literature default. If Hc2_T_used differs from
     Hc2_T_default while the source says Tier_3, one of the two is wrong.
  2. The provenance table's tier agrees with the fit table's tier, per paper.
  3. The provenance table's Hc2_anchor_T is one of the values the fits use for
     that paper. A paper resolving Hc2 per isotherm has several, so the test is
     membership rather than equality.
  4. The anchor table's Hc2_T agrees with the provenance table wherever the
     provenance is a literature catalog value or a Tier-3 default, and may
     differ only where the provenance is Tier 1 or Tier 2. The two columns hold
     different quantities in that case: the anchor table keeps the reference
     value for the compound and the provenance table keeps the value resolved
     from the paper, so requiring equality everywhere would fire on 37 rows
     that are behaving as designed. The first version of this check did exactly
     that, and the invariant above is what survived checking those rows.

  4b. The anchor table's Tc agrees with the provenance table, per paper and
     compound. Nothing else in the deposit compares them.
  5. Every Hc2 in every table is positive and below 250 T. Nothing measured in
     this corpus exceeds that, so anything above it is a unit or a parse error.
  6. No withdrawn record still carries an Hc2 anywhere.

    python analysis/audit_hc2_tables.py
"""
import csv
import os
import sys

DATA, AUDIT = "data", "audit"
CEILING_T = 250.0
failures = []


def load(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def check(label, ok, detail=""):
    print("   %-56s %s%s" % (label, "ok" if ok else "FAILED",
                             ("   " + detail) if detail else ""))
    if not ok:
        failures.append(label)


def tier_of(s):
    for t in ("Tier_1", "Tier_2", "Tier_3"):
        if s.startswith(t):
            return t
    return "other"


def prov_tier(s):
    s = (s or "").lower()
    if "literature catalog" in s:
        return "catalog"
    for t in ("tier_1", "tier_2", "tier_3"):
        if s.startswith(t):
            return t.title()
    return "other"


def main():
    fits = load(os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv"))
    prov = load(os.path.join(DATA, "provenance_table_fitcohort_full.csv"))
    anch = load(os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv"))

    print("upper-critical-field consistency across the deposited tables\n")

    # 1 --------------------------------------------------------------------
    bad = [r for r in fits if r["Hc2_source"].startswith("Tier_3")
           and num(r["Hc2_T_used"]) is not None
           and num(r["Hc2_T_default"]) is not None
           and abs(num(r["Hc2_T_used"]) - num(r["Hc2_T_default"])) > 1e-9]
    check("a Tier-3 fit uses the literature default", not bad,
          "%d fit(s) disagree" % len(bad) if bad else "%d Tier-3 fits" %
          sum(1 for r in fits if r["Hc2_source"].startswith("Tier_3")))

    # a paper identifier appears in three shapes across the tables
    def key(s):
        return (s.replace("elsevier_", "").replace("springer_", "")
                 .replace("iop_", "").replace("arxiv_", "")
                 .replace("_", "/").lower())

    fit_by_paper = {}
    for r in fits:
        fit_by_paper.setdefault(key(r["arxiv_id"]), []).append(r)

    # 2 --------------------------------------------------------------------
    mismatch = []
    for p in prov:
        k = key(p["identifier"])
        rs = fit_by_paper.get(k)
        if not rs:
            continue
        want = prov_tier(p["Hc2_provenance"])
        got = {tier_of(r["Hc2_source"]) for r in rs}
        if want in ("Tier_1", "Tier_2", "Tier_3") and want not in got:
            mismatch.append((p["identifier"], want, sorted(got)))
    check("the provenance tier matches the fit table's tier", not mismatch,
          "%d paper(s) disagree" % len(mismatch) if mismatch else "")
    for m in mismatch:
        print("      %-44s provenance %s, fits %s" % m)

    # 3 --------------------------------------------------------------------
    off = []
    for p in prov:
        k = key(p["identifier"])
        rs = fit_by_paper.get(k)
        v = num(p["Hc2_anchor_T"])
        if not rs or v is None:
            continue
        used = {round(num(r["Hc2_T_used"]), 4) for r in rs
                if num(r["Hc2_T_used"]) is not None}
        dflt = {round(num(r["Hc2_T_default"]), 4) for r in rs
                if num(r["Hc2_T_default"]) is not None}
        if round(v, 4) not in used | dflt:
            off.append((p["identifier"], v, sorted(used)[:4]))
    check("the provenance anchor is a value the fits actually use", not off,
          "%d paper(s) disagree" % len(off) if off else "")
    for o in off:
        print("      %-44s provenance %.4g, fits use %s" % o)

    # 4 --------------------------------------------------------------------
    prov_by = {}
    for p in prov:
        prov_by[(key(p["identifier"]), p["compound"].lower())] = p
    clash, tc_clash, seen = [], [], set()
    for a in anch:
        kk = (key(a["paper_id"]), a["compound_formula"].lower())
        p = prov_by.get(kk)
        if not p or kk in seen:
            continue
        seen.add(kk)
        h0, hr = num(a.get("Hc2_T")), num(p.get("Hc2_anchor_T"))
        tier = p.get("Hc2_provenance", "")
        resolved = tier.startswith("Tier_1") or tier.startswith("Tier_2")
        if (h0 is not None and hr is not None and not resolved
                and abs(h0 - hr) > 1e-6):
            clash.append((a["paper_id"], a["compound_formula"], h0, hr, tier[:34]))
        t1, t2 = num(a.get("Tc_K")), num(p.get("Tc_anchor_K"))
        if t1 is not None and t2 is not None and abs(t1 - t2) > 1e-6:
            tc_clash.append((a["paper_id"], a["compound_formula"], t1, t2))
    check("Hc2 agrees unless the provenance is Tier 1 or Tier 2", not clash,
          "%d paper(s) disagree" % len(clash) if clash else
          "%d joined rows" % len(seen))
    for c in clash:
        print("      %-42s %-20s anchor %g, provenance %g, %s" % c)
    check("Tc agrees between the anchor and provenance tables", not tc_clash,
          "%d paper(s) disagree" % len(tc_clash) if tc_clash else "")
    for c in tc_clash:
        print("      %-42s %-20s anchor %g, provenance %g" % c)

    # 5 --------------------------------------------------------------------
    outs = []
    for path, cols in (
            (os.path.join(DATA, "phase_3_form3_fits_partial_cohortB_v2.csv"),
             ("Hc2_T_used", "Hc2_T_default")),
            (os.path.join(DATA, "phase_3_p31_jc_anchor_per_paper.csv"), ("Hc2_T",)),
            (os.path.join(DATA, "provenance_table_fitcohort_full.csv"),
             ("Hc2_anchor_T",)),
            (os.path.join(DATA, "phase_3_p56_candidate_tier_assignment.csv"),
             ("Hc2_T",)),
            (os.path.join(DATA, "phase_3_p57_de_novo_predictions.csv"),
             ("Hc2_T_anchor",))):
        if not os.path.exists(path):
            continue
        for r in load(path):
            for c in cols:
                v = num(r.get(c))
                if v is not None and (v <= 0 or v > CEILING_T):
                    outs.append((os.path.basename(path), c, v))
    check("every Hc2 is positive and below %g T" % CEILING_T, not outs,
          "%d value(s) out of range" % len(outs) if outs else "")
    for o in outs[:10]:
        print("      %-46s %-16s %g" % o)

    # 6 --------------------------------------------------------------------
    wpath = os.path.join(AUDIT, "withdrawn_records.csv")
    survivors = []
    if os.path.exists(wpath):
        ids = [r["identifier"] for r in load(wpath)]
        for i in ids:
            tail = i.split("/")[-1]
            for r in fits:
                if tail in r["arxiv_id"]:
                    survivors.append((i, "fit table"))
                    break
            for p in prov:
                if tail in p["identifier"]:
                    survivors.append((i, "provenance table"))
                    break
    check("no withdrawn record still carries an Hc2", not survivors,
          "%d survivor(s)" % len(survivors) if survivors else
          "%d withdrawn records" % len(ids) if os.path.exists(wpath) else "")
    for s in survivors:
        print("      %-44s still in the %s" % s)

    print()
    if failures:
        print("%d check(s) FAILED: %s" % (len(failures), "; ".join(failures)))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
