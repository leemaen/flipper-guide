"""Rendert eine Draufsicht (orthografisch, von oben) aus den VLM-Bake-Meshes einer entpackten VPX.
Aufruf: py -3 -I tools/cftbl/render_top.py <gameitems-ordner> <images-ordner> <breite_px> <tisch_breite> <tisch_hoehe> <out.png> [prefix=BM_]
Pixel = VPX-Koordinate * (breite_px / tisch_breite)  -> Homographie ist eine reine Skalierung.
"""
import sys, json, glob, os, math
import numpy as np
from PIL import Image
gi, imgdir, W, TW, TH, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
prefix = sys.argv[7] if len(sys.argv) > 7 else 'BM_'
SKIP = {'BM_PFGlass', 'BM_UnderPF'}
s = W / TW; H = int(round(TH * s))
col = np.zeros((H, W, 3), np.float32); zb = np.full((H, W), -1e9, np.float32)
texcache = {}
def tex(name):
    if name not in texcache:
        f = [p for p in glob.glob(os.path.join(imgdir, '*')) if os.path.splitext(os.path.basename(p))[0].lower() == name.lower()]
        texcache[name] = np.asarray(Image.open(f[0]).convert('RGB'), np.float32) if f else None
    return texcache[name]
def rot(ax, a):
    c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
    if ax == 'x': return np.array([[1,0,0],[0,c,-sn],[0,sn,c]])
    if ax == 'y': return np.array([[c,0,sn],[0,1,0],[-sn,0,c]])
    return np.array([[c,-sn,0],[sn,c,0],[0,0,1]])
for jf in sorted(glob.glob(os.path.join(gi, f'Primitive.{prefix}*.json'))):
    d = json.load(open(jf))['Primitive']
    if d['name'] in SKIP or not d.get('is_visible', True): continue
    of = jf[:-5] + '.obj'
    if not os.path.exists(of): continue
    T = tex(d['image'])
    if T is None: continue
    th, tw = T.shape[:2]
    V, VT, F = [], [], []
    for l in open(of):
        if l.startswith('v '): V.append([float(x) for x in l.split()[1:4]])
        elif l.startswith('vt '): VT.append([float(x) for x in l.split()[1:3]])
        elif l.startswith('f '):
            F.append([[int(x) - 1 for x in p.split('/')[:2]] for p in l.split()[1:4]])
    V = np.array(V); VT = np.array(VT)
    r = d['rot_and_tra']; sz = d['size']; p = d['position']
    V = V * [sz['x'], sz['y'], sz['z']]
    R = rot('z', r[2] + r[8]) @ rot('y', r[1] + r[7]) @ rot('x', r[0] + r[6])
    V = V @ R.T + [p['x'] + r[3], p['y'] + r[4], p['z'] + r[5]]
    P = V[:, :2] * s
    for f in F:
        ia = [q[0] for q in f]; it = [q[1] for q in f]
        tri = P[ia]; z = V[ia, 2]; uv = VT[it]
        x0, y0 = np.floor(tri.min(0)).astype(int); x1, y1 = np.ceil(tri.max(0)).astype(int)
        x0 = max(x0, 0); y0 = max(y0, 0); x1 = min(x1, W - 1); y1 = min(y1, H - 1)
        if x1 < x0 or y1 < y0: continue
        (ax, ay), (bx, by), (cx, cy) = tri
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5)
        l1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        l2 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-4) & (l2 >= -1e-4) & (l3 >= -1e-4)
        if not m.any(): continue
        zz = l1 * z[0] + l2 * z[1] + l3 * z[2]
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        m &= zz > sub
        if not m.any(): continue
        u = l1 * uv[0, 0] + l2 * uv[1, 0] + l3 * uv[2, 0]
        v = l1 * uv[0, 1] + l2 * uv[1, 1] + l3 * uv[2, 1]
        tx = np.clip((u * tw).astype(int), 0, tw - 1); ty = np.clip(((1 - v) * th).astype(int), 0, th - 1)
        sub[m] = zz[m]
        col[y0:y1 + 1, x0:x1 + 1][m] = T[ty[m], tx[m]]
    print(d['name'], len(F))
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save(out)
print('saved', out, W, H, 'scale', s)
