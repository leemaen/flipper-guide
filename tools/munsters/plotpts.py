"""Plan-Punkte (Schalter p16 / Lichter p19) ins Foto projizieren und beschriften. Aufruf: plotpts.py x0 y0 x1 y1 out scale"""
import json, sys
sys.path.insert(0, 'tools')
from homography import apply
import numpy as np
from PIL import Image, ImageDraw, ImageFont
H = np.array(json.load(open('tools/munsters/H_plan2photo.json')))
k = 1.1
x0, y0, x1, y1 = map(int, sys.argv[1:5]); out = sys.argv[5]; sc = float(sys.argv[6])
sw = {'64':(543,388),'65':(1027,395),'69':(875,313),'70':(952,663),'68':(604,697),'45':(698,582),'39':(792,580),'59':(824,703),'37':(591,790),'38':(673,765),'40':(877,785),'41':(962,828),'34':(545,848),'29':(486,948),'28':(534,1040),'28b':(534,1115),'31':(1003,1040),'31b':(1003,1120),'50':(824,507),'51':(970,540),'52':(858,624),'53':(893,478),'54':(948,478),'32':(1048,1073)}
im = Image.open('_quellen/munsters/stern_topview.png').convert('RGB').crop((x0, y0, x1, y1))
im = im.resize((int(im.width*sc), int(im.height*sc)), Image.LANCZOS); d = ImageDraw.Draw(im)
f = ImageFont.truetype('arial.ttf', 16)
for n, (x, y) in sw.items():
    X, Y = apply(H, [((x-188)*k, y*k)])[0]; X = (X-x0)*sc; Y = (Y-y0)*sc
    d.ellipse([X-5, Y-5, X+5, Y+5], outline=(255, 0, 255), width=2); d.text((X+6, Y-8), 'S'+n, fill=(255, 80, 255), font=f, stroke_width=2, stroke_fill=(0,0,0))
im.save(out)
