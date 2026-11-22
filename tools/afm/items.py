"""Liest Schalter, Flipper, Lichter, Wände aus der entpackten VPX. Aufruf: py -3 -I tools/afm/items.py <id>"""
import sys, json, glob, os
tid = sys.argv[1]
G = f'_quellen/{tid}/vpx/{tid}/gameitems/'
items, lights = {}, {}
for f in glob.glob(G + '*.json'):
    t = os.path.basename(f).split('.')[0]
    try: d = json.load(open(f, encoding='utf-8'))[t]
    except Exception: continue
    c = d.get('center') or d.get('position') or d.get('vCenter')
    if t == 'Light':
        if c: lights[d['name']] = [c['x'], c['y'], d.get('surface', ''), d.get('is_visible', True)]
    elif t in ('Trigger', 'Kicker', 'HitTarget', 'Spinner', 'Gate', 'Bumper', 'Flipper', 'Plunger') and c:
        e = [round(c['x'], 1), round(c['y'], 1)]
        if t == 'Flipper': e += [d.get('start_angle'), d.get('end_angle'), d.get('flipper_radius_max') or d.get('base_radius'), d.get('end_radius')]
        if t == 'HitTarget': e += [d.get('rot_z'), d.get('target_type')]
        items[d['name']] = [t] + e
os.makedirs(f'tools/{tid}', exist_ok=True)
json.dump(items, open(f'tools/{tid}/vpx_items.json', 'w'), indent=0)
json.dump(lights, open(f'tools/{tid}/vpx_lights.json', 'w'), indent=0)
print(len(items), 'items', len(lights), 'lights')
for k, v in sorted(items.items()): print(k, v)
