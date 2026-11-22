"""Homographie Stern-Schalterplan (Handbuch S. 17, 200 dpi) -> Stern-Herstellerfoto (1476 x 2500).
Nur zur Identifikation/Prüfung: projiziert die Schalternummern des Plans ins Foto (Prüfbild).
Aufruf: py -3 -I tools/tmnt/plan_H.py
"""
import sys, json, os
sys.path.insert(0, 'tools')
from homography import apply
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nh import fitn as fit
import numpy as np
# Ankerpunkte: Inserts, die in Plan und Foto eindeutig sind (Plan-px, Foto-px)
P = {
 'L': ((704,1164),(465,1167)), 'A1': ((701,1209),(462,1222)), 'I1': ((701,1253),(461,1272)), 'R1': ((704,1298),(459,1325)),
 '123': ((695,1377),(445,1422)),
 'A': ((1092,1144),(977,1148)), 'P': ((1077,1187),(964,1195)), 'R': ((1098,1230),(990,1244)), 'I': ((1086,1274),(976,1298)), 'Lr': ((1106,1314),(1004,1350)),
 'bigclear': ((842,1322),(645,1355)), 'smclear': ((836,1396),(632,1450)), 'rclear': ((992,1370),(848,1417)),
 'c1': ((877,1441),(692,1509)), 'c2': ((960,1441),(791,1509)),
 'c3': ((940,1510),(780,1600)), 'c4': ((975,1543),(830,1645)), 'c5': ((813,1543),(600,1630)), 'c6': ((855,1570),(660,1685)),
 'ep3': ((771,947),(568,935)), 'ep2': ((824,934),(637,921)), 'startep': ((855,843),(679,821)), 'donatello': ((896,921),(712,900)),
 'pop69': ((855,560),(696,544)), 'pop70': ((1040,605),(903,559)), 'pop71': ((915,695),(781,609)),
 'teamup': ((910,1623),(730,1765)), 'training': ((788,1166),(580,1157)),
}
if __name__ == '__main__':
    src = [v[0] for v in P.values()]; dst = [v[1] for v in P.values()]
    H = fit(src, dst); res = apply(H, src) - np.array(dst)
    for k, r in zip(P, res): print(k, np.round(r, 1))
    print('rms', np.sqrt((res**2).sum(1).mean()))
    json.dump(H.tolist(), open('tools/tmnt/H_plan2photo.json', 'w'))
    if '--overlay' in sys.argv:
        from PIL import Image
        pl = Image.open('_quellen/tmnt/man_p17.png').convert('L')
        ph = Image.open('_quellen/tmnt/stern_topview.png').convert('RGB')
        Hi = np.linalg.inv(H); Hi = Hi / Hi[2, 2]
        w = pl.transform(ph.size, Image.PERSPECTIVE, tuple(Hi.flatten()[:8]), Image.BILINEAR, fillcolor=255)
        a = np.array(ph).astype(float); m = np.array(w).astype(float) < 128
        a[m] = a[m] * 0.2 + np.array([0, 255, 255]) * 0.8
        Image.fromarray(a.astype('uint8')).save('_quellen/tmnt/overlay_plan.png')
