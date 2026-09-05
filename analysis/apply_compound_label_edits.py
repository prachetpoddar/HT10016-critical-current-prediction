"""
apply_compound_label_edits.py

Say in the documents what the 35 in Table I counts.

An independent review of the regenerated figures asked what "distinct
compounds" means, and the answer is that it counts labels drawn from two
naming systems: the structure registry's formula for Cohort A rows, the
paper's stoichiometry for Cohort B rows. Section II.D already discloses the
two systems and Table S3 already gives the mapping. What no document said is
that the count itself is a label count, so one material can be counted twice
(Pr2FeAs2O and PrFeAsO0.6F0.12 are the same specimen set from the same paper)
and one label can cover two dopings (Ba(FeAs)2 at 38 K, BaFe2As2 at 20 K).

analysis/compound_label_reduction.py reduces the 35 labels to 27 composition
keys under a stated rule and reports where that rule is wrong in each
direction. The numbers written in here come from that script.

Usage:
    python3 analysis/apply_compound_label_edits.py IN_DIR OUT_DIR

The script refuses to write if any target text is missing.
"""
import os
import re
import shutil
import sys
import zipfile

MAIN = "HT10016_revised_final14.docx"
SUPP = "SUPPLEMENTAL_MATERIAL_revised_final14.docx"
RESP = "RESPONSE_TO_REFEREES_final14.docx"

OUT = {MAIN: "HT10016_revised_final15.docx",
       SUPP: "SUPPLEMENTAL_MATERIAL_revised_final15.docx",
       RESP: "RESPONSE_TO_REFEREES_final15.docx"}

# (file, find, replace). Every one must match exactly once.
EDITS = [
    # ---- Table I, the row label and what it supports -------------------
    (MAIN, "Distinct compounds with fitted curves",
     "Distinct compound labels with fitted curves"),
    (MAIN, "Family population counts",
     "Family population counts. A label count, not a count of distinct "
     "materials; see Sec. II.D"),

    # ---- the abstract -------------------------------------------------
    (MAIN, "covering 35 compounds and 3303 extracted data points",
     "covering 35 compound labels, which reduce to 27 distinct composition "
     "keys, and 3303 extracted data points"),

    # ---- Sec. II.D, Compound naming -----------------------------------
    (MAIN,
     "and Bi-2223 for Sr2Ca2Cu3(BiO5)2.",
     "and Bi-2223 for Sr2Ca2Cu3(BiO5)2. One consequence should be stated "
     "plainly, because it bears on how Table I is read: the count of 35 in "
     "Table I is a count of these labels and not of distinct materials. Rows "
     "extracted through the registry carry the registry formula and rows "
     "extracted from the published paper carry the paper's stoichiometry, so "
     "the same material can appear under two labels, as Pr2FeAs2O and "
     "PrFeAsO0.6F0.12 do for one specimen set from one paper, while a single "
     "label can cover samples with different dopants and different transition "
     "temperatures, as Ba(FeAs)2 at 38 K and BaFe2As2 at 20 K do. Reducing "
     "the 35 labels to distinct combinations of substructure family, element "
     "set, and dopant marker leaves 27 composition keys; the reduction is "
     "mechanical and errs in both directions, merging Fe9Se8 with FeSe and "
     "separating PrFeAsO0.6F0.12 from Pr2FeAs2O, so 27 is reported as the "
     "output of a stated rule rather than as a material count. No aggregation "
     "in this work groups by label: exponents are aggregated by substructure "
     "family and sample form. The one analysis for which a label is the unit "
     "is the compound leave-one-out, and its two cohorts differ. The "
     "temperature-axis cohort holds nine labels denoting nine different "
     "compositions. The field-axis cohort holds ten, of which FeSe_Te_doped "
     "and FeTe0.5Se0.5 name the same Fe(Se,Te) material in two papers, so a "
     "compound held out under one label is not fully held out; the field axis "
     "is not validated at family level in this revision and no claim rests "
     "on it."),

    # ---- the Fig. 1 caption -------------------------------------------
    (MAIN, "contribute fitted curves across 35 compounds and 3303 "
           "critical-current data points",
     "contribute fitted curves across 35 compound labels, denoting 27 "
     "distinct composition keys in the reduction of Sec. II.D, and 3303 "
     "critical-current data points"),

    # ---- the response ladder ------------------------------------------
    (RESP, "50 contributing fitted curves, 35 distinct compounds, 3303 "
           "extracted critical-current points",
     "50 contributing fitted curves, 35 distinct compound labels, 3303 "
     "extracted critical-current points"),
    (RESP, "50 contributing papers, 35 compounds, 3303 extracted points",
     "50 contributing papers, 35 compound labels, 3303 extracted points"),
    (RESP, "The corrected counts are 50 papers, 35 compounds and 3303 "
           "extracted points.",
     "The corrected counts are 50 papers, 35 compound labels and 3303 "
     "extracted points."),
]


def paragraphs(doc):
    return re.findall(r"<w:p[ >].*?</w:p>", doc, re.S)


def plain(par):
    return "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", par, re.S))


def unescape(s):
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def replace_in_paragraph(par, find, repl):
    """Put repl where find is, inside one paragraph's runs.

    The replacement text lands in the first run of the matched span and the
    rest of the span is emptied. That keeps the first run's formatting and
    loses any variation inside the span, which is why the targets above are
    chosen to sit inside a single formatting run.
    """
    runs = list(re.finditer(r"<w:t[^>]*>(.*?)</w:t>", par, re.S))
    text = "".join(unescape(m.group(1)) for m in runs)
    at = text.find(find)
    if at < 0:
        return None
    end = at + len(find)
    out, pos, done = [], 0, False
    last = 0
    for m in runs:
        seg = unescape(m.group(1))
        lo, hi = pos, pos + len(seg)
        pos = hi
        out.append(par[last:m.start(1)])
        if hi <= at or lo >= end:
            out.append(m.group(1))
        else:
            keep_l = seg[:max(0, at - lo)]
            keep_r = seg[max(0, end - lo):] if hi > end else ""
            if not done:
                out.append(escape(keep_l + repl + keep_r))
                done = True
            else:
                out.append(escape(keep_r))
        last = m.end(1)
    out.append(par[last:])
    return "".join(out)


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: apply_compound_label_edits.py IN_DIR OUT_DIR")
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)

    by_file = {}
    for f, find, repl in EDITS:
        by_file.setdefault(f, []).append((find, repl))

    for name in (MAIN, SUPP, RESP):
        ip = os.path.join(src, name)
        op = os.path.join(dst, OUT[name])
        if not os.path.exists(ip):
            sys.exit("missing input: %s" % ip)
        zin = zipfile.ZipFile(ip)
        doc = zin.read("word/document.xml").decode("utf-8")
        for find, repl in by_file.get(name, []):
            pars = paragraphs(doc)
            hits = [p for p in pars if find in unescape(plain(p))]
            if len(hits) != 1:
                sys.exit("%s: %d paragraph(s) contain %r, expected exactly 1"
                         % (name, len(hits), find[:60]))
            new = replace_in_paragraph(hits[0], find, repl)
            if new is None:
                sys.exit("%s: could not place the replacement for %r"
                         % (name, find[:60]))
            doc = doc.replace(hits[0], new, 1)
            print("   %-42s %s" % (name.split("_")[0], find[:52]))
        tmp = op + ".part"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, doc)
                else:
                    zout.writestr(item, zin.read(item.filename))
        zin.close()
        shutil.move(tmp, op)
        print("   wrote %s" % op)
    return 0


if __name__ == "__main__":
    sys.exit(main())
