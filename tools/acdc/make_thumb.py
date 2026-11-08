"""Erzeugt ein 360 px breites Vorschaubild. Aufruf: make_thumb.py quelle.png ziel.jpg [x0 y0 x1 y1]"""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB')
if len(sys.argv) > 3: im = im.crop(tuple(int(v) for v in sys.argv[3:7]))
im.resize((360, round(im.height * 360 / im.width)), Image.LANCZOS).save(sys.argv[2], quality=82, optimize=True, progressive=True)
