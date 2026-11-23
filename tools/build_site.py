"""Static site generator for the Chukwunedum Mejeha BIM portfolio.

Reads content.json (captured from the A3 PDF build) and boxes.json (element
geometry measured from the rendered PDF pages), converts the evidence images
to WebP and writes a plain HTML/CSS/JS site into ../dist.
"""
import json, os, re, shutil, html, hashlib, datetime
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SRC_IMG = os.environ.get('PORTFOLIO_IMG', os.path.join(SITE, '..', 'spread', 'img'))
DIST = os.path.join(SITE, 'dist')
ASSETS = os.path.join(SITE, 'assets')

C = json.load(open(os.path.join(SITE, 'content.json')))
BOX = json.load(open(os.path.join(SITE, 'boxes.json')))

NAME = "Chukwunedum Mejeha"
EMAIL = "mejehaarc@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/nedum-mejeha"
GITHUB = "https://github.com/mej94"
REPO = "https://github.com/mej94/bim-portfolio"
SITE_URL = "https://chukwunedum-mejeha.vercel.app"

PROJECTS = [
    dict(slug="mhh", code="MHH", num="01", opener=5, sheets=[6, 7, 8, 9, 10, 11, 12],
         where="New South Wales, Australia", line="430 live clashes triaged into 94 owned issues"),
    dict(slug="acl", code="ACL", num="02", opener=13, sheets=[14, 15, 16, 17],
         where="United Kingdom", line="Bare model to a 16 sheet P01 issue"),
    dict(slug="aob", code="AOB", num="03", opener=18, sheets=[19, 20, 21],
         where="Austral, New South Wales, Australia", line="62 rooms classified, IFC4 validated"),
    dict(slug="prjc", code="PRJC", num="04", opener=22, sheets=[23, 24, 25],
         where="Notional UK site", line="Warnings from 56 to 7, 609 elements purged"),
]

# ---------------------------------------------------------------- page 09
# The triage page was hand built in the PDF, so its content is restated here.
C['9'] = dict(num=9, hdr_l="<b>MHH</b>&nbsp;&nbsp;Mental Health Hospital&nbsp;&nbsp;·&nbsp;&nbsp;Coordination 4 of 7",
              hdr_r="MHH-MEJ-ZZ-ZZ-M3-Z-0001.nwf&nbsp;&nbsp;·&nbsp;&nbsp;Run 4&nbsp;&nbsp;·&nbsp;&nbsp;22 Nov 2026", items=[
    dict(t='left', kicker="Clash triage", h1="Triage of 430 live clashes into 94 owned issues",
         hero='<span class="n">430</span><span class="arr">→</span><span class="n">94</span>',
         herocap="live clashes in Run 4, grouped into owned issues across 10 tests",
         qs=[dict(title="What was wrong", p="With the noise filtered out, Run 4 still held 430 live clashes. A flat list that long gets opened once in a meeting and then nobody acts on it.", extra=""),
             dict(title="What I decided", p="Group clashes by system pair and location, then give each group a single owner using services precedence: structure stays put, ducts take priority over trays. Priority follows penetration depth, High above 100 mm and Medium from 25 to 100 mm. When the fix is a design decision, it goes to the engineer as an RFI instead of being modelled away.", extra=""),
             dict(title="What changed", p="94 issues, 41 of them High. Two RFIs carry 71 issues between them. Every line has an owner, an action and a due date in the issue log and the BCF file.",
                  extra='<table class="own"><tr><th>Owner</th><th>Issues</th><th>Clashes</th></tr><tr><td>Electrical</td><td>39</td><td>134</td></tr><tr><td>Mechanical and Electrical, shared</td><td>30</td><td>132</td></tr><tr><td>Electrical and Fire, shared</td><td>13</td><td>30</td></tr><tr><td>Mechanical</td><td>9</td><td>108</td></tr><tr><td>Architect, Structural, Hydraulic</td><td>3</td><td>26</td></tr><tr class="t"><td>Total</td><td>94</td><td>430</td></tr></table>'),
             dict(title="What I would do next", p="Run 5 after the RFI 002 tray zone study. One answer on the tray route should close most of its 69 linked issues at once.", extra="")],
         role=[["Model source", "NSW course dataset, 7 discipline models"], ["My role", "BIM coordination: federation, clash tests, triage, issue log, RFIs"], ["Tools", "Navisworks Manage 2027, Revit 2027, Excel, BCF 2.1"]]),
    dict(t='fig', src="mhh10.jpg", marks=[[1, 53, 42]], caps=[[1, "Group T01-C2. A supply duct takeoff (green) passes through the web of a roof beam (red), grid Q to 2, roof level. <span class='src mono'>MHH_10</span>"]]),
    dict(t='box', cls='card', html='<div class="lab">Worked example · how an issue is written</div><div class="id mono">MHH-ISS-002&nbsp;&nbsp;/&nbsp;&nbsp;T01-C2</div><div class="tags"><span class="tag hi">HIGH</span><span class="tag">STRUCTURAL</span><span class="tag">MHH-RFI-001</span></div><p>Walkway and roof level. Ten supply duct takeoffs pass through the webs of 460UB67, 410UB54, 360UB51 and 310UB40 beams. Median penetration 76 mm, maximum 155 mm, against a 25 mm tolerance.</p><p>Each duct is shallower than the beam it crosses, so a web opening may beat a reroute. Only the engineer can approve one, so the question goes to Structural instead of being modelled away.</p><dl><dt>Action</dt><dd>Confirm web opening size, position and stiffening, or relocate.</dd><dt>Due</dt><dd class="mono">2026-11-29</dd><dt>If held</dt><dd>These duct runs cannot be released for fabrication.</dd></dl><div class="weak">The usual version: <s>“Clash between duct and beam at roof.”</s></div>'),
    dict(t='fig', src="mhh09.jpg", marks=[[2, 41, 29.7], [3, 74, 10.7]], caps=[[2, "T08 CEIL v SERV in Clash Detective. Group T08-G01 holds 42 clashes under one name and one owner."], [3, "22 groups, all Active, none left as New. <span class='src mono'>MHH_09</span>"]]),
    dict(t='fig', src="mhh15.jpg", marks=[[4, 84, 15]], caps=[[4, "Issue log filtered to High priority: owner, required action, RFI and due date on every line. MHH-ISS-002 links to RFI 001. <span class='src mono'>MHH_15 · MHH-MEJ-ZZ-ZZ-SH-Z-0001_IssueLog_Run4.xlsx</span>"]]),
])

# ---------------------------------------------------------------- images
IMG_DONE = {}
os.makedirs(os.path.join(DIST, 'img'), exist_ok=True)


def webp(src, maxw=2000, q=80, size=None, name=None):
    key = (src, size, name)
    if key in IMG_DONE:
        return IMG_DONE[key]
    im = Image.open(os.path.join(SRC_IMG, src)).convert('RGB')
    if size:
        im = im.resize(size, Image.LANCZOS)
    big = im.width > 5000
    mw = 3200 if big else maxw
    if im.width > mw:
        im = im.resize((mw, round(im.height * mw / im.width)), Image.LANCZOS)
    out = (name or os.path.splitext(src)[0]) + '.webp'
    im.save(os.path.join(DIST, 'img', out), 'WEBP', quality=q, method=6)
    IMG_DONE[key] = (out, im.width, im.height)
    return IMG_DONE[key]


def strip(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()


def clean(h):
    h = re.sub(r'font-size:[^;"]*;?', '', h or '')
    h = re.sub(r'line-height:[^;"]*;?', '', h)
    h = re.sub(r' style=""', '', h)
    return h


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', strip(s).lower()).strip('-')


def count_spans(h):
    """Mark plain numbers inside hero spans for the count-up animation."""
    return re.sub(r'<span class="n">([\d,\.]+)</span>', r'<span class="n" data-count="\1">\1</span>', h)


# ---------------------------------------------------------------- layout
CW = (390 - 55) / 12
X0 = 113.75  # left edge of the evidence area (column 4)


def gcol(x, w):
    s = round((x - X0) / (CW + 5)) + 1
    n = max(1, round((w + 5) / (CW + 5)))
    s = max(1, min(9, s))
    return s, min(10, s + n)


def fig_html(it, eager=False):
    f, w, h = webp(it['src'])
    marks = "".join(f'<span class="mk" style="left:{l}%;top:{t}%">{n}</span>' for n, l, t in it.get('marks', []))
    alt = html.escape(strip(it['caps'][0][1]) if it['caps'] else '')
    caps = "".join(f'<figcaption class="cap">{f"<span class=num>{n}</span>" if n else ""}<span>{t}</span></figcaption>' for n, t in it['caps'])
    return (f'<figure class="fig reveal"><div class="mat"><button class="zoom" data-full="/img/{f}" aria-label="Enlarge image">'
            f'<img src="/img/{f}" width="{w}" height="{h}" alt="{alt}" loading="{"eager" if eager else "lazy"}" decoding="async">{marks}'
            f'<span class="zi" aria-hidden="true">⤢</span></button></div>{caps}</figure>')


def slider_html(a, b):
    ia = Image.open(os.path.join(SRC_IMG, a['src']))
    fa, w, h = webp(a['src'])
    fb, _, _ = webp(b['src'], size=ia.size, name=os.path.splitext(b['src'])[0] + '_eq')
    caps = "".join(f'<figcaption class="cap"><span class="ba">{lab}</span><span>{t}</span></figcaption>'
                   for lab, it in (("Before", a), ("After", b)) for _, t in it['caps'])
    alt = html.escape(strip(a['caps'][0][1]))
    return (f'<figure class="fig reveal"><div class="mat"><div class="ba-slider" style="--pos:50%" tabindex="0" role="slider" aria-label="Before and after comparison" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50">'
            f'<img src="/img/{fb}" width="{w}" height="{h}" alt="After: {alt}" loading="lazy">'
            f'<div class="ba-before"><img src="/img/{fa}" width="{w}" height="{h}" alt="Before: {alt}" loading="lazy"></div>'
            f'<div class="ba-handle"><span>◀ ▶</span></div><span class="ba-l">BEFORE</span><span class="ba-r">AFTER</span></div></div>{caps}'
            f'<div class="ba-hint mono">Drag to compare</div></figure>')


def box_html(it):
    cls = it.get('cls') or ''
    return f'<div class="bx {cls} reveal">{clean(it["html"])}</div>'


def is_pair(a, b):
    if a['t'] != 'fig' or b['t'] != 'fig':
        return False
    sa, sb = a['src'], b['src']
    ok = (sa.replace('before', 'after') == sb) or (sa, sb) in {('aob22w.jpg', 'aob23w.jpg'), ('aob28atb.jpg', 'aob28tb.jpg')}
    if not ok:
        return False
    A = Image.open(os.path.join(SRC_IMG, sa)).size
    B = Image.open(os.path.join(SRC_IMG, sb)).size
    return abs(A[0] / A[1] - B[0] / B[1]) < 0.03


def layout(num):
    p = C[str(num)]
    items = [i for i in p['items'] if i['t'] != 'left']
    geo = BOX[str(num)]
    els = []
    for it, (x, y, w, h, _) in zip(items, geo):
        els.append(dict(it=it, x=x, y=y, w=w, h=h))
    # merge before/after pairs into sliders
    out, i = [], 0
    while i < len(els):
        e = els[i]
        if i + 1 < len(els) and is_pair(e['it'], els[i + 1]['it']):
            f = els[i + 1]
            x0, y0 = min(e['x'], f['x']), min(e['y'], f['y'])
            x1, y1 = max(e['x'] + e['w'], f['x'] + f['w']), max(e['y'] + e['h'], f['y'] + f['h'])
            # a side by side pair keeps one image width so the slider is not oversized
            w = (x1 - x0) if e['y'] != f['y'] else max(e['w'], f['w']) * 1.6
            out.append(dict(kind='slider', a=e['it'], b=f['it'], x=x0, y=y0, w=min(w, x1 - x0), h=y1 - y0))
            i += 2
        else:
            out.append(dict(kind=e['it']['t'], it=e['it'], x=e['x'], y=e['y'], w=e['w'], h=e['h']))
            i += 1
    for e in out:
        e['c0'], e['c1'] = gcol(e['x'], e['w'])
    # bands
    out.sort(key=lambda e: (round(e['y']), e['x']))
    bands, cur, bottom = [], [], -1
    for e in out:
        if cur and e['y'] >= bottom - 2:
            bands.append(cur); cur = []; bottom = -1
        cur.append(e); bottom = max(bottom, e['y'] + e['h'])
    if cur:
        bands.append(cur)
    res = ""
    first = True
    for band in bands:
        stacks = []
        for e in sorted(band, key=lambda e: e['c0']):
            for s in stacks:
                if e['c0'] < s['c1'] and e['c1'] > s['c0']:
                    s['els'].append(e); s['c0'] = min(s['c0'], e['c0']); s['c1'] = max(s['c1'], e['c1']); break
            else:
                stacks.append(dict(c0=e['c0'], c1=e['c1'], els=[e]))
        # stretch stacks to fill all nine columns when there is a gap at the end
        stacks.sort(key=lambda s: s['c0'])
        if stacks[-1]['c1'] < 10 and len(stacks) > 1:
            stacks[-1]['c1'] = 10
        res += '<div class="band">'
        for s in stacks:
            res += f'<div class="stack" style="--c0:{s["c0"]};--c1:{s["c1"]}">'
            for e in sorted(s['els'], key=lambda e: e['y']):
                if e['kind'] == 'fig':
                    res += fig_html(e['it'], eager=first); first = False
                elif e['kind'] == 'slider':
                    res += slider_html(e['a'], e['b'])
                else:
                    res += box_html(e['it'])
            res += '</div>'
        res += '</div>'
    return res


# ---------------------------------------------------------------- shell
def head(title, desc, path):
    return f"""<!doctype html>
<html lang="en-GB" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="author" content="{NAME}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{SITE_URL}/img/og.webp">
<meta name="theme-color" content="#1E1F22">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={VER}">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t;else if(matchMedia('(prefers-color-scheme: dark)').matches)document.documentElement.dataset.theme='dark'}}catch(e){{}}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"><span></span></div>
<header class="nav">
 <a class="brand" href="/" aria-label="Home"><span class="mono">CM</span><span class="bn">Chukwunedum Mejeha</span></a>
 <nav class="links" aria-label="Main">
  <a href="/#projects">Projects</a><a href="/#about">About</a><a href="/#skills">Skills</a><a href="/#experience">Experience</a><a href="/#contact">Contact</a>
 </nav>
 <div class="tools">
  <button class="kbtn" data-palette aria-label="Open command palette"><span>Search</span><kbd class="mono">Ctrl K</kbd></button>
  <button class="ibtn" data-theme-toggle aria-label="Toggle dark mode"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9z" fill="currentColor"/></svg></button>
 </div>
</header>
<main id="main">
"""


def footer():
    stack = ["HTML5", "CSS custom properties", "CSS grid", "Vanilla JS (ES modules)", "Canvas 2D", "IntersectionObserver",
             "Python build pipeline", "Pillow, WebP", "Playwright", "Vercel", "GitHub"]
    chips = "".join(f'<li>{s}</li>' for s in stack)
    return f"""</main>
<footer class="foot">
 <div class="wrap fgrid">
  <div>
   <div class="kicker">Built, not templated</div>
   <p class="fbig">Designed and developed by <b>{NAME}</b></p>
   <p class="fsmall">No framework and no page builder. A Python pipeline reads the same source data as the A3 portfolio PDF, measures each page layout in a headless browser, converts every screenshot to WebP and writes this static site. The hero model is drawn live in Canvas 2D.</p>
   <ul class="chips mono">{chips}</ul>
  </div>
  <div class="fcol">
   <div class="sec">Find me</div>
   <a href="mailto:{EMAIL}">{EMAIL}</a>
   <a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
   <a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
   <a href="{REPO}" target="_blank" rel="noopener">Source code for this site</a>
  </div>
  <div class="fcol">
   <div class="sec">Build</div>
   <span class="mono bline">v{VER}</span>
   <span class="mono bline">{BUILD_DATE}</span>
   <span class="mono bline">{{PAGES}} pages · {{IMGS}} images</span>
   <span class="mono bline">0 frameworks · 0 trackers</span>
  </div>
 </div>
 <div class="wrap fbar"><span>© 2026 {NAME}</span><span class="mono">Press <kbd>Ctrl K</kbd> to navigate · <kbd>T</kbd> for theme</span></div>
</footer>
<div class="lightbox" hidden><button class="lb-x" aria-label="Close">×</button><div class="lb-stage"><img alt=""></div><div class="lb-bar mono"><span class="lb-cap"></span><span>Scroll to zoom · drag to pan · Esc to close</span></div></div>
<div class="palette" hidden><div class="pal-box" role="dialog" aria-label="Command palette"><input class="pal-in" placeholder="Jump to a project, a section or an action" aria-label="Search"><ul class="pal-list" role="listbox"></ul><div class="pal-foot mono"><span>↑ ↓ to move</span><span>Enter to open</span><span>Esc to close</span></div></div></div>
<div class="toast mono" role="status" aria-live="polite"></div>
<script type="module" src="/assets/site.js?v={VER}"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- project page
def opener_html(p):
    o = C[str(p['opener'])]['opener']
    figs = ""
    for v, l in o['figures']:
        v2 = re.sub(r'^([\d,]+)$', r'<span data-count="\1">\1</span>', v)
        v2 = re.sub(r'^([\d,]+) → ([\d,]+)$', r'<span data-count="\1">\1</span><i>→</i><span data-count="\2">\2</span>', v2)
        figs += f'<div class="fg"><div class="fv">{v2}</div><div class="fl">{l}</div></div>'
    facts = "".join(f'<dt>{a}</dt><dd>{b}</dd>' for a, b in o['facts'])
    imgs = ""
    for i, src in enumerate(o['imgs']):
        f, w, h = webp(src, maxw=2400, q=82)
        imgs += f'<img src="/img/{f}" width="{w}" height="{h}" alt="{o["title"]}, render {i + 1}" class="{"on" if i == 0 else ""}" {"fetchpriority=high" if i == 0 else "loading=lazy"}>'
    tags = "".join(f'<li>{t.strip()}</li>' for t in o['tags'].split('·'))
    return f"""<section class="op">
 <div class="op-media" data-fade>{imgs}<div class="op-grad"></div></div>
 <div class="wrap op-in">
  <a class="back mono" href="/#projects">← All projects</a>
  <div class="kicker">Project {p['num']} · {p['where']}</div>
  <h1 class="op-t">{o['title']}</h1>
  <div class="op-code mono" data-scramble>{o['code']}</div>
  <ul class="op-tags mono">{tags}</ul>
 </div>
</section>
<section class="wrap op-body">
 <div class="op-ov reveal"><p>{o['overview']}</p><dl class="facts">{facts}</dl></div>
 <div class="op-figs reveal">{figs}</div>
</section>"""


def sheet_html(num, idx, total):
    p = C[str(num)]
    L = next(i for i in p['items'] if i['t'] == 'left')
    qs = "".join(f'<div class="q"><h3><span class="mono">0{i + 1}</span>{q["title"]}</h3><p>{q["p"]}</p>{clean(q.get("extra", ""))}</div>'
                 for i, q in enumerate(L['qs']))
    role = "".join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in L.get('role', []))
    sid = slug(L['kicker'])
    hdr_r = p.get('hdr_r', '')
    return sid, L['kicker'], f"""<section class="sheet" id="{sid}">
 <div class="wrap">
  <div class="sh-hdr mono"><span>{idx:02d} / {total:02d}</span><span>{hdr_r}</span></div>
  <div class="sh-grid">
   <aside class="sh-left">
    <div class="kicker">{L['kicker']}</div>
    <h2>{L['h1']}</h2>
    <div class="hero">{count_spans(L['hero'])}</div>
    <div class="herocap">{L['herocap']}</div>
    <div class="qs">{qs}</div>
    {f'<dl class="role">{role}</dl>' if role else ''}
   </aside>
   <div class="sh-ev">{layout(num)}</div>
  </div>
 </div>
</section>"""


def project_page(k):
    p = PROJECTS[k]
    o = C[str(p['opener'])]['opener']
    secs, toc = "", []
    for i, n in enumerate(p['sheets']):
        sid, kick, h = sheet_html(n, i + 1, len(p['sheets']))
        secs += h; toc.append((sid, kick))
    tocs = "".join(f'<a href="#{s}"><span class="mono">{i + 1:02d}</span>{t}</a>' for i, (s, t) in enumerate(toc))
    prv, nxt = PROJECTS[k - 1], PROJECTS[(k + 1) % 4]
    pn = lambda q: C[str(q['opener'])]['opener']['title']
    nav = f"""<nav class="pn wrap" aria-label="More projects">
 <a href="/{prv['slug']}/" class="pn-a"><span class="mono">← Project {prv['num']}</span><b>{pn(prv)}</b></a>
 <a href="/{nxt['slug']}/" class="pn-a r"><span class="mono">Project {nxt['num']} →</span><b>{pn(nxt)}</b></a>
</nav>"""
    body = (opener_html(p) + f'<div class="toc" data-toc><div class="wrap toc-in"><span class="mono toc-l">{p["code"]}</span>{tocs}</div></div>'
            + secs + nav)
    title = f"{o['title']} · {NAME}, BIM Technician"
    page = head(title, strip(o['overview'])[:155], f"/{p['slug']}/") + body + footer()
    return page, toc


# ---------------------------------------------------------------- home page
def home():
    cards = ""
    for p in PROJECTS:
        o = C[str(p['opener'])]['opener']
        f, w, h = webp(o['imgs'][0], maxw=2400, q=82)
        figs = "".join(f'<div><b>{v}</b><span>{l}</span></div>' for v, l in o['figures'][:3])
        tags = "".join(f'<li>{t.strip()}</li>' for t in o['tags'].split('·')[:4])
        cards += f"""<a class="pc reveal" href="/{p['slug']}/">
 <div class="pc-img"><img src="/img/{f}" width="{w}" height="{h}" alt="{o['title']} render" loading="lazy"><span class="pc-code mono">{o['code']}</span></div>
 <div class="pc-txt">
  <div class="pc-k mono"><span>{p['num']} · {p['code']}</span><span>{p['where']}</span></div>
  <h3>{o['title']}</h3>
  <p class="pc-line">{p['line']}</p>
  <ul class="pc-tags mono">{tags}</ul>
  <div class="pc-figs">{figs}</div>
  <span class="pc-go mono">Open project <i>→</i></span>
 </div>
</a>"""
    skills = [("Coordination", "Federation on a shared origin, clash matrices by discipline pair, tolerances by trade, triage by owner and precedence, issue writing, RFIs, BCF 2.1"),
              ("Information", "ISO 19650 container naming, status and revision codes, Uniclass 2015 classification, shared parameters, IFC4 export and validation, BEP and document registers"),
              ("Modelling and production", "Architectural modelling in Revit from shell to detail: walls, floors, roofs, stairs and attic, parametric families, rooms and areas, ISO named sheet sets, view templates and title blocks"),
              ("Model health", "Warning audits with written residues, purge cascades, imported CAD removal, relationship fixes before geometry, guarded scripted changes with rollback")]
    sk = "".join(f'<div class="skc reveal"><span class="mono">0{i + 1}</span><h3>{a}</h3><p>{b}</p></div>' for i, (a, b) in enumerate(skills))
    mat = [("Federation and clash detection", 1, 0, 0, 0), ("Issue management, RFIs, BCF", 1, 0, 0, 0), ("Common data environment", 1, 0, 0, 1),
           ("ISO 19650 naming and status", 1, 1, 1, 1), ("Classification, Uniclass 2015", 0, 0, 1, 0), ("IFC export and validation", 0, 0, 1, 0),
           ("Rooms, areas, schedules", 0, 1, 1, 0), ("Sheet sets and title blocks", 0, 1, 1, 0), ("Parametric families", 0, 1, 0, 0),
           ("Model audit and cleanup", 0, 0, 1, 1), ("BEP and document register", 0, 0, 0, 1)]
    mrows = "".join('<tr><th scope="row">' + r[0] + '</th>' + "".join(
        f'<td data-p="{PROJECTS[j]["slug"]}">{"<span class=dot></span>" if v else ""}</td>' for j, v in enumerate(r[1:])) + '</tr>' for r in mat)
    mhead = "".join(f'<th scope="col"><a href="/{p["slug"]}/" data-p="{p["slug"]}">{p["code"]}</a></th>' for p in PROJECTS)
    work = [("2024 to date", "BIM Technician", "Mejarc Integrated Services", "Model coordination, information management and drawing production; the four projects on this site."),
            ("2023 to 2024", "CAD Designer", "Wren Living Ltd", "Drawing production for a residential developer."),
            ("2020 to 2023", "Architectural Technologist", "Barkwaj Consult Ltd", ""),
            ("2019 to 2020", "Design Technician", "SENL (Army Engineers)", "")]
    wk = "".join(f'<li class="reveal"><span class="yr mono">{y}</span><div><h3>{r}</h3><div class="co">{c}</div>{f"<p>{d}</p>" if d else ""}</div></li>' for y, r, c, d in work)
    cert = ["Autodesk BIM Certificate for Architecture", "Autodesk BIM Certificate for AECO", "Introduction to ISO Global BIM Standards", "NEBOSH Construction"]
    sw = [("Revit 2027", "Modelling, families, schedules, sheets, IFC"), ("Navisworks Manage 2027", "Federation, Clash Detective, viewpoints"),
          ("Autodesk Construction Cloud", "Docs, Design Collaboration, packages"), ("BIMcollab Zoom", "IFC property checks"),
          ("IfcOpenShell", "Schema and rule validation"), ("Excel, BCF 2.1", "Issue logs and exchange"), ("Python, pyRevit", "Scripted, logged model changes")]
    std = [("ISO 19650 parts 1 and 2", "Container naming, status and revision codes, CDE states. BS EN ISO with the UK National Annex on ACL and PRJC, AS ISO on the Australian projects, MHH and AOB."),
           ("Uniclass 2015", "SL codes on rooms, Pr codes on door types, carried into IFC. Aqualand Office Building."),
           ("IFC4 Reference View", "Exported, then checked for schema and for property content. Aqualand Office Building."),
           ("BCF 2.1", "94 issue topics exchanged with the clash log. Mental Health Hospital."),
           ("Approved Documents B and K", "Protected stair, FD20 door and stair headroom checks. Aussi Close.")]
    photo, pw, ph = webp('photo.jpg', maxw=900, q=82)
    body = f"""<section class="hero-s" id="top">
 <canvas id="bim" aria-hidden="true"></canvas>
 <div class="hero-grid wrap">
  <div class="hero-txt">
   <div class="kicker">BIM Technician · United Kingdom · open to UK and Australian roles</div>
   <h1 class="name"><span>Chukwunedum</span><span>Mejeha</span></h1>
   <p class="lede">Coordination, information management and drawing production, shown through four Revit models and the decisions that made them fit to share.</p>
   <div class="ctas"><a class="btn pri" href="#projects">See the four projects</a><a class="btn" href="#contact">Get in touch</a></div>
  </div>
  <div class="term reveal" aria-label="Summary of results">
   <div class="term-bar"><i></i><i></i><i></i><span class="mono">mejeha@portfolio: ~/2027</span></div>
   <pre class="term-body mono" data-typer></pre>
  </div>
 </div>
 <div class="hero-foot wrap mono"><span>Live model: hover to orbit</span><span class="hz">Orange points are clashes</span><span>Scroll ↓</span></div>
</section>

<section class="stats wrap" aria-label="Headline numbers">
 <div class="st reveal"><b><span data-count="7">7</span></b><span>discipline models federated on one origin</span></div>
 <div class="st reveal"><b><span data-count="430">430</span><i>→</i><span data-count="94">94</span></b><span>live clashes turned into owned issues</span></div>
 <div class="st reveal"><b><span data-count="62">62</span></b><span>rooms classified and exported to IFC4, 0 schema errors</span></div>
 <div class="st reveal"><b><span data-count="56">56</span><i>→</i><span data-count="7">7</span></b><span>warnings, each one left with a written reason</span></div>
</section>

<section class="wrap sect" id="projects">
 <div class="sect-h reveal"><div class="kicker">Selected work</div><h2>Four projects</h2><p>Each project page puts the number beside the decision that moved it, in the same four questions: what was wrong, what I decided, what changed, and what I would do next.</p></div>
 <div class="pcs">{cards}</div>
</section>

<section class="wrap sect about" id="about">
 <div class="ab-photo reveal"><img src="/img/{photo}" width="{pw}" height="{ph}" alt="Portrait of {NAME}" loading="lazy"></div>
 <div class="ab-txt">
  <div class="kicker">About me</div>
  <h2>BIM technician specialising in modelling, coordination and information quality</h2>
  <div class="ab-cols reveal">
   <p>I am a BIM technician based in the United Kingdom, working at Mejarc Integrated Services since 2024. Before that I drew for a residential developer at Wren Living, spent three years as an architectural technologist at Barkwaj Consult, and started out as a design technician with an army engineers unit. I hold an MSc in Project Management for construction and the built environment, and a B.Tech in Architecture.</p>
   <p>Most portfolios show finished buildings. This one shows the state the information was in, and what I changed so that a team could use it. Clash counts mean nothing until each clash has an owner, a warning count means nothing until the leftovers have reasons, and a valid IFC means nothing until someone opens it and checks the data.</p>
   <p>I work in Revit 2027 and Navisworks Manage, publish through Autodesk Construction Cloud, and script the repetitive parts so every change is logged and reversible.</p>
  </div>
  <blockquote class="pull reveal">A warning count of zero usually means someone deleted something that mattered. I would rather show you the seven I kept and why.</blockquote>
 </div>
</section>

<section class="wrap sect" id="skills">
 <div class="sect-h reveal"><div class="kicker">What I bring</div><h2>Skills, and where to find the proof</h2><p>Hover a row to see which projects carry the evidence. Click a project code to open it.</p></div>
 <div class="skg">{sk}</div>
 <div class="mx-wrap reveal"><table class="mx"><thead><tr><th scope="col">Skill</th>{mhead}</tr></thead><tbody>{mrows}</tbody></table></div>
 <div class="sw reveal"><div class="sec">Software</div><ul>{''.join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in sw)}</ul></div>
</section>

<section class="wrap sect" id="experience">
 <div class="sect-h reveal"><div class="kicker">Experience</div><h2>Professional experience</h2></div>
 <div class="xp">
  <ol class="tl">{wk}</ol>
  <div class="xp-side">
   <div class="reveal"><div class="sec">Education</div><dl class="ct2"><dt>MSc</dt><dd>Project Management (Construction and Built Environment)</dd><dt>B.Tech</dt><dd>Architecture</dd></dl></div>
   <div class="reveal"><div class="sec">Certifications</div><ul class="cl">{''.join(f'<li>{c}</li>' for c in cert)}</ul></div>
   <div class="reveal"><div class="sec">Languages</div><ul class="cl"><li>English</li></ul></div>
  </div>
 </div>
 <div class="stds"><div class="kicker">Standards I work to</div><div class="std-g">{''.join(f'<div class="std reveal"><h3>{n}</h3><p>{d}</p></div>' for n, d in std)}</div></div>
</section>

<section class="contact" id="contact">
 <div class="wrap ct-in">
  <div class="kicker">Contact</div>
  <h2 class="ct-h">Let's talk about your next model.</h2>
  <p class="ct-p">Based in the United Kingdom. Open to BIM technician and modeller roles in the UK and Australia from 2027.</p>
  <div class="ct-links">
   <button class="ct-mail mono" data-copy="{EMAIL}"><span>{EMAIL}</span><em>Copy</em></button>
   <a class="btn pri" href="mailto:{EMAIL}">Email me</a>
   <a class="btn" href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
   <a class="btn" href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
  </div>
 </div>
</section>
"""
    return head(f"{NAME} · BIM Technician portfolio", "BIM technician portfolio: federation and clash triage, ISO 19650 information management, Uniclass and IFC4, Revit modelling and model health, across four projects.", "/") + body + footer()


# ---------------------------------------------------------------- write
VER = hashlib.sha1(json.dumps(C, sort_keys=True).encode() + b''.join(open(os.path.join(ASSETS, f), 'rb').read() for f in sorted(os.listdir(ASSETS)))).hexdigest()[:7]
BUILD_DATE = datetime.date.today().isoformat()

if __name__ == '__main__':
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'img'))
    pages = {'index.html': home()}
    palette = [dict(t="Home", h="/", g="Pages")]
    for k, p in enumerate(PROJECTS):
        pg, toc = project_page(k)
        pages[f"{p['slug']}/index.html"] = pg
        o = C[str(p['opener'])]['opener']
        palette.append(dict(t=f"{o['title']}", h=f"/{p['slug']}/", g="Projects", s=p['code']))
        for sid, kick in toc:
            palette.append(dict(t=f"{kick}", h=f"/{p['slug']}/#{sid}", g=o['title'], s=p['code']))
    for sec in ["projects", "about", "skills", "experience", "contact"]:
        palette.append(dict(t=sec.capitalize(), h=f"/#{sec}", g="Home"))
    # og image
    og = Image.open(os.path.join(SRC_IMG, 'mhh_render0.jpg')).convert('RGB')
    og = og.resize((1200, round(og.height * 1200 / og.width))).crop((0, 0, 1200, 630))
    og.save(os.path.join(DIST, 'img', 'og.webp'), 'WEBP', quality=80)
    nimg = len(os.listdir(os.path.join(DIST, 'img')))
    for path, h in pages.items():
        fp = os.path.join(DIST, path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        h = h.replace('{PAGES}', str(len(pages))).replace('{IMGS}', str(nimg))
        open(fp, 'w').write(h)
    shutil.copytree(ASSETS, os.path.join(DIST, 'assets'))
    json.dump(palette, open(os.path.join(DIST, 'assets', 'nav.json'), 'w'))
    for f in ['favicon.svg', 'vercel.json', '404.html', 'robots.txt']:
        if os.path.exists(os.path.join(SITE, 'static', f)):
            shutil.copy(os.path.join(SITE, 'static', f), DIST)
    tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(DIST) for f in fs)
    print(f"built {len(pages)} pages, {nimg} images, {tot / 1e6:.1f} MB, v{VER}")
