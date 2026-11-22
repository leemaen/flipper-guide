"""VPX-Ansicht Transformers: eigenes Draufsicht-Render (render_top.py: pf.webp + texturierte Primitive), aufgehellt, 1000 px breit.
H_vpx = reine Skalierung (Render-Pixel = VPX-Koordinate * 1000/952)."""
import json
from PIL import Image
import numpy as np
im = np.asarray(Image.open('_quellen/transformers/vpx_top.png').convert('RGB'), np.float32) / 255
im = np.clip((im ** 0.85) * 1.05, 0, 1)
out = Image.fromarray((im * 255).astype(np.uint8))
k = 1000 / out.width
out.resize((1000, round(out.height * k)), Image.LANCZOS).save('_quellen/transformers/vpx_view_1000.png')
s = 1200 / 952 * k
json.dump([[s, 0, 0], [0, s, 0], [0, 0, 1]], open('tools/transformers/H_vpx.json', 'w'))
print(out.size, s)
