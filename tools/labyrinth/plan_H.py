"""Homographie Handbuch-Schalterplan 4-84 (aufgerichtet, switches-upright.png 1102x1815) -> Hersteller-Spielfeldgrafik (1888x4285).
Plan 4-82 (page-164, gedreht -> plan82_up.png) wird über einen eigenen Ankersatz abgebildet. Aufruf: plan_H.py [--overlay]"""
import sys, json
sys.path.insert(0, 'tools'); sys.path.insert(0, 'tools/tmnt')
from homography import apply
from nh import fitn
import numpy as np
P84 = {
 'hoggle': ((364,1163),(512,2732)), 'ludo': ((448,1241),(742,2942)), 'didy': ((564,1247),(1045,2962)),
 'med': ((567,1078),(1025,2517)), 'c1': ((352,1044),(492,2442)), 'c2': ((417,1017),(657,2367)), 'c3': ((630,936),(1220,2155)),
}
if __name__ == '__main__':
    for nm, P, img in [('84', P84, 'old-expansion/switches-upright.png')]:
        src = [v[0] for v in P.values()]; dst = [v[1] for v in P.values()]
        H = fitn(src, dst); res = apply(H, src) - np.array(dst)
        for k, r in zip(P, res): print(nm, k, np.round(r, 1))
        print('rms', np.sqrt((res**2).sum(1).mean()))
        json.dump(H.tolist(), open(f'tools/labyrinth/H_plan{nm}.json', 'w'))
        if '--overlay' in sys.argv:
            from PIL import Image
            pl = Image.open('_quellen/labyrinth/' + img).convert('L')
            ph = Image.open('_quellen/labyrinth/labyrinth-playfield-art.jpg').convert('RGB')
            Hi = np.linalg.inv(H); Hi = Hi/Hi[2, 2]
            w = pl.transform(ph.size, Image.PERSPECTIVE, tuple(Hi.flatten()[:8]), Image.BILINEAR, fillcolor=255)
            a = np.array(ph).astype(float); m = np.array(w).astype(float) < 110
            a[m] = a[m]*0.2 + np.array([255, 0, 255])*0.8
            Image.fromarray(a.astype('uint8')).save(f'_quellen/labyrinth/overlay_{nm}.png')
