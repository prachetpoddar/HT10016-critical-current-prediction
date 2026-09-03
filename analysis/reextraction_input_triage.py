"""Decide, per figure, whether a screenshot alone is enough.

The one thing that decides it is whether the series are separable by colour.
If they are, everything the manifest asks for can be read off a rendered page:
the axis types come from tick geometry, the series come from the colours, and
the legend mapping comes from reading the labels. If they are not, the series
count and the temperature list have to be supplied, because colour separation
returns nothing on a monochrome figure and a visual count of overplotted black
curves is exactly where reading a figure has been shown to wobble.
"""
import glob, json, os, re, sys, collections
import numpy as np, pymupdf
sys.path.insert(0, "/home/claude/ht_gh/analysis")
from figure_spec_builder import find_axes_boxes

U = "/mnt/user-data/uploads/SuperconductorWorkflow/pdfs_for_page_review/"
JC = re.compile(r"critical[- ]current|current densit|\bJ\s*c\b|\bJc\b|\bjc\b|\bJ\s*s\b", re.I)
HC = re.compile(r"phase diagram|irreversibilit|H\s*irr|Hirr|B\s*irr|Birr|"
                r"upper critical field|H\s*c2|Hc2|B\s*c2|Bc2|vortex (?:solid|liquid|glass)|"
                r"melting line", re.I)
CAPSTART = re.compile(r"^\s*(?:FIG\.?|Figure|Fig\.)\s*\.?\s*([0-9]+[a-z]?)\b(.{0,320})", re.S | re.I)


def caption_pages(doc, want):
    """Pages carrying a real caption block (one that STARTS with FIG/Figure)."""
    out = []
    for pi in range(doc.page_count):
        for b in doc[pi].get_text("blocks"):
            t = re.sub(r"\s+", " ", b[4]).strip()
            m = CAPSTART.match(t)
            if m and want.search(m.group(2)):
                out.append((pi + 1, m.group(0)[:110]))
                break
    return out


def series_colours(arr, box, min_px):
    """Distinct saturated colours occupying a real area inside the frame.

    Greys are excluded because the frame, the ticks and the axis annotations are
    grey or black, and a black data series cannot be told from them.
    """
    x0, x1, y0, y1 = box
    sub = arr[y0 + 3:y1 - 3, x0 + 3:x1 - 3].astype(np.int16)
    if sub.size == 0:
        return []
    mx, mn = sub.max(axis=2), sub.min(axis=2)
    sat = (mx - mn) >= 60
    if not sat.any():
        return []
    px = sub[sat]
    keys = (px // 48).astype(np.int8)
    cnt = collections.Counter(map(tuple, keys.tolist()))
    return [(c, n) for c, n in cnt.items() if n >= min_px]


def probe(path, want):
    doc = pymupdf.open(path)
    pages = caption_pages(doc, want)
    res = []
    for pg, cap in pages[:6]:
        best = (0, 0, None)          # n_colours, box area, scale
        for sc in (4.0,):
            pix = doc[pg - 1].get_pixmap(matrix=pymupdf.Matrix(sc, sc))
            arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, 3)
            for box in find_axes_boxes(arr):
                area = (box[1] - box[0]) * (box[3] - box[2])
                cols = series_colours(arr, box, int(120 * (sc / 4.0) ** 2))
                if len(cols) > best[0]:
                    best = (len(cols), area, sc)
        res.append(dict(page=pg, caption=cap, n_colours=best[0],
                        box_found=best[1] > 0, scale=best[2]))
    doc.close()
    return res


if __name__ == "__main__":
    import sys
    lo,hi=int(sys.argv[2]),int(sys.argv[3])
    out = {}
    for p in sorted(glob.glob(U + "*.pdf"))[lo:hi]:
        n = os.path.basename(p)[:-4]
        try:
            out[n] = dict(jc=probe(p, JC), hc2=probe(p, HC))
        except Exception as e:
            out[n] = dict(error=str(e))
        print(n, "done", flush=True)
    json.dump(out, open(sys.argv[1], "w"), indent=1)
