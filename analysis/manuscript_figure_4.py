"""
manuscript_figure_4.py

Generator for Figure 4 of the manuscript. Anchor-count sensitivity in the
external cuprate validation.

Every value is now read from audit/external_anchor_count.csv, which
analysis/external_anchor_count.py computes from the deposited prediction files,
rather than hardcoded. An earlier version of this script carried the comment
that its numbers were "recovered from the pipeline's own artwork and
cross-checked against the text", which was true and is not a provenance a paper
about provenance should ship: the confidence intervals in particular existed in
no script and no table anywhere in the workflow.

What changed in the figure itself. The K = 3 point was 0.927, described in the
caption as the error across the three monotonic cuprates after the non-monotonic
one is refused. That number is the pooled error across all four, the refused one
included. The carried comparison is now the matched three-compound one, 1.267 at
one anchor to 0.694 at three, a 45.2% reduction. The four-compound pair is drawn
faintly beside it, labelled as unmatched, because it is what the earlier version
reported and a reader should be able to see the difference rather than be told
about it.

Figure-to-script mapping for this deposit, because the names do not line up on
their own and using the wrong script produces a figure in a different visual
style that still looks plausible:

    Fig. 1  analysis/manuscript_figure_1.py
    Fig. 2  analysis/manuscript_figure_2.py
    Fig. 3  analysis/figure_4_source.py      (also the variance-decomposition library)
    Fig. 4  analysis/manuscript_figure_4.py
    Fig. 5  analysis/manuscript_figure_5.py  (reads data/family_params.json)
    Fig. S1 analysis/manuscript_figure_s1_extraction_examples.py

Run from the repository root; writes into figures/.
"""
import os
import subprocess
import sys

import matplotlib; matplotlib.use("Agg")
import logging as _logging
# font.family carries fallbacks for other machines, so matplotlib warns
# once per missing family per text element. Several hundred lines that
# look like failures, on a render that succeeded.
_logging.getLogger("matplotlib.font_manager").setLevel(_logging.ERROR)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({"font.family":"serif","font.size":9,"mathtext.fontset":"dejavuserif"})
INK="#1A1D23"; OK="#1B8A7A"; GREY="#7A828E"; ACC="#3B4A8C"

SRC = os.path.join("audit", "external_anchor_count.csv")
if not os.path.exists(SRC):
    subprocess.run([sys.executable, os.path.join("analysis",
                    "external_anchor_count.py")], check=True)
t = pd.read_csv(SRC).set_index("cohort")
m3, m3lo, m3hi = t.loc["K=3, three monotonic", ["mae","ci_lo","ci_hi"]]
m1 = t.loc["K=1, three monotonic", "mae"]
m1lo, m1hi = t.loc["K=1, three monotonic", ["ci_lo","ci_hi"]]
f1, f1lo, f1hi = t.loc["K=1, all four", ["mae","ci_lo","ci_hi"]]
f3, f3lo, f3hi = t.loc["K=3, all four", ["mae","ci_lo","ci_hi"]]
TC_ONLY, IN_CORPUS = 1.166, 0.567
red = 100*(m1-m3)/m1

fig,ax=plt.subplots(figsize=(3.5,3.3))
ax.axhline(TC_ONLY, ls=(0,(6,3)), lw=1.0, color=GREY, zorder=1)
ax.axhline(IN_CORPUS, ls=(0,(1.5,2.5)), lw=1.0, color=GREY, zorder=1)
ax.text(1.42, TC_ONLY*1.02, "$T_c$-only baseline", fontsize=7.4, color="#5A616C", ha="left", va="bottom")
ax.text(1.42, IN_CORPUS*1.02, "in-corpus baseline", fontsize=7.4, color="#5A616C", ha="left", va="bottom")

# the unmatched four-compound pair the earlier version reported, kept visible
ax.plot([1.06,3.06],[f1,f3], "-", lw=1.2, color=GREY, alpha=0.55, zorder=2)
for x,v,lo,hi in ((1.06,f1,f1lo,f1hi),(3.06,f3,f3lo,f3hi)):
    ax.errorbar([x],[v], yerr=[[v-lo],[hi-v]], fmt="s", ms=5, mfc="white",
                mec=GREY, ecolor=GREY, elinewidth=1.0, capsize=3, capthick=1.0,
                alpha=0.8, zorder=3)
ax.text(3.14, f3*0.86, "all four,\nunmatched", fontsize=7.0, color="#5A616C",
        va="center", ha="left", linespacing=1.3)

# the matched three-compound comparison the paper carries
ax.plot([1,3],[m1,m3], "-", lw=1.9, color=OK, zorder=4)
for x,v,lo,hi in ((1,m1,m1lo,m1hi),(3,m3,m3lo,m3hi)):
    ax.errorbar([x],[v], yerr=[[v-lo],[hi-v]], fmt="o", ms=7, mfc=OK, mec=OK,
                ecolor=OK, elinewidth=1.2, capsize=4, capthick=1.2, zorder=5)
ax.text(1.16, m1*1.20, "three monotonic,\nmatched", fontsize=7.4, color="#2E6B60",
        va="bottom", ha="left", linespacing=1.3)

ax.annotate("%.1f%% reduction\non the matched cohort" % red,
            xy=(2.0, np.sqrt(m1*m3)), xytext=(2.30, 1.90),
            fontsize=7.8, color=ACC, ha="center", va="center", linespacing=1.35,
            arrowprops=dict(arrowstyle="-|>", lw=0.9, color=ACC, shrinkA=4, shrinkB=4,
                            connectionstyle="arc3,rad=0.15"))

ax.set_xticks([1,3]); ax.set_xlim(0.72,3.66)
ax.set_xlabel("anchor measurements per candidate, $K$", fontsize=8.6)
ax.set_ylabel("pooled error in the field exponent", fontsize=8.6)
ax.set_ylim(0.30, 2.45)
ax.tick_params(labelsize=7.8)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
os.makedirs("figures", exist_ok=True)
fig.tight_layout()
fig.savefig(os.path.join("figures","figure_4_anchor_count.png"), dpi=300)
print("written figures/figure_4_anchor_count.png   matched %.3f -> %.3f (%.1f%%)"
      % (m1, m3, red))
