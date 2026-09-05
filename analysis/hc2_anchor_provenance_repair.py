#!/usr/bin/env python3
"""
hc2_anchor_provenance_repair.py

What every Hc2 anchor in the field-axis cohort was actually read from, and which
passing fits do not survive being told.

Why. analysis/hc2_anchor_audit.py found two anchors that rise with temperature,
which no upper critical field does, and could not say why. The reason is in the
deposit's own supplementary files. Each paper in the Cohort B extension carries
an `*_HcT_supplementary.csv` whose `notes` column names the figure the anchor
was read from, and for several papers that figure does not measure a critical
field at all. The `Hc2_source` string in the fits file records only a
temperature and a term; the term is asserted, not derived.

The chain this walks:

    <paper>_HcT_supplementary.csv   ->  (T_K, field_T, source_term, notes)
    phase_3_form3_fits_partial_...  ->  Hc2_T_used, Hc2_source
    Eq. (1) field clause            ->  (Hmax - Hmin) / Hc2 > 0.3

The last step is why this matters. An irreversibility field is smaller than the
upper critical field, so recording one in the Hc2 slot shrinks the denominator
and makes a fit easier to pass, not harder. The error runs in the direction that
enlarges the cohort.

THE RULE, fixed before the tables were read
-------------------------------------------
A named source figure supports an anchor only as strong as what it measures:

  Hc2      a phase diagram, a stated upper critical field, or resistivity,
           susceptibility or magnetisation measured against TEMPERATURE in an
           applied field
  H_irr    a Jc-versus-field curve, a magnetisation loop against FIELD, or a
           pinning-force curve; the field is read off by a criterion and is an
           irreversibility field however the row labels it
  none     a figure of some other quantity, or a figure of literature data from
           other samples

A row is over-claimed when the term it records is stronger than what its own
named figure supports.

    python3 analysis/hc2_anchor_provenance_repair.py

Run from the repository root. Writes audit/hc2_anchor_provenance.csv and
changes nothing else.
"""
import glob
import os
import re
import sys

import pandas as pd

EXT = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
       "v3_2_2B_extension")
PDFS = ("/mnt/user-data/uploads/SuperconductorWorkflow/kappa_pipeline/analysis/"
        "v3_2_9_path_2_prep/phase_3_p19_elsevier_pdfs")
FITS = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
OUT = os.path.join("audit", "hc2_anchor_provenance.csv")

# The rule above, as patterns on the note. Order matters: the first class whose
# pattern matches is taken, so the disqualifying classes are tested first.
CLASSES = [
    ("literature_comparison", r"from the literature|literature showing"),
    ("relaxation_rate",       r"relaxation rate|interpolation index|\bS at\b"),
    ("phase_diagram",         r"phase diagram|upper critical field|critical "
                              r"field|\bBc2\b|\bHc2\b|WHH"),
    ("vs_temperature",        r"temperature dependence of (?:zero-field )?"
                              r"(?:resistivity|magneti|ac-susceptibility|"
                              r"magnetic moment)"),
    ("pinning_force",         r"pinning force"),
    ("Jc_vs_H",               r"j_?c ?\(?h\)?|jc vs|j_c vs|critical current "
                              r"density \(jc\) versus|field dependence of "
                              r"(?:the )?(?:in-plane )?critical current"),
    ("M_vs_H",                r"magnetic field dependence of magnetization|"
                              r"magnetic hysteresis|magnetization loop"),
]
SUPPORTS = {
    "phase_diagram": "Hc2",
    "vs_temperature": "Hc2",
    "Jc_vs_H": "H_irr",
    "M_vs_H": "H_irr",
    "pinning_force": "H_irr",
    "relaxation_rate": "none",
    "literature_comparison": "none",
    # a body-text statement that names a field is taken at its word; one that
    # names anything else records no source for a field
    "text_names_a_field": "as_recorded",
    "text_other": "none",
    # no note at all: the row records no source, so nothing supports it
    "unnamed": "none",
}
# How strong each recorded term claims to be.
CLAIMS = {
    "Hc2": "Hc2", "Bc2": "Hc2", "both_Hc2_and_H_irr": "Hc2",
    "H_irr": "H_irr", "Birr": "H_irr", "B_irr": "H_irr",
    "H_irr_Birr": "H_irr",
    "ambiguous_label": "ambiguous",
}
# An `ambiguous_label` row is one the extractor could not resolve, but the fits
# file consumes its value in the Hc2 slot, so the effective claim is an Hc2 and
# it is ranked as one. Ranking it at zero, as the first version did, made the
# least certain provenance class the one class that could never be flagged.
RANK = {"none": 0, "H_irr": 1, "ambiguous": 2, "Hc2": 2}


def classify(note):
    """Which class of figure the note names, and the strongest field it supports."""
    if not isinstance(note, str) or not note.strip() or note.strip() == "nan":
        return "unnamed", SUPPORTS["unnamed"]
    for name, pat in CLASSES:
        if re.search(pat, note, re.I):
            return name, SUPPORTS[name]
    # A note that is not a figure caption is a body-text statement. It is taken
    # at its word only when it names a field; a note that names something else
    # (a project specification, a temperature, "approximation from body text")
    # records no source for a field and supports nothing.
    if re.search(r"critical field|\bHc2\b|\bBc2\b|\bBz0\b|irrevers|"
                 r"\bH ?/{0,2}(?:ab|c)\b|pressure|WHH", note, re.I):
        return "text_names_a_field", "as_recorded"
    return "text_other", "none"


def squash(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def caption_status(note, text):
    """Whether the paper carries the figure the note names, at that number.

    The first version of this compared the note's words against the whole
    document with the separators stripped. That returns yes for an invented
    caption against an unrelated paper, because the vocabulary of a figure
    caption in this field is common to every paper in it, and it never checked
    the figure NUMBER at all, so a note naming Fig. 2 was satisfied by Fig. 6.

    This version finds the figure label in the text and compares only the
    window that follows it. Words are matched with boundaries so that "plane"
    does not match inside "ab-plane". Captions are matched word by word rather
    than as a string because pdfplumber splits subscripts out of the line
    ("J_c(H)" comes back as "J(H)" with a stray "c").
    """
    if text is None:
        return "no_pdf"
    if not isinstance(note, str):
        return "not_a_caption"
    m = re.match(r"\s*Fig(?:ure)?\.?\s*([0-9]+)", note, re.I)
    if not m:
        return "not_a_caption"
    number = m.group(1)
    words = [w for w in re.findall(r"[a-z]+", note.lower())
             if len(w) >= 4 and w not in ("figure",)]
    if len(words) < 4:
        return "too_short"
    flat = re.sub(r"\s+", " ", text)
    labels = list(re.finditer(rf"Fig(?:ure)?\.?\s*{number}\b", flat, re.I))
    if not labels:
        return "no_such_figure"
    best = 0.0
    for lab in labels:
        # The window is squashed rather than matched word by word: pdfplumber
        # returns long runs with the spaces missing, so a word-boundary test
        # fails on text that is plainly there. Confining the test to the window
        # after the right figure label is what makes it mean something.
        window = squash(flat[lab.start():lab.start() + 30 * len(words)])
        hit = sum(1 for w in words if w in window)
        best = max(best, hit / len(words))
    return "yes" if best >= 0.7 else "no"


def pdf_text(paper_id):
    """The paper's full text, or None when there is no PDF to read.

    The filename is not trusted. One PDF in this corpus is filed under a DOI
    that is not its own, and it is a paper this audit reports on, so the DOI
    printed on the document itself is compared with the identifier before the
    text is used for anything.
    """
    doi = paper_id.split("_", 1)[1] if "_" in paper_id else paper_id
    path = os.path.join(PDFS, doi.replace("/", "_") + ".pdf")
    if not os.path.exists(path):
        return None, "no_pdf"
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        raw = " ".join((p.extract_text() or "") for p in pdf.pages)
    m = re.search(r"doi:\s*(10\.\d{4,}/[^\s,]+)", raw, re.I)
    printed = m.group(1).rstrip(".").lower() if m else ""
    want = doi.replace("_", "/").lower()
    if printed and printed.replace(" ", "") not in want.replace(" ", ""):
        return None, f"pdf_is_{printed}"
    return raw, "ok"


# Readings that decide a paper's fits and that no rule above can reach. Each is
# a phrase the script locates in the paper itself, so the reading is reproduced
# rather than asserted. The check runs on every run and prints a line per item.
READINGS = [
    ("elsevier_10.1016/j.matchemphys.2023.128348", "present",
     "Jcdecreasedfrom1.11", "10.0 K 1.11 and 15.0 K 9.34 are the paper's "
     "self-field Jc in 1e5 A/cm2, entered in the field column as tesla"),
    ("elsevier_10.1016/j.physc.2009.11.051", "absent", "irrevers",
     "the paper prints no irreversibility field"),
    ("elsevier_10.1016/j.physc.2009.11.051", "absent", "uppercritical",
     "the paper prints no upper critical field"),
    ("elsevier_10.1016/j.physc.2010.05.048", "absent", "irrevers",
     "the paper prints no irreversibility field"),
    ("elsevier_10.1016/j.physc.2010.05.048", "absent", "uppercritical",
     "the paper prints no upper critical field"),
]


def check_readings():
    """Locate each decisive phrase in its paper. Returns the number that failed."""
    bad = 0
    for pid, want, phrase, why in READINGS:
        raw, state = pdf_text(pid)
        if state != "ok":
            print(f"  [SKIP] {pid.split('/')[-1]:26s} {state}")
            bad += 1
            continue
        there = squash(phrase) in squash(raw)
        ok = (there and want == "present") or (not there and want == "absent")
        print(f"  [{'PASS' if ok else 'FAIL'}] {pid.split('/')[-1]:26s} "
              f"{phrase!r} {want} -> {why}")
        bad += not ok
    return bad


def rising_within_file(prov):
    """Rows contradicted by another row of the same file at a higher temperature.

    Both Hc2 and the irreversibility field fall as temperature rises, so a
    paper's own file recording a LARGER field at a HIGHER temperature makes the
    smaller row wrong, whatever figure it names. This catches the case the
    term-versus-figure rule is blind to: a value that is not the field it is
    called but the instrument's maximum. phpro.2015.06.160 records 9.0 T at
    17.7 K, exactly the 9 T maximum its own figure states, alongside 26 T at
    18.9 K from the same paper's body text.
    """
    out = []
    keys = ["paper_id", "note", "source_term", "field_orientation",
            "sample_form", "figure_id"]
    keys = [k for k in keys if k in prov.columns]
    for gid, g in prov.groupby(keys, dropna=False):
        pid = gid[0] if isinstance(gid, tuple) else gid
        g = g.dropna(subset=["T_K"])
        for i, r in g.iterrows():
            higher = g[(g.T_K > r.T_K) & (g.field_T > r.field_T)]
            if len(higher):
                top = higher.loc[higher.field_T.idxmax()]
                out.append(dict(paper_id=pid, ladder=str(gid[1])[:38],
                                T_K=r.T_K, field_T=r.field_T,
                                contradicted_by=f"{top.field_T} T at {top.T_K} K",
                                factor=round(top.field_T / r.field_T, 2)))
    return pd.DataFrame(out)


def selftest():
    """The caption check has to fail on captions it should fail on.

    Two known-bad inputs, both of which the first version of caption_status
    passed: a caption for a figure number the paper does not have, and a real
    caption from one paper checked against a different paper.
    """
    raw, state = pdf_text("elsevier_10.1016/j.physc.2009.11.051")
    if state != "ok":
        raise SystemExit(f"selftest cannot run: {state}")
    cases = [
        ("Fig. 99. Temperature dependence of magnetization measured under "
         "several magnetic fields for these samples.", "no_such_figure"),
        ("Fig. 3. Temperature dependence of upper critical field along "
         "ab-plane and c-axis obtained by the midpoint criterion.", "no"),
    ]
    bad = 0
    for note, want in cases:
        got = caption_status(note, raw)
        ok = "PASS" if got == want else "FAIL"
        bad += got != want
        print(f"  [{ok}] {note[:52]:52s} want {want:15s} got {got}")
    print("  selftest:", "all guards fire" if not bad else f"{bad} GUARD(S) DID NOT FIRE")
    return bad


def main():
    if "--selftest" in sys.argv:
        return selftest()
    print("decisive readings, located in the papers themselves")
    if check_readings():
        print("  A READING DID NOT REPRODUCE. The claims that rest on it are "
              "not supported by this run.")
    print()
    rows = []
    texts = {}
    for f in sorted(glob.glob(os.path.join(EXT, "*_HcT_supplementary.csv"))):
        d = pd.read_csv(f)
        missing = ({"paper_id", "T_K", "field_T", "source_term", "notes"}
                   - set(d.columns))
        if missing:
            raise SystemExit(f"{f} is missing columns {sorted(missing)}")
        for _, r in d.iterrows():
            fig, supports = classify(r.notes)
            term = str(r.source_term)
            claim = CLAIMS.get(term, "unknown")
            pid = r.paper_id
            if pid not in texts:
                texts[pid] = pdf_text(pid)
            t, pdf_state = texts[pid]
            # Does the named figure exist in the paper at all? A caption is
            # matched on its first sixty squashed characters.
            found = (caption_status(r.notes, t) if pdf_state == "ok"
                     else pdf_state)
            rows.append(dict(
                paper_id=pid, T_K=r.T_K, field_T=r.field_T,
                source_term=term, claims=claim,
                field_orientation=r.get("field_orientation", ""),
                sample_form=r.get("sample_form", ""),
                figure_id=r.get("figure_id", ""),
                source_figure_class=fig, figure_supports=supports,
                caption_found_in_pdf=found,
                over_claimed=(supports != "as_recorded"
                              and RANK.get(claim, 0) > RANK.get(supports, 0)),
                note=str(r.notes)[:110],
            ))
    prov = pd.DataFrame(rows)

    # Anchors that never reach a fit are noise; join to the passing cohort.
    fits = pd.read_csv(FITS)
    passing = fits[(fits.ok == True) & (fits.physicality == "ok")].copy()
    if len(passing) != 94:
        print(f"NOTE: the passing cohort is {len(passing)} fits, not the 94 "
              f"this audit was written against. The counts below still stand "
              f"for whatever cohort is present.")

    def anchor_T(src):
        """The temperature the anchor was read or extrapolated to, if named."""
        m = re.search(r"(?:at_|anchor_)([0-9.]+)K", str(src))
        return float(m.group(1)) if m else float("nan")

    passing["anchor_T"] = passing.Hc2_source.map(anchor_T)

    # Match a fit to the anchor row it used by the VALUE of the anchor, which
    # survives the extrapolated and interpolated cases where the temperature in
    # the source string is the row's and not the fit's. Where more than one row
    # of the paper carries that value, the classes of all of them are reported
    # and the fit counts as over-claimed only if every candidate is.
    recs = []
    for _, r in passing.iterrows():
        cand = prov[(prov.paper_id == r.paper_key)
                    & (abs(prov.field_T - r.Hc2_T_used) < 1e-6)]
        if len(cand):
            supports = sorted(set(cand.figure_supports))
            claims = sorted(set(cand.claims))
            classes = sorted(set(cand.source_figure_class))
            # any(), not all(): where two rows of a paper share a value and
            # only one of them is over-claimed, the fit cannot be said to rest
            # on the clean one.
            over = bool(cand.over_claimed.any())
            note = cand.iloc[0].note
            at_own_T = bool((cand.T_K == r.fixed_axis_value).any())
        else:
            supports, claims, classes, over, note, at_own_T = [], [], [], False, "", False
        recs.append(dict(
            paper_key=r.paper_key, sample=r.sample_identifier,
            fixed_T=r.fixed_axis_value, Hc2_T_used=r.Hc2_T_used,
            Hc2_source=r.Hc2_source, anchor_T=r.anchor_T,
            matched=bool(len(cand)),
            source_figure_class="|".join(classes),
            figure_supports="|".join(supports),
            claims="|".join(claims),
            anchor_row_at_fit_temperature=at_own_T,
            over_claimed=over,
            note=note,
        ))
    joined = pd.DataFrame(recs)
    os.makedirs("audit", exist_ok=True)
    joined.to_csv(OUT, index=False)

    print(f"{len(prov)} anchor rows across {prov.paper_id.nunique()} papers")
    print()
    print("what the named source figures measure")
    print(prov.groupby(["source_figure_class", "figure_supports"]).size().to_string())
    print()
    print("named figures checked against the PDF in the corpus")
    print(prov.caption_found_in_pdf.value_counts().to_string())
    miss = prov[prov.caption_found_in_pdf == "no"]
    for pid, g in miss.groupby("paper_id"):
        print(f"  not found: {pid}  {g.iloc[0].note[:70]}")
    print()
    print("rows whose recorded term is stronger than their figure supports")
    bad = prov[prov.over_claimed]
    for _, r in bad.iterrows():
        print(f"  {r.paper_id:52s} {r.T_K:>6} K  {r.field_T:>7} T  "
              f"term={r.source_term:<20s} figure={r.source_figure_class}")
    print()
    print(f"passing fits matched to an anchor row by value: "
          f"{joined.matched.sum()} of {len(joined)}")
    print()
    print("unmatched passing fits: no row of their paper carries the value used")
    um = joined[~joined.matched]
    print(um.groupby(["paper_key", "Hc2_source"]).size().to_string())
    print()
    print("matched passing fits by what their own anchor's figure supports")
    print(joined[joined.matched].groupby(["paper_key", "figure_supports"])
          .size().to_string())
    print()
    over = joined[joined.over_claimed]
    print(f"passing fits resting on an over-claimed anchor: {len(over)} "
          f"over {over.paper_key.nunique()} papers")
    print(over.groupby(["paper_key", "source_figure_class", "claims"]).size().to_string())
    print()
    held = joined[joined.matched & ~joined.anchor_row_at_fit_temperature]
    print(f"matched passing fits whose anchor row was read at a DIFFERENT "
          f"temperature than the fit: {len(held)} of {int(joined.matched.sum())}")
    down = held[held.anchor_T > held.fixed_T]
    print(f"  of those, held from a HIGHER temperature down to the fit's: "
          f"{len(down)}, by up to {(down.anchor_T - down.fixed_T).max():.1f} K")
    print("  both fields rise as temperature falls, so this understates the "
          "denominator and enlarges the cohort")
    print(down.groupby("paper_key").size().to_string())
    print()
    rise = rising_within_file(prov)
    print(f"anchor rows contradicted by another row of the SAME ladder "
          f"(same paper, figure, term, orientation and sample) at a higher "
          f"temperature: {len(rise)}")
    if len(rise):
        # Sorted by how far the inversion runs: a ratio near one is digitisation
        # noise on a ladder that is otherwise the right way up, a ratio of
        # several is a ladder that runs backwards.
        print(rise.sort_values("factor", ascending=False).to_string(index=False))
    print()
    none = joined[joined.figure_supports.str.contains("none")]
    print(f"passing fits whose anchor row names no source, or names a figure "
          f"that measures no critical field: {len(none)} over "
          f"{none.paper_key.nunique()} papers")
    print(none.groupby(["paper_key", "source_figure_class"]).size().to_string())
    print()
    # The applicability window of Eq. (1) has two clauses. Only one of them is
    # applied here, and the cohort is screened on it exactly.
    tr = passing.fixed_axis_value / passing.Tc_K_anchor
    print("the applicability window, as applied to this cohort")
    print(f"  field clause  (Hmax-Hmin)/Hc2 > 0.3 : "
          f"{int((passing.H_axis_range_normalized <= 0.3).sum())} of "
          f"{len(passing)} passing fits violate it")
    print(f"  temperature clause  T/Tc < 0.7      : "
          f"{int((tr > 0.7).sum())} of {len(passing)} passing fits violate it, "
          f"the worst at T/Tc = {tr.max():.3f}")
    print("  the temperature clause is not applied to the fit cohort; the "
          "field clause partitions it exactly")
    print(passing[tr > 0.7].groupby("paper_key").size().to_string())
    print()
    print(f"written: {OUT}")


if __name__ == "__main__":
    sys.exit(main() or 0)
