"""Homographie VPX (JP's Deadpool 6.1.0) -> Stern-Pro-Foto (DP-Pro-Playfield-01a, 1384x2500) aus Insert-Mittelpunkten.
Fotopixel per Gitter-Ausschnitt (tools/gridcrop.py) vermessen; VPX-Werte = Licht-Mittelpunkte der Tischdatei."""
import sys, json; sys.path.insert(0, 'tools')
from homography import fit, apply
import numpy as np
it = json.load(open('_quellen/deadpool/pages/li_items.json'))
PH = {
 'li005': (652, 1782), 'li003': (578, 1810), 'li004': (723, 1810), 'li002': (652, 1838),
 'li024': (395, 1255), 'li023': (394, 1310), 'li022': (392, 1365), 'li021': (390, 1417),
 'li020': (960, 1257), 'li019': (960, 1310), 'li018': (959, 1365), 'li017': (960, 1417),
 'li008': (505, 1582), 'li010': (652, 1582), 'li011': (803, 1582), 'li007': (570, 1680), 'li009': (730, 1680),
 'li012': (850, 1488), 'li013': (793, 1365),
}
PH.update(json.load(open('tools/deadpool/extra_pts.json')) if __import__('os').path.exists('tools/deadpool/extra_pts.json') else {})
src = [it[k]['c'] for k in PH]; dst = list(PH.values())
H = fit(src, dst); res = apply(H, src) - np.array(dst)
for k, r in zip(PH, res): print(k, it[k]['c'], PH[k], np.round(r, 1))
print('rms', np.sqrt((res ** 2).sum(1).mean()), 'n', len(PH))
json.dump(H.tolist(), open('tools/deadpool/H_photo.json', 'w'))
