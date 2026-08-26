"""Caption-scoped discriminator over the archived PDF corpus. Resumable:
each run processes for at most TIME_BUDGET seconds and appends to the CSV."""
import os, re, csv, subprocess, sys, time

ROOT = os.path.expanduser("~/mnt/SuperconductorWorkflow")
D    = os.path.join(ROOT, "kappa_pipeline/analysis/v3_2_9_path_2_prep/caption_sweep")
OUT  = os.path.join(D, "caption_sweep.csv")
TIME_BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 35.0

CAPTION    = re.compile(r"^\s*(fig(?:ure)?\.?\s*\.?\s*\d|table\s+\d)", re.I)
FIELD_TERM = re.compile(r"(?i)\b(h\s*_?\s*c2|b\s*_?\s*c2|hc2|bc2|upper[- ]critical[- ]field|"
                        r"irreversibility[- ]field|h\s*_?\s*irr|b\s*_?\s*irr|hirr|birr)\b")
TEMP_DEP   = re.compile(r"(?i)(vs\.?\s*t\b|versus\s+t\b|temperature[- ]depend|as a function of temperature|"
                        r"\(\s*t\s*\)|phase diagram|t\s*-\s*h\s+diagram|h\s*-\s*t\s+diagram|vs\.?\s*temperature)")
JC_TERM    = re.compile(r"(?i)\b(j\s*_?\s*c|critical current density|critical current)\b")
FIELD_DEP  = re.compile(r"(?i)(vs\.?\s*h\b|versus\s+h\b|vs\.?\s*b\b|vs\.?\s*(magnetic\s+)?field|"
                        r"field[- ]depend|as a function of (the )?(magnetic )?field|\(\s*h\s*\)|\bm\s*\(\s*h\s*\))")
FAMILY = {
 "iron_chalcogenide_11": re.compile(r"(?i)\bfese|fete|fe\(se|11[- ]type|iron chalcogen"),
 "iron_pnictide_122":    re.compile(r"(?i)bafe2as2|ba\(fe|kfe2as2|122[- ]type|\(ba[, ]?k\)fe|srfe2as2|cafe2as2"),
 "MgB2_class":           re.compile(r"(?i)\bmgb\s*_?\s*2|magnesium diboride|diboride"),
 "cuprate":              re.compile(r"(?i)ybco|rebco|bscco|yba\s*_?\s*2|bi\s*-?\s*22|lsco|cuprate"),
 "iron_pnictide_1111":   re.compile(r"(?i)lafeaso|smfeaso|ndfeaso|prfeaso|1111[- ]type|feaso"),
}
FIELDS = ["pdf","n_chars","families","cap_field_vs_T","cap_jc_vs_H","both","unreadable"]

done = set()
if os.path.exists(OUT):
    with open(OUT) as fh:
        for r in csv.DictReader(fh): done.add(r["pdf"])

paths, seen = [], set()
for dp, _, files in os.walk(ROOT):
    for f in files:
        if f.lower().endswith(".pdf") and f not in seen:
            seen.add(f); paths.append(os.path.join(dp, f))
todo = [p for p in paths if os.path.basename(p) not in done]

new, t0 = [], time.time()
for p in todo:
    if time.time() - t0 > TIME_BUDGET: break
    base = os.path.basename(p)
    try:
        t = subprocess.run(["pdftotext","-q","-l","40",p,"-"], capture_output=True, timeout=12
                           ).stdout.decode("utf8","ignore")
    except Exception:
        t = ""
    if not t:
        new.append(dict(pdf=base,n_chars=0,families="",cap_field_vs_T=0,cap_jc_vs_H=0,both=0,unreadable=1)); continue
    lines = t.splitlines()
    capblob = " || ".join(" ".join(lines[j:j+3]) for j,ln in enumerate(lines) if CAPTION.match(ln))
    fvt = 1 if (FIELD_TERM.search(capblob) and TEMP_DEP.search(capblob)) else 0
    jvh = 1 if (JC_TERM.search(capblob) and FIELD_DEP.search(capblob)) else 0
    fams = [k for k,rx in FAMILY.items() if rx.search(t[:200000])]
    new.append(dict(pdf=base,n_chars=len(t),families=";".join(fams),
                    cap_field_vs_T=fvt,cap_jc_vs_H=jvh,both=int(fvt and jvh),unreadable=0))

first = not os.path.exists(OUT)
with open(OUT,"a",newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    if first: w.writeheader()
    w.writerows(new)
print(f"unique_total={len(paths)} done_before={len(done)} added={len(new)} remaining={len(todo)-len(new)}")
