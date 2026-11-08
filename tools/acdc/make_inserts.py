"""Erzeugt content/acdc/inserts.json aus den Licht-Positionen der VPX (Bildpixel = VPX * Maßstab).
Lampennamen/-nummern: Stern-Handbuch S. 18-21 und Lampz-Zuordnung im Tischscript."""
import json
S = 1.05
it = json.load(open('_quellen/acdc/pages/li_items.json'))
P = lambda names: [[round(it[n]['c'][0] * S, 1), round(it[n]['c'][1] * S, 1)] for n in names]
D = {
 'note_arrows': ('Noten-Pfeile (Song-Schüsse)', 'Note shot arrows (RGB): L. Loop top/bot, L. Ramp, Bell top/bot, R. Ramp, R. Loop mid/bot',
   'Farbige Pfeile vor den fünf Hauptschüssen. Blinkende Noten-Schüsse bringen Punkte und Song-Fortschritt; im Multiball zeigen sie Jackpots bzw. Add-a-Ball. Je Orbit und an der Bell sitzen zwei Pfeile.',
   ['l52', 'l18', 'l20', 'l35', 'l36', 'l26', 'l28', 'l29'], 17),
 'axe': ('A-X-E-Bahnen oben', 'Left / Center / Right Top Lane', 'Drei Bahnen oben. A-X-E gehört zum Song „Whole Lotta Rosie“.', ['l37', 'l38', 'l39'], 14),
 'tunes': ('Tunes-N-Stuff', 'Tunes - N - Stuff (lamp 96)', 'Anzeige an der Jukebox ganz oben.', ['l40'], 16),
 'acdc_ins': ('A-C-/-D-C-Anzeigen', 'AC/DC drop target inserts (lamps 17-21)', 'Zeigen, welche der fünf A-C-/-D-C-Fallziele links schon gefallen sind (Song „Back in Black“, Album-Multiball, Extraball).', ['l13', 'l12', 'l11', 'l10', 'l9'], 15),
 'rock_ins': ('R-O-C-K-Anzeigen', 'ROCK target inserts (lamps 33-36)', 'Zeigen die vier R-O-C-K-Ziele rechts (Song „Let There Be Rock“, Album-Multiball, Extraball).', ['l30', 'l31', 'l32', 'l33'], 16),
 'tnt_ins': ('T-N-T-Anzeigen', 'T.N.T. inserts (lamps 49-51)', 'Die drei T-N-T-Fallziele in der Mitte (Song „T.N.T.“).', ['l22', 'l23', 'l24'], 16),
 'tnt_arrow': ('T.N.T.-Pfeil', 'T.N.T. Arrow wht./note (lamp 24)', 'Pfeil unter den T-N-T-Fallzielen.', ['l25'], 15),
 'bolts': ('Blitze (Thunder-Ziele)', 'Lightning bolts: L. Ramp standup L/R, R. Ramp standup (lamps 22, 23, 41)', 'Blitz-Anzeigen vor den drei kleinen Thunder-Zielen neben den Rampen (Song „Thunderstruck“).', ['l19', 'l21', 'l64'], 13),
 'fire_ins': ('F-I-R-E-Bahnen', 'F-I-R-E in/outlane inserts (lamps 12, 13, 43, 44)', 'F-I-R-E in den Außen- und Rückführbahnen. FIRE komplett qualifiziert die Kanonen-Features.', ['l3', 'l4', 'l7', 'l8'], 13),
 'pf_x': ('2X / 3X Spielfeld', '2X (lamp 14) / 3X (lamp 42)', 'Spielfeld-Multiplikator (über die Bell).', ['l5', 'l6'], 15),
 'mb_ins': ('Multiball-Anzeigen', 'Jam Multiball · Album Multiball · Tour Multiball (lamps 1, 4, 11)', 'Zeigen, welcher Multiball beleuchtet ist bzw. läuft.', ['l41', 'l44', 'l49'], 15),
 'super_ins': ('Super-Features', 'Super Targets · Super Lanes · Super Combos · Super Loops (lamps 2, 3, 10, 9)', 'Die vier Super-Features (mehr Punkte für Ziele, Bahnen, Combos, Loops).', ['l42', 'l43', 'l50', 'l51'], 14),
 'cannon_ins': ('Kanonen-Features', 'Cannon Fodder · Cannon Volley · Cannon Chaos (lamps 5-7)', 'Durch F-I-R-E qualifiziert, über die Kanone gespielt.', ['l45', 'l46', 'l47'], 14),
 'rock_again': ('Rock Again', 'Rock Again (lamp 8, Shoot Again)', 'Ball-Retter / Shoot Again.', ['l48'], 14),
 'eb_ins': ('Extraball', 'Extra Ball (lamp 40)', 'Leuchtet, wenn der Extraball am rechten Loop abholbereit ist.', ['l27'], 15),
 'special_ins': ('Special', 'Special (lamp 38)', 'Special-Anzeige.', ['l34'], 14),
 'lpf_arrows': ('Pfeile im unteren Spielfeld', 'Lower PF L./R. loop arrows (lamps 25, 37)', 'Pfeile vor den beiden Loops im unteren Spielfeld (Hell).', ['l1', 'l2'], 14),
 'face': ('Gesicht (unteres Spielfeld)', 'Face left eye · right eye · mouth (lamps 81, 82, 84)', 'Augen und Mund im unteren Spielfeld.', ['l14', 'l15', 'l17'], 16),
}
out = {k: {'name': v[0], 'en': v[1], 'text': v[2], 'px': P(v[3]), 'r': v[4]} for k, v in D.items()}
json.dump(out, open('content/acdc/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
