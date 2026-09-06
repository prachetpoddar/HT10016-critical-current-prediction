"""
manuscript_figure_1.py

Figure 1, composited from the rendered assets the author built it from.

figures/fig1_assets/ holds the Blender renders and the Inkscape drawing behind
the original: the funnel, the Jc(T,H) surface with its two confidence sheets,
the four substructure prototypes, and the gate Venn. Earlier versions of this
script drew a funnel in matplotlib, which was never going to match a rendered
one, so the renders are used directly.

Three things had to be done to the assets and each is a function below.

  The renders are composited over black, so their RGB is premultiplied by
  coverage. key_black recovers an alpha from luminance and divides the
  premultiplication back out; without that the antialiased rim carries a dark
  halo onto a light panel.

  The Venn is an SVG whose subscript tspan uses font-size:65% with
  baseline-shift, neither of which cairosvg honours: the first render put a
  giant stray "C" in the corner. venn() writes the subscript inline instead.

  The Venn also printed a population threshold, "(2<=n<=6 compounds)", that
  appears nowhere in the manuscript. venn() replaces it with what Sec. III.E
  does say, that three families meet the requirement.

The 3D bar chart in figures/fig1_assets is deliberately not used. Its three
bars are the Stage 1, Stage 2 and Stage 3 errors of 10.10, 0.43 and 0.84, and
Sec. III.A withdraws that comparison: the first two are computed on different
cohorts, nine families against five, and both are in-sample. Drawing the bars
would re-assert with their heights a claim the text retracts in words.

Every count comes from analysis/figure_counts.py, which recomputes from the
deposited tables and refuses to return if the numbers the figures share with
Table I disagree with it. Every result is pinned in RESULTS with the section
it is taken from. Every text run is measured against the box it sits in by
analysis/figure_layout.py and the figure refuses to write on overflow.

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
import os

import matplotlib
matplotlib.use("Agg")
_logging.getLogger("matplotlib.font_manager").setLevel(_logging.ERROR)
import numpy as np                                               # noqa: E402
from PIL import Image                                            # noqa: E402
from matplotlib.offsetbox import AnnotationBbox, OffsetImage     # noqa: E402

from figure_counts import from_deposit, UPSTREAM                 # noqa: E402
from figure_layout import new_figure                             # noqa: E402

ASSETS = os.path.join("figures", "fig1_assets")
CACHE = os.path.join(ASSETS, "_keyed")

WHITE = "#FFFFFF"
PANEL_L, EDGE_L = "#F0F2F8", "#D5DAE8"
PANEL_M, EDGE_M = "#F8F5EF", "#E6DECB"
PANEL_R, EDGE_R = "#F3F7F2", "#D8E6DA"
PILL, PILL_E = "#F9F2D2", "#DEBB5C"
BAND_ACCENT = "#2E3C78"
INK, SOFT, GREY = "#1A1D23", "#4A4A4A", "#7A828E"
AMBER_T = "#7A5C16"

RESULTS = dict(
    # Sec. III.C, the permutation test on the substructure label with source
    # papers as the unit, added to the manuscript on 2026-09-06.
    eta2_temperature=0.524, perm_p_temperature=0.007,
    eta2_field=0.038, perm_p_field=0.98,
    # Sec. III.A, after the anchor repair of Sec. III.F. The sample counts the
    # manuscript prints beside these are not reproduced: "0.37 on 7"
    # disagrees with audit/variance_decomposition_repaired.csv, which has 5.
    ratio_11=0.81, ratio_122=0.37, ratio_mgb2=0.04, p_floor_mgb2=0.33,
    # Sec. III.D and Table III
    universal_sd_pct=13.0, universal_var_pct=24.3, universal_threshold=30,
    universal_cohort=23,
    # Sec. III.E
    family_median=4.98, median_T=4.2, median_H=5,
    # Table IV, combined row
    field_refused_compounds=60,
)


# ---------------------------------------------------------------- assets
def key_black(name, thresh=26.0, floor=30):
    """Recover alpha from a render composited over black, and crop it.

    The renders carry a faint ambient wash over the whole frame at a few
    percent coverage; anything below floor is that wash and not the object.
    """
    out = os.path.join(CACHE, name + ".png")
    if os.path.exists(out):
        return out
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    a = np.asarray(Image.open(os.path.join(ASSETS, name + ".png"))
                   .convert("RGB")).astype(np.float32)
    alpha = np.clip(a.max(axis=2) / thresh, 0, 1)
    alpha[alpha < floor / 255.0] = 0.0
    rgb = np.where(alpha[..., None] > 0.02,
                   a / np.maximum(alpha[..., None], 0.02), 0)
    px = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    ys, xs = np.nonzero(px[:, :, 3] > 0)
    Image.fromarray(px, "RGBA").crop(
        (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(out)
    return out


def venn():
    """Render the gate Venn from its SVG, with two source defects repaired."""
    out = os.path.join(CACHE, "venn.png")
    if os.path.exists(out):
        return out
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    import cairosvg
    s = open(os.path.join(ASSETS, "venn.svg")).read()
    sub = ('Monotonic J<tspan\n   style="font-size:65%;baseline-shift:sub"\n'
           '   id="tspan15">c</tspan>(T) </tspan>')
    if sub not in s:
        raise SystemExit("venn.svg: the Jc subscript fragment is not where "
                         "this script expects it; check the source drawing")
    s = s.replace(sub, "Monotonic Jc(T)</tspan>")
    if "(2≤n≤6 compounds)" not in s:
        raise SystemExit("venn.svg: the population-threshold label is not "
                         "where this script expects it")
    s = s.replace("(2≤n≤6 compounds)", "(three families qualify)")
    tmp = os.path.join(CACHE, "venn_edited.svg")
    open(tmp, "w").write(s)
    cairosvg.svg2png(url=tmp, write_to=out, output_width=2200,
                     output_height=2200, background_color=None)
    px = np.asarray(Image.open(out))
    ys, xs = np.nonzero(px[:, :, 3] > 8)
    Image.open(out).crop(
        (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(out)
    return out


C = from_deposit()
fig, ax, L = new_figure(11.4, 7.2, 152, 96, WHITE)
DPI = 300


def place(path, cx, cy, w=None, h=None, z=3):
    """Centred placement with an exact width or height in data units."""
    im = Image.open(path)
    iw, ih = im.size
    ux, uy = 152.0 / 11.4, 96.0 / 7.2          # data units per inch
    if w is not None:
        target_in = w / ux
        zoom = target_in * DPI / iw
    else:
        target_in = h / uy
        zoom = target_in * DPI / ih
    ax.add_artist(AnnotationBbox(OffsetImage(im, zoom=zoom, dpi_cor=False),
                                 (cx, cy), frameon=False, zorder=z))


# ================================ panels ================================
for x, fc, ec, nm in ((2, PANEL_L, EDGE_L, "panel a"),
                      (52.5, PANEL_M, EDGE_M, "panel b"),
                      (103, PANEL_R, EDGE_R, "panel c")):
    L.box(x, 3, 47, 88, fc, ec=ec, lw=1.0, r=1.4, z=1, name=nm)
    L.region(x + 2, 5, 43, 84, "%s text area" % nm)
for x0 in (49.6, 100.1):
    ax.annotate("", xy=(x0 + 2.4, 47), xytext=(x0, 47), zorder=4,
                arrowprops=dict(arrowstyle="-|>", color="#8A8A8A", lw=1.7))

# ===================== (a) heterogeneous literature =====================
L.txt(25.5, 87.4, "Heterogeneous J$_c$(T,H)", size=11.2, weight="bold")
L.txt(25.5, 84.2, "literature", size=11.2, weight="bold")

for dx, dy in ((0, 0), (1.3, -1.1), (2.6, -2.2)):
    ax.add_patch(matplotlib.patches.Polygon(
        [(6.6 + dx, 80.0 + dy), (11.2 + dx, 80.0 + dy),
         (11.2 + dx, 75.2 + dy), (6.6 + dx, 75.2 + dy)], closed=True,
        facecolor=WHITE, edgecolor=INK, linewidth=0.7, zorder=3))
# Sec. II.A says the fitted cohort is not drawn exclusively from the two
# publisher APIs, and says so because an earlier version implied it was.
L.txt(31.0, 79.0, "n = %d articles retrieved" % UPSTREAM["articles_screened"],
      size=7.8)
L.txt(31.0, 76.8, "and screened, Elsevier + Springer;", size=7.0, color=SOFT)
L.txt(31.0, 74.8, "fitted curves also come from arXiv", size=7.0, color=SOFT)
L.txt(31.0, 72.8, "preprints and NHMFL records", size=7.0, color=SOFT)

FUNNEL_TOP, FUNNEL_BOT, FUNNEL_CX = 71.6, 38.9, 25.5
place(key_black("funnel"), FUNNEL_CX, (FUNNEL_TOP + FUNNEL_BOT) / 2.0,
      h=FUNNEL_TOP - FUNNEL_BOT, z=3)

# The funnel's half-width at a height, measured from the render's own alpha
# channel rather than modelled. Two band labels overflowed a hand-written
# taper, and a picture that already knows its silhouette should not be
# described a second time in arithmetic.
_F = np.asarray(Image.open(key_black("funnel")))
_F_ROWS = (_F[:, :, 3] > 8).sum(axis=1).astype(float)
_F_H, _F_W = _F.shape[0], _F.shape[1]
FUNNEL_W = (FUNNEL_TOP - FUNNEL_BOT) * _F_W / float(_F_H)


def funnel_half(y):
    """Half the drawn funnel's width at data-space height y, in data units."""
    if not (FUNNEL_BOT <= y <= FUNNEL_TOP):
        return 0.0
    row = int(round((FUNNEL_TOP - y) / (FUNNEL_TOP - FUNNEL_BOT)
                    * (_F_H - 1)))
    return _F_ROWS[min(max(row, 0), _F_H - 1)] / 2.0 / _F_W * FUNNEL_W


BANDS = [(65.6, 62.6, "Applicability window, Eq. (1)", BAND_ACCENT),
         (59.6, 56.6, "Partial-fit and full-fit", WHITE),
         (53.8, 51.0, "Cross-model agreement", WHITE)]
for y, rule, label, colour in BANDS:
    half = funnel_half(rule)
    ax.plot([FUNNEL_CX - half * 0.94, FUNNEL_CX + half * 0.94], [rule, rule],
            lw=0.7, color="#FFFFFF", alpha=0.5, zorder=5,
            solid_capstyle="butt")
    L.band_region(FUNNEL_CX, funnel_half, y - 1.5, y + 1.5,
                  "funnel at \"%s\"" % label)
    L.txt(FUNNEL_CX, y, label, size=7.0, weight="bold", color=colour, z=6)

L.txt(25.5, 36.6, "Cohort A:  J$_c$(T) at fixed H", size=8.2, weight="bold")
L.txt(25.5, 33.8, "Cohort B:  J$_c$(H) at fixed T", size=8.2, weight="bold")
L.txt(25.5, 31.0, "T/T$_c$ < 0.7            $\\Delta$H/H$_{c2}$ > 0.3",
      size=7.8, color=SOFT)

L.box(5, 7, 41, 20.5, WHITE, ec=EDGE_L, r=0.8, name="cohort census")
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
    y = 24.9 - n * 3.15
    L.txt(13.6, y, val, size=8.4, weight="bold", ha="right")
    L.txt(14.8, y, lab, size=7.0, ha="left", color=SOFT)

# ===================== (b) multi-stage aggregation ======================
L.txt(76, 87.4, "Multi-stage substructure", size=11.2, weight="bold")
L.txt(76, 84.2, "conditional aggregation", size=11.2, weight="bold")

L.box(56.5, 74.4, 39, 8.0, PILL, ec=PILL_E, lw=1.3, r=0.9, name="headline")
L.txt(76, 80.3, "the family label accounts for %.2f of the"
      % RESULTS["eta2_temperature"], size=8.4, weight="bold", color=AMBER_T)
L.txt(76, 77.5, "temperature-exponent variance, p = %.3f"
      % RESULTS["perm_p_temperature"], size=8.4, weight="bold", color=AMBER_T)
L.txt(76, 71.6, "source papers are the permutation unit. On the field axis",
      size=6.9, color=SOFT, style="italic")
L.txt(76, 69.6, "it is %.3f at p = %.2f and no family-level verdict is given"
      % (RESULTS["eta2_field"], RESULTS["perm_p_field"]), size=6.9,
      color=SOFT, style="italic")

L.txt(76, 65.0, "log$_{10}$J$_c$ = log$_{10}$J$_{c,\\mathrm{partial}}$ + "
                "$\\beta$ log$_{10}$(1 $-$ x/x$_c$)", size=9.4)
L.txt(76, 61.8, "fitted per axis, then aggregated at three scopes:  "
                "monolithic,", size=6.9, color=SOFT, style="italic")
L.txt(76, 59.8, "sample-form-conditional median, substructure-aggregate "
                "median", size=6.9, color=SOFT, style="italic")

PROTOS = [(60.5, "compound_chalcogenide_11", "Iron chalcogenide", "11-type"),
          (70.7, "compound_pnictide_122", "Iron pnictide", "122-type"),
          (80.9, "compound_AlB2", "MgB$_2$-class", "AlB$_2$ prototype"),
          (91.1, "compound_pnictide_1111", "Iron pnictide", "1111-type")]
for cx, asset, l1, l2 in PROTOS:
    place(key_black(asset), cx, 51.0, h=8.6, z=3)
    L.txt(cx, 45.0, l1, size=6.6)
    L.txt(cx, 43.0, l2, size=6.6, color=SOFT)

L.box(56.5, 7, 39, 32.0, WHITE, ec="#DED6C4", r=0.8, name="diagnostic")
L.txt(76, 36.4, "The sample-form diagnostic sets the rule", size=8.0,
      weight="bold")
L.txt(76, 34.0, "the predictor follows, family by family. After the",
      size=6.9, color=SOFT)
L.txt(76, 32.0, "repair of Sec. III.F it explains %.2f, %.2f and %.2f of the"
      % (RESULTS["ratio_11"], RESULTS["ratio_122"], RESULTS["ratio_mgb2"]),
      size=6.9, color=SOFT)
L.txt(76, 30.0, "within-family scatter in the anchor, for the three",
      size=6.9, color=SOFT)
L.txt(76, 28.0, "families above in that order.", size=6.9, color=SOFT)
L.txt(76, 24.6, "It does not establish the distinction to significance:",
      size=6.9, color=SOFT)
L.txt(76, 22.6, "sample form is nearly a relabelling of source paper here,",
      size=6.9, color=SOFT)
L.txt(76, 20.6, "and under the only null that respects that structure the",
      size=6.9, color=SOFT)
L.txt(76, 18.6, "MgB$_2$ cell can never return p below %.2f."
      % RESULTS["p_floor_mgb2"], size=6.9, color=SOFT)
L.txt(76, 15.2, "No fold improvement is reported either. Under leave-one-",
      size=6.9, color=SOFT)
L.txt(76, 13.2, "substructure-out the errors are 12.3 without conditioning",
      size=6.9, color=SOFT)
L.txt(76, 11.2, "and 14.9 with it over seven families, 1.19 and 0.55 on the",
      size=6.9, color=SOFT)
L.txt(76, 9.2, "fits passing physicality over three.", size=6.9, color=SOFT)

# ====================== (c) bounded predictions =========================
L.txt(126.5, 87.4, "Bounded screening", size=11.2, weight="bold")
L.txt(126.5, 84.2, "grade predictions", size=11.2, weight="bold")

place(venn(), 126.5, 68.4, h=29.0, z=3)

L.txt(126.5, 51.0, "Universal (T/T$_c$, H/H$_{c2}$) scaling is not adopted",
      size=8.2, weight="bold")
L.txt(126.5, 48.4, "within-bin standard deviation falls %.1f%%, %.1f%% on the"
      % (RESULTS["universal_sd_pct"], RESULTS["universal_var_pct"]),
      size=7.0, color=SOFT)
L.txt(126.5, 46.3, "variance scale, both below the %d%% adoption threshold, on"
      % RESULTS["universal_threshold"], size=7.0, color=SOFT)
L.txt(126.5, 44.2, "the pre-withdrawal %d-compound cohort (Table III)"
      % RESULTS["universal_cohort"], size=7.0, color=SOFT)

place(key_black("surface_plot"), 126.5, 36.4, w=36.5, z=3)
L.txt(126.5, 27.4, "Family-scope J$_c$(T,H) envelope with a 95% bootstrap "
                   "interval", size=7.0, color=SOFT, style="italic")

L.box(105.5, 7, 41, 18.5, WHITE, ec=EDGE_R, r=0.8, name="dispatch outcome")
OUT = [("%d" % C["candidate_compounds"], "candidate compounds evaluated"),
       ("%d" % C["dispatched_compounds"],
        "dispatched, every one MgB$_2$-class"),
       ("%d" % RESULTS["field_refused_compounds"],
        "refused a field target, no H$_{c2,0}$ anchor"),
       ("%.2f" % RESULTS["family_median"],
        "log$_{10}$J$_c$ at %.1f K and %d T" % (RESULTS["median_T"],
                                                RESULTS["median_H"]))]
for n, (val, lab) in enumerate(OUT):
    y = 22.6 - n * 3.3
    L.txt(115.5, y, val, size=8.4, weight="bold", ha="right")
    L.txt(116.7, y, lab, size=7.0, ha="left", color=SOFT)
L.txt(126.5, 9.2, "One family curve per grid point; no per-compound ranking.",
      size=6.9, color=SOFT, style="italic")

# =============================== write out ==============================
n_txt, n_box = L.check()
print("   %d text runs checked against %d boxes, none overflowing"
      % (n_txt, n_box))
fig.savefig("figures/manuscript_figure_1.png", dpi=DPI)
fig.savefig("figures/manuscript_figure_1.pdf")
print("wrote figures/manuscript_figure_1.png and .pdf")
print("   counts from the deposit: %d screened, %d papers, %d labels, %d "
      "points," % (UPSTREAM["articles_screened"], C["fitted_curve_papers"],
                   C["fitted_curve_compounds"], C["extracted_points"]))
print("   %d fittable on both axes, %d anchors over %d papers, %d candidates "
      "of which %d dispatched"
      % (UPSTREAM["fittable_compounds_v321"], C["anchor_rows"],
         C["anchor_papers"], C["candidate_compounds"],
         C["dispatched_compounds"]))
