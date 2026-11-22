"""Symbole der M-A-R-T-I-A-N-Einsätze aus der Spielfeldtextur der Tischdatei (Scan des Original-Artworks) ausschneiden -> app/img/afm-icon-*.png"""
import json
from PIL import Image, ImageDraw
SX, SY = 1.78125, 1.74298
tex = Image.open('_quellen/afm/vpx/afm/images/PLAYFIELD_GI_off_base.png').convert('RGB')
from PIL import ImageEnhance
tex = ImageEnhance.Brightness(tex).enhance(1.9)
L = json.load(open('tools/afm/vpx_lights.json'))
def disc(names, r, out):
    parts = []
    for n in names:
        x, y = L[n][:2]; X, Y = x * SX, y * SY; R = r * SX
        parts.append(tex.crop((int(X - R), int(Y - R), int(X + R), int(Y + R))).resize((120, 120), Image.LANCZOS))
    if len(parts) == 1: im = parts[0]
    else:
        im = Image.new('RGB', (120, 120), (20, 10, 10)); w = 120 // len(parts)
        for i, p in enumerate(parts): im.paste(p.resize((w, w), Image.LANCZOS), (i * w, (120 - w) // 2))
    m = Image.new('L', (120, 120), 0); ImageDraw.Draw(m).ellipse((0, 0, 119, 119), fill=255)
    o = im.convert('RGBA'); o.putalpha(m); o.save(f'app/img/afm-icon-{out}.png')
disc(['l48'], 26, 't'); disc(['l68'], 26, 'i')
disc(['l76', 'l77', 'l78'], 20, 'mar'); disc(['l62', 'l61'], 20, 'an')
