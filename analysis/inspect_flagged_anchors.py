#!/usr/bin/env python3
"""
inspect_flagged_anchors.py

Second look at the rows audit_cohort_anchors.py flagged. That test only asks
whether the anchor value occurs in the paper text, which fails for three quite
different reasons: the anchor is a rounded family value while the paper reports
38.9, the PDF carries no text layer so nothing matches, or the anchor genuinely
does not come from that paper. Only the third is an error.

Prints, for each flagged row, how much text the PDF yielded, every temperature
the paper states near a Tc mention, and every bare temperature in kelvin, so the
three cases can be told apart by eye.

    python inspect_flagged_anchors.py
"""
import csv, glob, os, re, sys

AUDIT = "audit/cohort_anchor_audit.csv"


def local_pdfs():
    out = {}
    for f in glob.glob("*/*.pdf"):
        out.setdefault(os.path.basename(f)[:-4], f)
    return out


def resolve(identifier, pdfs):
    key = identifier
    for pre in ("elsevier_", "springer_", "iop_"):
        key = key.replace(pre, "")
    key = key.replace("/", "_")
    if key in pdfs:
        return pdfs[key]
    core = re.sub(r"v\d+$", "", key)
    hit = [n for n in pdfs if core and core in n]
    return pdfs[sorted(hit)[0]] if hit else None


TC_CONTEXT = re.compile(
    r"[^.\n]{0,90}?T\s?[c(C]\s?[^.\n]{0,60}?(\d{1,3}(?:\.\d+)?)\s?K[^.\n]{0,30}", re.I)
BARE_K = re.compile(r"(\d{1,3}(?:\.\d+)?)\s?K\b")


def main():
    try:
        import fitz
    except ImportError:
        sys.exit("pymupdf is not installed here. pip install pymupdf")
    if not os.path.exists(AUDIT):
        sys.exit("run audit_cohort_anchors.py first")

    pdfs = local_pdfs()
    rows = [r for r in csv.DictReader(open(AUDIT)) if r["verdict"] != "ok"
            and r["verdict"] != "no local pdf"]
    for r in rows:
        path = resolve(r["identifier"], pdfs)
        d = fitz.open(path)
        text = "".join(d.load_page(i).get_text("text") for i in range(d.page_count))
        npages = d.page_count
        d.close()
        print("=" * 78)
        print("%s" % r["identifier"])
        print("  recorded   : compound %s   Tc_anchor %s K   (%s)"
              % (r["compound"], r["Tc_anchor_K"], r["Tc_provenance"]))
        print("  pdf        : %s, %d pages, %d characters of extractable text"
              % (os.path.basename(path), npages, len(text)))
        if len(text) < 500:
            print("  NOTE       : almost no text layer, so the audit test cannot "
                  "say anything about this row")
            continue
        ctx = []
        for m in TC_CONTEXT.finditer(text):
            s = " ".join(m.group(0).split())
            if s not in ctx:
                ctx.append(s)
        print("  Tc mentions:")
        for s in ctx[:8] or ["    none matched"]:
            print("     %s" % s[:120])
        vals = sorted({float(v) for v in BARE_K.findall(text)}, reverse=True)
        print("  all K values in text: %s"
              % ", ".join(("%g" % v) for v in vals[:24]))
    print("=" * 78)
    print("%d rows inspected" % len(rows))


if __name__ == "__main__":
    main()
