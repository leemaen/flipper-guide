"""content/transformers/inserts.json: Insert-Lichter der Tischdatei in Pixel der VPX-Ansicht. Benennung nach dem aufgedruckten Artwork (Lampenliste des Pro-Handbuchs nicht ausgewertet)."""
import sys, json; sys.path.insert(0, 'tools')
import numpy as np
from homography import apply
H = np.array(json.load(open('tools/transformers/H_vpx.json'))); L = json.load(open('tools/transformers/vpx_lights.json'))
G = [
 ('decepticon_modes', 'Decepticon-Modi', 'Megatron · Starscream · Shockwave · Blackout · Devastator', 'Linke Spalte der Modus-Felder (Aufdruck „Decepticons“). Gespielte Modi leuchten.', ['li27','li7','li6','li5','li4'], 22),
 ('autobot_modes', 'Autobot-Modi', 'Optimus Prime · Bumblebee · Ironhide · Mudflap & Skids · Ratchet', 'Rechte Spalte der Modus-Felder (Aufdruck „Autobots“). Gespielte Modi leuchten.', ['li22','li23','li24','li25','li26'], 22),
 ('sentinel', 'Sentinel Prime', 'Sentinel Prime', 'Feld über den Modus-Spalten. Was es genau anzeigt, ist nicht belegt (laut Code-Notizen gibt es einen Sentinel-Prime-Super-Jackpot).', ['li28'], 20),
 ('challenge_megatron', 'Challenge Megatron', 'Challenge Megatron', 'Rundes Feld unter Megatron. Bedeutung laut Aufdruck: Megatron herausfordern. Genaue Regel nicht belegt.', ['li29'], 22),
 ('triangles', 'Dreieck-Säulen vor den Hauptschüssen', 'Autobot / Decepticon / X triangles', 'Fünf Säulen aus Dreiecken: vor linkem Orbit, linker Rampe, TF-Rampe, Bumblebee-Captive-Ball und rechtem Orbit (Zuordnung nach Lage). Leuchtende Autobot- bzw. Decepticon-Dreiecke zeigen, welcher Schuss den Modus weiterbringt. Getroffen wird der Eingang dahinter.', ['li31','li16','li17','li18','li19','li44','li45','li46','li40','li41','li42','li43','li30','li32','li33','li34','li36','li37','li38','li39'], 13),
 ('top_lane_lamps', 'Obere Bahnen', 'Top lanes', 'Lampen der oberen Rollover-Bahnen (Skill Shot, Cyber-Multiplier-Symbole).', ['li50','li49'], 14),
]
out = {}
for gid, name, en, text, ns, r in G:
    pts = apply(H, [L.get(n, L.get(n + 'a'))[:2] for n in ns])
    out[gid] = {'name': name, 'en': en, 'text': text, 'px': [[round(float(x), 1), round(float(y), 1)] for x, y in pts], 'r': r}
json.dump(out, open('content/transformers/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
