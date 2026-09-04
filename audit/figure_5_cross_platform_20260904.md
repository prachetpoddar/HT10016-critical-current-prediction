# Figure 5 at identical size, two platforms

Recorded 2026-09-04. The measurement that settled why
`analysis/check_figures.py` cannot compare a regenerated figure with the
committed one outside the environment that drew it.

## What was seen

`analysis/check_figures.py` reported, on macOS, at commit `5f05365`:

    Figure 1 regenerates from the current deposit   n/a      2731x1538 here against 2729x1538 committed
    Figure 2 regenerates from the current deposit   n/a      2254x2095 here against 2253x2095 committed
    Figure 5 regenerates from the current deposit   FAILED   max pixel difference 255

The committed PNG is the same blob on both machines
(`c8e0f9c03bcb9fee3dcc94b17bbdb3135128660b`), so the difference is in the
regeneration, and Figure 5's regeneration came out at an identical 2796x1330.
The rule in force was "same size, so compare pixels strictly", which therefore
called the deposit broken.

## The plotted content is identical by construction

`analysis/manuscript_figure_5.py` contains no random number generator: no
seed, no `numpy.random`, no bootstrap, no resampling. It reads
`data/family_params.json` and a small set of module constants and evaluates
Form 3 on a fixed grid. Both machines ran it from the same commit over the
same committed inputs, so the numbers it plots cannot differ. Whatever the
difference is, it is in the drawing.

## Where the differing pixels are

The macOS render was staged and compared against the committed one. Both
2796x1330.

| quantity | value |
|---|---:|
| differing pixels | 40993 of 3718680, 1.10% |
| difference of 1 to 8 out of 255 | 67.2% |
| difference of 33 or more | 4.5% |
| difference of exactly 255 | 2 pixels |
| **differing pixels in a locally flat region of the committed render** | **0** |

The last row is the one that decides it. For every differing pixel, the 3x3
luminance range of the committed render at that pixel is at least 4 out of
255; 89.9% sit where it is above 20. Not one differing pixel lies in a flat
interior. A figure drawn from different numbers moves a filled band or a
marker and therefore differs in flat interiors. A figure drawn from the same
numbers by a renderer that assigns edge coverage slightly differently differs
only on edges, which is what this is.

The two pixels at the full range are at x=1387, y=1197 and y=1198: black in
the committed render, white in the macOS one. That is a glyph stem one pixel
wide, landing on the other side of a pixel boundary.

## The mechanism is broader than text

34.0% of the differing pixels are coloured (saturation above 24 in one render
or the other), with a median difference of 5 and a maximum of 216. Those are
the family curves and the alpha-blended interval bands, which are drawn by
Agg's path rasteriser and never touch freetype. The remaining 27074 are grey
or black, median 3, and include the glyph edges.

So the earlier account, that this is freetype rasterising glyphs differently,
named only part of it. Both the glyph rasteriser and the path rasteriser
assign edge coverage differently between the two platform builds, and text is
merely where it shows up as a size change as well, because matplotlib saves
with `bbox_inches="tight"` and sizes the canvas from rendered text extents.

## Two explanations ruled out by measurement

- **matplotlib version.** 3.8.4 and 3.10.9 were installed side by side on the
  Linux machine and give byte-identical output for Figures 1, 2 and 5.
- **Font resolution.** Pinning `font.family` to the bundled DejaVu Serif did
  not change the macOS output.

## What was done

`figures/render_env.json` records the system, matplotlib version and freetype
version that drew the committed PNGs. The regeneration check compares pixels
only where that matches and reports `n/a` elsewhere, with the numbers and the
differing fields. What that gives up is stated in the README: away from the
recording machine, a figure that has genuinely gone stale is reported as not
comparable rather than as a failure, so long as its size stays within 1%. The
document comparison compares two committed artifacts rather than a fresh
render and is unaffected.
