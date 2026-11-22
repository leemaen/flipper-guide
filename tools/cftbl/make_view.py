"""VPX-Ansicht CFTBL: eigenes Draufsicht-Render der VLM-Bake-Meshes (render_top.py), aufgehellt, 1000 px breit.
H_vpx = reine Skalierung (Render-Pixel = VPX-Koordinate * 1000/964)."""
import json
from PIL import Image
import numpy as np
im = np.asarray(Image.open('_quellen/cftbl/vpx_top.png').convert('RGB'), np.float32) / 255
im = np.clip((im ** 0.6) * 1.2, 0, 1)
out = Image.fromarray((im * 255).astype(np.uint8))
k = 1000 / out.width
out.resize((1000, round(out.height * k)), Image.LANCZOS).save('_quellen/cftbl/vpx_view_1000.png')
s = 1200 / 964 * k
json.dump([[s, 0, 0], [0, s, 0], [0, 0, 1]], open('tools/cftbl/H_vpx.json', 'w'))
print(out.size, s)
