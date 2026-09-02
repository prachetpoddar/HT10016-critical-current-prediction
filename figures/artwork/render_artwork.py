import asyncio, pathlib, re
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for src, out, width in [("figure_1_contribution_updated.svg", "fig1_render.png", 3000)]:
            s = pathlib.Path(src).read_text()
            m = re.search(r'viewBox="([\d.\-]+) ([\d.\-]+) ([\d.]+) ([\d.]+)"', s)
            vw, vh = float(m.group(3)), float(m.group(4)); h = round(width*vh/vw)
            s = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"', r'\1', s, count=1)
            s = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"', r'\1', s, count=1)
            html = ("<!doctype html><meta charset='utf-8'><style>html,body{margin:0;background:#fff}"
                    "svg{display:block;width:%dpx;height:%dpx}</style>%s" % (width, h, s))
            pg = await b.new_page(viewport={"width": width, "height": h})
            await pg.set_content(html, wait_until="networkidle"); await pg.wait_for_timeout(1200)
            await pg.screenshot(path=out, clip={"x":0,"y":0,"width":width,"height":h}); await pg.close()
            print("wrote", out, width, h)
        await b.close()
asyncio.run(main())
