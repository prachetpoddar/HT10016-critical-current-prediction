"""
manuscript_figure_4.py

Generator for Figure 4 of the manuscript. Anchor-count sensitivity in the external cuprate validation. Every value is hardcoded from that validation and does not depend on the fitted cohort, so this figure is unchanged by the record withdrawals.

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
import numpy as np

plt.rcParams.update({"font.family":"serif","font.size":9,"mathtext.fontset":"dejavuserif"})
INK="#1A1D23"; OK="#1B8A7A"; GREY="#7A828E"; ACC="#3B4A8C"

fig,ax=plt.subplots(figsize=(3.5,3.3))

# values recovered from the pipeline's own artwork and cross-checked against the text
K1_all,   K1_all_lo,   K1_all_hi   = 1.592, 1.192, 2.234   # four held-out cuprates
K1_match                            = 1.267                 # matched three monotonic cuprates
K3,       K3_lo,       K3_hi        = 0.927, 0.765, 1.094   # three monotonic cuprates
TC_ONLY, IN_CORPUS                  = 1.166, 0.567

ax.axhline(TC_ONLY, ls=(0,(6,3)), lw=1.0, color=GREY, zorder=1)
ax.axhline(IN_CORPUS, ls=(0,(1.5,2.5)), lw=1.0, color=GREY, zorder=1)
ax.text(3.42, TC_ONLY*1.03, "$T_c$-only baseline", fontsize=7.4, color="#5A616C", ha="right", va="bottom")
ax.text(3.42, IN_CORPUS*1.03, "in-corpus baseline", fontsize=7.4, color="#5A616C", ha="right", va="bottom")

# four-compound K = 1, the cohort-mismatched starting point
ax.errorbar([1],[K1_all], yerr=[[K1_all-K1_all_lo],[K1_all_hi-K1_all]],
            fmt="o", ms=7, mfc="white", mec=OK, ecolor=OK, elinewidth=1.2,
            capsize=4, capthick=1.2, zorder=3)
ax.text(0.88, K1_all, "all four\nheld out", fontsize=7.4, color="#454C57", va="center", ha="right", linespacing=1.3)

# matched three-compound K = 1 and K = 3, the comparison the paper carries
ax.plot([1,3],[K1_match,K3], "-", lw=1.8, color=OK, zorder=2)
ax.errorbar([3],[K3], yerr=[[K3-K3_lo],[K3_hi-K3]],
            fmt="o", ms=7, mfc=OK, mec=OK, ecolor=OK, elinewidth=1.2,
            capsize=4, capthick=1.2, zorder=3)
ax.plot([1],[K1_match],"o",ms=7,mfc=OK,mec=OK,zorder=3)
ax.text(0.88, K1_match, "matched\ncohort", fontsize=7.4, color="#454C57", va="center", ha="right", linespacing=1.3)

ax.annotate("26.8% reduction\non the matched cohort",
            xy=(2.0, np.sqrt(K1_match*K3)), xytext=(2.15, 1.80),
            fontsize=7.8, color=ACC, ha="center", va="center", linespacing=1.35,
            arrowprops=dict(arrowstyle="-|>", lw=0.9, color=ACC, shrinkA=4, shrinkB=4,
                            connectionstyle="arc3,rad=0.15"))

ax.set_xlim(0.38,3.55); ax.set_xticks([1,3]); ax.set_xticklabels(["1","3"])
ax.set_yscale("log"); ax.set_ylim(0.45,2.45)
ax.set_yticks([0.5,0.7,1.0,1.5,2.0]); ax.set_yticklabels(["0.5","0.7","1.0","1.5","2.0"])
ax.minorticks_off()
ax.set_xlabel("Anchor count $K$")
ax.set_ylabel(r"Pooled $L_1$ error in $\beta_H$  (dimensionless)")
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.spines["left"].set_color("#555B66"); ax.spines["bottom"].set_color("#555B66")
ax.tick_params(colors="#555B66", labelcolor=INK)

fig.tight_layout()
fig.savefig("figures/manuscript_figure_4.png", dpi=400, bbox_inches="tight")
fig.savefig("figures/manuscript_figure_4.pdf", bbox_inches="tight")
print("written")
