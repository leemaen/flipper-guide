"""Listet sichtbare Primitives mit Bild, Material und grober Lage (für render_top --skip)."""
import json, glob, os, sys, re
G = os.path.join(sys.argv[1], 'gameitems'); pat = sys.argv[2] if len(sys.argv) > 2 else '.'
for jf in sorted(glob.glob(os.path.join(G, 'Primitive.*.json'))):
    d = json.load(open(jf))['Primitive']
    if not d.get('is_visible', True) or not re.search(pat, json.dumps(d)): continue
    p = d['position']; print(f"{d['name']:32s} pos=({p['x']:.0f},{p['y']:.0f},{p['z']:.0f}) img={d.get('image')} mat={d.get('material')} size={d['size']['x']:.2f}")
