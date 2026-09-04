"""
manuscript_figure_5.py

Generator for Figure 5 of the manuscript. Family-scope critical-current envelopes, drawn from the per-family Form 3 parameters in data/family_params.json, which analysis/fit_family_params.py regenerates from the dispatch table.

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
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import logging as _logging
# font.family carries fallbacks for other machines, so matplotlib warns
# once per missing family per text element. Several hundred lines that
# look like failures, on a render that succeeded.
_logging.getLogger("matplotlib.font_manager").setLevel(_logging.ERROR)
from matplotlib.lines import Line2D

P=json.load(open("data/family_params.json"))
LAB={"iron_chalcogenide_11":"Iron chalcogenide 11-type",
     "iron_pnictide_122":"Iron pnictide 122-type",
     "conventional_AlB2":r"MgB$_2$-class"}
COL={"iron_chalcogenide_11":"#1B8A7A","iron_pnictide_122":"#D2691E","conventional_AlB2":"#6A5ACD"}
ORDER=["iron_chalcogenide_11","iron_pnictide_122","conventional_AlB2"]
# Half the median 95% interval width across the predictions the dispatch
# actually emits. An earlier version used 0.194, half of 0.39 dex. A note here
# said 0.39 came from a pre-gate population of 1671 rows carrying an emitted or
# a withheld value; that was wrong and gives 0.379. It came from the same
# emission test applied before the reduced-field gate and the withdrawals: at
# commit 8ad8d43 that returned 1386 rows with a median full width of 0.388328
# dex, half 0.194, antilog 2.445, which is the 0.39, 0.19 and 2.5 the documents
# printed. On the 256 rows the gate emits it is 0.825 dex. Recomputed from the
# deposit rather than restated, so it moves with the cohort.
import pandas as _pd, os as _os
_p = _pd.read_csv(_os.path.join("data", "phase_3_p57_de_novo_predictions.csv"),
                  low_memory=False)
_e = _p[_p.refusal_flag.fillna("") == ""]
_EM = _e   # the emitted set, used again below to mark the grid
HALF = float((_e.predicted_log_Jc_upper_95 - _e.predicted_log_Jc_lower_95).median()) / 2
H_MIN_VALID=0.30                # field-axis applicability bound, Eq. (1)
T_MAX_VALID=0.70                # temperature-axis applicability bound, Eq. (1)
H_REF=0.50                      # reduced field for the left panel, inside the window

plt.rcParams.update({"font.family":"serif","font.size":9,"axes.linewidth":0.8,
                     "xtick.direction":"in","ytick.direction":"in",
                     "xtick.top":True,"ytick.right":True,"mathtext.fontset":"dejavuserif"})
fig,(axL,axR)=plt.subplots(1,2,figsize=(7.1,3.15))

# ---------------- left: temperature dependence at fixed reduced field ----------------
t=np.linspace(0.02,0.95,400)
for k in ORDER:
    p=P[k]
    y=p["logJc_T"]+p["beta_T"]*np.log10(1-t)+p["beta_H"]*np.log10(1-H_REF)-p["beta_H"]*np.log10(1-p["H0"]/p["Hc2"])
    ok=t<=T_MAX_VALID
    axL.plot(t[ok],y[ok],color=COL[k],lw=1.6,zorder=3)
    axL.plot(t[~ok],y[~ok],color=COL[k],lw=1.2,ls=(0,(4,2)),zorder=3)
    axL.fill_between(t[ok],y[ok]-HALF,y[ok]+HALF,color=COL[k],alpha=0.15,lw=0,zorder=1)
axL.axvspan(T_MAX_VALID,0.95,color="0.90",zorder=0)
axL.text(0.815,0.055,"outside\nwindow",transform=axL.transAxes,ha="center",va="bottom",
         fontsize=7,color="0.35",linespacing=1.15)
axL.set_xlabel(r"Reduced temperature $T/T_c$")
axL.set_ylabel(r"$\log_{10} J_c$  (A cm$^{-2}$)")
axL.set_xlim(0,0.95); axL.set_title(rf"(a)  at $H/H_{{c2,0}} = {H_REF:.1f}$",fontsize=9,loc="left")

# ---------------- right: field dependence over the validated window ----------------
h=np.linspace(0.001,0.95,500)
for k in ORDER:
    p=P[k]
    y=p["logJc_H"]+p["beta_H"]*np.log10(1-h)
    val=h>=H_MIN_VALID
    axR.plot(h[val],y[val],color=COL[k],lw=1.6,zorder=3)
    axR.plot(h[~val],y[~val],color=COL[k],lw=1.2,ls=(0,(4,2)),zorder=3)
    axR.fill_between(h[val],y[val]-HALF,y[val]+HALF,color=COL[k],alpha=0.15,lw=0,zorder=1)
    for HT in (0.1,1.0,5.0):                       # the dispatch grid
        hh=HT/p["Hc2"]
        # Filled where the dispatch actually emits, open where it refuses.
        # Read from the deposited table rather than assumed: after the
        # reduced-field and reduced-temperature gates only one family and one
        # field survive, and drawing every grid point identically said the
        # opposite.
        live=bool(len(_EM[(_EM.substructure==k)&(np.isclose(_EM.H_T,HT))]))
        axR.plot(hh,p["logJc_H"]+p["beta_H"]*np.log10(1-hh),marker="o",ms=3.4,
                 mfc=COL[k] if live else "white",mec=COL[k],mew=1.1,zorder=4)
axR.axvspan(0,H_MIN_VALID,color="0.90",zorder=0)
axR.text(0.145,0.055,"refused:\nbelow the bound",transform=axR.transAxes,ha="center",va="bottom",
         fontsize=7,color="0.35",linespacing=1.15)
axR.axvline(H_MIN_VALID,color="0.45",lw=0.7,ls=":",zorder=2)
axR.set_xlabel(r"Reduced field $H/H_{c2,0}$")
axR.set_xlim(0,0.95); axR.set_title(r"(b)  at 4.2 K",fontsize=9,loc="left")
axR.tick_params(labelleft=False)
ylo=min(axL.get_ylim()[0],3.1); yhi=6.35
axL.set_ylim(ylo,yhi); axR.set_ylim(ylo,yhi)
axR.plot([0.589],[5.463],marker="x",ms=5,mew=1.2,color="0.25",zorder=5)
axR.annotate("ordering reverses",xy=(0.589,5.463),xytext=(0.40,6.05),fontsize=7,color="0.25",
             arrowprops=dict(arrowstyle="-",lw=0.6,color="0.45"))

handles=[Line2D([],[],color=COL[k],lw=1.6,label=LAB[k]) for k in ORDER]
handles+=[Line2D([],[],color="0.35",lw=1.2,ls=(0,(4,2)),label="outside applicability window"),
          Line2D([],[],color="0.35",lw=0,marker="o",ms=3.4,mfc="0.35",mec="0.35",label="dispatched grid point"),
          Line2D([],[],color="0.35",lw=0,marker="o",ms=3.4,mfc="white",mec="0.35",label="grid point refused")]
fig.legend(handles=handles,loc="lower center",ncol=3,frameon=False,fontsize=7.6,
           bbox_to_anchor=(0.5,-0.055),columnspacing=1.5,handletextpad=0.6)
fig.tight_layout(rect=[0,0.055,1,1])
fig.savefig("figures/manuscript_figure_5.png",dpi=400,bbox_inches="tight")
fig.savefig("figures/manuscript_figure_5.pdf",bbox_inches="tight")
print("written")
for k in ORDER:
    p=P[k]
    lo=p["logJc_H"]+p["beta_H"]*np.log10(1-0.30); hi=p["logJc_H"]+p["beta_H"]*np.log10(1-0.90)
    print(f"  {LAB[k]:28s} beta_H={p['beta_H']:.2f}  drop across the validated window 0.3->0.9: {lo-hi:.2f} dex")
