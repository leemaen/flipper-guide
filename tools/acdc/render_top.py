"""Rendert eine Draufsicht (orthografisch, von oben) aus einer mit vpxtool entpackten VPX-Tischdatei.

Aufruf:  py -3 -I tools/acdc/render_top.py <entpackter_ordner> <ausgabe.png> [px_pro_vpx_einheit] [--pf BILDNAME] [--skip REGEX]
Ergebnis: Bild mit Bildkoordinate = VPX-Koordinate * Maßstab (keine Perspektive), dazu <ausgabe>.json mit Maßstab.
Gezeichnet werden: Primitives (OBJ-Meshes mit Textur, Maler-Algorithmus nach Höhe), Spielfeldtextur (Löcher zeigen
die darunterliegenden Insert-Meshes), sichtbare Wände mit Oberseiten-Bild/Farbe, Flipper und Bumper schematisch.
Beleuchtung wird nicht simuliert. Das Bild dient nur als Ansicht; Geometrie kommt immer direkt aus den gameitems.
"""
import json, glob, os, re, sys, math
import numpy as np, cv2
from PIL import Image

args = [a for a in sys.argv[1:]]
def opt(name, default=None):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
PF_NAME = opt('--pf'); SKIP = opt('--skip', r'(?i)^(vr|pincab|cab_|cabinet|backbox|lockbar|leg|room|floor|siderail_vr|sideblade)')
ONLY_BELOW = opt('--zmax')
D, OUT = args[0], args[1]
S = float(args[2]) if len(args) > 2 else 1.1
G = os.path.join(D, 'gameitems')
gd = json.load(open(os.path.join(D, 'gamedata.json')))
TW, TH = gd['right'], gd['bottom']
W, H = int(round(TW * S)), int(round(TH * S))

imgfiles = {}
for f in os.listdir(os.path.join(D, 'images')):
    imgfiles[os.path.splitext(f)[0].lower()] = os.path.join(D, 'images', f)
_cache = {}
def tex(name):
    if not name: return None
    k = name.lower()
    if k in _cache: return _cache[k]
    p = imgfiles.get(k); t = None
    if p:
        try:
            im = Image.open(p).convert('RGBA')
            if max(im.size) > 2048:
                f = 2048 / max(im.size); im = im.resize((max(1, int(im.width * f)), max(1, int(im.height * f))))
            t = np.array(im).astype(np.float32) / 255.0
        except Exception:
            t = None
    _cache[k] = t
    return t

_mf = os.path.join(D, 'materials.json')
if not os.path.exists(_mf): _mf = os.path.join(D, 'materials-old.json')   # ältere Tischformate
mats = {m['name'].lower(): m for m in json.load(open(_mf))}
for m in mats.values():   # altes Format: opacity_active_edge_alpha (Bit 0 = aktiv)
    if 'opacity_active' not in m and 'opacity_active_edge_alpha' in m: m['opacity_active'] = bool(m['opacity_active_edge_alpha'] & 1)
def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
def matinfo(name):
    m = mats.get((name or '').lower())
    if not m: return hexc('#b4b4b4'), 1.0
    op = m.get('opacity', 1.0) if m.get('opacity_active') else 1.0
    return hexc(m.get('base_color', '#b4b4b4')), float(op)

def rx(a):
    c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, s], [0, -s, c]])
def ry(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
def rz(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])

def load_obj(p):
    V, T, F = [], [], []
    for ln in open(p, encoding='utf-8', errors='replace'):
        if ln.startswith('v '): V.append([float(x) for x in ln.split()[1:4]])
        elif ln.startswith('vt '): T.append([float(x) for x in ln.split()[1:3]])
        elif ln.startswith('f '):
            idx = [x.split('/') for x in ln.split()[1:]]
            vi = [int(i[0]) - 1 for i in idx]; ti = [int(i[1]) - 1 if len(i) > 1 and i[1] else int(i[0]) - 1 for i in idx]
            for k in range(1, len(vi) - 1):
                F.append((vi[0], vi[k], vi[k + 1], ti[0], ti[k], ti[k + 1]))
    return np.array(V, float), np.array(T, float) if T else np.zeros((len(V), 2)), np.array(F, int).reshape(-1, 6)

tris = []  # (zmean, kind, data)
def add_mesh(V, T, F, img, color, alpha):
    if len(F) == 0: return
    P = V[F[:, :3]]                       # n x 3 x 3 (Weltkoordinaten)
    UV = T[F[:, 3:]]
    z = P[:, :, 2].mean(1)
    for i in range(len(F)):
        tris.append((z[i], P[i], UV[i], img, color, alpha))

# ---- Primitives
nprim = 0
BBOX = []
HAS_PFMESH = []
for jf in sorted(glob.glob(os.path.join(G, 'Primitive.*.json'))):
    d = json.load(open(jf, encoding='utf-8'))['Primitive']
    if not d.get('is_visible', True) or re.search(SKIP, d['name']): continue
    of = jf[:-5] + '.obj'
    if not os.path.exists(of): continue
    V, T, F = load_obj(of)
    if len(V) == 0: continue
    V = V.copy(); V[:, 2] = -V[:, 2]          # vpxtool-OBJ: z gespiegelt (wie VPX-Export)
    r = d['rot_and_tra']; sz = d['size']; pos = d['position']
    V = V * [sz['x'], sz['y'], sz['z']]
    V = V + r[3:6]
    for M in (rz(math.radians(r[2])), ry(math.radians(r[1])), rx(math.radians(r[0])),
              rz(math.radians(r[8])), ry(math.radians(r[7])), rx(math.radians(r[6]))):
        V = V @ M
    V = V + [pos['x'], pos['y'], pos['z']]
    if V[:, 0].max() < -50 or V[:, 0].min() > TW + 50 or V[:, 1].max() < -50 or V[:, 1].min() > TH + 50: continue
    if V[:, 2].min() > 400: continue          # Glas/Kabinett
    if ONLY_BELOW is not None and V[:, 2].min() > float(ONLY_BELOW): continue
    col, op = matinfo(d.get('material'))
    T2 = T.copy(); T2[:, 1] = 1 - T2[:, 1]
    alpha = op * (d.get('alpha') if d.get('alpha') is not None else 100) / 100
    img = tex(d.get('image'))
    if d['name'].lower() == 'playfield_mesh':   # VPX: Spielfeld-Mesh nutzt Spielfeldbild der Tabelle
        img = tex(PF_NAME or gd.get('image')); HAS_PFMESH.append(1); col = np.ones(3, np.float32)
    add_mesh(V, T2, F, img, col * hexc(d.get('color') or '#ffffff'), alpha)
    nprim += 1
    BBOX.append((d['name'], [round(float(x)) for x in (V[:, 0].min(), V[:, 1].min(), V[:, 0].max(), V[:, 1].max(), V[:, 2].min(), V[:, 2].max())], d.get('image')))

# ---- Wände (Oberseite)
for jf in glob.glob(os.path.join(G, 'Wall.*.json')):
    d = json.load(open(jf, encoding='utf-8'))['Wall']
    if not d.get('is_top_bottom_visible', True): continue
    pts = [(p['x'], p['y']) for p in d['drag_points']]
    if len(pts) < 3: continue
    col, op = matinfo(d.get('top_material'))
    img = tex(d.get('image'))
    z = d.get('height_top', 50)
    tris.append((z, 'poly', np.array(pts), img, col, op))

# ---- Spielfeld
pf = tex(PF_NAME or gd.get('image'))
if not HAS_PFMESH: tris.append((0.0, 'pf', None, pf, None, 1.0))
tris.sort(key=lambda t: t[0])

canvas = np.zeros((H, W, 3), np.float32) + 0.05
def blend(region_mask, src_rgba, x0, y0):
    h, w = region_mask.shape
    a = src_rgba[:, :, 3:4] * region_mask[:, :, None]
    canvas[y0:y0 + h, x0:x0 + w] = canvas[y0:y0 + h, x0:x0 + w] * (1 - a) + src_rgba[:, :, :3] * a

for t in tris:
    z, a1, a2, img, col, alpha = t
    if isinstance(a1, str) and a1 == 'pf':
        if img is None: continue
        src = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
        blend(np.ones((H, W), np.float32), src, 0, 0)
        continue
    if isinstance(a1, str) and a1 == 'poly':
        pts = (a2 * S).astype(np.float32)
        x0, y0 = np.floor(pts.min(0)).astype(int); x1, y1 = np.ceil(pts.max(0)).astype(int)
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W), min(y1, H)
        if x1 <= x0 or y1 <= y0: continue
        m = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.fillPoly(m, [np.round(pts - [x0, y0]).astype(np.int32)], 1)
        if img is not None:   # Weltausrichtung: Textur über den ganzen Tisch
            src = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)[y0:y1, x0:x1]
        else:
            src = np.dstack([np.ones((y1 - y0, x1 - x0, 3), np.float32) * col, np.ones((y1 - y0, x1 - x0, 1), np.float32)])
        src = src.copy(); src[:, :, 3] *= alpha
        blend(m.astype(np.float32), src, x0, y0)
        continue
    P, UV = a1, a2
    q = (P[:, :2] * S).astype(np.float32)
    area = (q[1, 0] - q[0, 0]) * (q[2, 1] - q[0, 1]) - (q[2, 0] - q[0, 0]) * (q[1, 1] - q[0, 1])
    if abs(area) < 0.05: continue
    x0, y0 = np.floor(q.min(0)).astype(int); x1, y1 = np.ceil(q.max(0)).astype(int) + 1
    x0c, y0c = max(x0, 0), max(y0, 0); x1c, y1c = min(x1, W), min(y1, H)
    if x1c <= x0c or y1c <= y0c: continue
    m = np.zeros((y1c - y0c, x1c - x0c), np.uint8)
    cv2.fillConvexPoly(m, np.round(q - [x0c, y0c]).astype(np.int32), 1)
    if not m.any(): continue
    if img is None:
        src = np.dstack([np.ones(m.shape + (3,), np.float32) * col, np.ones(m.shape + (1,), np.float32)])
    else:
        th, tw = img.shape[:2]
        uv = (UV % 1.0001) * [tw - 1, th - 1] if (UV.min() < -0.01 or UV.max() > 1.01) else UV * [tw - 1, th - 1]
        A = cv2.getAffineTransform(uv.astype(np.float32), (q - [x0c, y0c]).astype(np.float32))
        src = cv2.warpAffine(img, A, (x1c - x0c, y1c - y0c), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        src[:, :, :3] *= col / max(col.max(), 1e-3) if col.max() < 0.99 else 1
    src = src.copy(); src[:, :, 3] *= alpha
    blend(m.astype(np.float32), src, x0c, y0c)

# ---- Flipper und Bumper schematisch
out = (np.clip(canvas, 0, 1) * 255).astype(np.uint8)
for jf in glob.glob(os.path.join(G, 'Flipper.*.json')):
    d = json.load(open(jf, encoding='utf-8'))['Flipper']
    if not d.get('is_visible', True): continue
    c = np.array([d['center']['x'], d['center']['y']]); a = math.radians(d['start_angle'])
    tip = c + d['flipper_radius_max'] * np.array([math.sin(a), -math.cos(a)])
    rb, re_ = d['base_radius'], d['end_radius']
    n = np.array([math.cos(a), math.sin(a)])
    poly = np.array([c + n * rb, tip + n * re_, tip - n * re_, c - n * rb]) * S
    cv2.fillConvexPoly(out, np.round(poly).astype(np.int32), (235, 235, 235), lineType=cv2.LINE_AA)
    cv2.circle(out, tuple(np.round(c * S).astype(int)), int(rb * S), (235, 235, 235), -1, cv2.LINE_AA)
    cv2.circle(out, tuple(np.round(tip * S).astype(int)), int(re_ * S), (235, 235, 235), -1, cv2.LINE_AA)
Image.fromarray(out).save(OUT)
json.dump({'bbox': BBOX, 'scale': S, 'w': W, 'h': H, 'table': [TW, TH], 'primitives': nprim}, open(os.path.splitext(OUT)[0] + '.json', 'w'))
print('ok', W, H, 'prims', nprim, 'tris', len(tris))
