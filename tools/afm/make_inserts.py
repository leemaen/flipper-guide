"""Erzeugt content/afm/inserts.json: Insert-Lichter der Tischdatei (Lampennummern = Bally-Lampenmatrix, Handbuch S. 2-3) per H_real ins Foto projiziert."""
import sys, json; sys.path.insert(0, 'tools')
import numpy as np
from homography import apply
H = np.array(json.load(open('tools/afm/H_real.json'))); L = json.load(open('tools/afm/vpx_lights.json'))
G = [
 ('ta_lights', 'Total-Annihilation-Lampen (je 3)', 'Capture 1–3 · Big-O-Beam 1–3 · Tractor Beam 1–3 · Atomic Blaster 1–3',
  'Drei Lampen vor jedem der vier äußeren Schüsse: Capture (linker Loop), Big-O-Beam (linke Rampe), Tractor Beam (rechte Rampe), Atomic Blaster (rechter Loop). Jeder Treffer füllt eine Lampe. Drei voll = Hurry-Up am Kraftfeld/Saucer. Alle zwölf voll = Total Annihilation.',
  ['l71','l72','l73','l21','l22','l23','l31','l32','l33','l63','l64','l65'], 9),
 ('jackpots', 'Jackpot-Einsätze', 'Left Loop / Left Ramp / Center Ramp / Right Ramp / Right Loop Jackpot',
  'Fünf Jackpot-Einsätze, je einer vor linkem Loop, linker Rampe, Lock-Rampe, rechter Rampe und rechtem Loop. Im Multiball zeigen sie, welche Jackpots noch offen sind. Der Super Jackpot wandert über diese fünf Schüsse.',
  ['l74','l24','l28','l34','l66'], 12),
 ('arrows', 'Rote Pfeile (Raketen)', 'Left Loop / Left Ramp / Center Ramp / Right Ramp / Right Loop Arrow',
  'Pfeile vor den fünf Hauptschüssen. Blinkend: Super Skill Shot bzw. Combo möglich. Getroffen wird der Eingang hinter der Pfeilspitze, nicht der Pfeil.',
  ['l75','l25','l42','l35','l41'], 12),
 ('locks', 'Lock 1–3 · Light Lock', 'Lock 1, Lock 2, Lock 3, Light Lock',
  'Grüne Dreiecke Lock 1–3 und darunter „Light Lock“. Zeigen den Stand der Locks an der Lock-Rampe.',
  ['l55','l26','l27','l54'], 10),
 ('countries', 'Länder (Attack Waves)', 'Paris France · Berlin Germany · Pisa Italy · London England · D.C. U.S.A. · Attack Mars',
  'Die fünf Länder in der Mitte. Ein gerettetes Land leuchtet dauerhaft. Sind alle fünf gerettet, folgt „Attack Mars“ (Conquer Mars).',
  ['l58','l57','l56','l53','l52','l51'], 12),
 ('right_column', 'Extra Ball · Stroke of Luck · Martian Attack · Rule the Universe', 'Extra Ball / Stroke of Luck / Martian Attack / Rule Universe',
  'Vier Felder rechts der Länder. Sie zeigen, was gerade am Stroke-of-Luck-Scoop (rechts oben neben dem I-Ziel) abgeholt werden kann.',
  ['l67','l38','l36','l37'], 10),
 ('martian_ins', 'M-A-R-T-I-A-N', 'Martian target inserts',
  'Buchstaben-Einsätze vor den sieben Marsmenschen-Zielen: M-A-R links unten, T links vom Kraftfeld, I rechts davon, A-N rechts unten. Getroffene Buchstaben leuchten.',
  ['l76','l77','l78','l48','l68','l62','l61'], 9),
 ('bank_lamps', 'Kraftfeld-Lampen', 'Left / Center / Right Motor Bank',
  'Drei rote Felder direkt unter der beweglichen 3er-Bank (Kraftfeld). Zeigen, welche der drei Ziele noch fehlen, um das Kraftfeld zu senken.',
  ['l45','l46','l47'], 12),
 ('rtu', 'Rule-the-Universe-Ziele', 'Super Jackpot · Super Jets · Martian Attack MB · Annihilation · Conquer Mars · 5-Way Combo',
  'Sechs runde Felder über den Flippern. Jedes leuchtet, sobald das Ziel einmal erreicht ist. Alle sechs = Rule the Universe am Stroke-of-Luck-Scoop.',
  ['l12','l11','l13','l14','l16','l17'], 10),
 ('rollover_lamps', 'In-/Outlane-Lampen', 'Left Outlane / Left Return / Right Return / Right Outlane',
  'Vier gelbe Lampen an den In- und Outlanes. Alle vier = Extraball (erstes Mal) bzw. Stroke of Luck am Scoop. Die Flipper verschieben die Lampen.',
  ['l82','l83','l84','l85'], 9),
 ('shoot_again', 'Shoot Again', 'Shoot Again', 'Leuchtet bei Extraball.', ['l81'], 12),
]
out = {}
for gid, name, en, text, ns, r in G:
    pts = apply(H, [L[n][:2] for n in ns])
    out[gid] = {'name': name, 'en': en, 'text': text, 'px': [[round(float(x), 1), round(float(y), 1)] for x, y in pts], 'r': r}
json.dump(out, open('content/afm/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
