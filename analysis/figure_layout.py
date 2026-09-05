"""
figure_layout.py

Measure every piece of text in a figure against the box it sits in, and refuse
to write the figure if any of it hangs outside.

Why this exists. Text overflow in these figures was found by looking at the
render, three times, and twice it survived a look. A string is laid out by the
font engine at draw time, so its width is not knowable from the source: a
caption that fits at one font size or in one matplotlib version does not fit
in another, and nothing in the generator notices. The document checker cannot
help, because it reads word/document.xml and can never see inside an image.

How it decides which box a text belongs to. The innermost box whose rectangle
contains the text's anchor point. That matches how these figures are written,
where a caption is placed inside the panel it describes, and it needs no
annotation at the call site, so it cannot fall out of step with the drawing
code the way a hand-maintained mapping would. Text anchored outside every box,
such as an arrow label in the gutter between panels, is unconstrained here and
is checked against the figure edge instead.

Usage:

    from figure_layout import Layout
    L = Layout(fig, ax)
    ... L.box(...) and L.txt(...) instead of the local helpers ...
    L.check()          # raises SystemExit listing every overflow
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


class Layout(object):
    """Records boxes and texts, then checks that the texts fit."""

    def __init__(self, fig, ax, pad=0.0):
        self.fig = fig
        self.ax = ax
        # Negative slack: the text must clear the box by this much. Glyph
        # advances are rounded to integer device pixels, so the same string
        # measures up to about 0.35 data units wider or narrower between the
        # dpi the check runs at and the dpi savefig writes at. A margin of
        # half that, on each side, is what keeps a pass at check time from
        # becoming an overflow in the file.
        self.pad = pad
        self.boxes = []         # (x, y, w, h, name)
        self.texts = []         # (artist, anchor_xy, label)

    # ---------------------------------------------------------------- draw
    def box(self, x, y, w, h, fc, ec="#9A9A9A", lw=0.9, r=0.9, z=2, ls="-",
            name=None, check=True):
        self.ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0,rounding_size=%.2f" % r,
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z, linestyle=ls))
        if check:
            self.boxes.append((x, y, w, h, name or "box at (%g, %g)" % (x, y)))

    def region(self, x, y, w, h, name):
        """Record a constraint rectangle without drawing anything.

        For the places where the shape that has to contain the text is not a
        drawn box: the text-safe inset of a panel whose border the prose must
        not touch, or a rectangle inscribed in a curved shape.
        """
        self.boxes.append((x, y, w, h, name))

    def circle_region(self, cx, cy, r, y_lo, y_hi, name):
        """The largest rectangle inside a circle spanning y_lo to y_hi.

        The half-width is taken at whichever of the two edges is further from
        the centre, not at the middle. An independent review found that taking
        it at the middle passes text whose top corners sit outside the circle
        by more than the radius: on a circle of radius 25 it accepted corners
        at 25.61. Every circle label in Figure 1 was registered that way.
        """
        far = max(abs(y_lo - cy), abs(y_hi - cy))
        if far >= r:
            raise SystemExit("%s: the label band %g to %g leaves the circle "
                             "at radius %g outright" % (name, y_lo, y_hi, r))
        half = (r * r - far * far) ** 0.5
        self.boxes.append((cx - half, y_lo, 2 * half, y_hi - y_lo, name))

    def band_region(self, cx, half_at, y_lo, y_hi, name):
        """A rectangle inside a shape centred on cx whose half-width is
        half_at(y).

        The half-width is evaluated at both edges and the narrower is used, so
        a tapering shape is never credited with width it does not have at the
        height the glyphs actually reach.
        """
        half = min(half_at(y_lo), half_at(y_hi))
        self.boxes.append((cx - half, y_lo, 2 * half, y_hi - y_lo, name))

    def txt(self, x, y, s, size=7.2, weight="normal", color="#1A1A1A",
            ha="center", va="center", z=5, style="normal", rot=0,
            check=True):
        a = self.ax.text(x, y, s, fontsize=size, fontweight=weight,
                         color=color, ha=ha, va=va, zorder=z, style=style,
                         linespacing=1.35, rotation=rot,
                         rotation_mode="anchor")
        if check:
            self.texts.append((a, (x, y), s.replace("\n", " / ")))
        return a

    # --------------------------------------------------------------- check
    def _innermost(self, x, y):
        """The smallest recorded box containing (x, y), or None."""
        hit = [b for b in self.boxes
               if b[0] <= x <= b[0] + b[2] and b[1] <= y <= b[1] + b[3]]
        if not hit:
            return None
        return min(hit, key=lambda b: b[2] * b[3])

    def check(self, expect_texts=None, expect_boxes=None):
        """Raise SystemExit listing every text that leaves its box.

        expect_texts and expect_boxes are asserted when given. Without them a
        mutation that stops recording texts reports "0 text runs checked, none
        overflowing" and passes, which an independent review demonstrated.
        """
        if expect_texts is not None and len(self.texts) != expect_texts:
            raise SystemExit("expected %d recorded texts, have %d: something "
                             "stopped recording" % (expect_texts,
                                                    len(self.texts)))
        if expect_boxes is not None and len(self.boxes) != expect_boxes:
            raise SystemExit("expected %d recorded boxes, have %d: something "
                             "stopped recording" % (expect_boxes,
                                                    len(self.boxes)))
        if not self.texts:
            raise SystemExit("no text was recorded; the check is vacuous")
        self.fig.canvas.draw()
        rend = self.fig.canvas.get_renderer()
        inv = self.ax.transData.inverted()
        bad = []
        for art, (ax_, ay), label in self.texts:
            bb = art.get_window_extent(renderer=rend)
            (x0, y0) = inv.transform((bb.x0, bb.y0))
            (x1, y1) = inv.transform((bb.x1, bb.y1))
            x0, x1 = min(x0, x1), max(x0, x1)
            y0, y1 = min(y0, y1), max(y0, y1)
            box = self._innermost(ax_, ay)
            if box is None:
                # No box: the figure's own limits are the constraint.
                lo_x, hi_x = self.ax.get_xlim()
                lo_y, hi_y = self.ax.get_ylim()
                bx, by, bw, bh, name = lo_x, lo_y, hi_x - lo_x, hi_y - lo_y, \
                    "the figure"
            else:
                bx, by, bw, bh, name = box
            p = self.pad
            over = []
            if x0 < bx - p:
                over.append("left by %.2f" % (bx - x0))
            if x1 > bx + bw + p:
                over.append("right by %.2f" % (x1 - bx - bw))
            if y0 < by - p:
                over.append("below by %.2f" % (by - y0))
            if y1 > by + bh + p:
                over.append("above by %.2f" % (y1 - by - bh))
            if over:
                bad.append("   %-58s %s: %s"
                           % ('"' + label[:56] + '"', name, ", ".join(over)))
        if bad:
            raise SystemExit(
                "text leaves its box in %d place(s):\n%s"
                % (len(bad), "\n".join(bad)))
        return len(self.texts), len(self.boxes)


def new_figure(w_in, h_in, xlim, ylim, canvas, font="DejaVu Sans", size=7.2,
               pad=0.25, dpi=300):
    """A figure, an axes filling it, a painted canvas, and a Layout.

    figure.dpi is pinned because the check measures on the live canvas and
    savefig re-renders: glyph advances round to integer device pixels, so the
    same string measures 42.06 units at 72 dpi and 42.43 at 300. Measuring at
    the dpi the file is written at removes that gap, and Layout's pad covers
    what is left.
    """
    plt.rcParams.update({"font.family": [font], "font.size": size,
                         "figure.dpi": dpi})
    fig = plt.figure(figsize=(w_in, h_in))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, xlim)
    ax.set_ylim(0, ylim)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), xlim, ylim, boxstyle="square,pad=0",
                                facecolor=canvas, edgecolor="none", zorder=0))
    return fig, ax, Layout(fig, ax, pad=-abs(pad))
