"""Prüft die Abbildung VPX -> Ansicht über die Einsatz-Aussparungen im Spielfeldbild.

Aufruf: py -3 -I tools/futurama/fit_H.py <entpackter_vpx_ordner> <ansichtsbreite_px> <H_out.json>
Für jedes Einsatz-Licht (Light mit Form, Fläche < 9000 VPX²) wird im Spielfeldbild (gamedata.image) die
transparente Aussparung unter dem Lichtmittelpunkt gesucht und ihr Schwerpunkt bestimmt. Aus den Paaren
(Licht-Mittelpunkt in VPX, Aussparungs-Schwerpunkt in Ansichtspixeln) wird eine Homographie geschätzt.
Ausgabe: RMS in Ansichtspixeln gegen die reine Skalierung und gegen die geschätzte Homographie.
Geschrieben wird die reine Skalierung (so ist die Ansicht gebaut); die Schätzung dient als Kontrolle.
"""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from homography import fit, apply
import numpy as np
from PIL import Image
from scipy import ndimage

SRC, WPX, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
gd = json.load(open(os.path.join(SRC, 'gamedata.json'), encoding='utf-8'))
TW, TH = gd['right'] - gd['left'], gd['bottom'] - gd['top']
k = gd['image'].lower()
fn = [f for f in glob.glob(os.path.join(SRC, 'images', '*')) if os.path.splitext(os.path.basename(f))[0].lower() == k][0]
pf = Image.open(fn).convert('RGBA'); PW, PH = pf.size
A = np.asarray(pf)[:, :, 3] < 100
lab, n = ndimage.label(A)
S = WPX / TW
src, dst, names = [], [], []
for f in glob.glob(os.path.join(SRC, 'gameitems', 'Light.*.json')):
    L = json.load(open(f, encoding='utf-8'))['Light']
    pts = [(p['x'], p['y']) for p in L.get('drag_points', [])]
    if len(pts) < 3 or L.get('is_backglass'): continue
    ar = 0.5 * abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts))))
    if ar > 9000 or ar < 150: continue
    cx, cy = L['center']['x'], L['center']['y']
    px, py = int(cx / TW * PW), int(cy / TH * PH)
    if not (0 <= px < PW and 0 <= py < PH): continue
    l = lab[py, px]
    if l == 0: continue
    ys, xs = np.nonzero(lab[max(0, py - 400):py + 400, max(0, px - 400):px + 400] == l)
    if len(xs) == 0 or len(xs) > 0.002 * PW * PH: continue
    gx = (xs.mean() + max(0, px - 400)) / PW * TW * S; gy = (ys.mean() + max(0, py - 400)) / PH * TH * S
    # nur Lichter, deren Mittelpunkt im Schwerpunkt der eigenen Form liegt (Einsatz, kein Pfeil mit Versatz)
    pcx, pcy = np.mean(pts, axis=0)
    if np.hypot(pcx - cx, pcy - cy) > 12: continue
    src.append((cx, cy)); dst.append((gx, gy)); names.append(L['name'])
src, dst = np.array(src), np.array(dst)
Hs = np.array([[S, 0, 0], [0, S, 0], [0, 0, 1.0]])
rs = apply(Hs, src) - dst
Hf = fit(src, dst); rf = apply(Hf, src) - dst
print('Einsätze:', len(src))
print('RMS Skalierung  %.2f px' % np.sqrt((rs ** 2).sum(1).mean()))
print('RMS Homographie %.2f px' % np.sqrt((rf ** 2).sum(1).mean()))
worst = np.argsort(-np.hypot(*rs.T))[:6]
for i in worst: print('  ', names[i], np.round(rs[i], 1))
json.dump(Hs.tolist(), open(OUT, 'w'))
json.dump({'n': len(src), 'rms_scale': float(np.sqrt((rs ** 2).sum(1).mean())), 'rms_fit': float(np.sqrt((rf ** 2).sum(1).mean())), 'lights': names},
          open(os.path.splitext(OUT)[0] + '_fit.json', 'w'), indent=1)
