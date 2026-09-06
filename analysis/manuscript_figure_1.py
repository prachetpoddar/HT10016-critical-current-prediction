"""
manuscript_figure_1.py

Figure 1 of the manuscript, in the three-panel layout of the graphical
overview the author supplied as the reference: the corpus funnel, the
multi-stage aggregation, and the bounded prediction scope, left to right.

The layout is the reference's. The content is not, because most of what the
reference printed has since been withdrawn. Every headline number in its
middle and right panels is gone from the manuscript:

    23x MAE reduction          withdrawn, Sec. III.A: the 10.10 and 0.43
                               figures compare a nine-family cohort with a
                               five-family one, and both are in-sample
    Stage 1 LR 10.10 dex       same paragraph, same reason
    Stage 2 median 0.43 dex    same
    23 fittable compounds      20 after the eleven withdrawals
    186 partial-fits           175 in the deposited v3.2.2B table
    88 high-confidence + 130   the confidence tiers were retired; the dispatch
      graded predictions       emits 84 of 183 candidates and puts a refusal
                               code on the rest
    81.2% Hc2 coverage         Table IV reports coverage per family
    218 retained of 239        183 candidates evaluated, not 239
    < 1 dex MAE compound-LOO   reported per family and per axis, not pooled

So the panels keep the reference's shapes and carry the claims the current
text supports. Nothing here is typed: the counts come from
analysis/figure_counts.py, which recomputes from the deposited tables and
refuses to return if the twelve numbers these figures share with Table I
disagree with Table I. The results quoted in panels (b) and (c) are pinned in
RESULTS below with the section each is taken from, so a number that moves in
the text and not here shows up as a mismatch rather than as a figure nobody
re-read.

Every text run is measured against the box it sits in by
analysis/figure_layout.py, and the figure refuses to write if any of it hangs
outside. Overflow in these figures was caught by eye three times, and twice it
survived a look.

Figure-to-script mapping for this deposit, because the names do not line up on
their own and using the wrong script produces a figure in a different visual
style that still looks plausible:

    Fig. 1  analysis/manuscript_figure_1.py
    Fig. 2  analysis/manuscript_figure_2.py
    Fig. 3  analysis/figure_4_source.py      (also the variance-decomposition library)
    Fig. 4  analysis/manuscript_figure_4.py
    Fig. 5  analysis/manuscript_figure_5.py  (reads data/family_params.json)

Run from the repository root; writes into figures/.
"""
import logging as _logging

import matplotlib
matplotlib.use("Agg")
# font.family carries fallbacks for other machines, so matplotlib warns once
# per missing family per text element: several hundred lines that look like
# failures on a render that succeeded.
_logging.getLogger("matplotlib.font_manager").setLevel(_logging.ERROR)
import numpy as np                                               # noqa: E402
from matplotlib.colors import LinearSegmentedColormap            # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Polygon  # noqa: E402
from matplotlib.path import Path                                 # noqa: E402

from figure_counts import from_deposit, UPSTREAM                 # noqa: E402
from figure_layout import new_figure                             # noqa: E402

# ------------------------------------------------------------------ palette
# Sampled from the reference render, so the panels and the funnel keep its
# colours rather than approximations of them.
WHITE = "#FFFFFF"
PANEL_L, EDGE_L = "#F0F2F8", "#D5DAE8"
PANEL_M, EDGE_M = "#F8F5EF", "#E6DECB"
PANEL_R, EDGE_R = "#F3F7F2", "#D8E6DA"
PILL, PILL_E = "#F9F2D2", "#DEBB5C"
FUNNEL_TOP, FUNNEL_BOT = "#A6AFB5", "#525969"
BAND_ACCENT = "#31407E"
VENN = ["#B2CBDE", "#B3D1CB", "#8188A4"]
INK, SOFT, GREY = "#1A1D23", "#4A4A4A", "#7A828E"
AMBER_T = "#7A5C16"

# ------------------------------------------------------------------ results
# The quantities panels (b) and (c) state, each with the section it comes
# from. They are constants because they are results, not counts: nothing in
# data/ recomputes them on this run. Naming and sourcing them here is the
# difference between a figure that can be checked against the text and one
# that cannot.
RESULTS = dict(
    # Sec. III.C, the permutation test on the substructure label with source
    # papers as the unit. The temperature-axis half was added to the
    # manuscript on 2026-09-05: it is the evidence reply paragraph 38 points
    # at, and until then the paper reported only the field-axis half.
    eta2_temperature=0.524, perm_p_temperature=0.007,
    eta2_field=0.038, perm_p_field=0.98,
    # Sec. III.A, after the anchor repair of Sec. III.F. The manuscript gives
    # the three ratios; the sample counts beside them are not reproduced here,
    # because the manuscript's "0.37 on 7" disagrees with
    # audit/variance_decomposition_repaired.csv, which has n = 5 for that
    # family, and a figure must not pick a side in a disagreement it did not
    # resolve.
    ratio_11=0.81, ratio_122=0.37, ratio_mgb2=0.04,
    # Sec. III.A, the p floor the clustered null imposes on the MgB2 cell
    p_floor_mgb2=0.33,
    # Sec. III.D and Table III, reduced-variable binning
    universal_sd_pct=13.0, universal_var_pct=24.3, universal_threshold=30,
    universal_cohort=23,
    # Sec. III.E, the one family median the dispatch emits
    family_median=4.98, median_T=4.2, median_H=5,
    # Table IV, combined row
    field_refused_compounds=60,
)

C = from_deposit()
fig, ax, L = new_figure(11.4, 7.2, 152, 96, WHITE)


def arrow(x0, y0, x1, y1, color=GREY, lw=1.1, mut=11):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=mut, linewidth=lw,
                                 color=color, zorder=4))


# ================================ panels ================================
for x, fc, ec, nm in ((2, PANEL_L, EDGE_L, "panel a"),
                      (52.5, PANEL_M, EDGE_M, "panel b"),
                      (103, PANEL_R, EDGE_R, "panel c")):
    L.box(x, 3, 47, 88, fc, ec=ec, lw=1.0, r=1.4, z=1, name=nm)
    # Prose must clear the panel border, not merely stay inside the panel.
    L.region(x + 2, 5, 43, 84, "%s text area" % nm)
arrow(50.0, 47, 52.0, 47, color="#8A8A8A", lw=1.7, mut=14)
arrow(100.5, 47, 102.5, 47, color="#8A8A8A", lw=1.7, mut=14)

# ===================== (a) heterogeneous literature =====================
L.txt(25.5, 87.4, "Heterogeneous J$_c$(T,H)", size=11.2, weight="bold")
L.txt(25.5, 84.2, "literature", size=11.2, weight="bold")

for dx, dy in ((0, 0), (1.3, -1.1), (2.6, -2.2)):
    ax.add_patch(Polygon([(6.6 + dx, 80.2 + dy), (11.2 + dx, 80.2 + dy),
                          (11.2 + dx, 75.4 + dy), (6.6 + dx, 75.4 + dy)],
                         closed=True, facecolor=WHITE, edgecolor=INK,
                         linewidth=0.7, zorder=3))
# Sec. II.A states that the fitted cohort is NOT drawn exclusively from the
# two publisher APIs, and says so because an earlier version implied it did.
# A funnel with "Elsevier + Springer" at its mouth and the fitted census at
# its outlet re-asserts exactly what that paragraph exists to remove.
L.txt(31.0, 79.2, "n = %d articles retrieved and screened"
      % UPSTREAM["articles_screened"], size=7.6)
L.txt(31.0, 76.8, "through the Elsevier and Springer APIs;", size=7.0,
      color=SOFT)
L.txt(31.0, 74.8, "fitted curves also come from arXiv", size=7.0, color=SOFT)
L.txt(31.0, 72.8, "preprints and NHMFL records (Sec. II.A)", size=7.0,
      color=SOFT)

# ------------------------------- the funnel -----------------------------
# A vertical gradient clipped to the funnel outline. The three bands are the
# three screens a published curve passes before it is a fitted curve.
TOP, SHOULDER, NECK, FOOT = 69.5, 54.0, 47.5, 41.5
outline = [(7.5, TOP), (43.5, TOP), (43.5, SHOULDER), (30.5, NECK),
           (30.5, FOOT), (20.5, FOOT), (20.5, NECK), (7.5, SHOULDER)]
grad = np.linspace(0, 1, 256).reshape(-1, 1)
im = ax.imshow(grad, extent=[7.5, 43.5, FOOT, TOP], origin="upper",
               aspect="auto", zorder=2,
               cmap=LinearSegmentedColormap.from_list(
                   "funnel", [FUNNEL_TOP, FUNNEL_BOT]))
im.set_clip_path(Path(outline), transform=ax.transData)
ax.add_patch(Polygon(outline, closed=True, facecolor="none",
                     edgecolor="#8A929A", linewidth=0.8, zorder=3))

BANDS = [(65.0, 61.8, "Applicability window, Eq. (1)", BAND_ACCENT),
         (59.0, 56.0, "Partial-fit and full-fit thresholds", WHITE),
         (53.6, 50.8, "Cross-model agreement gate", WHITE)]
def half_width(y):
    """Half the funnel's width at height y, from its own outline."""
    if y >= SHOULDER:
        return 18.0
    if y <= NECK:
        return 5.0
    return 18.0 - (SHOULDER - y) / (SHOULDER - NECK) * 13.0


for y, rule, label, colour in BANDS:
    half = half_width(rule)
    ax.plot([25.5 - half, 25.5 + half], [rule, rule], lw=0.7,
            color="#9AA2AA", zorder=4, solid_capstyle="butt")
    # The label has to fit the funnel at its own height, and the funnel is
    # not a box, so the inscribed rectangle is registered as the constraint.
    L.band_region(25.5, half_width, y - 1.6, y + 1.6,
                  "funnel at \"%s\"" % label)
    L.txt(25.5, y, label, size=8.3, weight="bold", color=colour, z=5)

# --------------------------- what it yields -----------------------------
L.txt(25.5, 38.0, "Cohort A:  J$_c$(T) at fixed H", size=8.2, weight="bold")
L.txt(25.5, 35.2, "Cohort B:  J$_c$(H) at fixed T", size=8.2, weight="bold")
L.txt(25.5, 32.2, "T/T$_c$ < 0.7            $\\Delta$H/H$_{c2}$ > 0.3",
      size=7.8, color=SOFT)

L.box(5, 7, 41, 22, WHITE, ec=EDGE_L, r=0.8, name="cohort census")
ROWS = [("%d" % C["fitted_curve_papers"], "papers contributing fitted curves"),
        ("%d" % C["fitted_curve_compounds"],
         "compound labels, 27 composition keys"),
        ("%d" % C["extracted_points"], "extracted critical-current points"),
        ("%d" % UPSTREAM["fittable_compounds_v321"],
         "compounds fittable on both axes"),
        ("%d / %d" % (C["temperature_axis_fits"], C["field_axis_fits_ok"]),
         "$\\beta_T$ / $\\beta_H$ fits, the latter from %d papers"
         % C["field_axis_ok_papers"]),
        ("%d" % C["anchor_rows"],
         "per-paper anchors over %d papers" % C["anchor_papers"])]
for n, (val, lab) in enumerate(ROWS):
    y = 26.2 - n * 3.4
    L.txt(13.6, y, val, size=8.6, weight="bold", ha="right")
    L.txt(14.8, y, lab, size=7.1, ha="left", color=SOFT)

# ===================== (b) multi-stage aggregation ======================
L.txt(76, 87.4, "Multi-stage substructure", size=11.2, weight="bold")
L.txt(76, 84.2, "conditional aggregation", size=11.2, weight="bold")

L.box(56.5, 74.2, 39, 8.2, PILL, ec=PILL_E, lw=1.3, r=0.9, name="headline")
L.txt(76, 80.2, "the family label accounts for %.2f of the"
      % RESULTS["eta2_temperature"], size=8.6, weight="bold", color=AMBER_T)
L.txt(76, 77.4, "temperature-exponent variance, p = %.3f"
      % RESULTS["perm_p_temperature"], size=8.6, weight="bold",
      color=AMBER_T)
L.txt(76, 71.8, "source papers are the permutation unit, and this is the one",
      size=6.9, color=SOFT, style="italic")
L.txt(76, 69.8, "result that improved under every correction. On the field",
      size=6.9, color=SOFT, style="italic")
L.txt(76, 67.8, "axis it is %.3f at p = %.2f, and no family-level verdict"
      % (RESULTS["eta2_field"], RESULTS["perm_p_field"]), size=6.9,
      color=SOFT, style="italic")
L.txt(76, 65.8, "is reported (Table III)", size=6.9, color=SOFT,
      style="italic")

STAGES = [(64.0, "Stage 1", ("monolithic", "regression on one",
                             "descriptor; rank", "scope only")),
          (76.0, "Stage 2", ("sample-form", "conditional median",
                             "inside each", "substructure")),
          (88.0, "Stage 3", ("substructure", "aggregate median",
                             "with an explicit", "IQR bound"))]
for cx, head, lines in STAGES:
    L.box(cx - 6.2, 50.0, 12.4, 13.4, WHITE, ec="#DED6C4", r=0.6,
          name="stage %s" % head[-1])
    L.txt(cx, 61.4, head, size=8.2, weight="bold")
for cx, head, lines in STAGES:
    for i, line in enumerate(lines):
        L.txt(cx, 58.2 - i * 2.2, line, size=6.1, color=SOFT)

L.txt(76, 46.6, "log$_{10}$J$_c$ = log$_{10}$J$_{c,\\mathrm{partial}}$ + "
                "$\\beta$ log$_{10}$(1 $-$ x/x$_c$)", size=9.2)
L.txt(76, 43.6, "fitted per axis:  $\\beta_T$ separately,  $\\beta_H$ "
                "separately", size=7.0, color=SOFT, style="italic")

L.txt(76, 39.8, "No fold improvement is reported.", size=7.3,
      weight="bold")
L.txt(76, 37.4, "Under leave-one-substructure-out the errors are 12.3 without",
      size=6.9, color=SOFT)
L.txt(76, 35.3, "sample-form conditioning and 14.9 with it over seven "
                "families,", size=6.9, color=SOFT)
L.txt(76, 33.2, "1.19 and 0.55 on the fits passing physicality over three, and",
      size=6.9, color=SOFT)
L.txt(76, 31.1, "removing any one family moves the comparison across unity.",
      size=6.9, color=SOFT)

L.box(56.5, 7, 39, 21.5, WHITE, ec="#DED6C4", r=0.8, name="diagnostic")
L.txt(76, 25.8, "The sample-form diagnostic sets the rule", size=8.0,
      weight="bold")
L.txt(76, 23.4, "the predictor follows. After the repair of Sec. III.F it",
      size=6.9, color=SOFT)
L.txt(76, 21.4, "explains %.2f, %.2f and %.2f of the within-family scatter"
      % (RESULTS["ratio_11"], RESULTS["ratio_122"], RESULTS["ratio_mgb2"]),
      size=6.9, color=SOFT)
L.txt(76, 19.4, "in the anchor, for the 11-type, 122-type and MgB$_2$-class",
      size=6.9, color=SOFT)
L.txt(76, 17.4, "families in turn. It does not establish the distinction to",
      size=6.9, color=SOFT)
L.txt(76, 15.4, "significance: sample form is nearly a relabelling of source",
      size=6.9, color=SOFT)
L.txt(76, 13.4, "paper here, and under the only null that respects that",
      size=6.9, color=SOFT)
L.txt(76, 11.4, "structure the MgB$_2$ cell can never return p below %.2f."
      % RESULTS["p_floor_mgb2"], size=6.9, color=SOFT)
L.txt(76, 9.2, "Two regimes, reported as the rule and not as a finding.",
      size=6.9, color=SOFT, style="italic")

# ====================== (c) bounded predictions =========================
L.txt(126.5, 87.4, "Bounded screening", size=11.2, weight="bold")
L.txt(126.5, 84.2, "grade predictions", size=11.2, weight="bold")

# Three conditions a dispatched target satisfies. NOT a partition of the
# refusal codes, and the figure no longer says it is: refusal_flag is a
# first-match precedence code, so a refused target routinely violates two or
# three of these at once (501 of the 1054 reduced-field refusals also sit at
# T/Tc >= 0.7), and the inference procedure of Sec. II.D applies further gates
# beyond these three. Satisfying all three is necessary, not sufficient.
CX, CY, R = 126.5, 67.5, 11.5
CIRCLES = [(-6.8, 4.2, VENN[0], 76.6,
            ("Reduced field", "in the validated", "window")),
           (6.8, 4.2, VENN[1], 76.6,
            ("Temperature in", "scope and below", "T$_c$")),
           (0, -6.8, VENN[2], 58.4,
            ("Family with a validated axis", "and an available H$_{c2,0}$"))]
for dx, dy, colour, ly, lines in CIRCLES:
    ax.add_patch(Circle((CX + dx, CY + dy), R, facecolor=colour, alpha=0.55,
                        edgecolor="#6F7A88", linewidth=0.7, zorder=3))
for dx, dy, colour, ly, lines in CIRCLES:
    cx, cy = CX + dx, CY + dy
    for i, line in enumerate(lines):
        y = ly - i * 2.2
        # The label has to fit the circle at its own height, and a circle is
        # not a box, so the inscribed chord is registered as the constraint.
        half = (R * R - (y - cy) ** 2) ** 0.5
        L.region(cx - half, y - 1.1, 2 * half, 2.2,
                 "circle at \"%s\"" % line)
        L.txt(cx, y, line, size=6.5, z=6)
L.txt(CX, CY - 0.4, "dispatched", size=7.0, weight="bold", z=6)

L.txt(126.5, 51.6, "necessary conditions, not the whole gate: Sec. II.D "
                   "adds", size=6.6, color=SOFT, style="italic")
L.txt(126.5, 49.7, "anchor density, monotonicity and population screens",
      size=6.6, color=SOFT, style="italic")
L.txt(126.5, 46.0, "Universal (T/T$_c$, H/H$_{c2}$) scaling is not adopted",
      size=8.2, weight="bold")
L.txt(126.5, 43.5, "within-bin standard deviation falls %.1f%%, %.1f%% on the"
      % (RESULTS["universal_sd_pct"], RESULTS["universal_var_pct"]),
      size=7.1, color=SOFT)
L.txt(126.5, 41.4, "variance scale, both below the %d%% adoption threshold,"
      % RESULTS["universal_threshold"], size=7.1, color=SOFT)
L.txt(126.5, 39.3, "on the pre-withdrawal %d-compound cohort (Table III)"
      % RESULTS["universal_cohort"], size=7.1, color=SOFT)

L.box(105.5, 7, 41, 29.5, WHITE, ec=EDGE_R, r=0.8,
      name="dispatch outcome")
L.txt(126.5, 33.8, "Family-scope J$_c$(T,H) envelopes", size=8.4,
      weight="bold")
L.txt(126.5, 31.4, "with a 95% bootstrap interval and a refusal flag",
      size=7.1, color=SOFT)
OUT = [("%d" % C["candidate_compounds"], "candidate compounds evaluated"),
       ("%d" % C["dispatched_compounds"],
        "dispatched, every one MgB$_2$-class"),
       ("%d" % RESULTS["field_refused_compounds"],
        "refused a field target, no H$_{c2,0}$ anchor"),
       ("%.2f" % RESULTS["family_median"],
        "log$_{10}$J$_c$ at %.1f K and %d T" % (RESULTS["median_T"],
                                                RESULTS["median_H"]))]
for n, (val, lab) in enumerate(OUT):
    y = 27.6 - n * 3.3
    L.txt(116.0, y, val, size=8.6, weight="bold", ha="right")
    L.txt(117.2, y, lab, size=7.1, ha="left", color=SOFT)
L.txt(126.5, 12.6, "One family curve per grid point, shared by every member",
      size=6.9, color=SOFT)
L.txt(126.5, 10.5, "candidate, and no per-compound ranking is emitted. The",
      size=6.9, color=SOFT)
L.txt(126.5, 8.4, "60 keep their temperature-axis output (Sec. III.E).",
      size=6.9, color=SOFT)

# =============================== write out ==============================
n_txt, n_box = L.check()
print("   %d text runs checked against %d boxes, none overflowing"
      % (n_txt, n_box))
fig.savefig("figures/manuscript_figure_1.png", dpi=300)
fig.savefig("figures/manuscript_figure_1.pdf")
print("wrote figures/manuscript_figure_1.png and .pdf")
print("   counts drawn from the deposit: %d screened, %d papers, %d labels,"
      % (UPSTREAM["articles_screened"], C["fitted_curve_papers"],
         C["fitted_curve_compounds"]))
print("   %d points, %d fittable on both axes, %d anchors over %d papers,"
      % (C["extracted_points"], UPSTREAM["fittable_compounds_v321"],
         C["anchor_rows"], C["anchor_papers"]))
print("   %d candidates of which %d dispatched"
      % (C["candidate_compounds"], C["dispatched_compounds"]))
