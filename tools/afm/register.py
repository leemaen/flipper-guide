"""Homographie VPX -> Foto ueber Insert-Lichter.
1) SIFT-Grobregistrierung VPX-Ansicht <-> Foto, 2) jedes Insert-Licht per Template-Matching im Foto vermessen,
3) H (VPX-Koordinaten -> Fotopixel) aus den vermessenen Inserts fitten, Residuen/RMS ausgeben.
Aufruf: register.py <id> <vpx_view.png> <sx,sy> <foto> <out_H.json> <lichtregex> [foto_scale]"""
import sys, json, re; sys.path.insert(0, 'tools')
import numpy as np, cv2
from homography import fit, apply
tid, view, sc, photo, outH, rx = sys.argv[1:7]
sx, sy = map(float, sc.split(','))
S = np.diag([sx, sy, 1.0])
V = cv2.imread(view); P = cv2.imread(photo)
k = P.shape[1] / V.shape[1]
Vs = cv2.resize(V, (P.shape[1], int(V.shape[0] * k)))
S2 = np.diag([k, k, 1.0]) @ S                      # VPX -> verkleinerte Ansicht
g1, g2 = cv2.cvtColor(Vs, cv2.COLOR_BGR2GRAY), cv2.cvtColor(P, cv2.COLOR_BGR2GRAY)
sift = cv2.SIFT_create(8000)
k1, d1 = sift.detectAndCompute(g1, None); k2, d2 = sift.detectAndCompute(g2, None)
m = cv2.BFMatcher().knnMatch(d1, d2, k=2)
good = [a for a, b in m if a.distance < 0.75 * b.distance]
A = np.float32([k1[a.queryIdx].pt for a in good]); B = np.float32([k2[a.trainIdx].pt for a in good])
H0, inl = cv2.findHomography(A, B, cv2.RANSAC, 4.0)
print('SIFT matches', len(good), 'inliers', int(inl.sum()))
Hg = H0 @ S2                                         # VPX -> Foto (grob)
W = cv2.warpPerspective(Vs, H0, (P.shape[1], P.shape[0]))
L = json.load(open(f'tools/{tid}/vpx_lights.json'))
names = [n for n in L if re.fullmatch(rx, n)]
src, dst, rep = [], [], []
R, SR = 9, 8
for n in names:
    x, y = apply(Hg, [L[n][:2]])[0]; xi, yi = int(round(x)), int(round(y))
    if xi - R - SR < 0 or yi - R - SR < 0 or xi + R + SR >= P.shape[1] or yi + R + SR >= P.shape[0]: continue
    t = W[yi - R:yi + R + 1, xi - R:xi + R + 1]
    s = P[yi - R - SR:yi + R + SR + 1, xi - R - SR:xi + R + SR + 1]
    if t.std() < 8: continue
    r = cv2.matchTemplate(s, t, cv2.TM_CCOEFF_NORMED); _, mv, _, ml = cv2.minMaxLoc(r)
    if mv < 0.6: continue
    px, py = xi + ml[0] - SR, yi + ml[1] - SR
    src.append(L[n][:2]); dst.append((x + px - xi, y + py - yi)); rep.append((n, round(mv, 2)))
src = np.array(src); dst = np.array(dst)
keep = np.ones(len(src), bool)
for it in range(3):
    H = fit(src[keep], dst[keep]); res = np.linalg.norm(apply(H, src) - dst, axis=1)
    keep = res < max(3 * np.sqrt((res[keep] ** 2).mean()), 2.0)
H = fit(src[keep], dst[keep]); res = np.linalg.norm(apply(H, src) - dst, axis=1)
for (n, c), r, kp in zip(rep, res, keep): print(n, c, round(r, 2), '' if kp else 'VERWORFEN')
print('Inserts verwendet', int(keep.sum()), 'von', len(src), ' RMS px', round(float(np.sqrt((res[keep] ** 2).mean())), 2))
json.dump(H.tolist(), open(outH, 'w'))
json.dump({'points': [[n, list(map(float, s)), list(map(float, d))] for (n, _), s, d, kp in zip(rep, src, dst, keep) if kp]}, open(outH.replace('.json', '_pts.json'), 'w'))
