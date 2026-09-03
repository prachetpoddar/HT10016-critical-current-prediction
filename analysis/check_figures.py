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

  1. Figure 1 regenerates from the current deposit to the same pixels as the
     committed PNG. The generator reads analysis/figure_counts.py, so this
     fails whenever the committed figure predates a change to the tables.
  2. Figure 2 regenerates to the same pixels as the committed PNG. It prints
     only one number, the retrieval corpus, but a silent style drift matters
     as much as a silent number.
  3. Every image embedded in the .docx is the committed PNG for that figure,
     compared pixel by pixel. This is what catches a corrected figure that was
     never put back into the document.

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


def check(label, ok, detail=""):
    print("   %-56s %s   %s" % (label, "ok" if ok else "FAILED", detail))
    if not ok:
        failures.append(label)


def same_pixels(a, b):
    """(equal, detail) for two images, compared without rescaling."""
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        return False, "%dx%d vs %dx%d" % (ia.size + ib.size)
    d = np.abs(np.asarray(ia).astype(int) - np.asarray(ib).astype(int))
    return d.max() == 0, "max pixel difference %d" % d.max()


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
    env = dict(os.environ, PYTHONPATH=os.path.abspath("analysis"))
    try:
        r = subprocess.run([sys.executable, script],
                           capture_output=True, text=True, env=env)
        if r.returncode != 0:
            return False, (r.stderr.strip().splitlines() or ["failed"])[-1][:90]
        if not os.path.exists(committed):
            return False, "the generator wrote nothing to %s" % committed
        return same_pixels(committed, keep)
    finally:
        for f, k in saved:
            shutil.copy2(k, f)


def main():
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")
    print("figures against the deposit\n")
    with tempfile.TemporaryDirectory() as work:
        for n, script, png in GENERATED:
            if not os.path.exists(png):
                check("Figure %d is committed" % n, False, png)
                continue
            ok, detail = regenerates(script, png, os.path.join(work, str(n)))
            check("Figure %d regenerates from the current deposit" % n,
                  ok, detail)

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
        with tempfile.TemporaryDirectory() as work:
            for n, rid in enumerate(embeds, start=1):
                if n not in IN_DOCUMENT:
                    continue
                part = "word/" + target[rid]
                out = os.path.join(work, "%d.png" % n)
                with open(out, "wb") as fh:
                    fh.write(z.read(part))
                ok, detail = same_pixels(out, IN_DOCUMENT[n])
                check("Figure %d in the document is the committed PNG" % n,
                      ok, detail)

    print()
    if failures:
        print("%d check(s) FAILED: %s" % (len(failures), "; ".join(failures)))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
