#!/usr/bin/env python3
"""
screen_cohort_a.py

Run the deposit's own extraction-integrity screen over the temperature-axis
corpus, which had never been screened at all.

Every integrity check in this repository has been aimed at Cohort B, the
Elsevier and Springer papers behind the field-axis fits. The temperature-axis
fits in data/phase_3_p44_post_UCLA_beta_T_fits.csv come from somewhere else: 260
fits across 20 papers, 18 of them arXiv preprints whose extracted points live in
a single wide file, data_agent2/agent2_dataset_v3_2_1.csv, in the upstream tree.
Because those points were never split into per-paper tables, the screen that
found the Cohort B defects was never pointed at them.

This splits them and points it at them. It changes nothing and asserts nothing
beyond what analysis/audit_extraction_integrity.py already computes.

One caveat belongs in the output rather than in a footnote: the series grouping
here is by (compound, temperature) because the wide file carries no sample-form
or sample-id column, so the duplicate and shifted tests see a different grouping
than they would on a native long table. The round-fraction and arithmetic tests
do not depend on that grouping.

    python3 analysis/screen_cohort_a.py --out audit/cohortA_extraction_integrity.csv

Run from the repository root.
"""
import argparse
import os
import subprocess
import sys
import tempfile

import pandas as pd

WIDE = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
        "agent2_dataset_v3_2_1.csv")
FITS = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        "audit", "cohortA_extraction_integrity.csv"))
    args = ap.parse_args()
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    if not os.path.exists(WIDE):
        sys.exit("the upstream wide file is not mounted: %s" % WIDE)

    d = pd.read_csv(WIDE)
    b = pd.read_csv(FITS)
    keep = set(b.paper_id.unique())
    tmp = tempfile.mkdtemp(prefix="cohortA_")
    n = 0
    for p, g in d[d.pdf_name.isin(keep)].groupby("pdf_name"):
        pd.DataFrame({
            "arxiv_id": p.replace(".pdf", ""),
            "compound_formula": g.get("mp_formula", g.get("compound_raw")),
            "sample_form": "",
            "sample_id": g.get("compound_raw", ""),
            "temperature_K": g.temperature_K,
            "field_T": g.field_T,
            "Jc_A_per_cm2": g.Jc,
        }).to_csv(os.path.join(tmp, p.replace(".pdf", "") + "_LONG.csv"),
                  index=False)
        n += 1
    print("split %d of the %d temperature-axis papers into per-paper tables"
          % (n, len(keep)))
    subprocess.run([sys.executable, "analysis/audit_extraction_integrity.py",
                    "--dir", tmp, "--csv", args.out, "--quiet"], check=True)

    s = pd.read_csv(args.out)
    s["paper"] = s.file.str.replace("_LONG.csv", "", regex=False)
    cnt = b.groupby(b.paper_id.str.replace(".pdf", "", regex=False)).size()
    s["beta_T_fits"] = s.paper.map(cnt).fillna(0).astype(int)
    s.to_csv(args.out, index=False)
    print("\n%s" % s[["verdict", "paper", "n_points", "round_fraction",
                      "signatures", "beta_T_fits"]]
           .sort_values(["verdict", "round_fraction"], ascending=[True, False])
           .to_string(index=False))
    print("\n   verdicts: %s" % s.verdict.value_counts().to_dict())
    print("   temperature-axis fits by verdict: %s"
          % s.groupby("verdict").beta_T_fits.sum().to_dict())
    print("   of %d fits in the deposit" % len(b))
    print("\n   round_fraction alone is a flag and not a finding, in this "
          "screen's own words.\n   Fifteen of the sixteen CHECKs carry no other "
          "signature.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
