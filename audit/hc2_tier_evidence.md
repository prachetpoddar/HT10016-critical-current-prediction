# What the field axis gains from a critical scale read out of the paper

Two questions, answered from the deposited fits rather than from argument. Both
were run read-only; the queries are reproduced so they can be rerun.

## 1. Does the provenance of Hc2 change the field-axis result?

Form 3 fits log Jc against log(1 - H/Hc2), so Hc2 is the denominator that
defines the fitted variable, not a label attached afterwards. Each fit is one
isotherm, so the scale it needs is Hc2(T) or H_irr(T) at that isotherm's
temperature.

From `data/phase_3_form3_fits_partial_cohortB_v2.csv`, grouping on the
`Hc2_source` prefix:

| tier | n | median beta | at the ceiling | median window | passing the 0.3 gate | median SE |
|---|---|---|---|---|---|---|
| Tier 1, read from the paper | 83 | 1.47 | 0 | 0.720 | 76 | 0.12 |
| Tier 2, per-substructure ratio | 9 | 2.22 | 0 | 0.267 | 4 | 0.32 |
| Tier 3, literature default | 83 | 24.20 | 34 | 0.080 | 8 | 3.05 |

75 of the 83 Tier-3 fits fail the pre-registered applicability gate, so the
field-axis result is carried by the Tier-1 papers.

The mechanism is in the Hc2 column itself. Tier 1 tracks temperature: the MgB2
paper uses 11.9 T at 10 K, 4.0 at 15 K, 3.0 at 20 K, 2.5 at 25 K, 2.0 at 30 K.
Tier 3 uses one constant on every isotherm, and that constant is Hc2(0). The
YBaCuO fit is at 77 K and divides by 130 T; the irreversibility field of YBCO at
77 K is single-digit tesla. The fit absorbs a denominator wrong by more than an
order of magnitude by driving the exponent to the ceiling.

### The controlled comparison

`data/reextraction/physc_2011_02_004_field_axis_refit.csv` holds the only
within-paper test: same Jc points, only the critical scale changed, from the
flat 120 T default to H_irr(T) read off arXiv 1002.0208 FIG. 7.

| T (K) | Hc2 used | window | beta | SE |
|---|---|---|---|---|
| 7 | 120 -> 23.9 | 0.122 -> 0.610 | 7.24 -> 0.98 | 1.71 -> 0.26 |
| 10 | 120 -> 20.8 | 0.119 -> 0.684 | 3.49 -> 0.35 | 1.52 -> 0.19 |
| 15 | 120 -> 16.0 | 0.117 -> 0.876 | 2.99 -> 0.22 | 1.25 -> 0.09 |
| 20 | 120 -> 11.7 | 0.117 -> 0.958 | 5.22 -> 0.09 | 1.02 -> 0.05 |
| 25 | 120 -> 8.0 | 0.116 -> 0.947 | 10.82 -> 0.00 | 1.17 -> 0.07 |
| 30 | 120 -> 4.9 | 0.066 -> 0.958 | 29.74 -> 0.28 | 2.19 -> 0.08 |

All six cross the gate, none pin at the ceiling, and `log_Jc_partial` barely
moves (5.86 to 5.84 at 7 K), so the anchor layer and the variance decomposition
are undisturbed.

### Three things this evidence does not establish

The cross-tier table is confounded. Tier-1 fits carry a median of 4 points
against Tier-3's 7, so their better residual (median rms 0.039 against 0.102) is
partly degrees of freedom. The within-paper refit is the only clean evidence and
it is one paper.

**That refit did not record its rms.** Its betas land between 0.00 and 0.98, and
a beta of 0.09 across a window of 0.96 produces about 0.13 dex of variation,
which is far less than the fall in the data. Until the refit residual is
reported next to the Tier-3 residual this is a better-conditioned fit, not
demonstrably a better one.

Reading the real Hc2(T) also deletes points: the higher isotherms lost 6 to 17
each, because they sat above the true irreversibility field. And some fits
cannot be rescued at any Hc2, because the achievable window is bounded by
1 - Hmin/Hmax and that bound is a property of what the paper measured.

A fourth risk, for the manuscript rather than the fits: if the Tier-3 exponents
collapse toward 0 to 1, the between-family spread in beta_H shrinks with them,
and the conditioning claim depends on that spread. This should be run on the one
refit already in hand before twelve more are attempted.

## 2. Do those papers actually contain a critical scale to read?

This is the question that decides whether any of the above is actionable, and
the answer is discouraging. Sweeping the figure captions of all 13 Tier-3 papers
for an Hc2(T), Hirr(T), phase-diagram or irreversibility-line caption:

| paper | what was found |
|---|---|
| 10.1016/j.cjph.2024.09.042 | Fig. 10 vortex phase diagram, Hirr(T) = Hirr(0)(1-T/Tc)^alpha stated |
| 10.1038/s41598-025-95932-9 | Bc2(0) parallel and perpendicular given in a table, no Hc2(T) figure |
| 10.1016/j.physc.2011.02.004 | nothing in the archived PDF, which is the first page only; the scale used in the refit came from its arXiv twin 1002.0208 |
| the other 10 | no caption naming any critical scale |

One paper of thirteen has the figure. That either means the figures are absent,
or means the caption route cannot see them. Today's precision work on the
archive screen says the second is likely: captions systematically omit what
lives in the legend, so an Hirr(T) curve plotted as an inset, as a second series
inside a Jc figure, or on an unlabelled panel of a phase diagram is invisible to
a caption sweep. Two of the 13 archived PDFs are also truncated to the first
page, so "none found" there is an archive defect and not a finding.

Nothing here can be settled without opening the figure pages of those 13 papers.
If the graphs really are absent, the Tier-3 fits cannot be repaired by
re-extraction and the honest move is to withdraw them rather than re-measure
them.

## Queries

    python3 - <<'PY'
    import csv, statistics as st, collections
    rows = list(csv.DictReader(open("data/phase_3_form3_fits_partial_cohortB_v2.csv")))
    f = lambda v: float(v) if v.strip() else None
    tier = lambda r: "_".join(r["Hc2_source"].split("_")[:2])
    g = collections.defaultdict(list)
    for r in rows:
        g[tier(r)].append(r)
    for t in ("Tier_1", "Tier_2", "Tier_3"):
        b = [f(r["beta"]) for r in g[t] if f(r["beta"]) is not None]
        w = [f(r["H_axis_range_normalized"]) for r in g[t]
             if f(r["H_axis_range_normalized"]) is not None]
        ok = sum(1 for r in g[t] if r["ok"] == "True" and r["physicality"] == "ok")
        print(t, len(g[t]), round(st.median(b), 2),
              sum(1 for x in b if x >= 29.99), round(st.median(w), 3), ok)
    PY
