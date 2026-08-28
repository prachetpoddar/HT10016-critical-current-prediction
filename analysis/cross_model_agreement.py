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
DPI = 130
CACHE = "phase_3_p22_cohort_b_v2_vision_cache"
PROV = "provenance_table_fitcohort_full.csv"
OUT = "audit/cross_model_agreement.csv"
PDF_DIRS = "*pdfs*"
MAX_PAGES = 4

FIELDS = ["jc_h_sweep_present", "jc_t_sweep_present", "primary_scan_direction",
          "primary_compound", "T_min_K", "T_max_K", "H_min_T", "H_max_T"]

PROMPT = """Using the task definition you were given, report what these pages
contain. Answer only from what is printed on them.

Return a single JSON object with exactly these keys:
  jc_h_sweep_present     true if the paper presents Jc as a function of magnetic field,
                         by any of the three accepted methodologies
  jc_t_sweep_present     true if the paper presents Jc as a function of temperature
  primary_scan_direction one of "H", "T", "both", "neither"
  primary_compound       the compound formula as printed, or null
  T_min_K, T_max_K       temperature range of the Jc data in kelvin, or null
  H_min_T, H_max_T       field range of the Jc data in tesla, converting from kOe or gauss
                         if the printed axis uses those units, or null

If a quantity is not shown on these pages, return null for it rather than
inferring a value. Return the JSON object and nothing else."""


PILOT = "phase_3_p22_elsevier_cohort_b_pilot_v2.py"

# The first pass defined the extraction task in VISION_SYSTEM_PROMPT_V2. That
# definition is not neutral: it states that Jc(H) reconstructed from M-H loops by
# a Bean-type critical-state model, and Jc(H) reconstructed from magneto-optical
# or scanning Hall-probe imaging, both count as a Jc(H) sweep. A second reader
# given a plainer instruction marks those papers "no Jc(H) figure" and the run
# then measures the difference between two prompts rather than between two
# models. The task definition is therefore read out of the first pass script and
# handed to the second reader verbatim.
def system_prompt():
    import re as _re
    if os.path.exists(PILOT):
        m = _re.search(r'VISION_SYSTEM_PROMPT_V2 = """(.*?)"""', open(PILOT).read(), _re.S)
        if m:
            return m.group(1)
    sys.exit("cannot read VISION_SYSTEM_PROMPT_V2 from %s; run from the folder "
             "that holds the first pass script" % PILOT)


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


def find_jc_h_pages(pdf_path, max_pages=4):
    """Page selection copied from phase_3_p22_elsevier_cohort_b_pilot_v2.py so the
    second reader is shown the same pages as the first. Sending the first N pages
    instead shows the reader the front matter and produces spurious disagreement."""
    import fitz, re
    doc = fitz.open(str(pdf_path))
    n_total = doc.page_count
    scores = []
    for i, page in enumerate(doc):
        t = (page.get_text("text") or "").lower()
        s = 0
        if re.search(r"fig\.?\s*\d", t): s += 1
        if "critical current" in t or " jc " in t or "jc(" in t: s += 3
        if "field dependence" in t or "magnetic field" in t: s += 2
        if "vs h" in t or "vs. h" in t or "vs b" in t or "vs. b" in t: s += 2
        if "j_c(h)" in t or "jc(h)" in t or "jc(b)" in t: s += 3
        if "in-field" in t or "in field" in t: s += 1
        if "m-h loop" in t or "magnetization hysteresis" in t: s += 2
        if "bean model" in t or "bean-livingston" in t or "critical-state" in t: s += 2
        if "squid" in t or "vsm" in t: s += 1
        if "magneto-optical" in t or "mo imaging" in t or "faraday" in t: s += 2
        if "scanning hall" in t: s += 1
        if ("a/cm" in t or "ma/cm" in t): s += 1
        if "single crystal" in t or "thin film" in t: s += 1
        scores.append((i, s))
    doc.close()
    scores.sort(key=lambda x: -x[1])
    top = sorted([i for i, s in scores[:max_pages] if s > 0])
    if not top:
        top = list(range(min(3, n_total)))
    return top


def page_images(path, n_pages):
    import fitz
    idxs = find_jc_h_pages(path, max_pages=MAX_PAGES)
    doc = fitz.open(path)
    out = []
    for i in idxs[:max(1, n_pages)]:
        pix = doc.load_page(i).get_pixmap(dpi=DPI)
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


def _formula_key(v):
    """Loose compound comparison: notation differs between readers for the same
    material, e.g. FeTe0.5Se0.5 against Fe1-x(MWCNT)xTe0.5Se0.5."""
    if not isinstance(v, str):
        return v
    keep = "".join(c for c in v.lower() if c.isalnum())
    for junk in ("delta", "x", "mwcnt", "doped", "sample"):
        keep = keep.replace(junk, "")
    return keep


def compare(a, b):
    """Field-level agreement between the two readers."""
    res = {}
    for f in FIELDS:
        x, y = norm(a.get(f)), norm(b.get(f))
        if f == "primary_compound":
            kx, ky = _formula_key(x), _formula_key(y)
            res[f] = bool(kx and ky and (kx in ky or ky in kx)) or kx == ky
        elif isinstance(x, float) and isinstance(y, float):
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
    system = system_prompt()

    new = not os.path.exists(OUT)
    fh = open(OUT, "a", newline="")
    cols = (["paper", "in_fitted_cohort", "model", "n_pages", "cost_usd",
             "n_fields_compared", "n_fields_agree", "agreement_fraction",
             "pdf_pages_first_pass", "pdf_pages_now", "pdf_changed", "error"]
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
                   n_fields_agree="", agreement_fraction="",
                   pdf_pages_first_pass=first.get("n_pages_total"),
                   pdf_pages_now="", pdf_changed="", error="")
        if not pdf:
            row["error"] = "pdf_not_found"
            w.writerow(row); fh.flush(); continue
        try:
            import fitz as _f
            _d = _f.open(pdf); row["pdf_pages_now"] = _d.page_count; _d.close()
            row["pdf_changed"] = (row["pdf_pages_now"] != first.get("n_pages_total"))
            imgs = page_images(pdf, min(n_pages, MAX_PAGES))
            content = [{"type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": b}}
                       for b in imgs]
            content.append({"type": "text", "text": PROMPT})
            msg = client.messages.create(
                model=args.model, max_tokens=2000, system=system,
                messages=[{"role": "user", "content": content}])
            txt = "".join(b.text for b in msg.content if b.type == "text").strip()
            if txt.startswith("```"):
                txt = txt.split("```")[1]
                if txt.startswith("json"):
                    txt = txt[4:]
            if "{" not in txt or "}" not in txt:
                raise ValueError("stop_reason=%s, no JSON in reply: %s"
                                 % (msg.stop_reason, txt[:100]))
            second = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
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
