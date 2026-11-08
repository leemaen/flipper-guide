"""Erzeugt Geometrie, Inserts und build.json für batman66 (Stern-Foto) und batman66-vpx (Draufsicht der Tribute-VPX).
Eingänge in Pixeln des Stern-Premium-Fotos vermessen (Gitter-Ausschnitte); Ziele/Bumper/Bahnen aus den Schaltern der
Tribute-VPX per Homographie (tools/batman66/H_photo.json, RMS 4,0 px über 36 Inserts) ins Foto übertragen.
Für batman66-vpx wird alles mit der inversen Homographie in VPX-Koordinaten zurückgerechnet."""
import sys, json, os
sys.path.insert(0, 'tools')
from homography import apply
import numpy as np
H = np.array(json.load(open('tools/batman66/H_photo.json'))); Hi = np.linalg.inv(H)
it = json.load(open('_quellen/batman66/pages/li_items.json'))
P = lambda n: [round(float(v), 1) for v in apply(H, [it[n]['c']])[0]]
SC = 0.92   # Fotopixel -> VPX-Einheiten (mittlerer Maßstab der Homographie)

def rect(c, dx, dy, ln, w): return {'type': 'rect', 'c': c, 'toward': [c[0] + dx, c[1] + dy], 'len': ln, 'w': w}
shots = {
 'left_orbit':  {'entrance': {'type': 'lane', 'c': [352, 815], 'toward': [350, 760], 'len': 50, 'w': 48}},
 'left_ramp':   {'entrance': {'type': 'lane', 'c': [456, 888], 'toward': [440, 840], 'len': 46, 'w': 66}},
 'turntable':   {'entrance': {'type': 'lane', 'c': [603, 805], 'toward': [603, 760], 'len': 40, 'w': 72}},
 'right_ramp':  {'entrance': {'type': 'lane', 'c': [772, 882], 'toward': [790, 835], 'len': 46, 'w': 66}},
 'spinner':     {'entrance': {'type': 'lane', 'c': P('Spinner001'), 'toward': [P('Spinner001')[0] + 2, P('Spinner001')[1] - 50], 'len': 34, 'w': 46}},
 'penguin':     {'entrance': {'type': 'circle', 'c': P('KickerPeng'), 'r': 24}},
 'gordon':      {'entrance': rect(P('tgGordon'), -10, 28, 14, 36)},
 'right_orbit': {'entrance': {'type': 'lane', 'c': [1088, 945], 'toward': [1092, 890], 'len': 50, 'w': 48}},
 'gadget':      {'entrance': {'type': 'multi', 'items': [rect(P(n), 30, 0, 12, 44) for n in ('tgtT', 'tgtE', 'tgtG2', 'tgtD', 'tgtA', 'tgtG')]}},
 'tv':          {'entrance': {'type': 'multi', 'items': [rect(P(n), -30, -3, 12, 44) for n in ('tgtTV1', 'tgtTV2', 'tgtTV3')]}},
 'bumpers':     {'entrance': {'type': 'multi', 'items': [{'type': 'circle', 'c': P(n), 'r': 44} for n in ('Bumper001', 'Bumper002', 'Bumper003')]}},
 'pow':         {'entrance': rect(P('tgtPow'), 0, 30, 12, 34)},
 'bat_lanes':   {'entrance': {'type': 'multi', 'items': [rect(P(n), 2, -55, 56, 32) for n in ('swInlane1', 'swInlane2', 'swInlane3')]}},
 'lanes':       {'entrance': {'type': 'multi', 'items': [rect(P(n), 0, -60, 58, 34) for n in ('swLeftOutlane', 'swLeftInlane', 'swRightInlane', 'swRightOutlane')]}},
 'plunger':     {'entrance': {'type': 'lane', 'c': [1188, 1960], 'toward': [1186, 1860], 'len': 170, 'w': 44}},
}
flippers = {'L': {'pivot': [271.0, 1778.8], 'aim': [347, 1792]}, 'R': {'pivot': [593.9, 1778.8], 'aim': [518, 1792]}}
note = ('Eingänge in Pixeln des Stern-Premium-Fotos (Prem Playfield.webp, 1476x2500) vermessen: Pfeil-Inserts liegen davor, markiert ist die Bahnmündung. '
        'Ziele, Bumper, Bahnen, Spinner und Penguin-Scoop aus der Tribute-VPX per Homographie (RMS 4,0 px, 36 Inserts) übertragen und mit dem Stern-Schalterplan (Handbuch 500-55I3-01 S. 14-16) abgeglichen. '
        'Die Drehscheiben-Ziele (Bat Computer / Crime Analyzer, Schalter 71/72) sitzen auf der drehenden Scheibe und sind nicht markiert.')
json.dump({'_note': note, 'space': 'px:real', 'pxToVpx': SC, 'flippers': flippers, 'shots': shots},
          open('content/batman66/geometry.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def to_vpx(e):
    e = dict(e)
    for k in ('c', 'toward'):
        if k in e: e[k] = [round(float(v), 1) for v in apply(Hi, [e[k]])[0]]
    for k in ('len', 'w', 'r'):
        if k in e: e[k] = round(e[k] * SC, 1)
    if 'items' in e: e['items'] = [to_vpx(i) for i in e['items']]
    return e
vshots = {k: {'entrance': to_vpx(v['entrance'])} for k, v in shots.items()}
json.dump({'_note': note + ' Hier in VPX-Koordinaten umgerechnet.', 'space': 'vpx', 'flippers': flippers, 'shots': vshots},
          open('content/batman66-vpx/geometry.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# Inserts: Foto-Pixel (gemessen, siehe fit_H.py) bzw. VPX-Licht * 1,05
S, X0, Y0 = 0.8, 150, 700
scr = {'lCrane5': (295, 290), 'lCrane4': (405, 430), 'lCrane3': (487, 475), 'lCrane2': (568, 493), 'lCrane1': (648, 493),
       'lJoker': (408, 680), 'lPeng': (485, 676), 'lRiddler': (528, 718), 'lCatwoman': (357, 718), 'lBatSignal': (443, 752),
       'LightPengScoop': (590, 440), 'lLock1': (668, 445), 'lLock2': (685, 400), 'lLock3': (700, 355),
       'lGadgetT': (200, 400), 'lGadgetE': (200, 445), 'lGadgetG2': (200, 493), 'lGadgetD': (198, 540), 'lGadgetA': (198, 585), 'lGadgetG1': (200, 630),
       'lRiddlerOrbit1': (172, 218), 'lTV': (188, 300), 'lExtraBall': (195, 340),
       'lJokerJ': (315, 175), 'lJokerO': (350, 195), 'lJokerK': (385, 195), 'lJokerE': (420, 190), 'lJokerR': (450, 165),
       'lTV1': (675, 555), 'lTV2': (680, 605), 'lTV3': (683, 650)}
PH = {k: (round(X0 + x / S, 1), round(Y0 + y / S, 1)) for k, (x, y) in scr.items()}
G = {
 'villains': ('Schurken: Catwoman · Joker · Penguin · Riddler', 'Major villain inserts', 'Die vier Hauptschurken. Verhaftete Schurken leuchten.', ['lCatwoman', 'lJoker', 'lPeng', 'lRiddler'], 22),
 'batsignal': ('Bat-Signal', 'Bat-Signal insert', 'Großes Insert über den Flippern.', ['lBatSignal'], 20),
 'gadget_ins': ('G-A-D-G-E-T', 'GADGET inserts', 'Zeigen die sechs GADGET-Ziele links. GADGET komplett = ein Gadget für den Action-Knopf.', ['lGadgetG1', 'lGadgetA', 'lGadgetD', 'lGadgetG2', 'lGadgetE', 'lGadgetT'], 17),
 'tv_ins': ('TV-Anzeigen', 'TV target inserts', 'Zeigen die drei TV-Ziele rechts. Alle drei, dann linker Orbit = Nebenschurke (Minor Villain).', ['lTV1', 'lTV2', 'lTV3'], 18),
 'joker_ins': ('J-O-K-E-R', 'JOKER inserts', 'Joker-Fortschritt; der Joker wird über die Villain-Vision-Ziele an der Drehscheibe qualifiziert.', ['lJokerJ', 'lJokerO', 'lJokerK', 'lJokerE', 'lJokerR'], 15),
 'crane_spots': ('Abrissbirnen-Stellen', 'Crane / wrecking ball spots (purple)', 'Fünf violette Inserts: Hier hält die Abrissbirne des Krans im Penguin-Modus. Nur Anzeige – getroffen wird die Kugel des Krans.', ['lCrane1', 'lCrane2', 'lCrane3', 'lCrane4', 'lCrane5'], 22),
 'lock_ins': ('Lock 1–3', 'Lock inserts', 'Zeigen die gelockten Kugeln für den Villain-Multiball.', ['lLock1', 'lLock2', 'lLock3'], 18),
 'peng_ins': ('Penguin-Scoop-Anzeige', 'The Penguin insert', 'Vor dem Penguin-Scoop.', ['LightPengScoop'], 18),
 'left_ins': ('Riddler · TV · Extraball (links)', 'Riddler / TV / Extra Ball inserts at the left orbit', 'Am linken Orbit: Riddler-Schuss, Nebenschurke bereit, Extraball bereit.', ['lRiddlerOrbit1', 'lTV', 'lExtraBall'], 16),
}
real = {k: {'name': v[0], 'en': v[1], 'text': v[2], 'px': [list(PH[n]) for n in v[3]], 'r': v[4]} for k, v in G.items()}
vpx = {k: {'name': v[0], 'en': v[1], 'text': v[2], 'px': [[round(it[n]['c'][0] * 1.05, 1), round(it[n]['c'][1] * 1.05, 1)] for n in v[3]], 'r': v[4]} for k, v in G.items()}
json.dump(real, open('content/batman66/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(vpx, open('content/batman66-vpx/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for tid, view, Hf, src, crop, out in (('batman66', 'real', 'tools/batman66/H_photo.json', '_quellen/batman66/fotos/stern_b66_prem_playfield.png', [180, 160, 1300, 2330], 'batman66-real.jpg'),
                                      ('batman66-vpx', 'vpx', 'tools/batman66/H_vpx.json', '_quellen/batman66/vpx_top.png', [0, 0, 1000, 2221], 'batman66-vpx.jpg')):
    json.dump({'views': {view: {'H': Hf, 'src': src, 'crop': crop, 'out': out, 'quality': 86}}, 'insertsView': view},
              open(f'content/{tid}/build.json', 'w', encoding='utf-8'), indent=1)
print('ok', len(shots), len(real))
