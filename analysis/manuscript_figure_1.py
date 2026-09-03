"""
manuscript_figure_1.py

Generator for Figure 1 of the manuscript. The corpus-to-cohort flow in panel (a) and candidate dispatch by family in panel (b). Every count here is also asserted by analysis/verify_deposit.py against the deposited tables, so the figure cannot drift from the data the way it did once already.

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
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from figure_counts import from_deposit, UPSTREAM

# Nothing this figure prints is typed here. The cohort counts come from the
# deposited tables and the four upstream constants are named in
# analysis/figure_counts.py, so a withdrawal moves the figure on the same run
# that moves the data.
C = from_deposit()

plt.rcParams.update({"font.family":"serif","font.size":8.6,"mathtext.fontset":"dejavuserif"})
fig=plt.figure(figsize=(7.1,4.5))
gs=fig.add_gridspec(1,2,width_ratios=[1.32,1.0],wspace=0.22)
axA=fig.add_subplot(gs[0]); axB=fig.add_subplot(gs[1])
for a in (axA,axB): a.axis("off")
INK="#1A1D23"; EDGE="#7A828E"; FILL="#F2F4F7"; ACC="#3B4A8C"; REF="#A24A3E"; OK="#1B8A7A"

# ---------------- (a) what the corpus actually supplies ----------------
axA.set_xlim(0,10); axA.set_ylim(-0.9,10)
axA.set_title("(a)  From retrieval to fitted evidence",fontsize=9,loc="left",pad=6)
rows=[(UPSTREAM["articles_screened"],"articles retrieved and screened",9.6,1.00),
      (C["fitted_curve_papers"],"papers contributing fitted curves",7.9,0.74),
      (C["fitted_curve_compounds"],"distinct compounds",6.2,0.56),
      (C["extracted_points"],"extracted critical-current points",4.5,0.56),
      (UPSTREAM["fittable_compounds_v321"],"compounds fittable on both axes",2.8,0.34),
      (C["anchor_rows"],"per-paper anchors behind Fig. 3",1.2,0.44)]
for n,(val,lab,y,w) in enumerate(rows):
    x0=0.35; W=8.6
    axA.add_patch(FancyBboxPatch((x0,y-0.62),W,0.98,boxstyle="round,pad=0.02,rounding_size=0.08",
        lw=0.9,edgecolor=ACC if n in (1,4) else EDGE,
        facecolor="#E8ECF7" if n in (1,4) else FILL,zorder=2))
    axA.text(x0+0.28,y-0.13,str(val),fontsize=11,fontweight="bold",color=ACC if n in (1,4) else INK,va="center",zorder=3)
    axA.text(x0+2.15,y-0.13,lab,fontsize=7.5,color="#454C57",va="center",zorder=3)
    if n<len(rows)-1:
        axA.add_patch(FancyArrowPatch((x0+0.55,y-0.62),(x0+0.55,rows[n+1][2]+0.36),
            arrowstyle="-|>",mutation_scale=9,lw=0.85,color=EDGE,zorder=1))
axA.text(0.35,-0.62,"The retrieval corpus is the screening scope.\nEvery fitted quantity rests on a smaller cohort.",
         fontsize=7.2,color="#5A616C",style="italic",linespacing=1.35)

# ---------------- (b) what the framework emits ----------------
axB.set_xlim(0,10); axB.set_ylim(0,10)
axB.set_title("(b)  Candidate dispatch, by family",fontsize=9,loc="left",pad=6)
fams=[(f["label"],f["total"],f["dispatched"],f["refused"]) for f in C["families"]]
y=8.5
for name,total,disp,ref in fams:
    axB.text(0.2,y+0.52,name,fontsize=8.2,color=INK,va="center")
    scale=8.4/max(f[1] for f in fams)
    axB.add_patch(Rectangle((0.2,y-0.46),disp*scale,0.62,facecolor=OK,alpha=0.85,edgecolor="none",zorder=2))
    axB.add_patch(Rectangle((0.2+disp*scale,y-0.46),ref*scale,0.62,facecolor=REF,alpha=0.75,edgecolor="none",zorder=2))
    axB.add_patch(Rectangle((0.2,y-0.46),total*scale,0.62,facecolor="none",edgecolor=EDGE,lw=0.7,zorder=3))
    axB.text(0.2+total*scale+0.18,y-0.15,f"{disp} / {total}",fontsize=7.8,color="#454C57",va="center")
    y-=2.35
axB.add_patch(Rectangle((0.2,1.30),0.42,0.34,facecolor=OK,alpha=0.85,edgecolor="none"))
axB.text(0.78,1.47,"dispatched: family envelope emitted",fontsize=7.3,color="#454C57",va="center")
axB.add_patch(Rectangle((0.2,0.70),0.42,0.34,facecolor=REF,alpha=0.75,edgecolor="none"))
axB.text(0.78,0.87,"refused: every target hit a refusal gate",fontsize=7.3,color="#454C57",va="center")
axB.text(0.2,0.05,"%d of %d candidate compounds receive at least one prediction."
              % (C["dispatched_compounds"],C["candidate_compounds"]),
         fontsize=7.2,color="#5A616C",style="italic")
fig.savefig("figures/manuscript_figure_1.png",dpi=400,bbox_inches="tight")
fig.savefig("figures/manuscript_figure_1.pdf",bbox_inches="tight")
print("written")
