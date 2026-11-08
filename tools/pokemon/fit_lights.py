"""Homographie Lampenplan (Stern Pokémon Pro-Handbuch S. 25, Vektor-PDF, Koordinaten in PDF-Punkten aus man/words.json)
-> Spielfeldfoto (_quellen/pokemon/pf.png). Nur Zuordnung/Kontrolle; Schüsse werden im Foto gemessen.
Aufruf: py -3 -I tools/pokemon/fit_lights.py [overlay]"""
import sys, json, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, '..'))
from homography import fit, apply
import numpy as np
P = {  # Lampe: (PDF-Punkte, Foto-Pixel)
 '76 Bulbasaur': ((151.1,354.3),(345,1092)), '88 Squirtle': ((186.6,378.6),(488,1180)), '118 Pikachu': ((275.3,364.1),(798,1139)), '127 Charmander': ((307.9,337.1),(936,1048)),
 '80 LO X': ((161.8,391.7),(380,1221)), '92 LR X': ((199.0,417.3),(515,1315)), '122 RR X': ((261.4,399.9),(762,1262)), '131 RO X': ((294.9,383.1),(886,1180)),

 '45 Discover': ((269.2,457.6),(786,1473)), '46 Catch': ((263.2,469.8),(768,1518)), '47 Train': ((257.5,482.2),(748,1561)), '48 Battle': ((251.0,494.0),(724,1609)),
 '11 BS L': ((127.2,488.6),(245,1588)), '12 BS R': ((325.5,488.2),(1009,1588)), '18 Shoot Again': ((226.1,582.2),(627,1971)), '17 Electric': ((182.3,543.3),(451,1812)),
}
src = [v[0] for v in P.values()]; dst = [v[1] for v in P.values()]
def nfit(a, b):  # normalisierte DLT (homography.fit ist bei PDF-Punkten schlecht konditioniert)
    a = np.array(a, float); b = np.array(b, float)
    def T(p):
        m = p.mean(0); k = np.sqrt(2) / np.mean(np.linalg.norm(p - m, axis=1)); return np.array([[k, 0, -k*m[0]], [0, k, -k*m[1]], [0, 0, 1]])
    Ta, Tb = T(a), T(b); Hn = fit(apply(Ta, a), apply(Tb, b)); Hh = np.linalg.inv(Tb) @ Hn @ Ta; return Hh / Hh[2, 2]
H = nfit(src, dst); res = apply(H, src) - np.array(dst)
for k, r in zip(P, res): print(k, np.round(r, 1))
print('rms', np.sqrt((res**2).sum(1).mean()))
json.dump(H.tolist(), open(os.path.join(D, 'H_lights.json'), 'w'))
if 'overlay' in sys.argv:
    from PIL import Image
    R = os.path.join(D, '..', '..', '_quellen', 'pokemon')
    ph = Image.open(os.path.join(R, 'pf.png')).convert('RGB')
    for nm, col in (('li', (255, 0, 255)), ('sw', (0, 255, 255))):
        pl = Image.open(os.path.join(R, 'man', nm + '_300.png')).convert('L')
        S = np.diag([72/300, 72/300, 1])  # Bildpixel (300 dpi) -> PDF-Punkte
        Hp = H @ S; Hi = np.linalg.inv(Hp); Hi = Hi / Hi[2, 2]
        w = pl.transform(ph.size, Image.PERSPECTIVE, tuple(Hi.flatten()[:8]), Image.BILINEAR, fillcolor=255)
        a = np.array(ph).astype(float) * 0.8; m = (np.array(w) < 110); a[m] = col
        Image.fromarray(a.astype('uint8')).save(os.path.join(R, f'overlay_{nm}.png'))
