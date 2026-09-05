"""
manuscript_figure_1.py

Figure 1 of the manuscript, redrawn in the visual language of the v22
manuscript so that it sits beside Figure 2 rather than beside nothing: the
cream canvas, the green section headers, the rounded pastel panels and the
DejaVu Sans face are the same as analysis/manuscript_figure_2.py, and the
two scripts share the palette constants by definition rather than by memory.

Panel (a) is the corpus-to-cohort funnel. Panel (b) is candidate dispatch by
family.

Figure-to-script mapping for this deposit, because the names do not line up on
their own and using the wrong script produces a figure in a different visual
style that still looks plausible:

    Fig. 1  analysis/manuscript_figure_1.py
    Fig. 2  analysis/manuscript_figure_2.py
    Fig. 3  analysis/figure_4_source.py      (also the variance-decomposition library)
    Fig. 4  analysis/manuscript_figure_4.py
    Fig. 5  analysis/manuscript_figure_5.py  (reads data/family_params.json)

Nothing this figure prints is typed here. Every count comes from
analysis/figure_counts.py, which recomputes from the deposited tables and
refuses to return if the six numbers Figure 1 shares with Table I disagree
with Table I. That assertion exists because these numbers drifted three
times, the last time silently: analysis/check_documents.py reads
word/document.xml and can never see inside an embedded image.

Run from the repository root; writes into figures/.
"""
import matplotlib
matplotlib.use("Agg")
import logging as _logging
# font.family carries fallbacks for other machines, so matplotlib warns once
# per missing family per text element: several hundred lines that look like
# failures on a render that succeeded.
_logging.getLogger("matplotlib.font_manager").setLevel(_logging.ERROR)
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from figure_counts import from_deposit, UPSTREAM

# The v22 palette, the same constants Figure 2 draws in.
CANVAS = "#FBFBDA"
GREEN = "#599E2A"
PINK = "#F9E7EF"
BLUE = "#D6E7ED"
BLUE_E = "#BBD2DC"
TEAL = "#8ABDA8"
SALMON = "#CD8A83"
SALMON_E = "#A66A66"
PEACH = "#F7EBCF"
LAV2 = "#E7D7E3"
AMBER = "#F7D77C"
AMBER_E = "#DEBB5C"
CREAM = "#F9F4DF"
INK = "#1A1A1A"
GREY = "#5A5A5A"
DASH = "#7A4A46"

C = from_deposit()

plt.rcParams.update({"font.family": ["DejaVu Sans"], "font.size": 7.2})
fig = plt.figure(figsize=(11.4, 5.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 152)
ax.set_ylim(0, 72)
ax.axis("off")
ax.add_patch(FancyBboxPatch((0, 0), 152, 72, boxstyle="square,pad=0",
                            facecolor=CANVAS, edgecolor="none", zorder=0))


def box(x, y, w, h, fc, ec="#9A9A9A", lw=0.9, r=0.9, z=2):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0,rounding_size=%.2f" % r,
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z))


def txt(x, y, s, size=7.2, weight="normal", color=INK, ha="center",
        va="center", z=5, style="normal"):
    ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha,
            va=va, zorder=z, style=style, linespacing=1.35)


# ============================== panels ==============================
box(2, 3, 72, 62, "#FDFDF0", ec="#C9C9A8", r=1.2, z=1)
box(78, 3, 72, 62, "#FDFDF0", ec="#C9C9A8", r=1.2, z=1)
txt(38, 68.0, "(a)   From retrieval to fitted evidence", size=11,
    weight="bold", color=GREEN)
txt(114, 68.0, "(b)   Candidate dispatch, by family", size=11,
    weight="bold", color=GREEN)

# ------------------------- (a) the funnel ---------------------------
# Two rows are drawn in the highlight colour: the paper cohort, which is what
# every fitted quantity in the paper rests on, and the both-axes cohort, which
# is what the closed-form comparison rests on. They are the two places the
# corpus narrows for a reason rather than by attrition.
rows = [
    (UPSTREAM["articles_screened"], "articles retrieved and screened",
     "Elsevier and Springer, Cohort A + Cohort B", BLUE, BLUE_E, False),
    (C["fitted_curve_papers"], "papers contributing fitted curves",
     "the cohort every fitted quantity rests on", AMBER, AMBER_E, True),
    # A label count, not a material count: see Sec. II.D and
    # analysis/compound_label_reduction.py, which reduces the 35 to 27.
    (C["fitted_curve_compounds"], "distinct compound labels",
     "27 composition keys under the reduction of Sec. II.D", BLUE, BLUE_E,
     False),
    (C["extracted_points"], "extracted critical-current points",
     "digitised J$_c$(T) and J$_c$(H) readings", BLUE, BLUE_E, False),
    (UPSTREAM["fittable_compounds_v321"], "compounds fittable on both axes",
     "the two-axis gate; the closed-form comparison ran on the "
     "pre-withdrawal 23", AMBER, AMBER_E, True),
    (C["anchor_rows"], "per-paper critical-current anchors",
     "over %d papers; the repair of Sec. III.F withdraws 26 and rescales 15"
     % C["anchor_papers"], BLUE, BLUE_E, False),
]

X0, W, H, TOP, STEP = 5, 66, 7.2, 55.0, 8.6
for n, (val, lab, sub, fc, ec, hi) in enumerate(rows):
    y = TOP - n * STEP
    box(X0, y, W, H, fc, ec=ec, lw=1.5 if hi else 0.9)
    txt(X0 + 6.5, y + H / 2, "{:,}".format(val), size=13.5, weight="bold",
        ha="center")
    txt(X0 + 14, y + H * 0.62, lab, size=8.6, weight="bold", ha="left")
    txt(X0 + 14, y + H * 0.28, sub, size=7.0, ha="left", color="#4A4A4A",
        style="italic")
    if n < len(rows) - 1:
        ax.add_patch(FancyArrowPatch(
            (X0 + 6.5, y), (X0 + 6.5, y - (STEP - H) + 0.15),
            arrowstyle="-|>", mutation_scale=10, linewidth=1.0, color=GREY,
            zorder=4))

txt(5, 6.4, "The retrieval corpus is the screening scope. Every fitted "
            "quantity rests on a smaller cohort,",
    size=7.4, color="#4A4A4A", ha="left", style="italic")
txt(5, 4.3, "and the two highlighted rows are the cohorts the paper's "
            "claims are made on.",
    size=7.4, color="#4A4A4A", ha="left", style="italic")

# --------------------- (b) dispatch by family -----------------------
# The refusal codes in the short form the bars have room for. The long form
# is in figure_counts.REFUSAL_LABEL and in Figure 2, and the two must say the
# same thing about the same code.
GATE_SHORT = {
    "H_below_validated_reduced_field": "field below window",
    "T_above_validated_reduced_temperature": "temperature above window",
    "T_above_Tc": "target above T$_c$",
    "Hc2_unavailable": "no critical field",
    "family_fails_field_axis_validation": "family field axis not validated",
}
fams = C["families"]
missing = sorted({c for f in fams for c, _ in f["gates"]} - set(GATE_SHORT))
if missing:
    raise SystemExit("no short wording for refusal code(s): %s"
                     % ", ".join(missing))
BX, BW = 82, 56
scale = BW / max(f["total"] for f in fams)
top = 55.0
gap = 13.6
for i, f in enumerate(fams):
    name, total = f["label"], f["total"]
    disp, ref = f["dispatched"], f["refused"]
    y = top - i * gap
    txt(BX, y + 6.0, name, size=9.0, weight="bold", ha="left")
    # A rounded FancyBboxPatch of zero width is not invisible: the rounding
    # turns it into a capsule about 0.8 units across, in the colour the legend
    # defines as dispatched, on the two families that dispatch nothing. An
    # independent review found it in the render.
    if disp:
        box(BX, y, disp * scale, 4.6, TEAL, ec="#5E9C82", lw=0.8, r=0.4, z=3)
    if ref:
        box(BX + disp * scale, y, ref * scale, 4.6, SALMON, ec=SALMON_E,
            lw=0.8, r=0.4, z=3)
    box(BX, y, total * scale, 4.6, "none", ec="#8A8A7A", lw=0.9, r=0.4, z=4)
    txt(BX + total * scale + 1.6, y + 2.3, "%d / %d" % (disp, total),
        size=8.4, ha="left", color="#3A3A3A")
    if disp:
        txt(BX + disp * scale / 2, y + 2.3, str(disp), size=7.6,
            weight="bold", color="#123A2A", z=6)
    # The gates that refused them, which the caption promises. Refusal is per
    # target and a compound routinely hits more than one gate, so these counts
    # overlap and the legend says so.
    if ref:
        parts = ["%s %d" % (GATE_SHORT[c], n) for c, n in f["gates"]]
        txt(BX, y - 2.3, "%d refused:  %s" % (ref, "   ".join(parts)),
            size=6.6, ha="left", color="#7A4A46", style="italic")

box(80, 5.0, 68, 16.5, CREAM, ec="#D8D2B0", r=0.9)
box(82, 16.4, 3.4, 2.6, TEAL, ec="#5E9C82", lw=0.8, r=0.3, z=3)
txt(86.6, 17.7, "dispatched: the family envelope is emitted", size=7.6,
    ha="left", color="#3A3A3A")
box(82, 12.6, 3.4, 2.6, SALMON, ec=SALMON_E, lw=0.8, r=0.3, z=3)
txt(86.6, 13.9, "refused: every target hit a refusal gate", size=7.6,
    ha="left", color="#3A3A3A")
txt(86.6, 11.4, "a refused compound may hit several gates, so the counts "
                "above overlap", size=6.8, ha="left", color="#5A5A5A",
    style="italic")
txt(82, 8.6, "%d of %d candidate compounds receive at least one prediction."
    % (C["dispatched_compounds"], C["candidate_compounds"]),
    size=7.2, ha="left", color="#4A4A4A", style="italic")
txt(82, 6.5, "The refusal reason is recorded for every one of the rest.",
    size=7.2, ha="left", color="#4A4A4A", style="italic")

fig.savefig("figures/manuscript_figure_1.png", dpi=300)
fig.savefig("figures/manuscript_figure_1.pdf")
print("wrote figures/manuscript_figure_1.png and .pdf")
print("   counts drawn from the deposit: %d screened, %d papers, %d compounds,"
      % (UPSTREAM["articles_screened"], C["fitted_curve_papers"],
         C["fitted_curve_compounds"]))
print("   %d points, %d fittable on both axes, %d anchors over %d papers"
      % (C["extracted_points"], UPSTREAM["fittable_compounds_v321"],
         C["anchor_rows"], C["anchor_papers"]))
