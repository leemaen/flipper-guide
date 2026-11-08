"""Ausschnitt eines Pruefbilds vergroessern: ckcrop.py <tisch> x0 y0 x1 y1 out [scale]"""
import sys
from PIL import Image
t, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
s = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
im = Image.open(f'_quellen/pages/check_{t}_real.png').crop((x0, y0, x1, y1))
im.resize((int(im.width*s), int(im.height*s))).save(out)
