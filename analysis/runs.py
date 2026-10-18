#!/usr/bin/env python3
"""
runs.py

Replace a span of text inside a paragraph without disturbing the rest of it.

This is a rewrite. The original was lost when the working container was
reclaimed on 2026-10-18, and it had never been pushed to the deposit. The
contract is the one the passes in this repository depend on: find `old`
somewhere in the paragraph's concatenated run text, put `new` there, and leave
every other run alone. The replaced span takes the formatting of the first run
it starts in, which is what keeps a highlighted passage highlighted and an
italic quotation italic.
"""


def replace(paragraph, old, new):
    runs = paragraph.runs
    text = "".join(r.text for r in runs)
    at = text.find(old)
    if at < 0:
        raise ValueError("paragraph does not carry %r" % old[:60])
    end = at + len(old)

    pos, first = 0, None
    for run in runs:
        start, stop = pos, pos + len(run.text)
        pos = stop
        if stop <= at or start >= end:
            continue                      # untouched
        head = run.text[:max(0, at - start)]
        tail = run.text[max(0, end - start):] if stop > end else ""
        if first is None:
            first = run
            run.text = head + new + tail
        else:
            run.text = head + tail
    if first is None:
        raise ValueError("no run holds the span")
    return paragraph
