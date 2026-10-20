#!/usr/bin/env python3
"""
sentence_split.py

Sentence boundaries for this corpus, which is dense with abbreviations,
section pointers and initials.

The previous splitter guarded abbreviations with negative lookbehinds placed
ahead of the period:

    (?<!\\bSec)(?<!\\bFig)...(?<=[.!?])\\s+(?=[A-Z(])

Every lookbehind in a pattern is evaluated at the same position, which here
is the position after the period. So the guard against "Sec" tested the three
characters "ec." and succeeded, and the same held for every other entry. The
guards were no-ops for the whole of their existence, which is why "the
envelope crossing of Sec. III.C is small" split into three fragments, one of
them the bare "III.C".

This version finds candidate boundaries and then rejects them by looking at
the token before the period, which is what the guard was meant to do.
"""

import re

# Abbreviations whose period never ends a sentence.
ABBR = {
    "sec", "secs", "fig", "figs", "eq", "eqs", "ref", "refs", "tab", "tabs",
    "no", "nos", "vs", "al", "cf", "dr", "prof", "approx", "ca", "etc",
    "supp", "mater", "vol", "pp", "ed", "eds", "inc", "ltd", "jr", "sr",
    "e.g", "i.e", "resp", "min", "max", "est", "st",
}

# A token that is only a label: a single letter, a roman numeral, or a
# dotted section pointer such as "III.A" or "II.C".
LABEL = re.compile(r"^(?:[A-Za-z]|[IVXLCivxlc]+|[IVXLC]+\.[A-Z](?:\.[0-9A-Z]+)*)$")

CANDIDATE = re.compile(r"[.!?]+\s+")
OPENS = re.compile(r"[A-Z(β]")      # (, an uppercase letter, or beta


EDGE = "()[]{}.,;:'" + chr(34) + chr(0x201c) + chr(0x201d) + chr(0x2018) + chr(0x2019)


def _token_before(text, i):
    """The word ending immediately before the period at text[i]."""
    j = i
    while j > 0 and not text[j - 1].isspace():
        j -= 1
    return text[j:i]


def boundary_at(text, i, after):
    """Is the period run starting at text[i] a sentence boundary?

    `after` is the index of the first character following the whitespace.
    """
    if after >= len(text) or not OPENS.match(text[after]):
        return False
    tok = _token_before(text, i)
    if not tok:
        return False
    # Strip the brackets and quotes that sit around a pointer such as
    # "(Sec." before testing the word itself.
    bare = tok.strip(EDGE)
    if not bare:
        return False
    if bare.lower() in ABBR:
        return False
    if LABEL.match(bare):
        return False
    return True


def spans(text):
    """Sentence spans as (start, end) pairs covering the whole string."""
    out = []
    start = 0
    for m in CANDIDATE.finditer(text):
        i, after = m.start(), m.end()
        if not boundary_at(text, i, after):
            continue
        # keep the period run with the sentence it closes
        end = i
        while end < len(text) and text[end] in ".!?":
            end += 1
        if text[start:end].strip():
            out.append((start, end))
        start = after
    if text[start:].strip():
        out.append((start, len(text)))
    return out


def sentences(text):
    return [text[a:b] for a, b in spans(text)]
