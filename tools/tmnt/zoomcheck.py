"""Vergrößerte Prüfausschnitte mit kräftigen Markierungen.
Aufruf: py -3 -I tools/tmnt/zoomcheck.py <tisch> <ansicht> x0 y0 x1 y1 out.png [scale]   (Koordinaten im Ausgabebild app/img)"""
import json, sys
from PIL import Image, ImageDraw, ImageFont
t, vk = sys.argv[1], sys.argv[2]; x0, y0, x1, y1 = map(int, sys.argv[3:7]); out = sys.argv[7]
sc = float(sys.argv[8]) if len(sys.argv) > 8 else 2.0
d = json.load(open(f'app/data/{t}.json', encoding='utf-8'))
im = Image.open('app/' + d['views'][vk]['image']).convert('RGB'); W, H = im.size
im = im.resize((int(W*sc), int(H*sc)), Image.LANCZOS); dr = ImageDraw.Draw(im)
f = ImageFont.truetype('arial.ttf', 18)
P = lambda p: (p[0]*W*sc, p[1]*H*sc)
for sid, s in d['shots'].items():
    g = s['geom'].get(vk) or {}
    for a in g.get('aim', []): dr.line([P(p) for p in a], fill=(255,255,255), width=2)
    if g.get('path'): dr.line([P(p) for p in g['path']], fill=(80,200,255), width=3)
    for o in g.get('outline', []): dr.polygon([P(p) for p in o], outline=(255,140,0), width=3)
    if g.get('center'): c = P(g['center']); dr.text((c[0]+8, c[1]-10), sid, fill=(255,255,0), font=f, stroke_width=2, stroke_fill=(0,0,0))
for iid, ins in d['inserts'].items():
    gi = ins['geom'].get(vk)
    if not gi: continue
    for p in gi['points']:
        c = P(p); r = gi['r']*W*sc
        dr.ellipse([c[0]-r, c[1]-r, c[0]+r, c[1]+r], outline=(0,255,120), width=3)
    c = P(gi['points'][0]); dr.text((c[0]+r+2, c[1]+6), iid, fill=(120,255,160), font=f, stroke_width=2, stroke_fill=(0,0,0))
im.crop((int(x0*sc), int(y0*sc), int(x1*sc), int(y1*sc))).save(out); print('ok')
