"""
test_figure_layout.py

Negative controls for analysis/figure_layout.py.

A checker that has only ever been run on figures that pass tells you nothing.
An independent review mutated figure_layout.py fifteen ways and eleven of the
mutations went undetected by the figures themselves, because nothing in the
repository was near a boundary and nothing asserted that the check fires. Each
test below plants a defect the checker must catch, and the last one plants the
mutations themselves.

Run from the repository root:
    python3 analysis/test_figure_layout.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figure_layout import Layout, new_figure                     # noqa: E402

FAILED = []


def case(name, build, must_fire):
    """Build a figure, check it, and require the expected verdict."""
    fired, msg = False, ""
    try:
        build()
    except SystemExit as e:
        fired, msg = True, str(e)
    ok = fired == must_fire
    print("   %-52s %s%s" % (name, "ok" if ok else "FAILED",
                             "" if ok else
                             ("  (fired: %s)" % msg[:70] if fired
                              else "  (did not fire)")))
    if not ok:
        FAILED.append(name)


def _fig(pad=0.25):
    return new_figure(6, 4, 100, 100, "#FFFFFF", pad=pad)


def too_wide():
    fig, ax, L = _fig()
    L.box(10, 40, 30, 10, "#EEE", name="narrow")
    L.txt(25, 45, "a line far too long for a box thirty units wide", size=9)
    L.check()


def too_tall():
    fig, ax, L = _fig()
    L.box(10, 40, 60, 4, "#EEE", name="short")
    L.txt(40, 42, "two\nlines", size=9)
    L.check()


def fits():
    fig, ax, L = _fig()
    L.box(10, 40, 60, 12, "#EEE", name="roomy")
    L.txt(40, 45, "short", size=9)
    L.check()


def clears_by_less_than_the_margin():
    """A string inside the box but within pad of its edge must still fire.

    This is the case a zero-margin check passes and the saved file fails,
    because glyph advances round differently at the dpi savefig uses.
    """
    fig, ax, L = _fig(pad=2.0)
    L.box(10, 40, 60, 12, "#EEE", name="roomy")
    L.txt(40, 45, "a string that clears the box by about one unit each side",
          size=9)
    L.check()


def measure(text, size, xlim=100, ylim=100):
    """Width and height of one string, in data units, at this figure size.

    Fixtures are built from this rather than guessed. An independent review
    found that every fixture in this repository sat far from the boundary it
    was meant to test, which is why eleven of fifteen mutations survived: a
    gross violation fires whatever the check has been loosened to.
    """
    fig, ax, L = new_figure(6, 4, xlim, ylim, "#FFFFFF", pad=0.0)
    a = L.txt(xlim / 2.0, ylim / 2.0, text, size=size)
    fig.canvas.draw()
    bb = a.get_window_extent(renderer=fig.canvas.get_renderer())
    inv = ax.transData.inverted()
    (x0, y0) = inv.transform((bb.x0, bb.y0))
    (x1, y1) = inv.transform((bb.x1, bb.y1))
    return abs(x1 - x0), abs(y1 - y0)


LABEL = "a label placed against the boundary"
W, H = measure(LABEL, 9)


def circle_corner_outside():
    """The defect the review demonstrated: corners outside, centre inside.

    The radius is chosen from the measured string so that the chord at the
    label's centre line admits it and the chord at its corners does not. That
    is the only band in which the two rules disagree, and a fixture outside it
    tests nothing.
    """
    fig, ax, L = _fig(pad=0.0)
    cx, cy = 50.0, 50.0
    y_lo, y_hi = 50.0 + H / 2 - H, 50.0 + H / 2
    mid = (y_lo + y_hi) / 2.0
    # Want: half-chord at mid > W/2 > half-chord at the far edge.
    far = max(abs(y_lo - cy), abs(y_hi - cy))
    want = (W / 2.0) ** 2 + (far ** 2 + (mid - cy) ** 2) / 2.0
    r = want ** 0.5
    L.circle_region(cx, cy, r, y_lo, y_hi, "circle")
    L.txt(cx, mid, LABEL, size=9)
    L.check()


def circle_rule_is_the_tighter_one():
    """circle_region must be strictly narrower than the mid-chord rule."""
    fig, ax, L = _fig(pad=0.0)
    cx, cy, r = 50.0, 50.0, 25.0
    L.circle_region(cx, cy, r, 58.0, 62.0, "inscribed")
    x, y, w, h, _ = L.boxes[-1]
    mid_half = (r * r - (60.0 - cy) ** 2) ** 0.5
    if not w < 2 * mid_half:
        raise SystemExit("circle_region is not tighter than the mid-chord "
                         "rule: %g vs %g" % (w, 2 * mid_half))


def taper_uses_the_narrow_edge():
    """A tapering shape gets its narrowest width, not its widest."""
    fig, ax, L = _fig(pad=0.0)

    def half_at(y):
        # wide at the bottom of the band, narrow at the top
        return (W / 2.0 + 1.0) - (y - 40.0) * 1.0

    L.band_region(50, half_at, 40.0, 42.0, "taper")
    L.txt(50, 41.0, LABEL, size=9)
    L.check()


def empty_is_not_a_pass():
    fig, ax, L = _fig()
    L.box(10, 40, 60, 12, "#EEE", name="roomy")
    L.check()


def counts_are_asserted():
    fig, ax, L = _fig()
    L.box(10, 40, 60, 12, "#EEE", name="roomy")
    L.txt(40, 45, "short", size=9)
    L.check(expect_texts=2)             # there is one; the assertion must fire


def mutations():
    """Plant the review's semantic mutations and require each to be caught.

    A mutation is caught when a figure that passes unmutated fails mutated, or
    a figure that fails unmutated passes mutated. Both directions count: a
    mutation that silently loosens the check is exactly as bad as one that
    breaks it loudly.
    """
    import figure_layout as F

    # Fixtures one unit either side of the boundary, built from the measured
    # string, so a loosened check changes the verdict.
    def nested(inner_w):
        fig, ax, L = _fig(pad=0.0)
        L.box(5, 30, 90, 40, "#EEE", name="outer")
        L.box(50 - inner_w / 2.0, 40, inner_w, 12, "#DDD", name="inner")
        L.txt(50, 45, LABEL, size=9)
        L.check()

    def build_pass():
        nested(W + 2.0)

    def build_fail():
        nested(W - 2.0)

    def verdict(build):
        try:
            build()
            return "pass"
        except SystemExit:
            return "fire"

    base = (verdict(build_pass), verdict(build_fail))
    if base != ("pass", "fire"):
        print("   %-52s FAILED  (baseline is %s)" % ("mutation baseline",
                                                     base))
        FAILED.append("mutation baseline")
        return

    original = F.Layout.check
    src_innermost = F.Layout._innermost
    muts = {}

    def mut_pad(self, *a, **k):
        self.pad = 5.0
        return original(self, *a, **k)
    muts["pad loosened to 5"] = mut_pad

    def mut_outermost(self, *a, **k):
        def outer(x, y):
            hit = [b for b in self.boxes
                   if b[0] <= x <= b[0] + b[2] and b[1] <= y <= b[1] + b[3]]
            return max(hit, key=lambda b: b[2] * b[3]) if hit else None
        self._innermost = outer
        try:
            return original(self, *a, **k)
        finally:
            self._innermost = src_innermost.__get__(self)
    muts["outermost box wins"] = mut_outermost

    for name, fn in muts.items():
        F.Layout.check = fn
        got = (verdict(build_pass), verdict(build_fail))
        F.Layout.check = original
        caught = got != base
        print("   %-52s %s" % ("mutation caught: " + name,
                               "ok" if caught else "FAILED  (survived)"))
        if not caught:
            FAILED.append("mutation " + name)


def main():
    print("figure_layout negative controls\n")
    case("a string wider than its box fires", too_wide, True)
    case("a string taller than its box fires", too_tall, True)
    case("a string that fits does not fire", fits, False)
    case("clearing by less than the margin fires",
         clears_by_less_than_the_margin, True)
    case("a circle label whose corners leave the circle fires",
         circle_corner_outside, True)
    case("circle_region is tighter than the mid-chord rule",
         circle_rule_is_the_tighter_one, False)
    case("a taper is credited with its narrow edge",
         taper_uses_the_narrow_edge, True)
    case("a figure with no recorded text is not a pass",
         empty_is_not_a_pass, True)
    case("a wrong expected count fires", counts_are_asserted, True)
    print()
    mutations()
    print()
    if FAILED:
        print("   %d control(s) failed: %s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("   every control behaved as required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
