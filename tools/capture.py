# Runs the PDF build scripts with a recording version of lib, and returns structured page content.
import sys, types, importlib, json, os, re
SPREAD = os.path.join(os.path.dirname(__file__), '..', 'spread')
sys.path.insert(0, SPREAD)
import lib as real

def run(script):
    cur = []
    pages = {}
    m = types.ModuleType('lib')
    for k in dir(real):
        if not k.startswith('__'):
            setattr(m, k, getattr(real, k))
    def left(kicker, h1, hero, herocap, qs, extra="", role=None, top=30):
        cur.append(dict(t='left', kicker=kicker, h1=h1, hero=hero, herocap=herocap,
                        qs=[dict(title=a, p=b, extra=c) for a, b, c in qs], role=role or []))
        return ''
    def fig(x, y, w, src, caps, marks=(), h=None, fit="contain"):
        cur.append(dict(t='fig', x=x, y=y, w=w, src=src, caps=[[n, t] for n, t in caps], marks=[list(m_) for m_ in marks]))
        return ''
    def box(x, y, w, html, cls="card", h=None):
        cur.append(dict(t='box', x=x, y=y, w=w, html=html, cls=cls))
        return ''
    def page(num, hdr_l, hdr_r, body, extra_css=""):
        pages[num] = dict(num=num, hdr_l=hdr_l, hdr_r=hdr_r, items=list(cur))
        cur.clear()
        return ''
    def opener(num, code, title, tags, overview, facts, figures, imgs, hdr_r, idx, ims_html=None):
        pages[num] = dict(num=num, opener=dict(code=code, title=title, tags=tags, overview=overview,
                          facts=facts, figures=figures, imgs=[i for i, _ in imgs], idx=idx))
        cur.clear()
        return ''
    m.left, m.fig, m.box, m.page, m.opener = left, fig, box, page, opener
    sys.modules['lib'] = m
    src = open(os.path.join(SPREAD, script)).read()
    src = re.sub(r"\nfor n, h in pages\.items\(\):[\s\S]*$", "\n", src)
    src = src.replace('t = open("p06.html")', 't = open(os.path.join(SPREAD,"p06.html"))')
    g = {'__name__': 'capture', 'os': os, 'SPREAD': SPREAD}
    old = os.getcwd(); os.chdir(SPREAD)
    try:
        exec(compile(src, script, 'exec'), g)
    finally:
        os.chdir(old)
    return pages

if __name__ == '__main__':
    out = {}
    for s in ['build_mhh.py', 'build_acl.py', 'build_aob.py', 'build_prjc.py']:
        for k, v in run(s).items():
            out[k] = v
    json.dump(out, open('content.json', 'w'), indent=1)
    for k in sorted(out):
        v = out[k]
        print(k, 'opener' if 'opener' in v else [i['t'] for i in v['items']])
