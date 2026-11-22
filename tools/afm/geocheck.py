"""Zeichnet geometry.json-Eingänge in eine Ansicht (Volldarstellung + Ausschnitt). geocheck.py <id> <bild> <H.json|scale:sx,sy> <out> [x0 y0 x1 y1]"""
import sys, json, math; sys.path.insert(0, 'tools')
from homography import apply
import numpy as np
from PIL import Image, ImageDraw, ImageFont
tid, src, hs, out = sys.argv[1:5]
H = np.diag([*map(float, hs[6:].split(',')), 1.0]) if hs.startswith('scale:') else np.array(json.load(open(hs)))
geo = json.load(open(f'content/{tid}/geometry.json', encoding='utf-8'))
def unit(a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]; n = math.hypot(dx, dy) or 1; return dx/n, dy/n
def shape(e):
    if e['type'] == 'circle': return [(e['c'][0]+e['r']*math.cos(a), e['c'][1]+e['r']*math.sin(a)) for a in np.linspace(0, 6.283, 24)]
    ux, uy = unit(e['c'], e['toward']); nx, ny = -uy, ux; L, W = e['len']/2, e['w']/2; cx, cy = e['c']
    return [(cx+ux*L*sx+nx*W*sy, cy+uy*L*sx+ny*W*sy) for sx, sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
im = Image.open(src).convert('RGB'); k = 2 if im.width < 800 else 1
if k > 1: im = im.resize((im.width*k, im.height*k), Image.LANCZOS)
d = ImageDraw.Draw(im); f = ImageFont.truetype('arial.ttf', 14)
for sid, s in geo['shots'].items():
    e = s['entrance']; items = e['items'] if e['type'] == 'multi' else [e]
    for it in items:
        q = [tuple(p*k) for p in apply(H, shape(it))]; d.polygon(q, outline=(255, 140, 0)); d.line(q+[q[0]], fill=(255, 140, 0), width=2)
        if 'toward' in it:
            a, b = apply(H, [it['c'], it['toward']])*k; d.line([tuple(a), tuple(b)], fill=(0, 255, 255), width=1)
    c = apply(H, [items[0]['c']])[0]*k; d.text((c[0]+8, c[1]-8), sid, fill=(255, 255, 0), font=f, stroke_width=2, stroke_fill=(0, 0, 0))
for fk, fl in geo['flippers'].items():
    a, b = apply(H, [fl['pivot'], fl['aim']])*k; d.line([tuple(a), tuple(b)], fill=(255, 0, 255), width=3)
if len(sys.argv) > 8:
    x0, y0, x1, y1 = map(int, sys.argv[5:9]); im = im.crop((x0*k, y0*k, x1*k, y1*k))
im.save(out)
