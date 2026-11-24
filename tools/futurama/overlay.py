"""Prüfbild: Schalter, Kicker, Ziele, Spinner, Flipper, Wände und Rampen der VPX-Datei auf die Ansicht projizieren.

Aufruf: py -3 -I tools/futurama/overlay.py <id> <bild> <H.json> [crop x0,y0,x1,y1] [--prims=name1,name2]
Schreibt _quellen/<id>/pages/ov_*.png (Ausschnitte in Originalpixeln, Gitter alle 100 px).
"""
import sys, json, glob, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from homography import apply
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ID, IMG, HF = sys.argv[1:4]
H = np.array(json.load(open(HF)))
G = glob.glob(f'_quellen/{ID}/vpx/*/gameitems/')[0]
PR = next((a.split('=')[1].split(',') for a in sys.argv if a.startswith('--prims=')), [])
im = Image.open(IMG).convert('RGB')
im = Image.blend(im, Image.new('RGB', im.size, (0, 0, 0)), 0.45)
d = ImageDraw.Draw(im); f = ImageFont.truetype('arial.ttf', 14)
items = {}
for fn in glob.glob(G + 'Wall.*.json'):
    w = json.load(open(fn))['Wall']
    if not w.get('is_collidable', True): continue
    pts = [(p['x'], p['y']) for p in w['drag_points']]
    if len(pts) < 2: continue
    q = [tuple(p) for p in apply(H, pts)]
    top = w.get('height_top', 50); bot = w.get('height_bottom', 0)
    col = (255, 80, 80) if bot > 5 else ((80, 200, 255) if top > 30 else (140, 140, 140))
    d.line(q + [q[0]], fill=col, width=2)
for fn in glob.glob(G + 'Ramp.*.json'):
    r = json.load(open(fn))['Ramp']
    if not r.get('is_collidable', True): continue
    pts = [(p['x'], p['y']) for p in r['drag_points']]
    if len(pts) < 2: continue
    q = [tuple(p) for p in apply(H, pts)]
    d.line(q, fill=(255, 0, 255), width=2); d.text(q[0], r['name'], fill=(255, 120, 255), font=f)
for fn in glob.glob(G + 'Rubber.*.json'):
    r = json.load(open(fn))['Rubber']
    pts = [(p['x'], p['y']) for p in r['drag_points']]
    if len(pts) < 2: continue
    q = [tuple(p) for p in apply(H, pts)]
    d.line(q + [q[0]], fill=(200, 200, 60), width=1)
for fn in glob.glob(G + '*.json'):
    t = os.path.basename(fn).split('.')[0]
    if t not in ('Trigger', 'Kicker', 'HitTarget', 'Spinner', 'Gate', 'Bumper', 'Flipper', 'Primitive'): continue
    o = json.load(open(fn))[t]
    if t == 'Primitive' and o['name'] not in PR: continue
    c = o.get('center') or o.get('position')
    if c: items[o['name']] = (c['x'], c['y'], t)
cols = {'Trigger': (0, 255, 0), 'Kicker': (255, 255, 0), 'HitTarget': (255, 128, 0), 'Spinner': (0, 255, 255), 'Gate': (180, 180, 255), 'Bumper': (255, 0, 0), 'Flipper': (255, 255, 255), 'Primitive': (255, 160, 200)}
for n, (x, y, t) in items.items():
    X, Y = apply(H, [(x, y)])[0]
    d.ellipse([X - 6, Y - 6, X + 6, Y + 6], outline=cols[t], width=3)
    d.text((X + 8, Y - 9), n, fill=cols[t], font=f, stroke_width=2, stroke_fill=(0, 0, 0))
for gx in range(0, im.width, 100):
    d.line([(gx, 0), (gx, im.height)], fill=(60, 60, 60)); d.text((gx + 2, 2), str(gx), fill=(200, 200, 200), font=f)
for gy in range(0, im.height, 100):
    d.line([(0, gy), (im.width, gy)], fill=(60, 60, 60)); d.text((2, gy + 2), str(gy), fill=(200, 200, 200), font=f)
os.makedirs(f'_quellen/{ID}/pages', exist_ok=True)
im.save(f'_quellen/{ID}/pages/ov_full.png')
h = im.height
for i, (a, b) in enumerate([(0, h // 3 + 100), (h // 3 - 100, 2 * h // 3 + 100), (2 * h // 3 - 100, h)]):
    im.crop((0, a, im.width, b)).save(f'_quellen/{ID}/pages/ov_{i}.png')
print('ok', len(items))
