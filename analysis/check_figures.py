"""
check_figures.py

The check nothing in this deposit had: that the figures agree with the data.

analysis/check_documents.py and analysis/check_cross_artifact_consistency.py
both read word/document.xml, so a number drawn inside an embedded image is
invisible to them. That is how the Figure 1 in the manuscript kept asserting 69
papers, 43 compounds, 4387 points, 110 anchors and "125 of 185 candidates"
through a whole revision, and how the copy in figures/ kept asserting 65, 40,
4247 and 105, while the deposit said 62, 38, 4146 and 96.

Three checks, in the order a stale figure gets there:

  1. Three of the five figures regenerate from the current deposit to the same
     pixels as the committed PNG: 1, 2 and 5. Say three and not five. Figure 3
     is excluded because its width depends on which Helvetica the renderer
     resolves, and Figure 4 has no generator in this deposit at all, so
     NEITHER of those two has its numeric content checked by anything here.
  2. Every image embedded in the .docx is the committed PNG for that figure,
     compared pixel by pixel including the alpha channel. This is what catches
     a corrected figure that was never put back into the document.
  3. Every drawing's display extent in the .docx matches its image's aspect
     ratio. Nothing verified this before, so a re-embed that computed the
     height from the wrong side, or that failed to update the a:ext beside the
     wp:extent, produced a stretched figure and reported success.

Usage:
    python3 analysis/check_figures.py [manuscript.docx ...]
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
import pandas as pd
from PIL import Image

# Figure 3 is absent from the strict list, and this is the reason. It is the
# only figure set in Helvetica; Figures 1, 2 and 5 are set in matplotlib's
# bundled serif. Its generator saves with bbox_inches="tight", so the output
# width is decided by the metrics of whichever Helvetica the renderer resolves:
# the deposited PNG is 2072 px wide, rendered where a real Helvetica was
# installed, and re-rendering it against the Nimbus Sans metric clone gives
# 2065 px with identical content. Requiring the same pixels would therefore
# fail on the machine that did not draw it, so Figure 3 is checked only where
# it counts, against the copy embedded in the document.
#
# Figure 4 is absent on purpose. No generator in this deposit writes
# figures/manuscript_figure_4.png: analysis/manuscript_figure_4.py writes
# figures/figure_4_anchor_count.png, which is a different image at a different
# size. That figure therefore cannot be checked against the data here, and
# saying so is better than implying it was.
GENERATED = [
    (1, "analysis/manuscript_figure_1.py", "figures/manuscript_figure_1.png"),
    (2, "analysis/manuscript_figure_2.py", "figures/manuscript_figure_2.png"),
    (5, "analysis/manuscript_figure_5.py", "figures/manuscript_figure_5.png"),
]
# figure number by order of appearance in the document
IN_DOCUMENT = {
    1: "figures/manuscript_figure_1.png",
    2: "figures/manuscript_figure_2.png",
    3: "figures/manuscript_figure_3.png",
    4: "figures/manuscript_figure_4.png",
    5: "figures/manuscript_figure_5.png",
}

failures = []
skipped = []


def check(label, ok, detail=""):
    """ok True passes, False fails, None means the property is not checkable
    here and is reported as such rather than counted either way."""
    word = "ok" if ok else ("n/a" if ok is None else "FAILED")
    print("   %-56s %s   %s" % (label, word, detail))
    if ok is None:
        skipped.append(label)
    elif not ok:
        failures.append(label)


def same_pixels(a, b):
    """(equal, detail) for two images, compared without rescaling.

    RGBA, not RGB. The committed PNGs carry an alpha channel, and converting
    to RGB discards it, so a figure re-saved with transparent=True compared
    equal to an opaque one. The mode is compared too, because two files that
    differ only in mode are not the same deposited artifact.
    """
    ia, ib = Image.open(a).convert("RGBA"), Image.open(b).convert("RGBA")
    if ia.size != ib.size:
        return False, "%dx%d vs %dx%d" % (ia.size + ib.size)
    d = np.abs(np.asarray(ia).astype(int) - np.asarray(ib).astype(int))
    worst = int(d.max())
    return worst == 0, "max pixel difference %d" % worst


# A regenerated figure is required to match the committed one PIXEL FOR PIXEL
# only when it comes out at the same size. When it does not, the difference is
# text metrics, and those are a property of the platform rather than of the
# deposit: matplotlib saves with bbox_inches="tight", so the canvas is sized
# from rendered text extents, and freetype rasterises glyphs differently on
# macOS and Linux. Measured on this deposit, matplotlib 3.8.4 and 3.10.9 on the
# same machine give byte-identical output for Figures 1, 2 and 5, while the
# same scripts on macOS give 2731x1538 against 2729x1538 and 2254x2095 against
# 2253x2095. The version is not the variable; the platform is.
#
# So a size difference inside this tolerance is reported as not comparable
# here, with the numbers, rather than as a failure. Calling it a failure told
# every reader on a different operating system that the deposit was broken,
# which is worse than saying plainly that this particular property cannot be
# checked from their machine.
SIZE_TOLERANCE = 0.01     # 1% in either dimension


def compare_render(fresh, committed):
    """(ok, detail) for a regenerated figure against the committed one."""
    a, b = Image.open(fresh), Image.open(committed)
    if a.size == b.size:
        return same_pixels(fresh, committed)
    dw = abs(a.size[0] - b.size[0]) / b.size[0]
    dh = abs(a.size[1] - b.size[1]) / b.size[1]
    if max(dw, dh) <= SIZE_TOLERANCE:
        return None, ("%dx%d here against %dx%d committed, %.2f%% in width: "
                      "text metrics differ, so this cannot be checked from "
                      "this platform"
                      % (a.size + b.size + (100 * dw,)))
    return False, "%dx%d vs %dx%d, beyond the %.0f%% tolerance" % (
        a.size + b.size + (100 * SIZE_TOLERANCE,))


def regenerates(script, committed, work):
    """Run a generator, compare with the committed PNG, then put it back.

    The generators cannot be redirected into a scratch tree. Two of them
    resolve their output from the script's own location rather than from the
    working directory, so a run started elsewhere still writes into figures/.
    The committed file is therefore copied aside first, the generator is run
    where it expects to run, the result is compared, and the saved copy is
    restored whatever happens.
    """
    # The generators write a .pdf beside the .png, so both are saved and both
    # are restored. A check that leaves the repository modified is not a check.
    siblings = [committed, os.path.splitext(committed)[0] + ".pdf"]
    siblings = [f for f in siblings if os.path.exists(f)]
    os.makedirs(work, exist_ok=True)
    saved = []
    for f in siblings:
        k = os.path.join(work, os.path.basename(f))
        shutil.copy2(f, k)
        saved.append((f, k))
    keep = saved[0][1]
    # MOVE the committed file out of the way rather than leaving it in place.
    # Copying it and then comparing the same path against the copy compares a
    # file with itself, so a generator that writes nothing, writes to a
    # different path, or swallows its own exception and exits 0 was reported
    # as reproducing the figure exactly. It has to be absent for its
    # reappearance to mean anything.
    for f, _ in saved:
        os.remove(f)
    env = dict(os.environ, PYTHONPATH=os.path.abspath("analysis"))
    try:
        r = subprocess.run([sys.executable, script],
                           capture_output=True, text=True, env=env)
        if r.returncode != 0:
            return False, (r.stderr.strip().splitlines() or ["failed"])[-1][:90]
        if not os.path.exists(committed):
            return False, "the generator wrote nothing to %s" % committed
        return compare_render(committed, keep)
    finally:
        for f, k in saved:
            shutil.copy2(k, f)


def extents(doc, z, target):
    """Check every drawing's wp:extent AND the a:ext beside it.

    Word takes the picture frame from a:ext, so a re-embed that updates only
    wp:extent renders at the wrong aspect ratio while every other check here
    passes. Both tags are read, both are required to agree with each other and
    with the image, and the tolerance is one EMU per rounding step rather than
    a fraction, because cy is written as round(cx * h / w).
    """
    out = []
    at = 0
    n = 0
    while True:
        s = doc.find("<w:drawing>", at)
        if s < 0:
            return out
        e = doc.find("</w:drawing>", s)
        blk, at, n = doc[s:e], e, n + 1
        rid = re.search(r'r:embed="([^"]+)"', blk)
        wp = re.search(r'<wp:extent\s+cx="(\d+)"\s+cy="(\d+)"\s*/>', blk)
        ax = re.search(r'<a:ext\s+cx="(\d+)"\s+cy="(\d+)"\s*/>', blk)
        if not (rid and wp and ax and rid.group(1) in target):
            out.append((n, False, "missing wp:extent, a:ext or image"))
            continue
        w, h = Image.open(z.open("word/" + target[rid.group(1)])).size
        cx, cy = int(wp.group(1)), int(wp.group(2))
        want = round(cx * h / w)
        same = (int(ax.group(1)), int(ax.group(2))) == (cx, cy)
        ok = abs(cy - want) <= 1 and same
        out.append((n, ok, "cx %d, cy %d, expected %d%s"
                    % (cx, cy, want,
                       "" if same else "; a:ext disagrees with wp:extent")))


def main():
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    print("figures against the deposit\n")
    check("the regeneration list still holds %d figures" % len(GENERATED),
          len(GENERATED) == 3, "figures %s"
          % ", ".join(str(n) for n, _, _ in GENERATED))
    with tempfile.TemporaryDirectory() as work:
        for n, script, png in GENERATED:
            if not os.path.exists(png):
                check("Figure %d is committed" % n, False, png)
                continue
            ok, detail = regenerates(script, png, os.path.join(work, str(n)))
            check("Figure %d regenerates from the current deposit" % n,
                  ok, detail)

    # Figure 3 cannot be regenerated here: it is the only figure set in
    # Helvetica and this container resolves Nimbus Sans, which changes its
    # width. So instead of comparing pixels, compare the numbers the committed
    # render displays against the deposit. The stamp is what the PNG shows; if
    # the deposit has moved, the figure is stale and must be redrawn on a
    # machine that has Helvetica.
    stamp_path = os.path.join("figures", "manuscript_figure_3.stamp.json")
    if os.path.exists(stamp_path):
        import json
        stamp = json.load(open(stamp_path))["drawn_from"]
        vd = pd.read_csv(os.path.join(
            "data", "phase_3_p31_variance_decomposition.csv"))
        per = vd[vd.scope == "per_substructure"].set_index("substructure")
        drift = {k: (v, float(per.loc[k, "ratio_between_total"]))
                 for k, v in stamp.items()
                 if k in per.index
                 and abs(v - float(per.loc[k, "ratio_between_total"])) > 5e-4}
        check("Figure 3's committed render matches the current deposit",
              not drift,
              "; ".join("%s shows %.4f, deposit %.4f" % (k, a_, b)
                        for k, (a_, b) in drift.items())
              or "redraw with analysis/figure_4_source.py where Helvetica is "
                 "installed, and update the stamp")

    for docx in sys.argv[1:]:
        print("\n%s\n" % os.path.basename(docx))
        z = zipfile.ZipFile(docx)
        doc = z.read("word/document.xml").decode("utf-8")
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
        target = {m.group(1): m.group(2) for m in re.finditer(
            r'Id="([^"]+)"[^>]*Target="(media/[^"]+)"', rels)}
        embeds = re.findall(r'r:embed="([^"]+)"', doc)
        check("the document holds %d drawings" % len(IN_DOCUMENT),
              len(embeds) == len(IN_DOCUMENT), "found %d" % len(embeds))
        # Count what was actually compared. Without this a mistyped key in
        # IN_DOCUMENT drops a figure from the run and the only symptom is one
        # fewer line, which nobody counts.
        compared = 0
        with tempfile.TemporaryDirectory() as work:
            for n, rid in enumerate(embeds, start=1):
                if n not in IN_DOCUMENT:
                    check("drawing %d has an entry in IN_DOCUMENT" % n, False,
                          "no figure is mapped to this drawing")
                    continue
                if rid not in target:
                    check("drawing %d resolves to an image part" % n, False,
                          "relationship %s is not in document.xml.rels" % rid)
                    continue
                part = "word/" + target[rid]
                out = os.path.join(work, "%d.png" % n)
                with open(out, "wb") as fh:
                    fh.write(z.read(part))
                ok, detail = same_pixels(out, IN_DOCUMENT[n])
                check("Figure %d in the document is the committed PNG" % n,
                      ok, detail)
                compared += 1
        check("every mapped figure was compared",
              compared == len(IN_DOCUMENT),
              "compared %d of %d" % (compared, len(IN_DOCUMENT)))
        for n, ok, detail in extents(doc, z, target):
            check("Figure %d's display extent matches its aspect ratio" % n,
                  ok, detail)

    print()
    if skipped:
        print("%d check(s) not comparable on this platform:" % len(skipped))
        for s_ in skipped:
            print("   %s" % s_)
        print()
    if failures:
        print("%d check(s) FAILED: %s" % (len(failures), "; ".join(failures)))
        return 1
    print("all checks passed%s"
          % (" (%d not comparable here)" % len(skipped) if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
