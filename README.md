# Flipper-Guide

Persönliche, offline nutzbare Flipper-Strategie-App (PWA). Erster Tisch: Stern *The Lord of the Rings* (2003), echter Tisch und VPX (VPW Valinor Edition 1.6).

- `app/`: die veröffentlichte App (statisch, kein Build nötig)
- `content/lotr/`: redaktionelle Quelle: `content.json` (Texte, Regeln, Quellen), `geometry.json` (Schuss-Geometrie in VPX-Koordinaten), `inserts.json` (Einsätze in Fotopixeln)
- `tools/`: `build_data.py` projiziert die Geometrie per Homographie in beide Spielfeldbilder (`--check` rendert Prüfbilder), `build_sw.py` erzeugt Service Worker und Offline-Dateiliste

Nach Änderungen:

```
py -3 -I tools/build_data.py --check
py -3 -I tools/build_sw.py
```

Die Rohquellen (Stern-Handbuch, Fotos, VPX-Auszüge, Prüfbilder) liegen lokal in `_quellen/` und sind nicht im Repository.
