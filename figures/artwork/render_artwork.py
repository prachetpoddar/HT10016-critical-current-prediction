"""
render_artwork.py

Renders figures/artwork/*.svg to the PNGs the deposit carries.

Two steps, and the second one matters as much as the first. The SVG is drawn in
headless Chromium at 3000 px wide, then the PNG is trimmed to the drawing and
re-padded by a uniform margin on all four sides.

Without the trim, Figure 2 sits off-centre inside its own frame: its canvas
carries 456 px of empty white on the right against none on the left, so the
drawing looks off-centre on the page however the paragraph is aligned. The
trim was dropped when this script was rewritten and is restored here.

"The drawing" is every pixel that is neither white nor the canvas background,
which for Figure 1 is the same thing (its canvas is white) and for Figure 2
excludes both the pale-yellow field and the empty white band beside it. The
pad is then laid down in the canvas colour, so Figure 2 keeps a yellow border
and Figure 1 a white one.

Render with Helvetica available, or with a metric clone: fc-match Helvetica
should not fall through to a default sans. Nimbus Sans is a metric clone and is
what this container resolves to.

TARGET is the size each figure came out at when it was last rendered with the
trim in place. A change here is not an error, because a label that got longer
moves the drawing's bounding box, but it should be a change you meant.
"""
import asyncio
import pathlib
import re

import numpy as np
from PIL import Image
from playwright.async_api import async_playwright

WIDTH = 3000
FIGURES = [
    # svg, png, uniform pad in px, size when last rendered with the trim
    ("manuscript_figure_1.svg", "manuscript_figure_1.png", 84, (3036, 2019)),
    ("manuscript_figure_2.svg", "manuscript_figure_2.png", 40, (2584, 2145)),
]
WHITE = (255, 255, 255)
TOL = 12


def trim_and_pad(path, pad):
    """Crop to the drawing, then re-pad by `pad` px of the canvas colour."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    canvas = tuple(int(v) for v in a[0, 0])
    off_white = np.abs(a - np.array(WHITE)).sum(axis=2) > TOL
    off_canvas = np.abs(a - np.array(canvas)).sum(axis=2) > TOL
    ys, xs = np.where(off_white & off_canvas)
    if not len(xs):
        raise SystemExit("%s: nothing but background was rendered" % path)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    drawing = im.crop(box)
    out = Image.new("RGB", (drawing.width + 2 * pad, drawing.height + 2 * pad),
                    canvas)
    out.paste(drawing, (pad, pad))
    out.save(path)
    return out.size, canvas


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for src, out, pad, target in FIGURES:
            s = pathlib.Path(src).read_text()
            m = re.search(
                r'viewBox="([\d.\-]+) ([\d.\-]+) ([\d.]+) ([\d.]+)"', s)
            vw, vh = float(m.group(3)), float(m.group(4))
            h = round(WIDTH * vh / vw)
            s = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"', r"\1", s, count=1)
            s = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"', r"\1", s, count=1)
            html = ("<!doctype html><meta charset='utf-8'>"
                    "<style>html,body{margin:0;background:#fff}"
                    "svg{display:block;width:%dpx;height:%dpx}</style>%s"
                    % (WIDTH, h, s))
            pg = await b.new_page(viewport={"width": WIDTH, "height": h})
            await pg.set_content(html, wait_until="networkidle")
            await pg.wait_for_timeout(1200)
            await pg.screenshot(path=out,
                                clip={"x": 0, "y": 0, "width": WIDTH,
                                      "height": h})
            await pg.close()
            size, canvas = trim_and_pad(out, pad)
            note = "" if size == target else "   (was %dx%d)" % target
            print("wrote %-28s %dx%d  pad %d  canvas %s%s"
                  % (out, size[0], size[1], pad, canvas, note))
        await b.close()


asyncio.run(main())
