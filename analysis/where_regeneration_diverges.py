#!/usr/bin/env python3
"""Where regenerating the dispatch diverges from the deposit, exhaustively.

Two questions, answered separately, because they have different answers.

  Does the RELEASED prediction file reproduce from the generator that shipped
  with it, on the tables that shipped with it? No, and the failure is one
  paper wide. Every one of its 2151 rows aligns, every anchor, provenance and
  refusal column is identical, and 337 predictions differ by at most 0.0138
  dex, which is the bootstrap draw. The exception is 18 rows: the generator
  commits `matpr.2019.05.078` to the (conventional_AlB2, wire) conditional
  cell and the released file does not, and those 18 predictions differ by
  0.266 dex at the median. The released file is the generator's own output
  with exactly the wire commitments removed and those rows recomputed on the
  aggregate predictor. Nothing in the repository writes that column except the
  generator, and the commitment path has been in it since the release commit
  and unchanged since.

  Does regenerating on the CURRENT tables move anything the paper reports? Only
  those same records. Aligning the deposit against a current regeneration, 2097
  rows to 2097, four emitted predictions differ by more than 0.02 dex and all
  four are the wire records. 141 further rows move materially, by up to 3.80
  dex, and every one is a refused temperature-axis-only prediction in
  iron_pnictide_122, which is the withdrawals and the anchor repair propagating
  through beta_T on rows the paper does not report. The rest is bootstrap
  noise or identical.

Six candidates also come back, 54 rows across two papers, because the
withdrawals were applied by editing the CSV while the candidate list is rebuilt
from the extraction directory. All 54 are refused, so no emitted prediction
changes, but the generator cannot enforce a withdrawal and any regeneration
restores them.

    python analysis/where_regeneration_diverges.py

Run from the repository root. The two comparison inputs are built by the run
recorded in audit/p57_regen_20260905/manifest.json; the release-era arm needs
`git show 8ad8d43:data/...` staged into data/ and the generator run without the
two gate scripts, which is how the file in that directory was made.
"""
import os

import numpy as np
import pandas as pd

REGEN_DIR = os.path.join("audit", "p57_regen_20260905")
DEP = os.path.join("data", "phase_3_p57_de_novo_predictions.csv")
REGEN = os.path.join(REGEN_DIR,
                     "phase_3_p57_de_novo_predictions_regenerated.csv")
RELEASE_FILE = os.path.join(REGEN_DIR, "released_8ad8d43.csv")
RELEASE_GEN = os.path.join(REGEN_DIR, "generator_on_release_tables_raw.csv")
KEY = ["compound_formula", "paper_id", "T_K", "H_T"]
NOISE = 0.02


def align(a, b):
    """One-to-one alignment.

    The key needs the Materials Project id and an occurrence index as well as
    the four obvious fields: 423 rows of the deposit share a (compound, paper,
    T, H) triple, so a merge on that alone is many-to-many and a sort-and-zip
    silently pairs the wrong rows. An earlier version did the second and
    reported differences in nine columns that were an artefact of it.
    """
    a, b = a.copy(), b.copy()
    for f in (a, b):
        f["MPk"] = f.MP_id.fillna("NA")
        f["occ"] = f.groupby(KEY + ["MPk"]).cumcount()
    return a.merge(b, on=KEY + ["MPk", "occ"], suffixes=("_a", "_b"),
                   validate="one_to_one")


def columns_differing(m, cols):
    out = []
    for c in cols:
        x, y = m[c + "_a"], m[c + "_b"]
        if x.dtype.kind in "fci" and y.dtype.kind in "fci":
            xn, yn = pd.to_numeric(x, errors="coerce"), \
                pd.to_numeric(y, errors="coerce")
            d = ~np.isclose(xn, yn, equal_nan=True, rtol=0, atol=1e-9)
            n = int(d.sum())
            mx = float(np.nanmax(np.abs(xn - yn))) if n else 0.0
        else:
            n = int((x.fillna("") != y.fillna("")).sum())
            mx = float("nan")
        if n:
            out.append((c, n, mx))
    return out


def main():
    fails = []

    if os.path.exists(RELEASE_FILE) and os.path.exists(RELEASE_GEN):
        rel = pd.read_csv(RELEASE_FILE)
        gen = pd.read_csv(RELEASE_GEN)
        m = align(rel, gen)
        shared = [c for c in rel.columns
                  if c in gen.columns and c not in KEY + ["MP_id"]]
        print("the released file against the generator that shipped with it\n")
        print("   rows %d and %d, aligned one to one on %d"
              % (len(rel), len(gen), len(m)))
        if len(m) != len(rel):
            fails.append("the release does not align one to one")
        diffs = columns_differing(m, shared)
        for c, n, mx in diffs:
            print("   %-38s %5d rows%s"
                  % (c, n, "  max |delta| %.4g" % mx if mx == mx else ""))
        cat = [c for c, _n, mx in diffs if mx != mx]
        if set(cat) - {"sample_form_commitment", "predictor_method_scope"}:
            fails.append("a categorical column other than the commitment and "
                         "the predictor scope differs: %s" % ", ".join(cat))
        m["delta"] = (m.predicted_log_Jc_a - m.predicted_log_Jc_b).abs()
        m["wire"] = m.sample_form_commitment_b.fillna("") == "wire"
        s = m[m.delta > 1e-9]
        w, o = s[s.wire], s[~s.wire]
        print("\n   predictions that changed        %d" % len(s))
        print("   on the wire-committed rows      %d, median %.4f, max %.4f"
              % (len(w), w.delta.median(), w.delta.max()))
        print("   on every other row              %d, median %.4f, max %.4f"
              % (len(o), o.delta.median(), o.delta.max()))
        if (o.delta > NOISE).any():
            fails.append("%d non-wire predictions moved by more than %.2f dex, "
                         "so the difference is not one paper wide"
                         % (int((o.delta > NOISE).sum()), NOISE))
        else:
            print("   none of the others exceeds %.2f dex, so the released "
                  "file is the generator's" % NOISE)
            print("   own output with the wire commitments removed and those "
                  "rows recomputed")
    else:
        print("the release-era arm is not staged; see the module docstring")

    d = pd.read_csv(DEP)
    r = pd.read_csv(REGEN)
    m = align(d, r)
    print("\n\nthe deposit against a regeneration on the current tables\n")
    print("   rows %d and %d, aligned one to one on %d"
          % (len(d), len(r), len(m)))
    if len(m) != len(d):
        fails.append("the deposit does not align one to one into the "
                     "regeneration")
    extra = len(r) - len(m)
    only = r[~r.set_index(KEY).index.isin(d.set_index(KEY).index)]
    print("   rows present only in the regeneration   %d, from %d papers"
          % (extra, only.paper_id.nunique()))
    for p, n in only.paper_id.value_counts().items():
        print("      %-56s %d" % (p, n))
    if (only.refusal_flag.fillna("") == "").any():
        fails.append("a resurrected candidate is emitted, not refused")
    else:
        print("   every one of them is refused, so no emitted prediction "
              "changes")

    m["delta"] = (m.predicted_log_Jc_a - m.predicted_log_Jc_b).abs()
    m["emitted"] = m.refusal_flag_a.fillna("") == ""
    m["wire"] = m.sample_form_commitment_b.fillna("") == "wire"
    big = m[m.delta > NOISE]
    print("\n   %-46s %6s %10s" % ("rows moving more than %.2f dex" % NOISE,
                                   "n", "max"))
    for lab, sel in [("emitted, on the wire records",
                      big[big.emitted & big.wire]),
                     ("emitted, anything else",
                      big[big.emitted & ~big.wire]),
                     ("refused, temperature-axis only",
                      big[~big.emitted])]:
        print("   %-46s %6d %10s"
              % (lab, len(sel), "%.4f" % sel.delta.max() if len(sel) else "-"))
    if len(big[big.emitted & ~big.wire]):
        fails.append("an emitted prediction moved materially and is not one of "
                     "the wire records, which the account does not explain")
    ref = big[~big.emitted]
    if len(ref):
        print("   the refused movers are %s, which is beta_T carrying the "
              "withdrawals and the"
              % ", ".join(sorted(set(ref.substructure_a.dropna()))))
        print("   anchor repair through rows the paper does not report")

    print("\nselftest")
    for f in fails:
        print("   FAIL %s" % f)
    if fails:
        raise SystemExit("the divergence is not what this script describes")
    print("   all checks pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
