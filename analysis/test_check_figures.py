"""
test_check_figures.py

The meta-test: plant a known defect and require analysis/check_figures.py to
go red. A passing suite is evidence about the suite, not about the code, and
an independent review of check_figures.py found that 16 of 31 semantic
mutations walked straight through it. The worst was structural rather than
subtle: the committed PNG was copied aside instead of moved, so the comparison
was between a file and a copy of itself, and a generator replaced by a single
print statement reported "regenerates from the current deposit, max pixel
difference 0".

Each case here restores whatever it touched, and the run asserts the working
tree is unchanged at the end. A test that leaves the repository dirty is worse
than no test.

Usage:
    python3 analysis/test_check_figures.py MANUSCRIPT.docx
"""
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

CHECK = os.path.join("analysis", "check_figures.py")
GEN1 = os.path.join("analysis", "manuscript_figure_1.py")
FIG1 = os.path.join("figures", "manuscript_figure_1.png")

failures = []


def run(docx=None):
    cmd = [sys.executable, CHECK] + ([docx] if docx else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def expect_red(label, why):
    code, out = run(*ARGS)
    ok = code != 0
    print("   %-52s %s" % (label, "ok" if ok else "SURVIVED"))
    if not ok:
        failures.append("%s: %s" % (label, why))
        print("      the suite stayed green; %s" % why)


def case_generator_writes_nothing(work):
    """The defect that was actually shipped."""
    shutil.copy2(GEN1, os.path.join(work, "gen1"))
    try:
        with open(GEN1, "w") as fh:
            fh.write('print("written")\n')
        expect_red("a generator that writes nothing",
                   "the committed figure is compared with a copy of itself")
    finally:
        shutil.copy2(os.path.join(work, "gen1"), GEN1)


def case_committed_figure_edited(work):
    """A committed PNG that no longer matches what the generator produces."""
    shutil.copy2(FIG1, os.path.join(work, "fig1"))
    try:
        from PIL import Image
        im = Image.open(FIG1).convert("RGBA")
        px = im.load()
        px[0, 0] = (255, 0, 0, 255)
        im.save(FIG1)
        expect_red("one pixel changed in the committed figure",
                   "the pixel comparison is not sensitive")
    finally:
        shutil.copy2(os.path.join(work, "fig1"), FIG1)


def case_other_platform(work):
    """A render that differs only in size, within tolerance, is NOT a failure.

    This is what a reader on another operating system sees: matplotlib sizes
    the canvas from rendered text extents, and freetype rasterises glyphs
    differently per platform, so Figures 1, 2 and 5 come out one or two pixels
    wider on macOS than on the Linux machine that drew them. Reporting that as
    a failure told every such reader the deposit was broken. The suite must
    stay green and say the property is not comparable there.
    """
    from PIL import Image
    shutil.copy2(FIG1, os.path.join(work, "fig1.plat"))
    try:
        im = Image.open(FIG1).convert("RGBA")
        wide = Image.new("RGBA", (im.size[0] + 2, im.size[1]), (255, 255, 255, 255))
        wide.paste(im, (0, 0))
        wide.save(FIG1)
        # Assert on the regeneration line only. Widening the committed PNG
        # also makes the document comparison fail, correctly, because the
        # .docx still holds the narrower image, so the suite's exit code is
        # not the thing under test here.
        _code, out = run(*ARGS)
        line = next((l for l in out.splitlines()
                     if "Figure 1 regenerates" in l), "")
        ok = " n/a " in line and "text metrics differ" in line
        print("   %-52s %s" % ("a two-pixel-wider render from another platform",
                               "ok" if ok else "FAILED"))
        if not ok:
            failures.append("a cross-platform size difference is not reported "
                            "as not-comparable: %s" % line.strip()[:80])
    finally:
        shutil.copy2(os.path.join(work, "fig1.plat"), FIG1)


def case_stretched_extent(work):
    """A display extent that does not match the image's aspect ratio."""
    src = ARGS[0]
    out = os.path.join(work, "stretched.docx")
    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")
    bad = doc.replace('<wp:extent cx="5715000" cy="3220839"/>',
                      '<wp:extent cx="5715000" cy="4000000"/>', 1)
    if bad == doc:
        print("   %-52s skipped, extent not found" % "a stretched figure")
        failures.append("stretched extent case could not be built")
        return
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zin.infolist():
            zo.writestr(it, bad if it.filename == "word/document.xml"
                        else zin.read(it.filename))
    code, _ = run(out)
    ok = code != 0
    print("   %-52s %s" % ("a stretched figure in the document",
                           "ok" if ok else "SURVIVED"))
    if not ok:
        failures.append("a stretched extent passes")


def case_swapped_images(work):
    """Two figures exchanged in the document."""
    src = ARGS[0]
    out = os.path.join(work, "swapped.docx")
    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")
    bad = doc.replace('r:embed="rId8"', "@@A@@", 1)
    bad = bad.replace('r:embed="rId9"', 'r:embed="rId8"', 1)
    bad = bad.replace("@@A@@", 'r:embed="rId9"', 1)
    if bad == doc:
        print("   %-52s skipped" % "two figures swapped")
        return
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zin.infolist():
            zo.writestr(it, bad if it.filename == "word/document.xml"
                        else zin.read(it.filename))
    code, _ = run(out)
    ok = code != 0
    print("   %-52s %s" % ("two figures swapped in the document",
                           "ok" if ok else "SURVIVED"))
    if not ok:
        failures.append("swapped figures pass")


def main():
    global ARGS
    if len(sys.argv) != 2:
        sys.exit("usage: python3 analysis/test_check_figures.py MS.docx")
    ARGS = (sys.argv[1],)
    if not os.path.isdir("data"):
        sys.exit("run from the repository root")

    before = subprocess.run(["git", "status", "--porcelain"],
                            capture_output=True, text=True).stdout

    code, _ = run(*ARGS)
    print("planting defects, each must turn the suite red\n")
    print("   %-52s %s" % ("the suite is green before any defect is planted",
                           "ok" if code == 0 else "FAILED"))
    if code != 0:
        failures.append("the suite was already red")

    with tempfile.TemporaryDirectory() as work:
        case_generator_writes_nothing(work)
        case_committed_figure_edited(work)
        case_other_platform(work)
        case_stretched_extent(work)
        case_swapped_images(work)

    after = subprocess.run(["git", "status", "--porcelain"],
                           capture_output=True, text=True).stdout
    clean = after == before
    print("\n   %-52s %s" % ("the working tree is as it was",
                             "ok" if clean else "FAILED"))
    if not clean:
        failures.append("the test left the tree modified")

    print()
    if failures:
        print("%d case(s) FAILED: %s" % (len(failures), "; ".join(failures)))
        return 1
    print("every planted defect was caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
