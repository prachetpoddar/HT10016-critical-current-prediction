"""
reembed_manuscript_figures.py

Replace an embedded figure in the manuscript .docx with the current file from
figures/, and recompute its display extent from the new pixel dimensions.

Why this is a script and not a manual step. analysis/check_documents.py and
analysis/check_cross_artifact_consistency.py both read word/document.xml, so
neither can see a number that is drawn inside an image. The Figure 1 embedded
in the manuscript asserted 69 papers, 43 compounds, 4387 extracted points, 110
anchors and "125 of 185 candidates" for the whole revision, every one of them
a pre-withdrawal value, and no check in the deposit could reach it.

The extent matters as much as the bytes. Word stores the display size in EMU
independently of the image, so dropping in a file with a different aspect ratio
silently stretches it. Each drawing here keeps its width and has its height
recomputed as cx * h / w, in both wp:extent and the a:ext inside a:xfrm, which
are the two places the size is written.

Usage:
    python3 analysis/reembed_manuscript_figures.py IN.docx OUT.docx

The mapping below is by order of appearance in the document, which is the order
Figures 1 to 5 are placed. It is asserted rather than assumed: the script
refuses to write unless it finds exactly five drawings.

Every drawing has its extent recomputed, not only the ones whose image is
replaced. Figures 2 and 4 were written by whatever tool first built the
document and carry heights that disagree with their own aspect ratio by 736 and
4012 EMU; both are under a tenth of a percent and invisible, but there is no
reason to keep a figure stretched by any amount once the correct height is one
line of arithmetic.
"""
import os
import re
import shutil
import sys
import zipfile

from PIL import Image

# figure number (1-based, by order of appearance) -> file in figures/
# Figures 2 and 4 in the document already match figures/, so they are left
# alone. Figures 3 and 5 do not: Figure 3 in the document still shows the
# pre-withdrawal variance ratios (0.73 chalcogenide, 0.60 for the 122 family
# against the deposit's 0.77 and 0.35, and a Wire column for a record that has
# since been withdrawn), and Figure 5 still shows the narrow pre-gate
# uncertainty envelope that 3c1e4e4 replaced. Both were regenerated in the
# repository during this revision and never put back into the document.
REPLACE = {
    1: os.path.join("figures", "manuscript_figure_1.png"),
    3: os.path.join("figures", "manuscript_figure_3.png"),
    5: os.path.join("figures", "manuscript_figure_5.png"),
}
EXPECTED_DRAWINGS = 5


def drawing_blocks(doc):
    """Every <w:drawing>...</w:drawing> span, in document order."""
    out = []
    at = 0
    while True:
        s = doc.find("<w:drawing>", at)
        if s < 0:
            return out
        e = doc.find("</w:drawing>", s)
        if e < 0:
            raise SystemExit("unterminated <w:drawing> in word/document.xml")
        out.append((s, e + len("</w:drawing>")))
        at = e


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip().splitlines()[-3].strip())
    src, dst = sys.argv[1], sys.argv[2]
    if not os.path.isdir("figures"):
        sys.exit("run from the repository root")

    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")
    rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
    target = {m.group(1): m.group(2) for m in re.finditer(
        r'Id="([^"]+)"[^>]*Target="(media/[^"]+)"', rels)}

    blocks = drawing_blocks(doc)
    if len(blocks) != EXPECTED_DRAWINGS:
        sys.exit("expected %d drawings, found %d; refusing to guess which is "
                 "which" % (EXPECTED_DRAWINGS, len(blocks)))

    swap = {}          # media part name -> new bytes
    pieces, at = [], 0
    for n, (s, e) in enumerate(blocks, start=1):
        pieces.append(doc[at:s])
        blk = doc[s:e]
        at = e
        m = re.search(r'r:embed="([^"]+)"', blk)
        if not m or m.group(1) not in target:
            sys.exit("drawing %d has no resolvable image relationship" % n)
        part = "word/" + target[m.group(1)]
        new = REPLACE.get(n)
        old_w, old_h = Image.open(zin.open(part)).size
        w, h = Image.open(new).size if new else (old_w, old_h)
        # Whitespace inside these tags is legal OOXML, so the patterns tolerate
        # it. An earlier version required the exact serialization and re.sub
        # then silently did nothing on a document written by a different tool.
        WP = r'<wp:extent\s+cx="(\d+)"\s+cy="(\d+)"\s*/>'
        AX = r'<a:ext\s+cx="(\d+)"\s+cy="(\d+)"\s*/>'
        cx = re.search(WP, blk)
        ax = re.search(AX, blk)
        # Both tags are required. Word takes the picture frame from a:ext, so
        # updating wp:extent alone renders the figure at the wrong aspect ratio
        # while every printed diagnostic, which reads wp:extent, says success.
        if not cx:
            sys.exit("drawing %d has no wp:extent" % n)
        if not ax:
            sys.exit("drawing %d has no a:ext beside its wp:extent" % n)
        keep_cx = int(cx.group(1))
        cy = round(keep_cx * h / w)
        before = "%s x %s" % (cx.group(1), cx.group(2))
        if (int(cx.group(1)), int(cx.group(2))) == (keep_cx, cy) and not new:
            pieces.append(blk)
            continue
        blk, nwp = re.subn(WP, '<wp:extent cx="%d" cy="%d"/>' % (keep_cx, cy),
                           blk)
        blk, nax = re.subn(AX, '<a:ext cx="%d" cy="%d"/>' % (keep_cx, cy), blk)
        if nwp != 1 or nax != 1:
            sys.exit("drawing %d: rewrote %d wp:extent and %d a:ext, expected "
                     "one of each" % (n, nwp, nax))
        if new:
            swap[part] = open(new, "rb").read()
            print("   Figure %d  %s" % (n, new))
            print("      pixels  %dx%d -> %dx%d" % (old_w, old_h, w, h))
        else:
            print("   Figure %d  extent only, image unchanged" % n)
        print("      extent  %s -> %d x %d EMU" % (before, keep_cx, cy))
        pieces.append(blk)
    pieces.append(doc[at:])
    doc = "".join(pieces)

    tmp = dst + ".part"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item, doc)
            elif item.filename in swap:
                zout.writestr(item, swap[item.filename])
            else:
                zout.writestr(item, zin.read(item.filename))
    zin.close()
    shutil.move(tmp, dst)
    print("\n   wrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
