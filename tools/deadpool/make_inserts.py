"""Inserts für deadpool (Foto-Pixel, per Gitter vermessen) und deadpool-vpx (Licht-Mittelpunkte der Tischdatei * 1,05).
Lampennamen nach Stern-Pro-Handbuch S. 18-21; Zuordnung VPX-Licht <-> Foto wie in tools/deadpool/fit_H.py."""
import json, shutil
it = json.load(open('_quellen/deadpool/pages/li_items.json'))
PH = {'li024': (395, 1255), 'li023': (394, 1310), 'li022': (392, 1365), 'li021': (390, 1417),
      'li020': (960, 1257), 'li019': (960, 1310), 'li018': (959, 1365), 'li017': (960, 1417),
      'li008': (505, 1582), 'li010': (652, 1582), 'li011': (803, 1582), 'li007': (570, 1680), 'li009': (730, 1680),
      'li005': (652, 1782), 'li003': (578, 1810), 'li004': (723, 1810), 'li002': (652, 1838), 'li012': (850, 1488), 'li013': (793, 1365),
      'li038': (570, 932), 'li037': (579, 991), 'li047': (591, 1061), 'li048': (943, 975),
      'li036': (704, 1014), 'li035': (750, 1036), 'li034': (800, 1054), 'li071': (634, 571), 'li046': (632, 622)}
G = {
 'dead_ins': ('D-E-A-D', '(D)EAD … DEA(D) inserts (lamps 30-33)', 'Zeigen die vier DEAD-Ziele links. DEAD komplett beleuchtet BATTLE am Scoop.', ['li024', 'li023', 'li022', 'li021'], 17),
 'pool_ins': ('P-O-O-L', '(P)OOL … POO(L) inserts (lamps 35-38)', 'Zeigen die vier POOL-Ziele rechts. POOL komplett beleuchtet den Lock an der rechten Rampe.', ['li020', 'li019', 'li018', 'li017'], 17),
 'battles': ('Gegner: Juggernaut · Mystique · Sabretooth', 'Juggernaut / Mystique / Sabretooth (lamps 18-20)', 'Die drei Battles. Gewonnene Battles leuchten; alle drei beleuchten Sauron-Multiball.', ['li008', 'li010', 'li011'], 18),
 'quests': ('Quests: T-Rex · Megalodon', 'T-Rex / Megalodon (lamps 21, 22)', 'Die beiden Quests (Zeitreisen).', ['li007', 'li009'], 18),
 'pfx': ('Spielfeld-Multiplikator', '2X · 3X · 4X · 5X (lamps 23-26)', 'Aktueller Playfield-X.', ['li002', 'li003', 'li004', 'li005'], 16),
 'sauron_ins': ('Sauron', 'Sauron (lamp 40)', 'Sauron-Multiball (nach allen drei Battles).', ['li012'], 16),
 'sinister_ins': ('Mr. Sinister', 'Mr Sinister (lamp 41)', 'Finale (Wizard-Modus).', ['li013'], 16),
 'eb_ins': ('Extraball', 'Extra Ball (lamp 68)', 'Extraball am Scoop abholbereit.', ['li038'], 16),
 'mystery_ins': ('Mystery', 'Mystery (lamp 67)', 'Mystery am Scoop (nach DEADPOOL komplett).', ['li037'], 16),
 'quest_ins': ('Quest', 'Quest (lamp 66)', 'Quest am Scoop abholbereit.', ['li047'], 16),
 'lock_ins': ('Lock', 'Lock (lamp 93)', 'Lock an der rechten Katana-Rampe beleuchtet.', ['li048'], 18),
 'oof_ins': ('O-O-F-Fallziele', '3-Bank Drop Target L/C/R (lamps 77-79)', 'Die drei Fallziele vor Lil Deadpool.', ['li036', 'li035', 'li034'], 15),
 'center_ins': ('Wolverine-Loop: Pfeil + Waffe', 'Center Loop Arrow (lamps 105-107) / Weapon (104)', 'Pfeil und Waffen-Insert vor dem mittleren Spinner.', ['li071', 'li046'], 16),
}
real = {k: {'name': v[0], 'en': v[1], 'text': v[2], 'px': [list(PH[n]) for n in v[3]], 'r': v[4]} for k, v in G.items()}
vpx = {k: {'name': v[0], 'en': v[1], 'text': v[2], 'px': [[round(it[n]['c'][0] * 1.05, 1), round(it[n]['c'][1] * 1.05, 1)] for n in v[3]], 'r': v[4]} for k, v in G.items()}
json.dump(real, open('content/deadpool/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(vpx, open('content/deadpool-vpx/inserts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
pass  # VPX-Geometrie wird separat gepflegt
for tid, view, H, src, crop, out in (('deadpool', 'real', 'tools/deadpool/H_photo.json', '_quellen/deadpool/fotos/stern_dp_pro_playfield.png', [130, 140, 1255, 2290], 'deadpool-real.jpg'),
                                     ('deadpool-vpx', 'vpx', 'tools/deadpool/H_vpx.json', '_quellen/deadpool/vpx_top.png', [0, 0, 1000, 2221], 'deadpool-vpx.jpg')):
    json.dump({'views': {view: {'H': H, 'src': src, 'crop': crop, 'out': out, 'quality': 86}}, 'insertsView': view},
              open(f'content/{tid}/build.json', 'w', encoding='utf-8'), indent=1)
print(len(real))
