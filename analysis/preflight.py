"""
preflight.py

Check that this environment can run the deposit, before a script fails on
import in the middle of something.

Written after `python3 analysis/figure_4_source.py` failed on
`ModuleNotFoundError: No module named 'numpy'` in an environment named for this
project. environment.yml also turned out to omit matplotlib, python-docx and
pillow, which fifteen, eight and four scripts import, so an environment created
correctly from the earlier file still could not draw a figure.

    python3 analysis/preflight.py

Exits non-zero and names what to install if anything is missing.
"""
import importlib
import sys

# module to import, what installs it, what stops working without it
NEEDED = [
    ("numpy", "numpy=1.26", "everything"),
    ("pandas", "pandas=2.1", "everything"),
    ("scipy", "scipy=1.11", "the fitting scripts"),
    ("matplotlib", "matplotlib=3.8", "all five manuscript figures"),
    ("docx", "pip install python-docx", "every document check and edit"),
    ("PIL", "pillow", "the figure and re-embedding checks"),
]
OPTIONAL = [
    ("fitz", "pip install pymupdf==1.24.9", "the PDF extraction audits"),
    ("anthropic", "pip install anthropic", "the paired-extraction audits"),
]


def probe(rows):
    out = []
    for mod, how, why in rows:
        try:
            m = importlib.import_module(mod)
            v = getattr(m, "__version__", "")
            out.append((mod, True, v, how, why))
        except Exception as e:
            out.append((mod, False, str(e)[:40], how, why))
    return out


def main():
    print("preflight for the HT10016 deposit\n")
    print("   python %s" % sys.version.split()[0])
    print("   %s\n" % sys.executable)
    req = probe(NEEDED)
    opt = probe(OPTIONAL)
    for mod, ok, v, how, why in req:
        print("   %-12s %-3s %-10s %s" % (mod, "ok" if ok else "NO", v if ok else "",
                                          "" if ok else "needed for " + why))
    print()
    for mod, ok, v, how, why in opt:
        print("   %-12s %-3s %-10s optional, %s"
              % (mod, "ok" if ok else "--", v if ok else "", why))

    missing = [(m, how) for m, ok, _, how, _ in req if not ok]
    print()
    if missing:
        print("%d required package(s) missing.\n" % len(missing))
        conda = [h for _, h in missing if not h.startswith("pip")]
        pips = [h for _, h in missing if h.startswith("pip")]
        if conda:
            print("   conda install -c conda-forge %s" % " ".join(conda))
        for p in pips:
            print("   %s" % p)
        print("\n   or rebuild the whole environment:")
        print("   conda env create -f environment.yml && conda activate ht10016")
        return 1

    # Helvetica matters for Figure 3 only, and only for its width, so this is
    # reported rather than failed.
    try:
        from matplotlib import font_manager
        # Resolve the same family LIST figure_4_source.py sets, not "Helvetica"
        # alone. Asking for Helvetica by itself falls through to the matplotlib
        # default and reports a font the figure would never use.
        import os as _os
        _src = _os.path.join("analysis", "figure_4_source.py")
        fams = ["Helvetica", "Nimbus Sans", "Arial", "Liberation Sans",
                "DejaVu Sans"]
        if _os.path.exists(_src):
            import re as _re
            m = _re.search(r'"font\.family":\s*\[([^\]]*)\]',
                           open(_src, encoding="utf-8").read())
            if m:
                fams = [x.strip().strip('"\'') for x in m.group(1).split(",")]
        got = font_manager.findfont(font_manager.FontProperties(family=fams),
                                    fallback_to_default=True)
        name = font_manager.FontProperties(fname=got).get_name()
        print("   font for Figure 3: %s" % name)
        if name not in ("Helvetica", "Arial"):
            print("   Figure 3 was deposited in Helvetica. This environment "
                  "resolves %s," % name)
            print("   which changes the figure's width. Redraw it elsewhere.")
    except Exception as e:
        print("   could not resolve a font: %s" % e)

    print("\nthis environment can run the deposit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
