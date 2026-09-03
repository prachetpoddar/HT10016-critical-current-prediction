"""
manuscript_figure_2.py

Generator for Figure 2 of the manuscript. The runtime architecture schematic. It carries one datum, the screened-corpus count, and is otherwise independent of the cohort.

Figure-to-script mapping for this deposit, because the names do not line up on
their own and using the wrong script produces a figure in a different visual
style that still looks plausible:

    Fig. 1  analysis/manuscript_figure_1.py
    Fig. 2  analysis/manuscript_figure_2.py
    Fig. 3  analysis/figure_4_source.py      (also the variance-decomposition library)
    Fig. 4  analysis/manuscript_figure_4.py
    Fig. 5  analysis/manuscript_figure_5.py  (reads data/family_params.json)

Figures 2, 4 and 5 reproduce the deposited images byte for byte. Figures 1 and 3
depend on the cohort and change with it.

Run from the repository root; writes into figures/.
"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from figure_counts import UPSTREAM

plt.rcParams.update({"font.family":"serif","font.size":8.6,"mathtext.fontset":"dejavuserif"})
fig,ax=plt.subplots(figsize=(6.9,6.5)); ax.set_xlim(0,10); ax.set_ylim(0,12.6); ax.axis("off")

INK="#1A1D23"; EDGE="#7A828E"; FILL="#F2F4F7"; HL="#3B4A8C"; HLFILL="#E8ECF7"; REF="#A24A3E"
STAGES=[
 ("1", "Corpus assembly and fittability filtering",
      "Retrieval, deduplication by DOI, screening against\nthe applicability window of Eq. (1)"),
 ("2", "Curve-level extraction",
      "Vision-assisted plot reading under a cross-model\nagreement gate; deterministic code thereafter"),
 ("3", "Critical-scale resolution",
      r"Assign $T_c$ and $H_{c2,0}$ to each fitted curve" "\n"
      "through the provenance hierarchy of Sec. II.B"),
 ("4", "Per-axis exponent fitting",
      "Fit Form 3, Eq. (1), independently on each axis\nwithin physically grouped curves"),
 ("5", "Scope selection and aggregation",
      "Variance diagnostic selects Stage 2 or Stage 3;\nmedians taken within the selected cell"),
 ("6", "Dispatch through refusal gates",
      "Anchor count, monotonicity, family population,\nanchor availability, target inside calibration"),
]
ARROWS=[
 "%d screened articles" % UPSTREAM["articles_screened"],
 "curve records: sample form, sample identifier,\nfixed-axis value, source paper",
 r"$T_c$ and $H_{c2,0}$ per curve, each tagged with its provenance tier",
 r"$\beta_T$, $\beta_H$, $\log_{10} J_{c,\mathrm{partial}}$ per curve",
 "family median parameters and the regime label",
]
H=1.28; GAP=0.62; y=12.2
box_y=[]
for i,(num,title,detail) in enumerate(STAGES):
    hl = (num=="3")
    ax.add_patch(FancyBboxPatch((0.55,y-H),6.4,H,boxstyle="round,pad=0.02,rounding_size=0.10",
        linewidth=1.15 if hl else 0.9, edgecolor=HL if hl else EDGE, facecolor=HLFILL if hl else FILL, zorder=2))
    ax.text(0.95,y-0.40,num,fontsize=10,fontweight="bold",color=HL if hl else EDGE,va="center",ha="center",zorder=3)
    ax.text(1.40,y-0.40,title,fontsize=9.3,fontweight="bold",color=HL if hl else INK,va="center",ha="left",zorder=3)
    ax.text(1.40,y-0.92,detail,fontsize=7.5,color="#4A515C",va="center",ha="left",linespacing=1.35,zorder=3)
    box_y.append((y,y-H))
    if i<len(STAGES)-1:
        ytop=y-H; ybot=y-H-GAP
        ax.add_patch(FancyArrowPatch((3.75,ytop),(3.75,ybot),arrowstyle="-|>",mutation_scale=11,
                     lw=1.0,color=EDGE,zorder=2,shrinkA=0,shrinkB=0))
        ax.text(4.00,(ytop+ybot)/2,ARROWS[i],fontsize=7.1,color="#3E444E",va="center",ha="left",
                linespacing=1.3,zorder=3)
        y=ybot
ax.text(0.55,12.45,"Input",fontsize=8.6,style="italic",color=EDGE,ha="left")

# refusal branch off stage 6
ytop,ybot=box_y[-1]
ax.add_patch(FancyArrowPatch((6.95,(ytop+ybot)/2),(8.55,(ytop+ybot)/2),arrowstyle="-|>",
             mutation_scale=11,lw=1.0,color=REF,zorder=2))
ax.text(8.62,(ytop+ybot)/2+0.14,"refusal code",fontsize=7.4,color=REF,ha="left",va="center")
ax.text(8.62,(ytop+ybot)/2-0.20,"no value emitted",fontsize=7.0,color=REF,ha="left",va="center",style="italic")
# output
ax.add_patch(FancyArrowPatch((3.75,ybot),(3.75,ybot-0.60),arrowstyle="-|>",mutation_scale=11,lw=1.0,color=EDGE))
ax.text(4.00,ybot-0.34,"family-scope envelope with a 95% bootstrap interval",
        fontsize=7.1,color="#3E444E",va="center",ha="left")
ax.text(0.55,ybot-0.86,"Predictor output",fontsize=8.6,style="italic",color=EDGE,ha="left")
fig.savefig("figures/manuscript_figure_2.png",dpi=400,bbox_inches="tight")
fig.savefig("figures/manuscript_figure_2.pdf",bbox_inches="tight")
print("written")
