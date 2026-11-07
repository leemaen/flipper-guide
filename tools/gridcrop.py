# Usage: py -3 -I gridcrop.py <image> <x0> <y0> <x1> <y1> <out> [step] [scale]
import sys
from PIL import Image, ImageDraw, ImageFont
img, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
step = int(sys.argv[7]) if len(sys.argv) > 7 else 50
scale = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0
im = Image.open(img).convert('RGB').crop((x0, y0, x1, y1))
if scale != 1.0:
    im = im.resize((int(im.width*scale), int(im.height*scale)), Image.LANCZOS)
d = ImageDraw.Draw(im)
try: f = ImageFont.truetype('arial.ttf', 14)
except: f = ImageFont.load_default()
for gx in range((x0//step+1)*step, x1, step):
    X = (gx-x0)*scale; d.line([(X,0),(X,im.height)], fill=(0,255,255) if gx%(step*2)==0 else (0,140,140), width=1)
    d.text((X+2,2), str(gx), fill=(255,255,0), font=f)
for gy in range((y0//step+1)*step, y1, step):
    Y = (gy-y0)*scale; d.line([(0,Y),(im.width,Y)], fill=(0,255,255) if gy%(step*2)==0 else (0,140,140), width=1)
    d.text((2,Y+2), str(gy), fill=(255,255,0), font=f)
im.save(out)
print(im.size)
