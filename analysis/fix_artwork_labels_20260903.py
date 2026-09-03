"""
fix_artwork_labels_20260903.py

Put the artwork's own styling back after the label edits of 176d750.

That commit changed the text of six labels in figures/artwork and left every
geometry attribute alone, so three of them no longer fit the shape they sit in.
Measured in the rendered SVG, in user units:

  Fig. 1 gold callout   box 267.61-486.30, text 303.87-516.35
                        The text runs 30.05 past the right border and starts
                        36.26 inside the left one. The original label was
                        centred in the box with 36.26 / 33.50 of padding.
  Fig. 2 callout line 2 box 372.32-458.18, text 373.24-459.24
                        The line is wider than the whole box.
  Fig. 2 refusal list   box 221.71-356.38, line 3 ends at 359.62
                        The original three lines ended at 322.73 at the
                        furthest, and were centred on 285.9-287.7.

Two labels also read as unfinished rather than as a result. Stages 2 and 3 of
Fig. 1 carry "n/a" where the original carried a number, because when 176d750
was written there was no genuine leave-one-substructure-out error for them.
analysis/multi_stage_loso.py was written afterwards and supplies one, so the
three columns can carry the three numbers the layout was drawn for.

Every number written here is read from analysis/multi_stage_loso.py's
all-families cohort, not typed: Stage 1 12.295, best Stage 2 11.543, Stage 3
9.006, which is also what the manuscript now prints.

Idempotent: each edit asserts its target is present before writing, and the
script refuses to touch a file if any edit for it misses.
"""
import os
import sys

ART = os.path.join("figures", "artwork")

FIG1 = os.path.join(ART, "manuscript_figure_1.svg")
FIG2 = os.path.join(ART, "manuscript_figure_2.svg")

# The gold callout is centred by setting the anchor to the middle of the box
# and putting the text origin at the box centre. The text element carries
# transform matrix(1.3333333,0,0,1.3330865,303.8681,97.900557) and the box
# spans 267.61-486.30, so the centre 376.95 is local x
# (376.95 - 303.8681) / 1.3333333 = 54.81.
FIG1_EDITS = [
    ('style="font-variant:normal;font-weight:700;font-size:12.0102px;'
     'font-family:Helvetica;writing-mode:lr-tb;fill:#b96b00;fill-opacity:1;'
     'fill-rule:nonzero;stroke:none" x="0" y="0">compound-scope validation</tspan>',
     'style="font-variant:normal;font-weight:700;font-size:12.0102px;'
     'font-family:Helvetica;writing-mode:lr-tb;text-anchor:middle;fill:#b96b00;'
     'fill-opacity:1;fill-rule:nonzero;stroke:none" x="54.81" y="0">'
     'validation scope</tspan>'),
    ('y="20.017115">LR 11.37</tspan>', 'y="20.017115">LR 12.30</tspan>'),
    ('x="-1.5579721" y="30.025673">n/a</tspan></text>\n'
     '    <text id="text512"',
     'x="-1.5579721" y="30.025673">11.54</tspan></text>\n'
     '    <text id="text512"'),
    ('x="-1.5579721" y="30.025673">n/a</tspan></text>\n'
     '    <text id="text415"',
     'x="-1.5579721" y="30.025673">9.01</tspan></text>\n'
     '    <text id="text415"'),
]

# Group text_35 carries matrix(1.1327291,...,-33.465903,...) and each text a
# further scale(1.0148077,...), so the horizontal factor is 1.14950 and a
# rendered centre T sits at local x (T + 33.4659) / 1.14950. The unedited first
# line is centred on 287.74, so the two rewrapped lines are put there too:
# (287.74 + 33.4659) / 1.14950 = 279.43.
FIG2_EDITS = [
    # The two stage lines are a matplotlib export and carry non-breaking
    # spaces, so the match has to as well.
    ('id="tspan247">Stage\xa01\xa0LOSO\xa011.37</tspan>',
     'id="tspan247">Stage\xa01\xa0LOSO\xa012.30</tspan>'),
    ('<!-- Stage 2 within-family scope -->', '<!-- Stage 2 LOSO 11.54 -->'),
    ('id="tspan271">Stage\xa02:\xa0within-family\xa0scope</tspan>',
     'id="tspan271">Stage\xa02\xa0LOSO\xa011.54</tspan>'),
    ('x="246.68707"\n           y="166.40158"\n           id="text14"',
     'x="279.43"\n           y="166.40158"\n           id="text14"'),
    ('id="tspan9"\n             style="stroke-width:0"\n'
     '             x="246.68707"\n'
     '             y="166.40158">(reduced field, Hc2, T&gt;Tc, family</tspan>',
     'id="tspan9"\n             style="stroke-width:0;text-anchor:middle"\n'
     '             x="279.43"\n'
     '             y="166.40158">(reduced field, Hc2, T &gt; Tc,</tspan>'),
    ('x="245.70917"\n           y="175.14893"\n           id="text15"',
     'x="279.43"\n           y="175.14893"\n           id="text15"'),
    ('id="tspan14"\n             style="stroke-width:0"\n'
     '             x="245.70917"\n'
     '             y="175.14893">threshold, K_min, monotonic, OOD)</tspan>',
     'id="tspan14"\n             style="stroke-width:0;text-anchor:middle"\n'
     '             x="279.43"\n'
     '             y="175.14893">family, K_min, monotonic, OOD)</tspan>'),
]


def apply(path, edits):
    src = open(path, encoding="utf-8").read()
    missing = [f for f, _ in edits if f not in src]
    done = [f for f, r in edits if f not in src and r in src]
    if missing and len(done) == len(missing):
        print("   %-40s already applied" % os.path.basename(path))
        return True
    if missing:
        print("   %-40s REFUSED, %d edit(s) did not match"
              % (os.path.basename(path), len(missing)))
        for f in missing:
            print("      no match: %s" % f[:90].replace("\n", "\\n"))
        return False
    # No backup file is written. These SVGs are tracked, one of them is 7 MB,
    # and "git show HEAD:<path>" is a better copy of the previous state than a
    # sidecar that would be committed beside it. Earlier scripts in this
    # deposit wrote .backup files and then had to guard against clobbering them
    # on a second run; that whole problem belongs to git.
    for f, r in edits:
        src = src.replace(f, r, 1)
    # The SVGs are write-protected in the deposit, so clear the bit, write, and
    # put it back exactly as it was.
    mode = os.stat(path).st_mode
    os.chmod(path, 0o644)
    open(path, "w", encoding="utf-8").write(src)
    os.chmod(path, mode)
    print("   %-40s %d edit(s) applied" % (os.path.basename(path), len(edits)))
    return True


def main():
    if not os.path.isdir(ART):
        sys.exit("run from the repository root")
    print("restoring the artwork's label fit\n")
    ok = apply(FIG1, FIG1_EDITS) and apply(FIG2, FIG2_EDITS)
    print()
    if not ok:
        print("nothing was written")
        return 1
    print("now re-render: cd %s && python3 render_artwork.py" % ART)
    return 0


if __name__ == "__main__":
    sys.exit(main())
