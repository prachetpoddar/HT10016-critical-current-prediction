#!/usr/bin/env python3
"""Figure 2, the runtime architecture, in the v22 visual language.

The style is v22's: a pale canvas, coloured subsystem panels, amber inner
boxes, green section headers, cream call-outs on the right, and the source
logos. Every colour below was sampled from the v22 render rather than matched
by eye, and the logos are cropped from it into figures/logos/.

Three things are different from v22, and each is required rather than
preferred.

**The arrows carry labels and the chain closes.** Referee B's fifth item is
about this figure: "There is no connection between Input and Predictor if you
follow the arrows. Could you denote the information below between these steps
visually? Ideally the arrows would include what information is being passed."
In v22 the arrows are unlabelled dashed connectors that skip between panels.
Here every arrow carries what it passes, and following them runs from the
corpus to the emitted envelope without a gap.

**The critical-scale resolution stage is drawn.** The response letter says that
following the referee's arrows showed a stage was missing from the
architecture, not only a line: between extraction and fitting the workflow
resolves the transition temperature and the critical field for each curve, and
v22 does not show it. That stage is where every defect this revision reports
occurs, so it is drawn explicitly, with its provenance tiers, and highlighted.
Adding arrows alone would have left the letter promising a figure that does not
exist.

**The refusal branch leaves the dispatch stage.** So that refusal reads as an
output of the predictor rather than as an omission, which is also what the
letter says.

Numbers. Every count is read from figure_counts.from_deposit(), which pins the
six it shares with Table I and refuses to return if they disagree. The v22
render carries several that this revision has withdrawn, and they are gone:
the 23x MAE reduction with its 10.10 and 0.43 dex, the "<1 dex MAE at 3 of 4
testable substructures", n=773, n=23 fittable, and 239 candidates.

    python analysis/manuscript_figure_2.py

Writes figures/manuscript_figure_2.png and .pdf. Run from the repository root.
"""
import logging as _logging
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402
from matplotlib.offsetbox import OffsetImage, AnnotationBbox    # noqa: E402
import matplotlib.image as mpimg                                # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figure_counts import REFUSAL_LABEL, from_deposit, UPSTREAM
from figure_layout import Layout                # noqa: E402

_logging.getLogger("matplotlib.font_manager").setLevel(_logging.ERROR)

# Sampled from the v22 render, not matched by eye.
CANVAS = "#FBFBDA"
GREEN = "#599E2A"
PINK = "#F9E7EF"
BLUE = "#D6E7ED"
BLUE_E = "#BBD2DC"
TEAL = "#8ABDA8"
SALMON = "#CD8A83"
SALMON_E = "#A66A66"
PEACH = "#F7EBCF"
LAV = "#E7DCDE"
LAV2 = "#E7D7E3"
AMBER = "#F7D77C"
CREAM = "#F9F4DF"
INK = "#1A1A1A"
DASH = "#7A4A46"
# The one colour not in v22: the critical-scale stage it does not draw.
HILITE = "#CFE3F2"
HILITE_E = "#2F5C86"

LOGOS = os.path.join("figures", "logos")
C = from_deposit()

plt.rcParams.update({"font.family": ["DejaVu Sans"], "font.size": 7.2})
fig = plt.figure(figsize=(11.4, 7.9))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 152)
ax.set_ylim(0, 105)
ax.axis("off")
ax.add_patch(FancyBboxPatch((0, 0), 152, 105, boxstyle="square,pad=0",
                            facecolor=CANVAS, edgecolor="none", zorder=0))


L = Layout(fig, ax)


def box(x, y, w, h, fc, ec="#9A9A9A", lw=0.9, r=0.9, z=2, ls="-"):
    L.box(x, y, w, h, fc, ec=ec, lw=lw, r=r, z=z, ls=ls)


def txt(x, y, s, size=7.2, weight="normal", color=INK, ha="center",
        va="center", z=5, style="normal", rot=0):
    L.txt(x, y, s, size=size, weight=weight, color=color, ha=ha, va=va, z=z,
          style=style, rot=rot)


def logo(name, x, y, zoom):
    p = os.path.join(LOGOS, "%s.png" % name)
    if not os.path.exists(p):
        return
    ax.add_artist(AnnotationBbox(OffsetImage(mpimg.imread(p), zoom=zoom),
                                 (x, y), frameon=False, zorder=6))


def arrow(x0, y0, x1, y1, label=None, lx=None, ly=None, dashed=True,
          color=DASH, ha="left", size=6.3):
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=11,
        linewidth=1.15, color=color, zorder=4,
        linestyle=(0, (4, 2.6)) if dashed else "-",
        connectionstyle="arc3,rad=0"))
    if label:
        txt(lx if lx is not None else (x0 + x1) / 2,
            ly if ly is not None else (y0 + y1) / 2, label, size=size,
            color="#4A4A4A", ha=ha, style="italic")


# ============================== headers ==============================
txt(33, 101.5, "Data acquisition  +  Extraction", size=11, weight="bold",
    color=GREEN)
txt(107, 101.5, "Predictor  +  Empirical Validation  +  Output", size=11,
    weight="bold", color=GREEN)

# ============================ left column ============================
box(2, 27, 62, 71, "#FDFDF0", ec="#C9C9A8", r=1.2, z=1)

# INPUT
box(4, 74, 58, 22.5, PINK, ec="#E3C8D6", r=1.0)
txt(33, 94.2, "INPUT", size=10.5, weight="bold")
box(5.5, 84.5, 27, 8.2, BLUE, ec=BLUE_E)
logo("corpus", 9.6, 90.2, 0.30)
txt(21.5, 90.6, "Literature corpus", size=8.2, weight="bold")
txt(19.5, 88.2, "Cohort A + Cohort B", size=7.6)
txt(19.0, 86.0, "%d screened, %d contributing"
    % (UPSTREAM["articles_screened"], C["fitted_curve_papers"]), size=7.4)
box(33.5, 84.5, 27, 8.2, BLUE, ec=BLUE_E)
logo("mp", 37.6, 90.2, 0.30)
txt(49.5, 90.6, "Materials Project", size=8.2, weight="bold")
txt(47.5, 88.2, "Tc + Hc2 + spacegroup", size=7.6)
txt(47.5, 86.0, "2.2M+ structural records", size=7.4)
box(5.5, 75.5, 27, 8.2, BLUE, ec=BLUE_E)
txt(19, 82.2, "3DSC canonical cohort", size=8.2, weight="bold")
logo("3dsc", 9.8, 78.4, 0.26)
txt(23.2, 79.6, "%d fittable on both axes;"
    % UPSTREAM["fittable_compounds_v321"], size=6.9)
txt(23.2, 77.3, "%d field-axis fits admitted" % C["field_axis_fits_ok"],
    size=6.9)
box(33.5, 75.5, 27, 8.2, BLUE, ec=BLUE_E)
txt(47, 82.2, "Compositional features", size=8.2, weight="bold")
logo("magpie", 37.8, 78.4, 0.26)
txt(52.5, 79.6, "Magpie descriptors;", size=7.3)
txt(52.5, 77.3, "classifier inputs", size=7.3)

# EXTRACTION
box(4, 47, 58, 25.6, TEAL, ec="#6FA48D", r=1.0)
txt(33, 71.2, "EXTRACTION", size=10.5, weight="bold")
box(5.5, 59.5, 55, 9.5, SALMON, ec=SALMON_E)
txt(33, 67.4, "Vision-pass extraction", size=8.6, weight="bold")
logo("openai", 33, 64.6, 0.26)
txt(33, 62.4, "Round 1/2/3 disambiguation passes under a cross-model "
              "agreement gate", size=7.2)
txt(33, 60.5, "Jc(T) at fixed H  →  βT   |   Jc(H) at fixed T  "
              "→  βH         n=%d vision cache entries"
    % UPSTREAM["vision_cache_entries"], size=7.0)
box(5.5, 48.3, 55, 10, SALMON, ec=SALMON_E)
logo("mp_small", 22, 56.4, 0.26)
logo("elsevier", 31, 56.4, 0.26)
logo("springer", 44, 56.4, 0.26)
txt(33, 53.0, "Multi-API mainframe", size=8.6, weight="bold")
txt(33, 51.0, "DOI-based retrieval orchestration + UCLA library "
              "cross-reference", size=7.2)
txt(33, 49.3, "%d papers over %d compound labels, %d extracted points"
    % (C["fitted_curve_papers"], C["fitted_curve_compounds"],
       C["extracted_points"]), size=7.0)

# CRITICAL-SCALE RESOLUTION, the stage v22 does not draw
box(4, 33.4, 58, 12.1, HILITE, ec=HILITE_E, lw=1.7, r=1.0)
txt(33, 43.4, "CRITICAL-SCALE RESOLUTION", size=9.6, weight="bold",
    color=HILITE_E)
txt(33, 41.0, "Assign Tc and Hc2,0 to every fitted curve through the "
              "provenance hierarchy", size=7.4)
txt(33, 38.8, "Tier 1 paper-reported   ·   Tier 2 literature-cited   "
              "·   Tier 3 registry   ·   Tier 4 estimated", size=7.0)
txt(33, 36.7, "every curve's T$_c$ and H$_{c2,0}$ carries its tier",
    size=7.0, style="italic", color="#3E5F7E")
txt(33, 34.7, "%d per-paper anchors over %d papers feed Sec. III.F"
    % (C["anchor_rows"], C["anchor_papers"]), size=7.0, style="italic",
    color="#3E5F7E")

# AI TOOLING
box(4, 4, 58, 20, PEACH, ec="#E0CFA8", r=1.0)
txt(33, 21.2, "AI TOOLING", size=10.5, weight="bold")
box(7, 6.5, 52, 12, "#FFFFFF", ec="#D9D9D9")
logo("anthropic", 33, 14.6, 0.30)
txt(33, 10.4, "Claude (Anthropic)", size=8.6, weight="bold")
txt(33, 8.2, "Methodology + dispatch + audit", size=7.4)

# =========================== right column ============================
box(70, 3, 52, 95, "#FDFDF0", ec="#C9C9A8", r=1.2, z=1)

# PREDICTOR
box(72, 60, 48, 36.5, LAV, ec="#D4C4C7", r=1.0)
txt(96, 94.6, "PREDICTOR", size=10.5, weight="bold")
box(73.5, 85.2, 45, 8.2, AMBER, ec="#DEBB5C")
txt(96, 91.6, "Form 3 partial-fit", size=9.4, weight="bold")
txt(96, 89.2, "log Jc = log Jc,partial + β · log$_{10}$ (1 − x/x$_c$)",
    size=8.2)
txt(96, 86.6, "fitted per axis: β$_T$ separately, β$_H$ separately",
    size=7.2)
box(73.5, 72.5, 45, 11.5, AMBER, ec="#DEBB5C")
txt(96, 82.2, "Multi-stage predictor architecture", size=9.0, weight="bold")
txt(96, 79.8, "Stage 1  substructure classification, rank scope", size=7.3)
txt(96, 77.6, "Stage 2  sample-form-conditional median", size=7.3)
txt(96, 75.4, "Stage 3  substructure-aggregate median with an IQR bound",
    size=7.3)
txt(96, 73.4, "%d temperature-axis fits  ·  %d field-axis fits from %d "
              "papers" % (C["temperature_axis_fits"], C["field_axis_fits_ok"],
                          C["field_axis_ok_papers"]), size=7.0, style="italic",
    color="#6A5A3A")
box(73.5, 61.3, 45, 10, AMBER, ec="#DEBB5C")
txt(96, 69.6, "Dispatch through refusal gates", size=9.0, weight="bold")
N_GATES = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
if len(REFUSAL_LABEL) not in N_GATES:
    raise SystemExit("no word for %d refusal conditions" % len(REFUSAL_LABEL))
txt(96, 67.3, "%s refusal conditions:  reduced field below the validated "
              "window," % N_GATES[len(REFUSAL_LABEL)], size=7.2)
txt(96, 65.3, "reduced temperature at or above it, target above Tc,", size=7.2)
txt(96, 63.3, "critical field unavailable, family without a validated field "
              "axis", size=7.2)

# EMPIRICAL VALIDATION
box(72, 33, 48, 24.5, LAV2, ec="#D4C4C7", r=1.0)
txt(96, 55.6, "EMPIRICAL VALIDATION", size=10.5, weight="bold")
box(73.5, 35, 21.5, 17.5, AMBER, ec="#DEBB5C")
txt(84.2, 50.6, "In-corpus", size=8.8, weight="bold")
txt(84.2, 48.2, "leave-one-compound-out", size=7.2)
txt(84.2, 46.2, "within substructure", size=7.2)
txt(84.2, 43.6, "permutation test on the", size=7.2)
txt(84.2, 41.6, "family label, papers as", size=7.2)
txt(84.2, 39.6, "the unit", size=7.2)
txt(84.2, 37.0, "bootstrap CI, N=5000", size=7.0, style="italic",
    color="#6A5A3A")
box(97, 35, 21.5, 17.5, AMBER, ec="#DEBB5C")
txt(107.7, 50.6, "External", size=8.8, weight="bold")
txt(107.7, 48.2, "out-of-corpus cuprates", size=7.2)
txt(107.7, 46.2, "held out entirely", size=7.2)
txt(107.7, 43.6, "K-anchor sensitivity", size=7.2)
txt(107.7, 41.6, "at K = 1 and K = 3", size=7.2)
txt(107.7, 38.6, "measurement-window", size=7.0, style="italic",
    color="#6A5A3A")
txt(107.7, 36.8, "saturation reported", size=7.0, style="italic",
    color="#6A5A3A")

# OUTPUT
box(72, 6, 48, 24, LAV2, ec="#D4C4C7", r=1.0)
txt(96, 28.2, "OUTPUT", size=10.5, weight="bold")
box(73.5, 17, 45, 9, AMBER, ec="#DEBB5C")
txt(96, 24.2, "Family-scope Jc(T,H) envelope", size=9.0, weight="bold")
txt(96, 21.8, "with a 95% bootstrap interval and an explicit refusal flag",
    size=7.3)
txt(96, 19.4, "%d candidate compounds evaluated, %d receive an emitted target"
    % (C["candidate_compounds"], C["dispatched_compounds"]), size=7.0,
    style="italic", color="#6A5A3A")
box(73.5, 7.2, 45, 8.4, AMBER, ec="#DEBB5C")
txt(96, 13.8, "Family-level screening curves", size=9.0, weight="bold")
txt(96, 11.6, "one family curve per grid point; the within-family spread",
    size=7.0)
txt(96, 9.8, "is a small fraction of the bootstrap interval, and no",
    size=7.0)
txt(96, 8.1, "per-compound ranking is emitted", size=7.0)

# ============================== arrows ==============================
arrow(33, 74, 33, 72.4, "corpus records: figure, axes, source paper",
      lx=34.2, ly=73.2, ha="left", dashed=False, color="#5A5A5A")
arrow(33, 47, 33, 45.8, "curve records: sample form, fixed-axis value",
      lx=34.2, ly=46.4, ha="left", dashed=False, color="#5A5A5A")
# AI tooling feeds extraction, so the arrow points into it, as in v22.
arrow(33, 24.2, 33, 34.3, None, dashed=True, color=DASH)
txt(34.4, 29.0, "methodology,\ndispatch, audit", size=6.4, color="#4A4A4A",
    ha="left", style="italic")
# The one connection Referee B could not follow: extraction and its resolved
# scales into the predictor. It is a single labelled arrow now.
arrow(62.2, 44.6, 71.9, 76.0, None)
txt(65.4, 60.3, "resolved T$_c$ and H$_{c2,0}$ per curve,\n"
                "each tagged with its provenance tier",
    size=6.5, color="#4A4A4A", ha="center", style="italic", rot=72.9)
arrow(96, 85.2, 96, 84.2, "β$_T$, β$_H$ and log J$_c$,partial per curve",
      lx=97.2, ly=84.7, ha="left", dashed=False, color="#5A5A5A", size=6.3)
arrow(96, 72.5, 96, 71.4, "family medians and the regime label",
      lx=97.2, ly=71.9, ha="left", dashed=False, color="#5A5A5A", size=6.3)
arrow(96, 61.3, 96, 57.7, "the validated scope, per family and axis",
      lx=97.2, ly=59.4, ha="left", dashed=False, color="#5A5A5A", size=6.3)
arrow(96, 33, 96, 30.2, "envelopes that survive every gate", lx=97.2,
      ly=31.5, ha="left", dashed=False, color="#5A5A5A")
# the refusal branch, leaving dispatch explicitly
arrow(118.5, 66.3, 126.5, 66.3, None, dashed=False, color="#A83A2E")
txt(127.5, 67.6, "refusal code", size=7.4, weight="bold", color="#A83A2E",
    ha="left")
txt(127.5, 65.4, "the target is withheld", size=7.0, color="#A83A2E",
    ha="left",
    style="italic")

# =============================== call-outs ===========================
box(125, 84, 25, 11, CREAM, ec="#D8D0A8", r=0.8)
txt(137.5, 92.6, "Conditioning is a", size=8.0, weight="bold")
txt(137.5, 90.6, "temperature-axis result", size=8.0, weight="bold")
txt(137.5, 88.4, "all three assessable families", size=7.0)
txt(137.5, 86.6, "fall below the screening-grade", size=7.0)
txt(137.5, 84.8, "threshold on the repaired", size=7.0)
txt(137.5, 83.0, "257-fit cohort (Sec. III.C)", size=7.0)

box(125, 37, 25, 13, CREAM, ec="#D8D0A8", r=0.8)
txt(137.5, 47.6, "Field axis not validated", size=8.0, weight="bold")
txt(137.5, 45.4, "at family level", size=8.0, weight="bold")
txt(137.5, 43.0, "the exponent separates no", size=7.0)
txt(137.5, 41.4, "family on any cohort;", size=7.0)
txt(137.5, 39.8, "0.038 at p = 0.98 on the", size=7.0)
txt(137.5, 38.2, "%d admitted fits" % C["field_axis_fits_ok"], size=7.0)

box(125, 15, 25, 11, CREAM, ec="#D8D0A8", r=0.8)
txt(137.5, 23.6, "%d compounds evaluated" % C["candidate_compounds"],
    size=8.0, weight="bold")
txt(137.5, 21.4, "%d receive an emitted target," % C["dispatched_compounds"],
    size=7.0)
txt(137.5, 19.8, "all MgB2-class; the other two", size=7.0)
txt(137.5, 18.2, "families dispatch nothing and", size=7.0)
txt(137.5, 16.4, "the refusal reason is recorded", size=7.0)

for x0, y0, x1, y1 in ((120, 89.5, 125, 89.5), (120, 44, 125, 44),
                       (120, 20.5, 125, 20.5)):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-",
                                 linewidth=0.9, color="#8A8A6A", zorder=3))

os.makedirs("figures", exist_ok=True)
n_txt, n_box = L.check()
print("   %d text runs checked against %d boxes, none overflowing"
      % (n_txt, n_box))
fig.savefig("figures/manuscript_figure_2.png", dpi=300,
            facecolor=CANVAS)
fig.savefig("figures/manuscript_figure_2.pdf", facecolor=CANVAS)
print("wrote figures/manuscript_figure_2.png and .pdf")
print("   counts drawn from the deposit: %d screened, %d papers, %d compounds,"
      % (UPSTREAM["articles_screened"], C["fitted_curve_papers"],
         C["fitted_curve_compounds"]))
print("   %d points, %d temperature fits, %d field fits from %d papers"
      % (C["extracted_points"], C["temperature_axis_fits"],
         C["field_axis_fits_ok"], C["field_axis_ok_papers"]))
