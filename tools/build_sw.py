"""Erzeugt app/sw-manifest.json und app/sw.js mit Dateiliste und Inhalts-Version."""
import hashlib, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
skip = {'sw.js', 'sw-manifest.json', '.nojekyll'}
assets, hsh = [], hashlib.sha256()
for dp, dn, fn in os.walk(APP):
    dn.sort()
    for f in sorted(fn):
        rel = os.path.relpath(os.path.join(dp, f), APP).replace(os.sep, '/')
        if rel in skip: continue
        data = open(os.path.join(dp, f), 'rb').read()
        hsh.update(rel.encode()); hsh.update(data)
        assets.append(rel)
version = hsh.hexdigest()[:12]
assets = ['./'] + assets + ['sw-manifest.json']
json.dump({'version': version, 'assets': assets}, open(os.path.join(APP, 'sw-manifest.json'), 'w'), indent=1)
tpl = open(os.path.join(ROOT, 'tools/sw_template.js'), encoding='utf-8').read()
open(os.path.join(APP, 'sw.js'), 'w', encoding='utf-8').write(tpl.replace('__VERSION__', version).replace('__ASSETS__', json.dumps(assets)))
open(os.path.join(APP, '.nojekyll'), 'w').close()
print('version', version, len(assets), 'assets')
