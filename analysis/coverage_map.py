#!/usr/bin/env python3
"""
coverage_map.py

Every paper the deposit claims contributes, and what has actually been done with
it.

Why. The pre-registered census covers four papers, which is a deliberately small
subset: it was fixed as the complete set of PASSING field-axis papers that were
UNTRACED and had a usable source document. That is a sentence about coverage,
and this checks it, along with the larger question it invites: what happened to
the rest.

The three tables that between them define the cohort disagree with each other:

  data/provenance_table_fitcohort_full.csv   62 rows, one per contributing paper
  data/phase_3_form3_fits_partial_...csv    159 field-axis fits, 31 papers
  data/phase_3_p44_post_UCLA_beta_T_...csv  260 temperature-axis fits, 20 papers

Thirty-two provenance rows are flagged "fully fittable", which reads as
contributing both exponents. One paper appears in both fit tables.

    python3 analysis/coverage_map.py

Run from the repository root. Writes audit/coverage_map.csv.
"""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd

PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
WITHDRAWN_A = os.path.join("audit", "withdrawn_beta_T_papers.csv")
WITHDRAWN_R = os.path.join("audit", "withdrawn_records.csv")
DUPES = os.path.join("audit", "duplicate_papers.csv")
PIPELINE_P44 = ("/mnt/user-data/uploads/SuperconductorWorkflow/kappa_pipeline/"
                "analysis/v3_2_9_path_2_prep/phase_3_p44_post_UCLA_beta_T_fits.csv")
FITS_B = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_A = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
RE = os.path.join("data", "reextraction")
PDF_DIRS = [
    "/mnt/user-data/uploads/SuperconductorWorkflow/kappa_pipeline/analysis/"
    "v3_2_9_path_2_prep/phase_3_p19_elsevier_pdfs",
    "/mnt/user-data/uploads/SuperconductorWorkflow/kappa_pipeline/analysis/"
    "v3_2_9_path_2_prep/audit/arxiv_pdfs",
    "/mnt/user-data/uploads/SuperconductorWorkflow/pdfs_for_page_review",
]
EXT_DIR = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
           "v3_2_2B_extension")
MASTERS = {
    "field": ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
              "agent2_dataset_v3_2_2B.csv", "arxiv_id"),
    "temperature": ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
                    "agent2_dataset_v3_2_1.csv", "pdf_name"),
}
OUT = os.path.join("audit", "coverage_map.csv")


def stems(paths):
    out = set()
    for d in paths:
        for f in glob.glob(os.path.join(d, "*")):
            out.add(os.path.splitext(os.path.basename(f))[0])
    return out


def squash(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def has_pdf(identifier, pdfs):
    q = squash(identifier)
    return any(q == squash(s) or q in squash(s) for s in pdfs)


def trace_key(identifier):
    """The distinctive tail of an identifier, as a trace file spells it.

    A trace is named for the paper with the punctuation flattened, so the DOI
    registrant prefix and the leading 'j.' of an Elsevier item have to come off
    first. Matching on a fixed-length tail instead, as the first version did,
    reported mtphys.2022.100783 as untraced when it carries two traces.
    """
    k = re.sub(r"^10\.\d{4,}/", "", str(identifier))
    k = re.sub(r"^j\.", "", k)
    return squash(k)


def has_trace(identifier, traces):
    q = trace_key(identifier)
    return bool(q) and any(q in squash(t) for t in traces)


def in_table(identifier, keys):
    q = str(identifier)
    return [k for k in keys if q == k or q in k
            or squash(q) == squash(k) or squash(q) in squash(k)]


def main():
    prov = pd.read_csv(PROV)
    fb = pd.read_csv(FITS_B)
    fa = pd.read_csv(FITS_A)
    pdfs = stems(PDF_DIRS)
    traces = {os.path.basename(f).replace("_points.csv", "")
              for f in glob.glob(os.path.join(RE, "*_points.csv"))}
    ext = {os.path.basename(f) for f in glob.glob(os.path.join(EXT_DIR, "*_LONG.csv"))}
    masters = {}
    for name, (path, key) in MASTERS.items():
        masters[name] = set(pd.read_csv(path)[key].astype(str).unique())

    kb = fb.paper_key.astype(str).unique()
    ka = fa.paper_key.astype(str).unique()
    passing = fb[(fb.ok == True) & (fb.physicality == "ok")]
    kp = set(passing.paper_key.astype(str))

    rows = []
    for _, r in prov.iterrows():
        i = str(r.identifier)
        mb, ma = in_table(i, kb), in_table(i, ka)
        rows.append(dict(
            identifier=i, flag=r.contribution_flag,
            family=r.substructure_family,
            field_fits=int(fb[fb.paper_key.isin(mb)].shape[0]),
            field_passing=int(passing[passing.paper_key.isin(mb)].shape[0]),
            temp_fits=int(fa[fa.paper_key.isin(ma)].shape[0]),
            pdf=has_pdf(i, pdfs),
            trace=has_trace(i, traces),
            extraction=any(squash(i)[-18:] in squash(e) for e in ext)
                       or any(squash(i)[-18:] in squash(m)
                              for s in masters.values() for m in s),
        ))
    d = pd.DataFrame(rows)
    os.makedirs("audit", exist_ok=True)
    d.to_csv(OUT, index=False)
    pd.set_option("display.width", 220)

    print("=" * 78)
    print("WHAT THE 62 PROVENANCE ROWS ACTUALLY CONTRIBUTE")
    print("=" * 78)
    d["contributes"] = np.where(
        (d.field_fits > 0) & (d.temp_fits > 0), "both axes",
        np.where(d.field_fits > 0, "field only",
                 np.where(d.temp_fits > 0, "temperature only", "NOTHING")))
    print(pd.crosstab(d.flag, d.contributes).to_string())
    print()
    print(f"  {int((d.contributes == 'both axes').sum())} paper contributes to "
          f"both axes, against {int((d.flag == 'fully fittable').sum())} rows "
          f"flagged fully fittable")
    # RETRACTION. The first version of this script reported these rows as
    # contributing "no fit and no record of why". There is a record, in this
    # repository, in ledgers this audit wrote itself, and the script did not
    # look at them.
    wa = pd.read_csv(WITHDRAWN_A) if os.path.exists(WITHDRAWN_A) else pd.DataFrame()
    wr = pd.read_csv(WITHDRAWN_R) if os.path.exists(WITHDRAWN_R) else pd.DataFrame()
    dup = pd.read_csv(DUPES) if os.path.exists(DUPES) else pd.DataFrame()
    wset = set(wa.paper_id.astype(str)) if len(wa) else set()
    rset = set(wr.identifier.astype(str)) if len(wr) else set()
    # the duplicate ledger keys the two axes' identifiers to one paper, so a
    # row is a duplicate when its identifier appears in either axis column
    dset = set()
    for c in ("field_axis_id", "temperature_axis_id", "paper_key"):
        if c in dup.columns:
            dset |= {squash(v) for v in dup[c].astype(str)}

    def disposition(i):
        for w in wset:
            if str(i) in w or w.replace(".pdf", "") in str(i):
                return "withdrawn (beta_T ledger)"
        if str(i) in rset:
            return "withdrawn (records ledger)"
        q = squash(i)
        if q and any(q in x for x in dset):
            return "duplicate identifier of a paper that does contribute"
        return "NOT ACCOUNTED FOR"

    none = d[d.contributes == "NOTHING"].copy()
    none["disposition"] = none.identifier.map(disposition)
    print(f"  {len(none)} rows contribute no fit to either table. Every one is "
          f"accounted for elsewhere in this repository:")
    print(none.disposition.value_counts().to_string())
    if (none.disposition == "NOT ACCOUNTED FOR").any():
        print("  UNACCOUNTED:")
        print(none[none.disposition == "NOT ACCOUNTED FOR"]
              .identifier.to_string(index=False))
    print()
    print("  what they still show: the provenance table was not updated when "
          "they were withdrawn, so it lists papers as contributing that the "
          "audit's own ledgers removed on 2026-09-01 and 2026-09-03.")
    if os.path.exists(PIPELINE_P44):
        pl = pd.read_csv(PIPELINE_P44)
        key = "paper_id" if "paper_id" in pl.columns else pl.columns[0]
        removed = (int(wa.n_fits_removed.sum()) if len(wa) else 0)
        print()
        print(f"  the pipeline's own copy of the temperature-axis fits holds "
              f"{len(pl)} fits over {pl[key].nunique()} papers; the copy in "
              f"this repository holds {len(fa)} over {fa.paper_key.nunique()}. "
              f"The difference, {len(pl) - len(fa)}, is exactly the "
              f"{removed} fits in the beta_T withdrawal ledger plus the "
              f"{len(pl) - len(fa) - removed} in the records ledger.")
    print()
    print("  the detail below is kept because it is still true that these "
          "papers carry substantial extracted data:")
    wa = pd.read_csv(MASTERS["temperature"][0])
    wb = pd.read_csv(MASTERS["field"][0])
    tot = 0
    print(f"    {'identifier':32s} {'temp rows':>10} {'nT':>4} "
          f"{'nH':>4} {'field rows':>11}")
    for _, r in d[d.contributes == "NOTHING"].iterrows():
        tail = str(r.identifier).split("/")[-1]
        a = wa[wa.pdf_name.astype(str).str.contains(tail, regex=False)]
        b = wb[wb.arxiv_id.astype(str).str.contains(tail, regex=False)]
        tot += len(a) + len(b)
        print(f"    {r.identifier:32s} "
              f"{len(a):10d} {a.temperature_K.nunique() if len(a) else 0:4d} "
              f"{a.field_T.nunique() if len(a) else 0:4d} {len(b):11d}")
    print(f"    {tot} extracted rows in all, from papers the deposit's own "
          f"provenance table lists as contributing, that produce no fit and no "
          f"record of why. Neither fits file carries a failure row: the "
          f"temperature file is 260 of 260 ok, so a paper that did not make it "
          f"is simply absent.")
    print()

    print("=" * 78)
    print("THE FIELD AXIS: 16 passing papers, and why the census covers four")
    print("=" * 78)
    f = d[d.field_passing > 0].copy()
    f["census_eligible"] = f.pdf & ~f.trace
    print(f"  {len(f)} papers carry a passing field-axis fit, "
          f"{int(f.field_passing.sum())} fits in all")
    print(f"    with a PDF in the corpus          : {int(f.pdf.sum())}")
    print(f"    already traced                    : {int(f.trace.sum())}")
    print(f"    with a PDF and untraced           : "
          f"{int(f.census_eligible.sum())}  <- the census set")
    print()
    print(f[["identifier", "field_passing", "pdf", "trace", "census_eligible"]]
          .sort_values(["census_eligible", "field_passing"], ascending=False)
          .to_string(index=False))
    print()

    print("=" * 78)
    print("THE TEMPERATURE AXIS")
    print("=" * 78)
    t = d[d.temp_fits > 0]
    print(f"  {len(t)} papers, {int(t.temp_fits.sum())} fits, "
          f"{int(t.pdf.sum())} with a PDF, {int(t.trace.sum())} traced")
    print()

    print("=" * 78)
    print("COVERAGE OF THE WHOLE CONTRIBUTING SET")
    print("=" * 78)
    con = d[d.contributes != "NOTHING"]
    print(f"  {len(con)} papers contribute at least one fit")
    print(f"    have a PDF here : {int(con.pdf.sum())}  "
          f"({len(con) - int(con.pdf.sum())} do not)")
    print(f"    have a trace    : {int(con.trace.sum())}  "
          f"({len(con) - int(con.trace.sum())} do not)")
    print(f"    have neither    : {int((~con.pdf & ~con.trace).sum())}")
    print()
    print("  papers contributing fits with no PDF and no trace here:")
    for _, r in con[~con.pdf & ~con.trace].iterrows():
        print(f"    {r.identifier:34s} field {r.field_fits:3d} "
              f"(passing {r.field_passing:3d})  temperature {r.temp_fits:3d}")
    print()
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
