#!/usr/bin/env python3
"""
audit_archive_integrity.py

Asks whether the PDFs on disk are still the documents the extraction pipeline
read.

Two findings prompted this. The file named 10.1016_j.jallcom.2023.170146.pdf
now contains 10.1016/j.physc.2009.11.051, a different paper that also exists
correctly under its own name; the vision cache for that identifier records an
8-page MgB2 paper, so the right document was read at extraction time and the
file was replaced afterwards. Separately, 208 of the 662 cached papers have more
pages now than the cache recorded, the archive having been completed after the
first pass ran.

Neither is an extraction error, but together they mean the current archive is not
a safe source of record for re-checking deposited values, and any re-read of a
changed file compares against a document the pipeline never saw.

Three checks per file:
  doi_in_pdf      the DOI printed in the first two pages against the filename.
                  Blank for files that print no DOI, which is normal for old
                  scans and for arXiv preprints, and is not evidence of a problem
  pages_now       current page count against n_pages_total in the vision cache
  duplicate_of    files whose bytes are identical to another file in the archive

    python audit_archive_integrity.py
    python audit_archive_integrity.py --cohort-only
"""
import argparse, csv, glob, hashlib, json, os, re, sys

CACHE = "phase_3_p22_cohort_b_v2_vision_cache"
PROV = "provenance_table_fitcohort_full.csv"
OUT = "audit/archive_integrity.csv"
DOI = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
ARXIV_NAME = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$|^\d{7}(v\d+)?$")


def cohort_keys():
    keys = set()
    if not os.path.exists(PROV):
        return keys
    for r in csv.DictReader(open(PROV)):
        s = r.get("identifier", "")
        for pre in ("elsevier_", "springer_", "iop_"):
            s = s.replace(pre, "")
        keys.add(s.replace("/", "_"))
    return keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort-only", action="store_true")
    args = ap.parse_args()
    try:
        import fitz
    except ImportError:
        sys.exit("pymupdf is not installed here. pip install pymupdf")

    os.makedirs("audit", exist_ok=True)
    keys = cohort_keys()
    files = sorted(glob.glob("*/*.pdf"))
    cache = {}
    for p in glob.glob(os.path.join(CACHE, "*.json")):
        try:
            cache[os.path.basename(p)[:-5]] = json.load(open(p)).get("n_pages_total")
        except Exception:
            pass

    cols = ["file", "name", "in_fitted_cohort", "pages_now", "pages_at_first_pass",
            "pages_changed", "doi_in_pdf", "doi_matches_name", "sha1", "duplicate_of",
            "verdict"]
    rows, byhash = [], {}
    for f in files:
        name = os.path.basename(f)[:-4]
        if args.cohort_only and name not in keys:
            continue
        try:
            d = fitz.open(f)
            n = d.page_count
            head = "".join(d.load_page(i).get_text("text")
                           for i in range(min(2, n)))
            d.close()
        except Exception as exc:
            rows.append(dict(file=f, name=name, verdict="unreadable: %s" % str(exc)[:60]))
            continue
        sha = hashlib.sha1(open(f, "rb").read()).hexdigest()
        found = [m.group(0).rstrip(".") for m in DOI.finditer(head)]
        # A filename cannot carry slashes, so every slash of the DOI was written
        # as an underscore. Compare with both punctuation marks flattened, or
        # multi-segment DOIs such as 10.1140/epjc/s10052-... never match their own
        # file. arXiv preprints legitimately print the DOI of the published
        # version, so a preprint filename is compared against neither.
        flat = lambda x: re.sub(r"[/_]", "", x.lower())
        fname_flat = flat(name)
        matches = ""
        if found and not ARXIV_NAME.match(name):
            matches = any(flat(x).endswith(fname_flat) or fname_flat.endswith(flat(x))
                          for x in found)
        cached = cache.get(name)
        changed = "" if cached is None else (n != cached)
        dup = byhash.get(sha, "")
        byhash.setdefault(sha, f)

        verdict = "ok"
        if matches is False:
            verdict = "CONTENT IS A DIFFERENT PAPER"
        elif changed is True:
            verdict = "pages changed since first pass"
        elif matches == "" and cached is None:
            verdict = "no DOI printed and not in cache, unverifiable"
        if dup:
            verdict += "; byte-identical to %s" % os.path.basename(dup)

        rows.append(dict(file=f, name=name, in_fitted_cohort=name in keys,
                         pages_now=n, pages_at_first_pass=cached,
                         pages_changed=changed, doi_in_pdf=found[0] if found else "",
                         doi_matches_name=matches, sha1=sha[:12],
                         duplicate_of=os.path.basename(dup) if dup else "",
                         verdict=verdict))

    w = csv.DictWriter(open(OUT, "w", newline=""), fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in cols})

    wrong = [r for r in rows if r.get("doi_matches_name") is False]
    changed = [r for r in rows if r.get("pages_changed") is True]
    dups = [r for r in rows if r.get("duplicate_of")]
    print("files examined                        : %d" % len(rows))
    print("content is a different paper          : %d" % len(wrong))
    print("page count changed since first pass   : %d" % len(changed))
    print("byte-identical duplicates             : %d" % len(dups))
    print("  of the above, in the fitted cohort  : %d wrong, %d changed"
          % (sum(1 for r in wrong if r["in_fitted_cohort"]),
             sum(1 for r in changed if r["in_fitted_cohort"])))
    if wrong:
        print("\nfilename does not match the DOI printed inside:")
        for r in wrong:
            print("   %-42s contains %s%s" % (r["name"][:42], r["doi_in_pdf"],
                  "   [FITTED COHORT]" if r["in_fitted_cohort"] else ""))
    if dups:
        print("\nbyte-identical pairs:")
        for r in dups[:20]:
            print("   %-42s == %s" % (r["name"][:42], r["duplicate_of"]))
    print("\nwritten to %s" % OUT)


if __name__ == "__main__":
    main()
