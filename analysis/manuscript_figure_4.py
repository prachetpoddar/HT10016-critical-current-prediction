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
# The in-corpus baseline of 0.567 that an earlier version drew here has been
# removed. It is not derivable from anything in the deposit, it appeared only
# as this literal and once in the manuscript, and it was drawn on an axis
# carrying dex while being described as an exponent error.
TC_ONLY = 1.166
red = 100*(m1-m3)/m1

fig,ax=plt.subplots(figsize=(3.5,3.3))
ax.axhline(TC_ONLY, ls=(0,(6,3)), lw=1.0, color=GREY, zorder=1)

# the unmatched four-compound pair the earlier version reported, kept visible
ax.plot([1.06,3.06],[f1,f3], "-", lw=1.2, color=GREY, alpha=0.55, zorder=2)
for x,v,lo,hi in ((1.06,f1,f1lo,f1hi),(3.06,f3,f3lo,f3hi)):
    ax.errorbar([x],[v], yerr=[[v-lo],[hi-v]], fmt="s", ms=5, mfc="white",
                mec=GREY, ecolor=GREY, elinewidth=1.0, capsize=3, capthick=1.0,
                alpha=0.8, zorder=3)

# the matched three-compound comparison the paper carries
ax.plot([1,3],[m1,m3], "-", lw=1.9, color=OK, zorder=4)
for x,v,lo,hi in ((1,m1,m1lo,m1hi),(3,m3,m3lo,m3hi)):
    ax.errorbar([x],[v], yerr=[[v-lo],[hi-v]], fmt="o", ms=7, mfc=OK, mec=OK,
                ecolor=OK, elinewidth=1.2, capsize=4, capthick=1.2, zorder=5)

ax.set_xticks([1,3]); ax.set_xlim(0.72,3.66)
ax.set_xlabel("Anchor measurements per candidate, $K$", fontsize=8.6)
# The quantity is |predicted_log_Jc - actual_log_Jc| from
# analysis/external_anchor_count.py, which is dex. An earlier version of this
# label called it an exponent error, which is the convention Sec. II.A sets
# out and which this figure then contradicted.
ax.set_ylabel("Pooled error in log$_{10}$ $J_c$ (dex)", fontsize=8.6)
ax.set_ylim(0.30, 2.45)
ax.tick_params(labelsize=7.8)
for sp in ("top","right"): ax.spines[sp].set_visible(False)

# ---------------------------------------------------------------- labels
# Every in-plot label used to be placed by hand, and two of them sat on a
# line: the matched-cohort label lay across the grey unmatched line, and the
# reduction annotation's arrow crossed both the grey line and the dashed
# baseline on its way down to the teal one. Hossain asked for the arrowed
# text below both lines, pointing at the right line without crossing
# anything, and for no label to touch a line at all.
#
# Hand-fitting that is what produced the overlap in the first place, so the
# placements below are candidates and the figure picks the first one that
# clears every drawn line. The check is on rendered pixels, not on data
# coordinates, so it holds whatever the font metrics do on the machine that
# draws it. If no candidate clears, the run fails rather than shipping a
# label on a line.
LABELS = [
    dict(name="matched",
         text="three monotonic,\nmatched", color="#2E6B60", size=7.4,
         where=[(1.10, 0.92, "left", "top"), (1.10, 0.86, "left", "top"),
                (1.34, 0.92, "left", "top"), (1.10, 2.42, "left", "top")]),
    dict(name="unmatched",
         text="all four,\nunmatched", color="#5A616C", size=7.0,
         where=[(3.14, 0.80, "left", "center"), (3.14, 0.72, "left", "center"),
                (3.64, 1.74, "right", "center")]),
]

# The baseline label is an annotation rather than a plain label. Sitting
# beside the dashed line put it on the upper cap of the four-compound
# uncertainty bound, so it moves up into clear space and points back down at
# the line it names.
BASELINE_PLACES = [((3.18, 1.86), (3.40, 1.19)),
                   ((3.05, 2.05), (3.34, 1.19)),
                   ((2.30, 2.12), (2.62, 1.19)),
                   ((1.45, 2.26), (1.70, 1.19))]
for spec in LABELS:
    spec["artists"] = [
        ax.text(x, y, spec["text"], fontsize=spec["size"], color=spec["color"],
                ha=ha, va=va, linespacing=1.3, zorder=6, visible=False)
        for x, y, ha, va in spec["where"]]

# The arrow now runs straight up from below the teal line to the teal line,
# so it crosses nothing. rad=0 keeps the drawn path identical to the segment
# the overlap check tests.
ARROW_TIP = (2.20, m1 + (m3 - m1) * (2.20 - 1) / 2.0)
ARROW_TEXT = (2.20, 0.52)


def arrowed(text, tip, at, color, size):
    return ax.annotate(text, xy=tip, xytext=at, fontsize=size, color=color,
                       ha="center", va="center", linespacing=1.35, zorder=6,
                       arrowprops=dict(arrowstyle="-|>", lw=0.9, color=color,
                                       shrinkA=5, shrinkB=4,
                                       connectionstyle="arc3,rad=0"))


note = arrowed("%.1f%% reduction\non the matched cohort" % red,
               ARROW_TIP, ARROW_TEXT, ACC, 7.8)
baselines = [arrowed("$T_c$-only baseline", tip, at, "#5A616C", 7.4)
             for at, tip in BASELINE_PLACES]
for b in baselines:
    b.set_visible(False)


def segments(axis):
    """Every drawn line and error bar, in data coordinates.

    axis.get_lines() is NOT enough and the first version of this check used
    only that. errorbar draws its vertical bars as a LineCollection, which
    get_lines() does not return, so the bars were invisible to the check and
    the baseline label sat on an uncertainty bound with the figure reporting
    itself clear. The caps and markers are Line2D and were covered; the bars
    were not. Collections are read here as well.
    """
    out = []
    for line in axis.get_lines():
        if line.get_visible() and len(line.get_xydata()):
            out.append(line.get_xydata())
    for coll in axis.collections:
        if not coll.get_visible():
            continue
        for seg in coll.get_segments():
            if len(seg):
                out.append(seg)
    return out


def drawn_points(axis, n=400):
    """Those segments, as rendered pixel positions."""
    import numpy as _np
    pts = []
    for xy in segments(axis):
        if len(xy) == 1:
            pts.append(axis.transData.transform(xy))
            continue
        for a, b in zip(xy[:-1], xy[1:]):
            t = _np.linspace(0, 1, n)[:, None]
            pts.append(axis.transData.transform(_np.asarray(a)
                                                + (_np.asarray(b) - _np.asarray(a)) * t))
    return _np.vstack(pts) if pts else _np.empty((0, 2))


def clear_of_lines(artist, points, pad=4.0):
    """True when no drawn point falls inside the artist's TEXT box.

    Annotation.get_window_extent returns the text box union the arrow, so
    asking an annotation for its extent reports a box reaching all the way to
    the arrow tip, which by construction touches the line being pointed at.
    The base Text method gives the box the reader sees as text.
    """
    import matplotlib.text as _mtext
    box = _mtext.Text.get_window_extent(
        artist, renderer=fig.canvas.get_renderer())
    return not (((points[:, 0] > box.x0 - pad) & (points[:, 0] < box.x1 + pad) &
                 (points[:, 1] > box.y0 - pad) & (points[:, 1] < box.y1 + pad)).any())


fig.tight_layout()
fig.canvas.draw()
POINTS = drawn_points(ax)
chosen = []
for spec in LABELS:
    for artist, place in zip(spec["artists"], spec["where"]):
        artist.set_visible(True)
        if clear_of_lines(artist, POINTS):
            chosen.append((spec["name"], place))
            break
        artist.set_visible(False)
    else:
        raise SystemExit("no clear placement for the %s label" % spec["name"])

# Each annotation is checked the same way, and so is the segment its arrow
# draws. An arrow may touch only the line it points at, and only at its tip,
# so the sampled span stops short of both ends.
import numpy as _np


def arrow_path(at, tip):
    return _np.vstack([ax.transData.transform(
        _np.array(at) + (_np.array(tip) - _np.array(at)) * t)
        for t in _np.linspace(0.12, 0.88, 200)])


def crosses_anything(path, exclude=None):
    for xy in segments(ax):
        if len(xy) < 2:
            continue
        if exclude is not None and _np.allclose(xy, exclude):
            continue
        px = ax.transData.transform(_np.asarray(xy))
        for a, b in zip(px[:-1], px[1:]):
            d = b - a
            L2 = float(d @ d)
            if L2 == 0:
                continue
            for p in path:
                u = max(0.0, min(1.0, float((p - a) @ d) / L2))
                if _np.hypot(*(a + d * u - p)) < 4.0:
                    return True
    return False


fig.canvas.draw()
if not clear_of_lines(note, POINTS) or crosses_anything(
        arrow_path(ARROW_TEXT, ARROW_TIP)):
    raise SystemExit("the reduction annotation sits on or crosses a line")

for artist, (at, tip) in zip(baselines, BASELINE_PLACES):
    artist.set_visible(True)
    fig.canvas.draw()
    if clear_of_lines(artist, POINTS) and not crosses_anything(
            arrow_path(at, tip)):
        chosen.append(("baseline", at + tip))
        break
    artist.set_visible(False)
else:
    raise SystemExit("no clear placement for the baseline annotation")
print("   label placements: %s" % chosen)
print("   the arrow runs from %.2f to %.2f dex at K = %.2f, crossing nothing"
      % (ARROW_TEXT[1], ARROW_TIP[1], ARROW_TIP[0]))

os.makedirs("figures", exist_ok=True)
# tight_layout already ran before the overlap check. Running it again here
# would move the axes after the placements were verified, so it does not.
# 400 dpi: the image this replaces in the document was 1358 px across a 3.5
# inch figure, so a 300 dpi render would embed at a lower resolution than the
# one it replaces at the same printed size.
fig.savefig(os.path.join("figures","figure_4_anchor_count.png"), dpi=400)
print("written figures/figure_4_anchor_count.png   matched %.3f -> %.3f (%.1f%%)"
      % (m1, m3, red))
