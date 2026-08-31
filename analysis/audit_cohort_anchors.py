#!/usr/bin/env python3
"""
audit_cohort_anchors.py

Checks the anchors in provenance_table_fitcohort_full.csv against the papers they
claim to come from.

Prompted by a concrete failure. For 10.1016/0921-4534(94)00021-2 the table
records the compound Hg0.8V0.2Ba2Ca2Cu3O8 with Tc_anchor 134 K. That paper
synthesises Hg-1201 and Hg-1212 and reports Tc of 90, 115 and 124 K; neither the
string "134" nor any Ca2Cu3 stoichiometry appears anywhere in it. 134 K is the
literature Tc of Hg-1223, the phase the extractor named. A compound identity that
was not in the paper carried an anchor temperature into the fitted cohort with
it, roughly 50 K away from the measured value.

The test here is deliberately weak in one direction and sharp in the other.
A number appearing somewhere in the text proves very little, since 39 will occur
in any MgB2 paper. A number appearing nowhere in the text is hard to explain for
a row whose provenance says the value was reported by that paper, and those are
the rows worth reading by hand.

Run from the folder holding provenance_table_fitcohort_full.csv and the PDF
directories:

    python audit_cohort_anchors.py
    python audit_cohort_anchors.py --all      # every row, not only paper-reported
"""
import argparse, csv, glob, os, re, sys

PROV = "provenance_table_fitcohort_full.csv"
OUT = "audit/cohort_anchor_audit.csv"


def local_pdfs():
    out = {}
    for pattern in ("*/*.pdf", "audit/arxiv_pdfs/*.pdf"):
        for f in glob.glob(pattern):
            out.setdefault(os.path.basename(f)[:-4], f)
    return out


def doi_index():
    """Map printed DOI to file path, so a paper stored under a name that is not
    its DOI can still be found. MAGLAB records are the case that matters: the
    file 11_4_2K.pdf carries 10.1088/0953-2048/29/3/035013 inside it. Built from
    audit/archive_integrity.csv when that has been generated."""
    idx = {}
    path = os.path.join("audit", "archive_integrity.csv")
    if not os.path.exists(path):
        return idx
    for r in csv.DictReader(open(path)):
        doi = (r.get("doi_in_pdf") or "").strip().lower()
        if doi and r.get("file"):
            idx.setdefault(doi, r["file"])
    return idx


def _flat(s):
    """Flatten DOI punctuation. A filename cannot hold a slash, so a DOI written
    into an identifier arrives with its slashes turned into underscores, and an
    exact match against the DOI printed in the PDF then fails."""
    return re.sub(r"[/_.\-]", "", str(s).lower())


def resolve(identifier, pdfs, dois=None):
    if dois:
        hit = dois.get(identifier.strip().lower())
        if hit and os.path.exists(hit):
            return hit
        want = _flat(identifier)
        for doi, path in dois.items():
            if _flat(doi) == want and os.path.exists(path):
                return path
    # NHMFL records are named by their laboratory label, and the file drops the
    # MAGLAB_ prefix: MAGLAB_11_4_2K is stored as 11_4_2K.pdf.
    if identifier.startswith("MAGLAB_"):
        stem = identifier[len("MAGLAB_"):]
        if stem in pdfs:
            return pdfs[stem]
    key = identifier
    for pre in ("elsevier_", "springer_", "iop_"):
        key = key.replace(pre, "")
    key = key.replace("/", "_")
    if key in pdfs:
        return pdfs[key]
    core = re.sub(r"v\d+$", "", key)
    hit = [n for n in pdfs if core and core in n]
    return pdfs[sorted(hit)[0]] if hit else None


def page_text(path):
    import fitz
    d = fitz.open(path)
    t = "".join(d.load_page(i).get_text("text") for i in range(d.page_count))
    d.close()
    return t


ELEMENT = re.compile(r"[A-Z][a-z]?")


def elements(s):
    if not isinstance(s, str) or not s.strip():
        return frozenset()
    s = re.sub(r"[0-9.\-+()\[\]\s,]", "", s)
    for junk in ("x", "y", "z", "δ"):
        s = s.replace(junk, "")
    return frozenset(ELEMENT.findall(s))


def number_present(value, text_nospace):
    """True if the anchor value appears in the paper text, as an integer or with
    one decimal place."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    forms = {str(int(v))} if v == int(v) else set()
    forms.add(("%.1f" % v).rstrip("0").rstrip("."))
    forms.add("%.1f" % v)
    return any(f in text_nospace for f in forms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="check every row, not only those claiming paper-reported Tc")
    args = ap.parse_args()

    try:
        import fitz                                   # noqa: F401
    except ImportError:
        sys.exit("pymupdf is not installed here. pip install pymupdf")

    pdfs = local_pdfs()
    dois = doi_index()
    os.makedirs("audit", exist_ok=True)
    rows = list(csv.DictReader(open(PROV)))

    cols = ["identifier", "compound", "substructure_family", "Tc_anchor_K",
            "Tc_provenance", "Hc2_anchor_T", "Hc2_provenance",
            "pdf", "tc_in_paper", "hc2_in_paper", "compound_elements_present",
            "verdict"]
    w = csv.DictWriter(open(OUT, "w", newline=""), fieldnames=cols)
    w.writeheader()

    flagged, checked, nopdf = [], 0, 0
    for r in rows:
        claims_paper = "paper-reported" in (r.get("Tc_provenance") or "")
        if not args.all and not claims_paper:
            continue
        path = resolve(r["identifier"], pdfs, dois)
        out = {c: r.get(c, "") for c in cols if c in r}
        out["identifier"] = r["identifier"]
        if not path:
            nopdf += 1
            out.update(pdf="", verdict="no local pdf")
            w.writerow(out)
            continue
        text = page_text(path)
        ns = re.sub(r"\s", "", text)
        checked += 1
        tc_ok = number_present(r.get("Tc_anchor_K"), ns)
        hc2_ok = number_present(r.get("Hc2_anchor_T"), ns)
        # Presence of every element, and nothing more. This test cannot detect a
        # stoichiometry substitution: Hg, V, Ba, Ca, Cu and O all occur in a
        # paper about Hg0.8V0.2Ba2CaCu2O6, so it passed the row whose recorded
        # compound was the m=3 member the paper says it could not synthesise. It
        # is a screen for gross mismatch, not evidence that a formula is right.
        want = elements(r.get("compound", ""))
        found = elements(" ".join(re.findall(r"[A-Z][A-Za-z0-9.()\-+]{2,30}", text)))
        el_ok = bool(want) and want <= found

        verdict = "ok"
        if claims_paper and tc_ok is False:
            verdict = "Tc anchor not present in paper text"
        if not el_ok and verdict == "ok":
            verdict = "compound elements not all present in paper text"
        elif not el_ok:
            verdict += "; compound elements not all present"

        out.update(pdf=os.path.basename(path), tc_in_paper=tc_ok,
                   hc2_in_paper=hc2_ok, compound_elements_present=el_ok,
                   verdict=verdict)
        w.writerow(out)
        if verdict != "ok":
            flagged.append((r["identifier"], r.get("compound"),
                            r.get("Tc_anchor_K"), verdict))

    print("rows checked            : %d" % checked)
    print("rows with no local PDF  : %d" % nopdf)
    print("rows flagged            : %d" % len(flagged))
    if flagged:
        print()
        print("  %-38s %-26s %-8s %s" % ("identifier", "compound", "Tc", "verdict"))
        for i, c, t, v in flagged:
            print("  %-38s %-26s %-8s %s" % (i[:38], str(c)[:26], t, v))
    print("\nwritten to %s" % OUT)


if __name__ == "__main__":
    main()
