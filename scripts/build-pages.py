#!/usr/bin/env python3
"""Builds a front-door file for every page and project: p/<slug>.html.
Each is a copy of index.html with that page's title, description, share image,
canonical address and a short text summary for search engines.
Run from the repo root after any change to index.html:  python3 scripts/build-pages.py
Share images live in og/<slug>.jpg (made by scripts/make-og.py); missing ones fall back to og-image.jpg."""
import re, json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.presidentswork.com"
src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

a = src.index("const SEO = {"); b = src.index("};", a)
SEO = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(r'\n  (\w+): \["(.*?)", "(.*?)"\],', src[a:b])}
w = src.index("const WORKDATA = "); w2 = src.index(";\n", w)
WORK = json.loads(src[w + len("const WORKDATA = "):w2])
llms = open(os.path.join(ROOT, "llms.txt"), encoding="utf-8").read()

def llms_section(head):
    m = re.search(r"\n#{2,3} " + re.escape(head) + r"\n(.*?)(?=\n#{2,3} |\Z)", llms, re.S)
    return m.group(1).strip() if m else ""

PAGES = {  # slug in the URL -> (SEO key, llms.txt section to include)
    "programs": ("programs", "How to choose a program"), "boardroom": ("boardroom", "Boardroom™"), "launch": ("launch", "Launch™"),
    "formation": ("formation", "Formation™"), "elevation": ("elevation", "Elevation™"), "direction": ("direction", "Direction™"),
    "enterprise": ("enterprise", "Enterprise"), "method": ("method", "Method: The Presidential Run©"), "about": ("about", "Company and founder"),
    "contact": ("contact", "Company and founder"), "work": ("index", "Selected work"), "yankyperl": ("yankyperl", "Company and founder"),
}

def text_block(h1, desc, extra):
    lines = [l.strip("- ").strip() for l in extra.splitlines() if l.strip()]
    items = "".join(f"<li>{html.escape(l)}</li>" for l in lines[:14])
    return (f'<div class="seo-copy" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap">'
            f"<h1>{html.escape(h1)}</h1><p>{html.escape(desc)}</p>" + (f"<ul>{items}</ul>" if items else "") + "</div>")

def page(slug, title, desc, h1, extra, img_alt):
    img = f"og/{slug}.jpg" if os.path.exists(os.path.join(ROOT, "og", slug + ".jpg")) else "og-image.jpg"
    url = f"{SITE}/{slug}"
    t = src
    esc = lambda v: html.escape(v, quote=True)
    t = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", t, count=1)
    for sel, val in [('name="description"', desc), ('property="og:title"', title), ('property="og:description"', desc),
                     ('name="twitter:title"', title), ('name="twitter:description"', desc), ('property="og:url"', url),
                     ('property="og:image"', f"{SITE}/{img}"), ('name="twitter:image"', f"{SITE}/{img}"), ('property="og:image:alt"', img_alt)]:
        t = re.sub(r"<meta " + re.escape(sel) + r' content="[^"]*">', f'<meta {sel} content="{esc(val)}">', t, count=1)
    t = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', t, count=1)
    t = t.replace("<body", "<body", 1)
    i = t.index(">", t.index("<body")) + 1
    t = t[:i] + "\n" + text_block(h1, desc, extra) + t[i:]
    os.makedirs(os.path.join(ROOT, "p"), exist_ok=True)
    open(os.path.join(ROOT, "p", slug + ".html"), "w", encoding="utf-8").write(t)
    return slug

built = []
for slug, (key, sec) in PAGES.items():
    title, desc = SEO[key]
    built.append(page(slug, title, desc, title.split(" | ")[0], llms_section(sec), f"{title.split(' - ')[0]}, President's Work"))
for pid, P in WORK.items():
    if P.get("art") != "photo": continue
    scope = ", ".join(P.get("scope", [])[:2]) or "Case study"
    title = f"{P['name']} - {scope} | President's Work"
    d = (P.get("tagline") or P.get("overview") or "").strip()
    desc = (d + " A President's Work case study" + (": " + P["services"] + "." if P.get("services") else "."))[:300]
    built.append(page(pid, title, desc, P["name"], "\n".join(P.get("body", [])), f"{P['name']}, a President's Work case study"))

vj = os.path.join(ROOT, "vercel.json"); v = json.load(open(vj))
v["rewrites"] = [{"source": "/" + s, "destination": f"/p/{s}.html"} for s in built] + [{"source": "/index", "destination": "/p/work.html"}, {"source": "/founders", "destination": "/"}, {"source": "/leadership", "destination": "/"}]
json.dump(v, open(vj, "w"), indent=2)
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>' + SITE + '/</loc></url>\n' + "".join(f"  <url><loc>{SITE}/{s}</loc></url>\n" for s in built) + "</urlset>\n"
open(os.path.join(ROOT, "sitemap.xml"), "w").write(sm)
print("built", len(built), "front doors:", " ".join(built))
