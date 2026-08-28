#!/usr/bin/env python3
"""
paired_extraction_agreement.py

Cross-model extraction agreement for manuscript HT10016, measured as a paired
run rather than against the first pass's cached output.

Referee A asked how reliable the vision extraction is. The obvious way to answer
that is to compare the cached first-pass assessments against a second model, but
that comparison does not isolate the model. Three things differ at once: the
first pass ran GPT-4o under a pydantic-constrained schema, many of the archive
PDFs were single-page previews at the time and have since been completed, and
only 29 of the 69 fitted-cohort entries appear in that cache at all, 9 of them
with an unchanged PDF. A rate built on that is not interpretable as a
cross-model rate.

This script instead runs two models now, over the same pages of the same current
document, under the same task definition, with the same requested output. The
model is then the only thing that differs.

Reader A : GPT-4o        (the model the extraction pipeline actually used)
Reader B : Claude Sonnet 5

The task definition is read verbatim out of the first pass script so that the
measurement applies to the extraction task as it was actually specified, and is
not a paraphrase of it.

Sources
-------
Fitted-cohort identifiers come from provenance_table_fitcohort_full.csv. PDFs are
resolved from the local archive where present and fetched from arXiv where the
identifier is an arXiv ID. MAGLAB_* identifiers are NHMFL tabulated data records
rather than papers and are reported as out of scope, not as failures.

Usage
-----
    export ANTHROPIC_API_KEY=...
    export OPENAI_API_KEY=...
    pip install anthropic openai pymupdf

    python3 paired_extraction_agreement.py --dry-run
    python3 paired_extraction_agreement.py --limit 10
    python3 paired_extraction_agreement.py
    python3 paired_extraction_agreement.py --scope archive     # the 662 archive

Cost
----
Roughly $0.04 per paper for the two readers together. The fitted cohort is about
$2.50. The script prints a running total and stops at --max-spend.
"""
import argparse, base64, csv, glob, json, os, re, sys, time, urllib.request

PILOT = "phase_3_p22_elsevier_cohort_b_pilot_v2.py"
PROV = "provenance_table_fitcohort_full.csv"
CACHE = "phase_3_p22_cohort_b_v2_vision_cache"
ARXIV_DIR = "audit/arxiv_pdfs"
REPLY_DIR = "audit/paired_replies"
OUT = "audit/paired_extraction_agreement.csv"

MODEL_A = "gpt-4o-2024-08-06"
MODEL_B = "claude-sonnet-5"
PRICE = {MODEL_A: (2.50, 10.00), MODEL_B: (3.00, 15.00)}   # $ per 1M in, out

DPI = 130
MAX_PAGES = 4

FIELDS = ["jc_h_sweep_present", "jc_t_sweep_present", "primary_scan_direction",
          "primary_compound", "T_min_K", "T_max_K", "H_min_T", "H_max_T"]
GATING = FIELDS[:3]
NUMERIC = ["T_min_K", "T_max_K", "H_min_T", "H_max_T"]

OUTPUT_SPEC = """Using the task definition above, report what these pages contain.
Answer only from what is printed on them.

Return a single JSON object with exactly these keys:
  jc_h_sweep_present     true if the paper presents Jc as a function of magnetic field,
                         by any of the accepted methodologies
  jc_t_sweep_present     true if the paper presents Jc as a function of temperature
  primary_scan_direction one of "H", "T", "both", "neither"
  primary_compound       the compound formula as printed, or null
  T_min_K, T_max_K       temperature range of the Jc data in kelvin, or null
  H_min_T, H_max_T       field range of the Jc data in tesla, converting from kOe or
                         gauss if the printed axis uses those units, or null

If a quantity is not shown on these pages, return null for it rather than
inferring a value. Return the JSON object and nothing else."""


def task_definition():
    """The first pass's own VISION_SYSTEM_PROMPT_V2, read verbatim."""
    if not os.path.exists(PILOT):
        sys.exit("cannot find %s; run from the folder that holds the first pass "
                 "script" % PILOT)
    m = re.search(r'VISION_SYSTEM_PROMPT_V2 = """(.*?)"""', open(PILOT).read(), re.S)
    if not m:
        sys.exit("VISION_SYSTEM_PROMPT_V2 not found in %s" % PILOT)
    return m.group(1)


# ---------------------------------------------------------------- sources

def local_pdfs():
    out = {}
    for f in glob.glob("*/*.pdf"):
        out.setdefault(os.path.basename(f)[:-4], f)
    return out


ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")


def resolve(identifier, pdfs):
    """Return (path, kind) or (None, reason)."""
    key = identifier
    for pre in ("elsevier_", "springer_", "iop_"):
        key = key.replace(pre, "")
    key = key.replace("/", "_")
    if key in pdfs:
        return pdfs[key], "local"
    core = re.sub(r"v\d+$", "", key)
    hit = [n for n in pdfs if core and core in n]
    if hit:
        return pdfs[sorted(hit)[0]], "local"
    if key.startswith("MAGLAB_"):
        return None, "out_of_scope_nhmfl_data_record"
    if ARXIV_RE.match(key):
        os.makedirs(ARXIV_DIR, exist_ok=True)
        dest = os.path.join(ARXIV_DIR, key + ".pdf")
        if os.path.exists(dest) and os.path.getsize(dest) > 20000:
            return dest, "arxiv_cached"
        url = "https://arxiv.org/pdf/" + key
        req = urllib.request.Request(url, headers={
            "User-Agent": "HT10016-reproducibility/1.0 (mailto:shossain@seas.ucla.edu)"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
            if not body.startswith(b"%PDF"):
                return None, "arxiv_fetch_not_a_pdf"
            open(dest, "wb").write(body)
            time.sleep(3)          # arXiv asks for one request every few seconds
            return dest, "arxiv_fetched"
        except Exception as exc:
            return None, "arxiv_fetch_failed: " + str(exc)[:60]
    return None, "pdf_unavailable"


# ------------------------------------------------------------ page choice

def find_jc_h_pages(pdf_path, max_pages=MAX_PAGES):
    """Page selection copied from phase_3_p22_elsevier_cohort_b_pilot_v2.py, so
    both readers are shown the pages the pipeline would have shown."""
    import fitz
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
        if "a/cm" in t or "ma/cm" in t: s += 1
        if "single crystal" in t or "thin film" in t: s += 1
        scores.append((i, s))
    doc.close()
    scores.sort(key=lambda x: -x[1])
    top = sorted([i for i, s in scores[:max_pages] if s > 0])
    if not top:
        top = list(range(min(3, n_total)))
    return top, n_total


def page_images(path, idxs):
    import fitz
    doc = fitz.open(path)
    out = []
    for i in idxs:
        pix = doc.load_page(i).get_pixmap(dpi=DPI)
        out.append(base64.b64encode(pix.tobytes("png")).decode())
    doc.close()
    return out


# ---------------------------------------------------------------- readers

def parse_json(txt):
    txt = txt.strip()
    if txt.startswith("```"):
        txt = txt.split("```")[1]
        if txt.startswith("json"):
            txt = txt[4:]
    if "{" not in txt or "}" not in txt:
        raise ValueError("no JSON object in reply: " + txt[:120])
    return json.loads(txt[txt.find("{"): txt.rfind("}") + 1])


def save_reply(ident, reader, txt):
    os.makedirs(REPLY_DIR, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", ident)
    path = os.path.join(REPLY_DIR, "%s.%s.txt" % (safe, reader))
    open(path, "w").write(txt)


def read_anthropic(client, model, system, imgs):
    content = [{"type": "image", "source": {"type": "base64",
                "media_type": "image/png", "data": b}} for b in imgs]
    content.append({"type": "text", "text": OUTPUT_SPEC})
    msg = client.messages.create(model=model, max_tokens=2000, system=system,
                                 messages=[{"role": "user", "content": content}])
    txt = "".join(b.text for b in msg.content if b.type == "text")
    if not txt.strip():
        raise ValueError("empty reply, stop_reason=%s" % msg.stop_reason)
    return (parse_json(txt), msg.usage.input_tokens, msg.usage.output_tokens,
            "stop_reason=%s\n%s" % (msg.stop_reason, txt))


def read_openai(client, model, system, imgs):
    content = [{"type": "image_url", "image_url":
                {"url": "data:image/png;base64," + b}} for b in imgs]
    content.append({"type": "text", "text": OUTPUT_SPEC})
    r = client.chat.completions.create(
        model=model, max_tokens=2000,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": content}])
    body = r.choices[0].message.content
    return (parse_json(body), r.usage.prompt_tokens, r.usage.completion_tokens,
            "finish_reason=%s\n%s" % (r.choices[0].finish_reason, body))


# ------------------------------------------------------------- comparison

ELEMENT = re.compile(r"[A-Z][a-z]?")
NOT_ELEMENTS = {"MWCNT", "CNT", "SWCNT"}


def norm(v):
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "yes"): return True
        if s in ("false", "no"): return False
        if s in ("null", "none", "nan"): return None
        try:
            return round(float(s), 3)
        except ValueError:
            return s
    if isinstance(v, (int, float)):
        return round(float(v), 3)
    return v


ACRONYM = re.compile(r"\(\s*[A-Z][A-Z0-9-]{2,}\s*\)")


def strip_acronym(s):
    """Drop a parenthesised all-caps name such as (BSCCO) or (YBCO). Parentheses
    carrying stoichiometry, as in Ba(Fe0.93Co0.07)2As2, are left alone."""
    return ACRONYM.sub("", s).strip() if isinstance(s, str) else s


def elements(s):
    if not isinstance(s, str) or not s.strip():
        return None
    s = re.sub(r"\((MWCNT|SWCNT|CNT)\)", "(C)", s, flags=re.I)
    s = strip_acronym(s)
    s = re.sub(r"[0-9.\-+()\[\]\s]", "", s)
    s = s.replace("x", "").replace("y", "").replace("z", "").replace("δ", "")
    return frozenset(e for e in ELEMENT.findall(s) if e not in NOT_ELEMENTS)


def compound_relation(a, b):
    """Label the relation between two compound strings rather than force it to a
    boolean. The first pass convention records the parent compound with doping in
    a separate field; a second reader records the full stoichiometry. Calling
    those two strings unequal measures the convention, and calling them equal
    would erase real phase differences such as Bi-2223 against Bi-2212, which
    share an element set. The non-exact cases are labelled so they can be
    adjudicated rather than averaged."""
    if not isinstance(a, str) or not isinstance(b, str) or not a.strip() or not b.strip():
        return "missing"
    ca = re.sub(r"[\s\-]", "", strip_acronym(a)).lower()
    cb = re.sub(r"[\s\-]", "", strip_acronym(b)).lower()
    if ca == cb:
        return "exact"
    ea, eb = elements(a), elements(b)
    if not ea or not eb:
        return "missing"
    if ea == eb:
        return "same_elements_diff_coefficients"     # candidate phase difference
    if ea < eb or eb < ea:
        return "subset_extra_elements"               # candidate doping notation
    return "disjoint"


def compare(a, b):
    res = {}
    for f in FIELDS:
        x, y = norm(a.get(f)), norm(b.get(f))
        if f == "primary_compound":
            rel = compound_relation(a.get(f), b.get(f))
            res[f] = (rel == "exact")
            res["_compound_relation"] = rel
        elif isinstance(x, float) and isinstance(y, float):
            res[f] = abs(x - y) <= max(0.05 * max(abs(x), abs(y)), 0.1)
        else:
            res[f] = (x == y)
    return res


# ------------------------------------------------------------------ main

def cost(model, nin, nout):
    pin, pout = PRICE[model]
    return (nin * pin + nout * pout) / 1e6


def targets(scope):
    if scope == "cohort":
        seen, out = set(), []
        for r in csv.DictReader(open(PROV)):
            i = r.get("identifier", "")
            if i and i not in seen:
                seen.add(i)
                out.append(i)
        return out
    return sorted(os.path.basename(p)[:-5]
                  for p in glob.glob(os.path.join(CACHE, "*.json")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=["cohort", "archive"], default="cohort")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fetch-only", action="store_true",
                    help="download the arXiv PDFs and stop, making no API calls")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-spend", type=float, default=30.0)
    ap.add_argument("--model-a", default=MODEL_A)
    ap.add_argument("--model-b", default=MODEL_B)
    args = ap.parse_args()

    ids = targets(args.scope)
    pdfs = local_pdfs()
    os.makedirs("audit", exist_ok=True)

    done = set()
    if os.path.exists(OUT):
        done = {r["identifier"] for r in csv.DictReader(open(OUT))}
    todo = [i for i in ids if i not in done]
    if args.limit:
        todo = todo[:args.limit]

    print("scope            : %s" % args.scope)
    print("identifiers      : %d   already done: %d" % (len(ids), len(done)))
    print("queued this run  : %d" % len(todo))
    print("readers          : %s  and  %s" % (args.model_a, args.model_b))

    if args.dry_run:
        kinds = {}
        for i in todo:
            key = i
            for pre in ("elsevier_", "springer_", "iop_"):
                key = key.replace(pre, "")
            key = key.replace("/", "_")
            if key in pdfs or [n for n in pdfs if re.sub(r"v\d+$", "", key) in n]:
                k = "local"
            elif key.startswith("MAGLAB_"):
                k = "out_of_scope_nhmfl_data_record"
            elif ARXIV_RE.match(key):
                k = "arxiv_to_fetch"
            else:
                k = "pdf_unavailable"
            kinds[k] = kinds.get(k, 0) + 1
        print("\nDRY RUN, no API calls and no downloads.")
        for k, v in sorted(kinds.items()):
            print("   %-34s %d" % (k, v))
        billable = sum(v for k, v in kinds.items()
                       if k in ("local", "arxiv_to_fetch"))
        print("\nbillable papers: %d, estimated spend $%.2f" % (billable, 0.04 * billable))
        return

    if args.fetch_only:
        got = fail = have = 0
        for ident in todo:
            path, kind = resolve(ident, pdfs)
            if kind == "arxiv_fetched":
                got += 1
                print("   fetched   %s" % ident)
            elif kind == "arxiv_cached":
                have += 1
            elif kind.startswith("arxiv_fetch_"):
                fail += 1
                print("   FAILED    %s   %s" % (ident, kind))
        print("\narXiv: %d fetched, %d already present, %d failed. No API calls made."
              % (got, have, fail))
        return

    for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        if not os.environ.get(var):
            sys.exit("%s is not set. Export it and run again." % var)
    import anthropic, openai
    ant = anthropic.Anthropic()
    oai = openai.OpenAI()
    system = task_definition()

    cols = (["identifier", "source", "n_pages", "pages", "pdf_n_pages",
             "model_a", "model_b", "cost_usd",
             "n_fields_compared", "n_fields_agree", "agreement_fraction",
             "gating_all_agree", "compound_relation", "error"]
            + ["agree__%s" % f for f in FIELDS]
            + ["a__%s" % f for f in FIELDS]
            + ["b__%s" % f for f in FIELDS])
    new = not os.path.exists(OUT)
    fh = open(OUT, "a", newline="")
    w = csv.DictWriter(fh, fieldnames=cols)
    if new:
        w.writeheader()

    spend = 0.0
    for n, ident in enumerate(todo, 1):
        if spend > args.max_spend:
            print("stopping: spend $%.2f exceeded --max-spend" % spend)
            break
        row = dict.fromkeys(cols, "")
        row.update(identifier=ident, model_a=args.model_a, model_b=args.model_b)
        path, kind = resolve(ident, pdfs)
        row["source"] = kind
        if not path:
            row["error"] = kind
            w.writerow(row); fh.flush()
            continue
        try:
            idxs, n_total = find_jc_h_pages(path)
            imgs = page_images(path, idxs)
            row.update(n_pages=len(idxs), pages=" ".join(str(i) for i in idxs),
                       pdf_n_pages=n_total)
            a, ain, aout, araw = read_openai(oai, args.model_a, system, imgs)
            save_reply(ident, "a", araw)
            b, bin_, bout, braw = read_anthropic(ant, args.model_b, system, imgs)
            save_reply(ident, "b", braw)
            c = cost(args.model_a, ain, aout) + cost(args.model_b, bin_, bout)
            spend += c
            agree = compare(a, b)
            rel = agree.pop("_compound_relation", "")
            n_ok = sum(1 for v in agree.values() if v)
            row.update(cost_usd=round(c, 5), n_fields_compared=len(agree),
                       n_fields_agree=n_ok,
                       agreement_fraction=round(n_ok / len(agree), 4),
                       gating_all_agree=all(agree[f] for f in GATING),
                       compound_relation=rel)
            row.update({"agree__%s" % f: agree[f] for f in FIELDS})
            row.update({"a__%s" % f: a.get(f) for f in FIELDS})
            row.update({"b__%s" % f: b.get(f) for f in FIELDS})
        except Exception as exc:
            detail = str(exc)
            if ("authentication" in detail.lower() or "invalid x-api-key" in detail
                    or "Incorrect API key" in detail):
                fh.close()
                sys.exit("\nAn API key was rejected (%s). Nothing further was "
                         "charged. Re-export and run again." % detail[:80])
            row["error"] = type(exc).__name__ + ": " + detail[:160]
            time.sleep(2)
        w.writerow(row); fh.flush()
        if n % 10 == 0:
            print("   %d/%d   running spend $%.2f" % (n, len(todo), spend))
    fh.close()
    print("\ndone. rows written to %s. spend this run $%.2f" % (OUT, spend))
    print("summarise with: python3 summarise_paired_agreement.py")


if __name__ == "__main__":
    main()
