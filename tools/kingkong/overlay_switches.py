"""Schalterplan (sw_0.png) -> Lampenplan (affin, gleiche CAD-Zeichnung) -> Foto (H_lights). Nur Kontrolle."""
import sys, json, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, '..'))
from homography import fit, apply
import numpy as np
from PIL import Image
sw = [(440,1957),(942,1957),(692,1885),(425,1700),(475,2408),(908,2408)]
li = [(399*1.1,1213*1.1),(658*1.1,1213*1.1),(529*1.1,1177*1.1),(392*1.1,1080*1.1),(409*1.1,1428*1.1),(650*1.1,1428*1.1)]
M = np.c_[np.array(sw, float), np.ones(len(sw))]
sol = np.linalg.lstsq(M, np.array(li, float), rcond=None)[0]  # affin, da alle Paare im unteren Feld liegen
A = np.vstack([sol.T, [0, 0, 1]])
print('res', np.round(apply(A, sw) - np.array(li), 1))
H = np.array(json.load(open(os.path.join(D, 'H_lights.json')))) @ A
json.dump(H.tolist(), open(os.path.join(D, 'H_switch.json'), 'w'))
R = os.path.join(D, '..', '..', '_quellen', 'kingkong')
ph = Image.open(os.path.join(R, 'pf.png')).convert('RGB')
pl = Image.open(os.path.join(R, 'man', 'sw_0.png')).convert('L')
Hi = np.linalg.inv(H); Hi = Hi / Hi[2, 2]
w = pl.transform(ph.size, Image.PERSPECTIVE, tuple(Hi.flatten()[:8]), Image.BILINEAR, fillcolor=255)
a = np.array(ph).astype(float) * 0.8; m = (np.array(w) < 110)
a[m] = [0, 255, 255]
Image.fromarray(a.astype('uint8')).save(os.path.join(R, 'overlay_switches.png'))
