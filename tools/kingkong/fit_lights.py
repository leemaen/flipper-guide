"""Homographie Handbuch-Lampenplan (Stern KK Pro-Handbuch S. 26, gerendert 200 dpi -> man/lights.png) -> Spielfeldfoto.
Paare: Lampennummer aus dem Plan  <->  Einsatzmitte im Foto (pf.png, 1319x2560). Nur Kontrolle/Zuordnung.
Aufruf: py -3 -I tools/kingkong/fit_lights.py [overlay]"""
import sys, json, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, '..'))
from homography import fit, apply
import numpy as np
S = 1.1  # Plan-Koordinaten wurden in einer 1545-px-Ansicht abgelesen
P = {
 30: ((399,1213),(462,1534)), 31: ((426,1182),(503,1492)), 32: ((458,1158),(550,1459)), 33: ((498,1145),(600,1441)),
 34: ((561,1145),(700,1441)), 35: ((598,1158),(750,1457)), 36: ((632,1182),(797,1492)), 37: ((658,1213),(837,1532)),
 43: ((457,1028),(535,1285)), 42: ((450,1067),(532,1328)), 41: ((447,1100),(530,1370)), 40: ((430,1127),(510,1413)),
 13: ((354,1405),(398,1825)), 16: ((699,1400),(905,1825)),
 53: ((490,1097),(600,1370)), 54: ((529,1097),(650,1370)), 55: ((566,1097),(700,1370)),
 56: ((490,1056),(600,1313)), 57: ((529,1056),(650,1313)), 58: ((566,1056),(700,1313)),
 119: ((605,715),(763,846)), 129: ((780,708),(999,844)), 130: ((770,748),(991,894)), 118: ((610,668),(757,790)), 112: ((525,705),(648,814)),
 91: ((282,632),(307,735)), 96: ((346,657),(400,773)), 92: ((318,590),(363,690)), 84: ((255,688),(263,810)), 85: ((316,706),(333,787)),
}
X = json.load(open(os.path.join(D, 'fit_lights_extra.json'))) if os.path.exists(os.path.join(D, 'fit_lights_extra.json')) else {}
P.update({k: tuple(map(tuple, v)) for k, v in X.items()})
src = [(a*S, b*S) for (a, b), _ in P.values()]; dst = [v[1] for v in P.values()]
H = fit(src, dst); res = apply(H, src) - np.array(dst)
for k, r in zip(P, res): print(k, np.round(r, 1))
print('rms', np.sqrt((res**2).sum(1).mean()))
json.dump(H.tolist(), open(os.path.join(D, 'H_lights.json'), 'w'))
if 'overlay' in sys.argv:
    from PIL import Image
    R = os.path.join(D, '..', '..', '_quellen', 'kingkong')
    ph = Image.open(os.path.join(R, 'pf.png')).convert('RGB')
    pl = Image.open(os.path.join(R, 'man', 'lights.png')).convert('L')
    Hi = np.linalg.inv(H); Hi = Hi / Hi[2, 2]
    w = pl.transform(ph.size, Image.PERSPECTIVE, tuple(Hi.flatten()[:8]), Image.BILINEAR, fillcolor=255)
    a = np.array(ph).astype(float) * 0.75; m = (np.array(w) < 110)
    a[m] = [255, 0, 255]
    Image.fromarray(a.astype('uint8')).save(os.path.join(R, 'overlay_lights.png'))
