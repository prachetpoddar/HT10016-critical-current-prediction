#!/usr/bin/env python3
"""
plan_paragraph_splits.py

Where to break the paragraphs that run past ten rendered lines.

Hossain's ceiling is a ceiling on LINES, which a character count cannot stand
in for: a paragraph of 1,200 characters is eleven lines in one place and nine
in another once an equation, a subscript or a long compound name lands in it.
So this renders the document with LibreOffice, reads the rendered lines back,
and measures each paragraph as it actually sets.

Matching a paragraph to its rendered lines resynchronises on the paragraph's
own opening rather than walking the line list in order. A table between two
paragraphs contributes lines that belong to no paragraph, and a sequential
walk charges them to whatever comes next and then drifts for the rest of the
document. That drift is not hypothetical: it reported 18 oversized paragraphs
in the Supplemental Material where there were 11, and it would have cut four
paragraphs that did not need cutting.

Given the sentences of an oversized paragraph, a short dynamic program finds
the partition that keeps every piece inside the ceiling, preferring pieces
that fill it and penalising a piece that would open on a bare referent. A
paragraph beginning "It also requires" has lost its subject the moment a
blank line sits above it, so the planner avoids such a break where another
partition exists, and names the ones it cannot avoid.

Front matter, headings, captions, equation numbers and the reference list are
not paragraphs of prose and are left out.

Usage: python3 analysis/plan_paragraph_splits.py <docx> <plan.json>
"""
import pdfplumber, re, docx, json, os, math
import sys
SRC=sys.argv[1] if len(sys.argv)>1 else "out_final60/HT10016_revised_final60.docx"
OUT=sys.argv[2] if len(sys.argv)>2 else "analysis/paragraph_splits.json"
import subprocess, shutil
shutil.rmtree("/tmp/pdfs", ignore_errors=True)
subprocess.run(["soffice","--headless","--convert-to","pdf","--outdir","/tmp/pdfs",SRC],capture_output=True)
def norm(s): return re.sub(r'\s+',' ',s).strip()
lines=[]
with pdfplumber.open("/tmp/pdfs/"+os.path.basename(SRC).replace(".docx",".pdf")) as pdf:
    for pg in pdf.pages: lines += ((pg.extract_text() or "").split("\n"))
joined=[norm(l) for l in lines]
d=docx.Document(SRC)
paras=[p.text.strip() for p in d.paragraphs if p.text.strip()]
HEAD=re.compile(r'^(I{1,3}V?|IV|V|VI{0,3}|[A-H])\.\s+\S|^ABSTRACT|^REFERENCES|^ACKNOW|^ARTIFICIAL|^DATA AVAIL', re.I)
CAP=re.compile(r'^(FIG\.|TABLE)\s', re.I)
EQ=re.compile(r'^\(\d+\)$')
li=0; rows=[]
def head_of(t, n=28):
    return t[:n]
for idx,p in enumerate(paras):
    target=norm(p)
    # Resynchronise rather than walk blindly. A table between two paragraphs
    # contributes rendered lines that belong to no paragraph, and a sequential
    # walk silently charges them to whichever paragraph comes next, which then
    # drifts for the rest of the document. Find this paragraph's own opening
    # first, and measure from there.
    probe = head_of(target)
    at = -1
    for k in range(li, min(li+400, len(joined))):
        if joined[k].startswith(probe[:min(len(probe), len(joined[k]))]) or probe in joined[k]:
            at = k; break
    if at < 0:
        rows.append({"i":idx,"lines":None,"kind":"unmeasured","text":p}); continue
    li = at; acc=""; used=0
    while li<len(joined) and len(acc)<len(target)*0.92:
        acc=(acc+" "+joined[li]).strip(); li+=1; used+=1
        if used>60: break
    kind=("front" if idx<8 else "heading" if HEAD.match(p) else "caption" if CAP.match(p)
          else "equation" if EQ.match(p) else "body")
    rows.append({"i":idx,"lines":used,"kind":kind,"text":p})
ABBR=r'(?<!\bSec)(?<!\bSecs)(?<!\bFig)(?<!\bFigs)(?<!\bEq)(?<!\bEqs)(?<!\bRef)(?<!\bRefs)(?<!\bTab)(?<!\bNo)(?<!\bvs)(?<!\bal)(?<!\bcf)(?<!\bDr)(?<!\bProf)(?<!\bapprox)(?<!\be\.g)(?<!\bi\.e)(?<!\bSupp)(?<!\bMater)'
SPLIT=re.compile(ABBR+r'(?<=[.!?])\s+(?=[A-Z(])')
BARE=re.compile(r'^(It|They|Them|These|Those|Such|This|That|Its|Their|Here|There|Then|Otherwise|Thus|Hence)\b')
NOUNY=re.compile(r'^(This|That|These|Those|Such)\s+(a\s+|an\s+|the\s+)?[a-z]')
def penalty(s):
    if NOUNY.match(s): return 1      # carries its own noun: mild
    if BARE.match(s): return 6       # bare pronoun: bad
    return 0
MAX=10
REFS=next((r["i"] for r in rows if r["text"].upper().startswith("REFERENCES")), 10**9)
out=[]
for r in rows:
    if r["kind"]!="body" or r["lines"] is None or r["lines"]<=MAX or r["text"].startswith("[") or r["i"]>=REFS: continue
    ss=[s for s in SPLIT.split(r["text"]) if s.strip()]
    chars=len(r["text"]); lpc=r["lines"]/chars
    cum=[0.0]
    for s in ss: cum.append(cum[-1]+(len(s)+1)*lpc)
    n=len(ss)
    INF=1e9
    # dp[j] = (cost, prev) best cost to end a piece at boundary j
    dp=[(INF,None)]*(n+1); dp[0]=(0.0,None)
    for j in range(1,n+1):
        best=(INF,None)
        for i in range(0,j):
            if dp[i][0]>=INF: continue
            size=cum[j]-cum[i]
            if size>MAX+0.25: continue
            c=dp[i][0]+(MAX-size)**2*0.12          # prefer full pieces
            if i>0: c+=penalty(ss[i])
            if c<best[0]: best=(c,i)
        dp[j]=best
    if dp[n][0]>=INF:
        out.append({"i":r["i"],"lines":r["lines"],"marks":None,"sentences":ss}); continue
    marks=[]; j=n
    while dp[j][1] is not None and dp[j][1]>0:
        marks.append(dp[j][1]); j=dp[j][1]
    marks=sorted(marks)
    out.append({"i":r["i"],"lines":r["lines"],"marks":marks,"sentences":ss,
                "sizes":[round(cum[b]-cum[a],1) for a,b in zip([0]+marks, marks+[n])]})
json.dump(out, open(OUT,"w"), indent=1)
bad=[o for o in out if o["marks"] is None]
tot=sum(len(o["marks"]) for o in out if o["marks"])
print("paragraphs: %d, breaks: %d, unsolvable: %d" % (len(out), tot, len(bad)))
print("pieces over 10 lines after split:",
      sum(1 for o in out if o["marks"] for s in o["sizes"] if s>10.25))
print("\nbreaks still opening on a bare referent:")
k=0
for o in out:
    if not o["marks"]: continue
    for m in o["marks"]:
        if penalty(o["sentences"][m])>=6:
            k+=1; print("  [%3d] %s" % (o["i"], o["sentences"][m][:120]))
print("  total %d" % k)
for o in bad: print("UNSOLVABLE [%d] %d lines, %d sentences, longest sentence %d chars" % (o["i"],o["lines"],len(o["sentences"]),max(len(s) for s in o["sentences"])))
