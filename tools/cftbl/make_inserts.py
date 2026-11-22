"""content/cftbl/inserts.json: Insert-Lichter der VPW-Tischdatei (Lampennummern = Bally-Lampenliste, Handbuch S. 2-40) in Pixel der VPX-Ansicht (vpx_view_1000.png)."""
import sys, json; sys.path.insert(0, 'tools')
import numpy as np
from homography import apply
H = np.array(json.load(open('tools/cftbl/H_vpx.json'))); L = json.load(open('tools/cftbl/vpx_lights.json'))
G = [
 ('film', 'F-I-L-M', '(F)-I-L-M … F-I-L-M', 'Vier Buchstaben über den Flippern. F = K-I-S-S, I = alle 4 Menu-Ziele, L = P-A-I-D, M = Slide (Playground-Saucer). Alle vier = Multiball bereit.', ['L81','L82','L83','L84'], 14),
 ('kiss', 'K-I-S-S und Lippen', 'K-I-S-S / Lips (Taillight Park)', 'Unter der Taillight-Park-Bahn links. Jeder Treffer in die Bahn bzw. der Skill Shot über den oberen linken Rollover schaltet Buchstaben weiter. Erstes K-I-S-S = F.', ['L21','L22','L23','L24','L41'], 12),
 ('left_lane', 'Start Movie · Video · Search (links)', 'Left Start Movie / Left Video / Left Search', 'Anzeigen an der Taillight-Park-Bahn. Blinkend: Film (Multiball) starten, Video-Modus starten, im Multiball die Kreatur suchen.', ['L44','L44b','L43','L42'], 12),
 ('right_lane', 'Playground-Bahn', 'Start Movie / Video / Search / Slide / Big Millions / Playground Award / Start Mega Menu', 'Reihe vor der Playground-Bahn rechts. Zeigt, was der Playground-Saucer gerade bringt: Slide (M), Start Mega Menu, Playground Award, Big Millions, Video, Start Movie, Search.', ['L37','L37b','L36','L35','L34','L33','L32','L31'], 12),
 ('center_lane', 'Center-Shot-Anzeigen', 'Extra Ball / Move Your Car / Parking O.K. / Collect Combo', 'In der Mitte vor dem Center Shot. Extra Ball abholen, Move Your Car, Parking O.K., Double-Feature-Combo kassieren.', ['L48','L47','L46','L45'], 13),
 ('menu_lamps', 'Menu-Anzeigen und Mega Menu', 'Cola / Hot Dog / Popcorn / Ice Cream / Mega Menu', 'Je eine Lampe an den vier Menu-Zielen und das Feld „Mega Menu“. Alle vier Ziele = Snack Bar offen.', ['L53','L54','L86','L87','L38'], 12),
 ('paid', 'P-A-I-D', 'P-A-I-D lanes', 'Vier Bahnen oben rechts. Komplett = L, Bonus-Multiplikator steigt.', ['L11','L12','L13','L14'], 12),
 ('combo', 'Double Feature Combo', 'Build Combo / Start Combo', 'Links unter der linken Rampe: Combo aufbauen (linke Rampe), Abschluss über den Center Shot. „Start Combo“ an der rechten Inlane.', ['L62','L85'], 13),
 ('center_search', 'Search (Snack Bar)', 'Center Search', 'Links neben der Snack Bar: im Multiball eine der drei Suchstellen.', ['L52'], 13),
 ('free_pass', 'Free Pass', 'Free Pass', 'Leuchtet bei aktivem Ball-Retter („Stay cool, Daddy-O“).', ['L61'], 13),
]
out = {}
for gid, name, en, text, ns, r in G:
    pts = apply(H, [L[n][:2] for n in ns])
    out[gid] = {'name': name, 'en': en, 'text': text, 'px': [[round(float(x), 1), round(float(y), 1)] for x, y in pts], 'r': r}
json.dump(out, open('content/cftbl/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
