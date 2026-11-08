"""content/batman66-vpx/content.json aus content/batman66 ableiten.
Die Tribute-VPX bildet die Stern-Regeln im eigenen Script nach (Konstanten in script.vbs Z. 6970-7005: 8 Hauptschurken-Modi,
14 Nebenschurken-Modi, Villain Escape, Villain-MB, Bat Turn, Batusi, Gas Attack, Holy). Kein Original-ROM -> eigener Tisch."""
import json, copy
c = json.load(open('content/batman66/content.json', encoding='utf-8'))
v = copy.deepcopy(c)
v['table'].update({
 'id': 'batman66-vpx', 'name': 'Batman 66 (VPX Tribute)', 'short': 'Batman 66 VPX', 'manufacturer': 'Mr H & Daphishbowl (Tribute an Stern)', 'year': 2021,
 'system': 'VPX, eigenes Script mit PuP-Videos (kein Original-ROM)',
 'editions': '„Batman 66 Stern Tribute“ 1.1.0 (Mr H & Daphishbowl, 24.07.2021). Laut Autoren soll sie sich „exactly like the real thing“ anfühlen; Regeln, Videos und Ablauf sind im Script nachprogrammiert, nicht die Stern-Software. Spielfeld wie Stern Premium/LE. Den echten Tisch findest du als eigenen Eintrag „Batman 66 (Premium)“.',
 'ruleVersion': 'Regeln wie beim echten Tisch nach dem Batman-66-Rulesheet (Code 1.03); im Script geprüft: alle 8 Hauptschurken-, 14 Nebenschurken- und die Wizard-Modi sind vorhanden, ebenso Combos (Rampe/Orbit → Gegenseite), Extraball über den linken Orbit und Bat-Phone. Einzelwerte (Punkte, Zählerstände) habe ich nicht gegen den echten Tisch verglichen.'})
v['sources'] = [s for s in c['sources'] if s['id'] in ('rules', 'ball')]
v['sources'].insert(1, {'id': 'script', 'title': 'Batman 66 Stern Tribute 1.1.0 – Tischscript (Batman 66 Stern Tribute 1.1.0.vbs)', 'url': 'https://vpuniverse.com/files/file/6868-batman-66-stern-tribute/',
                        'use': 'Prüfung, dass die Regeln dem echten Tisch folgen: Modus-Konstanten (Z. 6970–7005), Rampen-/Orbit-Schalter mit Combos (swCat1/swCat2/swLeftOrbit, Z. 23235 ff.), Extraball am linken Orbit (trgVirtualGate, Z. 23304).'})
v['sources'].insert(2, {'id': 'vpx', 'title': 'VPX: Batman 66 Stern Tribute 1.1.0 (Mr H & Daphishbowl)', 'url': 'https://vpuniverse.com/files/file/6868-batman-66-stern-tribute/',
                        'use': 'Schalter-, Ziel-, Flipper- und Lichtpositionen; Draufsicht aus den 3D-Modellen der Tischdatei gerendert.'})
v['views'] = {'vpx': {'label': 'VPX (Tribute 1.1.0)', 'note': 'Draufsicht aus den 3D-Modellen der Tischdatei gerendert (ohne Beleuchtung). Kran und Drehscheibe in Ruhestellung.'}}
for s in v['shots'].values():
    s['sources'] = sorted({('vpx' if x in ('manual', 'photo', 'vpx') else x) for x in s['sources']} | {'script'} if 'rules' in s['sources'] else {('vpx' if x in ('manual', 'photo', 'vpx') else x) for x in s['sources']})
v['limits'] = ['Die Regeln folgen laut Script dem echten Tisch; Punktwerte und Zähler im Detail nicht verglichen.'] + c['limits'][1:]
json.dump(v, open('content/batman66-vpx/content.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for tid, lib in (('batman66', {"id": "batman66", "name": "Batman 66 (Premium)", "manufacturer": "Stern", "year": 2016, "versions": "Echter Tisch (Premium/LE, keine Pro) · VPX-Tribute: eigener Eintrag", "accent": "#7b3fbf", "thumb": "img/batman66-thumb.jpg", "data": "data/batman66.json"}),
                 ('batman66-vpx', {"id": "batman66-vpx", "name": "Batman 66 (VPX Tribute)", "manufacturer": "Mr H & Daphishbowl / Stern-Tribute", "year": 2021, "versions": "VPX (Stern Tribute 1.1.0, Script-Regeln nach dem Original, kein ROM)", "accent": "#7b3fbf", "thumb": "img/batman66-vpx-thumb.jpg", "data": "data/batman66-vpx.json"})):
    json.dump(lib, open(f'content/{tid}/library.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
