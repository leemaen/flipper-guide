"""Erzeugt content/harrypotter-vpx/inserts.json aus den Licht-Mittelpunkten der Tischdatei (VPX -> Ansichtspixel per Skalierung)."""
import json, glob, os
S = json.load(open('tools/harrypotter-vpx/H_view.json'))[0][0]
L = {}
for f in glob.glob('_quellen/harrypotter-vpx/vpx/harrypotter-vpx/gameitems/Light.*.json'):
    d = json.load(open(f))['Light']; L[d['name']] = (d['center']['x'], d['center']['y'])
spec = json.load(open('tools/harrypotter-vpx/inserts_spec.json', encoding='utf-8'))
out = {}
for k, v in spec.items():
    v = dict(v); v['px'] = [[round(L[n][0] * S, 1), round(L[n][1] * S, 1)] for n in v.pop('lights')]
    out[k] = v
json.dump(out, open('content/harrypotter-vpx/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
