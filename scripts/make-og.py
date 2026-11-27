#!/usr/bin/env python3
"""Makes og/<slug>.jpg share images (1200x630) with headless Chrome.
Programs and pages: the name in Instrument Serif on brand yellow. Projects: their cover photo with the name over it.
Run from the repo root: python3 scripts/make-og.py  (needs playwright + chrome)."""
import os, re, json, asyncio
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
a = src.index("const SEO = {"); b = src.index("};", a)
SEO = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'\n  (\w+): \["(.*?)", "(.*?)"\],', src[a:b])}
w = src.index("const WORKDATA = "); w2 = src.index(";\n", w); WORK = json.loads(src[w + 17:w2])
MARK = re.search(r'<a class="mark"[^>]*>(<svg viewBox="0 0 31.8515 30.1058".*?</svg>)', src, re.S).group(1)
PAGES = {"programs": "programs", "boardroom": "boardroom", "launch": "launch", "formation": "formation", "elevation": "elevation", "direction": "direction",
         "enterprise": "enterprise", "method": "method", "about": "about", "contact": "contact", "work": "index", "yankyperl": "yankyperl"}
FONT = "file://" + os.path.join(ROOT, "fonts", "instrument-serif.woff2")
SANS = "file://" + os.path.join(ROOT, "fonts", "nhg-display-55.woff2")
def doc(bg, color, big, small, size, photo=None):
    shade = '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,10,8,.5),rgba(8,10,8,.78))"></div>' if photo else ""
    pic = f'<img src="file://{photo}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">' if photo else ""
    return f"""<!doctype html><meta charset="utf-8"><style>@font-face{{font-family:IS;src:url({FONT})}}@font-face{{font-family:NH;src:url({SANS})}}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}body{{background:{bg};color:{color};position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
h1{{position:relative;font:400 {size}px/.86 IS,serif;letter-spacing:-.04em;margin:0 60px}}p{{position:relative;font:400 30px/1.3 NH,sans-serif;margin:26px 0 0;opacity:.85;letter-spacing:-.01em}}
.m{{position:relative;width:52px;margin-top:40px}}.m svg{{width:100%;height:auto;display:block;color:{color}}}</style><body>{pic}{shade}<h1>{big}</h1><p>{small}</p><div class="m">{MARK}</div></body>"""
async def main():
    os.makedirs(os.path.join(ROOT, "og"), exist_ok=True)
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await br.new_page(viewport={"width": 1200, "height": 630})
        jobs = []
        for slug, key in PAGES.items():
            t = SEO[key][0]; name = t.split(" - ")[0].split(" | ")[0]; sub = (t.split(" - ")[1] if " - " in t else "").split(" | ")[0]
            jobs.append((slug, doc("#ffca6e", "#121212", name, sub, 190 if len(name) < 14 else 130)))
        for pid, P in WORK.items():
            if P.get("art") != "photo": continue
            photo = os.path.join(ROOT, P.get("hero") or P.get("card"))
            jobs.append((pid, doc("#111", "#fff", P["name"], ", ".join(P.get("scope", [])[:2]), 170 if len(P["name"]) < 12 else 128, photo)))
        for slug, h in jobs:
            f = os.path.join(ROOT, "og", "_t.html"); open(f, "w").write(h)
            await pg.goto("file://" + f); await pg.wait_for_timeout(500)
            await pg.screenshot(path=os.path.join(ROOT, "og", slug + ".jpg"), type="jpeg", quality=86)
        os.remove(os.path.join(ROOT, "og", "_t.html"))
        await br.close()
    print("made", len(jobs), "share images")
asyncio.run(main())
