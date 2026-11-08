"""Homographie VPX (Batman 66 Stern Tribute 1.1.0) -> Stern-Premium-Foto (Prem Playfield.webp, 1476x2500) aus Insert-Mittelpunkten.
Fotopixel per Gitter-Ausschnitt (tools/gridcrop.py) vermessen; VPX = Licht-Mittelpunkte der Tischdatei."""
import sys, json; sys.path.insert(0, 'tools')
from homography import fit, apply
import numpy as np
it = json.load(open('_quellen/batman66/pages/li_items.json'))
S = 0.8; X0, Y0 = 150, 700
scr = {'lCrane5': (295, 290), 'lCrane4': (405, 430), 'lCrane3': (487, 475), 'lCrane2': (568, 493), 'lCrane1': (648, 493),
       'lCrane5x': (305, 333), 'lCrane4x': (410, 476), 'lCrane3x': (483, 518), 'lCrane2x': (547, 536), 'lCrane1x': (628, 542),
       'lJoker': (408, 680), 'lPeng': (485, 676), 'lRiddler': (528, 718), 'lCatwoman': (357, 718), 'lBatSignal': (443, 752),
       'LightPengScoop': (590, 440), 'lLock1': (668, 445), 'lLock2': (685, 400), 'lLock3': (700, 355),
       'lGadgetT': (200, 400), 'lGadgetE': (200, 445), 'lGadgetG2': (200, 493), 'lGadgetD': (198, 540), 'lGadgetA': (198, 585), 'lGadgetG1': (200, 630),
       'lRiddlerOrbit1': (172, 218), 'lTV': (188, 300), 'lExtraBall': (195, 340),
       'lJokerJ': (315, 175), 'lJokerO': (350, 195), 'lJokerK': (385, 195), 'lJokerE': (420, 190), 'lJokerR': (450, 165),
       'lTV1': (675, 555), 'lTV2': (680, 605), 'lTV3': (683, 650)}
PH = {k: (X0 + x / S, Y0 + y / S) for k, (x, y) in scr.items() if k in it}
missing = [k for k in scr if k not in it]
src = [it[k]['c'] for k in PH]; dst = list(PH.values())
H = fit(src, dst); res = apply(H, src) - np.array(dst)
for k, r in zip(PH, res): print(k, it[k]['c'], np.round(PH[k]), np.round(r, 1))
print('missing', missing, 'rms', np.sqrt((res ** 2).sum(1).mean()), 'n', len(PH))
json.dump(H.tolist(), open('tools/batman66/H_photo.json', 'w'))
