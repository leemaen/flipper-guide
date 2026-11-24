"""Draufsicht (orthografisch) einer entpackten VPX-Tischdatei rendern.

Aufruf: py -3 -I tools/futurama/vpxrender.py <entpackter_vpx_ordner> <out.png> [breite_px] [--inserts=0.45] [--skip=name1,name2]
Grundlage: Spielfeldbild (gamedata.image) exakt auf die Tischmaße gelegt, darüber sichtbare Primitive
(Dreiecke mit Textur bzw. Materialfarbe, Painter-Verfahren nach Höhe), sichtbare Rampen, Wände, Gummis,
Bumper-Ringe, Einsatz-Lichter (Formen aus den Light-Drag-Points). Ausgabe-Pixel = VPX * (breite/tischbreite),
d. h. die Abbildung VPX -> Bild ist eine reine Skalierung (wird in build.json als Homographie abgelegt).
Dient nur als Spielfeldansicht, nicht als originalgetreues Rendering (keine Perspektive, kein Licht-Setup).
"""
import json, glob, os, sys, math
import numpy as np
from PIL import Image, ImageDraw

SRC, OUT = sys.argv[1], sys.argv[2]
WPX = int(next((a for a in sys.argv[3:] if a.isdigit()), 1000))
INS = float(next((a.split('=')[1] for a in sys.argv if a.startswith('--inserts=')), 0.7))
AL = next((a.split('=')[1].split(',') for a in sys.argv if a.startswith('--glass=')), [])  # als Klarsicht-Rampen zeichnen
FL = next((a.split('=')[1].split(',') for a in sys.argv if a.startswith('--flashers=')), [])
SKIP = set(next((a.split('=')[1].split(',') for a in sys.argv if a.startswith('--skip=')), []))
GI = os.path.join(SRC, 'gameitems')
gd = json.load(open(os.path.join(SRC, 'gamedata.json'), encoding='utf-8'))
TW, TH = gd['right'] - gd['left'], gd['bottom'] - gd['top']
S = WPX / TW; HPX = int(round(TH * S))
imgs = {e['name'].lower(): e for e in json.load(open(os.path.join(SRC, 'images.json'), encoding='utf-8'))}
mats = {m['name']: m for m in json.load(open(os.path.join(SRC, 'materials.json'), encoding='utf-8'))} if os.path.exists(os.path.join(SRC, 'materials.json')) else {}
_cache = {}

def tex(name):
    if not name: return None
    k = name.lower()
    if k in _cache: return _cache[k]
    fs = [f for f in glob.glob(os.path.join(SRC, 'images', '*')) if os.path.splitext(os.path.basename(f))[0].lower() == k]
    im = None
    for f in fs:
        try:
            im = Image.open(f).convert('RGBA'); break
        except Exception:
            pass
    if im is not None and max(im.size) > 1024:
        im.thumbnail((1024, 1024))
    _cache[k] = (np.asarray(im).astype(np.float32) if im is not None else None)
    return _cache[k]

def hexc(c, d=(150, 150, 150)):
    try: return tuple(int(c[i:i+2], 16) for i in (1, 3, 5))
    except Exception: return d

def load(t):
    out = []
    for f in sorted(glob.glob(os.path.join(GI, t + '.*.json'))):
        d = json.load(open(f, encoding='utf-8'))[t]; d['_file'] = f; out.append(d)
    return out

def P(x, y): return (x * S, y * S)

# ---- Primitive ----
def rotm(ax, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    if ax == 'x': return np.array([[1, 0, 0], [0, c, s], [0, -s, c]])
    if ax == 'y': return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
    return np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])

def read_obj(fn):
    V, T, F = [], [], []
    with open(fn, encoding='utf-8', errors='ignore') as fh:
        for ln in fh:
            if ln.startswith('v '): V.append([float(a) for a in ln.split()[1:4]])
            elif ln.startswith('vt '): T.append([float(a) for a in ln.split()[1:3]])
            elif ln.startswith('f '):
                F.append([tuple(int(x) - 1 if x else -1 for x in (q.split('/') + ['', ''])[:2]) for q in ln.split()[1:4]])
    return np.array(V), np.array(T) if T else None, F

prims = []
for p in load('Primitive'):
    if not p.get('is_visible') or p['name'] in SKIP or p['name'].lower() == 'playfield_mesh' or 'bake' in (p.get('image') or '').lower() or p.get('add_blend'): continue
    obj = p['_file'][:-5] + '.obj'
    if not os.path.exists(obj): continue
    V, T, F = read_obj(obj)
    if len(V) == 0 or not F: continue
    V = V.copy(); V[:, 2] *= -1  # vpxtool schreibt z negiert
    sz = p['size']; r = p['rot_and_tra']
    M = np.diag([sz['x'], sz['y'], sz['z']]).astype(float)
    for ax, i in (('z', 2), ('y', 1), ('x', 0), ('z', 8), ('y', 7), ('x', 6)):  # VPX: RotZ/Y/X (Index 2,1,0), dann ObjRot (8,7,6)
        M = M @ rotm(ax, r[i])
    W = V @ M + np.array([r[3], r[4], r[5]]) + np.array([p['position']['x'], p['position']['y'], p['position']['z']])
    prims.append((float(np.mean(W[:, 2])), p, W, T, F))
prims.sort(key=lambda t: t[0])
def draw_prims(canvas, plist):
    Ld = np.array([0.3, -0.5, 0.8]); Ld /= np.linalg.norm(Ld)
    for zc, p, W, T, F in plist:
        tx = tex(p.get('image')); m = mats.get(p.get('material'), {})
        col = np.array(hexc(m.get('base_color'), (170, 170, 170)), float)
        tint = np.array(hexc(p.get('color', '#ffffff'), (255, 255, 255)), float) / 255
        alpha = p.get('alpha', 100) / 100.0
        flat = False
        if p['name'] in AL:
            alpha = 0.3; col = np.array((200, 215, 230), float); tx = None
        elif m.get('opacity_active'):
            alpha *= max(0.15, m.get('opacity', 1.0)) * 0.5; flat = True
            if tx is not None: col = np.mean(tx[:, :, :3], axis=(0, 1)); tx = None
        tris = []
        for f in F:
            a, b, c = (W[q[0]] for q in f)
            n = np.cross(b - a, c - a); nn = np.linalg.norm(n)
            if nn < 1e-9: continue
            n /= nn
            if n[2] < 0: n = -n
            sh = 0.45 + 0.55 * max(0.0, float(n @ Ld))
            if tx is not None and T is not None and f[0][1] >= 0:
                uv = np.mean([T[q[1]] for q in f], axis=0)
                h, w = tx.shape[:2]
                px = tx[int(min(h - 1, max(0, (1 - (uv[1] % 1.0001)) * (h - 1)))), int(min(w - 1, max(0, (uv[0] % 1.0001) * (w - 1))))]
                if px[3] < 40: continue
                cc = px[:3]
            else:
                cc = col
            cc = np.clip(cc * tint * sh, 0, 255)
            tris.append((max(a[2], b[2], c[2]), [P(a[0], a[1]), P(b[0], b[1]), P(c[0], c[1])], tuple(int(v) for v in cc)))
        if not tris: continue
        tris.sort(key=lambda t: t[0])
        if alpha >= 0.95:
            d = ImageDraw.Draw(canvas)
            for _, pts, cc in tris: d.polygon(pts, fill=cc + (255,))
        else:
            lay = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            for _, pts, cc in tris: d.polygon(pts, fill=cc + (int(255 * alpha),))
            canvas.alpha_composite(lay)


canvas = Image.new('RGBA', (WPX, HPX), (20, 20, 24, 255))
under = [t for t in prims if t[2][:, 2].max() < 1.0 and 'off' not in (t[1].get('image') or '').lower() and np.ptp(t[2][:, 0]) * np.ptp(t[2][:, 1]) < 40000]
over = [t for t in prims if t[2][:, 2].max() >= 1.0]
draw_prims(canvas, under)   # Einsatz-Körper, Lochkästen: nur durch Aussparungen im Artwork sichtbar
# Einsatz-Lichter (Formen), ebenfalls unter dem Artwork
lay = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
for L in load('Light'):
    pts = [P(q['x'], q['y']) for q in L.get('drag_points', [])]
    if len(pts) < 3 or L.get('is_backglass') or not L.get('visible', True): continue
    ar = 0.5 * abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))) / S / S
    if ar > 9000: continue  # GI-/Flaechenlicht, kein Einsatz
    c = hexc(L.get('color'))
    if sum(c) < 60: c = hexc(L.get('color2'), (255, 255, 255))
    if sum(c) < 60: continue
    dl.polygon(pts, fill=c + (int(255 * INS),))
canvas.alpha_composite(lay)
for fl in load('Flasher'):  # weltbezogene Flasher-Bilder unter dem Artwork (z. B. Luken), nur auf Wunsch
    if fl['name'] not in FL: continue
    t = tex(fl.get('image_a'))
    if t is None: continue
    timg = Image.fromarray(t.astype(np.uint8)).resize((WPX, HPX))
    mask = Image.new('L', canvas.size, 0); ImageDraw.Draw(mask).polygon([P(q['x'], q['y']) for q in fl['drag_points']], fill=255)
    timg.putalpha(Image.fromarray(np.minimum(np.asarray(timg)[:, :, 3], np.asarray(mask)).astype(np.uint8))); canvas.alpha_composite(timg)
pf = tex(gd.get('image'))
if pf is not None:
    canvas.alpha_composite(Image.fromarray(pf.astype(np.uint8)).resize((WPX, HPX), Image.LANCZOS))
draw_prims(canvas, over)

# ---- sichtbare Rampen (Bänder) ----
def ramp_poly(r):
    pts = [(q['x'], q['y']) for q in r['drag_points']]
    if len(pts) < 2: return None
    n = len(pts); L, R = [], []
    for i in range(n):
        a = pts[max(0, i - 1)]; b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = (r['width_bottom'] + (r['width_top'] - r['width_bottom']) * i / max(1, n - 1)) / 2
        L.append(P(pts[i][0] + nx * w, pts[i][1] + ny * w)); R.append(P(pts[i][0] - nx * w, pts[i][1] - ny * w))
    return L + R[::-1]
for r in sorted(load('Ramp'), key=lambda r: r['height_top']):
    if not r.get('is_visible') or r['name'] in SKIP: continue
    poly = ramp_poly(r)
    if not poly: continue
    tx = tex(r.get('image')); m = mats.get(r.get('material'), {})
    if tx is not None and r.get('image_alignment') == 'world' and r.get('ramp_type', 'flat') == 'flat':
        timg = Image.fromarray(tx.astype(np.uint8)).resize((WPX, HPX))
        mask = Image.new('L', canvas.size, 0); ImageDraw.Draw(mask).polygon(poly, fill=255)
        a = np.minimum(np.asarray(timg)[:, :, 3], np.asarray(mask)).astype(np.uint8)
        timg.putalpha(Image.fromarray(a)); canvas.alpha_composite(timg)
        continue
    if r.get('ramp_type', 'flat') != 'flat':
        cc = (200, 200, 205)
        d = ImageDraw.Draw(canvas); d.line(poly[:len(poly)//2], fill=cc + (255,), width=3); d.line(poly[len(poly)//2:], fill=cc + (255,), width=3)
        continue
    cc = tuple(int(v) for v in (np.mean(tx[:, :, :3], axis=(0, 1)) if tx is not None else hexc(m.get('base_color'), (180, 180, 190))))
    lay = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon(poly, fill=cc + (110 if tx is not None else 45,), outline=(230, 230, 240, 200))
    canvas.alpha_composite(lay)

# ---- Wände / Gummis / Bumper ----
d = ImageDraw.Draw(canvas)
for w in load('Wall'):
    if not w.get('is_top_bottom_visible') or w['name'] in SKIP or w.get('height_top', 0) > 150: continue
    pts = [P(q['x'], q['y']) for q in w['drag_points']]
    if len(pts) < 3: continue
    if not w.get('image') and not w.get('top_material'): continue  # ohne Textur/Material: nicht zeichnen
    if w.get('height_top', 0) < 1: 
        continue
    tx = tex(w.get('image')); m = mats.get(w.get('top_material'), {})
    if tx is not None:  # VPX legt Wand-Texturen auf die Tischmaße (Weltkoordinaten)
        timg = Image.fromarray(tx.astype(np.uint8)).resize((WPX, HPX))
        mask = Image.new('L', canvas.size, 0); ImageDraw.Draw(mask).polygon(pts, fill=255)
        a = np.minimum(np.asarray(timg)[:, :, 3], np.asarray(mask))
        if tx.shape[0] < 600: a = a * 0.35  # kleine Kacheltextur (Metall): nur angedeutet, damit Bahnen sichtbar bleiben
        timg.putalpha(Image.fromarray(a.astype(np.uint8))); canvas.alpha_composite(timg); d = ImageDraw.Draw(canvas)
        continue
    cc = tuple(int(v) for v in (np.mean(tx[:, :, :3], axis=(0, 1)) if tx is not None else hexc(m.get('base_color'), (120, 120, 120))))
    d.polygon(pts, fill=cc + (255,))
for rb in load('Rubber'):
    if not rb.get('is_visible'): continue
    pts = [P(q['x'], q['y']) for q in rb['drag_points']]
    if len(pts) > 1: d.line(pts + [pts[0]], fill=(25, 25, 25, 255), width=max(2, int(rb.get('thickness', 8) * S)))
for b in load('Bumper'):
    if not (b.get('is_cap_visible') or b.get('is_ring_visible') or b.get('is_base_visible')): continue
    x, y = P(b['center']['x'], b['center']['y']); rr = b['radius'] * S
    d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(230, 230, 230, 255), width=3)
canvas.convert('RGB').save(OUT)
json.dump([[S, 0, 0], [0, S, 0], [0, 0, 1]], open(os.path.splitext(OUT)[0] + '_H.json', 'w'))
print('ok', WPX, HPX, 'scale', round(S, 5), len(prims), 'prims')
