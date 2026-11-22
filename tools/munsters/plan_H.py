"""Homographie Stern-Lichterplan (Munsters Pro Handbuch S. 19, 200 dpi) -> Stern-Herstellerfoto (1476 x 2500).
Nur Prüfung/Identifikation. Aufruf: py -3 -I tools/munsters/plan_H.py [--overlay] [--plan 16|19]"""
import sys, json, os
sys.path.insert(0, 'tools'); sys.path.insert(0, 'tools/tmnt')
from homography import apply
from nh import fitn
import numpy as np
k = 1.1  # Anzeige(1545 breit) -> Original(1700)
D = lambda x, y: (x*k, y*k)
P = {  # Lichterplan (Anzeige-px) : Foto-px
 'mm': (D(567,1342),(741,1688)), 'herman': (D(503,1396),(639,1769)), 'raven': (D(567,1398),(741,1770)), 'lily': (D(632,1396),(841,1769)),
 'spot': (D(531,1447),(684,1843)), 'grandpa': (D(605,1447),(793,1843)), '2x': (D(548,1495),(694,1911)), '3x': (D(589,1495),(770,1911)),
 'd': (D(380,1010),(470,1228)), 'r': (D(385,1042),(477,1270)), 'a': (D(378,1073),(468,1312)), 'g': (D(384,1105),(470,1355)), 'u': (D(376,1137),(459,1399)), 'l': (D(381,1168),(470,1441)), 'a2': (D(375,1200),(461,1484)),
 'L1': (D(758,1020),(999,1228)), 'I': (D(758,1073),(999,1303)), 'L2': (D(758,1124),(999,1380)),
 'h59': (D(521,745),(677,903)), 'h58': (D(506,771),(657,929)), 'h60': (D(544,766),(712,929)),
}
if __name__ == '__main__':
    src = [v[0] for v in P.values()]; dst = [v[1] for v in P.values()]
    H = fitn(src, dst); res = apply(H, src) - np.array(dst)
    for kk, r in zip(P, res): print(kk, np.round(r, 1))
    print('rms', np.sqrt((res**2).sum(1).mean()))
    json.dump(H.tolist(), open('tools/munsters/H_plan2photo.json', 'w'))
    if '--overlay' in sys.argv:
        from PIL import Image
        for pg in ('16', '19'):
            pl = Image.open(f'_quellen/munsters/man_p{pg}.png').convert('L')
            ph = Image.open('_quellen/munsters/stern_topview.png').convert('RGB')
            Hi = np.linalg.inv(H); Hi = Hi / Hi[2, 2]
            w = pl.transform(ph.size, Image.PERSPECTIVE, tuple(Hi.flatten()[:8]), Image.BILINEAR, fillcolor=255)
            a = np.array(ph).astype(float); m = np.array(w).astype(float) < 128
            a[m] = a[m]*0.2 + np.array([0, 255, 255])*0.8
            Image.fromarray(a.astype('uint8')).save(f'_quellen/munsters/overlay_p{pg}.png')
