#!/usr/bin/env python3
"""
cross_model_agreement.py

Second independent reader over the Cohort B v2 vision cache, to measure the
cross-model extraction agreement rate requested by Referee A.

The first pass (cached in phase_3_p22_cohort_b_v2_vision_cache/) screened each
paper for the presence of Jc(H) and Jc(T) sweeps and recorded the measurement
window. This script re-reads the same pages with a second model, from a
different generation, and compares the two on the fields that gate a paper into
the fitted cohort.

Papers are tagged `fitted_cohort` when they appear in
provenance_table_fitcohort_full.csv, so the agreement rate can be reported for
that subset as well as for the full archive.

The API key is read from the environment and is never written to disk or to the
output. Results are written incrementally, so the run is resumable: re-running
skips papers already present in the output file.

Usage
-----
    export ANTHROPIC_API_KEY=...            # your key, your machine
    pip install anthropic pymupdf

    python3 analysis/cross_model_agreement.py --dry-run     # no API calls
    python3 analysis/cross_model_agreement.py --limit 20    # small paid test
    python3 analysis/cross_model_agreement.py               # full 662

Cost
----
The first pass over these 662 papers cost $4.98 in total, a mean of $0.0075 per
paper at a mean of 1.5 pages sent. A second pass is of the same order. The
script prints a running total and stops if --max-spend is exceeded.
"""
import argparse, base64, csv, glob, io, json, os, sys, time

MODEL = "claude-sonnet-5"
CACHE = "phase_3_p22_cohort_b_v2_vision_cache"
PROV = "provenance_table_fitcohort_full.csv"
OUT = "audit/cross_model_agreement.csv"
PDF_DIRS = "*pdfs*"
MAX_PAGES = 4

FIELDS = ["jc_h_sweep_present", "jc_t_sweep_present", "primary_scan_direction",
          "primary_compound", "T_min_K", "T_max_K", "H_min_T", "H_max_T"]

PROMPT = """You are reading pages from a superconductivity paper to record what
measurements it contains. Answer only from what is printed on these pages.

Return a single JSON object with exactly these keys:
  jc_h_sweep_present     true if a figure plots critical current density against magnetic field
  jc_t_sweep_present     true if a figure plots critical current density against temperature
  primary_scan_direction one of "H", "T", "both", "neither"
  primary_compound       the compound formula as printed, or null
  T_min_K, T_max_K       temperature range of the Jc data in kelvin, or null
  H_min_T, H_max_T       field range of the Jc data in tesla, converting from kOe or gauss
                         if the printed axis uses those units, or null

"No such data in this paper" is a correct and expected answer. If a quantity is
not shown on these pages, return null for it rather than inferring a value.
Return the JSON object and nothing else."""


def find_pdfs():
    out = {}
    for d in glob.glob(PDF_DIRS):
        if os.path.isdir(d):
            for f in glob.glob(os.path.join(d, "*.pdf")):
                out.setdefault(os.path.basename(f)[:-4], f)
    return out


def fitted_cohort_ids():
    ids = set()
    if not os.path.exists(PROV):
        return ids
    for r in csv.DictReader(open(PROV)):
        s = r.get("identifier", "")
        for pre in ("elsevier_", "springer_", "iop_"):
            s = s.replace(pre, "")
        ids.add(s.replace("/", "_"))
    return ids


def page_images(path, n_pages):
    import fitz
    doc = fitz.open(path)
    out = []
    for i in range(min(n_pages, doc.page_count)):
        pix = doc.load_page(i).get_pixmap(dpi=150)
        out.append(base64.b64encode(pix.tobytes("png")).decode())
    doc.close()
    return out


def norm(v):
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "yes"):
            return True
        if s in ("false", "no"):
            return False
        if s in ("null", "none", "nan"):
            return None
        try:
            return round(float(s), 3)
        except ValueError:
            return s
    if isinstance(v, (int, float)):
        return round(float(v), 3)
    return v


def compare(a, b):
    """Field-level agreement between the two readers."""
    res = {}
    for f in FIELDS:
        x, y = norm(a.get(f)), norm(b.get(f))
        if isinstance(x, float) and isinstance(y, float):
            res[f] = abs(x - y) <= max(0.05 * max(abs(x), abs(y)), 0.1)
        else:
            res[f] = (x == y)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-spend", type=float, default=25.0)
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()

    entries = sorted(glob.glob(os.path.join(CACHE, "*.json")))
    pdfs = find_pdfs()
    cohort = fitted_cohort_ids()
    os.makedirs("audit", exist_ok=True)

    done = set()
    if os.path.exists(OUT):
        done = {r["paper"] for r in csv.DictReader(open(OUT))}

    todo = []
    for e in entries:
        key = os.path.basename(e)[:-5]
        if key in done:
            continue
        todo.append((key, e, pdfs.get(key)))
    # fitted-cohort papers first, so a partial run still answers the referee
    todo.sort(key=lambda t: (t[0] not in cohort, t[0]))
    if args.limit:
        todo = todo[:args.limit]

    n_cohort = sum(1 for k, _, _ in todo if k in cohort)
    missing = sum(1 for _, _, p in todo if p is None)
    print(f"model            : {args.model}")
    print(f"cache entries    : {len(entries)}  already done: {len(done)}")
    print(f"queued this run  : {len(todo)}  of which fitted-cohort: {n_cohort}")
    print(f"missing PDFs     : {missing}")
    if args.dry_run:
        print("\nDRY RUN, no API calls. First five queued:")
        for k, _, p in todo[:5]:
            tag = "fitted_cohort" if k in cohort else "archive"
            print(f"   {k:44} {tag:14} {'PDF ok' if p else 'PDF MISSING'}")
        est = 0.0075 * len(todo)
        print(f"\nestimated spend at the first pass rate: ${est:.2f}")
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set. Export it and re-run.")
    import anthropic
    client = anthropic.Anthropic()

    new = not os.path.exists(OUT)
    fh = open(OUT, "a", newline="")
    cols = (["paper", "in_fitted_cohort", "model", "n_pages", "cost_usd",
             "n_fields_compared", "n_fields_agree", "agreement_fraction", "error"]
            + [f"agree__{f}" for f in FIELDS]
            + [f"second__{f}" for f in FIELDS])
    w = csv.DictWriter(fh, fieldnames=cols)
    if new:
        w.writeheader()

    spend = 0.0
    for i, (key, cache_path, pdf) in enumerate(todo, 1):
        if spend > args.max_spend:
            print(f"stopping: spend ${spend:.2f} exceeded --max-spend")
            break
        first = json.load(open(cache_path))
        n_pages = int(first.get("n_pages_provided") or 1)
        row = dict(paper=key, in_fitted_cohort=key in cohort, model=args.model,
                   n_pages=n_pages, cost_usd="", n_fields_compared="",
                   n_fields_agree="", agreement_fraction="", error="")
        if not pdf:
            row["error"] = "pdf_not_found"
            w.writerow(row); fh.flush(); continue
        try:
            imgs = page_images(pdf, min(n_pages, MAX_PAGES))
            content = [{"type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": b}}
                       for b in imgs]
            content.append({"type": "text", "text": PROMPT})
            msg = client.messages.create(
                model=args.model, max_tokens=800,
                messages=[{"role": "user", "content": content}])
            txt = "".join(b.text for b in msg.content if b.type == "text").strip()
            txt = txt[txt.find("{"): txt.rfind("}") + 1]
            second = json.loads(txt)
            agree = compare(first.get("assessment", {}), second)
            n_ok = sum(1 for v in agree.values() if v)
            cost = (msg.usage.input_tokens * 3 + msg.usage.output_tokens * 15) / 1e6
            spend += cost
            row.update(cost_usd=round(cost, 5), n_fields_compared=len(agree),
                       n_fields_agree=n_ok,
                       agreement_fraction=round(n_ok / len(agree), 4))
            row.update({f"agree__{f}": agree[f] for f in FIELDS})
            row.update({f"second__{f}": second.get(f) for f in FIELDS})
        except Exception as exc:
            row["error"] = type(exc).__name__ + ": " + str(exc)[:160]
            time.sleep(2)
        w.writerow(row); fh.flush()
        if i % 25 == 0:
            print(f"  {i}/{len(todo)}   running spend ${spend:.2f}")
    fh.close()
    print(f"\ndone. rows written to {OUT}. spend this run ${spend:.2f}")
    print("summarise with: python3 analysis/summarise_agreement.py")


if __name__ == "__main__":
    main()
