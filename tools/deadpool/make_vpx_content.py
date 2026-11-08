"""Erzeugt content/deadpool-vpx/content.json: Schussbeschreibungen aus content/deadpool (gleiches Spielfeld),
Regeln neu nach Tischscript JP's Deadpool 6.1.0 (Zeilennummern in den Quellenangaben)."""
import json, copy
c = json.load(open('content/deadpool/content.json', encoding='utf-8'))
v = copy.deepcopy(c)
v['table'] = {
 'id': 'deadpool-vpx', 'name': 'Deadpool (VPX, JP Salas)', 'short': 'Deadpool VPX', 'manufacturer': 'JP Salas (Tribute an Stern)', 'year': 2021,
 'system': 'VPX, eigenes Script (kein Original-ROM)', 'design': 'Spielfeld nach George Gomez (Stern 2018); Script/Regeln: jpsalas, Änderungen 6.1.0 von leon1638',
 'editions': 'JP\'s Deadpool 6.1.0 (14.01.2026, VPX 8). Laut Autor „Table, graphics and rules by me“ – die Regeln sind nachempfunden, nicht die Stern-Software. Spielfeld wie Stern Pro (Katana-Rampe, 3 Fallziele). Den echten Stern-Tisch findest du als eigenen Eintrag „Deadpool (Pro)“.',
 'ruleVersion': 'Regeln aus dem Tischscript (script.vbs der Version 6.1.0) und der Spielanleitungs-Textur „rulescard“ im Tisch. Die Karte ist eine Kopie der Stern-Karte und beschreibt einige Dinge (z. B. Quests), die das Script so nicht umsetzt – maßgeblich ist hier das Script.',
 'accent': '#c8102e', 'contentDate': '2026-11-08'}
v['sources'] = [
 {'id': 'script', 'title': "JP's Deadpool 6.1.0 – Tischscript (script.vbs)", 'url': 'https://www.vpforums.org/', 'use': 'Regeln: Battles (StartChooseBattle, Z. 4806 ff.), Lock/Ninja-Multiball (Lock_Hit, Z. 5432), Disco (CheckDisco), Berserker (CheckBerserker, Z. 5550), Waffen (Checkweapons, Z. 5358), Ninja-Sterne (CheckNinjaStars), Katanarama (CheckKatanarama), Lil Deadpool (Z. 4350 ff.), Scoop (HellHouse_Hit, Z. 4578).'},
 {'id': 'card', 'title': 'Spielanleitung im Tisch (Textur „rulescard“, Kopie der Stern-Karte)', 'url': 'https://www.vpforums.org/', 'use': 'Überblick der Spielelemente.'},
 {'id': 'log', 'title': 'Änderungsprotokoll im Tisch (Tischbeschreibung 6.1.0)', 'url': 'https://www.vpforums.org/', 'use': 'Lil-DP-Multiball nach 2 Treffern, Battle nach jedem neuen Ball bereit, Ballretter in Multibällen.'},
 {'id': 'vpx', 'title': "VPX: JP's Deadpool 6.1.0 (jpsalas)", 'url': 'https://www.vpforums.org/', 'use': 'Schalter-, Ziel-, Flipper- und Lichtpositionen; Draufsicht aus der Tischdatei gerendert.'},
 c['sources'][-1]]
v['views'] = {'vpx': {'label': 'VPX (JP 6.1.0)', 'note': 'Draufsicht aus den 3D-Modellen der Tischdatei gerendert (ohne Beleuchtung). Katana und Drahtbahnen teils nur schematisch.'}}
for s in v['shots'].values():
    s['sources'] = ['vpx' if x in ('vpx', 'manual') else 'script' for x in s['sources']]
    s['sources'] = sorted(set(s['sources']))
S = v['shots']
S['left_orbit']['awards'] = ['Disco: 50 Drehungen = Disco Loops, 100 = Disco-Multiball', 'Berserker Rage (25 Spinner-Drehungen)', 'Katanarama-Time-Schuss']
S['u_turn']['awards'] = ['Special, wenn beleuchtet (Schalter „colossus loop“)', 'Laut Spielanleitung: Colossal Jackpot vom Colossus-Loop aus']
S['u_turn']['sources'] = ['script', 'card']
S['scoop']['awards'] = ['Battle wählen (Flippertasten) und starten – zu jedem neuen Ball bereit', 'Waffen-Jackpot (1M), Extraball, Mystery', 'Mechsuit-Multiball starten / Super Jackpot']
S['center_loop']['awards'] = ['Berserker Rage (25 Spinner-Drehungen)', 'Katanarama-Time-Schuss']
S['right_ramp']['awards'] = ['Lock für Ninja-Multiball (3 Kugeln)', 'Ninja-Multiball: Super Jackpot (6× Jackpot) am Lock', 'Katana-Diamanten']
S['right_orbit']['awards'] = ['Chimichangas (alle 10 = +1 Playfield X)', 'Katanarama-Time-Schuss']
S['snikt']['awards'] = ['Nur 1.000 Punkte – die SNIKT-Combo mit Playfield-X-Bonus des echten Tisches gibt es im Script nicht']
S['pool']['awards'] = ['POOL komplett → Lock beleuchtet (Spielanleitung)', 'DEADPOOL komplett → Mystery']
S['dead']['awards'] = ['DEAD komplett → Battle (Spielanleitung)', 'DEADPOOL komplett → Mystery']
S['lildp']['awards'] = ['2 Treffer (je Modus +1, höchstens 4) → Lil-Deadpool-Multiball', 'Jackpots im Lil-Deadpool-Multiball']
S['colossal']['awards'] = ['Colossal Jackpot (laut Spielanleitung); im Script nur als Punkte-Ziel geführt']
for k in ('snikt', 'colossal', 'pool', 'dead', 'lildp'):
    S[k]['sources'] = sorted(set(S[k]['sources'] + ['card']))
v['strategies'] = [
 {'id': 'solid', 'title': 'Solide spielen', 'subtitle': 'Battle zu jedem Ball, Ninja-Multiball, Lil Deadpool', 'steps': [
  {'title': 'Battle am Scoop', 'shots': ['scoop'], 'prep': 'Battle ist zu jedem neuen Ball bereit.', 'go': 'Hell-House-Scoop (Hell House Scoop), mit den Flippertasten einen Gegner wählen, Abschussknopf bestätigt.', 'why': 'Fünf Gegner wählbar: Juggernaut, Mystique, Sabretooth, T-Rex, Megalodon.', 'sources': ['script', 'log']},
  {'title': 'Ninja-Multiball', 'shots': ['right_ramp'], 'prep': 'Lock leuchtet.', 'go': 'Dreimal die rechte Katana-Rampe.', 'why': 'Dritter Lock startet den Multiball (Ballretter an). Jackpot = 500K + 50K je Ninja-Stern.', 'sources': ['script']},
  {'title': 'Lil-Deadpool-Multiball', 'shots': ['oof', 'lildp'], 'prep': 'O-O-F-Fallziele abräumen.', 'go': 'Lil-Deadpool-Ziel 2-mal treffen.', 'why': 'Startet Lil-Deadpool-Multiball; danach braucht es je einen Treffer mehr (max. 4).', 'sources': ['script', 'log']},
  {'title': 'Extraball', 'shots': ['scoop'], 'prep': '30 Waffen oder 50 Ninja-Sterne.', 'go': 'Extraball am Scoop abholen.', 'why': 'Beide Zähler beleuchten den Extraball am Scoop.', 'sources': ['script']}]},
 {'id': 'high', 'title': 'Auf Highscore', 'subtitle': 'Playfield X über Zähler, Sauron und Mr. Sinister', 'steps': [
  {'title': 'Playfield X sammeln', 'shots': ['right_orbit', 'bumpers', 'left_orbit', 'left_ramp', 'center_loop', 'right_ramp', 'scoop'], 'prep': 'Zähler laufen über das ganze Spiel.', 'go': 'Chimichangas (rechter Orbit), Ninja-Sterne (Bumper → blaue Schüsse), Waffen (weiße Schüsse → Scoop).', 'why': 'Je 10 Chimichangas, 25 Ninja-Sterne und 50 Waffen +1 Playfield X.', 'sources': ['script']},
  {'title': 'Waffen-Jackpot und Mechsuit', 'shots': ['scoop'], 'prep': 'Alle 6 Waffen leuchtet der Waffen-Jackpot (1M) am Scoop, bei 75 Waffen Mechsuit-Multiball.', 'go': 'Scoop.', 'why': 'Mechsuit: Super Jackpot am Scoop = 6× Jackpot.', 'sources': ['script']},
  {'title': 'Drei Battles → Sauron', 'shots': ['scoop'], 'prep': 'Drei Battles gewonnen.', 'go': 'Am Scoop Sauron wählen.', 'why': 'Sauron startet mit 2 Zusatzkugeln; grüne Schüsse treffen ihn.', 'sources': ['script']},
  {'title': 'Katanarama Time', 'shots': ['left_ramp', 'right_ramp', 'left_orbit', 'right_orbit'], 'prep': 'Rampen schießen füllt 6 Diamanten.', 'go': 'Nach dem 6. Diamanten Orbits und Rampen.', 'why': 'Zeitmodus (20 s + Dazzler-Bonus) mit Katanarama-Wert auf Orbits und Rampen.', 'sources': ['script']}]}]
v['multiballs'] = [
 {'id': 'ninja', 'name': 'Ninja-Multiball', 'tag': 'Lock-Multiball', 'balls': '3 Kugeln',
  'prep': [{'title': '3 Kugeln locken', 'shots': ['right_ramp', 'pool'], 'text': 'Locks an der rechten Katana-Rampe, wenn Lock leuchtet (POOL beleuchtet ihn laut Spielanleitung).', 'sources': ['script', 'card']}],
  'start': {'title': 'Dritter Lock', 'shots': ['right_ramp'], 'text': 'Nach dem dritten Lock kommen 2 Kugeln dazu.', 'sources': ['script']},
  'score': [{'title': 'Jackpots, Super am Lock', 'shots': ['left_orbit', 'left_ramp', 'center_loop', 'right_orbit', 'right_ramp'], 'text': 'Jackpot 500K + 50K je Ninja-Stern. Super Jackpot an der rechten Rampe (Lock) = 6× Jackpot, danach +1M.', 'sources': ['script']}]},
 {'id': 'lildp', 'name': 'Lil-Deadpool-Multiball', 'tag': 'Lil Deadpool', 'balls': '2 Kugeln',
  'prep': [{'title': 'Fallziele + 2 Treffer', 'shots': ['oof', 'lildp'], 'text': 'O-O-F abräumen, Lil-Deadpool-Ziel 2-mal (je Modus +1, max. 4).', 'sources': ['script', 'log']}],
  'start': {'title': 'Lil-Deadpool-Ziel', 'shots': ['lildp'], 'text': 'Der letzte nötige Treffer startet den Multiball.', 'sources': ['script']},
  'score': [{'title': 'Jackpots, dann Hauptschüsse', 'shots': ['lildp', 'left_orbit', 'left_ramp', 'center_loop', 'right_orbit'], 'text': 'Jackpots am Lil-Deadpool-Ziel, im zweiten Teil an den Hauptschüssen; zuletzt Spinner je 500K.', 'sources': ['script']}]},
 {'id': 'disco', 'name': 'Disco Loops / Disco-Multiball', 'tag': 'Spinner', 'balls': '1 bzw. 2 Kugeln',
  'prep': [{'title': 'Dazzler-Spinner', 'shots': ['left_orbit'], 'text': 'Zählt nicht während eines Battles: 50 Drehungen = Disco Loops (Zeitmodus), 100 = Disco-Multiball (+1 Kugel), dann von vorn.', 'sources': ['script']}],
  'start': {'title': 'Automatisch', 'shots': ['left_orbit'], 'text': 'Startet beim Erreichen der Drehungen.', 'sources': ['script']},
  'score': [{'title': 'Spinner erhöht den Super Jackpot', 'shots': ['left_orbit', 'left_ramp'], 'text': 'Im Disco-Multiball +100K Super Jackpot je Drehung; beleuchtete Schüsse treffen.', 'sources': ['script']}]},
 {'id': 'sauron', 'name': 'Sauron', 'tag': 'Battle-Multiball', 'balls': '3 Kugeln',
  'prep': [{'title': 'Drei Battles gewinnen', 'shots': ['scoop'], 'text': 'Danach ist Sauron als sechster Gegner wählbar.', 'sources': ['script']}],
  'start': {'title': 'Scoop, Sauron wählen', 'shots': ['scoop'], 'text': 'Startet mit 2 Zusatzkugeln.', 'sources': ['script']},
  'score': [{'title': 'Grüne Schüsse', 'shots': [], 'text': '„Shoot green shots to attack Sauron“ – welche Schüsse grün sind, zeigt der Tisch.', 'sources': ['script']}]},
 {'id': 'mech', 'name': 'Mechsuit-Multiball', 'tag': 'Waffen', 'balls': 'Multiball',
  'prep': [{'title': '75 Waffen', 'shots': ['left_orbit', 'left_ramp', 'center_loop', 'right_ramp', 'right_orbit', 'scoop'], 'text': 'Weiße Waffen-Schüsse; alle 75 Waffen wird Mechsuit beleuchtet.', 'sources': ['script']}],
  'start': {'title': 'Scoop', 'shots': ['scoop'], 'text': 'Am Hell-House-Scoop.', 'sources': ['script']},
  'score': [{'title': 'Super am Scoop', 'shots': ['scoop'], 'text': 'Super Jackpot = 6× Mechsuit-Jackpot, danach +1M.', 'sources': ['script']}]}]
v['modesIntro'] = 'Am Hell-House-Scoop wählst du einen Gegner (Flippertasten, Abschussknopf bestätigt). Nach 3 Siegen ist Sauron wählbar, nach 6 Siegen Mr. Sinister. Quests wie am echten Tisch gibt es nicht – T-Rex und Megalodon sind hier Battles.'
v['modes'] = [
 {'id': 'jugg', 'name': 'Juggernaut', 'film': 'Battle', 'time': 'Lebensbalken', 'steps': [{'title': 'Blinkende Schüsse', 'shots': ['center_loop'], 'text': 'Laut Änderungsprotokoll macht der Wolverine-Loop Schaden. Danach Scoop.'}]},
 {'id': 'myst', 'name': 'Mystique', 'film': 'Battle', 'time': 'Lebensbalken', 'steps': [{'title': 'Blinkende Schüsse', 'shots': [], 'text': 'Blinkende Schüsse und Display beachten; Ablauf im Detail nicht ausgewertet.'}]},
 {'id': 'sabre', 'name': 'Sabretooth', 'film': 'Battle', 'time': 'Lebensbalken', 'steps': [{'title': 'Orbits', 'shots': ['left_orbit', 'right_orbit'], 'text': 'Laut Änderungsprotokoll nehmen linker und rechter Loop Schaden.'}]},
 {'id': 'trex', 'name': 'T-Rex', 'film': 'Battle', 'time': 'Lebensbalken', 'steps': [{'title': 'Blinkende Schüsse', 'shots': [], 'text': 'Hier ein Battle (am echten Tisch eine Quest). Ablauf nicht ausgewertet.'}]},
 {'id': 'mega', 'name': 'Megalodon', 'film': 'Battle', 'time': 'Lebensbalken', 'steps': [{'title': 'Blinkende Schüsse', 'shots': [], 'text': 'Hier ein Battle (am echten Tisch eine Quest). Ablauf nicht ausgewertet.'}]},
 {'id': 'sinister', 'name': 'Mr. Sinister', 'film': 'Finale', 'time': '–', 'steps': [{'title': 'Blinkende Schüsse', 'shots': [], 'text': '„Shoot flashing shots to attack Mr. Sinister“. Nach 6 gewonnenen Battles wählbar.'}]},
 {'id': 'katana', 'name': 'Katanarama Time', 'film': 'Rampen', 'time': '20 s + Bonus', 'steps': [{'title': '6 Diamanten', 'shots': ['left_ramp', 'right_ramp', 'left_orbit', 'right_orbit'], 'text': 'Rampen füllen die Diamanten; dann Orbits und Rampen.'}]},
 {'id': 'berserk', 'name': 'Berserker Rage', 'film': 'Spinner', 'time': 'Zeitmodus', 'steps': [{'title': 'Spinner', 'shots': ['left_orbit', 'center_loop'], 'text': 'Nach 25 Spinner-Drehungen; danach steigt der Wert je Drehung um 10K.'}]}]
v['limits'] = [
 'Regeln aus dem Tischscript ausgewertet, nicht aus einem Rulesheet. Battle-Abläufe im Detail sind nicht vollständig beschrieben.',
 'Die Spielanleitung im Tisch ist eine Kopie der Stern-Karte und passt nicht überall zum Script (z. B. Quests, SNIKT).',
 'Die Mündung des Colossus-U-Turns ist nicht markiert.',
 'Flipper-Empfehlungen aus der Lage abgeleitet.']
json.dump(v, open('content/deadpool-vpx/content.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
