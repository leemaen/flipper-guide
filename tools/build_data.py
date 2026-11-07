"""Projiziert die Tisch-Geometrie in die Spielfeldbilder und schreibt app/data/<tisch>.json.

Aufruf (im Projektordner):  py -3 -I tools/build_data.py <tisch> [--check]
Konfiguration je Tisch: content/<tisch>/build.json (Ansichten, Homographien, Bildausschnitte).
--check rendert Prüfbilder nach _quellen/pages/check_<tisch>_<ansicht>.png
"""
import json, math, os, sys, shutil
sys.path.insert(0, os.path.dirname(__file__))
from homography import apply
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = next((a for a in sys.argv[1:] if not a.startswith('--')), 'lotr')
CD = os.path.join(ROOT, 'content', TABLE)
geo = json.load(open(os.path.join(CD, 'geometry.json'), encoding='utf-8'))
content = json.load(open(os.path.join(CD, 'content.json'), encoding='utf-8'))
inserts = json.load(open(os.path.join(CD, 'inserts.json'), encoding='utf-8'))
cfg = json.load(open(os.path.join(CD, 'build.json'), encoding='utf-8'))
VIEWS = {}
for vk, v in cfg['views'].items():
    VIEWS[vk] = dict(v, H=np.array(json.load(open(os.path.join(ROOT, v['H'])))), crop=tuple(v['crop']))
INS_VIEW = cfg.get('insertsView', 'real')

# Geometrie wahlweise in Bildpixeln einer Ansicht erfasst -> in VPX-Koordinaten umrechnen
if geo.get('space', 'vpx') != 'vpx':
    pv = geo['space'].split(':')[1]
    Hi = np.linalg.inv(VIEWS[pv]['H'])
    tv = lambda p: [float(x) for x in apply(Hi, [p])[0]]
    sc = float(geo.get('pxToVpx', 0.75))
    def conv(e):
        e = dict(e)
        for k in ('c', 'toward'):
            if k in e: e[k] = tv(e[k])
        for k in ('len', 'w', 'r'):
            if k in e: e[k] = e[k] * sc
        if 'items' in e: e['items'] = [conv(i) for i in e['items']]
        return e
    for sh in geo['shots'].values():
        sh['entrance'] = conv(sh['entrance'])
        for pk in ('path', 'path2'):
            if pk in sh: sh[pk] = [tv(p) for p in sh[pk]]
    for f in geo['flippers'].values():
        for k in ('pivot', 'aim'):
            if k in f and geo.get('flipperSpace', 'vpx') != 'vpx': f[k] = tv(f[k])

def unit(a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]; n = math.hypot(dx, dy) or 1
    return dx/n, dy/n

def shape_pts(e):
    """Umriss in VPX-Koordinaten als Polygon (geschlossen)."""
    t = e['type']
    if t == 'circle':
        return [(e['c'][0] + e['r']*math.cos(a), e['c'][1] + e['r']*math.sin(a)) for a in np.linspace(0, 2*math.pi, 24, endpoint=False)]
    ux, uy = unit(e['c'], e['toward']); nx, ny = -uy, ux
    L, W = e['len']/2, e['w']/2
    if t == 'lane':
        # Kapsel: hinten offen wirkend, vorne abgerundet -> als abgerundetes Rechteck
        pts = []
        cx, cy = e['c']
        r = W
        # gerade Seiten + Halbkreis am Eingang (Richtung Spieler)
        for s in np.linspace(0, math.pi, 10):
            # Halbkreis um den unteren Mittelpunkt
            bx, by = cx - ux*L, cy - uy*L
            ang = math.atan2(ny, nx) + s
            pts.append((bx + r*math.cos(ang), by + r*math.sin(ang)))
        tx, ty = cx + ux*L, cy + uy*L
        pts += [(tx - nx*W, ty - ny*W), (tx + nx*W, ty + ny*W)]
        return pts
    # rect
    cx, cy = e['c']
    return [(cx + ux*L*sx + nx*W*sy, cy + uy*L*sx + ny*W*sy) for sx, sy in ((-1,-1),(1,-1),(1,1),(-1,1))]

def proj(view, pts):
    v = VIEWS[view]; x0, y0, x1, y1 = v['crop']
    p = apply(v['H'], pts)
    return [[round((x-x0)/(x1-x0), 4), round((y-y0)/(y1-y0), 4)] for x, y in p]

def ball_d(view, pts):
    """Kugeldurchmesser (50 VPX-Einheiten = 1 1/16 Zoll) je Bahnpunkt, normiert auf die Bildbreite."""
    v = VIEWS[view]; x0, y0, x1, y1 = v['crop']
    out = []
    for x, y in pts:
        a, b, c = apply(v['H'], [(x - 25, y), (x + 25, y), (x, y + 25)])
        d = (math.hypot(*(b - a)) + 2 * math.hypot(*(c - (a + b) / 2))) / 2
        out.append(round(d / (x1 - x0), 4))
    return out

def build():
    out = {'table': content['table'], 'sources': content['sources'], 'views': {}, 'shots': {}, 'inserts': {},
           'strategies': content['strategies'], 'multiballs': content['multiballs'], 'modes': content['modes'], 'modesIntro': content.get('modesIntro', ''),
           'icons': content.get('icons', {}), 'glossary': content.get('glossary', []), 'limits': content.get('limits', [])}
    for vk, v in VIEWS.items():
        x0, y0, x1, y1 = v['crop']
        out['views'][vk] = {'image': 'img/' + v['out'], 'w': x1-x0, 'h': y1-y0, **content['views'][vk]}
    for sid, meta in content['shots'].items():
        g = geo['shots'].get(sid)
        s = dict(meta); s['geom'] = {}
        for vk in VIEWS:
            if vk in meta.get('hideIn', []):
                continue
            gv = {}
            if g:
                e = g['entrance']
                items = e['items'] if e['type'] == 'multi' else [e]
                gv['outline'] = [proj(vk, shape_pts(it)) for it in items]
                gv['center'] = proj(vk, [items[0]['c']])[0] if len(items) == 1 else proj(vk, [tuple(np.mean([it['c'] for it in items], axis=0))])[0]
                fl = meta.get('flipper')
                if fl:
                    keys = ['L', 'R'] if fl == 'beide' else (fl if isinstance(fl, list) else [fl])
                    gv['aim'] = [proj(vk, [geo['flippers'][k]['aim'], items[0]['c']]) for k in keys]
                    gv['aimBall'] = [ball_d(vk, [geo['flippers'][k]['aim'], items[0]['c']]) for k in keys]
                for pk in ('path', 'path2'):
                    if pk in g:
                        gv[pk] = proj(vk, g[pk])
                        gv[pk + 'Ball'] = ball_d(vk, g[pk])
            ov = meta.get('override', {}).get(vk)
            if ov:  # direkt gemessene Bildkoordinaten (Pixel im Original) fuer erhoehte/verdeckte Objekte
                x0, y0, x1, y1 = VIEWS[vk]['crop']
                n = lambda p: [round((p[0]-x0)/(x1-x0), 4), round((p[1]-y0)/(y1-y0), 4)]
                if 'circle' in ov:
                    cx, cy, r = ov['circle']
                    gv['outline'] = [[n((cx + r*math.cos(a), cy + r*math.sin(a))) for a in np.linspace(0, 2*math.pi, 24, endpoint=False)]]
                    gv['center'] = n((cx, cy))
                if 'poly' in ov:
                    gv['outline'] = [[n(p) for p in ov['poly']]]
                    gv['center'] = n(tuple(np.mean(ov['poly'], axis=0)))
                    gv.pop('aim', None); gv.pop('path', None)
            s['geom'][vk] = gv
        s.pop('override', None)
        out['shots'][sid] = s
    # Einsaetze: Pixel im Bild der Einsatz-Ansicht -> normiert
    x0, y0, x1, y1 = VIEWS[INS_VIEW]['crop']
    for iid, ins in inserts.items():
        d = dict(ins)
        d['geom'] = {INS_VIEW: {'points': [[round((p[0]-x0)/(x1-x0), 4), round((p[1]-y0)/(y1-y0), 4)] for p in ins['px']],
                              'r': round(ins.get('r', 14)/(x1-x0), 4)}}
        d.pop('px', None); d.pop('r', None)
        out['inserts'][iid] = d
    os.makedirs(os.path.join(ROOT, 'app/data'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'app/img'), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, f'app/data/{TABLE}.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    from PIL import Image
    for vk, v in VIEWS.items():
        im = Image.open(os.path.join(ROOT, v['src'])).convert('RGB').crop(v['crop'])
        im.save(os.path.join(ROOT, 'app/img', v['out']), quality=v['quality'], optimize=True, progressive=True)
    return out

def check(out):
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype('arial.ttf', 15)
    for vk, v in VIEWS.items():
        im = Image.open(os.path.join(ROOT, 'app/img', v['out'])).convert('RGB')
        W, H = im.size; d = ImageDraw.Draw(im)
        P = lambda p: (p[0]*W, p[1]*H)
        for sid, s in out['shots'].items():
            g = s['geom'].get(vk)
            if not g: continue
            for pl in g.get('path', []) and [g['path']]:
                d.line([P(p) for p in pl], fill=(80, 200, 255), width=2)
            if g.get('path2'):
                d.line([P(p) for p in g['path2']], fill=(80, 120, 255), width=2)
            for a in g.get('aim', []):
                d.line([P(p) for p in a], fill=(255, 255, 255), width=1)
            for o in g.get('outline', []):
                d.polygon([P(p) for p in o], outline=(255, 140, 0))
            if g.get('center'):
                c = P(g['center']); d.text((c[0]+6, c[1]-8), sid, fill=(255, 230, 0), font=f)
        if vk == INS_VIEW:
            for iid, ins in out['inserts'].items():
                for p in ins['geom'][vk]['points']:
                    c = P(p); r = ins['geom'][vk]['r']*W
                    d.ellipse([c[0]-r, c[1]-r, c[0]+r, c[1]+r], outline=(0, 255, 120), width=2)
        im.save(os.path.join(ROOT, f'_quellen/pages/check_{TABLE}_{vk}.png'))

if __name__ == '__main__':
    o = build()
    if '--check' in sys.argv:
        check(o)
    print('ok', len(o['shots']), 'shots', len(o['inserts']), 'inserts')
