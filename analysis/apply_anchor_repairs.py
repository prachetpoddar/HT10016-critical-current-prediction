#!/usr/bin/env python3
"""
apply_anchor_repairs.py

Repair the anchor layer on both axes, and recompute everything that depends on
it.

Why now. The anchor is the scale of the frozen factor of Eq. (1). On the
temperature axis it sets the fit window and the abscissa; on the field axis it
also sets which points are kept and the applicability clause. Nothing downstream
is stable until it is right, so this runs before any re-extraction.

What is repaired, and on what evidence. Every correction below is a value
printed in the paper the record claims to come from, located in the PDF by
analysis/tc_anchor_audit.py or analysis/cohortB_tc_anchor_check.py, or a
provenance defect established by analysis/hc2_anchor_provenance_repair.py. No
correction is an estimate.

REPRODUCTION BEFORE CHANGE. Both fit rules are recovered from the extractions
first, and the script refuses to write anything if they are not:

  beta_T  257 of 258 fits with an extraction
  beta_H  88 of the 94 passing fits, the other six being 1002.0208v2, which is
          keyed in the other extraction file

Only fits whose rule is reproduced are refitted. A fit whose anchor changed but
whose rule is not reproduced is marked, not silently recomputed.

    python3 analysis/apply_anchor_repairs.py --check     report, write nothing
    python3 analysis/apply_anchor_repairs.py --apply     write the repairs

Run from the repository root. --apply snapshots every table it touches into
audit/pre_anchor_repair_20260905/ first, and writes a ledger to
audit/anchor_repairs.csv with one row per change.
"""
import os
import shutil
import sys

import numpy as np
import pandas as pd

MASTER_B = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
            "agent2_dataset_v3_2_2B.csv")
MASTER_A = ("/mnt/user-data/uploads/SuperconductorWorkflow/data_agent2/"
            "agent2_dataset_v3_2_1.csv")
FITS_B = os.path.join("data", "phase_3_form3_fits_partial_cohortB_v2.csv")
FITS_A = os.path.join("data", "phase_3_p44_post_UCLA_beta_T_fits.csv")
PROV = os.path.join("data", "provenance_table_fitcohort_full.csv")
SNAP = os.path.join("audit", "pre_anchor_repair_20260905")
LEDGER = os.path.join("audit", "anchor_repairs.csv")
TEMP_CLAUSE = 0.7
FIELD_CLAUSE = 0.3
MIN_PTS = 3
# the span of the abscissa a fit is made over. Below this the exponent is not
# identified by the data: a 15.5 against a deposited 1.4 was a short-lever
# artefact once already, in analysis/refit_from_traces.py.
MIN_LEVER_DEX = 0.05
# a range for beta_H outside which the fit is reported but not believed. The
# deposit applies no upper screen at all: its passing cohort already contains a
# 12.14 and its bounded set a 30.0. This is a flag, not a gate, because setting
# the gate is a protocol decision and not an anchor repair.
BETA_PLAUSIBLE = (0.2, 5.0)

# ---------------------------------------------------------------- corrections
# paper -> Tc the paper prints for the sample whose figure was extracted.
# Quotes are in analysis/tc_anchor_audit.py TC_READ.
TC_A = {
    "0806.2839v1.pdf": 54.6, "0903.0004v2.pdf": 22.6, "0906.0444v1.pdf": 24.0,
    "0907.0147v2.pdf": 15.3, "1002.0208v2.pdf": 48.0, "1104.0477v2.pdf": 15.2,
    "1108.0407v1.pdf": 9.8, "1111.3923v1.pdf": 17.7, "1502.05345v1.pdf": 30.7,
    "1611.08455v1.pdf": 13.7, "1903.00866v2.pdf": 36.0, "2012.13723v3.pdf": 36.4,
    "2207.06629v1.pdf": 39.8, "2305.10034v1.pdf": 13.3, "2308.10492v1.pdf": 19.3,
    "2510.10264v1.pdf": 25.1, "2511.19058v1.pdf": 9.0,
}
# the one paper that states no Tc for its own sample: the anchor stays, the
# claim that it is paper-reported does not
TC_A_UNSTATED = {"1009.4896v1.pdf": "the paper states no Tc for this sample; "
                                    "its only temperatures are measurement "
                                    "temperatures"}

# (paper fragment, sample or None) -> Tc, from analysis/cohortB_tc_anchor_check.py
TC_B = {
    ("physc.2010.05.048", None): 12.0,
    ("physc.2009.11.051", None): 24.0,
    ("jallcom.2023.170384", None): 13.3,
    ("matchemphys.2023.128348", None): 37.7,
    ("mtphys.2022.100783", "Polycrystal"): 25.7,
    ("mtphys.2022.100783", "Single crystal"): 24.4,
    ("phpro.2015.06.160", "BaFe1.91Ni0.09As2"): 18.9,
    ("phpro.2015.06.160", "Ba0.64K0.36Fe2As2"): 25.5,
    ("jallcom.2013.04.183", "N1"): 74.38,
    ("jallcom.2013.04.183", "N2"): 64.11,
    ("jallcom.2013.04.183", "N3"): 66.0,
    ("jallcom.2013.04.183", "N4"): 74.18,
    ("cjph.2024.09.042", "FeSe"): 10.0,
    ("cjph.2024.09.042", "H_x-FeSe 1#"): 41.0,
    ("cjph.2024.09.042", "H_x-FeSe 2#"): 41.0,
}
TC_B_NOTE = {
    "cjph.2024.09.042": "41 K is the M(T) value, the same measurement as the "
                        "10 K it is compared with. The paper also gives a "
                        "resistive onset of 44.5 K for sample 2#.",
    "jallcom.2013.04.183": "the deposit also records this Bi-2212 paper as "
                           "Bi-2223; the compound string is not repaired here.",
}

# Hc2 anchors replaced by a value the paper prints
HC2_B = {
    ("phpro.2015.06.160", "BaFe1.91Ni0.09As2"): (
        26.0, "the recorded 9.0 T is the maximum applied field its own Fig. 1 "
              "states, not a critical field. The paper gives Hc2(0) = 26 T for "
              "this sample."),
    ("phpro.2015.06.160", "Ba0.64K0.36Fe2As2"): (
        31.0, "the same, and the paper gives 31 T for THIS sample. The first "
              "version of this repair applied 26 T to both, which is the other "
              "sample's number."),
    # physc.2013.04.060's own Table 1 (10 K) and Table 2 (4.2 K), Birr defined
    # by the paper as the field at which Jc falls to 100 A/cm2. The first
    # version withdrew this paper for having no source; it has two tables of
    # per-sample sources, and the deposit mis-transcribed two of them.
    ("physc.2013.04.060", "Undoped_MgB2_10K"): (11.0, "Table 1, MgB2"),
    ("physc.2013.04.060", "SiC_Doped_MgB2_10K"): (16.9, "Table 1, +SiC"),
    ("physc.2013.04.060", "ZrB2_Doped_MgB2_10K"): (13.1, "Table 1, +ZrB2"),
    ("physc.2013.04.060", "Ag_Doped_MgB2_10K"): (14.5, "Table 1, +Ag"),
    ("physc.2013.04.060", "TiC_Doped_MgB2_10K"): (11.9, "Table 1, +TiC"),
    ("physc.2013.04.060", "MgB2_4_2K"): (11.2, "Table 2, MgB2-00"),
    ("physc.2013.04.060", "MgB(2-x)Cx_x_0_0386_4_2K"): (15.3, "Table 2, MgB2-01"),
    ("physc.2013.04.060", "MgB(2-x)Cx_x_0_1202_4_2K"): (23.6, "Table 2, MgB2-04"),
}
# what the deposit recorded against what the paper prints, for the record
MISTRANSCRIBED = {
    "physc.2013.04.060": "the supplementary records MgB2 at 11.9 T, which is "
                         "the TiC value, and +ZrB2 at 14.5 T, which is the Ag "
                         "value, and omits +Ag entirely. All five 10 K fits "
                         "use a single 11.9 T.",
}

# whole papers whose anchor supports nothing, with the reason
# Two clauses were dropped from these reasons after review, because they do not
# hold. The kilo-oersted clause is scale-invariant where the anchor was read off
# the same kilo-oersted figure as the data: dividing both by ten leaves
# (Hmax - Hmin)/Hc2 exactly where it was. And it contradicts the
# instrument-maximum clause that stood beside it, since values in kilo-oersted
# do not exceed a 5 T maximum. Both clauses are gone; what remains is what the
# papers do and do not print.
WITHDRAW_B = {
    "physc.2009.11.051": "the paper contains no occurrence of 'upper critical' "
                         "or 'irrevers' anywhere in its text, and has no "
                         "critical-field figure; the anchor's own source note "
                         "names a figure that measures neither; and the "
                         "recorded values rise monotonically with temperature "
                         "within one sample, which no critical field does",
    "physc.2010.05.048": "the same: no occurrence of 'upper critical' or "
                         "'irrevers' anywhere in the text, no critical-field "
                         "figure, a source note naming the magnetisation "
                         "loops, and a ladder rising by a factor of seven with "
                         "temperature within one sample",
    "physc.2009.05.098": "the field axis is kilo-oersted recorded as tesla, "
                         "confirmed at source, and the anchor is an 86 T "
                         "literature default that does NOT scale with the "
                         "axis, so correcting the unit takes the measured span "
                         "from 0.53 to 0.053 of it and the field clause fails. "
                         "This is the one paper of the three for which the "
                         "unit argument does any work.",
}

# recorded term stronger than the source figure supports; value unchanged
RETERM_B = {
    "matpr.2019.05.078": ("Hc2", "H_irr", "the source note names Fig. 2(a), a "
                                          "Jc-versus-field figure, which gives "
                                          "an irreversibility field"),
    "physc.2011.05.018": ("Hc2", "H_irr", "the source note names Fig. 2(c,d), "
                                          "magnetisation loops"),
}


def beta(x_num, J, scale):
    """log10 Jc on log10(1 - x/scale). The rule both axes use.

    Returns the slope, the number of points, and the span of the abscissa,
    which is the lever the slope is estimated over.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        x = np.log10(1 - np.asarray(x_num, float) / scale)
        y = np.log10(np.asarray(J, float))
    m = np.isfinite(x) & np.isfinite(y) & (np.asarray(J, float) > 0)
    if m.sum() < MIN_PTS:
        return np.nan, int(m.sum()), 0.0
    lev = float(x[m].max() - x[m].min())
    return float(np.polyfit(x[m], y[m], 1)[0]), int(m.sum()), lev


def slice_for(master, key_col, paper, at_col, at, sample_cols=()):
    """Rows of the extraction for one fit, trying each sample split in turn."""
    g0 = master[(master[key_col] == paper) & (np.isclose(master[at_col], at))]
    if not len(g0):
        return []
    out = [("all", g0)]
    for c in sample_cols:
        if c in g0.columns and g0[c].nunique() > 1:
            out += [(f"{c}={v}", g) for v, g in g0.groupby(c)]
    return out


def reproduce_B(master, fits):
    """For each field-axis fit, the extraction slice that recovers its beta."""
    found = {}
    for i, r in fits.iterrows():
        hit = None
        # the fits table carries BOTH arxiv_id and paper_key and they differ on
        # one paper. Keying on paper_key alone lost six fits of 1002.0208v2,
        # whose extraction is filed under its arxiv_id, and the loss was then
        # reported as a property of the data.
        key = (r.arxiv_id if r.arxiv_id in set(master.arxiv_id)
               else r.paper_key)
        for fac in (1.0, 0.95):
            for name, g in slice_for(master, "arxiv_id", key,
                                     "temperature_K", r.fixed_axis_value,
                                     ("doping_or_composition", "sample_form",
                                      "figure_id", "notes")):
                gg = g[g.field_T < fac * r.Hc2_T_used]
                b, n, _ = beta(gg.field_T, gg.Jc_A_per_cm2, r.Hc2_T_used)
                if np.isfinite(b) and abs(b - r.beta) < 1e-3 and n == r.n_pts:
                    hit = (name, fac)
                    break
            if hit:
                break
        found[i] = hit
    return found


def reproduce_A(master, fits):
    found = {}
    for i, r in fits.iterrows():
        g = master[(master.pdf_name == r.paper_key)
                   & (np.isclose(master.field_T, r.field_T))]
        g = g[(g.temperature_K >= r.T_min - 1e-9)
              & (g.temperature_K <= r.T_max + 1e-9)]
        b, n, _ = beta(g.temperature_K, g.Jc, r.Tc_K)
        found[i] = (np.isfinite(b) and abs(b - r.beta_T) < 1e-3
                    and n == r.n_T_pts)
    return found


def tc_for(paper_key, sample):
    for (frag, samp), v in TC_B.items():
        if frag in str(paper_key) and (samp is None or samp == str(sample)):
            return v, frag
    return None, None


def main():
    mode = ("--apply" if "--apply" in sys.argv else "--check")
    mb = pd.read_csv(MASTER_B)
    ma = pd.read_csv(MASTER_A)
    fb = pd.read_csv(FITS_B)
    fa = pd.read_csv(FITS_A)
    prov = pd.read_csv(PROV)

    print("REPRODUCTION BEFORE CHANGE")
    repB = reproduce_B(mb, fb)
    repA = reproduce_A(ma, fa)
    passing = (fb.ok == True) & (fb.physicality == "ok")
    nB = sum(1 for i in fb[passing].index if repB.get(i))
    nA = sum(repA.values())
    print(f"  beta_H recovered for {nB} of {int(passing.sum())} passing "
          f"field-axis fits, {sum(1 for v in repB.values() if v)} of {len(fb)} "
          f"overall")
    print(f"  beta_T recovered for {nA} of {len(fa)} temperature-axis fits")
    if nB < 85 or nA < 250:
        print("  THE FIT RULES ARE NOT REPRODUCED. Nothing is written.")
        return 1
    print()

    led = []
    fired = set()

    # ---------------------------------------------------------- temperature
    fa2 = fa.copy()
    fa2["Tc_repaired"] = fa2.Tc_K
    fa2["repair"] = ""
    for pk, tc_new in TC_A.items():
        m = fa2.paper_key == pk
        if not m.any():
            continue
        old = fa2.loc[m, "Tc_K"].iloc[0]
        fired.add(("TC_A", pk, ""))
        fa2.loc[m, "Tc_repaired"] = tc_new
        fa2.loc[m, "repair"] = f"Tc {old} -> {tc_new}, paper-reported"
        led.append(dict(table="phase_3_p44", paper=pk, quantity="Tc_K",
                        old=old, new=tc_new, action="corrected",
                        reason="the value the paper prints for this sample",
                        source="analysis/tc_anchor_audit.py TC_READ"))
    for pk, why in TC_A_UNSTATED.items():
        m = fa2.paper_key == pk
        if m.any():
            fa2.loc[m, "repair"] = "Tc unchanged, provenance corrected"
            led.append(dict(table="phase_3_p44", paper=pk, quantity="Tc_K",
                            old=fa2.loc[m, "Tc_K"].iloc[0], new="",
                            action="provenance corrected", reason=why,
                            source="analysis/tc_anchor_audit.py"))

    # refit beta_T under the repaired Tc, and re-cut the window against it
    rows = []
    for i, r in fa2.iterrows():
        tc = r.Tc_repaired
        g = ma[(ma.pdf_name == r.paper_key)
               & (np.isclose(ma.field_T, r.field_T))]
        g = g[(g.temperature_K >= r.T_min - 1e-9)
              & (g.temperature_K <= TEMP_CLAUSE * tc + 1e-9)]
        # the docstring's promise, now enforced on this axis too: a fit whose
        # deposited rule was not recovered is not silently recomputed
        if not repA.get(i):
            b, n, lev = np.nan, 0, 0.0
            g = g.iloc[0:0]
        else:
            b, n, lev = beta(g.temperature_K, g.Jc, tc)
        rows.append(dict(beta_T_repaired=b, n_T_pts_repaired=n, lever_T=lev,
                         window_cut=bool(r.T_max > TEMP_CLAUSE * tc + 1e-9),
                         T_max_repaired=(g.temperature_K.max() if len(g)
                                         else np.nan),
                         reproduced=bool(repA.get(i)),
                         survives=bool(n >= MIN_PTS)))
    fa2 = pd.concat([fa2, pd.DataFrame(rows, index=fa2.index)], axis=1)

    print("TEMPERATURE AXIS")
    nfire = len([1 for k in TC_A if ("TC_A", k, "") in fired])
    print(f"  Tc corrections that fired: {nfire} of the {len(TC_A)} in the "
          f"table, over {fa.paper_key.nunique()} papers, and one more "
          f"relabelled as not paper-reported")
    if nfire != len(TC_A):
        print("  A CORRECTION KEY MATCHED NOTHING. Check the table against "
              "the fits file.")
    print(f"  fits whose window the repaired Tc actually cuts: "
          f"{int(fa2.window_cut.sum())} of {len(fa2)}")
    print(f"  fits surviving the cut with at least {MIN_PTS} points: "
          f"{int(fa2.survives.sum())} of {len(fa2)}")
    had = fa2.paper_key.isin(set(ma.pdf_name))
    lost = fa2[~fa2.survives & had & fa2.reproduced]
    print(f"  lost to the cut, too few points below {TEMP_CLAUSE} Tc: "
          f"{len(lost)}")
    if len(lost):
        print(lost.groupby("paper_key").size().to_string())
    print(f"  not scored for other reasons: "
          f"{int((~had).sum())} fits whose paper has no rows in this "
          f"extraction at all, and {int((had & ~fa2.reproduced).sum())} whose "
          f"deposited rule was not recovered. Neither is a cost of the repair.")
    gained = fa2[fa2.reproduced & (fa2.n_T_pts_repaired > fa2.n_T_pts)]
    print(f"  and the repair ADDS points to {len(gained)} fits, where the "
          f"corrected Tc is higher and the window opens:")
    if len(gained):
        print(gained.groupby("paper_key").size().to_string())
    sur = fa2[fa2.survives & fa2.reproduced]
    d = (sur.beta_T_repaired - sur.beta_T).abs()
    print(f"  beta_T moves by a median of {d.median():.3f} and up to "
          f"{d.max():.3f} on the {len(sur)} surviving reproduced fits")
    print()

    # ---------------------------------------------------------------- field
    fb2 = fb.copy()
    fb2["Tc_repaired"] = fb2.Tc_K_anchor
    fb2["Hc2_repaired"] = fb2.Hc2_T_used
    fb2["withdrawn"] = ""
    fb2["repair"] = ""
    for i, r in fb2.iterrows():
        tc_new, frag = tc_for(r.paper_key, r.sample_identifier)
        if tc_new is not None and abs(tc_new - r.Tc_K_anchor) > 1e-9:
            fb2.at[i, "Tc_repaired"] = tc_new
            fired.add(("TC_B", frag, str(r.sample_identifier)))
            led.append(dict(table="cohortB", paper=r.paper_key,
                            sample=r.sample_identifier,
                            quantity=f"Tc_K_anchor [{r.sample_identifier}]",
                            old=r.Tc_K_anchor, new=tc_new, action="corrected",
                            reason="the value the paper prints for this sample",
                            source="analysis/cohortB_tc_anchor_check.py"))
        for (frag2, samp), (val, why) in HC2_B.items():
            if frag2 in str(r.paper_key) and samp == str(r.sample_identifier):
                fb2.at[i, "Hc2_repaired"] = val
                fired.add(("HC2_B", frag2, samp))
                led.append(dict(table="cohortB", paper=r.paper_key,
                                sample=r.sample_identifier,
                                quantity="Hc2_T_used", old=r.Hc2_T_used,
                                new=val, action="corrected", reason=why,
                                source="the paper's own table or body text"))
        for frag2, why in WITHDRAW_B.items():
            if frag2 in str(r.paper_key):
                fb2.at[i, "withdrawn"] = frag2
                fired.add(("WITHDRAW_B", frag2, ""))
                led.append(dict(table="cohortB", paper=r.paper_key,
                                quantity="fit", old="in cohort",
                                new="withdrawn", action="withdrawn",
                                reason=why,
                                source="analysis/hc2_anchor_provenance_repair.py"))
        for frag2, (old_t, new_t, why) in RETERM_B.items():
            if frag2 in str(r.paper_key):
                fb2.at[i, "repair"] = f"term {old_t} -> {new_t}"
                fired.add(("RETERM_B", frag2, ""))
                led.append(dict(table="cohortB", paper=r.paper_key,
                                quantity="Hc2 term", old=old_t, new=new_t,
                                action="downgraded", reason=why,
                                source="analysis/hc2_anchor_provenance_repair.py"))

    # recompute the clause and refit beta_H where the anchor moved
    rows = []
    for i, r in fb2.iterrows():
        hc2 = r.Hc2_repaired
        hit = repB.get(i)
        rec = dict(reproduced=bool(hit))
        g = None
        if hit:
            name, fac = hit
            key = (r.arxiv_id if r.arxiv_id in set(mb.arxiv_id)
                   else r.paper_key)
            for nm, gg in slice_for(mb, "arxiv_id", key,
                                    "temperature_K", r.fixed_axis_value,
                                    ("doping_or_composition", "sample_form",
                                     "figure_id", "notes")):
                if nm == name:
                    # the DEPOSITED retained set, not a set re-cut with the new
                    # anchor. The clause asks what fraction of Hc2 the
                    # measurement spans; the span belongs to the measurement and
                    # only the denominator is being repaired. Re-cutting with a
                    # larger anchor admits points the deposited fit never had
                    # and inflates the span, which rescued six fits the audit
                    # had already shown fail.
                    g = gg[gg.field_T < fac * r.Hc2_T_used]
                    break
        if g is not None and len(g):
            H = g.field_T.to_numpy(float)
            rec["range_repaired"] = ((H.max() - H.min()) / hc2
                                     if len(H) >= 2 else np.nan)
            b, n, lev = beta(H, g.Jc_A_per_cm2, hc2)
            rec["beta_repaired"], rec["n_pts_repaired"] = b, n
            rec["lever_H"] = lev
        else:
            rec["range_repaired"] = np.nan
            rec["beta_repaired"] = np.nan
            rec["n_pts_repaired"] = 0
            rec["lever_H"] = 0.0
        rows.append(rec)
    fb2 = pd.concat([fb2, pd.DataFrame(rows, index=fb2.index)], axis=1)
    fb2["clears_field_clause"] = fb2.range_repaired > FIELD_CLAUSE
    fb2["passing_repaired"] = (fb2.clears_field_clause
                               & (fb2.withdrawn == "")
                               & (fb2.n_pts_repaired >= MIN_PTS)
                               & (fb2.lever_H >= MIN_LEVER_DEX))

    same = fb2[fb2.reproduced
               & (fb2.Hc2_repaired - fb2.Hc2_T_used).abs().lt(1e-12)]
    dR = (same.range_repaired - same.H_axis_range_normalized).abs().max()
    dB = (same.beta_repaired - same.beta).abs().max()
    dN = (same.n_pts_repaired - same.n_pts).abs().max()
    print("NO-OP INVARIANT")
    print(f"  {len(same)} reproduced fits whose anchor did not move must come "
          f"back unchanged: max |d range| {dR:.1e}, max |d beta| {dB:.1e}, "
          f"max |d n| {dN}")
    print(f"  the tolerance is the one the reproduction gate above already "
          f"accepted, 1e-3 on beta; the six fits that carry the residue are "
          f"1002.0208v2, whose deposited values agree with this extraction to "
          f"about 3e-4 rather than exactly")
    if not (dR < 1e-4 and dB < 1e-3 and dN == 0):
        print("  THE REFIT IS NOT A NO-OP WHERE IT SHOULD BE. Nothing is "
              "written.")
        return 1
    print()

    print("FIELD AXIS")
    was = int(passing.sum())
    print(f"  passing before: {was} fits over "
          f"{fb[passing].paper_key.nunique()} papers")
    for frag, why in WITHDRAW_B.items():
        n = int(((fb2.withdrawn == frag) & passing).sum())
        print(f"    withdrawn, {frag:24s} {n} fits")
    now = fb2[fb2.passing_repaired & fb2.reproduced]
    print(f"  passing after: {len(now)} fits over {now.paper_key.nunique()} "
          f"papers")
    print(f"  (fits whose rule is not reproduced are excluded rather than "
          f"recomputed: {int((~fb2.reproduced & passing).sum())} of the "
          f"original {was})")
    short = fb2[passing & fb2.reproduced & (fb2.lever_H < MIN_LEVER_DEX)]
    print(f"  and {len(short)} of the originally passing fits are refused for "
          f"a lever below {MIN_LEVER_DEX} dex, where the exponent is not "
          f"identified by the data")
    if len(short):
        print(short.groupby("paper_key").size().to_string())
    moved = fb2[passing & fb2.reproduced & fb2.beta_repaired.notna()
                & (fb2.lever_H >= MIN_LEVER_DEX)]
    dd = (moved.beta_repaired - moved.beta).abs()
    print(f"  beta_H moves by a median of {dd.median():.3f} on the "
          f"{len(moved)} reproduced fits, up to {dd.max():.3f}")
    imp = now[(now.beta_repaired < BETA_PLAUSIBLE[0])
              | (now.beta_repaired > BETA_PLAUSIBLE[1])]
    print(f"  {len(imp)} of the {len(now)} survivors carry a repaired beta_H "
          f"outside {BETA_PLAUSIBLE}, which is flagged and not gated here:")
    if len(imp):
        print(imp.groupby("paper_key").agg(
            n=("beta", "size"), was=("beta", "median"),
            now=("beta_repaired", "median")).round(2).to_string())
        print("    none of these is phpro.2015.06.160: with its own "
              "per-sample Hc2(0) of 26 T (Ni-doped) and 31 T (K-doped) its "
              "normalised range falls to 0.269 and 0.226 and all six fits "
              "fail the field clause, which is what "
              "audit/anchor_provenance_repaired_20260905.md predicted. Their "
              "exponents under the corrected anchor would have been 13.6 to "
              "19.8, which no critical-current field exponent is, and that is "
              "a second reason not to keep them: an Hc2(0) held at every "
              "temperature OVERSTATES Hc2 wherever T > 0, and the paper's own "
              "text says the reduced field for these curves should be built "
              "on the irreversibility field rather than on Hc2.")
    trh = now.fixed_axis_value / now.Tc_repaired
    print(f"  and if the temperature clause were applied to this cohort, "
          f"{int((trh > TEMP_CLAUSE).sum())} of the {len(now)} survivors "
          f"would also fall")
    print()

    ledger = pd.DataFrame(led)
    # one row per change, not one per fit row it touched
    ledger["fits_touched"] = 1
    keys = [c for c in ("table", "paper", "sample", "quantity", "old", "new",
                        "action", "reason", "source") if c in ledger.columns]
    ledger = (ledger.groupby(keys, dropna=False, as_index=False)
              .fits_touched.sum())
    print(f"{len(ledger)} distinct repairs, touching "
          f"{int(ledger.fits_touched.sum())} fit rows, by action")
    print(ledger.action.value_counts().to_string())
    for frag, note in MISTRANSCRIBED.items():
        print(f"  recorded against {frag}: {note}")
    for frag, note in TC_B_NOTE.items():
        print(f"  recorded against {frag}: {note}")
    print()

    if mode == "--check":
        print("--check: nothing written. Re-run with --apply to write.")
        return 0

    # never overwrite an existing snapshot: a second --apply after anything
    # else has touched these tables would replace the pre-repair copy with a
    # post-repair one and the original would be gone
    first = not os.path.isdir(SNAP)
    os.makedirs(SNAP, exist_ok=True)
    for f in (FITS_A, FITS_B, PROV):
        dst = os.path.join(SNAP, os.path.basename(f))
        if os.path.exists(dst):
            continue
        shutil.copy2(f, dst)
    ledger.to_csv(LEDGER, index=False)
    fa2.to_csv(FITS_A.replace(".csv", "_repaired.csv"), index=False)
    fb2.to_csv(FITS_B.replace(".csv", "_repaired.csv"), index=False)
    print(f"snapshot: {SNAP}" + ("" if first else "  (already present, kept)"))
    print(f"ledger:   {LEDGER}")
    print(f"repaired tables written alongside the originals, which are left "
          f"in place so every number in the manuscript can still be traced to "
          f"what produced it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
