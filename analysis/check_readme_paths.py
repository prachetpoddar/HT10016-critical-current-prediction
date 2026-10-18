#!/usr/bin/env python3
"""
check_readme_paths.py

Every repository path named in README.md must exist.

The landing section added on 2026-10-18 maps the sections of the paper onto the
files behind them, which is only useful while the map is true. A rename that
misses the README leaves a reader following a path to nothing, which is the
complaint the section was written to answer. This runs in a second and fails
loudly, so the map goes stale in CI rather than in a reader's hands.

A backticked token counts as a path when it ends in a known extension or in a
separator. Sections that work inside one directory name their files bare, so a
bare name is resolved against the directory roots as well as the repository
root. Shell fragments and prose in backticks are skipped.
"""

import glob
import os
import re
import sys

EXT = (".py", ".csv", ".json", ".md", ".yml", ".docx", ".png", ".svg")
ROOTS = ("", "data/", "analysis/", "audit/", "figures/", "specs/", "out_final52/")


def paths(text):
    for m in re.finditer(r"`([^`\n]+)`", text):
        token = m.group(1).strip()
        if token.startswith(("-", "--", "python3", "$")) or " " in token:
            continue
        if token.endswith(EXT) or token.endswith("/"):
            yield token


def main(readme="README.md"):
    text = open(readme).read()
    seen, missing = [], []
    for token in paths(text):
        hit = []
        for root in ROOTS:
            candidate = root + token
            hit = (
                glob.glob(candidate) if "*" in candidate
                else ([candidate] if os.path.exists(candidate) else [])
            )
            if hit:
                break
        seen.append(token)
        if not hit:
            missing.append(token)
    for token in sorted(set(seen)):
        print("%-6s %s" % ("" if token not in missing else "MISSING", token))
    if missing:
        print("\n%d path(s) named in %s do not exist" % (len(missing), readme))
        return 1
    print("\nall %d distinct paths named in %s exist" % (len(set(seen)), readme))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
