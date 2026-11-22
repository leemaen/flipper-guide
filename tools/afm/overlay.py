"""Overlay: Schalter, Lichter, Wände, Rampen (VPX) auf ein Bild. Aufruf: overlay.py <id> <bild> <H.json|scale:sx,sy> <out_prefix> [lights]"""
import sys, json, glob, os; sys.path.insert(0, 'tools')
from homography import apply
import numpy as np
from PIL import Image, ImageDraw, ImageFont
tid, src, hs, outp = sys.argv[1:5]
showL = 'lights' in sys.argv
if hs.startswith('scale:'):
    sx, sy = map(float, hs[6:].split(',')); H = np.diag([sx, sy, 1.0])
else: H = np.array(json.load(open(hs)))
G = f'_quellen/{tid}/vpx/{tid}/gameitems/'
im = Image.open(src).convert('RGB')
im = Image.blend(im, Image.new('RGB', im.size, (0, 0, 0)), 0.45); d = ImageDraw.Draw(im); f = ImageFont.truetype('arial.ttf', 15)
for fn in glob.glob(G + 'Wall.*.json') + glob.glob(G + 'Ramp.*.json') + glob.glob(G + 'Rubber.*.json'):
    t = os.path.basename(fn).split('.')[0]; w = json.load(open(fn, encoding='utf-8'))[t]
    pts = [(p['x'], p['y']) for p in w.get('drag_points', [])]
    if len(pts) < 2: continue
    q = [tuple(p) for p in apply(H, pts)]
    if t == 'Ramp':
        d.line(q, fill=(255, 0, 255), width=2); d.text(q[0], w['name'], fill=(255, 120, 255), font=f)
    elif t == 'Rubber':
        d.line(q, fill=(255, 255, 0), width=1)
    else:
        if not w.get('is_collidable', True): continue
        bot = w.get('height_bottom', 0); top = w.get('height_top', 50)
        col = (255, 80, 80) if bot > 5 else ((80, 200, 255) if top > 30 else (140, 140, 140))
        d.line(q + [q[0]], fill=col, width=2)
it = json.load(open(f'tools/{tid}/vpx_items.json'))
for (n, p), q in zip(it.items(), apply(H, [v[1:3] for v in it.values()])):
    x, y = q; d.ellipse([x-6, y-6, x+6, y+6], outline=(0, 255, 0), width=3); d.text((x+8, y-9), n, fill=(0, 255, 0), font=f, stroke_width=2, stroke_fill=(0, 0, 0))
for fn in glob.glob(G + 'Wall.SW*.json') + glob.glob(G + 'Wall.sw*.json'):
    w = json.load(open(fn))['Wall']; pts = [(p['x'], p['y']) for p in w['drag_points']]
    c = apply(H, [np.mean(pts, 0)])[0]; d.text(tuple(c), w['name'], fill=(0, 255, 255), font=f, stroke_width=2, stroke_fill=(0, 0, 0))
if showL:
    L = json.load(open(f'tools/{tid}/vpx_lights.json'))
    for (n, p), q in zip(L.items(), apply(H, [v[:2] for v in L.values()])):
        x, y = q; d.ellipse([x-4, y-4, x+4, y+4], outline=(255, 160, 0), width=2); d.text((x+5, y+3), n, fill=(255, 200, 80), font=ImageFont.truetype('arial.ttf', 12))
im.save(outp + '.png')
W, Hh = im.size
im.crop((0, 0, W, Hh // 2 + 100)).save(outp + '_top.png'); im.crop((0, Hh // 2 - 100, W, Hh)).save(outp + '_bot.png')
