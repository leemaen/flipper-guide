"""Labyrinth: Geometrie + Einsätze in Pixeln der Hersteller-Spielfeldgrafik (Handbuch 1.3, 1888 x 4285) erfassen
und für die Ansicht (art_1000.png, auf 1000 px Breite skaliert) umrechnen.
Quellen der Koordinaten: Schusskarten des Handbuchs (S. 2-3 bis 2-16; dieselbe Grafik, 600-dpi-Ausschnitt ~ Grafik x 1,0048),
Schalterplan 4-84 (tools/labyrinth/plan_H.py) als Gegenprobe.
Aufruf: py -3 -I tools/labyrinth/make_geo.py"""
import json
S = 1000 / 1888          # Grafik-px -> Ansicht-px
M = 1 / 1.0048           # Karten-px -> Grafik-px
def m(x, y): return [round(x * M * S, 1), round(y * M * S, 1)]   # aus Schusskarten-Koordinaten
def a(x, y): return [round(x * S, 1), round(y * S, 1)]           # direkt in der Grafik gemessen
def v(x, y): return [x, y]                                       # direkt in der Ansicht (art_1000) gemessen
def lane(c, t, ln, w): return {"type": "lane", "c": c, "toward": t, "len": ln, "w": w}
def rect(c, t, ln, w): return {"type": "rect", "c": c, "toward": t, "len": ln, "w": w}
def circ(c, r): return {"type": "circle", "c": c, "r": r}
# Längen/Breiten in Ansicht-px (pxToVpx rechnet in Einheiten um)
shots = {
 "left_orbit":   lane(m(300, 1990), m(235, 1820), 40, 40),
 "forks":        {"type": "multi", "items": [circ(m(200, 1911), 13), circ(m(306, 1875), 13)]},
 "left_ramp":    lane(m(510, 1840), m(470, 1700), 40, 46),
 "change_mode":  rect(v(425, 893), v(420, 870), 10, 30),
 "village":      circ(v(261, 929), 26),
 "inner_loop":   lane(m(650, 1320), m(560, 1200), 40, 40),
 "center_ramp":  lane(m(765, 900), m(720, 760), 40, 40),
 "horseshoe_l":  lane(m(1000, 850), m(1015, 730), 36, 40),
 "wiseman":      rect(m(1180, 1050), m(1190, 1000), 12, 40),
 "horseshoe_r":  lane(m(1395, 1060), m(1425, 950), 36, 40),
 "wiseman_targets": {"type": "multi", "items": [rect(m(1060, 1073), m(1060, 1040), 10, 24), rect(m(1293, 1150), m(1293, 1117), 10, 24)]},
 "right_ramp":   lane(v(835, 735), v(845, 665), 40, 50),
 "right_orbit":  lane(m(1748, 1320), m(1752, 1180), 40, 40),
 "ello_lane":    lane(v(835, 1070), v(860, 1025), 34, 34),
 "ello_target":  rect(m(1467, 2567), m(1430, 2540), 10, 30),
 "helping_hands": lane(m(225, 2385), m(190, 2310), 36, 36),
 "junk_lady":    rect(m(150, 2110), m(185, 2110), 10, 26),
 "upper_flipper": circ(m(1650, 1850), 22),
}
fairy = {"type": "multi", "items": [rect(m(431, 1939), m(431, 1905), 10, 24), rect(m(675, 1814), m(675, 1780), 10, 24),
                                    rect(m(889, 944), m(889, 910), 10, 24), rect(m(736, 1258), m(736, 1224), 10, 24),
                                    rect(m(222, 2717), m(256, 2717), 10, 24)]}
shots["lock_targets"] = fairy
geo = {
 "_note": "Pixel der Ansicht art_1000.png (= Hersteller-Spielfeldgrafik aus dem Handbuch 1.3, 1888 px breit, auf 1000 px skaliert). Erzeugt von tools/labyrinth/make_geo.py aus den Schusskarten des Handbuchs (gleiche Grafik) mit Gegenprobe am Schalterplan 4-84. H = Skalierung 1,0593: 50 Einheiten = 1 1/16 Zoll Kugel.",
 "space": "px:art", "pxToVpx": round(1/1.0593, 4), "flipperSpace": "px",
 "flippers": {"L": {"pivot": v(300, 1912), "aim": v(370, 1950)}, "R": {"pivot": v(625, 1912), "aim": v(555, 1950)},
              "UR": {"pivot": v(905, 975), "aim": v(845, 990)}},
 "shots": {k: {"entrance": v} for k, v in shots.items()}
}
json.dump(geo, open('content/labyrinth/geometry.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def P(*pts): return [m(*p) for p in pts]
ins = {
 "lock_ins": {"name": "Grüne Lock-Einsätze (Wall + 4 Fairies)", "en": "Brick Keeper lock target inserts", "text": "Blinken grün vor den fünf Zielen. Jeder Treffer macht einen Einsatz dauerhaft grün. Alle fünf = Ball Lock leuchtet (Handbuch 2-13).", "px": P((278, 2730), (444, 2036), (675, 1830), (889, 1017), (736, 1258)), "r": 16},
 "lock_tri": {"name": "Lock 1 · Lock 2 · Start Multiball", "en": "Lock triangles", "text": "Dreieck-Einsätze: Lock 1 am linken Orbit, Lock 2 an der Mittelrampe, Start Multiball am rechten Orbit (Handbuch 2-13).", "px": P((361, 2119), (792, 1017), (1778, 1194)), "r": 20},
 "start_mode": {"name": "Start Mode", "en": "Start Mode inserts", "text": "Runde Einsätze links und rechts am Horseshoe. Blinken, wenn LABYRINTH komplett ist: Horseshoe oder Wiseman-Scoop startet den Modus (Handbuch 2-3).", "px": P((973, 1160), (1293, 1400)), "r": 28},
 "friends_adv": {"name": "Advance-Friend-Kreise", "en": "Advance Friend inserts (5)", "text": "Fünf runde Einsätze. Blinkend in Freundesfarbe = Freund finden, dauerhaft = Gegenstand sammeln. Gelb Hoggle, orange Ludo, blau Sir Didymus (Handbuch 2-10).", "px": P((817, 1533), (1660, 1667), (1217, 2160), (500, 2433), (660, 2373)), "r": 24},
 "friend_faces": {"name": "Hoggle · Ludo · Sir Didymus", "en": "Friend faces + Jackpot Ready", "text": "Gesichter leuchten, wenn der Freund gefunden ist; „Jackpot Ready“ blinkt, wenn sein Jackpot am Helping-Hands-Scoop bereit ist.", "px": P((512, 2730), (735, 2955), (1045, 2962)), "r": 80},
 "help_ins": {"name": "H-E-L-P", "en": "HELP lane inserts", "text": "In- und Outlanes. HELP komplett = Helping-Hands-Scoop leuchtet (Handbuch 2-3).", "px": P((95, 2983), (250, 2983), (1490, 2983), (1625, 2983)), "r": 20},
 "modes_ins": {"name": "Modus-Einsätze", "en": "Knockers · Four Guards · Fireys / Cleaners · Oubliette · Bog", "text": "Obere Reihe: Knockers, Four Guards, Fireys. Untere Reihe: Cleaners, Oubliette, Bog. Leuchten für gespielte/aktuelle Modi (Handbuch 2-3).", "px": P((870, 2400), (1025, 2390), (1180, 2400), (870, 2600), (1025, 2620), (1180, 2600)), "r": 40},
 "ello_ins": {"name": "Ello Mystery", "en": "Ello Mystery insert", "text": "Leuchtet nach beiden Wiseman-Zielen in derselben Kugel. Dann die Ello-Bahn unter dem oberen rechten Flipper (Handbuch 2-16).", "px": [v(741, 1141)], "r": 18},
 "orb_ins": {"name": "Collect Orb", "en": "Collect Orb insert", "text": "Dreieck vor der Ello-Bahn. Leuchtet nach einer der 13 Errungenschaften: 10 Mio. (Handbuch 2-17).", "px": [v(825, 1083)], "r": 18},
 "forks_ins": {"name": "Fang-Gabeln", "en": "Forks (blue circles)", "text": "Blaue Kreise im linken Orbit. Leuchten, wenn die Gabeln eine Kugel fangen (Fireys, Brick-Keeper-Super-Jackpot, Goblin City).", "px": P((200, 1911), (306, 1875)), "r": 18},
}
json.dump(ins, open('content/labyrinth/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
