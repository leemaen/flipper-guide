"""Schalter, Ziele, Flipper, Lichter und Wände einer entpackten VPX auf eine Draufsicht zeichnen.

Aufruf: py -3 -I tools/acdc/dump_items.py <entpackter_ordner> <bild.png> <H.json> <ausgabe_präfix> [--lights]
H.json: 3x3-Homographie VPX -> Bildpixel. Schreibt <präfix>_items.json und Prüfbilder <präfix>_ov*.png.
"""
import sys, json, glob, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from homography import apply
import numpy as np
from PIL import Image, ImageDraw, ImageFont
D, IMG, HF, OUT = sys.argv[1:5]
LIGHTS = '--lights' in sys.argv
H = np.array(json.load(open(HF)))
G = os.path.join(D, 'gameitems')
items = {}
for f in glob.glob(os.path.join(G, '*.json')):
    t = os.path.basename(f).split('.')[0]
    if t not in ('Trigger', 'Kicker', 'HitTarget', 'Spinner', 'Gate', 'Bumper', 'Flipper', 'Light'): continue
    d = json.load(open(f, encoding='utf-8'))[t]
    c = d.get('center') or d.get('position')
    if not c: continue
    e = {'type': t, 'c': [round(c['x'], 1), round(c['y'], 1)]}
    if t == 'Flipper': e.update(start=d['start_angle'], end=d['end_angle'], len=d['flipper_radius_max'])
    if t == 'Light':
        e['color'] = d.get('color'); e['surface'] = d.get('surface')
        if d.get('drag_points'): e['poly'] = [[round(p['x'], 1), round(p['y'], 1)] for p in d['drag_points']]
    if t == 'Trigger' and d.get('drag_points'): e['poly'] = [[round(p['x'], 1), round(p['y'], 1)] for p in d['drag_points']]
    items[d['name']] = e
json.dump(items, open(OUT + '_items.json', 'w'), indent=0)
im = Image.open(IMG).convert('RGB')
im = Image.blend(im, Image.new('RGB', im.size, (0, 0, 0)), 0.45); d = ImageDraw.Draw(im); f = ImageFont.truetype('arial.ttf', 14)
for fn in glob.glob(os.path.join(G, 'Wall.*.json')):
    w = json.load(open(fn, encoding='utf-8'))['Wall']
    if not w.get('is_collidable', True): continue
    pts = [(p['x'], p['y']) for p in w['drag_points']]
    if len(pts) < 2: continue
    q = [tuple(p) for p in apply(H, pts)]
    bot = w.get('height_bottom', 0); top = w.get('height_top', 50)
    col = (255, 80, 80) if bot > 5 else ((80, 200, 255) if top > 30 else (140, 140, 140))
    d.line(q + [q[0]], fill=col, width=1)
for n, e in items.items():
    if e['type'] == 'Light' and not LIGHTS: continue
    x, y = apply(H, [e['c']])[0]
    col = {'Trigger': (0, 255, 0), 'Kicker': (255, 0, 255), 'HitTarget': (255, 255, 0), 'Spinner': (0, 255, 255), 'Gate': (255, 160, 0),
           'Bumper': (255, 255, 255), 'Flipper': (255, 255, 255), 'Light': (255, 120, 120)}[e['type']]
    if e.get('poly') and e['type'] == 'Trigger':
        d.polygon([tuple(p) for p in apply(H, e['poly'])], outline=col)
    d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=col, width=2)
    d.text((x + 7, y - 8), n, fill=col, font=f, stroke_width=2, stroke_fill=(0, 0, 0))
im.save(OUT + '_ov.png')
w, h = im.size
im.crop((0, 0, w, h // 2 + 60)).save(OUT + '_ov_top.png')
im.crop((0, h // 2 - 60, w, h)).save(OUT + '_ov_bot.png')
print(len(items), 'items')
