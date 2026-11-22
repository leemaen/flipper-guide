"""VPX-Ansicht für AFM: gebackene Draufsicht PLAYFIELD_GI_off_base aus der g5k-Tischdatei, aufgehellt."""
from PIL import Image
import numpy as np
im = np.asarray(Image.open('_quellen/afm/vpx/afm/images/PLAYFIELD_GI_off_base.png').convert('RGB'), np.float32) / 255
im = np.clip((im ** 0.55) * 1.15, 0, 1)
Image.fromarray((im * 255).astype(np.uint8)).save('_quellen/afm/vpx_view.png')
# App-Fassung 1000 px breit; H_vpx = reine Skalierung VPX -> diese Bildpixel
k = 1000 / im.shape[1]
Image.fromarray((im * 255).astype(np.uint8)).resize((1000, round(im.shape[0] * k)), Image.LANCZOS).save('_quellen/afm/vpx_view_1000.png')
import json
json.dump([[1.78125 * k, 0, 0], [0, 1.74298 * k, 0], [0, 0, 1]], open('tools/afm/H_vpx.json', 'w'))
