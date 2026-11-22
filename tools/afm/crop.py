import sys
from PIL import Image
f, out, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
x0 = float(sys.argv[5]) if len(sys.argv) > 5 else 0; x1 = float(sys.argv[6]) if len(sys.argv) > 6 else 1
im = Image.open(f); w, h = im.size; im.crop((int(w*x0), int(h*a), int(w*x1), int(h*b))).save(out)
