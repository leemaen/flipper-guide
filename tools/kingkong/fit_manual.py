"""Homographie Handbuch-Schalterplan (Bild sw_0.png aus Stern-Pro-Handbuch S. 20) -> Spielfeldfoto.
Nur zur Kontrolle der Schalterlagen; die Schussgeometrie wird direkt im Foto gemessen.
Aufruf: py -3 -I tools/kingkong/fit_manual.py [overlay]"""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from homography import fit, apply
import numpy as np
P = {  # name: (Plan-Pixel, Foto-Pixel)
 'K1': ((440,1957),(462,1534)), 'I': ((490,1895),(503,1492)), 'N1': ((557,1852),(550,1459)), 'G1': ((630,1825),(600,1441)),
 'K2': ((757,1825),(700,1441)), 'O': ((828,1852),(750,1457)), 'N2': ((895,1895),(797,1492)), 'G2': ((942,1957),(837,1532)),
 'eye': ((692,1885),(655,1484)), 'pit': ((425,1700),(450,1338)),
 'Lflip': ((475,2408),(488,1878)), 'Rflip': ((908,2408),(818,1878)),
}
P.update(json.load(open(os.path.join(os.path.dirname(__file__), 'fit_extra.json')))) if os.path.exists(os.path.join(os.path.dirname(__file__), 'fit_extra.json')) else None
src = [v[0] for v in P.values()]; dst = [v[1] for v in P.values()]
H = fit(src, dst); res = apply(H, src) - np.array(dst)
for k, r in zip(P, res): print(k, np.round(r, 1))
print('rms', np.sqrt((res**2).sum(1).mean()))
json.dump(H.tolist(), open(os.path.join(os.path.dirname(__file__), 'H_manual.json'), 'w'))
if 'overlay' in sys.argv:
    from PIL import Image
    R = os.path.join(os.path.dirname(__file__), '..', '..', '_quellen', 'kingkong')
    ph = Image.open(os.path.join(R, 'pf.png')).convert('RGB')
    pl = Image.open(os.path.join(R, 'man', 'sw_0.png')).convert('L')
    Hi = np.linalg.inv(H); Hi = Hi / Hi[2, 2]
    w = pl.transform(ph.size, Image.PERSPECTIVE, tuple(Hi.flatten()[:8]), Image.BILINEAR, fillcolor=255)
    a = np.array(ph).astype(float); m = (np.array(w) < 128)
    a[m] = [255, 0, 255]
    Image.fromarray(a.astype('uint8')).save(os.path.join(R, 'overlay_manual.png'))
